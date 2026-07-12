#!/usr/bin/env python3
"""
VARRIMENTO do MIN_PROF — a faixa cega à volta da rede.  *** SÓ MEDE. ***

A IDEIA É DO VASCO (13 jul): "os de cá, perto da rede, devolvem a bola muito ALTA e PERTO da
rede — não dando tempo à bola de passar, nos frames."

O QUE ISSO É, NO CÓDIGO: o `cruzamentos()` só olha para frames com `profundidade >= MIN_PROF`.
Com MIN_PROF=0.35, há uma FAIXA CEGA de 35% do meio-campo de cada lado da rede.
Uma bola volleyada à rede atravessa e MORRE dentro dessa faixa — nunca chega a ficar funda do
outro lado ⇒ **a travessia nunca é registada.**

⚠️ O MIN_PROF=0.35 é um AJUSTE MEU (declarado "⚠️ ATALHO" no código), não uma lei do Vasco.
   O que ele existe para fazer: impedir que a bola a ROÇAR A FITA conte como travessia
   (é onde o ruído oscila de um lado para o outro).

⚠️ NADA É ALTERADO. Cópia em memória, com o MIN_PROF trocado à mão.
"""
import json, pickle
import numpy as np
import gerar_tempo_util as G

ORIG = G.MIN_PROF


def correr(mp, R2, tks, prof, cal, boxes, PAN, FIM):
    G.MIN_PROF = mp                        # só nesta cópia em memória
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    r  = G.avaliar(M)
    dentro = sum(1 for c in CR if any(a <= c/G.FPS <= b for a, b in G.GT))
    por_ponto = [sum(1 for c in CR if t0 <= c/G.FPS <= t1) for t0, t1 in G.GT]
    return CR, r, dentro, por_ponto


def main():
    R, prof = G.carregar()
    cal = json.load(open(G.CAL))
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R2, cal, boxes)
    FIM = G.fim_certo(R2, cal, boxes)

    print("\n" + "=" * 90)
    print("A FAIXA CEGA À VOLTA DA REDE — varrer o MIN_PROF")
    print("=" * 90)
    print(f"\n{'MIN_PROF':>9} {'travessias':>11} {'nos pontos':>11} {'nos interv':>11} "
          f"{'segm':>5} {'serv':>5} {'RECALL':>8} {'PRECISAO':>9} {'F1':>6}")
    print("-" * 90)

    guardado = {}
    for mp in (0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.0):
        CR, r, dentro, pp = correr(mp, R2, tks, prof, cal, boxes, PAN, FIM)
        guardado[mp] = pp
        marca = "  <- HOJE" if mp == ORIG else ""
        print(f"{mp:>9.2f} {len(CR):>11} {dentro:>11} {len(CR)-dentro:>11} "
              f"{r['n']:>5} {r['servicos']:>5} {r['recall']:>8.1f} {r['precisao']:>9.1f} "
              f"{r['f1']:>6.1f}{marca}")

    print("\n" + "-" * 90)
    print("TRAVESSIAS POR PONTO — os frágeis (10, 11, 13) recuperam?\n")
    cols = [0.35, 0.25, 0.15, 0.05]
    print(f"  {'ponto':>6} {'dur':>6}" + "".join(f"{c:>8.2f}" for c in cols))
    for k in range(13):
        t0, t1 = G.GT[k]
        m = "  <--" if k+1 in (10, 11, 13) else ""
        print(f"  {k+1:>6} {t1-t0:>5.1f}s" + "".join(f"{guardado[c][k]:>8}" for c in cols) + m)

    G.MIN_PROF = ORIG
    print("\n⚠️ O gerar_tempo_util.py NÃO foi alterado. MIN_PROF reposto em", ORIG, "\n")


if __name__ == "__main__":
    main()
