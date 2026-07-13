# Práctica 04 — AI/ML: detección de sensores defectuosos

**Materia:** Sistemas Programables · **Entorno:** AWS Academy, Ubuntu Server (pandas + scikit-learn)

## Objetivo académico

Entrenar un clasificador que detecte sensores defectuosos a partir de features
estadísticas, en un dataset donde **conocemos la verdad** (lo generamos nosotros):
200 sensores, 16 % con uno de tres modos de falla reales:

| Falla | Cómo se ve en los datos | Feature que la delata |
|---|---|---|
| `deriva` | se aleja lentamente del valor real (descalibración) | `delta_vs_aula` crece con las ventanas |
| `atascado` | repite casi el mismo valor | `desviacion` y `rango` ≈ 0 |
| `ruidoso` | varianza disparada (conexión floja) | `desviacion` y `rango` enormes |

Cada fila es un sensor durante una ventana de 1 h (12 lecturas agregadas):
`media, desviacion, minimo, maximo, rango, delta_vs_aula` + la etiqueta `estado`.

## El detalle metodológico importante

El split 80/20 es **por sensor, no por fila**. Si las ventanas de un mismo sensor
cayeran en ambos conjuntos, el modelo memorizaría sensores en lugar de aprender
fallas — la fuga de datos (*data leakage*) más común en series de tiempo. El
generador ya lo hace bien; tu trabajo es poder explicar por qué.

## Pasos

```bash
# 1. Genera los CSV (desde la raíz del repo); compara tu SHA-256 con el grupo
.venv/bin/python sistemas_programables/practica04_aiml/generar_dataset.py

# 2. Instala el stack de ML en tu venv
.venv/bin/pip install pandas scikit-learn

# 3. Explora ANTES de modelar (siempre):
#    - boxplot de `desviacion` por `estado`: ¿qué falla se separa sola?
#    - scatter `rango` vs `delta_vs_aula` coloreado por estado

# 4. Entrena un árbol de decisión (features numéricas → estado) con
#    sistemas_programables/practica04_aiml/salida/entrenamiento.csv y mide
#    accuracy y matriz de confusión sobre
#    sistemas_programables/practica04_aiml/salida/prueba.csv

# 5. Repite con un modelo binario: sano / defectuoso. ¿Sube el accuracy? ¿Por qué?
```

## Entregable

Notebook o script con la exploración (paso 3), el clasificador, la **matriz de
confusión** sobre `prueba.csv`, y un párrafo: ¿cuál falla se confunde más con
`sano` y qué feature nueva propondrías para separarla?

## Preguntas de reflexión

1. `atascado` casi no se confunde con nada. ¿Podrías detectarlo sin ML, con un
   simple umbral? ¿Entonces cuándo se justifica el modelo?
2. La accuracy sale alta aun con un modelo malo, porque 84 % de las filas son `sano`.
   ¿Qué métrica reporta mejor el desempeño con clases desbalanceadas?
3. `deriva` es la más difícil en ventanas tempranas (deriva acumulada ≈ 0).
   ¿Cómo la detectarías en producción: por ventana aislada o mirando la tendencia?
