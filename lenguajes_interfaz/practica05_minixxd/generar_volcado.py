#!/usr/bin/env python3
"""Práctica LI-05 — Mini-xxd: volcado hex forense de un binario.

Escenario real: análisis forense de una memoria USB decomisada — hay que
volcar un binario a hex legible para localizar evidencia (cadenas ASCII
escondidas entre bytes de relleno). Tu programa en assembly es un mini-xxd:
lee bytes de stdin y emite el volcado en este formato EXACTO:

    00000000: 4c 6f 20 71 75 65 20 65 6c 20 76 69 65 6e 74 6f
    00000010: 20 73 65 20 6c 6c 65 76  ...

(offset de 8 dígitos hex, ': ', 16 bytes en hex minúsculas separados por un
espacio, sin espacio final, '\\n'. La última línea puede traer menos de 16.)

Salida:
    salida/volcado.bin    el binario a analizar (con evidencia ASCII embebida)
    salida/esperado.txt   el volcado correcto — tu programa debe producirlo igual

Autoverificación:
    ./programa < salida/volcado.bin > salida.txt && cmp salida.txt salida/esperado.txt

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py xxd --seed 2026 --n 256

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
from pathlib import Path

from faker import Faker


def volcado_hex(data: bytes) -> str:
    lineas = []
    for off in range(0, len(data), 16):
        fila = data[off:off + 16]
        lineas.append(f"{off:08x}: " + " ".join(f"{b:02x}" for b in fila))
    return "\n".join(lineas) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=256,
                        help="tamaño del binario en bytes (default 256)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    Faker.seed(args.seed)
    rnd = fake.random

    # Relleno pseudoaleatorio con "evidencia" ASCII embebida en offsets al azar.
    data = bytearray(fake.binary(length=args.n))
    evidencias = [fake.name().encode("utf-8"),
                  fake.email().encode("ascii"),
                  b"CLAVE:" + fake.hexify("^^^^^^^^").upper().encode()]
    for ev in evidencias:
        off = rnd.randrange(0, max(1, args.n - len(ev)))
        data[off:off + len(ev)] = ev

    # n NO múltiplo de 16 a propósito: la última línea queda incompleta,
    # el caso que rompe los mini-xxd mal hechos.
    data = bytes(data[:args.n - 5])

    args.salida.mkdir(exist_ok=True)
    (args.salida / "volcado.bin").write_bytes(data)
    (args.salida / "esperado.txt").write_text(volcado_hex(data), encoding="utf-8")

    print(f"{len(data)} bytes en {args.salida}/volcado.bin "
          f"(última línea de {len(data) % 16} bytes — a propósito)")
    print(f"Evidencias embebidas: {len(evidencias)} (encuéntralas en el volcado)")
    print("Verifica:  ./programa < salida/volcado.bin > salida.txt "
          "&& cmp salida.txt salida/esperado.txt")


if __name__ == "__main__":
    main()
