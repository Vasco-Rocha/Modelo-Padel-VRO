"""Ligacao ao padel_analytics (Joao Silva) para a detecao de JOGADORES.

Le o `cache/players_detections.json` produzido pelo `PlayerTracker` dele
(yolov8m + polygon_zone + ByteTrack) e converte para o formato que os
modulos deste repo ja esperam: `player_boxes[frame] -> [(x1,y1,x2,y2), ...]`
em PIXEIS.

PORQUE ISTO EXISTE
------------------
As boxes do padel_analytics estao em pixeis ANTES da homografia. O campo
`projection` (metros) e separado e opcional. Nao ha nada a converter e nao ha
nenhum detetor para treinar: e ligar o que ja existe.

NAO improvisar outro detetor de jogadores. Ver HANDOFF_CENTRO_DECISOES.md.

Formato do JSON (uma lista por frame, cada item uma lista de jogadores):
    [[{"id": 1, "xyxy": [x1,y1,x2,y2], "projection": [...]|null,
       "class_id": 0, "confidence": 0.91}, ...], ...]
"""

from __future__ import annotations

import json
from pathlib import Path


def carregar_players(path: str | Path, n_frames: int | None = None,
                     conf_min: float = 0.0) -> list[list[tuple]]:
    """JSON do padel_analytics -> player_boxes em pixeis.

    Args:
        path: caminho do `players_detections.json`.
        n_frames: se dado, corta/estica a lista para este comprimento
                  (para alinhar com o traj.csv da bola).
        conf_min: descarta deteccoes abaixo desta confianca.

    Returns:
        Lista com um elemento por frame; cada elemento e uma lista de
        tuplos (x1, y1, x2, y2) em pixeis.
    """
    with open(path) as f:
        bruto = json.load(f)

    boxes: list[list[tuple]] = []
    for frame in bruto:
        do_frame = []
        for p in frame or []:
            if float(p.get("confidence", 1.0)) < conf_min:
                continue
            x1, y1, x2, y2 = (float(v) for v in p["xyxy"])
            do_frame.append((x1, y1, x2, y2))
        boxes.append(do_frame)

    if n_frames is not None:
        if len(boxes) < n_frames:
            boxes += [[] for _ in range(n_frames - len(boxes))]
        boxes = boxes[:n_frames]
    return boxes


def carregar_players_com_id(path: str | Path,
                            conf_min: float = 0.0) -> list[dict[int, tuple]]:
    """Igual a `carregar_players` mas preserva o tracker_id do ByteTrack.

    Devolve, por frame, {id: (x1,y1,x2,y2)}. O id e estavel ao longo do video
    (e o que permite seguir um jogador atraves de frames falhados) -- serve
    para as regras que precisam de identidade (alternancia, lado do servico).
    """
    with open(path) as f:
        bruto = json.load(f)

    saida: list[dict[int, tuple]] = []
    for frame in bruto:
        do_frame: dict[int, tuple] = {}
        for p in frame or []:
            if float(p.get("confidence", 1.0)) < conf_min:
                continue
            pid = p.get("id")
            if pid is None:
                continue
            x1, y1, x2, y2 = (float(v) for v in p["xyxy"])
            do_frame[int(pid)] = (x1, y1, x2, y2)
        saida.append(do_frame)
    return saida


def pes(box: tuple) -> tuple[float, float]:
    """Ponto dos PES da box (meio da aresta de baixo). E o que a formacao usa:
    onde o jogador ESTA no campo, nao onde esta a cabeca dele."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, y2)


def cobertura(player_boxes: list[list[tuple]], inicio: int = 0,
              fim: int | None = None) -> dict:
    """Diagnostico do SINAL -- e isto que estava a 53% com o yolov8n improvisado.

    Devolve a % de frames com 4, >=3 e >=1 jogadores. O numero que interessa
    e `pct_4`: a formacao de servico so consegue decidir com os 4 presentes.
    """
    fim = len(player_boxes) if fim is None else fim
    janela = player_boxes[inicio:fim]
    n = len(janela) or 1
    n4 = sum(1 for b in janela if len(b) >= 4)
    n3 = sum(1 for b in janela if len(b) >= 3)
    n1 = sum(1 for b in janela if len(b) >= 1)
    return {
        "frames": len(janela),
        "pct_4": round(100.0 * n4 / n, 1),
        "pct_3mais": round(100.0 * n3 / n, 1),
        "pct_1mais": round(100.0 * n1 / n, 1),
        "media_por_frame": round(sum(len(b) for b in janela) / n, 2),
    }
