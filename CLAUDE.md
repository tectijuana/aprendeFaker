# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito del proyecto

`aprendeFaker` es una **herramienta de línea de comandos para generar mockup data**
con `faker` para prácticas académicas del TecNM Tijuana. No tratar este
repo como una librería Python: el producto para alumnos y docentes es el comando
`faker` y los generadores ejecutables que producen archivos listos para consumir.
Python es solo el lenguaje usado internamente para automatizar salidas complejas.

El enfoque del repo es generar datos ficticios, reproducibles y plausibles para dos
materias:

1. **Lenguajes de Interfaz (ensamblador ARM64/AArch64)** — generar datos de prueba organizados según **por dónde entran y salen** del programa en assembly. Los generadores de Faker deben producir datos para cada vía de E/S que se practica en la materia:

   - **Datos en memoria (compilados en el fuente)**: tablas y buffers embebidos en la sección `.data`/`.rodata` como directivas GAS (`.byte`, `.hword`, `.word`, `.xword`, `.asciz`, `.space`) — arreglos para ordenar/buscar, cadenas para manipular, estructuras de tamaño fijo con offsets conocidos para practicar direccionamiento (`ldr`/`str` con desplazamiento). El generador emite el bloque `.data` listo para pegar o incluir con `.include`.
   - **Entrada estándar (stdin, syscall `read` fd 0)**: líneas de texto con formato predecible (números decimales/hex uno por línea, registros CSV de ancho conocido) para que el alumno practique lectura y parseo byte a byte. Generar también los casos límite: línea vacía, valor máximo, signo negativo.
   - **Archivos en disco (syscalls `openat`/`read`/`write`/`close`)**: archivos binarios `.bin` crudos (enteros little-endian de 1/2/4/8 bytes, estructuras empacadas tipo registro) y archivos de texto de ancho fijo. Junto a cada `.bin` generar un `.hex` de referencia (`xxd`) y documentar el layout exacto (offset, tamaño, tipo de cada campo) para que el alumno pueda verificar con `xxd`/`od`.
   - **Dispositivos serie / UART (`/dev/ttyS*`, `/dev/ttyAMA*`, o virtual con `socat`)**: tramas que un programa assembly lee/escribe por puerto serie — telemetría estilo NMEA/GPS, tramas propias con byte de inicio + longitud + payload + checksum (el generador calcula el checksum correcto e inyecta opcionalmente tramas corruptas para práctica de validación). En AWS Academy, donde no hay UART física, documentar el par virtual: `socat -d -d pty,raw,echo=0 pty,raw,echo=0`.
   - **Salida esperada (para autoverificación)**: junto con la entrada, cada generador debe poder emitir el archivo de salida correcta (mismo seed) para que el alumno compare con `diff`/`cmp` lo que produjo su programa.

   Rutinas típicas a alimentar: conversión de bases, ordenamiento/búsqueda, manejo de cadenas, checksums, parseo de tramas, syscalls Linux AArch64.
2. **Sistemas Programables (IoT stack completo)** — datos ficticios realistas para todo el pipeline: lecturas de sensores (temperatura, humedad, acelerómetro, GPS…), telemetría de dispositivos, series de tiempo para **InfluxDB**, dashboards en **Grafana**, documentos para bases **NoSQL** (MongoDB/JSON), **Microsoft SQL Server**, datasets para ejercicios de **AI/ML**, y payloads MQTT/HTTP. **Hardware de la materia: Raspberry Pi Pico W / Pico 2 W** (físicos y en el simulador **Wokwi**, con MicroPython) — no ESP32: los IDs de dispositivo usan prefijos `PICOW-`/`PICO2W-` y las MAC el OUI de Raspberry Pi (`28:cd:c1`), vía `providers/sensores.py`.

**Entorno de despliegue de los alumnos: AWS Academy — Ubuntu Server** (instancias EC2, típicamente Graviton/ARM64 para las prácticas de ensamblador). La experiencia documentada debe ser de herramienta CLI sin GUI: comandos `faker`, comandos de generadores y archivos de salida. Los scripts internos deben correr con Python 3 estándar de Ubuntu e incluir en su docstring los comandos para instalarse y ejecutarse en esa instancia (venv + pip, `scp` si aplica), pero la documentación no debe presentar el proyecto como una API o librería importable.

**Idioma: todo el repo es en español LATAM** — README, docstrings, comentarios, mensajes de salida, nombres de prácticas y documentación. Los identificadores de código (variables, funciones) pueden ir en inglés si es el idioma natural del stack, pero todo texto dirigido al alumno va en español. Locale de Faker por defecto: `es_MX`.

## Detalle crítico de instalación

La herramienta base es el CLI de **Faker** instalado vía **Homebrew**, que lo aísla
en su propio venv:

- CLI: `/usr/local/bin/faker` (funciona directo en la terminal)
- Python interno de Homebrew: cambia con cada actualización; no hardcodear rutas
  de `/usr/local/Cellar/faker/...` en scripts o documentación para alumnos

