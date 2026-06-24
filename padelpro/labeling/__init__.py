"""Pipeline de auto-labeling: clips de pancadas -> Gemini -> confirmacao -> dataset de treino."""
from .clips import ShotClip, extract_clips, cut_video_clips
from .prompt import build_label_prompt, STROKE_LABELS, OUTCOME_LABELS, RESPONSE_SCHEMA
from .gemini import GeminiLabeler
from .store import LabelStore, LabelRecord
from .dataset import build_training_table

__all__ = [
    "ShotClip", "extract_clips", "cut_video_clips",
    "build_label_prompt", "STROKE_LABELS", "OUTCOME_LABELS", "RESPONSE_SCHEMA",
    "GeminiLabeler", "LabelStore", "LabelRecord", "build_training_table",
]
