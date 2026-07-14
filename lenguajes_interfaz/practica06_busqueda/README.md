# Práctica LI-06 — Búsqueda binaria: consulta de inventario por serial

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Escenario del mundo real

El almacén consulta números de serie contra un catálogo **ordenado** de 200
entradas de 64 bits. La búsqueda lineal hace hasta 200 comparaciones; la binaria,
8 (⌈log₂ 200⌉). Con el catálogo de un almacén real (millones de SKUs) esa
diferencia es el sistema respondiendo en microsegundos o en segundos.

## Los datos

`salida/datos.s` exporta el catálogo ordenado, 24 consultas (**1/3 no existen**,
incluyendo los casos frontera: justo antes del primero y justo después del último)
y sus tamaños. Por cada consulta escribes 8 bytes a stdout: el índice como u64
little-endian, o `0xFFFFFFFFFFFFFFFF` si el serial no está.

## Pasos

```bash
# 1. Genera catálogo y consultas (desde la raíz del repo)
./aprendefaker.py busqueda --seed 2026

# 2. Completa el TODO de plantilla.s (el ciclo de consultas ya está armado)
make verificar     # CORRECTO ✔

# 3. Mide: implementa también la búsqueda lineal y compara con
#    perf stat -e instructions ./programa > /dev/null   (en ambas versiones)
```

## Entregable

`plantilla.s` completo, captura de `make verificar` con `CORRECTO ✔`, y la tabla
comparativa de instrucciones ejecutadas (lineal vs binaria) del paso 3.

## Preguntas de reflexión

1. `medio = (izq + der) / 2` puede desbordar si izq y der fueran enormes. ¿Cómo
   se escribe a prueba de overflow? (Es un bug histórico famoso en bibliotecas reales.)
2. ¿Por qué las entradas se indexan con `lsl #3`? ¿Qué cambiaría con un catálogo
   de u32?
3. Las consultas frontera (antes del primero, después del último) suelen colgar
   las búsquedas binarias mal escritas. ¿Qué condición del lazo las protege?
