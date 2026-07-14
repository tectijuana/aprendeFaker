# Práctica LI-06 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
programa: plantilla.s salida/datos.s
	as -o plantilla.o plantilla.s
	as -o datos.o salida/datos.s
	ld -o programa plantilla.o datos.o

salida/datos.s:
	cd ../.. && ./aprendefaker.py busqueda --seed 2026

verificar: programa
	./programa > salida.bin
	cmp salida.bin salida/esperado.bin && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (xxd salida.bin | diff - <(xxd salida/esperado.bin) | head)"

limpiar:
	rm -f *.o programa salida.bin

.PHONY: verificar limpiar
