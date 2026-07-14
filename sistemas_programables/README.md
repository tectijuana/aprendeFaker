# Sistemas Programables — generadores IoT

Cada práctica genera datos para un eslabón del stack:

| Práctica | Eslabón | Estado |
|---|---|---|
| `practica01_sensores_influxdb/` | Sensores → InfluxDB (line protocol) → Grafana | ✔ lista |
| `practica02_mssql/` | Registros → SQL Server (T-SQL para `sqlcmd`, CSV para `BULK INSERT`) | ✔ lista |
| `practica03_mqtt/` | Payloads MQTT (topics, retained, comodines con Mosquitto) | ✔ lista |
| `practica04_aiml/` | Dataset etiquetado → AI/ML (detección de sensores defectuosos) | ✔ lista |
| `practica05_mongodb/` | Documentos → MongoDB (embed vs reference, `mongoimport`) | ✔ lista |
| `practica06_rest/` | API REST Flask calificada caso por caso (201/400/422) | ✔ lista |
| `practica07_alertas_grafana/` | Alertas Grafana con incidentes inyectados (ola de calor, nodo caído, pico falso) | ✔ lista |
| `practica08_gps_geocercas/` | Rastreo GPS + geocercas (MongoDB 2dsphere, GeoJSON) | ✔ lista |
| `practica09_integrador/` | Proyecto final: pipeline completo MQTT→InfluxDB→Grafana+MongoDB+ML | ✔ lista |

Los nodos simulados son Raspberry Pi Pico W / Pico 2 W (como los físicos del kit o
los de Wokwi): IDs `PICOW-`/`PICO2W-` y MAC con OUI real de Raspberry Pi (`28:cd:c1`).

Antes de empezar, completa `modulo00_intro_faker/`.
