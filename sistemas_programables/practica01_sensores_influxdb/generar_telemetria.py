#!/usr/bin/env python3
"""Práctica 01 — Telemetría de sensores en line protocol para InfluxDB.

Simula una red de nodos Raspberry Pi Pico W / Pico 2 W (DHT22 + monitor de
batería, como los físicos del kit o los simulados en Wokwi) reportando cada
`--intervalo` segundos, y escribe la telemetría en formato line protocol:

    ambiente,dispositivo=PICO2W-3FA9BC,aula=LC-01 temperatura=24.31,humedad=54.8,bateria=87i 1751328000000000000

Las series son físicamente plausibles: la temperatura sigue una caminata suave
(deriva diurna) con ruido de sensor encima, la humedad se mueve en sentido
opuesto y la batería solo desciende.

Salida:
    salida/telemetria.lp   listo para cargar con `influx write --bucket iot --file <ruta>`

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python sistemas_programables/practica01_sensores_influxdb/generar_telemetria.py \
        --seed 2026 --dispositivos 3 --horas 24 --intervalo 300

Reproducibilidad: misma semilla → mismo archivo byte a byte (el timestamp
inicial es fijo, no "ahora"). El script imprime el SHA-256 del archivo para
que compares con tus compañeros.
"""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

# Permite importar providers/ al ejecutar desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider

# Timestamp inicial FIJO (no datetime.now()): si dependiera de la hora actual,
# el archivo cambiaría en cada corrida y adiós reproducibilidad.
INICIO = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
AULAS = ["LC-01", "LC-02", "LAB-IOT"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--dispositivos", type=int, default=3,
                        help="cantidad de nodos Pico W (default 3)")
    parser.add_argument("--horas", type=float, default=24,
                        help="horas de telemetría a simular (default 24)")
    parser.add_argument("--intervalo", type=int, default=300,
                        help="segundos entre reportes (default 300 = 5 min)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)

    # Estado por dispositivo: identidad fija + condiciones iniciales propias.
    nodos = []
    for _ in range(args.dispositivos):
        nodos.append({
            "id": fake.id_dispositivo(),
            "aula": fake.random_element(AULAS),
            "temp_base": 22.0 + fake.random.uniform(0, 4),   # cada aula, su clima
            "hum_base": 45.0 + fake.random.uniform(0, 20),
            "bateria": float(fake.bateria_pct()),
        })

    n_puntos = int(args.horas * 3600 // args.intervalo)
    args.salida.mkdir(exist_ok=True)
    ruta = args.salida / "telemetria.lp"

    with ruta.open("w") as f:
        for i in range(n_puntos):
            ts_s = int(INICIO.timestamp()) + i * args.intervalo
            ts_ns = ts_s * 1_000_000_000          # InfluxDB espera nanosegundos
            for nodo in nodos:
                # Deriva lenta (caminata) + ruido de sensor encima.
                nodo["temp_base"] += fake.random.gauss(0, 0.05)
                nodo["hum_base"] = min(95.0, max(20.0,
                                       nodo["hum_base"] + fake.random.gauss(0, 0.2)))
                nodo["bateria"] = max(5.0, nodo["bateria"] - abs(fake.random.gauss(0.003, 0.001)))

                temp = fake.temperatura_c(base=nodo["temp_base"], ruido=0.3)
                hum = fake.humedad_pct(base=nodo["hum_base"], ruido=1.0)

                # Line protocol: medicion,tags campos timestamp
                # bateria lleva sufijo 'i' = entero en InfluxDB.
                f.write(
                    f"ambiente,dispositivo={nodo['id']},aula={nodo['aula']} "
                    f"temperatura={temp},humedad={hum},bateria={int(nodo['bateria'])}i "
                    f"{ts_ns}\n"
                )

    sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
    print(f"Generados {n_puntos * len(nodos)} puntos "
          f"({args.dispositivos} nodos × {n_puntos} reportes) en {ruta}")
    print(f"Nodos: {[n['id'] for n in nodos]}")
    print(f"SHA-256 (compárala con tus compañeros): {sha}")
    print(f"\nCargar a InfluxDB:  influx write --bucket iot --file {ruta}")


if __name__ == "__main__":
    main()
