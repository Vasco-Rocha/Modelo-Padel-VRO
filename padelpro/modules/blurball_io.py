"""Integração do detetor temporal BlurBall com o pipeline de tempo útil.

O BlurBall (github.com/cogsys-tuebingen/blurball, MIT) substitui o detetor de bola YOLO.
Produz um `traj.csv` com a posição da bola por frame (960x540) + o rasto do borrão.

Porquê: o YOLO de-um-frame perdia a bola rápida/borrada (recall ~67%). O BlurBall, out-of-box
(sem treino), tem recall 85.6% dentro dos rallies. Ver docs/PLANO_TEMPO_UTIL_pos_BlurBall.md.
A Via A (fine-tune do YOLO) FALHOU e está fechada — não repetir.

Colunas do traj.csv: Frame, Visibility, X, Y, (L, Theta = comprimento/ângulo do rasto do borrão).
Coordenadas em 960x540 — a MESMA escala do Parada4 nativo e dos player_boxes. Não reescalar.
"""
from __future__ import annotations

import csv
import math


# ---------------------------------------------------------------------------
# Ponto de operação validado (jul 2026) — ver docs/PLANO_TEMPO_UTIL_pos_BlurBall.md
#
# Diretriz do produto: NUNCA perder um ponto. Recall > precisão; mais lixo é aceitável
# (um ponto que falta é informação perdida; lixo a mais é só um incómodo a saltar).
#
# vmin=6  : filtra a bola lenta/parada MAS mantém a bola do serviço (queda + ressalto).
#           vmin=12 dava melhor precisão (79%) mas PERDIA pontos -> rejeitado.
# gap=1.0 : corta nos gaps da bola em movimento.
# serve_zone_y=None : DESLIGA o merge-por-serviço do rallies_bola. Essa regra fundia tudo
#           (esperava um serviço que a heurística nunca detetava) -> mega-rallies.
#
# Resultado vs ground_truth_parada4 (117s / 12 rallies):
#   13 rallies | recall 99% | precisão 56% | tempo útil 205s
#   (baseline YOLO best.pt: 10 rallies | recall 67% | precisão 73% | 106s)
# ---------------------------------------------------------------------------
PONTO_OPERACAO = {
    "vmin": 6,                 # px/frame — velocidade mínima da bola para contar
    "gap_fora_s": 1.0,
    "serve_zone_y": None,      # ver nota acima
    "min_rally_s": 1.5,
    "margem_fim_s": 2.0,
    "min_gap_rallies_s": 2.5,
}


def carregar_traj_csv(path: str) -> list[tuple[float, float] | None]:
    """Lê o traj.csv do BlurBall → `ball_xy` (uma posição por frame, None se não detetada).

    É o formato que o `segmentar_rallies_bola` já espera — entra tal e qual,
    sem mexer nas regras.
    """
    ball_xy: list[tuple[float, float] | None] = []
    with open(path) as f:
        for row in csv.DictReader(f):
            visivel = int(float(row["Visibility"])) == 1
            ball_xy.append((float(row["X"]), float(row["Y"])) if visivel else None)
    return ball_xy


def filtrar_por_velocidade(ball_xy, vmin: float):
    """Mantém só as deteções em que a bola se MOVE (>= vmin px/frame).

    Porquê: entre pontos a bola continua visível (no chão, na mão, a ser devolvida). Com um
    detetor forte, "bola presente" deixa de ser sinal de jogo. A velocidade separa a bola
    em jogo da bola morta — e é o que faz o segmentador voltar a encontrar fronteiras.

    CUIDADO: um vmin alto (>=12) corta a bola LENTA do serviço (a queda da mão e o ressalto),
    cegando-nos ao arranque do ponto. Por isso o ponto de operação usa vmin=6.
    """
    out: list[tuple[float, float] | None] = [None] * len(ball_xy)
    for f in range(1, len(ball_xy)):
        p, q = ball_xy[f - 1], ball_xy[f]
        if p and q and math.hypot(q[0] - p[0], q[1] - p[1]) >= vmin:
            out[f] = q
    return out


def segmentar_com_blurball(traj_csv: str, player_boxes, fps: float, **overrides):
    """Atalho: traj.csv do BlurBall → rallies (regras v9), no ponto de operação validado.

    `overrides` permite variar qualquer parâmetro (ex.: `vmin=12`) para varrimentos.
    """
    from padelpro.modules.rallies_bola import segmentar_rallies_bola

    cfg = {**PONTO_OPERACAO, **overrides}
    vmin = cfg.pop("vmin")

    ball_xy = filtrar_por_velocidade(carregar_traj_csv(traj_csv), vmin)
    return segmentar_rallies_bola(ball_xy, player_boxes, fps, audio_hits_s=[], **cfg)


# ---------------------------------------------------------------------------
# Avaliação contra o ground-truth (conjunto de avaliação permanente do projeto)
# ---------------------------------------------------------------------------
GT_PARADA4 = [
    (38.0, 41.5), (46.8, 67.5), (77.6, 85.5), (95.9, 111.1), (122.4, 135.9),
    (157.9, 169.4), (178.1, 186.5), (197.0, 202.1), (210.5, 216.3),
    (229.9, 237.3), (249.6, 255.0), (263.8, 276.4),
]  # 12 rallies, 117s — anotado à mão (ver ground_truth_parada4.md)


def avaliar(res, gt=GT_PARADA4) -> dict:
    """Recall / precisão / segundos falsos dos rallies contra o ground-truth."""
    def _ov(a, b, c, d):
        return max(0.0, min(b, d) - max(a, c))

    segs = [(r["inicio_s"], r["fim_s"]) for r in res["rallies"]]
    gt_total = sum(b - a for a, b in gt)
    total = sum(e - s for s, e in segs)
    apanhado = sum(sum(_ov(a, b, s, e) for s, e in segs) for a, b in gt)
    falso = sum((e - s) - sum(_ov(s, e, a, b) for a, b in gt) for s, e in segs)

    return {
        "n_rallies": res["n_rallies"],
        "recall": apanhado / gt_total if gt_total else 0.0,
        "precisao": apanhado / total if total else 0.0,
        "falsos_s": round(falso, 1),
        "tempo_util_s": res["tempo_util_s"],
    }
