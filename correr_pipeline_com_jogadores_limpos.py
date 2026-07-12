#!/usr/bin/env python3
"""
Corre o pipeline do tempo util com um .pkl de jogadores DIFERENTE, SEM tocar no
gerar_tempo_util.py (Regra Zero). Faz monkeypatch da constante BOXES e compara
com o baseline travado.

    python3 correr_pipeline_com_jogadores_limpos.py  <player_boxes_limpo.pkl>

Isto NAO altera nada permanente. So mostra o que a ligacao (BOXES -> pkl limpo)
daria, para o Vasco decidir. O padrao-ouro e o teste_regressao ficam intactos.
"""
import sys, os, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_tempo_util as gt


def corre_com(boxes_path):
    # Espelha teste_regressao.py LINHA A LINHA: json.load/pickle.load FRESCOS em
    # cada chamada (nao partilhar dicts/listas -- evita mutacao de estado).
    R, prof = gt.carregar()
    R = gt.vai_e_vem(R)
    tks = gt.tracklets(R)
    CR = gt.cruzamentos(R, tks, prof)
    PAN = gt.pancadas(R, json.load(open(gt.CAL)),
                      pickle.load(open(boxes_path, "rb"))["player_boxes"])
    FIM = gt.fim_certo(R, json.load(open(gt.CAL)),
                       pickle.load(open(boxes_path, "rb"))["player_boxes"])
    RES = gt.ressaltos(R, tks)
    M = gt.rallies(CR, PAN, FIM, RES, R, prof)
    r = gt.avaliar(M)
    r["pancadas"] = len(PAN); r["fim_certo"] = len(FIM)
    return r


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    limpo = sys.argv[1]

    base = corre_com(gt.BOXES)          # padrao-ouro (o que esta' travado)
    novo = corre_com(limpo)             # jogadores limpos (sem cap + regras J)

    linha = "{:<12}{:>12}{:>12}{:>10}"
    print("=" * 46)
    print(linha.format("metrica", "TRAVADO", "LIMPO", "delta"))
    print("-" * 46)
    for k in ("recall", "precisao", "f1", "servicos", "n", "pancadas", "fim_certo"):
        b, x = base.get(k), novo.get(k)
        if isinstance(b, float):
            print(linha.format(k, f"{b:.1f}", f"{x:.1f}", f"{x-b:+.1f}"))
        else:
            print(linha.format(k, str(b), str(x), f"{x-b:+d}"))
    print("=" * 46)
    print("tempo util:  travado %.1fs   ·   limpo %.1fs" % (base["tempo"], novo["tempo"]))
    print("\n(A coluna TRAVADO reproduz o que o teste_regressao.py trava AGORA -- "
          "confirma que bate com ele antes de confiar no delta.)")


if __name__ == "__main__":
    main()
