#!/usr/bin/env python3
"""Práctica 02 — Datos IoT para Microsoft SQL Server.

Genera un inventario de dispositivos y sus lecturas por las DOS vías de
ingesta que se practican en la materia:

  salida/01_esquema_y_dispositivos.sql   T-SQL: CREATE TABLE + INSERT por lotes (sqlcmd)
  salida/lecturas.csv                    lecturas masivas en CSV UTF-8
  salida/02_bulk_insert.sql              T-SQL: BULK INSERT del CSV anterior

Puntos didácticos deliberados en los datos:
  * Responsables con acentos y eñes (es_MX)  → obliga a NVARCHAR + prefijo N'…'
    y a cargar el CSV con CODEPAGE 65001 (UTF-8).
  * Algunas notas traen comillas simples      → obliga a escapar '' en T-SQL.
  * Fechas en ISO 8601                        → DATETIME2 las acepta sin ambigüedad.

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python sistemas_programables/practica02_mssql/generar_mssql.py \
        --seed 2026 --dispositivos 10 --lecturas 50

Reproducible: misma semilla → mismos archivos byte a byte (imprime SHA-256).
"""

import argparse
import hashlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider

INICIO = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)
AULAS = ["LC-01", "LC-02", "LAB-IOT"]
# Notas con comilla simple A PROPÓSITO: sin escape, el INSERT truena.
NOTAS = [
    "Nodo de referencia del aula",
    "Sensor 'testigo' para calibración",
    "Reubicado del laboratorio 'viejo'",
    "Carcasa impresa en 3D",
    "Antena externa instalada",
]


def sql_txt(valor: str) -> str:
    """Escapa comillas simples y antepone N para literales Unicode en T-SQL."""
    return "N'" + valor.replace("'", "''") + "'"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--dispositivos", type=int, default=10,
                        help="nodos en el inventario (default 10)")
    parser.add_argument("--lecturas", type=int, default=50,
                        help="lecturas por dispositivo en el CSV (default 50)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)

    args.salida.mkdir(exist_ok=True)

    # ---- Inventario de dispositivos --------------------------------------
    dispositivos = []
    for _ in range(args.dispositivos):
        dispositivos.append({
            "id": fake.id_dispositivo(),
            "mac": fake.mac_pico(),   # OUI 28:cd:c1 = Raspberry Pi, como un Pico W real
            "aula": fake.random_element(AULAS),
            "responsable": fake.name(),
            "notas": fake.random_element(NOTAS),
            "alta": fake.date_time_between(INICIO - timedelta(days=90),
                                            INICIO - timedelta(days=1),
                                            tzinfo=timezone.utc)
                        .strftime("%Y-%m-%d %H:%M:%S"),
        })

    # ---- 1) Esquema + INSERTs (vía sqlcmd) --------------------------------
    sql = [
        "-- Generado por generar_mssql.py — NO editar a mano.",
        f"-- seed={args.seed} dispositivos={args.dispositivos}",
        "USE iot;",
        "GO",
        "DROP TABLE IF EXISTS dbo.lecturas;",
        "DROP TABLE IF EXISTS dbo.dispositivos;",
        "GO",
        "CREATE TABLE dbo.dispositivos (",
        "    id_dispositivo NVARCHAR(20)  NOT NULL PRIMARY KEY,",
        "    mac            CHAR(17)      NOT NULL,",
        "    aula           NVARCHAR(10)  NOT NULL,",
        "    responsable    NVARCHAR(80)  NOT NULL,   -- acentos/eñes: por eso NVARCHAR",
        "    notas          NVARCHAR(200) NULL,",
        "    fecha_alta     DATETIME2(0)  NOT NULL",
        ");",
        "CREATE TABLE dbo.lecturas (",
        "    id             BIGINT IDENTITY(1,1) PRIMARY KEY,",
        "    id_dispositivo NVARCHAR(20) NOT NULL",
        "        REFERENCES dbo.dispositivos(id_dispositivo),",
        "    ts             DATETIME2(0) NOT NULL,",
        "    temperatura    DECIMAL(5,2) NOT NULL,",
        "    humedad        DECIMAL(4,1) NOT NULL,",
        "    bateria        TINYINT      NOT NULL",
        ");",
        "GO",
        "INSERT INTO dbo.dispositivos",
        "    (id_dispositivo, mac, aula, responsable, notas, fecha_alta)",
        "VALUES",
    ]
    filas = []
    for d in dispositivos:
        filas.append(
            f"    ({sql_txt(d['id'])}, '{d['mac']}', {sql_txt(d['aula'])}, "
            f"{sql_txt(d['responsable'])}, {sql_txt(d['notas'])}, '{d['alta']}')"
        )
    sql.append(",\n".join(filas) + ";")
    sql += ["GO", "SELECT COUNT(*) AS dispositivos_insertados FROM dbo.dispositivos;", "GO", ""]
    ruta_sql = args.salida / "01_esquema_y_dispositivos.sql"
    ruta_sql.write_text("\n".join(sql), encoding="utf-8")

    # ---- 2) Lecturas masivas (vía CSV + BULK INSERT) ----------------------
    ruta_csv = args.salida / "lecturas.csv"
    with ruta_csv.open("w", encoding="utf-8", newline="\n") as f:
        f.write("id_dispositivo,ts,temperatura,humedad,bateria\n")
        for d in dispositivos:
            bateria = float(fake.bateria_pct())
            base_t = 22.0 + fake.random.uniform(0, 4)
            for i in range(args.lecturas):
                ts = (INICIO + timedelta(minutes=5 * i)).strftime("%Y-%m-%d %H:%M:%S")
                bateria = max(5.0, bateria - abs(fake.random.gauss(0.01, 0.005)))
                f.write(f"{d['id']},{ts},{fake.temperatura_c(base=base_t)},"
                        f"{fake.humedad_pct()},{int(bateria)}\n")

    bulk = f"""-- Generado por generar_mssql.py — NO editar a mano.
-- Ajusta la ruta absoluta del CSV en tu instancia antes de ejecutar.
USE iot;
GO
BULK INSERT dbo.lecturas
FROM '/ruta/absoluta/a/lecturas.csv'
WITH (
    FIRSTROW = 2,           -- salta el encabezado
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '0x0a',
    CODEPAGE = '65001'      -- UTF-8: sin esto, los acentos llegan corruptos
);
GO
SELECT COUNT(*) AS lecturas_cargadas FROM dbo.lecturas;
GO
"""
    ruta_bulk = args.salida / "02_bulk_insert.sql"
    ruta_bulk.write_text(bulk, encoding="utf-8")

    for ruta in (ruta_sql, ruta_csv, ruta_bulk):
        sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
        print(f"{ruta.name:32s} SHA-256 {sha[:16]}…")
    print(f"\n{args.dispositivos} dispositivos, "
          f"{args.dispositivos * args.lecturas} lecturas en {args.salida}/")
    print(f"Cargar:  sqlcmd -S localhost -U sa -i {ruta_sql}")
    print(f"         (edita la ruta del CSV) sqlcmd ... -i {ruta_bulk}")


if __name__ == "__main__":
    main()
