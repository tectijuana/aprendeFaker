# Práctica LI-04 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
# Uso:  make            → genera tramas (si faltan) y ensambla ./programa
#       make verificar  → alimenta las tramas por stdin y compara contra esperado.txt
#       make limpiar

PYTHON ?= ../../.venv/bin/python

programa: plantilla.s
	as -o plantilla.o plantilla.s
	ld -o programa plantilla.o

salida/tramas.nmea:
	cd ../.. && $(subst ../../,,$(PYTHON)) aprendefaker.py uart --seed 2026 --n 40

verificar: programa salida/tramas.nmea
	./programa < salida/tramas.nmea > salida.txt
	cmp salida.txt salida/esperado.txt && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (compara: diff <(cat -A salida.txt) <(cat -A salida/esperado.txt) | head)"

limpiar:
	rm -f *.o programa salida.txt

.PHONY: verificar limpiar
