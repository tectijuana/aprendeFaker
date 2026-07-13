#!/usr/bin/env python3
"""Práctica 01 — Generador de datos: ordenamiento de enteros en ARM64.

Genera el mismo arreglo de enteros de 32 bits en tres presentaciones:

  salida/datos.s       bloque .data con directivas GAS (se ensambla junto a tu programa)
  salida/datos.bin     el arreglo crudo little-endian (para inspección con xxd)
  salida/esperado.bin  el arreglo YA ordenado, crudo little-endian — tu programa
                       debe producir exactamente estos bytes en stdout

Autoverificación del alumno:
    ./programa > salida.bin && cmp salida.bin salida/esperado.bin && echo CORRECTO

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python lenguajes_interfaz/practica01_ordenamiento_arm64/generar_datos.py \
        --seed 2026 --n 16

Misma semilla y misma n → mismos datos para todo el grupo.
"""

import argparse
import struct
from pathlib import Path

from faker import Faker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=16,
                        help="cantidad de enteros de 32 bits (default 16)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker()
    Faker.seed(args.seed)
    # Enteros de 32 bits CON signo: obliga a usar comparación con signo
    # (b.lt, no b.lo) — el error clásico de la práctica.
    datos = [fake.random_int(-(2**31), 2**31 - 1) for _ in range(args.n)]

    args.salida.mkdir(exist_ok=True)

    # 1) datos.s — bloque .data para ensamblar junto al programa del alumno.
    lineas = [
        "// Generado por generar_datos.py — NO editar a mano.",
        f"// seed={args.seed} n={args.n}",
        "    .data",
        "    .global arreglo",
        "    .global longitud",
        "arreglo:",
    ]
    for i in range(0, args.n, 4):
        grupo = ", ".join(str(v) for v in datos[i:i + 4])
        lineas.append(f"    .word {grupo}")
    lineas += ["longitud:", f"    .word {args.n}", ""]
    (args.salida / "datos.s").write_text("\n".join(lineas))

    # 2) datos.bin — mismos enteros, crudos, little-endian con signo.
    empaquetar = lambda vals: struct.pack(f"<{len(vals)}i", *vals)
    (args.salida / "datos.bin").write_bytes(empaquetar(datos))

    # 3) esperado.bin — la respuesta correcta: el arreglo ordenado ascendente.
    (args.salida / "esperado.bin").write_bytes(empaquetar(sorted(datos)))

    print(f"Generados {args.n} enteros de 32 bits (seed={args.seed}) en {args.salida}/")
    print("  datos.s       → ensámblalo junto a tu programa")
    print("  datos.bin     → inspección: xxd salida/datos.bin")
    print("  esperado.bin  → compara:   cmp salida.bin salida/esperado.bin")
    print(f"Primeros valores: {datos[:5]} …")


if __name__ == "__main__":
    main()
