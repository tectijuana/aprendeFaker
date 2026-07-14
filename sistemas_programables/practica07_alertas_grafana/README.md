# Práctica SP-07 — Alertas en Grafana: que el NOC duerma tranquilo

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server + InfluxDB + Grafana

## Escenario del mundo real

Un NOC no mira dashboards todo el día: configura **alertas** y espera. El reto de
las alertas reales no es que disparen — es que disparen **solo cuando deben**.
El generador produce 48 h de telemetría con la verdad conocida:

| Hora | Evento | Tu alerta debe… |
|---|---|---|
| 10.0–10.3 | Pico falso en LC-01 (~31 °C, 20 min) | analizarlo: ¿dispara con `for: 15m`? |
| 20–26 | Ola de calor en LC-02 (meseta ~35 °C) | **disparar** durante la meseta |
| 30 → fin | Un nodo de LAB-IOT muere | **disparar** la alerta *no data* |
| resto | Operación normal | **cero** alertas |

La bitácora exacta está en `salida/incidentes.txt` (léela DESPUÉS de configurar,
como autoverificación).

## Pasos

```bash
# 1. Genera y carga (desde la raíz del repo)
./aprendefaker.py alertas
influx write --bucket iot --file salida/telemetria_incidentes.lp

# 2. En Grafana (rango: 2026-07-01 00:00 → 2026-07-03 00:00):
#    a) Alerta "temperatura alta": promedio por aula > 30 °C, pendiente `for: 15m`
#    b) Alerta "nodo caído": no data por dispositivo durante > 15 min
#    (usa la vista de estado de alertas para ver Normal/Pending/Firing)

# 3. Verifica contra salida/incidentes.txt: ¿disparó lo que debía y NADA más?
```

## Entregable

Captura del historial de alertas mostrando: el disparo de la ola de calor, el
disparo de no-data, y tu análisis del pico falso (¿disparó? ¿por qué? ¿qué `for:`
lo habría filtrado?).

## Preguntas de reflexión

1. El pico falso dura 20 min y tu `for:` es 15 min. ¿Dispara? ¿Es un falso positivo
   o un evento legítimo? ¿Quién decide eso en un NOC real?
2. ¿Por qué la alerta de no-data se configura **por dispositivo** y no por aula?
   (En LAB-IOT queda otro nodo vivo…)
3. Alerta que dispara de noche y se resuelve sola en 10 min: ¿la mandas a un canal
   de Slack o despiertas a alguien? Investiga "alert fatigue".
