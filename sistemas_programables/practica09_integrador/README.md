# Práctica SP-09 — Proyecto integrador: el pipeline IoT completo

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server (todo el stack)

## Escenario del mundo real

Eres el equipo de plataforma de una empresa que instala monitoreo ambiental en
escuelas. Debes entregar el sistema completo funcionando de punta a punta —
**sin hardware**: toda la flota se simula con los generadores del repo.

```
[Pico W (Wokwi/simulado)] → MQTT → [puente Python] → InfluxDB → Grafana (+ alertas)
                                        ↓
                                   MongoDB (fichas + eventos)      AI/ML (detección de fallas)
```

## Requisitos del sistema (no hay pasos: tú diseñas)

1. **Ingesta**: broker Mosquitto recibiendo la flota. Genera el tráfico con
   `./aprendefaker.py mqtt --dispositivos 10 --mensajes 120` (o publica desde
   Wokwi con MicroPython para los puntos extra de firmware).
2. **Puente**: un servicio Python (`paho-mqtt` + cliente InfluxDB) que se suscribe
   a `tec/#`, valida cada payload (reusa el contrato de la práctica SP-06: descarta
   lo malformado) y escribe puntos a InfluxDB.
3. **Almacenamiento dual**: telemetría a InfluxDB; fichas de dispositivos y eventos
   de estado a MongoDB (modelo de la práctica SP-05).
4. **Visualización y alertas**: dashboard de Grafana con al menos 3 paneles y las
   2 alertas de la práctica SP-07 configuradas.
5. **Inteligencia**: corre el clasificador de la práctica SP-04 sobre ventanas de
   la telemetría acumulada y reporta qué nodos parecen defectuosos.

## Reglas

- Todo reproducible: semillas documentadas en tu README.
- El puente debe sobrevivir a payloads corruptos (inyecta algunos a mano con
  `mosquitto_pub` y demuéstralo en la bitácora).
- Entrega en un repo Git con README que permita a otro equipo levantar todo
  en una instancia limpia en < 30 minutos.

## Entregable

Repo + demo en vivo (o video ≤ 5 min): flota publicando, dashboard moviéndose,
una alerta disparando y el reporte de nodos defectuosos.

## Rúbrica sugerida

| Componente | Peso |
|---|---|
| Puente MQTT→InfluxDB robusto (valida y no se cae) | 30 % |
| Dashboard + alertas funcionando | 25 % |
| Modelo dual InfluxDB/MongoDB bien justificado | 20 % |
| Detección de fallas sobre datos acumulados | 15 % |
| README reproducible + semillas | 10 % |
