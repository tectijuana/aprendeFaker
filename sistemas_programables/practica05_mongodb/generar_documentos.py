#!/usr/bin/env python3
"""Práctica 05 — Documentos para MongoDB: modelado NoSQL de una flota IoT.

Genera dos colecciones en JSON Lines (un documento por línea, formato de
mongoimport) que contrastan los dos patrones de modelado NoSQL:

  salida/dispositivos.jsonl  documentos RICOS y anidados: ficha del nodo con
                             subdocumento ubicacion, arreglo sensores[] y el
                             ultimo_estado EMBEBIDO (patrón "embed")
  salida/eventos.jsonl       documentos PLANOS y pequeños que referencian al
                             nodo por id_dispositivo (patrón "reference")

La pregunta de la práctica es cuándo conviene cada patrón — exactamente la
decisión que en SQL no existe (ahí todo es tabla y JOIN, práctica 02).

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python sistemas_programables/practica05_mongodb/generar_documentos.py \
        --seed 2026 --dispositivos 12 --eventos 40

Reproducible: misma semilla → mismos archivos byte a byte (imprime SHA-256).
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider

TS0 = 1782864000  # 2026-07-01 00:00:00 UTC, fijo por reproducibilidad
AULAS = ["LC-01", "LC-02", "LAB-IOT", "LAB-ELEC"]
EDIFICIOS = {"LC-01": "Edificio LC", "LC-02": "Edificio LC",
             "LAB-IOT": "Posgrado", "LAB-ELEC": "Edificio E"}
TIPOS_EVENTO = ["arranque", "bateria_baja", "sin_senal", "lectura_fuera_de_rango",
                "actualizacion_fw"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--dispositivos", type=int, default=12,
                        help="nodos Pico W en la flota (default 12)")
    parser.add_argument("--eventos", type=int, default=40,
                        help="eventos por dispositivo (default 40)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)
    rnd = fake.random

    args.salida.mkdir(exist_ok=True)

    # ---- Colección 1: dispositivos (documentos ricos, patrón "embed") -----
    dispositivos = []
    for _ in range(args.dispositivos):
        aula = fake.random_element(AULAS)
        # No todos los nodos llevan los mismos sensores: los documentos NO
        # comparten esquema rígido — eso es lo normal (y lo cómodo) en NoSQL.
        sensores = [{"tipo": "DHT22", "magnitudes": ["temperatura", "humedad"]}]
        if rnd.random() < 0.5:
            sensores.append({"tipo": "MPU6050", "magnitudes": ["aceleracion"]})
        if rnd.random() < 0.3:
            sensores.append({"tipo": "BH1750", "magnitudes": ["luz"]})
        # Coordenadas de una ciudad real de México (GeoJSON: [lon, lat]).
        lat, lon, ciudad, _, _ = fake.local_latlng(country_code="MX")
        dispositivos.append({
            "_id": fake.id_dispositivo(),          # nuestro id como _id natural
            "mac": fake.mac_pico(),
            "fw": f"v1.{fake.random_int(0, 9)}",
            "ubicacion": {                          # subdocumento anidado
                "aula": aula,
                "edificio": EDIFICIOS[aula],
                "campus": ciudad,
                "coordenadas": [float(lon), float(lat)],
            },
            "responsable": {"nombre": fake.name(), "correo": fake.email()},
            "sensores": sensores,                   # arreglo de subdocumentos
            "ultimo_estado": {                      # embebido: 1 consulta = ficha completa
                "ts": TS0,
                "temperatura": fake.temperatura_c(),
                "bateria": fake.bateria_pct(),
            },
        })

    ruta_disp = args.salida / "dispositivos.jsonl"
    with ruta_disp.open("w", encoding="utf-8") as f:
        for d in dispositivos:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    # ---- Colección 2: eventos (documentos planos, patrón "reference") -----
    ruta_ev = args.salida / "eventos.jsonl"
    with ruta_ev.open("w", encoding="utf-8") as f:
        for d in dispositivos:
            ts = TS0
            for _ in range(args.eventos):
                ts += fake.random_int(300, 7200)   # entre 5 min y 2 h después
                tipo = fake.random_element(TIPOS_EVENTO)
                ev = {"id_dispositivo": d["_id"],  # referencia, no embebido
                      "tipo": tipo, "ts": ts}
                if tipo == "bateria_baja":
                    ev["bateria"] = fake.random_int(5, 19)
                elif tipo == "lectura_fuera_de_rango":
                    ev["valor"] = fake.temperatura_c(base=55.0, ruido=8.0)
                elif tipo == "actualizacion_fw":
                    ev["fw_nuevo"] = f"v1.{fake.random_int(0, 9)}"
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    for ruta in (ruta_disp, ruta_ev):
        n = sum(1 for _ in ruta.open())
        sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
        print(f"{ruta.name:20s} {n:5d} documentos  SHA-256 {sha[:16]}…")
    print("\nImportar:")
    print(f"  mongoimport --db iot --collection dispositivos --file {ruta_disp}")
    print(f"  mongoimport --db iot --collection eventos --file {ruta_ev}")


if __name__ == "__main__":
    main()
