#!/usr/bin/env python3
"""Lección 04 — El catálogo de providers que usaremos en las materias.

Objetivo: conocer los "fakes" de serie más útiles para Lenguajes de Interfaz
y Sistemas Programables, agrupados por para qué sirven.

Ejecución:
    .venv/bin/python modulo00_intro_faker/04_providers_utiles.py

Tip: la lista completa está en https://faker.readthedocs.io/ y también con
`python -c "from faker import Faker; print([m for m in dir(Faker()) if not m.startswith('_')])"`
"""

from datetime import datetime, timezone

from faker import Faker

fake = Faker("es_MX")
Faker.seed(2026)
FECHA_REFERENCIA = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
FECHA_INICIO = datetime(2026, 6, 24, 0, 0, 0, tzinfo=timezone.utc)

print("=== Números y bytes (assembly, buffers, tramas) ===")
print("random_int(0, 255):      ", fake.random_int(0, 255))
print("random_int 32 bits:      ", fake.random_int(-2**31, 2**31 - 1))
print("hexify('BE:^^:^^'):      ", fake.hexify("BE:^^:^^"))       # ^ = dígito hex
print("numerify('SN-####'):     ", fake.numerify("SN-####"))      # # = dígito
print("bothify('LOTE-??##'):    ", fake.bothify("LOTE-??##"))     # ? = letra
print("binary(8) bytes crudos:  ", fake.binary(length=8).hex(" "))

print("\n=== Identidad de dispositivos (IoT) ===")
print("mac_address():           ", fake.mac_address())
print("ipv4_private():          ", fake.ipv4_private())
print("uuid4():                 ", fake.uuid4())
print("port_number():           ", fake.port_number())
print("sha256() (token/firma):  ", fake.sha256()[:32], "…")

print("\n=== Tiempo (series de tiempo, logs, InfluxDB) ===")
print("unix_time fijo:          ", fake.unix_time(end_datetime=FECHA_REFERENCIA))
print("iso8601 fijo:            ", fake.iso8601(end_datetime=FECHA_REFERENCIA))
print("date_time_between fijo:  ", fake.date_time_between(
    FECHA_INICIO, FECHA_REFERENCIA))

print("\n=== Geografía (GPS, NMEA, geo-tagging) ===")
print("latitude(), longitude(): ", fake.latitude(), fake.longitude())
print("local_latlng('MX'):      ", fake.local_latlng(country_code="MX"))

print("\n=== Ruido numérico controlado (sensores) ===")
# fake.random es el generador ya sembrado: gauss(media, desviación).
lecturas = [round(25.0 + fake.random.gauss(0, 0.5), 2) for _ in range(5)]
print("Temperaturas ~25°C ±0.5: ", lecturas)
