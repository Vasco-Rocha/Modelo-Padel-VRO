#!/usr/bin/env python3
"""
S22 — O VOLLEY À REDE É UMA TRAVESSIA DUPLA.   *** SÓ MEDE. Não altera nada. ***

A REGRA É DO VASCO (13 jul):
    "Se a bola ENTROU numa bounding box perto da zona da rede, da parte de CIMA, e MUDOU DE
     DIREÇÃO, provavelmente serão DUAS travessias — porque deve ter havido pancada."

PORQUÊ: um jogador de cima que volleya à rede recebeu a bola do OUTRO lado (1.ª travessia) e
devolveu-a para o OUTRO lado (2.ª travessia). A bola atravessou DUAS VEZES — e o código não vê
NENHUMA, porque ela nunca chega a ficar FUNDA de nenhum dos lados: morre na faixa cega do
`MIN_PROF`, junto à rede.  **A pancada é a PROVA de que as duas travessias existiram.**

ZERO NÚMEROS NOVOS — tudo já existe no gerar_tempo_util:
    "dentro da box"      -> dist_box <= MAO_RAIO   (frações do meio-campo local, não píxeis)
    "mudou de direção"   -> |dTheta| >= PAN_DTHETA (o mesmo teste das pancadas)
    "perto da rede"      -> profundidade < MIN_PROF (é a PRÓPRIA faixa cega)
    "da parte de cima"   -> lado == "cima"

A/B/C/D:
    A  baseline (hoje)
    B  MIN_PROF=0.15         (baixar a faixa cega — traz travessias E lixo)
    C  S22, a regra do Vasco (MIN_PROF fica nos 0.35 — traz travessias, e lixo?)
    D  a minha ideia: baixar o MIN_PROF mas exigir que a travessia seja COERENTE no Theta
       (a bola que PASSA vai direita; o ruído a roçar a fita oscila) — a proteção passa a vir
       do Theta em vez da distância.
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G

ORIG = G.MIN_PROF


# ---------------------------------------------------------------- C: a regra do Vasco
def volleys_rede(R, PAN, prof, cal, boxes):
    """Os frames em que houve PANCADA (a lista PAN que o código já calcula — logo já exige
    bola A VOAR, L>=PAN_L, e jogador ao pé), e essa pancada aconteceu DENTRO de uma box,
    na faixa junto à REDE, do lado de CIMA.
    Cada um destes eventos = DUAS travessias que o código não viu.

    ⚠️ v2 — a v1 reimplementou "pancada" à mão e ESQUECEU-SE do L (bola a voar). Resultado:
       apanhava bolas PARADAS na mão de gente à rede, ENTRE pontos. 11 dos 13 eventos eram lixo.
       A regra do Vasco diz "deve ter havido PANCADA" — então usa-se a PANCADA do código."""
    _, _, meio = G.campo(cal)

    def dist_box(f):
        x, y = R[f][0], R[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    out = []
    for f in PAN:                                   # ← a PANCADA já vem feita
        if f not in R:
            continue
        lado, p = prof(R[f][0], R[f][1])
        if lado != "cima" or p >= ORIG:             # na FAIXA CEGA junto à rede, em CIMA
            continue
        if dist_box(f) > G.MAO_RAIO:                # DENTRO da box
            continue
        out.append(f)
    return out


# ---------------------------------------------------------------- D: a minha ideia (Theta)
def cruzamentos_theta(R, tks, prof, mp):
    """Como o cruzamentos(), mas o roçar-a-fita é rejeitado pelo THETA, não pela distância.
    A bola que PASSA vai direita (Theta coerente com o movimento). O ruído oscila."""
    fs = sorted(R)
    Lmax = lambda f: max([R[g][2] for g in fs if abs(g-f) <= 5] or [0])
    out = []
    for tk in tks:
        ult, ult_f = None, None
        for f in tk:
            l, p = prof(R[f][0], R[f][1])
            if p < mp:
                continue
            raq = Lmax(f) >= G.L_RAQUETE if G.REGRAS["S15_MAO_RAQUETE"] else True
            if ult and ult != l and raq:
                if G.erro_theta(R, ult_f, f) <= G.TOL_THETA:     # ← a proteção do Theta
                    out.append(f)
            ult, ult_f = l, f
    return sorted(out)


def metricas(CR, PAN, FIM):
    M = G.rallies(CR, PAN, FIM)
    r = G.avaliar(M)
    dentro = sum(1 for c in CR if any(a <= c/G.FPS <= b for a, b in G.GT))
    pp = [sum(1 for c in CR if t0 <= c/G.FPS <= t1) for t0, t1 in G.GT]
    fora = [s for s in M
            if not any(s[0]/G.FPS <= g1 and s[1]/G.FPS >= g0 for g0, g1 in G.GT)]
    return M, r, dentro, pp, fora


def main():
    R, prof = G.carregar()
    cal = json.load(open(G.CAL))
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R2, cal, boxes)
    FIM = G.fim_certo(R2, cal, boxes)

    G.MIN_PROF = ORIG
    CR_A = G.cruzamentos(R2, tks, prof)

    G.MIN_PROF = 0.15
    CR_B = G.cruzamentos(R2, tks, prof)
    G.MIN_PROF = ORIG

    VOL = volleys_rede(R2, PAN, prof, cal, boxes)
    CR_C = sorted(CR_A + VOL)                 # a regra do Vasco: o volley ancora o rally

    CR_D = cruzamentos_theta(R2, tks, prof, 0.15)

    print("\n" + "=" * 100)
    print("A REGRA DO VASCO: o VOLLEY À REDE é uma travessia DUPLA")
    print("=" * 100)
    print(f"\nvolleys à rede detetados (pancada DENTRO da box, na faixa junto à rede, em CIMA): "
          f"{len(VOL)}")
    print(f"   ⇒ implicam {2*len(VOL)} travessias que o código NÃO via\n")

    linhas = [("A · hoje (MIN_PROF 0.35)", CR_A),
              ("B · MIN_PROF 0.15",        CR_B),
              ("C · S22 VOLLEY (Vasco)",   CR_C),
              ("D · Theta em vez de dist", CR_D)]

    print(f"{'':28}{'travess':>8}{'nos pts':>8}{'interv':>7}{'segm':>6}{'serv':>6}"
          f"{'RECALL':>8}{'PRECISAO':>9}{'F1':>7}{'lixo':>6}")
    print("-" * 100)
    guard = {}
    for nome, CR in linhas:
        M, r, dentro, pp, fora = metricas(CR, PAN, FIM)
        guard[nome] = (pp, fora)
        print(f"{nome:<28}{len(CR):>8}{dentro:>8}{len(CR)-dentro:>7}{r['n']:>6}"
              f"{r['servicos']:>6}{r['recall']:>8.1f}{r['precisao']:>9.1f}{r['f1']:>7.1f}"
              f"{len(fora):>6}")

    print("\n" + "-" * 100)
    print("TRAVESSIAS POR PONTO — os frágeis: 10, 11, 13\n")
    print(f"  {'pt':>3}{'dur':>7}" + "".join(f"{n.split(' · ')[0]:>9}" for n, _ in linhas))
    for k in range(13):
        t0, t1 = G.GT[k]
        m = "  <--" if k+1 in (10, 11, 13) else ""
        print(f"  {k+1:>3}{t1-t0:>6.1f}s"
              + "".join(f"{guard[n][0][k]:>9}" for n, _ in linhas) + m)

    print("\n" + "-" * 100)
    for nome, _ in linhas:
        fora = guard[nome][1]
        if fora:
            s = ", ".join(f"{a/G.FPS:.0f}-{b/G.FPS:.0f}s" for a, b in fora)
            print(f"  LIXO em {nome}: {s}")
        else:
            print(f"  LIXO em {nome}: nenhum ✅")

    G.MIN_PROF = ORIG
    print("\n⚠️ O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
