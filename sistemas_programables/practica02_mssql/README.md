# Práctica 02 — Inventario y telemetría IoT en Microsoft SQL Server

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server + SQL Server en Docker

## Objetivo académico

Diseñar y poblar una base relacional para IoT practicando las **dos vías de ingesta**:

1. **T-SQL con `sqlcmd`** — esquema (`CREATE TABLE` con llaves y FK) e `INSERT` por lotes,
   para el inventario de dispositivos (pocas filas, datos "sucios de la vida real").
2. **`BULK INSERT` desde CSV** — la vía correcta para telemetría masiva (500 lecturas);
   los `INSERT` fila por fila no escalan.

## Trampas didácticas incluidas a propósito en los datos

| Trampa | Dónde | Qué aprende el alumno |
|---|---|---|
| Nombres con acentos y eñes | `responsable` | `NVARCHAR` + prefijo `N'…'`; `VARCHAR` los corrompe |
| Notas con comillas simples (`Sensor 'testigo'`) | `notas` | Escapar `''` — sin eso el `INSERT` falla con error de sintaxis |
| CSV en UTF-8 | `lecturas.csv` | `CODEPAGE = '65001'` en `BULK INSERT`, o llegan `Ã©` en lugar de `é` |
| Fechas ISO 8601 | ambas tablas | `DATETIME2` sin ambigüedad de formato regional |

## Preparación: SQL Server en tu instancia (una vez)

```bash
# Docker es la vía más simple en AWS Academy (necesita instancia x86 con ≥2 GB RAM)
sudo docker run -e ACCEPT_EULA=Y -e MSSQL_SA_PASSWORD='TuPassw0rd!' \
    -p 1433:1433 -d --name mssql mcr.microsoft.com/mssql/server:2022-latest

# Cliente sqlcmd (repos de Microsoft) y crear la base
sqlcmd -S localhost -U sa -P 'TuPassw0rd!' -Q "CREATE DATABASE iot;"
```

> Nota: la imagen de SQL Server es x86_64. Si tu instancia es Graviton (ARM64, la de
> assembly), levanta una instancia x86 aparte para esta práctica, o usa Azure SQL Edge.

## Pasos

```bash
# 1. Genera los tres archivos (desde la raíz del repo) y compara tu SHA-256 con el grupo
.venv/bin/python sistemas_programables/practica02_mssql/generar_mssql.py

# 2. Esquema + inventario (vía 1: sqlcmd)
sqlcmd -S localhost -U sa -P 'TuPassw0rd!' -i sistemas_programables/practica02_mssql/salida/01_esquema_y_dispositivos.sql

# 3. Copia el CSV a donde el contenedor lo vea y edita la ruta en 02_bulk_insert.sql
sudo docker cp sistemas_programables/practica02_mssql/salida/lecturas.csv mssql:/var/opt/mssql/lecturas.csv
#    → en el .sql: FROM '/var/opt/mssql/lecturas.csv'

# 4. Carga masiva (vía 2: BULK INSERT)
sqlcmd -S localhost -U sa -P 'TuPassw0rd!' -i sistemas_programables/practica02_mssql/salida/02_bulk_insert.sql

# 5. Consultas de verificación (escríbelas tú):
#    a) Temperatura promedio por aula (JOIN dispositivos–lecturas + GROUP BY)
#    b) El dispositivo con menor batería final y su responsable
#    c) ¿Cuántas lecturas por dispositivo? ¿Coincide con lo que generaste?
```

## Entregable

Las tres consultas del paso 5 con sus resultados, y una captura del error que produce
el `INSERT` si **quitas** el escape de una comilla simple (rómpelo a propósito en una
copia del `.sql` y documenta el mensaje de error).

## Preguntas de reflexión

1. ¿Por qué `mac` es `CHAR(17)` y no `NVARCHAR`? ¿Cuándo conviene cada uno?
2. `bateria` es `TINYINT` (0–255). ¿Qué pasaría si un sensor reportara −1?
3. Cronometra: ¿cuánto tardarían 500 `INSERT` individuales contra un `BULK INSERT`?
   ¿Y 5 millones? (Genera más con `--lecturas 5000` y compara.)
