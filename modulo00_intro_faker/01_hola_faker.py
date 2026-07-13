#!/usr/bin/env python3
"""Lección 01 — Hola Faker.

Objetivo: crear una instancia de Faker y generar los datos básicos.

Ejecución (desde la raíz del repo):
    .venv/bin/python modulo00_intro_faker/01_hola_faker.py
"""

from faker import Faker

# Una sola instancia por script es la mejor práctica: crearla es costoso
# (carga catálogos de datos) y todas las llamadas comparten el mismo
# generador aleatorio.
fake = Faker("es_MX")

print("=== Datos de una persona ficticia ===")
print("Nombre:    ", fake.name())
print("Dirección: ", fake.address().replace("\n", " / "))
print("Teléfono:  ", fake.phone_number())
print("Correo:    ", fake.email())
print("CURP-like: ", fake.bothify("????######???").upper())  # patrón, no CURP real

print("\n=== Datos de un dispositivo ficticio ===")
print("MAC:       ", fake.mac_address())
print("IPv4 priv.:", fake.ipv4_private())
print("UUID:      ", fake.uuid4())
print("Timestamp: ", fake.iso8601())

print("\nVuelve a ejecutar el script: los datos CAMBIAN cada vez.")
print("En la lección 02 aprenderás a congelarlos con una semilla.")
