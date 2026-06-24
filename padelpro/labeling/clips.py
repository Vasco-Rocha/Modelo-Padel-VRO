"""Recorta uma janela em torno de cada pancada e calcula features de contexto."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import os
import shutil
import subprocess
import numpy as np

from ..core.schema import GameData, Shot
from ..core.court import Court


@dataclass
class ShotClip:
    clip_id: str
    shot: Shot
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float
    features: dict = field(default_factory=dict)
    video_path: Optional[str] = None   # preenchido por cut_video_clips


def _row_at(game: GameData, frame: int):
    df = game.frames
    sub = df.loc[df["frame"] == frame]
    return sub.iloc[0] if not sub.empty else None


def _features(game: GameData, shot: Shot, court: Court, rallies: list[dict] | None) -> dict:
    feats: dict = {"incoming_ball_speed": shot.incoming_ball_speed}
    row = _row_at(game, shot.frame)
    if row is not None:
        px, py = row.get(f"p{shot.player_id}_x"), row.get(f"p{shot.player_id}_y")
        if px is not None and not np.isnan(px):
            feats["player_zone"] = court.zone(float(px), float(py))
            feats["dist_to_net"] = round(court.dist_to_net(float(py)), 2)
        if game.has_ball and "ball_x" in row and not np.isnan(row.get("ball_x", np.nan)):
            if px is not None and not np.isnan(px):
                feats["reach_distance"] = round(
                    float(np.hypot(row["ball_x"] - px, row["ball_y"] - py)), 2
                )
    if rallies:
        for r in rallies:
            if r["start_frame"] <= shot.frame <= r["end_frame"]:
                feats["rally_index"] = r["index"]
                feats["is_last_in_rally"] = (shot.frame == r["end_frame"]) or \
                    (r["end_frame"] - shot.frame) <= int(0.3 * game.fps)
                break
    return feats


def extract_clips(
    game: GameData,
    shots: list[Shot],
    pre_s: float = 1.5,
    post_s: float = 1.0,
    court: Court | None = None,
    rallies: list[dict] | None = None,
) -> list[ShotClip]:
    court = court or Court()
    fps = game.fps
    n_last = int(game.frames["frame"].max())
    n_first = int(game.frames["frame"].min())
    pre, post = int(pre_s * fps), int(post_s * fps)
    clips = []
    for i, s in enumerate(sorted(shots, key=lambda x: x.frame)):
        sf = max(n_first, s.frame - pre)
        ef = min(n_last, s.frame + post)
        clips.append(ShotClip(
            clip_id=f"shot_{i:04d}_f{s.frame}",
            shot=s,
            start_frame=sf, end_frame=ef,
            start_time=round(sf / fps, 3), end_time=round(ef / fps, 3),
            features=_features(game, s, court, rallies),
        ))
    return clips


def cut_video_clips(clips: list[ShotClip], video_path: str, out_dir: str) -> list[ShotClip]:
    """Corta os clips do video com ffmpeg (se disponivel). Atualiza clip.video_path."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg nao encontrado; instala-o ou salta o corte de video.")
    os.makedirs(out_dir, exist_ok=True)
    for c in clips:
        out = os.path.join(out_dir, f"{c.clip_id}.mp4")
        dur = max(0.1, c.end_time - c.start_time)
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(c.start_time), "-i", video_path,
             "-t", str(dur), "-c", "copy", out],
            check=True, capture_output=True,
        )
        c.video_path = out
    return clips
