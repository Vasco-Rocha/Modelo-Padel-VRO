#!/usr/bin/env python3
"""
🏓 O RESSALTO — detetor INDEPENDENTE.   13 jul 2026.

    python3 ressalto.py

NÃO entra no pipeline. Produz um SINAL, que depois se CRUZA com as regras do Vasco.
(Lei de desenho do Vasco: as regras PONTUAM, não CORTAM.)

A ASSINATURA DO CHÃO
--------------------
O `Theta` do BlurBall dá a direção do rasto a ~2°, numa ÚNICA deteção. Logo eu vejo a
componente VERTICAL da bola, frame a frame.

    o CHÃO    inverte a bola para CIMA  (desce -> sobe)   <- é ISTO que procuro
    a PAREDE  inverte na HORIZONTAL     (vai -> volta)
    a RAQUETE inverte em qualquer direção — MAS tem um jogador ao pé

⇒ um ressalto = **inversão VERTICAL** (desce -> sobe), dentro de um tracklet.

A VERDADE, DE GRAÇA
-------------------
Não temos quiques anotados. Mas temos os **13 serviços**, e a S9 do Vasco diz:
    SAI DA MÃO -> **CHÃO** -> RAQUETE -> RESSALTO NO QUADRADO CRUZADO
Todo o serviço TEM um quique antes da raquetada. Se o detetor não os encontra, não presta.
"""
import sys, json, math, pickle
import numpy as np
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos, pancadas,
                              campo, CAL, BOXES, FPS, N_FRAMES, GT, L_RAQUETE, PAD_ANTES)

DY_MIN = 1.0   # ⚠️ AJUSTE — píxeis de descida/subida para contar como inversão.
               #    (declarado: é o mínimo para não contar ruído de 1 px)


def ressaltos(R, tks):
    """A INVERSÃO VERTICAL: a bola vinha a DESCER e passa a SUBIR. É o chão."""
    out = []
    for tk in tks:
        for i in range(1, len(tk) - 1):
            a, b, c = tk[i-1], tk[i], tk[i+1]
            if c - a > 8:
                continue
            desce = R[b][1] - R[a][1]
            sobe = R[c][1] - R[b][1]
            if desce > DY_MIN and sobe < -DY_MIN:
                out.append(b)
    # agrupar (um quique dura 1-2 frames)
    g = []
    for f in sorted(set(out)):
        if g and f - g[-1][-1] <= 4:
            g[-1].append(f)
        else:
            g.append([f])
    return [x[0] for x in g]


def main():
    R, prof = carregar()
    R = vai_e_vem(R)
    tks = tracklets(R)
    cal = json.load(open(CAL))
    boxes = pickle.load(open(BOXES, "rb"))["player_boxes"]
    _, y_base, meio = campo(cal)
    CR = cruzamentos(R, tks, prof)
    PAN = pancadas(R, cal, boxes)
    RES = ressaltos(R, tks)
    fs = sorted(R)
    Lmax = lambda f: max([R[g][2] for g in fs if abs(g - f) <= 5] or [0])

    def dbox(f):
        x, y = R[f][0], R[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    print(f"RESSALTOS detetados: {len(RES)}   (um cada {N_FRAMES/len(RES)/FPS:.1f}s)")
    print(f"  para comparar: {len(PAN)} pancadas, {len(CR)} cruzamentos\n")

    # =====================================================================
    #  TESTE 1 — A S9 DO VASCO: todo o SERVIÇO tem um quique antes da raquetada.
    #  Esta é a ÚNICA verdade que temos. Se falha aqui, o detetor não presta.
    # =====================================================================
    print("=" * 88)
    print("TESTE 1 — os 13 SERVIÇOS têm um quique antes?   (S9: mão -> CHÃO -> raquete)")
    print("=" * 88)
    print("%-4s %-9s %-11s %-9s %-9s %-8s %s" %
          ("#", "serviço", "1o cruzam.", "quique", "antes de", "prof", "dist_box"))
    print("-" * 88)
    ok = 0
    for k, (g0, g1) in enumerate(GT, 1):
        f0 = int(g0 * FPS)
        cr = [c for c in CR if f0 - 3*FPS <= c <= f0 + 4*FPS]
        c0 = cr[0] if cr else None
        # o quique do serviço: entre 2,5s antes do serviço e o cruzamento
        lim = c0 if c0 else f0 + int(2*FPS)
        q = [f for f in RES if f0 - int(2.5*FPS) <= f <= lim]
        if q:
            ok += 1
            f = q[-1]                       # o ÚLTIMO antes de cruzar = o do serviço
            lado, p = prof(R[f][0], R[f][1])
            print("%-4d %-9.1f %-11s %-9.1f %-9s %-8s %-8.2f" %
                  (k, g0, f"{c0/FPS:.1f}s" if c0 else "—", f/FPS,
                   f"{(lim-f)/FPS:.1f}s" if c0 else "—", f"{lado} {p:.2f}", dbox(f)))
        else:
            print("%-4d %-9.1f %-11s ⛔ NENHUM" % (k, g0, f"{c0/FPS:.1f}s" if c0 else "—"))
    print("-" * 88)
    print(f">>> {ok}/{len(GT)} serviços com quique antes da raquetada\n")

    # =====================================================================
    #  TESTE 2 — S14: o FIM do ponto = 2 quiques SEM RAQUETE pelo meio.
    # =====================================================================
    print("=" * 88)
    print("TESTE 2 — S14: o fim do ponto = 2 QUIQUES sem raquetada pelo meio")
    print("=" * 88)
    RAQ = [p for p in PAN if Lmax(p) >= L_RAQUETE]
    duplos = []
    for a, b in zip(RES, RES[1:]):
        if (b - a) / FPS > 2.0:
            continue
        if any(a < r < b for r in RAQ):     # bateram-lhe pelo meio -> continua o ponto
            continue
        duplos.append(b)
    gt = np.zeros(N_FRAMES, bool)
    fg = np.zeros(N_FRAMES, bool)
    for a, b in GT:
        gt[int(a*FPS):int(b*FPS)+1] = True
        fg[int((b-1.5)*FPS):int(b*FPS)+1] = True
    c = {"⛔ DENTRO": 0, "FIM": 0, "INTERVALO": 0}
    for f in duplos:
        c["INTERVALO" if not gt[f] else ("FIM" if fg[f] else "⛔ DENTRO")] += 1
    print(f"  duplos-quique sem raquete: {len(duplos)}")
    print(f"     a meio de pontos reais: {c['⛔ DENTRO']}   <- se >0, cortaria pontos")
    print(f"     no FIM de pontos:       {c['FIM']}")
    print(f"     nos intervalos:         {c['INTERVALO']}")
    print()
    for k, (g0, g1) in enumerate(GT, 1):
        q = [f for f in duplos if g1 - 3.0 <= f/FPS <= g1 + 2.0]
        if q:
            print(f"     ponto {k:2d} (acaba {g1:6.1f}s): duplo aos {q[0]/FPS:6.1f}s  "
                  f"({q[0]/FPS - g1:+.1f}s)")


if __name__ == "__main__":
    main()
