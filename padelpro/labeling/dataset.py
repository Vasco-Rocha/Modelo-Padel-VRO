"""Converte labels confirmados num dataset de treino para o classificador de pancadas."""
from __future__ import annotations
import pandas as pd

from .store import LabelStore

FEATURE_COLS = ["incoming_ball_speed", "reach_distance", "dist_to_net", "is_last_in_rally"]


def build_training_table(store: LabelStore, target: str = "outcome") -> pd.DataFrame:
    """Tabela treino (features + label) a partir dos registos CONFIRMADOS.

    target: 'outcome' (forced/unforced/winner/in_play) ou 'stroke' (tipo de pancada).
    """
    assert target in ("outcome", "stroke")
    rows = []
    for r in store.confirmed():
        label = r.outcome_final if target == "outcome" else r.stroke_final
        if not label:
            continue
        feats = r.features or {}
        row = {"clip_id": r.clip_id, "label": label}
        for c in FEATURE_COLS:
            v = feats.get(c)
            row[c] = float(v) if isinstance(v, bool) else v
        rows.append(row)
    df = pd.DataFrame(rows)
    if "is_last_in_rally" in df:
        df["is_last_in_rally"] = df["is_last_in_rally"].astype("float")
    return df
