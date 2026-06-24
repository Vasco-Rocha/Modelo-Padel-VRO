"""Modulo 3 — Pancadas e erros.

Recebe as pancadas ja detetadas/classificadas pelo padel_analytics e acrescenta
a camada de RESULTADO: a ultima pancada de cada rally e' classificada como
winner / erro forcado / erro nao forcado; as restantes ficam 'in_play'.

A classificacao forcado/nao-forcado e' HEURISTICA e deve ser calibrada com dados
anotados. Esta funcao esta isolada (`classify_outcome`) para ser facilmente
substituida por um classificador treinado (ex.: alimentado por auto-labels Gemini).
"""
from __future__ import annotations
from typing import Optional
import numpy as np

from ..core.schema import GameData, Shot


def classify_outcome(
    shot: Shot,
    reach_distance: Optional[float],
    forced_speed_threshold: float = 18.0,
    forced_reach_threshold_m: float = 2.0,
) -> str:
    """Heuristica: erro forcado se a bola vinha rapida OU o jogador estava longe.

    Substituir por modelo treinado quando houver dataset anotado.
    """
    fast = shot.incoming_ball_speed is not None and shot.incoming_ball_speed >= forced_speed_threshold
    far = reach_distance is not None and reach_distance >= forced_reach_threshold_m
    return "forced_error" if (fast or far) else "unforced_error"


def _reach_distance(game: GameData, shot: Shot) -> Optional[float]:
    """Distancia do jogador a' bola no instante da pancada (se houver bola)."""
    if not game.has_ball:
        return None
    df = game.frames
    row = df.loc[df["frame"] == shot.frame]
    if row.empty or f"p{shot.player_id}_x" not in df:
        return None
    row = row.iloc[0]
    if any(np.isnan([row.get("ball_x", np.nan), row.get(f"p{shot.player_id}_x", np.nan)])):
        return None
    return float(np.hypot(row["ball_x"] - row[f"p{shot.player_id}_x"],
                          row["ball_y"] - row[f"p{shot.player_id}_y"]))


def analyze_shots(
    game: GameData,
    shots: list[Shot],
    rallies: list[dict],
    forced_speed_threshold: float = 18.0,
    forced_reach_threshold_m: float = 2.0,
) -> dict:
    shots = sorted(shots, key=lambda s: s.frame)

    # associar cada pancada a um rally e marcar a ultima de cada rally
    for r in rallies:
        in_rally = [s for s in shots if r["start_frame"] <= s.frame <= r["end_frame"]]
        for s in in_rally:
            s.rally_index = r["index"]
            s.outcome = "in_play"
        if in_rally:
            last = in_rally[-1]
            last.reach_distance = _reach_distance(game, last)
            # heuristica simples: ultima pancada do rally e' o erro que o terminou
            last.outcome = classify_outcome(
                last, last.reach_distance,
                forced_speed_threshold, forced_reach_threshold_m,
            )

    # estatisticas por jogador
    per_player: dict[int, dict] = {}
    for s in shots:
        p = per_player.setdefault(s.player_id, {
            "total": 0, "by_stroke": {}, "winners": 0,
            "forced_errors": 0, "unforced_errors": 0,
        })
        p["total"] += 1
        p["by_stroke"][s.stroke] = p["by_stroke"].get(s.stroke, 0) + 1
        if s.outcome == "winner":
            p["winners"] += 1
        elif s.outcome == "forced_error":
            p["forced_errors"] += 1
        elif s.outcome == "unforced_error":
            p["unforced_errors"] += 1

    return {
        "n_shots": len(shots),
        "outcomes": {
            "in_play": sum(1 for s in shots if s.outcome == "in_play"),
            "winner": sum(1 for s in shots if s.outcome == "winner"),
            "forced_error": sum(1 for s in shots if s.outcome == "forced_error"),
            "unforced_error": sum(1 for s in shots if s.outcome == "unforced_error"),
        },
        "per_player": per_player,
        "shots": [vars(s) for s in shots],
        "note": "outcome heuristico (calibrar com dados anotados; ver classify_outcome).",
    }
