# Práctica SP-08 — Rastreo GPS del transporte universitario (MongoDB geoespacial)

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server + MongoDB

## Escenario del mundo real

Dos unidades del transporte universitario (Otay → campus TecNM Tijuana) reportan
posición cada 30 s. El sistema debe responder lo que el jefe de transporte pregunta:
¿ya llegó?, ¿se salió de ruta?, ¿por qué dejó de reportar? Con datos GeoJSON y los
índices geoespaciales de MongoDB.

**Eventos inyectados (la verdad conocida):** U2 se desvía a mitad del recorrido;
U1 pierde señal 5 minutos (hueco de 330 s en sus timestamps).

## Pasos

```bash
# 1. Genera e importa (desde la raíz del repo)
./aprendefaker.py gps
mongoimport --db transporte --collection posiciones --file salida/posiciones.jsonl
mongoimport --db transporte --collection geocercas --file salida/geocercas.jsonl

# 2. Índice geoespacial (sin él, las consultas geo fallan)
#    db.posiciones.createIndex({loc: "2dsphere"})

# 3. Consultas meta (mongosh):
#    a) ¿Qué unidad llegó al campus? → $geoWithin con el polígono de la geocerca
#    b) Posiciones a menos de 500 m del campus → $near / $nearSphere
#    c) El hueco de señal de U1 → aggregate: ordenar por ts y detectar deltas > 60 s
#    d) La última posición conocida de cada unidad → $sort + $group con $last

# 4. Visualiza: exporta las posiciones a GeoJSON y pégalas en geojson.io —
#    ¿ves el desvío de U2 a simple vista?
```

## Detalle que siempre muerde

GeoJSON es `[longitud, latitud]` — al revés de como se dice ("lat, lon"). Si tu
consulta `$near` "no encuentra nada", casi seguro invertiste el orden.

## Entregable

Las 4 consultas con resultados, la captura de geojson.io mostrando el desvío de
U2, y tu explicación del hueco de U1 (¿a qué hora empezó y cuánto duró?).

## Preguntas de reflexión

1. ¿Por qué la geocerca del campus es un polígono de 17 puntos y no "un círculo"?
   ¿Qué operador de Mongo sí acepta radios?
2. `2dsphere` vs `2d`: ¿cuál usas para coordenadas reales del planeta y por qué?
3. Con 1000 unidades reportando cada 30 s, ¿conviene un documento por fix (como
   aquí) o arreglos por unidad-hora? Relaciona con la práctica 05 (embed vs reference).
