#!/usr/bin/env python3
"""Práctica LI-03 — Registros en disco: padrón de nómina en archivo binario.

Escenario real: un sistema de nómina legado guarda el padrón de empleados en
un archivo binario de REGISTROS DE TAMAÑO FIJO (32 bytes), como los sistemas
COBOL/RPG que aún corren en bancos y gobierno. Tu programa en assembly debe
abrir el archivo, recorrer los registros y extraer el del empleado ACTIVO
mejor pagado.

Layout de cada registro (32 bytes, little-endian — ver salida/layout.txt):
    offset  tamaño  campo
    0       4       id        u32
    4       20      nombre    ASCII, relleno con \\0 (sin acentos: legado)
    24      4       salario   u32, quincenal en centavos
    28      1       activo    u8 (1 = activo, 0 = baja)
    29      3       relleno   \\0\\0\\0 (alineación a 32)

Salida:
    salida/empleados.bin   el padrón completo
    salida/esperado.bin    los 32 bytes del registro que tu programa debe emitir
    salida/layout.txt      el layout y el desglose hex del primer registro

Autoverificación:
    ./programa > salida.bin && cmp salida.bin salida/esperado.bin

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py disco --seed 2026 --n 30

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
import struct
import unicodedata
from pathlib import Path

from faker import Faker

FORMATO = "<I20sIB3x"          # id, nombre, salario, activo, 3 de relleno
TAMANO = struct.calcsize(FORMATO)   # 32 bytes


def ascii_legado(nombre: str) -> bytes:
    """Sin acentos ni eñes (NFD + descarte), truncado a 19 bytes + \\0 mínimo."""
    plano = unicodedata.normalize("NFD", nombre).encode("ascii", "ignore")
    return plano[:19]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=30,
                        help="cantidad de empleados (default 30)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    Faker.seed(args.seed)

    registros = []
    for i in range(args.n):
        registros.append({
            "id": 1000 + i,
            "nombre": ascii_legado(f"{fake.first_name()} {fake.last_name()}"),
            # Quincena en centavos: $4,000.00 a $28,000.00
            "salario": fake.random_int(400000, 2800000),
            "activo": 1 if fake.random.random() < 0.8 else 0,
        })

    # Trampa didáctica: el salario MÁXIMO del archivo es de un empleado dado
    # de baja — quien no filtre por `activo` entrega el registro equivocado.
    bajas = [r for r in registros if r["activo"] == 0]
    tope = max(r["salario"] for r in registros)
    bajas[0]["salario"] = tope + 100000

    empaquetados = [struct.pack(FORMATO, r["id"], r["nombre"],
                                r["salario"], r["activo"]) for r in registros]
    ganador = max((r for r in registros if r["activo"] == 1),
                  key=lambda r: r["salario"])
    esperado = empaquetados[registros.index(ganador)]

    args.salida.mkdir(exist_ok=True)
    (args.salida / "empleados.bin").write_bytes(b"".join(empaquetados))
    (args.salida / "esperado.bin").write_bytes(esperado)

    r0 = registros[0]
    desglose = [
        "Layout del registro (32 bytes, little-endian):",
        "  offset  tamaño  campo",
        "  0       4       id       u32",
        "  4       20      nombre   ASCII relleno con \\0",
        "  24      4       salario  u32 (quincena en centavos)",
        "  28      1       activo   u8 (1=activo, 0=baja)",
        "  29      3       relleno",
        "",
        f"Registro 0: id={r0['id']} nombre={r0['nombre'].decode()!r} "
        f"salario={r0['salario']} activo={r0['activo']}",
        "Hex:",
        " ".join(f"{b:02x}" for b in empaquetados[0]),
    ]
    (args.salida / "layout.txt").write_text("\n".join(desglose) + "\n", encoding="utf-8")

    activos = sum(r["activo"] for r in registros)
    print(f"{args.n} registros ({activos} activos) en {args.salida}/empleados.bin "
          f"({args.n * TAMANO} bytes)")
    print(f"Mejor pagado ACTIVO: id={ganador['id']} "
          f"{ganador['nombre'].decode()} (${ganador['salario'] / 100:,.2f})")
    print("Verifica:  ./programa > salida.bin && cmp salida.bin salida/esperado.bin")


if __name__ == "__main__":
    main()
