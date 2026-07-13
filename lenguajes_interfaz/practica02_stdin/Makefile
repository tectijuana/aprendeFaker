# Práctica LI-02 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
# Uso:  make            → genera entradas (si faltan) y ensambla ./programa
#       make verificar  → alimenta entrada.txt por stdin y compara el corte de caja
#       make limpiar

PYTHON ?= ../../.venv/bin/python

programa: plantilla.s
	as -o plantilla.o plantilla.s
	ld -o programa plantilla.o

salida/entrada.txt:
	cd ../.. && ./aprendefaker.py stdin --seed 2026 --n 50

verificar: programa salida/entrada.txt
	./programa < salida/entrada.txt > salida.txt
	cmp salida.txt salida/esperado.txt && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (esperado: $$(cat salida/esperado.txt) | tuyo: $$(cat salida.txt))"

limpiar:
	rm -f *.o programa salida.txt

.PHONY: verificar limpiar
