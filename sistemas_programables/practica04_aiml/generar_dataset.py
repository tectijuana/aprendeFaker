#!/usr/bin/env python3
"""Práctica 04 — Dataset etiquetado para AI/ML: detección de sensores defectuosos.

Genera lecturas de una flota de sensores donde una fracción está fallando, con
la etiqueta de la verdad (`estado`): el alumno entrena un clasificador que
detecte la falla a partir de las features, y valida contra la etiqueta.

Modos de falla simulados (los tres clásicos de un sensor real):
  deriva       la lectura se aleja lentamente del valor real (descalibración)
  atascado     el sensor repite casi el mismo valor sin importar el ambiente
  ruidoso      la varianza se dispara (conexión floja, interferencia)

Salida (CSV aptos para pandas):
  salida/entrenamiento.csv   80 % de los sensores, CON columna `estado`
  salida/prueba.csv          20 % restante, CON `estado` (para medir accuracy)

Features por fila: lecturas estadísticas de una ventana de 1 hora por sensor:
  media, desviación, mínimo, máximo, rango, delta_vs_aula (distancia a la
  mediana de los sensores de la misma aula — la feature más delatora).

Ejecución (en la instancia de AWS Academy, desde la raíz del repo):
    .venv/bin/python sistemas_programables/practica04_aiml/generar_dataset.py \
        --seed 2026 --sensores 200 --ventanas 24

Reproducible: misma semilla → mismos archivos byte a byte (imprime SHA-256).
"""

import argparse
import hashlib
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from faker import Faker

from providers.sensores import SensorProvider

AULAS = ["LC-01", "LC-02", "LAB-IOT", "LAB-ELEC"]
LECTURAS_POR_VENTANA = 12  # cada 5 min durante 1 h


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--sensores", type=int, default=200,
                        help="sensores en la flota (default 200)")
    parser.add_argument("--ventanas", type=int, default=24,
                        help="ventanas de 1 h por sensor (default 24 = un día)")
    parser.add_argument("--prop-fallas", type=float, default=0.15,
                        help="fracción de sensores defectuosos (default 0.15)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker("es_MX")
    fake.add_provider(SensorProvider)
    Faker.seed(args.seed)
    rnd = fake.random

    # Temperatura real de cada aula por ventana (todos los sensores del aula la ven).
    temp_aula = {a: [22.0 + rnd.uniform(0, 3) + 2.0 * rnd.random()] for a in AULAS}
    for a in AULAS:
        for _ in range(args.ventanas - 1):
            temp_aula[a].append(temp_aula[a][-1] + rnd.gauss(0, 0.3))

    # Flota: a cada sensor se le asigna aula y estado (sano o un modo de falla).
    sensores = []
    for _ in range(args.sensores):
        estado = "sano"
        if rnd.random() < args.prop_fallas:
            estado = rnd.choice(["deriva", "atascado", "ruidoso"])
        sensores.append({"id": fake.id_dispositivo(), "aula": rnd.choice(AULAS),
                         "estado": estado, "deriva_acum": 0.0,
                         "valor_atascado": None})

    # Lecturas por ventana según el modo de falla.
    def lecturas_ventana(sensor, temp_real):
        vals = []
        for _ in range(LECTURAS_POR_VENTANA):
            if sensor["estado"] == "atascado":
                if sensor["valor_atascado"] is None:
                    sensor["valor_atascado"] = temp_real + rnd.gauss(0, 0.5)
                vals.append(round(sensor["valor_atascado"] + rnd.gauss(0, 0.02), 2))
            elif sensor["estado"] == "ruidoso":
                vals.append(round(temp_real + rnd.gauss(0, 2.5), 2))
            elif sensor["estado"] == "deriva":
                sensor["deriva_acum"] += abs(rnd.gauss(0.015, 0.005))
                vals.append(round(temp_real + sensor["deriva_acum"] + rnd.gauss(0, 0.3), 2))
            else:  # sano
                vals.append(round(temp_real + rnd.gauss(0, 0.3), 2))
        return vals

    # Una fila = un sensor en una ventana, con features agregadas.
    filas = []
    for v in range(args.ventanas):
        crudas = {s["id"]: lecturas_ventana(s, temp_aula[s["aula"]][v]) for s in sensores}
        # Mediana del aula en esta ventana (para delta_vs_aula).
        med_aula = {a: statistics.median(
            statistics.mean(crudas[s["id"]]) for s in sensores if s["aula"] == a)
            for a in AULAS}
        for s in sensores:
            vals = crudas[s["id"]]
            media = statistics.mean(vals)
            filas.append({
                "id_sensor": s["id"], "aula": s["aula"], "ventana": v,
                "media": round(media, 3),
                "desviacion": round(statistics.pstdev(vals), 3),
                "minimo": min(vals), "maximo": max(vals),
                "rango": round(max(vals) - min(vals), 3),
                "delta_vs_aula": round(media - med_aula[s["aula"]], 3),
                "estado": s["estado"],
            })

    # Split 80/20 POR SENSOR (no por fila): si un sensor aparece en ambos
    # conjuntos, el modelo "memoriza" al sensor — fuga de datos clásica.
    ids = sorted({s["id"] for s in sensores})
    rnd.shuffle(ids)
    corte = int(len(ids) * 0.8)
    ids_prueba = set(ids[corte:])

    args.salida.mkdir(exist_ok=True)
    columnas = list(filas[0].keys())
    rutas = {"entrenamiento.csv": [f for f in filas if f["id_sensor"] not in ids_prueba],
             "prueba.csv": [f for f in filas if f["id_sensor"] in ids_prueba]}
    for nombre, subconjunto in rutas.items():
        ruta = args.salida / nombre
        with ruta.open("w", encoding="utf-8", newline="\n") as f:
            f.write(",".join(columnas) + "\n")
            for fila in subconjunto:
                f.write(",".join(str(fila[c]) for c in columnas) + "\n")
        sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
        print(f"{nombre:20s} {len(subconjunto):6d} filas  SHA-256 {sha[:16]}…")

    n_fallas = sum(1 for s in sensores if s["estado"] != "sano")
    print(f"\nFlota: {args.sensores} sensores, {n_fallas} defectuosos "
          f"({n_fallas / args.sensores:.0%}), {args.ventanas} ventanas de 1 h")
    print(f"Empieza con: pandas.read_csv('{args.salida / 'entrenamiento.csv'}')")


if __name__ == "__main__":
    main()
