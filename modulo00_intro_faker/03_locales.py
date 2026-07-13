#!/usr/bin/env python3
"""Lección 03 — Locales: datos con acento local.

Objetivo: ver que el locale cambia los catálogos (nombres, direcciones,
teléfonos) y entender dos consecuencias prácticas:

1. Para prácticas con datos "de aquí", usa es_MX.
2. Los datos localizados traen acentos, eñes y apellidos con apóstrofo:
   tu programa (o tu INSERT de SQL) debe soportar UTF-8 y escapar comillas.

Ejecución:
    .venv/bin/python modulo00_intro_faker/03_locales.py
"""

from faker import Faker

for locale in ("es_MX", "en_US", "ja_JP"):
    fake = Faker(locale)
    Faker.seed(2026)
    print(f"--- {locale} ---")
    print("  Nombre:   ", fake.name())
    print("  Ciudad:   ", fake.city())
    print("  Teléfono: ", fake.phone_number())

print("\nMismo seed (2026) en los tres, pero datos distintos: el seed fija el")
print("generador aleatorio, no los catálogos, y cada locale tiene los suyos.")

# Ojo con la codificación: los datos es_MX incluyen á, é, ñ… Si tu programa
# en ensamblador procesa estos bytes, recuerda que en UTF-8 una "ñ" son
# DOS bytes (0xC3 0xB1), no uno.
fake = Faker("es_MX")
Faker.seed(2)
nombre = fake.first_name()
print(f"\n'{nombre}' ocupa {len(nombre)} caracteres "
      f"pero {len(nombre.encode('utf-8'))} bytes en UTF-8.")
