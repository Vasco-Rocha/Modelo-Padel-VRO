#!/usr/bin/env python3
"""
A TRAVESSIA ÚNICA DOS PONTOS FRÁGEIS — É O SERVIÇO?   *** SÓ LÊ. ***

A OBJEÇÃO DO VASCO (13 jul):
    "mas essas travessias não serão sempre garantidas logo no serviço?"

SE FOR VERDADE, os pontos 10/11/13 NÃO são frágeis — estão pendurados no evento MAIS FIÁVEL
do jogo inteiro:
    · o serviço TEM de atravessar a rede   (senão não é serviço)
    · vem da RAQUETE                       (L alto — passa a S15 com folga)
    · cai no quadrado CRUZADO, longe da rede (profundidade alta — passa o MIN_PROF com folga)

Uma travessia que passa as três portas COM FOLGA não é um fio. É uma corda.

Isto mede, para CADA ponto:
    · quando cai a 1.ª travessia (relativa ao início do ponto)  -> é o serviço?
    · com que FOLGA passa cada porta: L vs L_RAQUETE(11) · prof vs MIN_PROF(0.35)
    · e se essa travessia desaparecesse, o ponto sobrevivia?
"""
import json, pickle
import numpy as np
import gerar_tempo_util as G


def main():
    R, prof = G.carregar()
    cal = json.load(open(G.CAL))
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R2, cal, boxes)
    FIM = G.fim_certo(R2, cal, boxes)
    CR  = G.cruzamentos(R2, tks, prof)

    fs = sorted(R2)
    Lmax = lambda f: max([R2[g][2] for g in fs if abs(g - f) <= 5] or [0])

    print("\n" + "=" * 104)
    print("A 1.ª TRAVESSIA DE CADA PONTO — é o SERVIÇO? E com que FOLGA passa as portas?")
    print("=" * 104)
    print(f"\n{'pt':>3} {'dur':>6} {'n_trav':>7} │ {'1a trav':>9} {'apos o inicio':>14} │ "
          f"{'L':>6} {'(min 11)':>9} │ {'prof':>6} {'(min 0.35)':>11}")
    print("-" * 104)

    frageis = []
    for k, (t0, t1) in enumerate(G.GT, 1):
        cs = sorted(c for c in CR if t0 <= c / G.FPS <= t1)
        if not cs:
            print(f"{k:>3} {t1-t0:>5.1f}s {0:>7} │  (nenhuma)")
            continue
        c0 = cs[0]
        t = c0 / G.FPS
        atraso = t - t0
        L = Lmax(c0)
        _, p = prof(R2[c0][0], R2[c0][1])
        folga_L = "✅ com folga" if L >= 2 * G.L_RAQUETE else (
                  "⚠️ rente" if L < 1.5 * G.L_RAQUETE else "🆗")
        folga_p = "✅ com folga" if p >= 2 * G.MIN_PROF else (
                  "⚠️ rente" if p < 1.5 * G.MIN_PROF else "🆗")
        marca = " ⬅️" if len(cs) == 1 else ""
        print(f"{k:>3} {t1-t0:>5.1f}s {len(cs):>7} │ {t:>8.1f}s {atraso:>13.1f}s │ "
              f"{L:>6.1f} {folga_L:>12} │ {p:>6.2f} {folga_p:>14}{marca}")
        if len(cs) == 1:
            frageis.append((k, t, atraso, L, p))

    # ---- é o serviço? o M1 dá 13/13 — vamos ver se a 1.ª travessia coincide com o arranque
    print("\n" + "-" * 104)
    print("OS PONTOS COM UMA TRAVESSIA SÓ:\n")
    for k, t, atraso, L, p in frageis:
        serv = ("👉 É O SERVIÇO (cai logo no arranque do ponto)" if atraso <= 2.5
                else "❓ NÃO é o arranque — cai a meio")
        print(f"  ponto {k:>2}:  travessia a {t:.1f}s = {atraso:.1f}s depois do inicio   "
              f"L={L:.1f}  prof={p:.2f}")
        print(f"            {serv}")

    # ---- o teste a sério: e se essa travessia desaparecesse?
    print("\n" + "=" * 104)
    print("TESTE DE FRAGILIDADE — tirar a 1.ª travessia de cada ponto, um de cada vez")
    print("(⚠️ isto NÃO é uma alteração — é uma simulação em memória, para ver o que aguenta)")
    print("=" * 104 + "\n")

    M0 = G.rallies(CR, PAN, FIM)
    r0 = G.avaliar(M0)
    print(f"  base: {r0['n']} segmentos · recall {r0['recall']:.1f} · serviços {r0['servicos']}/13\n")

    for k, (t0, t1) in enumerate(G.GT, 1):
        cs = sorted(c for c in CR if t0 <= c / G.FPS <= t1)
        if not cs:
            continue
        CR2 = [c for c in CR if c != cs[0]]
        M = G.rallies(CR2, PAN, FIM)
        r = G.avaliar(M)
        # o ponto k sobreviveu?
        vivo = any(a/G.FPS <= t1 and b/G.FPS >= t0 for a, b in M)
        est = "✅ sobrevive" if vivo else "💀 O PONTO DESAPARECE"
        aviso = "   <-- só tinha esta!" if len(cs) == 1 else ""
        print(f"  sem a 1.ª travessia do ponto {k:>2} ({len(cs)} no total): "
              f"{est}   recall {r['recall']:.1f}  serviços {r['servicos']}/13{aviso}")

    print("\n⚠️ Leitura pura. O gerar_tempo_util.py não foi alterado.\n")


if __name__ == "__main__":
    main()
