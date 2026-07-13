#!/usr/bin/env python3
"""Práctica LI-02 — Parseo de stdin: caja de un kiosco de pagos.

Escenario real: un kiosco recibe por teclado montos en centavos, uno por
línea. El firmware debe parsear cada línea, DESCARTAR las inválidas (así
llegan de un teclado real) y reportar el corte de caja.

Una línea es VÁLIDA solo si: contiene puros dígitos ASCII ('0'-'9'), no está
vacía, y su valor cabe en 32 bits sin signo (≤ 4294967295). Todo lo demás se
descarta: vacías, signo negativo, letras, espacios, overflow.

Salida:
    salida/entrada.txt    las líneas capturadas (≈15 % inválidas, con TODOS
                          los casos límite del CLAUDE.md)
    salida/esperado.txt   una sola línea: "<validas> <suma>\\n" en decimal

Autoverificación:
    ./programa < salida/entrada.txt > salida.txt && cmp salida.txt salida/esperado.txt

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py stdin --seed 2026 --n 50

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
from pathlib import Path

from faker import Faker


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=50,
                        help="cantidad de líneas (default 50)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker()
    Faker.seed(args.seed)
    rnd = fake.random

    # Generadores de líneas inválidas: los errores típicos de captura.
    invalidas = [
        lambda: "",                                        # Enter en vacío
        lambda: f"-{fake.random_int(1, 99999)}",           # signo negativo
        lambda: fake.numerify("##a##"),                    # letra colada
        lambda: f" {fake.random_int(1, 9999)}",            # espacio inicial
        lambda: f"{fake.random_int(1, 999)} ",             # espacio final
        lambda: str(fake.random_int(2**32, 2**33)),        # overflow de 32 bits
        lambda: fake.numerify("##.##"),                    # punto decimal
    ]

    # Cobertura GARANTIZADA: cada tipo de inválida aparece al menos una vez,
    # más el máximo válido exacto de 32 bits. El resto se rellena al azar.
    lineas = [gen() for gen in invalidas] + ["4294967295"]
    while len(lineas) < args.n:
        if rnd.random() < 0.08:
            lineas.append(rnd.choice(invalidas)())
        else:
            # Montos plausibles de kiosco, en centavos (de $1.00 a $9,999.99).
            lineas.append(str(fake.random_int(100, 999999)))
    rnd.shuffle(lineas)  # que los casos límite no queden todos al inicio

    def es_valida(s: str) -> bool:
        return s.isdigit() and s.isascii() and int(s) <= 4294967295

    validas = [int(s) for s in lineas if es_valida(s)]

    args.salida.mkdir(exist_ok=True)
    (args.salida / "entrada.txt").write_text("\n".join(lineas) + "\n", encoding="ascii")
    (args.salida / "esperado.txt").write_text(
        f"{len(validas)} {sum(validas)}\n", encoding="ascii")

    print(f"{args.n} líneas ({args.n - len(validas)} inválidas) en {args.salida}/")
    print(f"Corte esperado: {len(validas)} válidas, suma {sum(validas)}")
    print("Verifica:  ./programa < salida/entrada.txt > salida.txt "
          "&& cmp salida.txt salida/esperado.txt")


if __name__ == "__main__":
    main()
