#!/usr/bin/env python3
"""Lección 02 — Semillas: la clave de la reproducibilidad.

Objetivo: entender que con `Faker.seed(n)` los datos "aleatorios" son
exactamente los mismos en tu máquina, la del profesor y la de tus compañeros.
Así, la salida de tu programa se puede comparar byte a byte contra la esperada.

Ejecución:
    .venv/bin/python modulo00_intro_faker/02_semillas_reproducibles.py
"""

from faker import Faker

fake = Faker("es_MX")

# REGLA: la semilla se fija ANTES de generar. Sembrar a la mitad reinicia
# la secuencia desde ese punto.
Faker.seed(2026)
primera_corrida = [fake.first_name() for _ in range(5)]

Faker.seed(2026)  # misma semilla → la secuencia se reinicia igual
segunda_corrida = [fake.first_name() for _ in range(5)]

print("Corrida 1:", primera_corrida)
print("Corrida 2:", segunda_corrida)
print("¿Idénticas?", primera_corrida == segunda_corrida)

Faker.seed(9999)  # semilla distinta → datos distintos
print("\nCon seed 9999:", [fake.first_name() for _ in range(5)])

# Mejor práctica del repo: la semilla llega por argumento, nunca "quemada"
# sin posibilidad de cambiarla. Patrón mínimo con argparse:
#
#     parser.add_argument("--seed", type=int, default=2026)
#     Faker.seed(args.seed)
#
# Todos los generadores de las prácticas siguen este patrón.

print("\nEjecuta el script varias veces: la salida NUNCA cambia.")
print("Eso es lo que permite calificar comparando contra una salida esperada.")
