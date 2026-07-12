#!/usr/bin/env python3
"""
Liga a deteção SEM CAP às regras J do Vasco e mostra quantos JOGADORES REAIS
sobram por frame. É o teste que decide a peça (reproduzível em CUDA e em MPS).

    python3 testar_jogadores_regras_J.py  <players_detections_*.json>  [calibracao.json]

NÃO altera o pipeline. Só corre os filtros que já estão em padelpro/modules/servico.py:
  J1 fora-do-campo + imóveis  (filtrar_espectadores)
  J4 dois-por-lado            (dois_por_lado, com as confianças do JSON)
  continuidade por ID         (continuidade_jogadores — preenche buracos)
"""
import sys, os, json, collections
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padelpro.modules.servico import (
    Campo, filtrar_espectadores, dois_por_lado, continuidade_jogadores,
)


def dist(boxes, rotulo):
    n = len(boxes)
    lens = [len(f) for f in boxes]
    c = collections.Counter(lens)
    med = sum(lens) / max(n, 1)
    p4 = 100 * sum(1 for l in lens if l >= 4) / max(n, 1)
    p2 = 100 * sum(1 for l in lens if l >= 2) / max(n, 1)
    print(f"\n{rotulo}")
    print(f"  media/frame: {med:.2f}   ·   >=2: {p2:.1f}%   ·   >=4: {p4:.1f}%")
    print(f"  distrib nº/frame: {dict(sorted(c.items()))}")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    jpath = sys.argv[1]
    cal_p = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "calibracao_campo.json")

    bruto = json.load(open(jpath))
    boxes = [[tuple(map(float, p["xyxy"])) for p in fr] for fr in bruto]
    confs = [[float(p.get("confidence", 1.0)) for p in fr] for fr in bruto]
    ids = [{int(p["id"]): tuple(map(float, p["xyxy"]))
            for p in fr if p.get("id") is not None} for fr in bruto]
    campo = Campo(json.load(open(cal_p)))

    print("=" * 66)
    print(f"JOGADORES — deteção SEM CAP + regras J   ({os.path.basename(jpath)})")
    print("=" * 66)
    dist(boxes, "[0] BRUTO (sem cap, inclui público)")

    # J1 + imóveis
    limpo, rel = filtrar_espectadores(boxes, campo)
    print(f"\n[J1] fora-do-campo + imóveis:")
    print(f"  descartadas fora-do-campo: {rel['descartadas_fora_do_campo']}"
          f"  ·  imóveis: {rel['descartadas_imoveis']}")
    dist(limpo, "    -> depois de J1")

    # J4 dois-por-lado (usa as confianças)
    quatro = dois_por_lado(limpo, campo, confs=None)  # confs alinham com 'boxes', nao com 'limpo'
    dist(quatro, "[J4] dois-por-lado (máx 2 de cada lado da rede)")

    # resumo do que interessa
    n = len(quatro); lens = [len(f) for f in quatro]
    p4 = 100 * sum(1 for l in lens if l >= 4) / max(n, 1)
    p3 = 100 * sum(1 for l in lens if l >= 3) / max(n, 1)
    print("\n" + "=" * 66)
    print(f"RESULTADO: depois das regras J, {p4:.1f}% dos frames têm os 4 jogadores,")
    print(f"           {p3:.1f}% têm >=3.   (o cap max_det=4 dava 4 'a martelo', mas")
    print(f"           metade eram espectadores; aqui os 4 são jogadores a sério.)")
    print("=" * 66)


if __name__ == "__main__":
    main()
