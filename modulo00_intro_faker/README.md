# Módulo 00 — Domina Faker

Antes de usar los generadores de las prácticas, trabaja este módulo. Son 5 scripts
cortos que se leen y ejecutan en orden; cada uno enseña un concepto que las prácticas
dan por sabido. Al final resuelve `EJERCICIOS.md`.

## ¿Qué es Faker?

Faker es el comando de terminal que usaremos para generar **datos ficticios pero
realistas**: nombres, direcciones, coordenadas, direcciones MAC, timestamps, texto…
En estas materias lo usaremos como herramienta de mockup data para fabricar buffers
para programas en ensamblador, lecturas de sensores y registros para bases de datos.

**¿Por qué no inventar los datos a mano?** Porque 5 datos escritos a mano no revelan
errores; 10,000 datos generados sí. Y porque con una **semilla** los datos son
reproducibles: todos en el grupo generamos exactamente lo mismo.

## Los dos modos de uso

**1. CLI (terminal)** — rápido, para explorar:

```bash
faker name                      # un nombre
faker -l es_MX name             # un nombre mexicano
faker -r 5 -s $'\n' address     # 5 direcciones
faker --seed 42 name            # reproducible: siempre "Allison Hill" en en_US
faker -o datos.txt -r 100 city  # 100 ciudades a un archivo
```

**2. Generadores del repo** — scripts ejecutables que usan Faker por dentro para dar
formato exacto a la salida:

```python
from faker import Faker

fake = Faker("es_MX")   # locale de México
Faker.seed(42)          # ¡semilla ANTES de generar!
print(fake.name())
```

## Lecciones (ejecuta en orden desde la raíz del repo)

| Script | Concepto |
|---|---|
| `01_hola_faker.py` | Crear la instancia, generar los fakes básicos |
| `02_semillas_reproducibles.py` | Por qué `Faker.seed()` lo cambia todo |
| `03_locales.py` | es_MX vs en_US vs ja_JP: datos localizados |
| `04_providers_utiles.py` | El catálogo que usaremos: hex, MAC, timestamps, coordenadas |
| `05_provider_personalizado.py` | Escribir tu propio provider (sensor de temperatura) |

```bash
.venv/bin/python modulo00_intro_faker/01_hola_faker.py
```

## Errores clásicos (no los cometas)

1. **Sembrar después de generar.** `Faker.seed(n)` debe ir antes del primer `fake.algo()`.
2. **Confundir `Faker.seed(n)` (método de clase) con `fake.seed_instance(n)`.** Para
   estos ejercicios usa `Faker.seed(n)`; ambas funcionan, pero mezcla de ambas = caos.
3. **Esperar que el mismo seed dé lo mismo en locales distintos.** El seed fija el
   generador aleatorio, pero cada locale tiene catálogos diferentes.
4. **Usar `random.random()` junto a Faker sin sembrarlo.** Si necesitas ruido numérico,
   usa `fake.random.gauss(...)` — usa el mismo generador ya sembrado.
