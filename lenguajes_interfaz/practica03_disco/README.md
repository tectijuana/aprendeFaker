# Práctica LI-03 — Padrón de nómina: registros binarios en disco

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Escenario del mundo real

Los sistemas de nómina legados (COBOL/RPG, aún vivos en bancos y gobierno) guardan
sus padrones en archivos binarios de **registros de tamaño fijo**: sin comas, sin
JSON, solo offsets. Tu programa es la utilería de auditoría: abre el padrón, lo
recorre registro por registro y extrae al empleado **activo** mejor pagado.

## El archivo: 30 registros × 32 bytes (ver `salida/layout.txt`)

| offset | tamaño | campo | tipo |
|---|---|---|---|
| 0 | 4 | id | u32 little-endian |
| 4 | 20 | nombre | ASCII relleno con `\0` (sin acentos: sistema legado) |
| 24 | 4 | salario | u32, quincena en centavos |
| 28 | 1 | activo | u8: 1 = activo, 0 = baja |
| 29 | 3 | relleno | alineación a 32 |

**Trampa deliberada:** el salario más alto de TODO el archivo pertenece a un
empleado dado de baja. Si no filtras por `activo`, tu salida pasa a simple vista…
pero falla el `cmp`. Así se audita de verdad.

## Pasos

```bash
# 1. Genera el padrón (desde la raíz del repo)
./aprendefaker.py disco --seed 2026 --n 30

# 2. Estudia el binario: ubica id, nombre, salario y activo del primer registro
xxd salida/empleados.bin | head -4
cat salida/layout.txt

# 3. Completa los TODO de plantilla.s (openat/read ya están armados)
make verificar     # CORRECTO ✔
```

## Entregable

`plantilla.s` completo y captura de `make verificar` con `CORRECTO ✔`.

## Preguntas de reflexión

1. El programa lee de 32 en 32 bytes. ¿Cuántas syscalls hace con 30 registros?
   ¿Cómo lo harías con UNA sola lectura y por qué sería más rápido?
2. El salario se compara con `b.hi` (sin signo). ¿Qué pasaría con `b.gt` si un
   salario "corrupto" tuviera el bit 31 encendido?
3. `openat` recibe `AT_FDCWD` (-100). ¿Desde qué directorio debe ejecutarse el
   programa para que `salida/empleados.bin` exista? ¿Cómo lo harías robusto?
