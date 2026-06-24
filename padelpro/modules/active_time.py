"""Modulo 1 — Tempo util de jogo.

Segmenta o jogo em rallies vs. pausas. Sinal de movimento: a bola, se disponivel;
senao, a media da velocidade dos jogadores. Regra v9: bola parada/fora > min_pause_s
fecha o rally.
"""
from __future__ import annotations
from typing import Optional
import numpy as np

from ..core.schema import GameData, Rally


def _motion_signal(game: GameData) -> np.ndarray:
    df = game.frames
    if game.has_ball and "ball_speed" in df:
        return df["ball_speed"].fillna(0.0).to_numpy()
    speeds = [df[c].fillna(0.0).to_numpy() for c in game.player_speed_columns()]
    return np.mean(speeds, axis=0) if speeds else np.zeros(len(df))


def analyze_active_time(
    game: GameData,
    speed_threshold: float = 1.5,
    min_pause_s: float = 2.0,
    min_rally_s: float = 1.0,
) -> dict:
    df = game.frames
    fps = game.fps
    signal = _motion_signal(game)
    active = signal >= speed_threshold

    # transforma em segmentos contiguos de "ativo", fundindo pausas curtas
    min_pause_frames = int(round(min_pause_s * fps))
    rallies: list[Rally] = []
    i, n = 0, len(active)
    idx = 0
    while i < n:
        if not active[i]:
            i += 1
            continue
        start = i
        gap = 0
        j = i
        while j < n:
            if active[j]:
                end = j
                gap = 0
            else:
                gap += 1
                if gap > min_pause_frames:
                    break
            j += 1
        frames_col = df["frame"].to_numpy()
        times_col = df["time"].to_numpy()
        r = Rally(
            index=idx,
            start_frame=int(frames_col[start]),
            end_frame=int(frames_col[end]),
            start_time=round(float(times_col[start]), 3),
            end_time=round(float(times_col[end]), 3),
        )
        if r.duration >= min_rally_s:
            rallies.append(r)
            idx += 1
        i = j

    total = game.duration_s
    active_s = round(sum(r.duration for r in rallies), 2)
    durations = [r.duration for r in rallies]
    return {
        "n_rallies": len(rallies),
        "active_time_s": active_s,
        "match_time_s": round(total, 2),
        "active_ratio": round(active_s / total, 3) if total else 0.0,
        "avg_rally_s": round(float(np.mean(durations)), 2) if durations else 0.0,
        "longest_rally_s": round(max(durations), 2) if durations else 0.0,
        "signal_source": "ball" if game.has_ball else "players",
        "rallies": [vars(r) | {"duration": r.duration} for r in rallies],
    }
