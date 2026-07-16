#!/usr/bin/env python3
"""
🎬 AS FASES (M2)  —  DEFESA · TRANSIÇÃO · ATAQUE     (14 jul 2026)

Com as DUAS leis novas do Vasco, ambas nascidas a olhar para um frame:

  📏 D19 — A LINHA É A LINHA. Não se põe um LIMIAR em cima dela.
           "Passou a linha?" é BINÁRIO. Nada de pontos médios, margens ou percentagens.

  📏 D20 — EM CIMA DA LINHA ⇒ CONTA COMO ATRÁS.
           A fronteira pertence SEMPRE à zona MAIS RECUADA.
           (É a D1 — em dúvida, o estado mais conservador. E é uma verdade do jogo:
            quem tem o pé NA linha ainda não a passou.)

⚠️ E AS LINHAS SÃO AS DA PAREDE, NÃO A LINHA DE SERVIÇO. Está na calibração, dele:

    "TRANSICAO = a faixa entre as duas costuras da PAREDE (vidro|malha3 -> malha2|malha3).
     NAO e' a linha de servico. CONTRADIZ a F2 escrita — A F2 E' QUE ESTA' ERRADA.
     A linha de servico continua a valer para o SERVICO (S1/S9), que e' outra coisa."
                                                              — Vasco, 13 jul, no .json

⇒ 🔴 A **F2** do REGRAS_DO_VASCO.md ESTÁ ERRADA e tem de ser corrigida.

E a fase é da EQUIPA (F1), pela REGRA DAS DUAS BOXES (F2):
    DEFESA   = os DOIS atrás da costura de trás
    ATAQUE   = os DOIS à frente da costura da frente
    TRANSIÇÃO = tudo o resto  (o estado-resíduo — inclui um no fundo e outro na rede)

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py. Não corre modelo nenhum.
"""
import pickle, sys
import cascata_jogadores as C

# as costuras da PAREDE, por lado. (perto = campo de baixo · longe = campo de cima)
LINHAS = {
    "baixo": ("trans_perto_frente_coef", "trans_perto_tras_coef"),
    "cima":  ("trans_longe_frente_coef", "trans_longe_tras_coef"),
}


def fase_do_jogador(b):
    """📏 D19 + D20 — comparação BINÁRIA contra a linha; em cima da linha ⇒ ATRÁS."""
    x, y = C.pes(b)
    l = C.lado(b)
    frente, tras = (C.ev(C.cal[k], x) for k in LINHAS[l])

    if l == "baixo":                     # perto da câmara: y MAIOR = mais recuado
        if y >= tras:                    # 📏 D20 — em cima da linha ⇒ ATRÁS
            return "DEFESA"
        if y >= frente:                  # 📏 D20 — em cima ⇒ a zona mais recuada
            return "TRANSICAO"
        return "ATAQUE"

    if y <= tras:                        # lado de cima: y MENOR = mais recuado
        return "DEFESA"
    if y <= frente:
        return "TRANSICAO"
    return "ATAQUE"


def fase_da_equipa(fr, l):
    """👥 F1 — a fase é da EQUIPA, nunca do jogador.
       🧱 F2 — a REGRA DAS DUAS BOXES: só é DEFESA se forem AMBOS; só é ATAQUE se forem AMBOS.
               TRANSIÇÃO é o ESTADO-RESÍDUO (tudo o resto)."""
    eq = [b for b in fr if C.lado(b) == l]
    if len(eq) < 2:
        return None                      # 🚫 D2/D4 — não vejo os dois ⇒ NÃO INVENTO
    f = [fase_do_jogador(b) for b in eq]
    if all(x == "DEFESA" for x in f):
        return "DEFESA"
    if all(x == "ATAQUE" for x in f):
        return "ATAQUE"
    return "TRANSICAO"


def main():
    pb = C.j4_dois_por_lado(C.j5_continuidade(C.j1_pes_no_poligono(
        pickle.load(open(C.BOXES, "rb"))["player_boxes"]))[0])

    print("=" * 84)
    print(f"🎬 AS FASES — {C.VID.upper()}   (as costuras da PAREDE, não a linha de serviço)")
    print("=" * 84)
    print("   D19: a linha é a linha  ·  D20: em cima da linha ⇒ ATRÁS\n")
    print("   no INSTANTE DO SERVIÇO — quem serve devia estar em ATAQUE ou TRANSIÇÃO;")
    print("   quem recebe, os DOIS atrás ⇒ DEFESA.  É a prova das duas leis.\n")
    print("    #      t        CIMA         BAIXO      ")
    print("   " + "-" * 48)
    for i, t in enumerate(C.GT, 1):
        f = int(t * C.FPS)
        jan = range(max(0, f - 15), min(len(pb), f + 15))
        fb = max(jan, key=lambda k: len(pb[k]))
        fr = pb[fb]
        print(f"   {i:2}  {t:6.1f}s   {str(fase_da_equipa(fr,'cima')):10}  "
              f"{str(fase_da_equipa(fr,'baixo')):10}")

    print("\n   " + "-" * 48)
    print("   DISTRIBUIÇÃO NO VÍDEO INTEIRO (só onde vejo os 2 da equipa):")
    for l in ("cima", "baixo"):
        cont = {}
        for fr in pb:
            k = fase_da_equipa(fr, l)
            cont[k] = cont.get(k, 0) + 1
        n = sum(v for k, v in cont.items() if k)
        print(f"     {l:6} " + "  ".join(
            f"{k}: {v/n*100:4.1f}%" for k, v in sorted(cont.items(), key=lambda x: -x[1]) if k)
            + f"   (cego em {cont.get(None,0)/len(pb)*100:.0f}% dos frames)")


if __name__ == "__main__":
    main()
