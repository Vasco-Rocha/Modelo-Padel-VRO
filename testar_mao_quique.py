#!/usr/bin/env python3
"""
A REGRA DO VASCO, À LETRA:  "bola na MÃO do NÃO SERVIDOR — ANTES de bater no CHÃO"
*** SÓ MEDE. Nada é alterado. ***

    SERVIDOR:      tem a bola na MÃO  ->  larga-a  ->  ela QUICA  ->  bate    ⇒ HÁ QUIQUE
    NÃO SERVIDOR:  tem a bola na MÃO  ->  passa-a / atira-a               ⇒ NÃO HÁ QUIQUE

⇒ **O QUIQUE ENTRE A MÃO E O INÍCIO DO PONTO É O QUE SEPARA O SERVIÇO DO LIXO.**

⚠️ v2 — a v1 exigia também uma RAQUETADA na janela, e falhava em 7 dos 13 pontos.
   Porquê: a raquetada do SERVIÇO **não está na lista de pancadas** — antes da batida a bola
   está na mão, quase parada, e não há mudança de direção que a detete. Eu estava a exigir
   uma coisa que o código não vê. A regra do Vasco não pede isso. Pede o QUIQUE.

Teste: entre a ÚLTIMA vez que a bola esteve NA MÃO e a 1.ª travessia do segmento —
       houve um QUIQUE (ressalto.py)?
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G
from ressalto import ressaltos

MP = 0.15
ORIG = G.MIN_PROF
JANELA = 3.0      # ⚠️ ATALHO MEU (declarado): onde procurar a mão antes da travessia


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    FIM   = G.fim_certo(R2, cal, boxes)
    _, _, meio = G.campo(cal)
    RES   = ressaltos(R2, tks)

    G.MIN_PROF = MP
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    G.MIN_PROF = ORIG

    fs = sorted(R2)

    def dist_box(f):
        x, y = R2[f][0], R2[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    print("\n" + "=" * 100)
    print('A REGRA DO VASCO:  "bola na MÃO do NÃO SERVIDOR — ANTES de bater no CHÃO"')
    print("   servidor: mão -> QUIQUE -> bate    ·    não-servidor: mão -> passa (SEM quique)")
    print("=" * 100)
    print(f"\n{'seg':>3} {'inicio':>8} │ {'frames MAO':>11} {'ult. MAO':>10} │ "
          f"{'QUIQUE apos a MAO?':>19} │ estado")
    print("-" * 100)

    ok_pt = falha_pt = 0
    res_lixo = None
    for i, (a, b) in enumerate(M, 1):
        t0, t1 = a / G.FPS, b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        cs = sorted(c for c in CR if a <= c <= b)
        if not cs:
            continue
        c0 = cs[0]
        j0 = c0 - int(JANELA * G.FPS)

        mao = [f for f in fs if j0 <= f < c0
               and R2[f][2] <= G.MAO_L and dist_box(f) <= G.MAO_RAIO]
        if mao:
            ult = max(mao)
            q = [x for x in RES if ult < x <= c0]
            txt = f"✅ SIM ({len(q)})" if q else "❌ NÃO — passou à mão"
            tem = bool(q)
            ult_s = f"{ult/G.FPS:.1f}s"
        else:
            txt, tem, ult_s = "— (não viu a mão)", None, "—"

        est = f"ponto {gt}" if gt else "🚨 LIXO"
        if gt:
            if tem:   ok_pt += 1
            elif tem is False: falha_pt += 1
        else:
            res_lixo = tem
        print(f"{i:>3} {t0:>7.1f}s │ {len(mao):>11} {ult_s:>10} │ {txt:>19} │ {est}")

    print("-" * 100)
    print(f"\n  PONTOS REAIS com QUIQUE depois da mão .......... {ok_pt}/13   (é o SERVIÇO ✅)")
    print(f"  PONTOS REAIS SEM quique (passou à mão) ......... {falha_pt}/13  "
          f"⚠️ estes MORRERIAM se a regra vetasse")
    print(f"  O LIXO (281s) tem quique? ...................... "
          f"{'✅ SIM (a regra NÃO o mata)' if res_lixo else '❌ NÃO (a regra MATA-O ✅)' if res_lixo is False else '— (não viu a mão)'}")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
