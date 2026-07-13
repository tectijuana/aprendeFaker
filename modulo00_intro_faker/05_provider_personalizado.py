#!/usr/bin/env python3
"""Lección 05 — Escribe tu propio provider.

Objetivo: cuando Faker no trae el dato que necesitas (una lectura de sensor,
un número de serie con TU formato), se escribe un provider: una clase que
hereda de BaseProvider y cuyos métodos se vuelven `fake.mi_metodo()`.

Este script usa el provider real del repo (providers/sensores.py) y además
define uno mínimo aquí mismo para que veas la anatomía completa.

Ejecución (desde la raíz del repo, importa `providers/`):
    .venv/bin/python modulo00_intro_faker/05_provider_personalizado.py
"""

import sys
from pathlib import Path

# Permite importar providers/ al ejecutar desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faker import Faker
from faker.providers import BaseProvider

from providers.sensores import SensorProvider


# --- Anatomía mínima de un provider -----------------------------------------
class TramaProvider(BaseProvider):
    """Tramas serie estilo práctica: [0xAA][len][payload][checksum]."""

    def trama(self, n_bytes: int = 4) -> bytes:
        # self.generator es la instancia Faker: usa SU generador ya sembrado.
        payload = bytes(self.random_int(0, 255) for _ in range(n_bytes))
        checksum = sum(payload) & 0xFF
        return bytes([0xAA, n_bytes]) + payload + bytes([checksum])


fake = Faker("es_MX")
fake.add_provider(SensorProvider)   # el provider compartido del repo
fake.add_provider(TramaProvider)    # el definido arriba
Faker.seed(2026)

print("=== SensorProvider (providers/sensores.py) ===")
print("Dispositivo:  ", fake.id_dispositivo())
print("Temperatura:  ", fake.temperatura_c(), "°C")
print("Humedad:      ", fake.humedad_pct(), "%")
print("Aceleración:  ", fake.aceleracion_g(), "g")
print("Batería:      ", fake.bateria_pct(), "%")

print("\n=== TramaProvider (definido en esta lección) ===")
t = fake.trama(4)
print("Trama:        ", t.hex(" "))
print("Checksum OK:  ", sum(t[2:-1]) & 0xFF == t[-1])

print("\nReto: agrega a TramaProvider un parámetro `corrupta=True` que dañe")
print("el checksum a propósito. Lo usarás en la práctica de UART.")
