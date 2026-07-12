#!/usr/bin/env python3
"""
A S9 MATA O LIXO?   *** SÓ MEDE. Nada é alterado. ***

A REGRA DO VASCO (13 jul):
    "Temos de matar este lixo pela BOLA NA MÃO DO NÃO SERVIDOR — ANTES DE BATER NO CHÃO."

É a S9 à letra:      SAI DA MÃO  ->  CHÃO  ->  RAQUETE  ->  o ponto começa
    · o SERVIDOR      larga a bola, ela QUICA, e só depois ele bate.
    · o NÃO SERVIDOR  tem a bola na mão e PASSA-A / ATIRA-A — **sem quique antes da raquetada**.

⇒ O QUE SEPARA UM DO OUTRO É O **QUIQUE**.
   Um segmento que arranca SEM a sequência mão→CHÃO→raquete **não é um ponto**.

E NÓS TEMOS O DETETOR DE QUIQUE: o `ressalto.py` (independente, 13/13 nos serviços).
Nunca entrou no pipeline. Aqui é usado como SINAL, não como corte — a lei do Vasco:
**as regras PONTUAM, não VETAM.**

Isto mede, para os 14 segmentos (com MIN_PROF=0.15):
    antes da 1.ª travessia de cada segmento, houve  MÃO -> QUIQUE -> RAQUETADA ?
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G
from ressalto import ressaltos

MP = 0.15
ORIG = G.MIN_PROF
JANELA = 3.0     # segundos antes da 1.ª travessia onde procurar o ritual do serviço
                 # ⚠️ ATALHO MEU — declarado. (o PAD_ANTES do pipeline é 1,6s)


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    FIM   = G.fim_certo(R2, cal, boxes)
    _, _, meio = G.campo(cal)
    RES   = ressaltos(R2, tks)          # os quiques (inversão vertical)

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

    print("\n" + "=" * 106)
    print("A S9 DO VASCO:  MÃO -> CHÃO -> RAQUETE.   Sem QUIQUE antes da raquetada, não é serviço.")
    print("=" * 106)
    print(f"\nquiques detetados no vídeo (ressalto.py): {len(RES)}\n")
    print(f"{'seg':>3} {'inicio':>8} {'dur':>6} │ {'MAO':>5} {'QUIQUE':>7} {'RAQUETADA':>10} │ "
          f"{'S9 COMPLETA?':>13} │ estado")
    print("-" * 106)

    acertos = falhas = 0
    for i, (a, b) in enumerate(M, 1):
        t0, t1 = a / G.FPS, b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        cs = sorted(c for c in CR if a <= c <= b)
        if not cs:
            continue
        c0 = cs[0]
        j0 = c0 - int(JANELA * G.FPS)

        # 1. MÃO: bola LENTA (L<=MAO_L) DENTRO/junto de uma box, antes da travessia
        mao = [f for f in fs if j0 <= f < c0
               and R2[f][2] <= G.MAO_L and dist_box(f) <= G.MAO_RAIO]
        # 2. QUIQUE: um ressalto DEPOIS da mão e ANTES da raquetada
        # 3. RAQUETADA: uma pancada (já tem jogador ao pé, já exige L alto)
        raq = [q for q in PAN if j0 <= q <= c0]

        if mao and raq:
            m0 = min(mao)
            r_ = max(raq)
            quique = [q for q in RES if m0 < q < r_]
        else:
            quique = []
            m0 = min(mao) if mao else None
            r_ = max(raq) if raq else None

        completa = bool(mao) and bool(quique) and bool(raq)
        s9 = "✅ SIM" if completa else "❌ NÃO"
        est = f"ponto {gt}" if gt else "🚨 LIXO"
        if gt and completa:
            acertos += 1
        if gt and not completa:
            falhas += 1
        print(f"{i:>3} {t0:>7.1f}s {t1-t0:>5.1f}s │ {len(mao):>5} {len(quique):>7} {len(raq):>10} │ "
              f"{s9:>13} │ {est}")

    print("-" * 106)
    print(f"\n  pontos REAIS com a S9 completa .... {acertos}/13")
    print(f"  pontos REAIS que a S9 NÃO vê ...... {falhas}/13   "
          f"⚠️ estes MORRERIAM se a regra VETASSE")
    lixo = [i for i, (a, b) in enumerate(M, 1)
            if not any(a/G.FPS <= g1 and b/G.FPS >= g0 for g0, g1 in G.GT)]
    print(f"  segmentos de LIXO ................. {lixo}")

    print("\n  ⚖️ LEI DO VASCO: as regras PONTUAM, não VETAM. Se a S9 falha num ponto real,")
    print("     ela não pode cortar — só pesar. Ver acima quantos falharia.")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
