# Ejercicios — Módulo 00

Resuélvelos en orden. Cada ejercicio es un script Python nuevo dentro de esta carpeta
(`ej1.py`, `ej2.py`, …). **Todos usan `Faker.seed()` con la semilla indicada**, así tu
salida debe coincidir exactamente con la de tus compañeros — compárenlas.

## Ejercicio 1 — Directorio telefónico (CLI, sin Python)

Con **una sola línea** del comando `faker`, genera un archivo `directorio.txt` con
20 nombres en español de México, uno por línea, con semilla 100.

<details><summary>Pista</summary>
Combina <code>-l</code>, <code>-r</code>, <code>-s</code>, <code>--seed</code> y <code>-o</code>.
</details>

## Ejercicio 2 — Inventario de dispositivos (seed + formato)

Script `ej2.py`: imprime 10 líneas CSV con columnas `id_dispositivo,mac,ip_privada`,
usando `hexify`, `mac_address` e `ipv4_private`, locale `es_MX`, semilla 200.
La primera línea debe ser el encabezado CSV.

## Ejercicio 3 — El bug de la semilla

El siguiente código pretende generar dos listas idénticas, pero no lo logra.
Explica en un comentario **por qué** y corrígelo en `ej3.py`:

```python
from faker import Faker
fake = Faker()
a = [fake.name() for _ in range(3)]
Faker.seed(5)
b = [fake.name() for _ in range(3)]
print(a == b)   # False :(
```

## Ejercicio 4 — Bytes para ensamblador

Script `ej4.py`: con semilla 300, genera 16 enteros de 8 bits (0–255) e imprímelos
en DOS formatos:

1. Una línea de texto hex separada por espacios: `3f a1 07 ...`
2. Una directiva GAS lista para pegar en un fuente ARM64:
   `datos: .byte 0x3f, 0xa1, 0x07, ...`

(Este es exactamente el trabajo que hacen los generadores de `lenguajes_interfaz/`.)

## Ejercicio 5 — Tu primer provider

Script `ej5.py`: escribe un provider `VoltajeProvider` con un método
`voltaje_mv(nominal=3300, ruido=25)` que simule el voltaje en mV de una fuente de
3.3 V con ruido gaussiano, redondeado a entero. Con semilla 400, imprime 10 lecturas
y su promedio. El promedio debe quedar cerca de 3300 — si no, revisa tu ruido.

## Ejercicio 6 (reto) — Trama corrupta

Extiende el `TramaProvider` de la lección 05 con `trama(n_bytes, corrupta=False)`:
si `corrupta=True`, el checksum debe ser incorrecto **pero solo por 1 bit**
(haz XOR con una potencia de 2 elegida al azar con `self.random_int`). Imprime con
semilla 500 cinco tramas válidas y cinco corruptas, marcando cada una con OK/MAL
según la verificación del checksum.
