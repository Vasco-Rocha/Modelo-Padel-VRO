"""Armazena labels (previstos pelo Gemini + confirmados pelo humano) em JSONL."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Optional
import json
import os
import pandas as pd


@dataclass
class LabelRecord:
    clip_id: str
    frame: int
    player_id: int
    # previstos pelo Gemini
    stroke_pred: Optional[str] = None
    outcome_pred: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    # confirmados pelo humano
    stroke_final: Optional[str] = None
    outcome_final: Optional[str] = None
    status: str = "pending"   # pending | confirmed | rejected
    features: dict = field(default_factory=dict)


class LabelStore:
    def __init__(self, records: Optional[list[LabelRecord]] = None):
        self.records: dict[str, LabelRecord] = {r.clip_id: r for r in (records or [])}

    def add(self, rec: LabelRecord) -> None:
        self.records[rec.clip_id] = rec

    def pending(self) -> list[LabelRecord]:
        return [r for r in self.records.values() if r.status == "pending"]

    def confirmed(self) -> list[LabelRecord]:
        return [r for r in self.records.values() if r.status == "confirmed"]

    def confirm(self, clip_id: str, stroke: Optional[str] = None,
                outcome: Optional[str] = None) -> None:
        r = self.records[clip_id]
        r.stroke_final = stroke if stroke is not None else r.stroke_pred
        r.outcome_final = outcome if outcome is not None else r.outcome_pred
        r.status = "confirmed"

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for r in self.records.values():
                f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, path: str) -> "LabelStore":
        recs = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    recs.append(LabelRecord(**json.loads(line)))
        return cls(recs)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(asdict(r) for r in self.records.values())
