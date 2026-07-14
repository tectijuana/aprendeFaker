# Práctica SP-06 — API REST de telemetría en Flask

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server

## Escenario del mundo real

Los nodos Pico W hacen POST de su telemetría a un backend. Tú escribes la API;
el generador fabrica el tráfico de producción: JSON roto, campos faltantes, tipos
incorrectos y valores físicamente imposibles. Tu API se califica **caso por caso**
con `enviar.sh` — como una suite de integración real.

## Contrato de la API

`POST /api/lecturas` con JSON `{"dispositivo": "PICOW-XXXXXX", "temperatura": float, "humedad": float}`

| Respuesta | Cuándo |
|---|---|
| `201` | lectura válida (guárdala en memoria o SQLite) |
| `400` | JSON inválido, campo faltante/mal nombrado, tipo incorrecto |
| `422` | JSON bien formado pero físicamente imposible (temp fuera de −40…85, hum fuera de 0…100) |

La distinción 400 vs 422 es el punto fino: *no se pudo leer* vs *se leyó pero no
tiene sentido*.

## Pasos

```bash
# 1. Genera el tráfico (desde la raíz del repo); 30 casos, 7 tipos de error garantizados
./aprendefaker.py rest --seed 2026

# 2. Estudia los casos y sus respuestas esperadas
head -5 salida/requests.jsonl | python3 -m json.tool --json-lines

# 3. Escribe tu API (Flask en el venv: .venv/bin/pip install flask) y arráncala
#    flask --app api run   (puerto 5000)

# 4. Califícala
./salida/enviar.sh          # PASA/FALLA por caso + veredicto final
```

## Entregable

`api.py` + captura de `enviar.sh` con `CORRECTO ✔`. Extra (+10 %): un
`GET /api/lecturas?dispositivo=X` que regrese lo guardado.

## Preguntas de reflexión

1. ¿Por qué `{"temperatura": "veintitres"}` debe ser 400 y `{"temperatura": 999}`
   422, si ambos "traen un valor malo"?
2. `request.get_json()` de Flask lanza excepción con JSON roto. ¿Cómo la conviertes
   en un 400 limpio en vez de un 500?
3. ¿Qué caso del generador rompería una API que hace `float(dato)` sin validar tipo?
