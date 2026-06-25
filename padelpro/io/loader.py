"""Leitura do output do padel_analytics para a camada partilhada (GameData).

O CSV principal segue o `into_dataframe()` do repo do Joao:
colunas `player{id}_x/y` (metros) e `player{id}_Vnorm1` (velocidade).
Bola e pancadas vivem em ficheiros separados (opcionais).
"""
from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd

from ..core.schema import GameData, Shot


def default_config() -> dict:
    return {
        "fps": 30,
        # origin: "corner" (0..width, 0..length, rede em net_y) ou
        # "centered" (origem no centro, rede em y=0, x/y podem ser negativos —
        # como o padel_analytics produz). Em "centered" o loader desloca para "corner".
        "court": {"width": 10.0, "length": 20.0, "net_y": 10.0, "origin": "corner"},
        "columns": {
            "frame": "frame",
            "time": "time",
            "player_x": "player{id}_x",
            "player_y": "player{id}_y",
            "player_speed": "player{id}_Vnorm1",
        },
        "ball": {"path": None, "frame": "frame", "x": "ball_x", "y": "ball_y", "hit": "ball_hit"},
        "shots": {"path": None, "frame": "frame", "player_id": "player_id",
                  "stroke": "stroke", "incoming_ball_speed": "incoming_ball_speed"},
    }


def _read_table(path: str) -> pd.DataFrame:
    if str(path).endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def load_game_data(
    players_path: str,
    ball_path: Optional[str] = None,
    fps: Optional[float] = None,
    config: Optional[dict] = None,
) -> GameData:
    """Constroi GameData a partir do CSV de jogadores (+ bola opcional)."""
    cfg = config or default_config()
    cols = cfg["columns"]
    fps = fps or cfg.get("fps", 30)

    raw = _read_table(players_path)
    out = pd.DataFrame()
    out["frame"] = raw[cols["frame"]]
    if cols.get("time") and cols["time"] in raw:
        out["time"] = raw[cols["time"]]
    else:
        out["time"] = out["frame"] / fps

    speed_tmpl = cols.get("player_speed")
    for pid in (1, 2, 3, 4):
        xc = cols["player_x"].format(id=pid)
        yc = cols["player_y"].format(id=pid)
        out[f"p{pid}_x"] = raw.get(xc, np.nan)
        out[f"p{pid}_y"] = raw.get(yc, np.nan)
        scol = speed_tmpl.format(id=pid) if speed_tmpl else None
        if scol and scol in raw:
            out[f"p{pid}_speed"] = raw[scol]
        else:  # fallback: derivar das posicoes
            dt = out["time"].diff().replace(0, np.nan)
            dx = out[f"p{pid}_x"].diff()
            dy = out[f"p{pid}_y"].diff()
            out[f"p{pid}_speed"] = np.sqrt(dx**2 + dy**2) / dt

    has_ball = False
    bcfg = cfg.get("ball", {})
    bpath = ball_path or bcfg.get("path")
    if bpath:
        ball = _read_table(bpath)
        bframe = bcfg.get("frame", "frame")
        b = pd.DataFrame({"frame": ball[bframe]})
        b["ball_x"] = ball[bcfg.get("x", "ball_x")]
        b["ball_y"] = ball[bcfg.get("y", "ball_y")]
        if bcfg.get("hit") and bcfg["hit"] in ball:
            b["ball_hit"] = ball[bcfg["hit"]].astype(bool)
        out = out.merge(b, on="frame", how="left")
        dt = out["time"].diff().replace(0, np.nan)
        out["ball_speed"] = np.sqrt(out["ball_x"].diff()**2 + out["ball_y"].diff()**2) / dt
        has_ball = True

    # Referencial: se as coordenadas vêm centradas (rede em y=0), deslocar para
    # o referencial de canto (0..width, 0..length) que os módulos assumem.
    court_cfg = cfg.get("court", {})
    if court_cfg.get("origin") == "centered":
        dx = court_cfg.get("width", 10.0) / 2.0
        dy = court_cfg.get("length", 20.0) / 2.0
        for pid in (1, 2, 3, 4):
            out[f"p{pid}_x"] = out[f"p{pid}_x"] + dx
            out[f"p{pid}_y"] = out[f"p{pid}_y"] + dy
        if has_ball:
            out["ball_x"] = out["ball_x"] + dx
            out["ball_y"] = out["ball_y"] + dy

    out = out.sort_values("frame").reset_index(drop=True)
    return GameData(frames=out, fps=float(fps), has_ball=has_ball)


def load_shots(shots_path: str, fps: float, config: Optional[dict] = None) -> list[Shot]:
    """Le as pancadas detetadas pelo padel_analytics."""
    cfg = (config or default_config())["shots"]
    raw = _read_table(shots_path)
    speed_col = cfg.get("incoming_ball_speed")
    shots: list[Shot] = []
    for _, r in raw.iterrows():
        frame = int(r[cfg.get("frame", "frame")])
        spd = float(r[speed_col]) if speed_col and speed_col in raw.columns and not pd.isna(r[speed_col]) else None
        shots.append(Shot(
            frame=frame,
            time=frame / fps,
            player_id=int(r[cfg.get("player_id", "player_id")]),
            stroke=str(r[cfg.get("stroke", "stroke")]),
            incoming_ball_speed=spd,
        ))
    return shots
