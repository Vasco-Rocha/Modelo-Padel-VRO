"""Gerador de dados sinteticos para testar os modulos sem GPU nem video."""
from __future__ import annotations
import numpy as np
import pandas as pd

from ..core.schema import GameData, Shot


def make_synthetic_game(
    fps: int = 30,
    n_rallies: int = 4,
    seed: int = 0,
) -> tuple[GameData, list[Shot]]:
    """Cria um jogo fake: rallies com bola/jogadores em movimento e pausas entre eles.

    Devolve (GameData com bola, lista de Shots) — suficiente para exercitar os 3 modulos.
    """
    rng = np.random.default_rng(seed)
    rows = []
    shots: list[Shot] = []
    frame = 0
    # posicoes base das 4 duplas (2 perto, 2 longe da rede), campo 10x20, rede em y=10
    base = {1: (3.0, 4.0), 2: (7.0, 4.0), 3: (3.0, 16.0), 4: (7.0, 16.0)}

    def emit(frame, positions, ball_xy, ball_speed, ball_hit):
        row = {"frame": frame, "time": frame / fps,
               "ball_x": ball_xy[0], "ball_y": ball_xy[1],
               "ball_speed": ball_speed, "ball_hit": ball_hit}
        for pid, (x, y) in positions.items():
            row[f"p{pid}_x"] = x
            row[f"p{pid}_y"] = y
        rows.append(row)

    for r in range(n_rallies):
        rally_frames = int(fps * rng.uniform(4, 9))
        # durante o rally os jogadores sobem progressivamente a rede
        for k in range(rally_frames):
            t = k / rally_frames
            pos = {}
            for pid, (bx, by) in base.items():
                near = pid in (1, 2)
                # aproximar da rede (y=10) ao longo do rally
                y = by + (1 - t) * 0.0 + (t * (6.0 if near else -6.0))
                x = bx + rng.normal(0, 0.3)
                pos[pid] = (float(np.clip(x, 0.5, 9.5)), float(np.clip(y, 1, 19)))
            # bola a saltar de um lado para o outro
            ball_y = 10 + 8 * np.sin(2 * np.pi * (k / fps))
            ball_x = 5 + 3 * np.sin(2 * np.pi * (k / (fps * 0.7)))
            ball_speed = float(abs(15 + 6 * np.cos(2 * np.pi * (k / fps))))
            is_hit = (k % int(fps * 0.8) == 0) and k > 0
            emit(frame, pos, (ball_x, ball_y), ball_speed, is_hit)
            if is_hit:
                hitter = int(rng.choice([1, 2, 3, 4]))
                shots.append(Shot(
                    frame=frame, time=frame / fps, player_id=hitter,
                    stroke=str(rng.choice(["drive", "volei", "bandeja", "remate", "globo"])),
                    incoming_ball_speed=ball_speed,
                ))
            frame += 1
        # erro final do rally: pancada com bola parada a seguir
        last_hitter = int(rng.choice([1, 2, 3, 4]))
        shots.append(Shot(
            frame=frame - 1, time=(frame - 1) / fps, player_id=last_hitter,
            stroke=str(rng.choice(["drive", "volei", "remate"])),
            incoming_ball_speed=float(rng.uniform(8, 25)),
        ))
        # pausa: tudo parado ~3s
        pause_frames = int(fps * rng.uniform(2.5, 4.0))
        last = {pid: (rows[-1][f"p{pid}_x"], rows[-1][f"p{pid}_y"]) for pid in (1, 2, 3, 4)}
        for k in range(pause_frames):
            emit(frame, last, (rows[-1]["ball_x"], rows[-1]["ball_y"]), 0.0, False)
            frame += 1

    df = pd.DataFrame(rows)
    # velocidade dos jogadores derivada
    dt = df["time"].diff().replace(0, np.nan)
    for pid in (1, 2, 3, 4):
        df[f"p{pid}_speed"] = np.sqrt(df[f"p{pid}_x"].diff()**2 + df[f"p{pid}_y"].diff()**2) / dt
    df = df.fillna(0.0)
    return GameData(frames=df, fps=float(fps), has_ball=True), shots
