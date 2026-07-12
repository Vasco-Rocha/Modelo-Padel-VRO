#!/usr/bin/env python3
"""
A/B — a travessia lê-se contra a BASE da rede ou contra o TOPO?
*** SÓ MEDE. Não altera o gerar_tempo_util.py. Faz uma CÓPIA do prof() em memória. ***

A IDEIA É DO VASCO (13 jul):
    "a travessia deve ser lida com a linha do TOPO da rede, não da base. Por isso detetas tão
     poucas. Os de cá perto da rede devolvem a bola muito ALTA e PERTO da rede — não dá tempo
     da bola passar, nos frames, o TOPO da rede."

PORQUÊ: a bola passa POR CIMA da rede, não pelo pé dela. A fronteira física entre os dois campos,
para uma bola em VOO, é a linha do TOPO — não a do chão.
(Hoje o `prof()` usa `rede_base_coef` para decidir CIMA vs BAIXO.)

A: BASE (o que corre hoje)   ·   B: TOPO (a ideia do Vasco)
Tudo o resto IGUAL: mesmos tracklets, mesmo MIN_PROF, mesma S15, mesmas regras, mesmo GT.
"""
import json, pickle
import numpy as np
import gerar_tempo_util as G


def fazer_prof(cal, chave_divisor):
    """O prof() do gerar_tempo_util, mas com o divisor CIMA/BAIXO à escolha."""
    ev = lambda c, t: float(np.polyval(c, t))
    y_div = lambda x: ev(cal[chave_divisor], x)
    y_sp  = lambda x: ev(cal["servico_perto_coef"], x)
    y_sl  = lambda x: ev(cal["servico_longe_coef"], x)

    def prof(x, y):
        yr = y_div(x)
        if y > yr:
            return "baixo", (y - yr) / max(y_sp(x) - yr, 1)
        return "cima", (yr - y) / max(yr - y_sl(x), 1)
    return prof


def correr(chave, R2, tks, cal, boxes, PAN, FIM):
    prof = fazer_prof(cal, chave)
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    r  = G.avaliar(M)
    # travessias dentro de pontos reais
    dentro = sum(1 for c in CR
                 if any(a <= c / G.FPS <= b for a, b in G.GT))
    return CR, M, r, dentro


def main():
    R, _ = G.carregar()
    cal = json.load(open(G.CAL))
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R2, cal, boxes)          # ⚠️ as pancadas NÃO dependem do divisor
    FIM = G.fim_certo(R2, cal, boxes)

    print("\n" + "=" * 84)
    print("A TRAVESSIA: contra a BASE da rede (hoje)  vs  contra o TOPO (a ideia do Vasco)")
    print("=" * 84)

    res = {}
    for nome, chave in (("A · BASE (hoje)", "rede_base_coef"),
                        ("B · TOPO (Vasco)", "rede_topo_coef")):
        CR, M, r, dentro = correr(chave, R2, tks, cal, boxes, PAN, FIM)
        res[nome] = (CR, M, r, dentro)
        print(f"\n{nome}")
        print(f"   travessias detetadas ......... {len(CR)}")
        print(f"   ... dentro de pontos reais ... {dentro}  ({100*dentro/max(len(CR),1):.0f}%)")
        print(f"   ... nos INTERVALOS ........... {len(CR)-dentro}")
        print(f"   segmentos .................... {r['n']}  (reais: {len(G.GT)})")
        print(f"   serviços ..................... {r['servicos']}/{len(G.GT)}")
        print(f"   >>> RECALL {r['recall']:.1f}%   PRECISAO {r['precisao']:.1f}%   F1 {r['f1']:.1f}")

    print("\n" + "-" * 84)
    (_, _, ra, da), (_, _, rb, db) = res["A · BASE (hoje)"], res["B · TOPO (Vasco)"]
    print(f"{'':22}{'BASE':>10}{'TOPO':>10}{'delta':>10}")
    for k, nome in (("recall", "RECALL"), ("precisao", "PRECISAO"), ("f1", "F1")):
        print(f"  {nome:<20}{ra[k]:>10.1f}{rb[k]:>10.1f}{rb[k]-ra[k]:>+10.1f}")
    print(f"  {'serviços':<20}{ra['servicos']:>10}{rb['servicos']:>10}{rb['servicos']-ra['servicos']:>+10}")
    print(f"  {'travessias':<20}{len(res['A · BASE (hoje)'][0]):>10}"
          f"{len(res['B · TOPO (Vasco)'][0]):>10}"
          f"{len(res['B · TOPO (Vasco)'][0])-len(res['A · BASE (hoje)'][0]):>+10}")

    # travessias por ponto — o que interessa: os pontos frágeis (10, 11, 13) melhoram?
    print("\n" + "-" * 84)
    print("TRAVESSIAS POR PONTO REAL     (os frágeis: 10, 11, 13)\n")
    print(f"  {'ponto':>6} {'dur':>6} {'BASE':>6} {'TOPO':>6}")
    for k, (t0, t1) in enumerate(G.GT, 1):
        na = sum(1 for c in res["A · BASE (hoje)"][0] if t0 <= c/G.FPS <= t1)
        nb = sum(1 for c in res["B · TOPO (Vasco)"][0] if t0 <= c/G.FPS <= t1)
        m = "  <--" if k in (10, 11, 13) else ""
        print(f"  {k:>6} {t1-t0:>5.1f}s {na:>6} {nb:>6}{m}")

    print("\n⚠️ O gerar_tempo_util.py NÃO foi alterado. Isto é uma cópia em memória.\n")


if __name__ == "__main__":
    main()
