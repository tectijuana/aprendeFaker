#!/usr/bin/env python3
"""Práctica SP-06 — Requests para una API REST de telemetría (Flask).

Escenario real: los nodos Pico W hacen POST de su telemetría a un backend.
Tú construyes la API en Flask; este generador fabrica el tráfico que la
golpeará — incluyendo lo que llega en producción: JSON roto, campos
faltantes, tipos incorrectos y valores fuera de rango físico.

Salida:
    salida/requests.jsonl  cada línea: {"caso": n, "payload": <str crudo>,
                           "esperado": <status HTTP que TU API debe devolver>}
    salida/enviar.sh       los POST con curl, mostrando el status recibido
                           vs el esperado (PASA/FALLA por caso)

Contrato de la API (POST /api/lecturas):
    JSON: {"dispositivo": "PICOW-XXXXXX", "temperatura": float, "humedad": float}
    201 creado | 400 JSON inválido o campos faltantes/mal tipados |
    422 valores fuera de rango físico (temp -40..85, hum 0..100)

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py rest --seed 2026 --n 30

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=30,
                        help="cantidad de requests (default 30)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)
    rnd = fake.random

    def valido():
        return json.dumps({"dispositivo": fake.id_dispositivo(),
                           "temperatura": fake.temperatura_c(),
                           "humedad": fake.humedad_pct()}), 201

    # Lo que llega en producción — cada generador devuelve (payload, esperado).
    malos = [
        lambda: ('{"dispositivo": "' + fake.id_dispositivo() + '", "temperatura": 23.5',
                 400),                                            # JSON truncado
        lambda: (json.dumps({"dispositivo": fake.id_dispositivo(),
                             "temperatura": fake.temperatura_c()}), 400),  # falta humedad
        lambda: (json.dumps({"dispositivo": fake.id_dispositivo(),
                             "temperatura": "veintitres",
                             "humedad": fake.humedad_pct()}), 400),        # tipo incorrecto
        lambda: (json.dumps({"device": fake.id_dispositivo(),
                             "temperatura": fake.temperatura_c(),
                             "humedad": fake.humedad_pct()}), 400),        # campo mal nombrado
        lambda: (json.dumps({"dispositivo": fake.id_dispositivo(),
                             "temperatura": 999.0,
                             "humedad": fake.humedad_pct()}), 422),        # temp imposible
        lambda: (json.dumps({"dispositivo": fake.id_dispositivo(),
                             "temperatura": fake.temperatura_c(),
                             "humedad": 150.0}), 422),                     # humedad imposible
        lambda: ("no soy json", 400),
    ]

    # Cobertura garantizada: cada caso malo al menos una vez; resto 70/30.
    casos = [m() for m in malos]
    while len(casos) < args.n:
        casos.append(valido() if rnd.random() < 0.7 else rnd.choice(malos)())
    rnd.shuffle(casos)

    args.salida.mkdir(exist_ok=True)
    with (args.salida / "requests.jsonl").open("w", encoding="utf-8") as f:
        for i, (payload, esperado) in enumerate(casos):
            f.write(json.dumps({"caso": i, "payload": payload,
                                "esperado": esperado}, ensure_ascii=False) + "\n")

    lineas = ["#!/bin/bash",
              "# Generado por generar_requests.py — golpea tu API y califica caso por caso.",
              "# Uso: ./enviar.sh [url]   (default: http://localhost:5000/api/lecturas)",
              'URL="${1:-http://localhost:5000/api/lecturas}"', "FALLAS=0", ""]
    for i, (payload, esperado) in enumerate(casos):
        pl = payload.replace("'", "'\\''")
        lineas += [
            f"CODIGO=$(curl -s -o /dev/null -w '%{{http_code}}' -X POST "
            f"-H 'Content-Type: application/json' -d '{pl}' \"$URL\")",
            f"if [ \"$CODIGO\" = \"{esperado}\" ]; then echo \"caso {i:02d}: PASA ({esperado})\"; "
            f"else echo \"caso {i:02d}: FALLA (esperado {esperado}, recibido $CODIGO)\"; "
            f"FALLAS=$((FALLAS+1)); fi",
        ]
    lineas += ["", 'echo; if [ "$FALLAS" -eq 0 ]; then echo "CORRECTO ✔ (todos los casos)"; '
               'else echo "INCORRECTO ✘ ($FALLAS casos fallan)"; fi']
    sh = args.salida / "enviar.sh"
    sh.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    sh.chmod(0o755)

    n201 = sum(1 for _, e in casos if e == 201)
    print(f"{len(casos)} requests ({n201} válidos, {len(casos) - n201} con error) "
          f"en {args.salida}/")
    print("Arranca tu API Flask y corre:  ./salida/enviar.sh")


if __name__ == "__main__":
    main()
