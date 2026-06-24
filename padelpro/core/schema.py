"""Estruturas de dados partilhadas pelos modulos."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import pandas as pd


@dataclass
class GameData:
    """Tabela unica por frame — a 'camada partilhada'.

    O DataFrame `frames` tem (no minimo) as colunas:
        frame, time,
        p1_x, p1_y, ..., p4_x, p4_y,
        p1_speed, ..., p4_speed
    E, se disponiveis:
        ball_x, ball_y, ball_speed, ball_hit
    """
    frames: pd.DataFrame
    fps: float
    has_ball: bool = False

    @property
    def n_frames(self) -> int:
        return len(self.frames)

    @property
    def duration_s(self) -> float:
        if "time" in self.frames:
            return float(self.frames["time"].iloc[-1])
        return self.n_frames / self.fps

    def player_speed_columns(self) -> list[str]:
        return [c for c in self.frames.columns if c.endswith("_speed") and c.startswith("p")]


@dataclass
class Rally:
    index: int
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        return round(self.end_time - self.start_time, 3)


@dataclass
class PhaseSegment:
    phase: str
    start_frame: int
    end_frame: int
    start_time: float
    end_time: float

    @property
    def duration(self) -> float:
        return round(self.end_time - self.start_time, 3)


@dataclass
class Shot:
    frame: int
    time: float
    player_id: int
    stroke: str
    outcome: Optional[str] = None        # "in_play" | "winner" | "forced_error" | "unforced_error"
    rally_index: Optional[int] = None
    incoming_ball_speed: Optional[float] = None
    reach_distance: Optional[float] = None


@dataclass
class MatchAnalysis:
    fps: float
    duration_s: float
    active_time: dict = field(default_factory=dict)
    phases: dict = field(default_factory=dict)
    shots: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
