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
    """Geometria do campo, DESENHADA A MAO no `calibrar_campo.html`.

    Nao e auto-detetada: a auto-detecao das linhas brancas falhou (marcou a linha
    de servico LONGE ~40 px abaixo da real, no meio do azul) porque o meio-campo
    longe ocupa ~65 px contra ~400 do perto -- a perspetiva esmaga-o e nao ha
    resolucao para o detetor. Ver HANDOFF / memoria `project_calibracao`.

    Novo campo = nova calibracao no `calibrar_campo.html`.
    """

    def __init__(self, cal: dict):
        g = lambda k: np.array(cal[k])
        self.perto = g("servico_perto_coef")     # linha de servico PERTO
        self.longe = g("servico_longe_coef")     # linha de servico LONGE
        self.rede = g("rede_tape_coef")          # TOPO da rede (a fita)
        self.fundo = np.array(cal["fundo_longe_coef"]) if "fundo_longe_coef" in cal else None

        # BASE da rede: e onde estao os PES de quem sobe a' rede. A fita fica ~35 px
        # acima -- comparar pes com a fita era um erro sistematico silencioso.
        self.rede_base = np.array(cal.get("rede_base_coef", cal["rede_tape_coef"]))

        # Juncao malha 2/3 = fronteira ATAQUE / TRANSICAO (M2). Nao e linha branca:
        # e a juncao de dois paineis de vidro. Tem sempre de ser desenhada.
        self.juncao_perto = np.array(cal["juncao_perto_coef"]) if "juncao_perto_coef" in cal else None
        self.juncao_longe = np.array(cal["juncao_longe_coef"]) if "juncao_longe_coef" in cal else None

        # Linha central: x = f(y). NAO e vertical -- em perspetiva o meio da imagem
        # nao e o meio do campo ao fundo. O antigo `centro_x` constante mentia,
        # e e' a central que decide o QUADRADO DE SERVICO CRUZADO.
        self.centro_coef = np.array(cal["centro_coef_em_y"]) if "centro_coef_em_y" in cal else None
        self.centro_x = cal.get("centro_x", 480)

        # LATERAIS (vidro): saem dos EXTREMOS das linhas horizontais desenhadas -- o ponto
        # onde cada linha encontra o vidro E' o canto. Regra do Vasco: os pes de um jogador
        # NUNCA passam para la' do vidro. Tudo o que tiver os pes fora do campo NAO e' jogador.
        self.lat_esq, self.lat_dir = self._laterais(cal)

    @staticmethod
    def _laterais(cal):
        P = cal.get("pontos", {})
        esq, dir_ = [], []
        for k in ("fundo_longe", "servico_longe", "rede_base", "servico_perto"):
            p = P.get(k)
            if not p or len(p) < 3:
                continue
            p = sorted(p, key=lambda q: q[0])
            esq.append((p[0][1], p[0][0]))       # (y, x) do extremo esquerdo
            dir_.append((p[-1][1], p[-1][0]))    # (y, x) do extremo direito
        if len(esq) < 3:
            return None, None
        E, D = np.array(esq), np.array(dir_)
        return np.polyfit(E[:, 0], E[:, 1], 2), np.polyfit(D[:, 0], D[:, 1], 2)

    def dentro_do_campo(self, box, margem=35, margem_fundo=4) -> bool:
        """Os PES estao dentro do campo? (regra do Vasco)

        Os pes de um jogador NUNCA passam para la' do vidro. No maximo vao aos
        espacos laterais -> `margem` lateral generosa (35 px).

        MAS no fundo LONGE a margem tem de ser ~0: la' a perspetiva esmaga tudo e
        35 px valem ~2,5 m -- deixariam passar meia bancada. Tudo o que tenha os pes
        ACIMA da linha do vidro de fundo esta' atras do vidro: e' publico.

        No Parada4 a detecao MAIS FREQUENTE do video inteiro era um espectador
        (pes em x~50, em 32% dos frames).
        """
        if self.lat_esq is None:
            return True
        xc, y2 = self._pes(box)
        if y2 < self.y_fundo_longe(xc) - margem_fundo:   # atras do vidro do fundo
            return False
        if xc < float(np.polyval(self.lat_esq, y2)) - margem:
            return False
        if xc > float(np.polyval(self.lat_dir, y2)) + margem:
            return False
        return True

    def y_fundo_longe(self, x):
        c = getattr(self, "fundo", None)
        return float(np.polyval(c, x)) if c is not None else 0.0

    def jogadores(self, boxes, margem=35):
        """Filtra as boxes: so' quem tem os PES dentro do campo e' jogador."""
        return [b for b in boxes if self.dentro_do_campo(b, margem)]

    def y_servico_perto(self, x): return float(np.polyval(self.perto, x))
    def y_servico_longe(self, x): return float(np.polyval(self.longe, x))
    def y_rede(self, x): return float(np.polyval(self.rede, x))
    def y_rede_base(self, x): return float(np.polyval(self.rede_base, x))

    def x_centro(self, y) -> float:
        """x da linha central a' altura y. Cai no `centro_x` antigo se nao houver curva."""
        if self.centro_coef is None:
            return float(self.centro_x)
        return float(np.polyval(self.centro_coef, y))

    def _pes(self, box):
        return (box[0] + box[2]) / 2.0, box[3]

    def lado(self, box):
        """'baixo' (perto da camara) ou 'cima' (longe), pela base da box."""
        xc, y2 = self._pes(box)
        return "baixo" if y2 > self.y_rede_base(xc) else "cima"

    def atras_da_linha(self, box) -> bool:
        """Pes do jogador para la' da linha de servico -> posicao de SERVIDOR."""
        xc, y2 = self._pes(box)
        return y2 > self.y_servico_perto(xc) or y2 < self.y_servico_longe(xc)

    def meio_campo_px(self, x, lado: str) -> float:
        """Altura em pixeis do meio-campo (rede -> linha de servico) daquele lado.

        E a REGUA local. A perspetiva esmaga o lado longe: no Parada4 o meio-campo
        perto tem ~290 px e o longe ~100 px -- os MESMOS 6.95 m. Uma tolerancia fixa
        em pixeis (o antigo `tol=45`) vale 1.1 m de um lado e 3.1 m do outro.
        Todas as tolerancias tem de ser FRACOES disto, nunca pixeis absolutos.
        """
        if lado == "baixo":
            return abs(self.y_servico_perto(x) - self.y_rede_base(x))
        return abs(self.y_rede_base(x) - self.y_servico_longe(x))

    def na_rede(self, box, frac=0.22) -> bool:
        """Pes perto da BASE da rede -> posicao de PARCEIRO do servidor.

        `frac` e' uma fracao do meio-campo daquele lado (0.22 * 6.95 m ~ 1.5 m),
        nao pixeis -- ver `meio_campo_px`.
        """
        xc, y2 = self._pes(box)
        tol = frac * self.meio_campo_px(xc, self.lado(box))
        return abs(y2 - self.y_rede_base(xc)) <= tol

    def metade(self, box) -> str:
        """'esq' ou 'dir' -- para o quadrado cruzado e o lado do servico (ace vs falta).
        Usa a central CURVA, a' altura dos pes do jogador."""
        xc, y2 = self._pes(box)
        return "esq" if xc < self.x_centro(y2) else "dir"

    def metade_ponto(self, p) -> str:
        """'esq' ou 'dir' de um ponto (x, y) -- ex.: onde a bola do servico ressaltou."""
        return "esq" if p[0] < self.x_centro(p[1]) else "dir"

    # ---------------- M2: fases taticas (geometria pura, sem IA) ----------------

    def zona(self, box) -> str:
        """DEFESA / TRANSICAO / ATAQUE de UM jogador, pelos PES.

        DEFESA    = atras da linha de servico do seu lado.
        ATAQUE    = a' frente da juncao malha 2/3 (mais perto da rede).
        TRANSICAO = o resto (estado-residuo).
        """
        if self.juncao_perto is None or self.juncao_longe is None:
            raise ValueError("Faltam as juncoes malha 2/3 na calibracao (M2).")
        xc, y2 = self._pes(box)
        if y2 >= 538:            # pes cortados pela borda -> esta' no fundo PERTO
            return "DEFESA"
        if self.lado(box) == "baixo":
            if y2 > self.y_servico_perto(xc):
                return "DEFESA"
            if y2 < float(np.polyval(self.juncao_perto, xc)):
                return "ATAQUE"
        else:
            if y2 < self.y_servico_longe(xc):
                return "DEFESA"
            if y2 > float(np.polyval(self.juncao_longe, xc)):
                return "ATAQUE"
        return "TRANSICAO"

    @staticmethod
    def fase_equipa(z1: str, z2: str) -> str:
        """Fase da DUPLA (regra das duas boxes): so' e' DEFESA/ATAQUE se AMBOS estiverem la'."""
        if z1 == z2 and z1 in ("DEFESA", "ATAQUE"):
            return z1
        return "TRANSICAO"



