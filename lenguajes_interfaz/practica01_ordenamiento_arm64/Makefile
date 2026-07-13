# Práctica 01 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
# Uso:  make            → genera datos (si faltan) y ensambla ./programa
#       make verificar  → corre el programa y compara contra esperado.bin
#       make limpiar

PYTHON ?= ../../.venv/bin/python

programa: plantilla.s salida/datos.s
	as -o plantilla.o plantilla.s
	as -o datos.o salida/datos.s
	ld -o programa plantilla.o datos.o

salida/datos.s:
	$(PYTHON) generar_datos.py --seed 2026 --n 16

verificar: programa
	./programa > salida.bin
	cmp salida.bin salida/esperado.bin && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (usa: xxd salida.bin | diff - <(xxd salida/esperado.bin))"

limpiar:
	rm -f *.o programa salida.bin

.PHONY: verificar limpiar
