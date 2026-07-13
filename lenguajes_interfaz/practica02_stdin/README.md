# Práctica LI-02 — Caja de kiosco: parseo y validación de stdin

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Escenario del mundo real

Un kiosco de pagos recibe montos en centavos tecleados uno por línea. Los teclados
reales producen basura: líneas vacías, espacios colados, signos, letras, montos
imposibles. Tu firmware debe **validar antes de sumar** — igual que cualquier
sistema de cobro real — y reportar el corte de caja: `<válidas> <suma>`.

## Reglas de validación

Una línea es válida **solo** si: contiene puros dígitos ASCII, no está vacía, y su
valor cabe en 32 bits sin signo (≤ 4294967295). La entrada generada garantiza al
menos un caso de cada tipo inválido: vacía, negativo, letra, espacio inicial,
espacio final, punto decimal y overflow — más el máximo válido exacto.

**Trampa deliberada:** la suma total (~4.3 mil millones) NO cabe en 32 bits.
Valida cada monto en 32 bits, pero acumula en un registro `x` de 64.

## Pasos

```bash
# 1. Genera la entrada (desde la raíz del repo)
./aprendefaker.py stdin --seed 2026 --n 50

# 2. Estudia los casos límite (¿ves el espacio final? usa cat -e)
cat -e salida/entrada.txt | head -20

# 3. Completa los TODO de plantilla.s (parseo, validación, suma, impresión decimal)
make verificar     # CORRECTO ✔ si tu corte coincide con esperado.txt
```

## Entregable

`plantilla.s` completo y captura de `make verificar` con `CORRECTO ✔`. El profesor
puede regenerar con otra semilla para validar que tu programa parsea, no memoriza.

## Preguntas de reflexión

1. `975 ` (con espacio final) parece válido a simple vista. ¿Por qué el generador
   lo marca inválido y qué pasaría en un sistema de cobro que lo aceptara "limpiándolo"?
2. ¿Cómo detectas overflow al ir armando el número dígito a dígito, ANTES de que
   el valor se desborde? (Pista: compara contra 429496729 antes de multiplicar por 10.)
3. Imprimir un número en decimal requiere dividir entre 10 repetidamente. ¿Por qué
   los dígitos salen en orden inverso y cómo lo resuelves sin usar la pila?
