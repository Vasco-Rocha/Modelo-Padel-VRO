#!/usr/bin/env python3
"""Onde é que a regra do VOLLEY morre?  *** SÓ MEDE. ***

A regra do Vasco tem 3 condições. Quantas pancadas passam cada uma?
    1. está na FAIXA junto à rede (prof < MIN_PROF)
    2. do lado de CIMA
    3. DENTRO de uma bounding box
Se a #3 mata tudo, o problema é o mesmo do "jogador toca na rede": **a box é do CORPO, e o
contacto do volley é na RAQUETE — que fica de FORA da box.**
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G

R, prof = G.carregar()
cal = json.load(open(G.CAL))
R2 = G.vai_e_vem(R)
boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
PAN = G.pancadas(R2, cal, boxes)
_, _, meio = G.campo(cal)

def dist_box(f):
    x, y = R2[f][0], R2[f][1]
    if f >= len(boxes) or not boxes[f]:
        return 99.0
    m = max(meio(x, y), 1)
    return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
               for x1, y1, x2, y2 in boxes[f])

print(f"\npancadas totais: {len(PAN)}\n")
faixa = [f for f in PAN if f in R2 and prof(R2[f][0], R2[f][1])[1] < G.MIN_PROF]
print(f"  1. na FAIXA junto à rede (prof < {G.MIN_PROF}) ....... {len(faixa)}")
cima = [f for f in faixa if prof(R2[f][0], R2[f][1])[0] == "cima"]
print(f"  2. ... e do lado de CIMA .......................... {len(cima)}")
dentro = [f for f in cima if dist_box(f) <= G.MAO_RAIO]
print(f"  3. ... e DENTRO da box (dist <= {G.MAO_RAIO}) ........... {len(dentro)}   <-- a regra")

print(f"\nDISTÂNCIA À BOX das {len(cima)} pancadas na faixa/cima")
print("(em FRAÇÕES do meio-campo local — 0 = dentro da box)\n")
ds = sorted(dist_box(f) for f in cima)
if ds:
    for lim in (0.0, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0, 2.0, 3.0):
        n = sum(1 for x in ds if x <= lim)
        barra = "█" * int(40 * n / len(ds))
        marca = "  <- MAO_RAIO (a regra)" if lim == G.MAO_RAIO else ""
        marca = "  <- PAN_DIST_MAX (a pancada ja usa este)" if lim == 3.0 else marca
        print(f"  dist <= {lim:<4} : {n:>3}/{len(ds)}  {barra}{marca}")
    print(f"\n  mediana {np.median(ds):.2f}   p25 {np.percentile(ds,25):.2f}   "
          f"p75 {np.percentile(ds,75):.2f}")

print("\n  Quantas caem DENTRO de pontos reais?")
for nome, L in (("na faixa/cima", cima), ("e dentro da box", dentro)):
    d_ = sum(1 for f in L if any(a <= f/G.FPS <= b for a, b in G.GT))
    print(f"    {nome:<18} {len(L):>3} eventos  ->  {d_} em pontos reais, {len(L)-d_} nos intervalos")

print("\n⚠️ Leitura pura.\n")
