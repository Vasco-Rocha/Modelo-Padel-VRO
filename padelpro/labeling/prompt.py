"""Prompt e schema de resposta para o Gemini classificar cada pancada.

Aprendizagem da v9: o Gemini ignora constraints soltas e alucina estrutura.
Por isso aqui: enums fechados, JSON estrito, definicoes curtas e features de
contexto injetadas no prompt para ancorar a resposta.
"""
from __future__ import annotations

STROKE_LABELS = ["drive", "backhand", "volei_direita", "volei_esquerda",
                 "bandeja", "vibora", "remate", "globo", "saque", "outro"]

OUTCOME_LABELS = ["in_play", "winner", "forced_error", "unforced_error"]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "stroke": {"type": "string", "enum": STROKE_LABELS},
        "outcome": {"type": "string", "enum": OUTCOME_LABELS},
        "confidence": {"type": "number"},
        "reasoning": {"type": "string"},
    },
    "required": ["stroke", "outcome", "confidence"],
}

_DEFS = """\
Definicoes (padel):
- winner: pancada ganhadora; o adversario nao chega a tocar a bola.
- forced_error: erro provocado por pressao (bola rapida, dificil, ou jogador deslocado/longe).
- unforced_error: erro numa bola controlavel, sem pressao significativa.
- in_play: pancada normal que mantem o ponto em jogo.
"""


def build_label_prompt(clip) -> str:
    """Monta o prompt para um clip. `clip` e' um ShotClip."""
    f = clip.features or {}
    ctx_lines = []
    if f.get("incoming_ball_speed") is not None:
        ctx_lines.append(f"- velocidade da bola recebida: {f['incoming_ball_speed']:.1f} m/s")
    if f.get("reach_distance") is not None:
        ctx_lines.append(f"- distancia do jogador a' bola no impacto: {f['reach_distance']:.1f} m")
    if f.get("player_zone"):
        ctx_lines.append(f"- zona do jogador: {f['player_zone']}")
    if f.get("is_last_in_rally") is not None:
        ctx_lines.append(f"- e' a ultima pancada do rally: {f['is_last_in_rally']}")
    ctx = "\n".join(ctx_lines) or "- (sem features de contexto)"

    return f"""Es um analista de padel. Vais ver um clip curto centrado numa pancada do jogador {clip.shot.player_id}.
Classifica o TIPO de pancada e o RESULTADO dessa pancada.

{_DEFS}
Contexto medido pelo sistema (usa como apoio, nao como verdade absoluta):
{ctx}

Regras de resposta (OBRIGATORIO):
1. Responde APENAS com JSON valido, sem texto antes ou depois.
2. "stroke" tem de ser um de: {STROKE_LABELS}.
3. "outcome" tem de ser um de: {OUTCOME_LABELS}.
4. "confidence" entre 0 e 1.
5. Se nao tiveres certeza do resultado, usa "in_play".

Formato:
{{"stroke": "...", "outcome": "...", "confidence": 0.0, "reasoning": "..."}}"""
