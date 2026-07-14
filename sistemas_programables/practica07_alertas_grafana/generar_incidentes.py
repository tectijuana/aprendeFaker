#!/usr/bin/env python3
"""Práctica SP-07 — Telemetría con incidentes para alertas de Grafana.

Escenario real: el NOC de la escuela debe enterarse SOLO cuando algo pasa:
un aula arriba de 30 °C sostenidos, o un nodo que deja de reportar. Este
generador produce 48 h de telemetría normal con DOS incidentes inyectados
en horarios conocidos (para que puedas verificar que tus alertas disparan
cuando deben — y no disparan cuando no):

  1. OLA DE CALOR en LC-02: la temperatura sube gradualmente hasta ~35 °C
     entre las horas 20 y 26, y regresa a la normalidad.
  2. CAÍDA DE NODO: un nodo de LAB-IOT deja de reportar en la hora 30 y
     nunca regresa (para la alerta "no data").

Además hay un PICO FALSO de 20 minutos en la hora 10 (una sola ventana a
31 °C): una alerta bien configurada con `for: 15m` NO debe dispararse.

Salida:
    salida/telemetria_incidentes.lp   listo para influx write
    salida/incidentes.txt             bitácora de la verdad (cuándo pasó qué)

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py alertas --seed 2026

Reproducible: misma semilla → mismo archivo byte a byte.
"""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider

INICIO = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
AULAS = ["LC-01", "LC-02", "LAB-IOT"]
INTERVALO = 300          # 5 min
HORAS = 48


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)
    rnd = fake.random

    # Dos nodos por aula; el segundo de LAB-IOT será el que muere.
    nodos = []
    for aula in AULAS:
        for _ in range(2):
            nodos.append({"id": fake.id_dispositivo(), "aula": aula,
                          "temp_base": 23.0 + rnd.uniform(0, 2),
                          "bateria": float(fake.bateria_pct())})
    nodo_muerto = next(n for n in nodos if n["aula"] == "LAB-IOT")

    n_puntos = HORAS * 3600 // INTERVALO
    args.salida.mkdir(exist_ok=True)
    ruta = args.salida / "telemetria_incidentes.lp"

    with ruta.open("w") as f:
        for i in range(n_puntos):
            hora = i * INTERVALO / 3600
            ts_ns = (int(INICIO.timestamp()) + i * INTERVALO) * 1_000_000_000
            for nodo in nodos:
                # Incidente 2: el nodo muere en la hora 30.
                if nodo is nodo_muerto and hora >= 30:
                    continue

                nodo["temp_base"] += rnd.gauss(0, 0.03)
                nodo["bateria"] = max(5.0, nodo["bateria"] - abs(rnd.gauss(0.005, 0.002)))
                extra = 0.0
                # Incidente 1: ola de calor en LC-02, horas 20→26 (sube, meseta, baja).
                if nodo["aula"] == "LC-02" and 20 <= hora < 26:
                    if hora < 22:
                        extra = (hora - 20) / 2 * 11          # rampa a +11 °C
                    elif hora < 24:
                        extra = 11 + rnd.gauss(0, 0.4)        # meseta ~35 °C
                    else:
                        extra = (26 - hora) / 2 * 11          # regreso
                # Pico FALSO: hora 10, dura 20 min (no debe alertar con for:15m).
                if nodo["aula"] == "LC-01" and 10 <= hora < 10.34:
                    extra = 8.0

                temp = fake.temperatura_c(base=nodo["temp_base"] + extra, ruido=0.3)
                f.write(f"ambiente,dispositivo={nodo['id']},aula={nodo['aula']} "
                        f"temperatura={temp},humedad={fake.humedad_pct()},"
                        f"bateria={int(nodo['bateria'])}i {ts_ns}\n")

    bitacora = [
        "BITÁCORA DE LA VERDAD (no la compartas hasta calificar):",
        "",
        "Hora 10.0–10.3   PICO FALSO en LC-01 (~31 °C, 20 min).",
        "                 Una alerta con `for: 15m+` NO debe disparar. (20 min > 15… ",
        "                 pruébalo: ¿dispara la tuya? ¿debería?)",
        "Hora 20–26       OLA DE CALOR en LC-02: rampa 2 h, meseta ~35 °C 2 h, regreso.",
        "                 La alerta de temperatura DEBE disparar en la meseta.",
        f"Hora 30          CAÍDA del nodo {nodo_muerto['id']} (LAB-IOT): deja de",
        "                 reportar y no regresa. La alerta 'no data' DEBE disparar.",
        "",
        "El resto de las 48 h es operación normal: cero alertas esperadas.",
    ]
    (args.salida / "incidentes.txt").write_text("\n".join(bitacora) + "\n",
                                                encoding="utf-8")

    sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
    print(f"48 h de telemetría, {len(nodos)} nodos, en {ruta}")
    print(f"Nodo que muere en hora 30: {nodo_muerto['id']}")
    print(f"SHA-256: {sha[:16]}…")
    print(f"Cargar:  influx write --bucket iot --file {ruta}")


if __name__ == "__main__":
    main()
