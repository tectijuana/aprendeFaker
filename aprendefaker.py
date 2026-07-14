#!/usr/bin/env python3
"""aprendefaker — comando único del repo: genera todos los datos de las prácticas.

Uso:
    ./aprendefaker.py <subcomando> [parámetros del generador]

Subcomandos (cada uno acepta -h para ver sus parámetros):
    asm       Lenguajes de Interfaz P01: arreglo para ordenar en ARM64 (datos.s/.bin/esperado.bin)
    stdin     Lenguajes de Interfaz P02: montos por stdin con líneas inválidas (kiosco)
    disco     Lenguajes de Interfaz P03: padrón de nómina en registros binarios de 32 bytes
    uart      Lenguajes de Interfaz P04: tramas NMEA/GPS con checksum (10% corruptas)
    xxd       Lenguajes de Interfaz P05: binario forense para volcar en hex (mini-xxd)
    busqueda  Lenguajes de Interfaz P06: catálogo ordenado de seriales (búsqueda binaria)
    rest      Sistemas Programables P06: requests JSON para API REST Flask (con inválidos)
    alertas   Sistemas Programables P07: telemetría con olas de calor y caídas (Grafana)
    gps       Sistemas Programables P08: rutas GPS y geocercas (MongoDB geoespacial)
    influx    Sistemas Programables P01: telemetría line protocol para InfluxDB
    mssql     Sistemas Programables P02: T-SQL + CSV para SQL Server
    mqtt      Sistemas Programables P03: payloads y publicador para Mosquitto
    dataset   Sistemas Programables P04: CSV etiquetado para AI/ML
    mongo     Sistemas Programables P05: JSON Lines para mongoimport

Ejemplos:
    ./aprendefaker.py influx --seed 2026 --dispositivos 3 --horas 24
    ./aprendefaker.py asm --seed 2026 --n 16
    ./aprendefaker.py dataset -h

Todos los subcomandos aceptan --seed (default 2026): misma semilla → misma
salida byte a byte en cualquier máquina.
"""

import runpy
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

SUBCOMANDOS = {
    "asm": "lenguajes_interfaz/practica01_ordenamiento_arm64/generar_datos.py",
    "stdin": "lenguajes_interfaz/practica02_stdin/generar_entradas.py",
    "disco": "lenguajes_interfaz/practica03_disco/generar_padron.py",
    "uart": "lenguajes_interfaz/practica04_uart_nmea/generar_tramas.py",
    "xxd": "lenguajes_interfaz/practica05_minixxd/generar_volcado.py",
    "busqueda": "lenguajes_interfaz/practica06_busqueda/generar_tabla.py",
    "rest": "sistemas_programables/practica06_rest/generar_requests.py",
    "alertas": "sistemas_programables/practica07_alertas_grafana/generar_incidentes.py",
    "gps": "sistemas_programables/practica08_gps_geocercas/generar_rutas.py",
    "influx": "sistemas_programables/practica01_sensores_influxdb/generar_telemetria.py",
    "mssql": "sistemas_programables/practica02_mssql/generar_mssql.py",
    "mqtt": "sistemas_programables/practica03_mqtt/generar_payloads.py",
    "dataset": "sistemas_programables/practica04_aiml/generar_dataset.py",
    "mongo": "sistemas_programables/practica05_mongodb/generar_documentos.py",
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    subcomando = sys.argv[1]
    if subcomando not in SUBCOMANDOS:
        print(f"Subcomando desconocido: {subcomando!r}", file=sys.stderr)
        print(f"Disponibles: {', '.join(SUBCOMANDOS)}  (o -h para ayuda)", file=sys.stderr)
        sys.exit(2)

    script = RAIZ / SUBCOMANDOS[subcomando]
    # El generador ve sus propios parámetros como si se hubiera invocado directo.
    sys.argv = [str(script)] + sys.argv[2:]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
