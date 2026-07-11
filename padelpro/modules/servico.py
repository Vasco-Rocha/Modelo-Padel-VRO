"""Limpeza da trajetória da bola + deteção de SERVIÇO (regras do Vasco, jul 2026).

Contexto: o BlurBall deteta a bola muito melhor que o YOLO, mas a segmentação continuava a
abrir os rallies 10-20s antes do ponto (o rally começava quando a bola mexia, não no serviço).
~80s dos ~95s de lixo eram BORDAS. Nenhum filtro de bola resolve isso — só saber onde está o
serviço. Ver docs/SPEC_M1_TEMPO_UTIL.md.

Duas camadas:
  LIMPEZA   — objetos imóveis + continuidade física (a bola não se teletransporta)
  SERVIÇO   — zona (onde) + sequência (quando) + formação (quem está onde)
"""
from __future__ import annotations

import math
from collections import defaultdict

import numpy as np


# ===========================================================================
# LIMPEZA DA TRAJETÓRIA
# ===========================================================================

def filtrar_objetos_imoveis(ball_xy, tol=6, min_hits=15, min_spread=0.35):
    """Remove deteções em objetos IMÓVEIS (regra do Vasco).

    Um objeto que aparece no MESMO píxel, espalhado por >35% do vídeo, não é a bola —
    a bola nunca pousa duas vezes no mesmo píxel, muito menos ao longo do jogo inteiro.
    No Parada4 apanha 4 objetos (postes/estruturas no topo). Sobe a precisão SEM custar recall.
    """
    n = len(ball_xy)
    pos = defaultdict(list)
    for f, p in enumerate(ball_xy):
        if p:
            pos[(round(p[0] / tol), round(p[1] / tol))].append(f)
    imoveis = {
        k for k, fs in pos.items()
        if len(fs) >= min_hits and (max(fs) - min(fs)) / n >= min_spread
    }
    return [
        None if (p is None or (round(p[0] / tol), round(p[1] / tol)) in imoveis) else p
        for p in ball_xy
    ], imoveis


def filtrar_continuidade(ball_xy, vmax=80.0, max_rejeicoes=6):
    """A bola NÃO se teletransporta (regra do Vasco).

    Entre frames a bola move-se no máximo `vmax` px. (80 px/frame ≈ bola a 100 km/h a 540p.)
    Uma deteção que salta 400px num frame é outro objeto — descarta-se. Não precisamos de
    saber QUEM são os falsos positivos; basta exigir que a trajetória seja fisicamente coerente.
    Se rejeitarmos muitas seguidas, é a âncora que estava errada → recomeça a track.
    """
    out = [None] * len(ball_xy)
    anc_f = anc_p = None
    rej = 0
    for f, p in enumerate(ball_xy):
        if p is None:
            continue
        if anc_p is None:
            out[f] = p; anc_f, anc_p, rej = f, p, 0; continue
        if math.hypot(p[0] - anc_p[0], p[1] - anc_p[1]) <= vmax * (f - anc_f):
            out[f] = p; anc_f, anc_p, rej = f, p, 0
        else:
            rej += 1
            if rej > max_rejeicoes:
                out[f] = p; anc_f, anc_p, rej = f, p, 0
    return out


def limpar(ball_xy, vmax=80.0):
    """Aplica as duas limpezas pela ordem certa (imóveis primeiro, senão contaminam tudo)."""
    b, _ = filtrar_objetos_imoveis(ball_xy)
    return filtrar_continuidade(b, vmax)


# ===========================================================================
# GEOMETRIA DO CAMPO (calibracao_campo.json — detetada das linhas brancas)
# ===========================================================================

