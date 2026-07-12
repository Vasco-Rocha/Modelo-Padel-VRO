#!/usr/bin/env python3
"""
DIAGNÓSTICO — porque é que os pontos 10, 11 e 13 só têm UMA travessia?
*** SÓ LÊ E MEDE. Não toca no gerar_tempo_util.py. ***

⚠️ v2 — a v1 estava ERRADA. Eu comparava frames CRUS consecutivos; o `cruzamentos()` não faz isso.
   Ele percorre TRACKLET a TRACKLET e **SALTA** (continue) os frames rasos SEM atualizar o lado.
   Logo a profundidade NÃO mata travessias — só ignora frames.
   (A lição de sempre: LER O CÓDIGO, NÃO O MAPA. Voltou a morder-me, em 10 minutos.)

O QUE O CÓDIGO FAZ, À LETRA:
    por cada TRACKLET:
        ult = None
        por cada frame f:
            se profundidade < MIN_PROF: SALTA  (o lado NÃO muda — o frame é invisível)
            raq = (L_max nos ±5 frames) >= L_RAQUETE
            se ult existe E o lado É OUTRO E raq:  -> TRAVESSIA
            ult = lado                              <-- ⚠️ atualiza-se MESMO QUANDO raq é FALSO

⇒ SÓ HÁ DUAS MANEIRAS DE PERDER UMA TRAVESSIA:
    B. o flip de lado cai numa QUEBRA DE TRACKLET  (o `ult` reinicia a None; não há comparação)
    D. o flip acontece, mas L < 11  ⇒ a S15 rejeita-a **e o lado é atualizado na mesma**
       ⇒ a travessia desaparece SEM DEIXAR RASTO. Não volta a ser contada.
"""
import numpy as np
import gerar_tempo_util as G


def analisar():
    R, prof = G.carregar()
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    fs  = sorted(R2)
    Lmax = lambda f: max([R2[g][2] for g in fs if abs(g - f) <= 5] or [0])

    # replicar cruzamentos(), mas a REGISTAR o que se perde
    contadas, perdidas_D, perdidas_B = [], [], []
    for tk in tks:
        ult, ult_f = None, None
        for f in tk:
            l, p = prof(R2[f][0], R2[f][1])
            if p < G.MIN_PROF:
                continue
            L = Lmax(f)
            raq = L >= G.L_RAQUETE
            if ult and ult != l:
                (contadas if raq else perdidas_D).append((f, L, p))
            ult, ult_f = l, f
        # o fim de um tracklet: se o tracklet seguinte começar do outro lado, o flip PERDE-SE
    # quebras de tracklet: o lado do último frame profundo de um tracklet vs o 1º do seguinte
    def ultimo_prof(tk, rev=False):
        seq = reversed(tk) if rev else tk
        for f in seq:
            l, p = prof(R2[f][0], R2[f][1])
            if p >= G.MIN_PROF:
                return f, l
        return None, None
    for t1, t2 in zip(tks, tks[1:]):
        fa, la = ultimo_prof(t1, rev=True)
        fb, lb = ultimo_prof(t2)
        if la and lb and la != lb:
            perdidas_B.append((fb, fa))

    idx = lambda L: {f for f, *_ in L}
    C, D = idx(contadas), idx(perdidas_D)
    B = {f for f, _ in perdidas_B}

    print("\n" + "=" * 96)
    print("AS TRAVESSIAS QUE SE PERDEM — replicando o cruzamentos() à letra")
    print("=" * 96)
    print(f"\nTOTAL:  contadas {len(contadas)}  |  "
          f"perdidas por L<{G.L_RAQUETE} (S15): {len(perdidas_D)}  |  "
          f"perdidas em quebra de tracklet: {len(perdidas_B)}\n")

    tot_c = tot_d = tot_b = 0
    for k, (t0, t1) in enumerate(G.GT, 1):
        f0, f1 = int(t0 * G.FPS), int(t1 * G.FPS)
        c = [f for f in C if f0 <= f <= f1]
        d = [(f, L, p) for f, L, p in perdidas_D if f0 <= f <= f1]
        b = [f for f in B if f0 <= f <= f1]
        tot_c += len(c); tot_d += len(d); tot_b += len(b)
        dur = t1 - t0
        frag = "  🚨 FRÁGIL" if len(c) <= 1 and dur > 4 else ""
        print(f"── PONTO {k:>2} ({t0:6.1f}–{t1:6.1f}s · {dur:4.1f}s) │ "
              f"contadas {len(c):>2} │ perdidas: L-baixo {len(d):>2}, quebra {len(b):>2}{frag}")
        if frag:
            for f, L, p in d:
                print(f"        💀 t={f/G.FPS:.1f}s  atravessa a rede, mas L={L:.1f} < {G.L_RAQUETE}"
                      f"  (prof {p:.2f}) → a S15 diz 'veio da MÃO' e DEITA-A FORA")
            for f in b:
                print(f"        💀 t={f/G.FPS:.1f}s  atravessa a rede numa QUEBRA de tracklet"
                      f" → não há com que comparar")

    print("\n" + "-" * 96)
    print(f"NO TOTAL, DENTRO DOS PONTOS REAIS:  contadas {tot_c}  |  "
          f"perdidas por L-baixo {tot_d}  |  perdidas por quebra {tot_b}")
    print(f"⇒ o código VÊ {100*tot_c/max(tot_c+tot_d+tot_b,1):.0f}% das travessias que a bola faz.")
    print("\n⚠️ Nada foi alterado. Leitura pura.\n")


if __name__ == "__main__":
    analisar()
