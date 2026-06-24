"""Geometria do campo de padel."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Court:
    """Campo de padel. Coordenadas em metros; origem num canto.

    Eixo x = largura (0..width), eixo y = comprimento (0..length).
    A rede divide o campo a meio do eixo y.
    """
    width: float = 10.0
    length: float = 20.0
    net_y: Optional[float] = None

    def __post_init__(self):
        if self.net_y is None:
            self.net_y = self.length / 2.0

    def dist_to_net(self, y: float) -> float:
        return abs(y - self.net_y)

    def side(self, y: float) -> str:
        """'near' (y < rede) ou 'far' (y >= rede)."""
        return "near" if y < self.net_y else "far"

    def zone(self, x: float, y: float, attack_threshold_m: float = 5.0) -> str:
        """Zona aproximada: rede / meio / fundo, por lado."""
        side = self.side(y)
        d = self.dist_to_net(y)
        half = self.net_y if side == "near" else (self.length - self.net_y)
        if d < attack_threshold_m:
            depth = "rede"
        elif d < half * 0.75:
            depth = "meio"
        else:
            depth = "fundo"
        return f"{side}_{depth}"
