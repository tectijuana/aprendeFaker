# aprendeFaker

[![CI](https://github.com/tectijuana/aprendeFaker/actions/workflows/ci.yml/badge.svg)](https://github.com/tectijuana/aprendeFaker/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](requirements.txt)
[![Faker](https://img.shields.io/badge/faker-40.x-green)](https://faker.readthedocs.io/)

> **EN** — Reproducible synthetic-data generators (fixed seed, byte-exact
> verification) for teaching ARM64 assembly and the IoT stack (MQTT, InfluxDB,
> Grafana, MongoDB, SQL Server, ML). One CLI, self-grading labs, no hardware
> required. Docs are in Spanish (LATAM); contributions welcome — see
> [CONTRIBUTING.md](CONTRIBUTING.md).

Herramienta de línea de comandos basada en **Faker** para generar
**mockup data** realista en las prácticas de:

- **Lenguajes de Interfaz** — ensamblador ARM64/AArch64 (Ubuntu Server en AWS Academy)
- **Sistemas Programables** — IoT: sensores, InfluxDB, Grafana, NoSQL, SQL Server, AI/ML

El objetivo es que **te ahorres tiempo**: en lugar de inventar datos a mano o copiar
datasets de dudosa procedencia, generas datos reproducibles, plausibles y en el
formato exacto que tu programa necesita. Este repo no se usa como librería Python;
se usa como herramienta CLI y como colección de generadores ejecutables.

## Instalación (AWS Academy — Ubuntu Server)

```bash
sudo apt update && sudo apt install -y python3-venv
git clone https://github.com/tectijuana/aprendeFaker.git && cd aprendeFaker
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## El comando del repo: `aprendefaker`

Todos los generadores se invocan con **un solo comando de terminal con parámetros**:

```bash
.venv/bin/python aprendefaker.py            # ayuda: lista los subcomandos
.venv/bin/python aprendefaker.py influx --seed 2026 --dispositivos 3 --horas 24
.venv/bin/python aprendefaker.py asm --seed 2026 --n 16
.venv/bin/python aprendefaker.py mssql -h   # parámetros de cada subcomando
```

Subcomandos: `asm` (assembly ARM64), `influx`, `mssql`, `mqtt`, `dataset` (AI/ML),
`mongo`. Cada uno acepta `--seed` (default 2026) y escribe en la carpeta `salida/`
de su práctica. Con el venv activado (`source .venv/bin/activate`) basta
`./aprendefaker.py <subcomando>`.

Para usar el CLI de Faker:

```bash
faker -l es_MX name
faker -l es_MX --seed 42 -r 5 -s $'\n' address
PYTHONPATH=. faker -l es_MX -i providers.sensores temperatura_c
```

Para usar providers personalizados desde el CLI, ejecuta desde la raíz del repo y
antepón `PYTHONPATH=.` para que Python encuentre `providers/`.

> **Nota macOS/Homebrew:** si instalaste Faker con `brew install faker`, el comando
> `faker` funciona directo en la terminal. Para ejecutar los generadores internos,
> usa el venv del repo porque el `python3` del sistema no necesariamente ve el
> paquete que Homebrew instaló para su CLI.

## Estructura

| Carpeta | Contenido |
|---|---|
| `modulo00_intro_faker/` | **Empieza aquí.** Lecciones y ejercicios para dominar Faker |
| `lenguajes_interfaz/` | Generadores de datos para prácticas de assembly ARM64 |
| `sistemas_programables/` | Generadores para el stack IoT (sensores, InfluxDB, NoSQL, MSSQL…) |
| `providers/` | Providers personalizados compartidos (sensores, dispositivos) |

## Regla de oro del repo

**Todo se genera con semilla (`--seed`).** Misma semilla → mismos datos → tu salida se
puede comparar byte a byte contra la salida esperada. Si tu resultado no coincide con
el esperado de la práctica, el error está en tu programa, no en los datos.

## Catálogo de prácticas

| Subcomando | Práctica | Escenario del mundo real |
|---|---|---|
| `asm` | LI-01 Ordenamiento | Ordenar enteros con signo en memoria y emitirlos por `write` |
| `stdin` | LI-02 Caja de kiosco | Validar montos tecleados: basura real de teclado, suma de 64 bits |
| `disco` | LI-03 Nómina legada | Registros binarios de 32 bytes estilo COBOL, auditoría por offsets |
| `uart` | LI-04 Receptor GPS | Tramas NMEA por UART, checksum XOR, descartar corruptas |
| `xxd` | LI-05 Forense | Mini-xxd: volcado hex con evidencia ASCII embebida |
| `busqueda` | LI-06 Almacén | Búsqueda binaria de seriales u64 en catálogo ordenado |
| `influx` | SP-01 Telemetría | Sensores → line protocol → InfluxDB → Grafana |
| `mssql` | SP-02 Inventario | T-SQL + BULK INSERT con acentos, comillas y UTF-8 |
| `mqtt` | SP-03 Pub/Sub | Topics, retained y comodines con Mosquitto |
| `dataset` | SP-04 ML | Detección de sensores defectuosos, split sin fuga de datos |
| `mongo` | SP-05 NoSQL | Embed vs reference con una flota IoT |
| `rest` | SP-06 API REST | Flask calificada caso por caso: 201/400/422 |
| `alertas` | SP-07 NOC | Alertas Grafana: ola de calor, nodo caído y pico falso |
| `gps` | SP-08 Geocercas | Transporte universitario: MongoDB 2dsphere y GeoJSON |
| — | SP-09 Integrador | Proyecto final: el pipeline completo, sin hardware |

## Licencia y cita

Código y material bajo [licencia MIT](LICENSE). Si lo usas en tu curso o
publicación, cítalo con los metadatos de [CITATION.cff](CITATION.cff) (GitHub
genera la cita con el botón "Cite this repository").
