# Práctica LI-03 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
# Uso:  make            → genera el padrón (si falta) y ensambla ./programa
#       make verificar  → corre el programa y compara contra esperado.bin
#       make limpiar

programa: plantilla.s
	as -o plantilla.o plantilla.s
	ld -o programa plantilla.o

salida/empleados.bin:
	cd ../.. && ./aprendefaker.py disco --seed 2026 --n 30

verificar: programa salida/empleados.bin
	./programa > salida.bin
	cmp salida.bin salida/esperado.bin && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (compara: xxd salida.bin; xxd salida/esperado.bin)"

limpiar:
	rm -f *.o programa salida.bin

.PHONY: verificar limpiar