El hecho de que los generadores internos hagan `from faker import Faker` es un
detalle de implementación, no una señal de que el repo sea una librería. Para esos
generadores, usar un venv propio del proyecto:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/ejemplo.py
```

(La alternativa rápida es el intérprete del venv de Homebrew — resolverlo con `head -1 $(which faker)` — pero la ruta cambia con cada upgrade, así que los scripts compartidos con alumnos no deben depender de ella.)

## Comandos comunes del CLI

```bash
faker <fake> [args]                 # un solo dato: faker address, faker name, faker profile
faker -l es_MX name                 # localizado a México
faker -r 10 -s $'\n' name           # 10 salidas separadas por newline
faker --seed 42 -r 5 name           # reproducible (clave para prácticas calificables)
faker -o salida.txt -r 100 address  # redirigir a archivo
faker profile ssn,birthdate         # fakes con argumentos (campos separados por coma)
PYTHONPATH=. faker -i providers.sensores temperatura_c
faker -i mi_modulo <fake>           # cargar un provider personalizado (ruta de import del módulo)
```

## Enfoque para futuros cambios

- Priorizar comandos de usuario, archivos generados y reproducibilidad por semilla.
- No agregar estructura de paquete Python, APIs públicas ni documentación centrada en
  `import aprendeFaker`; este repo no se distribuye como librería.
- Cuando haga falta Python, mantenerlo como implementación interna del generador y
  documentar el comando que el alumno debe ejecutar.
- Toda nueva práctica debe producir mockup data en formatos concretos: `.csv`,
  `.jsonl`, `.bin`, `.s`, `.lp`, `.sql`, scripts de publicación o salidas esperadas.
- Verificar con `faker --version` cuando se comparen salidas byte a byte; distintas
  versiones de Faker pueden cambiar catálogos y, por tanto, datos generados.

## Organización del repo

**Punto de entrada único: `aprendefaker.py`** — CLI con subcomandos (`asm`, `influx`, `mssql`, `mqtt`, `dataset`, `mongo`) que despacha vía `runpy` a los generadores de cada práctica; el alumno usa un solo comando de terminal con parámetros. Al agregar una práctica nueva, registrar su generador en el dict `SUBCOMANDOS`.

Los scripts se agrupan por materia y luego por práctica:

```
lenguajes_interfaz/    # datos para prácticas de assembly (buffers, hex, formato fijo)
sistemas_programables/ # sensores, series de tiempo, InfluxDB, Grafana, NoSQL, AI
providers/             # custom providers compartidos (heredan de faker.providers.BaseProvider)
```

Cada práctica debe incluir un encabezado docstring en español que diga: objetivo académico, formato de salida generado, y cómo consumirlo desde la materia correspondiente (ej. cómo cargar el archivo en un programa NASM, o cómo escribir los puntos a InfluxDB con `line protocol`).

## Providers y patrones por materia

**De serie en Faker, útiles aquí:** `mac_address`, `ipv4`/`ipv4_private`, `uuid4`, `hexify`, `numerify`, `port_number`, `unix_time`, `iso8601`, `date_time_between`, `latitude`/`longitude`/`local_latlng`, `pyfloat`, `random_int`, `binary`, `sha256`.

**Custom providers (en `providers/`):** lo que Faker no cubre — lecturas de sensores con ruido y deriva realistas, IDs de dispositivo con formato propio, tramas serie/CAN/LoRa, números de serie institucionales. Cargarlos con `fake.add_provider(...)` en scripts o `PYTHONPATH=. faker -i providers.modulo <fake>` desde el CLI (el CLI no agrega el directorio actual a `sys.path` por sí solo).

**Formatos de salida por destino:**
- Assembly ARM64: binario crudo (`.bin`), texto hex de ancho fijo, o directivas GAS (`.byte`/`.hword`/`.word`/`.xword`, `.asciz`) listas para `as`/`ld` o `gcc` en Ubuntu ARM64.
- InfluxDB: line protocol (`medicion,tag=valor campo=valor timestamp`) o JSON para el cliente Python.
- NoSQL/MongoDB: JSON Lines (un documento por línea) para `mongoimport`.
- SQL Server: scripts T-SQL (`CREATE TABLE` + `INSERT`, con `GO` por lotes) ejecutables con `sqlcmd`, o CSV apto para `bcp`/`BULK INSERT`. Usar tipos T-SQL correctos (`NVARCHAR`, `DATETIME2`, `DECIMAL`) y escapar comillas simples en los datos generados.
- Grafana: normalmente vía InfluxDB; no generar formatos propios de Grafana.
- AI/ML: CSV con encabezados, apto para pandas.

## Convenciones del proyecto

- **Reproducibilidad obligatoria**: todo script acepta/usa semilla (`Faker.seed(n)` o `--seed`) para que la salida documentada en la práctica coincida con la del alumno.
- Series de tiempo de sensores deben ser físicamente plausibles (rangos reales del sensor, ruido gaussiano moderado, sin saltos imposibles) — el objetivo es que el alumno no distinga a simple vista que son sintéticas.
- Documentación y comentarios en español LATAM; evitar regionalismos de España (usar "computadora", no "ordenador"; "ustedes", no "vosotros").
