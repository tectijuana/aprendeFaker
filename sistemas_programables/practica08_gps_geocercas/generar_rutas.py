#!/usr/bin/env python3
"""Práctica SP-08 — Rastreo GPS de transporte universitario con geocercas.

Escenario real: dos rutas del transporte de la universidad reportan posición
GPS cada 30 s. El sistema debe detectar: llegadas al campus (geocerca),
desvíos de ruta y pérdidas de señal — con consultas geoespaciales de MongoDB.

Genera:
    salida/posiciones.jsonl   colección para mongoimport: un doc por fix
                              {unidad, ts, loc: {type: Point, coordinates: [lon, lat]},
                               velocidad_kmh}  (GeoJSON: ¡lon primero!)
    salida/geocercas.jsonl    2 geocercas: campus TecNM Tijuana (círculo de
                              300 m como polígono) y la base de salida

Eventos inyectados (documentados al final de la corrida):
    * la unidad U2 se DESVÍA de la ruta a la mitad del recorrido
    * la unidad U1 PIERDE SEÑAL 5 minutos (hueco en los timestamps)

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py gps --seed 2026

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
import json
import math
from pathlib import Path

from faker import Faker

TS0 = 1782885600  # 2026-07-01 06:00:00 UTC — salida de la primera corrida
CAMPUS = (-117.0186, 32.5327)     # (lon, lat) TecNM Tijuana
BASE = (-116.9650, 32.5090)       # cochera de salida (Otay)
INTERVALO = 30                    # un fix cada 30 s


def circulo(centro, radio_m, n=16):
    """Polígono GeoJSON aproximando un círculo (radio en metros)."""
    lon0, lat0 = centro
    dlat = radio_m / 111320.0
    dlon = radio_m / (111320.0 * math.cos(math.radians(lat0)))
    pts = [[round(lon0 + dlon * math.cos(2 * math.pi * i / n), 6),
            round(lat0 + dlat * math.sin(2 * math.pi * i / n), 6)]
           for i in range(n)]
    return pts + [pts[0]]         # anillo cerrado


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--fixes", type=int, default=60,
                        help="fixes por unidad (default 60 = 30 min de ruta)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    Faker.seed(args.seed)
    rnd = fake.random

    args.salida.mkdir(exist_ok=True)

    docs = []
    for unidad, desvia in (("U1", False), ("U2", True)):
        lon, lat = BASE
        # Rumbo hacia el campus, en pasos iguales con jitter de GPS.
        dlon = (CAMPUS[0] - BASE[0]) / args.fixes
        dlat = (CAMPUS[1] - BASE[1]) / args.fixes
        for i in range(args.fixes):
            # U1 pierde señal 5 min (10 fixes) a partir del fix 20.
            if unidad == "U1" and 20 <= i < 30:
                continue
            # U2 se desvía: a partir de la mitad toma rumbo perpendicular.
            if desvia and i >= args.fixes // 2:
                lon += dlat * 1.5 + rnd.gauss(0, 0.00008)
                lat += -dlon * 1.5 + rnd.gauss(0, 0.00008)
            else:
                lon += dlon + rnd.gauss(0, 0.00008)
                lat += dlat + rnd.gauss(0, 0.00008)
            docs.append({
                "unidad": unidad,
                "ts": TS0 + i * INTERVALO,
                "loc": {"type": "Point",
                        "coordinates": [round(lon, 6), round(lat, 6)]},
                "velocidad_kmh": round(max(0.0, rnd.gauss(38, 6)), 1),
            })

    with (args.salida / "posiciones.jsonl").open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    geocercas = [
        {"nombre": "campus", "descripcion": "TecNM Tijuana, radio 300 m",
         "area": {"type": "Polygon", "coordinates": [circulo(CAMPUS, 300)]}},
        {"nombre": "base", "descripcion": "Cochera de salida (Otay), radio 150 m",
         "area": {"type": "Polygon", "coordinates": [circulo(BASE, 150)]}},
    ]
    with (args.salida / "geocercas.jsonl").open("w", encoding="utf-8") as f:
        for g in geocercas:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

    print(f"{len(docs)} posiciones de 2 unidades en {args.salida}/")
    print("Eventos: U2 se desvía a mitad de ruta; U1 pierde señal 5 min (fix 20).")
    print("Importar:")
    print("  mongoimport --db transporte --collection posiciones "
          "--file salida/posiciones.jsonl")
    print("  mongoimport --db transporte --collection geocercas "
          "--file salida/geocercas.jsonl")


if __name__ == "__main__":
    main()
