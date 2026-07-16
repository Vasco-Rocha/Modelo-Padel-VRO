#!/usr/bin/env python3
"""
S4 vs S9 vs S10 — QUAL MATA MAIS LIXO?   *** SÓ MEDE. O gerar_tempo_util.py NÃO é tocado. ***

    python3 testar_cruzado_s4_s9_s10.py

O testbed é o `m3_candidatos.py`: varre TODOS os quiques e devolve os CANDIDATOS a serviço
(Parada4: 37 candidatos = 13 reais + 24 falsos). A pergunta honesta, à Vasco:

    "de cada uma das TRÊS regras, quantos dos 24 FALSOS mata SEM perder um único dos 13 reais?"

⚖️ As três PONTUAM, não VETAM (D18). Aqui mede-se o poder de cada uma como SCORER — não se corta.

────────────────────────────────────────────────────────────────────────────────────────
AS TRÊS, e como cada uma se lê no sinal que existe:

  cada candidato = (q, c):  q = frame do ÚLTIMO quique FUNDO (o DROP do servidor, no seu lado)
                            c = frame da 1.ª travessia da rede

  S4  · QUADRADO CRUZADO — depois do drop, a bola cruza e RESSALTA na DIAGONAL:
        no OUTRO lado da rede, DENTRO do quadrado de serviço (0<=prof<=1) e na METADE OPOSTA.
  S9  · MÃO -> CHÃO -> RAQUETE — antes do quique há bola LENTA numa box (mão);
        e depois do quique há uma PANCADA (raquetada). Sem o ritual, não é serviço.
  S10 · DUPLO RESSALTO — o serviço é a ÚNICA jogada que ressalta dos DOIS lados da rede.
        q já é um ressalto (lado do servidor) ⇒ tem de haver OUTRO no lado oposto.

⚠️ ATALHOS DECLARADOS (nenhum número mágico novo):
    · MARGEM_POS = 1,0 s  — janela depois da travessia onde procurar o ressalto do recetor.
    · S9 reusa QUIQUE_JANELA (3 s), MAO_L (3), MAO_RAIO (0,10) do próprio pipeline.
    · a geometria (rede, linhas de serviço, centro) sai TODA da calibracao_parada4.json.
    · a metade E/D vem de centro_coef_em_y (a central é uma linha, não um x fixo).

⚠️ Ainda é a BOLA. Mas no Parada4 o quique dá 13/13 (não é o Barbosa, onde a B19 morde).
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G
import m3_candidatos as M3

MARGEM_POS = 1.0   # s — janela depois da travessia (ATALHO DECLARADO)


def main():
    R, prof = G.carregar()
    R = G.vai_e_vem(R)
    tks = G.tracklets(R)
    CR  = G.cruzamentos(R, tks, prof)
    RES = G.ressaltos(R, tks)
    cand = M3.candidatos(R, prof, tks, CR, RES)

    cal   = json.load(open(G.CAL))
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R, cal, boxes)
    _, _, meio = G.campo(cal)
    cx = lambda y: float(np.polyval(cal["centro_coef_em_y"], y))

    fs = sorted(R)
    mp = int(MARGEM_POS * G.FPS)
    jan = int(G.QUIQUE_JANELA * G.FPS)

    def lado_prof(f):
        l, p = prof(R[f][0], R[f][1])
        return l, p

    def metade(f):
        return "E" if R[f][0] < cx(R[f][1]) else "D"

    def dist_box(f):
        x, y = R[f][0], R[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1 - x, 0, x - x2), max(y1 - y, 0, y - y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    # ---- as três, como predicados sobre um candidato (q, c) ----
    def recetor_ressaltos(q, c):
        """ressaltos no lado OPOSTO ao drop, entre o drop e a travessia+margem."""
        ls, _ = lado_prof(q)
        return [r for r in RES if q < r <= c + mp and lado_prof(r)[0] != ls]

    def S10(q, c):                       # duplo ressalto, lados opostos
        return bool(recetor_ressaltos(q, c))

    def S4(q, c):                        # ressalto do recetor no quadrado CRUZADO (diagonal)
        hs = metade(q)
        for r in recetor_ressaltos(q, c):
            _, p = lado_prof(r)
            if 0.0 <= p <= 1.0 and metade(r) != hs:      # dentro do quadrado + diagonal
                return True
        return False

    def S9(q, c):                        # mao -> chao(quique q) -> raquete
        mao = any(q - jan <= f < q and R[f][2] <= G.MAO_L and dist_box(f) <= G.MAO_RAIO
                  for f in fs)
        raq = any(q < p <= c for p in PAN)
        return mao and raq

    # ---- rotular reais/falsos (mesma regra do m3: quique a +-3s do inicio do ponto) ----
    def e_real(q):
        return any(g0 - 3.0 <= q / G.FPS <= g0 + 3.0 for g0, g1 in G.GT)

    reais  = [(q, c) for q, c in cand if e_real(q)]
    falsos = [(q, c) for q, c in cand if not e_real(q)]

    print("\n" + "=" * 92)
    print("S4 vs S9 vs S10  —  quantos dos 24 FALSOS mata cada uma, SEM perder reais?  (Parada4)")
    print("=" * 92)
    print(f"  candidatos: {len(cand)}   ·   reais: {len(reais)}   ·   falsos: {len(falsos)}\n")

    # ---- por candidato, para VER (a lei do Vasco: olhar antes de citar) ----
    print(f"  {'t(s)':>7} {'tipo':>6} │ {'S4':>3} {'S9':>3} {'S10':>3} │ recetor (lado/prof/metade)")
    print("  " + "-" * 78)
    for q, c in cand:
        rr = recetor_ressaltos(q, c)
        det = ""
        if rr:
            r = rr[0]; l, p = lado_prof(r)
            det = f"{l}/{p:.2f}/{metade(r)}  (drop {metade(q)})"
        tipo = "REAL" if e_real(q) else "lixo"
        print(f"  {q/G.FPS:>7.1f} {tipo:>6} │ "
              f"{'✅' if S4(q,c) else '·':>3} {'✅' if S9(q,c) else '·':>3} "
              f"{'✅' if S10(q,c) else '·':>3} │ {det}")

    # ---- o veredito: reais mantidos / falsos mortos ----
    print("\n  " + "-" * 78)
    print(f"  {'REGRA':>5} │ {'reais mantidos':>15} │ {'falsos MORTOS':>14} │ potencial")
    print("  " + "-" * 78)
    for nome, pred in [("S4", S4), ("S9", S9), ("S10", S10)]:
        keep_real = sum(pred(q, c) for q, c in reais)
        kill_lixo = sum(not pred(q, c) for q, c in falsos)
        perde = len(reais) - keep_real
        flag = "🚨 perde reais" if perde else "✅ 0 reais perdidos"
        print(f"  {nome:>5} │ {keep_real:>10}/{len(reais):<4} │ "
              f"{kill_lixo:>9}/{len(falsos):<4} │ {flag}")
    print("\n  ⚖️ PONTUAM, não vetam. 'falsos mortos' = quantos NÃO passam no filtro.")
    print("     Uma regra que perca um real NÃO pode cortar — só pesar (D18).")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
