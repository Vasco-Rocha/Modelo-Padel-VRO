"""Orquestra o auto-labeling: clips -> Gemini -> LabelStore."""
from __future__ import annotations
from typing import Optional

from ..core.schema import GameData, Shot
from ..core.court import Court
from .clips import extract_clips, cut_video_clips
from .gemini import GeminiLabeler
from .store import LabelStore, LabelRecord


def run_labeling(
    game: GameData,
    shots: list[Shot],
    labeler: GeminiLabeler,
    rallies: Optional[list[dict]] = None,
    court: Court | None = None,
    video_path: Optional[str] = None,
    clips_dir: Optional[str] = None,
    pre_s: float = 1.5,
    post_s: float = 1.0,
) -> LabelStore:
    clips = extract_clips(game, shots, pre_s=pre_s, post_s=post_s,
                          court=court or Court(), rallies=rallies)
    if video_path and clips_dir and not labeler.mock:
        cut_video_clips(clips, video_path, clips_dir)

    store = LabelStore()
    for c in clips:
        pred = labeler.label_clip(c)
        store.add(LabelRecord(
            clip_id=c.clip_id, frame=c.shot.frame, player_id=c.shot.player_id,
            stroke_pred=pred.get("stroke"), outcome_pred=pred.get("outcome"),
            confidence=pred.get("confidence"), reasoning=pred.get("reasoning"),
            features=c.features, status="pending",
        ))
    return store
