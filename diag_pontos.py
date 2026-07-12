#!/usr/bin/env python3
"""
DIAGNOSTICO POR PONTO — onde e' que o M1 perde, ponto a ponto. So OBSERVA.

    python3 diag_pontos.py
"""
import sys, json, pickle
import numpy as np
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos, pancadas,
                              rallies, avaliar, fim_certo, CAL, BOXES, FPS, N_FRAMES, GT)

R, prof = carregar()
R = vai_e_vem(R)
tks = tracklets(R)
CR = cruzamentos(R, tks, prof)
cal = json.load(open(CAL))
boxes = pickle.load(open(BOXES, "rb"))["player_boxes"]
PAN = pancadas(R, cal, boxes)
FIM = fim_certo(R, cal, boxes)
M = rallies(CR, PAN, FIM)

cob = np.zeros(N_FRAMES, bool)
for a, b in M:
    cob[max(a, 0):min(b, N_FRAMES - 1) + 1] = True

print("=" * 90)
print(f"OS {len(GT)} PONTOS REAIS — o que o pipeline apanhou")
print("=" * 90)
print("%-3s %-14s %-6s %-8s %-8s %-7s %s" %
      ("#", "GT (s)", "dur", "apanhou", "falta", "segs", "onde falha"))
total_fn = 0
for k, (g0, g1) in enumerate(GT, 1):
    f0, f1 = int(g0 * FPS), int(g1 * FPS)
    m = cob[f0:f1 + 1]
    ap = m.sum() / FPS
    falta = (g1 - g0) - ap
    total_fn += falta
    segs = [(a, b) for a, b in M if b >= f0 and a <= f1]
    # onde falha: inicio, fim, ou meio
    onde = []
    if segs:
        if segs[0][0] > f0 + 3:
            onde.append(f"comeca {(segs[0][0]-f0)/FPS:.1f}s TARDE")
        if segs[-1][1] < f1 - 3:
            onde.append(f"acaba {(f1-segs[-1][1])/FPS:.1f}s CEDO")
        if len(segs) > 1:
            onde.append(f"PARTIDO em {len(segs)}")
    else:
        onde.append("PERDIDO TODO")
    print("%-3d %-14s %-6.1f %-8.1f %-8.1f %-7d %s" %
          (k, f"{g0:.1f}-{g1:.1f}", g1 - g0, ap, falta, len(segs),
           " + ".join(onde) or "ok"))
print("-" * 90)
print(f"TOTAL perdido: {total_fn:.1f}s de {sum(b-a for a,b in GT):.1f}s")

print()
print("=" * 90)
print("OS SEGMENTOS DO PIPELINE — quanto de cada um e' lixo")
print("=" * 90)
gt = np.zeros(N_FRAMES, bool)
for a, b in GT:
    gt[int(a * FPS):int(b * FPS) + 1] = True
print("%-3s %-16s %-7s %-8s %-8s %s" % ("#", "segmento (s)", "dur", "jogo", "lixo", "ponto GT"))
total_fp = 0
for i, (a, b) in enumerate(M, 1):
    a2, b2 = max(a, 0), min(b, N_FRAMES - 1)
    dur = (b2 - a2 + 1) / FPS
    jogo = gt[a2:b2 + 1].sum() / FPS
    lixo = dur - jogo
    total_fp += lixo
    quais = [str(k) for k, (g0, g1) in enumerate(GT, 1)
             if g1 >= a2 / FPS and g0 <= b2 / FPS]
    print("%-3d %-16s %-7.1f %-8.1f %-8.1f %s" %
          (i, f"{a2/FPS:.1f}-{b2/FPS:.1f}", dur, jogo, lixo, ",".join(quais) or "FALSO"))
print("-" * 90)
print(f"TOTAL lixo: {total_fp:.1f}s")
r = avaliar(M)
print(f"\nRECALL {r['recall']:.1f}%  PRECISAO {r['precisao']:.1f}%  "
      f"{r['n']} pontos  {r['tempo']:.1f}s")
