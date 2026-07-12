#!/usr/bin/env python3
"""
O QUIQUE DO SERVIÇO MATA O LIXO?   *** SÓ MEDE. Nada é alterado. ***

A REGRA DO VASCO: "matar o lixo pela BOLA NA MÃO DO NÃO SERVIDOR — ANTES de bater no chão."
    servidor      -> larga a bola, ela QUICA (na linha de serviço), e SÓ DEPOIS bate
    não servidor  -> tem a bola na mão e PASSA-A / ATIRA-A  ⇒ SEM quique

O `ressalto.py` (independente) já provou: **13/13 serviços têm quique antes da raquetada**,
e os 13 quiques caem em `prof ≈ 1,0` — EM CIMA DA LINHA DE SERVIÇO. É a S9 do Vasco, nos dados.

⚠️ v3 — as v1/v2 falharam por erro MEU: fui procurar o quique DEPOIS da "última mão", mas a
   "mão" que eu detetava era a bola **já depois do quique**, junto ao corpo do servidor no
   momento da batida. Procurei no sítio errado.

TESTE CERTO — a assinatura do serviço, tal como o ressalto.py a mediu:
    nos segundos ANTES da 1.ª travessia do segmento, houve um QUIQUE FUNDO (prof alto)?
    (o quique do serviço está LÁ ATRÁS, na linha de serviço — não à rede)
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G
from ressalto import ressaltos

MP = 0.15
ORIG = G.MIN_PROF
JANELA = 3.0     # ⚠️ ATALHO MEU (declarado). O ressalto.py mediu quiques 0,0–2,9s antes.
PROF_MIN = 0.7   # ⚠️ ATALHO MEU (declarado). "fundo" = lá atrás, perto da linha de serviço.
                 #    Os 13 serviços deram prof 0,44 / 0,70 / 0,85 / 0,97 / 1,02 ... 1,23
                 #    (dois abaixo de 0,7: o serviço 1 (0,44) e o 12 (0,08) — vão FALHAR.)


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    FIM   = G.fim_certo(R2, cal, boxes)
    RES   = ressaltos(R2, tks)

    G.MIN_PROF = MP
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    G.MIN_PROF = ORIG

    print("\n" + "=" * 104)
    print("O QUIQUE DO SERVIÇO — há um ressalto FUNDO antes da 1.ª travessia?")
    print("=" * 104)
    print(f"\n{'seg':>3} {'inicio':>8} {'1a trav':>9} │ {'quiques':>8} {'o + fundo':>10} "
          f"{'quando':>9} │ {'FUNDO?':>8} │ estado")
    print("-" * 104)

    ok = falha = 0
    lixo_tem = None
    for i, (a, b) in enumerate(M, 1):
        t0 = a / G.FPS
        t1 = b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        cs = sorted(c for c in CR if a <= c <= b)
        if not cs:
            continue
        c0 = cs[0]
        j0 = c0 - int(JANELA * G.FPS)

        qs = [(q, prof(R2[q][0], R2[q][1])[1]) for q in RES if j0 <= q <= c0 and q in R2]
        if qs:
            qmax, pmax = max(qs, key=lambda z: z[1])
            fundo = pmax >= PROF_MIN
            txt = "✅ SIM" if fundo else "❌ raso"
            info = f"{pmax:>10.2f} {(c0-qmax)/G.FPS:>8.1f}s"
        else:
            fundo, txt, info = False, "❌ NENHUM", f"{'—':>10} {'—':>9}"

        est = f"ponto {gt}" if gt else "🚨 LIXO"
        if gt:
            ok += fundo
            falha += (not fundo)
        else:
            lixo_tem = fundo
        print(f"{i:>3} {t0:>7.1f}s {c0/G.FPS:>8.1f}s │ {len(qs):>8} {info} │ {txt:>8} │ {est}")

    print("-" * 104)
    print(f"\n  PONTOS REAIS com quique FUNDO antes ....... {ok}/13   ✅")
    print(f"  PONTOS REAIS sem ele ...................... {falha}/13  "
          f"⚠️ morreriam se a regra VETASSE")
    print(f"  O LIXO (281s) tem quique fundo? ........... "
          f"{'✅ SIM — a regra NÃO o mata' if lixo_tem else '❌ NÃO — A REGRA MATA-O ✅'}")
    print("\n  ⚖️ LEI DO VASCO: as regras PONTUAM, não VETAM.")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
