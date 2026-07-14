# Práctica LI-05 — Mini-xxd: volcado hex forense

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Escenario del mundo real

Peritaje digital: te entregan un binario extraído de una USB decomisada y hay que
volcarlo a hex legible para localizar la evidencia — hay **3 cadenas ASCII
embebidas** (un nombre, un correo y una clave) entre bytes de relleno. Tu programa
es un `xxd` mínimo escrito en assembly: stdin → volcado hex por stdout.

## Formato de salida (exacto)

```
00000000: 3c a3 34 72 d7 fb e1 7a 01 29 38 93 32 e6 05 fb
```

Offset de 8 hex minúsculas, `: `, hasta 16 bytes `xx` con UN espacio entre ellos,
sin espacio final, `\n`. **El binario mide 251 bytes a propósito**: la última línea
trae 11 bytes — el caso que rompe los mini-xxd mal hechos.

## Pasos

```bash
# 1. Genera el binario (desde la raíz del repo)
./aprendefaker.py xxd --seed 2026 --n 256

# 2. Referencia: compara tu meta con el xxd real (formato distinto, contenido igual)
xxd salida/volcado.bin | head -3

# 3. Completa los TODO de plantilla.s
make verificar     # CORRECTO ✔

# 4. Forense: encuentra las 3 evidencias en tu propio volcado
grep -ab CLAVE salida/volcado.bin   # ¿en qué offset está? confírmalo en tu salida
```

## Entregable

`plantilla.s` completo, captura de `make verificar` con `CORRECTO ✔`, y los offsets
de las 3 evidencias encontradas.

## Preguntas de reflexión

1. ¿Por qué conviene armar la línea completa en memoria y hacer UN `write`, en
   lugar de un `write` por byte? Estima la diferencia en syscalls.
2. El nombre embebido trae un acento (UTF-8). ¿Cuántos bytes ocupa esa letra en
   el volcado y cómo la reconoces?
3. `xxd` real muestra también la columna ASCII a la derecha. ¿Qué agregarías a tu
   lazo para producirla? (Impleméntalo si quieres +10 %.)
