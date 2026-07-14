# Guía de contribución

¡Gracias por tu interés! Este repo es material didáctico vivo del TecNM Tijuana y
las contribuciones de estudiantes y docentes son bienvenidas.

## Qué aporta valor

- **Nuevas prácticas** (generador + README + verificación automática)
- **Nuevos providers** en `providers/` (sensores, protocolos, formatos)
- Correcciones a enunciados, erratas o casos límite que faltaron
- Traducciones de READMEs de prácticas al inglés (carpeta `docs/en/`)

## Reglas de la casa (no negociables)

1. **Español LATAM** en toda la documentación y mensajes al alumno
   ("computadora", no "ordenador"). Identificadores de código en inglés están bien.
2. **Reproducibilidad**: todo generador acepta `--seed` (default 2026) y produce
   los mismos bytes con la misma semilla. Nada de `datetime.now()` en los datos.
3. **Autoverificable**: toda práctica trae su `esperado.*` y una forma de comparar
   (`cmp`, `diff`, SHA-256 o script calificador).
4. **Datos plausibles**: rangos físicos reales, ruido moderado. La trampa didáctica
   deliberada (documentada en el README) es bienvenida.
5. **Hardware de referencia**: Raspberry Pi Pico W / Pico 2 W (no ESP32);
   assembly ARM64/AArch64 con sintaxis GAS.

## Cómo agregar una práctica

1. Crea `materia/practicaNN_nombre/` con `generar_*.py` y `README.md`
   (usa cualquier práctica existente como plantilla).
2. Registra el generador en el dict `SUBCOMANDOS` de `aprendefaker.py`.
3. Valida el `esperado` con una implementación independiente (no con el mismo
   código que lo generó) y muéstralo en la descripción del PR.
4. Verifica que `python aprendefaker.py <tu-subcomando>` corre dos veces con
   SHA-256 idéntico — el CI lo va a comprobar.

## Flujo

Fork → rama descriptiva → PR con: qué práctica/bug ataca, cómo lo verificaste y,
si es práctica nueva, el objetivo académico en una oración.
