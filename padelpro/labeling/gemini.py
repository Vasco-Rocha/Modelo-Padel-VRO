"""Cliente fino para o Gemini classificar clips de pancadas.

Funciona em dois modos:
- real: usa google-generativeai (precisa de pacote + API key + clip de video).
- mock: nao chama a rede; devolve um palpite deterministico a partir das features.
  Serve para desenvolver/testar o pipeline offline.
"""
from __future__ import annotations
from typing import Optional
import json

from .prompt import build_label_prompt, RESPONSE_SCHEMA, OUTCOME_LABELS


class GeminiLabeler:
    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        mock: bool = False,
        forced_speed_threshold: float = 18.0,
        forced_reach_threshold_m: float = 2.0,
    ):
        self.model_name = model
        self.api_key = api_key
        self.mock = mock or not api_key
        self._fs = forced_speed_threshold
        self._fr = forced_reach_threshold_m
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        import google.generativeai as genai  # import tardio: opcional
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name)

    def _mock_label(self, clip) -> dict:
        f = clip.features or {}
        stroke = clip.shot.stroke or "outro"
        outcome = "in_play"
        if f.get("is_last_in_rally"):
            fast = (f.get("incoming_ball_speed") or 0) >= self._fs
            far = (f.get("reach_distance") or 0) >= self._fr
            outcome = "forced_error" if (fast or far) else "unforced_error"
        return {"stroke": stroke, "outcome": outcome, "confidence": 0.5,
                "reasoning": "mock (heuristica de features; sem visao)"}

    def label_clip(self, clip) -> dict:
        """Devolve {stroke, outcome, confidence, reasoning} para um ShotClip."""
        if self.mock:
            return self._mock_label(clip)

        self._ensure_model()
        import google.generativeai as genai
        prompt = build_label_prompt(clip)
        if not clip.video_path:
            raise ValueError(f"{clip.clip_id}: clip.video_path em falta (corre cut_video_clips).")
        uploaded = genai.upload_file(clip.video_path)
        resp = self._model.generate_content(
            [prompt, uploaded],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": RESPONSE_SCHEMA,
            },
        )
        data = json.loads(resp.text)
        if data.get("outcome") not in OUTCOME_LABELS:
            data["outcome"] = "in_play"
        return data
