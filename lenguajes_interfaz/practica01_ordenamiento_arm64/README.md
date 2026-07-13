# Práctica 01 — Ordenamiento de enteros en ARM64

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Objetivo académico

Ordenar en memoria un arreglo de enteros de **32 bits con signo** en ensamblador
AArch64, y escribir el resultado a stdout con la syscall `write`. Se practica:
direccionamiento con desplazamiento (`ldr`/`str`), lazos anidados, **comparación con
signo** (`b.le`/`b.gt`, no `b.ls`/`b.hi` — el error clásico), y syscalls Linux.

## Los datos: por dónde entran y salen

| Vía | Archivo | Descripción |
|---|---|---|
| Memoria (`.data`) | `salida/datos.s` | El arreglo, ensamblado dentro de tu programa |
| Disco (referencia) | `salida/datos.bin` | Los mismos bytes crudos, para inspección con `xxd` |
| stdout (tu salida) | `salida.bin` | Lo que tu programa escribe con `write(1, …)` |
| Referencia correcta | `salida/esperado.bin` | El arreglo ordenado; se compara byte a byte |

Los tres archivos salen de `generar_datos.py` con **semilla 2026** — todos en el grupo
trabajan con los mismos datos, y tu salida es correcta si y solo si es idéntica a
`esperado.bin`.

## Pasos

```bash
# 1. Genera los datos (o deja que make lo haga)
cd lenguajes_interfaz/practica01_ordenamiento_arm64
../../.venv/bin/python generar_datos.py --seed 2026 --n 16

# 2. Inspecciona lo que vas a ordenar (¡mira los negativos en little-endian!)
xxd salida/datos.bin

# 3. Completa el TODO en plantilla.s (ordenamiento burbuja sugerido)

# 4. Ensambla y verifica
make verificar     # CORRECTO ✔  o  INCORRECTO ✘
```

## Entregable

`plantilla.s` completo y una captura de `make verificar` mostrando `CORRECTO ✔`.
El profesor puede regenerar los datos con otra semilla (`--seed`) para validar que
tu programa ordena, no que memorizó la salida.

## Preguntas de reflexión

1. En `xxd salida/datos.bin`, ¿cómo se ve el número −1 en little-endian?
2. ¿Qué pasa si usas `b.lo` en lugar de `b.lt`? Pruébalo: ¿qué números quedan mal
   colocados y por qué? (Pista: son los negativos.)
3. ¿Por qué `write` necesita `n*4` bytes y no `n`?
