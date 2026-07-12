#!/usr/bin/env python3
"""
Gera um .pkl de JOGADORES já LIMPO pelas regras J do Vasco, pronto para o pipeline.

    python3 gerar_pkl_jogadores_limpos.py \
        <players_detections_SEM_CAP.json>  <saida.pkl>  [calibracao.json]  [fps]

Aplica a cascata que JA existe em padelpro/modules/servico.py, na versao SEM cap
(a que preserva os jogadores todos):
    J1  filtrar_espectadores  (fora-do-campo + imoveis)
    J4  dois_por_lado         (max 2 de cada lado da rede)

Escreve { "player_boxes": [ [(x1,y1,x2,y2),...] por frame ], "fps": float } — o
formato exacto que gerar_tempo_util.py le em BOXES.

NAO toca no pipeline. So produz o ficheiro. Ligar o pipeline a este .pkl (mudar
BOXES) e' decisao do Vasco: MUDA os numeros travados (usa jogadores a serio em vez
das boxes cruas do padrao-ouro).
"""
import sys, os, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padelpro.modules.servico import Campo, filtrar_espectadores, dois_por_lado


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    jpath, out = sys.argv[1], sys.argv[2]
    cal_p = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "calibracao_campo.json")
    fps = float(sys.argv[4]) if len(sys.argv) > 4 else None

    bruto = json.load(open(jpath))
    boxes = [[tuple(map(float, p["xyxy"])) for p in fr] for fr in bruto]
    campo = Campo(json.load(open(cal_p)))

    antes = sum(len(f) for f in boxes)
    limpo, rel = filtrar_espectadores(boxes, campo)
    quatro = dois_por_lado(limpo, campo, confs=None)
    depois = sum(len(f) for f in quatro)

    if fps is None:
        fps = 29.97
    pickle.dump({"player_boxes": quatro, "fps": fps}, open(out, "wb"))

    n = len(quatro)
    p4 = 100 * sum(1 for f in quatro if len(f) >= 4) / max(n, 1)
    p3 = 100 * sum(1 for f in quatro if len(f) >= 3) / max(n, 1)
    print(f"✅ {out}")
    print(f"   frames: {n} · fps: {fps}")
    print(f"   boxes: {antes} (bruto) -> {depois} (limpo)   "
          f"[fora-do-campo {rel['descartadas_fora_do_campo']}, imoveis {rel['descartadas_imoveis']}]")
    print(f"   com os 4 jogadores: {p4:.1f}%   ·   com >=3: {p3:.1f}%")


if __name__ == "__main__":
    main()
