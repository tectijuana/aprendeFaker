# Práctica 05 — MongoDB: modelado NoSQL de una flota IoT

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server + MongoDB

## Objetivo académico

Modelar la misma flota de nodos Pico W que ya conoces de las prácticas anteriores,
pero en documentos — y entender **la decisión central de NoSQL** que en SQL no existe:
¿embebo o referencio?

| Colección | Patrón | Documento |
|---|---|---|
| `dispositivos` | **embed** | ficha rica: subdocumento `ubicacion`, arreglo `sensores[]`, `ultimo_estado` embebido |
| `eventos` | **reference** | plano y pequeño, apunta al nodo por `id_dispositivo` |

Nota cómo los documentos de `dispositivos` **no comparten esquema**: unos nodos
tienen 1 sensor, otros 3. En SQL eso costaría tablas extra o columnas NULL; aquí
es lo natural.

## Pasos

```bash
# 0. MongoDB en tu instancia (una vez; también sirve Docker: mongo:7)
sudo apt install -y mongodb-org || sudo docker run -d -p 27017:27017 --name mongo mongo:7

# 1. Genera las colecciones (desde la raíz del repo); compara tu SHA-256
.venv/bin/python sistemas_programables/practica05_mongodb/generar_documentos.py

# 2. Importa (JSON Lines = formato nativo de mongoimport)
mongoimport --db iot --collection dispositivos --file sistemas_programables/practica05_mongodb/salida/dispositivos.jsonl
mongoimport --db iot --collection eventos --file sistemas_programables/practica05_mongodb/salida/eventos.jsonl

# 3. Consultas en mongosh (escríbelas tú; estas son las metas):
#    a) Nodos con sensor BH1750 (buscar DENTRO del arreglo sensores[])
#    b) Eventos bateria_baja con bateria < 10, ordenados por ts
#    c) Conteo de eventos por tipo ($group — tu primer aggregate)
#    d) La ficha de un nodo + sus 5 eventos más recientes ($lookup:
#       el "JOIN" de Mongo — compáralo con el JOIN de la práctica 02)

# 4. Índices: mide con .explain("executionStats") la consulta (b) antes y
#    después de db.eventos.createIndex({id_dispositivo: 1, ts: -1})
```

## Entregable

Las 4 consultas con sus resultados, y el antes/después del `explain` del paso 4
(`totalDocsExamined` es el número a observar).

## Preguntas de reflexión

1. `ultimo_estado` está embebido en el dispositivo Y los eventos van aparte.
   ¿Por qué no embeber TODOS los eventos en un arreglo dentro del nodo?
   (Pista: 480 eventos hoy… ¿y en un año? Busca "unbounded array antipattern".)
2. ¿Cuándo preferirías el modelo relacional de la práctica 02 sobre este?
   Da un caso concreto con estos mismos datos.
3. `coordenadas` está en formato GeoJSON `[lon, lat]`. ¿Qué índice ofrece Mongo
   para consultas del tipo "nodos a menos de 1 km de aquí"?
