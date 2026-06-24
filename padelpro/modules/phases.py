"""Modulo 2 — Fases de jogo.

Classifica cada frame pela formacao das duas duplas (rede / fundo / transicao),
a partir das posicoes projetadas no campo. As duplas sao inferidas pelo lado da
rede onde cada jogador joga maioritariamente.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

from ..core.schema import GameData, PhaseSegment
from ..core.court import Court


def _assign_teams(df: pd.DataFrame, court: Court) -> dict[str, list[int]]:
    near, far = [], []
    for pid in (1, 2, 3, 4):
        y = df[f"p{pid}_y"].median()
        (near if court.side(float(y)) == "near" else far).append(pid)
    return {"near": near, "far": far}


def _team_formation(df_row, pids, court: Court, attack_threshold_m: float) -> str:
    at_net = []
    for pid in pids:
        y = df_row.get(f"p{pid}_y", np.nan)
        if pd.isna(y):
            continue
        at_net.append(court.dist_to_net(float(y)) < attack_threshold_m)
    if not at_net:
        return "desconhecido"
    if all(at_net):
        return "rede"
    if not any(at_net):
        return "fundo"
    return "transicao"


def analyze_phases(
    game: GameData,
    court: Court | None = None,
    attack_threshold_m: float = 5.0,
) -> dict:
    court = court or Court()
    df = game.frames
    teams = _assign_teams(df, court)

    labels = []
    for _, row in df.iterrows():
        near_f = _team_formation(row, teams["near"], court, attack_threshold_m)
        far_f = _team_formation(row, teams["far"], court, attack_threshold_m)
        labels.append(f"near:{near_f}|far:{far_f}")
    df = df.assign(_phase=labels)

    # segmentos contiguos
    segments: list[PhaseSegment] = []
    frames_col = df["frame"].to_numpy()
    times_col = df["time"].to_numpy()
    start = 0
    for i in range(1, len(df) + 1):
        if i == len(df) or labels[i] != labels[start]:
            segments.append(PhaseSegment(
                phase=labels[start],
                start_frame=int(frames_col[start]),
                end_frame=int(frames_col[i - 1]),
                start_time=round(float(times_col[start]), 3),
                end_time=round(float(times_col[i - 1]), 3),
            ))
            start = i

    # distribuicao de tempo por fase
    dist: dict[str, float] = {}
    for seg in segments:
        dist[seg.phase] = round(dist.get(seg.phase, 0.0) + seg.duration, 2)

    return {
        "teams": teams,
        "n_segments": len(segments),
        "time_by_phase_s": dict(sorted(dist.items(), key=lambda kv: -kv[1])),
        "segments": [vars(s) | {"duration": s.duration} for s in segments],
    }