class Campo:
    def __init__(self, cal: dict):
        self.perto = np.array(cal["servico_perto_coef"])   # linha de serviço PERTO (curva)
        self.longe = np.array(cal["servico_longe_coef"])   # linha de serviço LONGE (curva)
        self.rede = np.array(cal["rede_tape_coef"])        # tape da rede
        self.centro_x = cal["centro_x"]

    def y_servico_perto(self, x): return float(np.polyval(self.perto, x))
    def y_servico_longe(self, x): return float(np.polyval(self.longe, x))
    def y_rede(self, x): return float(np.polyval(self.rede, x))

    def lado(self, box):
        """'baixo' (perto da câmara) ou 'cima' (longe), pela base da box."""
        return "baixo" if box[3] > self.y_rede((box[0] + box[2]) / 2) + 30 else "cima"

    def atras_da_linha(self, box) -> bool:
        """Pés do jogador para lá da linha de serviço → posição de SERVIDOR."""
        xc, y2 = (box[0] + box[2]) / 2, box[3]
        return y2 > self.y_servico_perto(xc) or y2 < self.y_servico_longe(xc)

    def na_rede(self, box, tol=45) -> bool:
        """Pés perto da rede → posição de PARCEIRO do servidor."""
        xc, y2 = (box[0] + box[2]) / 2, box[3]
        return abs(y2 - self.y_rede(xc)) <= tol

    def metade(self, box) -> str:
        """'esq' ou 'dir' — para a regra do lado do serviço (ace vs falta)."""
        return "esq" if (box[0] + box[2]) / 2 < self.centro_x else "dir"


def _dist_box(p, b):
    x, y = p
    x1, y1, x2, y2 = b
    return math.hypot(max(x1 - x, 0, x - x2), max(y1 - y, 0, y - y2))


# ===========================================================================
# FORMAÇÃO DE SERVIÇO (regra do Vasco)
# ===========================================================================

def formacao_servico(boxes, servidor, campo: Campo) -> bool:
    """No serviço: o PARCEIRO do servidor está na REDE, e o ADVERSÁRIO CRUZADO está
    atrás da linha de serviço dele. Isto não acontece por acaso a meio de um ponto."""
    lado_s = campo.lado(servidor)
    meia_s = campo.metade(servidor)
    parceiro_na_rede = any(
        b is not servidor and campo.lado(b) == lado_s and campo.na_rede(b) for b in boxes
    )
    adversario_cruzado_atras = any(
        campo.lado(b) != lado_s and campo.metade(b) != meia_s and campo.atras_da_linha(b)
        for b in boxes
    )
    return parceiro_na_rede and adversario_cruzado_atras


# ===========================================================================
# DETEÇÃO DE SERVIÇO — zona (onde) + sequência (quando) + formação (quem)
# ===========================================================================

def detetar_servicos(ball_xy, player_boxes, fps, campo: Campo,
                     d_mao=70, h_chao=30, pico_vel=18.0, janela_s=1.2,
                     exigir_formacao=True, min_gap_s=5.0):
    """Serviço = a bola está no CHÃO junto a um jogador ATRÁS da linha (candidato),
    e a seguir há uma RAQUETADA (pico de velocidade) com a bola a AFASTAR-SE (validação).
    Opcionalmente exige a FORMAÇÃO (parceiro na rede + adversário cruzado atrás).

    Devolve os frames da raquetada (= início real do ponto).
    """
    n = len(ball_xy)
    W = int(janela_s * fps)
    servicos = []

    for f, p in enumerate(ball_xy):
        if p is None or not player_boxes[f]:
            continue
        b = min(player_boxes[f], key=lambda b: _dist_box(p, b))
        if _dist_box(p, b) > d_mao:
            continue
        if not campo.atras_da_linha(b):
            continue
        if abs(p[1] - b[3]) > h_chao:          # bola à altura dos PÉS = no chão
            continue
        if exigir_formacao and not formacao_servico(player_boxes[f], b, campo):
            continue

        # VALIDAÇÃO: nos frames seguintes, pico de velocidade + a bola AFASTA-SE do servidor
        for g in range(f + 1, min(f + W, n)):
            if ball_xy[g] is None or ball_xy[g - 1] is None:
                continue
            v = math.hypot(ball_xy[g][0] - ball_xy[g - 1][0], ball_xy[g][1] - ball_xy[g - 1][1])
            if v >= pico_vel and _dist_box(ball_xy[g], b) > d_mao:
                if not servicos or (g - servicos[-1]) > int(min_gap_s * fps):
                    servicos.append(g)          # a raquetada = o ponto começa aqui
                break
    return servicos
