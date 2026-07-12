#!/usr/bin/env python3
"""
O QUE DISTINGUE O LIXO DOS 13 PONTOS?   *** SÓ MEDE. Nada é alterado. ***

A pergunta do Vasco: "se ampliarmos o MIN_PROF, como tiramos aquele lixo?"

Se ampliarmos (MIN_PROF 0.35 -> 0.15) aparece UM segmento a mais: 281–285s.
Este script põe esse segmento LADO A LADO com os 13 verdadeiros, em TODOS os sinais que o
pipeline já calcula — e procura um que os separe.

⚠️ Sem inventar sinais novos. Se nenhum separar, a resposta é "não temos" — e diz-se.
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G

MP = 0.15
ORIG = G.MIN_PROF


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    FIM   = G.fim_certo(R2, cal, boxes)
    _, _, meio = G.campo(cal)

    G.MIN_PROF = MP
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    G.MIN_PROF = ORIG

    fs = sorted(R2)
    Lmax = lambda f: max([R2[g][2] for g in fs if abs(g-f) <= 5] or [0])

    def dist_box(f):
        x, y = R2[f][0], R2[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    print("\n" + "=" * 112)
    print(f"OS 14 SEGMENTOS com MIN_PROF={MP}  —  qual é o sinal que separa o LIXO dos PONTOS?")
    print("=" * 112)
    print(f"\n{'seg':>3} {'intervalo':>16} {'dur':>6} │ {'trav':>5} {'panc':>5} │ "
          f"{'1a trav L':>10} {'1a trav prof':>13} │ {'SERVICO?':>9} {'bola%':>7} │ estado")
    print("-" * 112)

    for i, (a, b) in enumerate(M, 1):
        t0, t1 = a / G.FPS, b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        cs  = sorted(c for c in CR if a <= c <= b)
        ps  = [q for q in PAN if a <= q <= b]

        # a 1.ª travessia: é o serviço? (vem da RAQUETE, funda, e é a que arranca o segmento)
        if cs:
            c0 = cs[0]; L0 = Lmax(c0); _, p0 = prof(R2[c0][0], R2[c0][1])
        else:
            L0, p0 = 0.0, 0.0

        # ASSINATURA DO SERVIÇO (S9/S15 do Vasco): antes da 1.ª travessia, houve uma bola
        # LENTA (na mão, L<=MAO_L) junto a um jogador, FUNDA (prof alto = na linha de servico)?
        serv = "-"
        if cs:
            jan = [f for f in fs if c0 - int(2.5*G.FPS) <= f < c0]
            mao = [f for f in jan
                   if R2[f][2] <= G.MAO_L and dist_box(f) <= G.PAN_DIST_MAX
                   and prof(R2[f][0], R2[f][1])[1] >= 0.7]
            serv = f"✅ {len(mao)}" if mao else "❌ 0"

        n_frames = b - a + 1
        cob = 100 * sum(1 for f in R2 if a <= f <= b) / max(n_frames, 1)
        est = f"ponto {gt}" if gt else "🚨 LIXO"
        print(f"{i:>3} {t0:>7.1f}–{t1:>6.1f}s {t1-t0:>5.1f}s │ {len(cs):>5} {len(ps):>5} │ "
              f"{L0:>10.1f} {p0:>13.2f} │ {serv:>9} {cob:>6.0f}% │ {est}")

    print("-" * 112)
    print("\nSERVIÇO? = nos 2,5s antes da 1.ª travessia houve bola LENTA (mão) junto a um jogador,")
    print("           FUNDA (prof>=0.7, i.e. na linha de serviço). É a S9/S15 do Vasco.")
    print("           ⚠️ o 0.7 é um ATALHO MEU para 'lá atrás'. Declarado.")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
