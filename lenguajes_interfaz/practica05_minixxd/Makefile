# Práctica LI-05 — ensamblar en Ubuntu ARM64 (AWS Academy, instancia Graviton)
programa: plantilla.s
	as -o plantilla.o plantilla.s
	ld -o programa plantilla.o

salida/volcado.bin:
	cd ../.. && ./aprendefaker.py xxd --seed 2026 --n 256

verificar: programa salida/volcado.bin
	./programa < salida/volcado.bin > salida.txt
	cmp salida.txt salida/esperado.txt && echo "CORRECTO ✔" || echo "INCORRECTO ✘ (diff salida.txt salida/esperado.txt | head)"

limpiar:
	rm -f *.o programa salida.txt

.PHONY: verificar limpiar
