#!/usr/bin/env python3
"""Práctica LI-06 — Búsqueda binaria: consulta de inventario por número de serie.

Escenario real: el sistema de almacén consulta números de serie contra un
catálogo ORDENADO de 200 entradas. Recorrerlo completo (búsqueda lineal)
funciona… hasta que el catálogo crece. Tu programa implementa búsqueda
binaria sobre una tabla en .data.

Salida:
    salida/datos.s        .data con: catalogo (200 u64 ordenados), n_catalogo,
                          busquedas (24 u64, 1/3 inexistentes), n_busquedas
    salida/esperado.bin   por cada búsqueda, un u64 little-endian: el ÍNDICE
                          donde está el serial, o 0xFFFFFFFFFFFFFFFF si no existe

Tu programa: por cada serial en `busquedas`, búsqueda binaria en `catalogo`
y write() del índice (8 bytes LE) a stdout.

Autoverificación:
    ./programa > salida.bin && cmp salida.bin salida/esperado.bin

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py busqueda --seed 2026

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
import struct
from pathlib import Path

from faker import Faker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=200,
                        help="tamaño del catálogo (default 200)")
    parser.add_argument("--busquedas", type=int, default=24,
                        help="cantidad de consultas (default 24)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker()
    Faker.seed(args.seed)
    rnd = fake.random

    # Seriales u64 únicos y ORDENADOS (precondición de la búsqueda binaria).
    catalogo = sorted(rnd.sample(range(10**12, 10**13), args.n))

    # 2/3 de consultas existentes, 1/3 inexistentes — incluyendo los extremos
    # (primero, último) y vecinos de frontera, los casos que rompen el lazo.
    existentes = [catalogo[0], catalogo[-1]] + rnd.sample(catalogo, args.busquedas * 2 // 3 - 2)
    inexistentes = [catalogo[0] - 1, catalogo[-1] + 1]
    while len(inexistentes) < args.busquedas - len(existentes):
        v = rnd.randrange(10**12, 10**13)
        if v not in catalogo:
            inexistentes.append(v)
    busquedas = existentes + inexistentes
    rnd.shuffle(busquedas)

    indice = {v: i for i, v in enumerate(catalogo)}
    resultados = [indice.get(b, 0xFFFFFFFFFFFFFFFF) for b in busquedas]

    args.salida.mkdir(exist_ok=True)

    lineas = ["// Generado por generar_tabla.py — NO editar a mano.",
              f"// seed={args.seed} n={args.n} busquedas={args.busquedas}",
              "    .data",
              "    .global catalogo, n_catalogo, busquedas, n_busquedas",
              "catalogo:"]
    for i in range(0, args.n, 4):
        lineas.append("    .xword " + ", ".join(str(v) for v in catalogo[i:i + 4]))
    lineas += ["n_catalogo:", f"    .xword {args.n}", "busquedas:"]
    for i in range(0, len(busquedas), 4):
        lineas.append("    .xword " + ", ".join(str(v) for v in busquedas[i:i + 4]))
    lineas += ["n_busquedas:", f"    .xword {len(busquedas)}", ""]
    (args.salida / "datos.s").write_text("\n".join(lineas), encoding="utf-8")

    (args.salida / "esperado.bin").write_bytes(
        struct.pack(f"<{len(resultados)}Q", *resultados))

    n_no = sum(1 for r in resultados if r == 0xFFFFFFFFFFFFFFFF)
    print(f"Catálogo de {args.n} seriales, {len(busquedas)} consultas "
          f"({n_no} inexistentes) en {args.salida}/")
    print("Verifica:  ./programa > salida.bin && cmp salida.bin salida/esperado.bin")


if __name__ == "__main__":
    main()
