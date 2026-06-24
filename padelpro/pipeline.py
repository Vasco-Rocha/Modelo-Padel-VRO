"""Orquestra os 3 modulos sobre uma GameData."""
from __future__ import annotations
from typing import Optional

from .core.schema import GameData, Shot, MatchAnalysis
from .core.court import Court
from .modules import analyze_active_time, analyze_phases, analyze_shots


def run_pipeline(
    game: GameData,
    shots: Optional[list[Shot]] = None,
    config: Optional[dict] = None,
) -> MatchAnalysis:
    cfg = config or {}
    court_cfg = cfg.get("court", {})
    court = Court(**{k: court_cfg[k] for k in ("width", "length", "net_y") if k in court_cfg}) \
        if court_cfg else Court()

    at_cfg = cfg.get("active_time", {})
    active = analyze_active_time(game, **at_cfg)

    ph_cfg = cfg.get("phases", {})
    phases = analyze_phases(game, court=court, **ph_cfg)

    shots_out = {}
    if shots:
        sa_cfg = cfg.get("shots_analysis", {})
        shots_out = analyze_shots(game, shots, active["rallies"], **sa_cfg)

    return MatchAnalysis(
        fps=game.fps,
        duration_s=round(game.duration_s, 2),
        active_time=active,
        phases=phases,
        shots=shots_out,
    )
