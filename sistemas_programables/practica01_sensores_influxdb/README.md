# Práctica 01 — Telemetría de sensores → InfluxDB → Grafana

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server

## Objetivo académico

Entender el camino de un dato IoT: **sensor → line protocol → InfluxDB → consulta →
Grafana**, usando telemetría sintética pero físicamente plausible (temperatura,
humedad, batería) de 3 nodos Raspberry Pi Pico W / Pico 2 W — como los físicos del
kit o los simulados en Wokwi — durante 24 horas. Al no depender de hardware, todo
el grupo trabaja con datos idénticos (semilla 2026) y los dashboards son comparables.

## Anatomía de un punto (line protocol)

```
ambiente,dispositivo=PICOW-A37DFE,aula=LC-01 temperatura=22.22,humedad=48.7,bateria=40i 1782864000000000000
└──────┘ └──────────────────────────────────┘ └──────────────────────────────────────┘ └─────────────────┘
medición                tags (indexados)                   campos (valores)              timestamp en ns
```

Detalles que importan: los **tags** siempre son texto y se indexan (por eso ahí van
`dispositivo` y `aula`); los **campos** llevan el valor — `bateria=40i` termina en `i`
porque es entero; el timestamp va en **nanosegundos** Unix.

## Pasos

```bash
# 1. Genera la telemetría (desde la raíz del repo)
.venv/bin/python sistemas_programables/practica01_sensores_influxdb/generar_telemetria.py

# 2. Verifica que tu SHA-256 coincide con el de tus compañeros (misma semilla = mismo archivo)

# 3. Instala InfluxDB 2.x en tu instancia y crea la organización/bucket `iot`
#    (guía del profesor; el puerto 8086 debe estar en el security group)

# 4. Carga el archivo
influx write --bucket iot --file sistemas_programables/practica01_sensores_influxdb/salida/telemetria.lp

# 5. Consulta desde el CLI (Flux): temperatura promedio por aula, ventanas de 1 h
influx query 'from(bucket:"iot") |> range(start: 2026-07-01T00:00:00Z, stop: 2026-07-02T00:00:00Z)
  |> filter(fn: (r) => r._measurement == "ambiente" and r._field == "temperatura")
  |> aggregateWindow(every: 1h, fn: mean) |> group(columns: ["aula"])'

# 6. Conecta Grafana a InfluxDB y arma un dashboard con 3 paneles:
#    temperatura por aula, humedad por dispositivo, y batería (¿qué nodo morirá primero?)
```

**Importante en Grafana:** los datos viven en julio de 2026 — ajusta el rango de
tiempo del dashboard a `2026-07-01 00:00` → `2026-07-02 00:00`, no "Last 6 hours".

## Entregable

Captura del dashboard con los 3 paneles + la consulta Flux del paso 5 con su resultado.

## Preguntas de reflexión

1. El nodo con menos batería arranca en 40 %. ¿En cuántos días morirá al ritmo de
   descarga observado? Estímalo desde el panel de Grafana.
2. ¿Por qué `aula` va como tag y `temperatura` como campo? ¿Qué pasaría con la
   cardinalidad si usáramos el timestamp como tag?
3. Regenera con `--intervalo 60`. ¿Cuántos puntos produce y cómo afecta al tamaño del
   archivo? ¿Qué implica para un nodo real transmitiendo por LoRa?
