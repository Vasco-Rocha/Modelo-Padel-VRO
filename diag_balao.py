#!/usr/bin/env python3
"""
DIAGNOSTICO DO BALAO — olhar aos pontos 3 e 6/7 DIRETAMENTE (Vasco, 12 jul).

Nao muda nada no pipeline. So OBSERVA.

    python3 diag_balao.py

Para cada ponto do ground-truth mostra:
  - o que o pipeline produziu (segmentos)
  - os tracklets que la vivem
  - TODAS as mudancas de lado (cima<->baixo) com prof>=MIN_PROF: as que passaram
    o teste da raquete (L>=11) e as que foram REJEITADAS, e com que L.
"""
import sys
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos, pancadas,
                              rallies, FPS, MIN_PROF, L_RAQUETE, GT, SILENCIO)

R, prof = carregar()
R = vai_e_vem(R)
tks = tracklets(R)
CR = cruzamentos(R, tks, prof)
PAN = pancadas(R)
M = rallies(CR, PAN)
fs = sorted(R)
Lmax = lambda f: max([R[g][2] for g in fs if abs(g - f) <= 5] or [0])

ALVO = [int(a) for a in sys.argv[1:]] or [3, 6, 7]

for k, (g0, g1) in enumerate(GT, 1):
    if k not in ALVO:
        continue
    f0, f1 = int(g0 * FPS), int(g1 * FPS)
    print("=" * 78)
    print(f"PONTO {k}  GT {g0:.1f}-{g1:.1f}s  (frames {f0}-{f1})")
    segs = [(a, b) for a, b in M if b >= f0 - 60 and a <= f1 + 60]
    print("  segmentos do pipeline que tocam este ponto:")
    for a, b in segs:
        print(f"     {a/FPS:7.1f}-{b/FPS:6.1f}s   (frames {a}-{b})")
    if len(segs) > 1:
        for (a1, b1), (a2, _) in zip(segs, segs[1:]):
            print(f"  >>> BURACO de {(a2-b1)/FPS:.1f}s entre {b1/FPS:.1f}s e {a2/FPS:.1f}s "
                  f"(SILENCIO={SILENCIO}s)")

    print("\n  cruzamentos ACEITES:", [round(c / FPS, 1) for c in CR if f0 - 60 <= c <= f1 + 60])

    print("\n  todas as passagens de lado dentro dos tracklets (prof>=%.2f):" % MIN_PROF)
    print("    %-8s %-6s %-6s %-7s %-6s %-8s %s" %
          ("t(s)", "frame", "lado", "prof", "L", "Lmax±5", "veredito"))
    for tk in tks:
        if tk[-1] < f0 - 60 or tk[0] > f1 + 60:
            continue
        ult = None
        for f in tk:
            l, p = prof(R[f][0], R[f][1])
            if p < MIN_PROF:
                continue
            if ult and ult != l:
                lm = Lmax(f)
                ok = lm >= L_RAQUETE
                print("    %-8.1f %-6d %-6s %-7.2f %-6.1f %-8.1f %s" %
                      (f / FPS, f, l, p, R[f][2], lm,
                       "aceite" if ok else f"REJEITADO (L<{L_RAQUETE})"))
            ult = l
    print()
