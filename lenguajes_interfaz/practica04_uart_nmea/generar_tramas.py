#!/usr/bin/env python3
"""Práctica LI-04 — Tramas NMEA (GPS) con checksum para validar en ARM64.

Escenario real: un receptor GPS envía tramas $GPGGA por UART; algunas llegan
corruptas (ruido en la línea). Tu programa en assembly debe validar el
checksum de cada trama y dejar pasar SOLO las válidas.

Formato NMEA: $GPGGA,<campos>*CS\r\n donde CS = XOR de todos los bytes entre
'$' y '*' (exclusive), expresado en 2 dígitos hex mayúsculos.

Salida:
    salida/tramas.nmea    todas las tramas (≈10 % corruptas: un byte dañado)
    salida/esperado.txt   solo las tramas válidas — lo que tu programa debe emitir
    salida/layout.txt     desglose de la primera trama byte a byte (para depurar)

Autoverificación:
    ./programa < salida/tramas.nmea > salida.txt && cmp salida.txt salida/esperado.txt

Ejecución (subcomando del CLI del repo, desde la raíz):
    ./aprendefaker.py uart --seed 2026 --n 40

Reproducible: misma semilla → mismos archivos byte a byte.
"""

import argparse
from pathlib import Path

from faker import Faker

# Punto de partida: campus TecNM Tijuana (~32.53 N, 117.02 W).
LAT0, LON0 = 32.5327, -117.0186


def checksum(cuerpo: str) -> int:
    """XOR de los bytes entre '$' y '*' (el cuerpo, sin incluirlos)."""
    cs = 0
    for ch in cuerpo:
        cs ^= ord(ch)
    return cs


def grados_a_nmea(valor: float, es_lat: bool) -> str:
    """Grados decimales → formato NMEA ddmm.mmmm / dddmm.mmmm + hemisferio."""
    hemi = ("N" if valor >= 0 else "S") if es_lat else ("E" if valor >= 0 else "W")
    v = abs(valor)
    grados = int(v)
    minutos = (v - grados) * 60
    ancho = 2 if es_lat else 3
    return f"{grados:0{ancho}d}{minutos:07.4f},{hemi}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=2026,
                        help="semilla (default 2026, la oficial de la práctica)")
    parser.add_argument("--n", type=int, default=40,
                        help="cantidad de tramas (default 40)")
    parser.add_argument("--prop-corruptas", type=float, default=0.10,
                        help="fracción de tramas corruptas (default 0.10)")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).parent / "salida",
                        help="carpeta de salida (default: ./salida)")
    args = parser.parse_args()

    fake = Faker()
    Faker.seed(args.seed)
    rnd = fake.random

    lat, lon = LAT0, LON0
    todas, validas = [], []
    for i in range(args.n):
        # El vehículo se mueve un poco entre tramas (1 s entre fixes).
        lat += rnd.gauss(0, 0.0004)
        lon += rnd.gauss(0, 0.0004)
        hora = 120000 + i  # 12:00:00 UTC en adelante, 1 s por trama
        cuerpo = (f"GPGGA,{hora:06d}.00,{grados_a_nmea(lat, True)},"
                  f"{grados_a_nmea(lon, False)},1,{fake.random_int(5, 12):02d},"
                  f"{rnd.uniform(0.8, 2.5):.1f},{rnd.uniform(20.0, 90.0):.1f},M,"
                  f"-33.3,M,,")
        trama = f"${cuerpo}*{checksum(cuerpo):02X}\r\n"

        if rnd.random() < args.prop_corruptas:
            # Ruido de línea: se daña UN byte del cuerpo (no '$', '*' ni el CS),
            # así el checksum declarado ya no coincide con el recalculado.
            pos = rnd.randrange(1, len(cuerpo))
            byte_malo = chr(ord(trama[pos]) ^ (1 << rnd.randrange(0, 4)))
            trama_corrupta = trama[:pos] + byte_malo + trama[pos + 1:]
            todas.append(trama_corrupta)
        else:
            todas.append(trama)
            validas.append(trama)

    args.salida.mkdir(exist_ok=True)
    (args.salida / "tramas.nmea").write_text("".join(todas), encoding="ascii")
    (args.salida / "esperado.txt").write_text("".join(validas), encoding="ascii")

    # Desglose didáctico de la primera trama.
    t0 = todas[0].rstrip("\r\n")
    cuerpo0 = t0[1:t0.index("*")]
    desglose = [
        f"Trama:    {t0}",
        f"Cuerpo (entre $ y *): {cuerpo0}",
        f"Checksum declarado:   {t0[t0.index('*') + 1:]}",
        f"Checksum calculado:   {checksum(cuerpo0):02X}  (XOR byte a byte)",
        "Terminador: 0x0D 0x0A (\\r\\n) — ¡dos bytes, no uno!",
        "",
        "Hex de los primeros 16 bytes:",
        " ".join(f"{ord(c):02x}" for c in todas[0][:16]),
    ]
    (args.salida / "layout.txt").write_text("\n".join(desglose) + "\n", encoding="utf-8")

    n_corr = args.n - len(validas)
    print(f"{args.n} tramas ({n_corr} corruptas) en {args.salida}/")
    print("Verifica tu programa:  ./programa < salida/tramas.nmea > salida.txt "
          "&& cmp salida.txt salida/esperado.txt")


if __name__ == "__main__":
    main()
