#!/usr/bin/env python3
"""
🎾 A LEI DA FORMAÇÃO  —  a S2 e a S3 fundidas numa só   (14 jul 2026)

    ⚖️  A FORMAÇÃO DIZ QUEM SERVE.

        ① vejo os 4  ⇒  leio a formação DIRETA                        (era a S2)
        ② só vejo os 2 de cima  ⇒  DEDUZO a de baixo                  (era a S3)

    Não são duas regras. É a MESMA lei, lida com menos luz.
    (A dupla que SERVE: um atrás + o parceiro NA REDE.
     A dupla que RECEBE: os DOIS atrás.  As configurações são INCOMPATÍVEIS
     ⇒ a formação de uma dupla DEDUZ a da outra.)   — Vasco, 12 jul

🤝 E É LIDA DUAS VEZES, POR CAMINHOS INDEPENDENTES  (D14 · D16):

        leitura A — os JOGADORES:  quem está na rede?
        leitura B — a BOLA:        quem está mais perto dela no instante do serviço?

    Concordam  ⇒  sabemos quem serve.
    Discordam  ⇒  🚫 NÃO SE INVENTA. Diz-se "não sei".        (D14, à letra)

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py. Não corre modelo nenhum.
"""
import pickle, sys, csv
import numpy as np

import cascata_jogadores as C

BOLA = {"parada4": "../dados_parada4/traj_frames_Parada4.csv",
        "barbosa": "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"}[C.VID]

JANELA = 15          # ⚠️ AJUSTE (declarado): ±0,5 s à volta do início do ponto


def na_rede(b):
    """Está À FRENTE DA LINHA DE SERVIÇO (do lado dele) — ou ATRÁS?

    📐 D10 — É UMA LINHA. Passou, ou não passou. NÃO HÁ LIMIAR.

    🩸 14 jul — ERRO CORRIGIDO (o Vasco viu-o na imagem, eu não o vi em número nenhum):
       eu tinha escrito `abs(y-rede) < abs(y-linha)` — que é o PONTO MÉDIO entre a linha
       e a rede, não a LINHA. Um jogador a 1 m à frente da linha era lido como "ATRÁS".
       "Vê os pés do jogador de vermelho. Está claramente à frente da linha de serviço.
        Porque não é detetado como estando à frente?"  — porque eu inventei uma linha.
    """
    x, y = C.pes(b)
    y_rede = C.y_base(x)
    if y > y_rede:                                        # lado de BAIXO (perto da câmara)
        return y < C.ev(C.cal["servico_perto_coef"], x)   # à frente = ACIMA da linha
    return y > C.ev(C.cal["servico_longe_coef"], x)       # lado de CIMA: à frente = ABAIXO


def leitura_A_jogadores(fr):
    """A FORMAÇÃO. Devolve o lado de quem SERVE, ou None."""
    for l in ("cima", "baixo"):
        eq = [b for b in fr if C.lado(b) == l]
        if len(eq) != 2:
            continue
        n = sum(na_rede(b) for b in eq)
        if n == 1:                       # 1 na rede + 1 atrás  ⇒  ESTA dupla SERVE
            return l
        if n == 0:                       # os 2 atrás           ⇒  esta RECEBE ⇒ serve a OUTRA
            return "baixo" if l == "cima" else "cima"
    return None


def leitura_B_bola(fr, xy):
    """A BOLA. Quem está mais perto dela no instante do serviço? Esse é o SERVIDOR.
       Independente da formação — não usa a rede, não usa a linha de serviço."""
    if xy is None or not fr:
        return None
    bx, by = xy
    perto = min(fr, key=lambda b: (bx - (b[0] + b[2]) / 2) ** 2 + (by - b[3]) ** 2)
    return C.lado(perto)


def main():
    pb0 = pickle.load(open(C.BOXES, "rb"))["player_boxes"]
    pb = C.j4_dois_por_lado(C.j5_continuidade(C.j1_pes_no_poligono(pb0))[0])

    R = {}
    for r in csv.DictReader(open(BOLA)):
        if int(r["Visibility"]) and float(r["X"]):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))

    print("=" * 88)
    print(f"🎾 A LEI DA FORMAÇÃO — {C.VID.upper()}   ({len(C.GT)} serviços)")
    print("=" * 88)
    print("   nível ① = vejo os 4   ·   nível ② = só os 2 de cima (DEDUZO)\n")
    print("   #     t       niv   A(jogadores)  B(bola)    veredito")
    print("   " + "-" * 66)

    acordo = so_A = so_B = nada = disc = 0
    for i, t in enumerate(C.GT, 1):
        f = int(t * C.FPS)
        jan = range(max(0, f - JANELA), min(len(pb), f + JANELA))
        # o frame mais limpo da janela: o que tem mais jogadores
        fb = max(jan, key=lambda k: len(pb[k]))
        fr = pb[fb]
        niv = "①" if len(fr) == 4 else ("②" if sum(C.lado(b) == "cima" for b in fr) == 2 else "—")

        xy = next((R[k] for k in sorted(jan, key=lambda k: abs(k - f)) if k in R), None)
        A, B = leitura_A_jogadores(fr), leitura_B_bola(fr, xy)

        if A and B and A == B:
            v, acordo = f"✅ serve {A.upper()}", acordo + 1
        elif A and B:
            v, disc = f"🚫 A diz {A}, B diz {B}  ⇒  NÃO SEI", disc + 1
        elif A:
            v, so_A = f"⚠️ só A: {A}", so_A + 1
        elif B:
            v, so_B = f"⚠️ só B: {B}", so_B + 1
        else:
            v, nada = "🔴 cego", nada + 1
        print(f"   {i:2}  {t:6.1f}s   {niv}    {str(A):6}       {str(B):6}     {v}")

    n = len(C.GT)
    print("\n   " + "-" * 66)
    print(f"   ✅ as DUAS leituras concordam ....... {acordo:2}/{n}  ({acordo/n*100:.0f}%)")
    print(f"   🚫 contradizem-se (⇒ não se inventa)  {disc:2}/{n}")
    print(f"   ⚠️ só uma leitura ................... {so_A + so_B:2}/{n}")
    print(f"   🔴 cego ............................. {nada:2}/{n}")


if __name__ == "__main__":
    main()
