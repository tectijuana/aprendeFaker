# Práctica 03 — MQTT: publicar y suscribirse a telemetría

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server + Mosquitto

## Objetivo académico

Dominar el patrón **publish/subscribe**: jerarquía de topics, comodines (`+`, `#`),
mensajes *retained* y QoS, usando la telemetría sintética de 3 nodos Raspberry Pi
Pico W / Pico 2 W sin necesitar hardware (los mensajes son los mismos que
publicaría el Pico físico o el simulado en Wokwi). El generador produce los mensajes Y el publicador; tú te
concentras en observar y filtrar del lado del suscriptor.

## Jerarquía de topics

```
tec/<aula>/<id_dispositivo>/ambiente   telemetría cada 60 s: {"t":23.2,"h":53.0,"bat":60,"ts":...}
tec/<aula>/<id_dispositivo>/estado     eventos: arranque (retained), bateria_baja
```

## Pasos

```bash
# 0. Broker y clientes (una vez)
sudo apt install -y mosquitto mosquitto-clients

# 1. Genera mensajes y publicador (desde la raíz del repo); compara tu SHA-256
.venv/bin/python sistemas_programables/practica03_mqtt/generar_payloads.py

# 2. En una terminal, suscríbete a TODO con comodín multinivel
mosquitto_sub -h localhost -t 'tec/#' -v

# 3. En otra terminal, publica simulando tiempo real (0.2 s entre mensajes)
cd sistemas_programables/practica03_mqtt && ./salida/publicar.sh localhost 0.2

# 4. Experimentos de suscripción (uno por uno; anota qué recibe cada uno y por qué):
mosquitto_sub -h localhost -t 'tec/+/+/estado' -v          # solo eventos, todas las aulas
mosquitto_sub -h localhost -t 'tec/LC-02/#' -v             # todo lo de un aula
mosquitto_sub -h localhost -t 'tec/+/PICOW-A37DFE/#' -v    # un dispositivo, esté donde esté

# 5. El mensaje retained: suscríbete DESPUÉS de publicar…
mosquitto_sub -h localhost -t 'tec/+/+/estado' -v
#    …¿por qué recibes los "arranque" de inmediato pero no los "bateria_baja"?
```

## Entregable

Capturas de los 4 experimentos del paso 4 con una línea explicando qué filtra cada
comodín, y la respuesta razonada del paso 5 (retained vs no retained).

## Preguntas de reflexión

1. ¿Por qué el evento `arranque` se publica con `-r` (retained) y la telemetría no?
2. ¿Qué diferencia hay entre `tec/#` y `tec/+`? Pruébalo.
3. El payload usa claves cortas (`t`, `h`, `bat`). En un nodo real por LoRa/2G,
   ¿cuántos bytes ahorra eso por mensaje frente a `temperatura`, `humedad`…?
   ¿Y frente a un formato binario como el de la práctica de UART?
