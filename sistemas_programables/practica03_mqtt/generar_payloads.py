#!/usr/bin/env python3
"""Práctica 03 — Payloads MQTT: publicar y suscribirse a telemetría.

Genera los mensajes que una red de nodos Raspberry Pi Pico W / Pico 2 W
(físicos o simulados en Wokwi) publicaría por MQTT, y el
script que los publica con mosquitto_pub respetando la cadencia real:

  salida/payloads.jsonl   un mensaje por línea: {"topic": ..., "payload": {...}}
  salida/publicar.sh      publica todo con mosquitto_pub (usa --pausa para simular tiempo real)

Jerarquía de topics de la práctica (obsérvala en el suscriptor con comodines):
    tec/<aula>/<id_dispositivo>/ambiente     (telemetría periódica)
    tec/<aula>/<id_dispositivo>/estado       (eventos: arranque, batería baja)

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python sistemas_programables/practica03_mqtt/generar_payloads.py \
        --seed 2026 --dispositivos 3 --mensajes 30

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

AULAS = ["LC-01", "LC-02", "LAB-IOT"]
TS0 = 1782864000  # 2026-07-01 00:00:00 UTC, fijo por reproducibilidad


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--dispositivos", type=int, default=3,
                        help="nodos Pico W (default 3)")
    parser.add_argument("--mensajes", type=int, default=30,
                        help="mensajes de ambiente por nodo (default 30)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)

    nodos = [{"id": fake.id_dispositivo(),
              "aula": fake.random_element(AULAS),
              "bateria": float(fake.bateria_pct()),
              "temp_base": 22.0 + fake.random.uniform(0, 4)}
             for _ in range(args.dispositivos)]

    mensajes = []
    # Evento de arranque de cada nodo (retained: el suscriptor tardío lo ve).
    for n in nodos:
        mensajes.append({
            "topic": f"tec/{n['aula']}/{n['id']}/estado",
            "retain": True,
            "payload": {"evento": "arranque", "fw": f"v1.{fake.random_int(0, 9)}",
                        "ip": fake.ipv4_private(), "ts": TS0},
        })
    # Telemetría periódica intercalada por tiempo.
    for i in range(args.mensajes):
        ts = TS0 + (i + 1) * 60
        for n in nodos:
            n["bateria"] = max(5.0, n["bateria"] - abs(fake.random.gauss(0.05, 0.02)))
            mensajes.append({
                "topic": f"tec/{n['aula']}/{n['id']}/ambiente",
                "retain": False,
                "payload": {"t": fake.temperatura_c(base=n["temp_base"]),
                            "h": fake.humedad_pct(),
                            "bat": int(n["bateria"]), "ts": ts},
            })
            if n["bateria"] < 20 and fake.random.random() < 0.1:
                mensajes.append({
                    "topic": f"tec/{n['aula']}/{n['id']}/estado",
                    "retain": False,
                    "payload": {"evento": "bateria_baja", "bat": int(n["bateria"]), "ts": ts},
                })

    args.salida.mkdir(exist_ok=True)

    ruta_jsonl = args.salida / "payloads.jsonl"
    with ruta_jsonl.open("w", encoding="utf-8") as f:
        for m in mensajes:
            f.write(json.dumps(m, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Script publicador: JSON compacto en comilla simple; -r para retained.
    lineas = ["#!/bin/bash",
              "# Generado por generar_payloads.py — publica la telemetría con mosquitto_pub.",
              "# Uso: ./publicar.sh [broker] [pausa_segundos]   (default: localhost, sin pausa)",
              'BROKER="${1:-localhost}"', 'PAUSA="${2:-0}"', ""]
    for m in mensajes:
        pl = json.dumps(m["payload"], ensure_ascii=False, separators=(",", ":"))
        r = " -r" if m["retain"] else ""
        lineas.append(f"mosquitto_pub -h \"$BROKER\"{r} -t '{m['topic']}' -m '{pl}'")
        lineas.append('sleep "$PAUSA"')
    ruta_sh = args.salida / "publicar.sh"
    ruta_sh.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    ruta_sh.chmod(0o755)

    for ruta in (ruta_jsonl, ruta_sh):
        sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
        print(f"{ruta.name:16s} SHA-256 {sha[:16]}…")
    print(f"\n{len(mensajes)} mensajes ({args.dispositivos} nodos) en {args.salida}/")
    print("Suscríbete primero:  mosquitto_sub -h localhost -t 'tec/#' -v")
    print(f"Publica después:     {ruta_sh} localhost 0.2")


if __name__ == "__main__":
    main()