def filtrar_espectadores(player_boxes, campo: Campo, margem=35, tol=25, max_frac=0.25):
    """Limpa as deteccoes de jogadores. Duas regras do Vasco, em cascata:

    1. FORA DO CAMPO -- os pes de um jogador NUNCA passam para la' do vidro.
       No maximo vao aos espacos laterais -> margem generosa.
    2. IMOVEL -- uma detecao que aparece na MESMA zona (tol px) em mais de
       `max_frac` do video nao e' um jogador: os jogadores MOVEM-SE.
       E' a mesma regra que ja limpava a bola (`filtrar_objetos_imoveis`).

    No Parada4 a detecao MAIS FREQUENTE do video inteiro era um espectador
    sentado fora do campo (pes em x~50, em 32% dos frames). Isto mata-o.

    Devolve (boxes_limpas, relatorio).
    """
    n = len(player_boxes)
    pes = lambda b: ((b[0] + b[2]) / 2.0, b[3])

    fora = 0
    passo1 = []
    for f in player_boxes:
        keep = []
        for b in f:
            if campo.dentro_do_campo(b, margem):
                keep.append(b)
            else:
                fora += 1
        passo1.append(keep)

    cont = {}
    for f in passo1:
        vistos = set()
        for b in f:
            x, y = pes(b)
            cel = (int(x // tol), int(y // tol))
            if cel not in vistos:
                cont[cel] = cont.get(cel, 0) + 1
                vistos.add(cel)
    mortos = {c for c, k in cont.items() if k > max_frac * n}

    imoveis = 0
    saida = []
    for f in passo1:
        keep = []
        for b in f:
            x, y = pes(b)
            if (int(x // tol), int(y // tol)) in mortos:
                imoveis += 1
            else:
                keep.append(b)
        saida.append(keep)

    return saida, {
        "antes": sum(len(f) for f in player_boxes),
        "descartadas_fora_do_campo": fora,
        "descartadas_imoveis": imoveis,
        "celulas_imoveis": sorted(mortos),
        "depois": sum(len(f) for f in saida),
    }



def dois_por_lado(player_boxes, campo: Campo, confs=None, H=540):
    """Regra do Vasco: sao SEMPRE 2 contra 2. No maximo 2 jogadores de cada lado da rede.

    Se aparecerem 3 deteccoes de um lado, uma e' lixo -- fica com as 2 melhores.
    Criterio (por ordem):
      1. maior CONFIANCA, se vier no JSON;
      2. senao, a box MAIOR (o publico ao fundo e' pequeno; um jogador nao).

    PORQUE ISTO IMPORTA MAIS DO QUE PARECE
    --------------------------------------
    E' uma verdade do JOGO, nao um threshold afinado a' mao. E como limpa o excesso,
    deixa-nos baixar o `CONF` do detetor a' vontade (0.5 -> 0.15) para recuperar:
      - os jogadores CORTADOS pela borda de baixo (meia pessoa = confianca baixa)
      - os do FUNDO longe (poucos pixeis)
    RECALL pela detecao, PRECISAO pela estrutura. As duas coisas deixam de competir.

    Nota: quem tem os PES cortados pela borda de baixo esta', por construcao, no lado
    de BAIXO -- nao ha ambiguidade.
    """
    saida = []
    for f, boxes in enumerate(player_boxes):
        cf = (confs[f] if confs else [None] * len(boxes))
        cima, baixo = [], []
        for b, c in zip(boxes, cf):
            xc, y2 = (b[0] + b[2]) / 2.0, b[3]
            pes_cortados = y2 >= H - 2
            lado = "baixo" if (pes_cortados or y2 > campo.y_rede_base(xc)) else "cima"
            area = (b[2] - b[0]) * (b[3] - b[1])
            (baixo if lado == "baixo" else cima).append((b, c if c is not None else area))
        keep = []
        for grupo in (cima, baixo):
            grupo.sort(key=lambda t: -t[1])
            keep += [b for b, _ in grupo[:2]]
        saida.append(keep)
    return saida


def pes_fora_do_frame(box, H=540) -> bool:
    """Os pes sairam pela borda de baixo. NAO e' motivo para descartar a detecao --
    e' informacao: o jogador esta' no fundo PERTO. Ver `Campo.zona`."""
    return box[3] >= H - 2



def continuidade_jogadores(frames_id, campo: Campo, fps=30.0, v_max_ms=9.0,
                           max_buraco_frames=15):
    """Regra do Vasco: um jogador NAO se teletransporta -- e nao desaparece a meio do ponto.

    A mesma regra que ja limpava a bola (`filtrar_continuidade`), agora nas pessoas.
    Usa os IDs do ByteTrack, portanto nao tem de adivinhar quem e' quem.

    Faz DUAS coisas (a segunda e' a que interessa):
      1. REJEITA saltos impossiveis -- se o #3 salta 300 px num frame, aquilo nao e' o #3.
      2. PREENCHE buracos -- se vi o #3 no frame 100 e no 104, ele ESTEVE algures no meio.
         Interpola. Um jogador nao desaparece a meio de um ponto.
         E' a unica regra que ACRESCENTA informacao em vez de a deitar fora.

    A velocidade maxima NAO pode ser em pixeis fixos: 9 m/s valem ~12 px/frame no fundo
    perto e ~4 px/frame no fundo longe (o meio-campo longe tem 100 px contra 290 do perto,
    para os mesmos 6.95 m). Converte-se localmente. Terceira vez hoje que a perspetiva
    obriga a isto -- nada em pixeis absolutos sobrevive.

    Args:
        frames_id: lista (por frame) de {id: (x1,y1,x2,y2)}  (de `carregar_players_com_id`)
    Returns:
        (frames_id_corrigido, relatorio)
    """
    n = len(frames_id)
    out = [dict(d) for d in frames_id]

    def px_por_m(box):
        xc, y2 = (box[0] + box[2]) / 2.0, box[3]
        lado = "baixo" if y2 > campo.y_rede_base(xc) else "cima"
        return max(campo.meio_campo_px(xc, lado) / 6.95, 1.0)

    def pes(b):
        return ((b[0] + b[2]) / 2.0, b[3])

    ids = set()
    for d in frames_id:
        ids |= set(d)

    saltos = preenchidos = 0
    for pid in ids:
        vistos = [f for f in range(n) if pid in out[f]]
        if len(vistos) < 2:
            continue

        # 1. saltos impossiveis
        for a, b in zip(vistos, vistos[1:]):
            pa, pb = pes(out[a][pid]), pes(out[b][pid])
            dt = (b - a) / fps
            limite = v_max_ms * px_por_m(out[a][pid]) * dt * 1.5   # 50% de folga
            if math.hypot(pb[0] - pa[0], pb[1] - pa[1]) > limite:
                del out[b][pid]
                saltos += 1

        # 2. preencher buracos curtos
        vistos = [f for f in range(n) if pid in out[f]]
        for a, b in zip(vistos, vistos[1:]):
            gap = b - a - 1
            if not (0 < gap <= max_buraco_frames):
                continue
            ba, bb = out[a][pid], out[b][pid]
            for k in range(1, gap + 1):
                t = k / (gap + 1)
                out[a + k][pid] = tuple(
                    ba[i] + t * (bb[i] - ba[i]) for i in range(4)
                )
                preenchidos += 1

    return out, {
        "ids": len(ids),
        "saltos_rejeitados": saltos,
        "frames_preenchidos": preenchidos,
    }


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
