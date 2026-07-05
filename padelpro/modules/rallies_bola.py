"""Segmentacao de rallies pelo ESTADO DA BOLA (regras v9 traduzidas para codigo).

Faz o *timing* do tempo util a partir das detecoes que ja produzimos (bola + jogadores
por frame), em vez de pedir timestamps ao Gemini. O v9/Gemini fica so' para o semantico.

Regras implementadas (ver REGRAS_BOLA_PARA_CODIGO.md):
  R1  inicio = SERVICO: bola colada a' box de um jogador e depois AFASTA-SE.
  R-pancada: bola aproxima-se de uma box e depois afasta-se / pico de velocidade.
  R2  fim: bola desaparece do jogo por > gap_fora_s.
  R3  fim: bola perto de um jogador e PARADA por >= K frames (bola na mao).
  R5  confirmacao: apos um fim candidato, esperar janela_fim_s; se houver nova PANCADA
      que nao seja servico, o rally continua.
  R7  descartar rallies < min_rally_s.
  R8  margem visual (+margem_video_s) — SO' para cortar o video, nao conta no tempo util.

Encaixe para regras EXTRA do Vasco (validade de servico, etc.): ver servico_valido().

Entradas:
  ball_xy       : list[tuple[float,float] | None]  — centro da bola por frame (None = nao detetada)
  player_boxes  : list[list[tuple[float,float,float,float]]]  — boxes (x1,y1,x2,y2) por frame
  fps           : float

Saida: dict com 'rallies' (frames inicio/fim + tempos), 'eventos' (servicos, pancadas),
       'tempo_util_s' e 'clips_video' (com margem R8).
"""
from __future__ import annotations
import math


def _dist_ponto_box(p, box) -> float:
    """Distancia de um ponto (x,y) a' box (x1,y1,x2,y2); 0 se dentro."""
    x, y = p
    x1, y1, x2, y2 = box
    dx = max(x1 - x, 0.0, x - x2)
    dy = max(y1 - y, 0.0, y - y2)
    return math.hypot(dx, dy)


def _bola_perto(p, boxes, limiar) -> int | None:
    """Indice do jogador cuja box esta' a < limiar da bola (o mais proximo), ou None."""
    if p is None or not boxes:
        return None
    dists = [(_dist_ponto_box(p, b), i) for i, b in enumerate(boxes)]
    d, i = min(dists)
    return i if d < limiar else None


def _vel(ball_xy, f) -> float | None:
    """Velocidade da bola em f (px/frame): |xy[f]-xy[f-1]|. None se faltar deteccao."""
    if f <= 0 or ball_xy[f] is None or ball_xy[f - 1] is None:
        return None
    (x0, y0), (x1, y1) = ball_xy[f - 1], ball_xy[f]
    return math.hypot(x1 - x0, y1 - y0)


def detetar_pancadas(ball_xy, player_boxes, fps, limiar_px=80.0, pico_vel=25.0):
    """R-pancada: bola aproxima-se de uma box e depois afasta-se / pico de velocidade.
    Devolve lista de frames onde ha' pancada."""
    n = len(ball_xy)
    pancadas = []
    for f in range(1, n - 1):
        pj = _bola_perto(ball_xy[f], player_boxes[f] if f < len(player_boxes) else [], limiar_px)
        if pj is None:
            continue
        v = _vel(ball_xy, f + 1)
        # aproximou-se (perto de um jogador) e a seguir acelera/afasta-se
        if v is not None and v >= pico_vel:
            if not pancadas or f - pancadas[-1] > int(0.3 * fps):  # anti-duplicado
                pancadas.append(f)
    return pancadas


def _centro(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def jogadores_parados(player_boxes, f, fps, n_jogadores=4, seg=3.0, desloc_px=15.0) -> bool:
    """R5 do prompt: TODOS os jogadores visiveis e ~parados durante `seg` segundos.
    So' devolve True se virmos os n_jogadores (nao adivinhar quando faltam boxes)."""
    w = int(seg * fps)
    if f - w < 0:
        return False
    janela = player_boxes[f - w: f + 1]
    if any(len(bs) < n_jogadores for bs in janela):
        return False   # nao ha' todos os jogadores visiveis => nao confirmar
    # deslocamento maximo do centro de cada jogador na janela
    for i in range(n_jogadores):
        centros = [_centro(bs[i]) for bs in janela]
        xs = [c[0] for c in centros]; ys = [c[1] for c in centros]
        if (max(xs) - min(xs)) > desloc_px or (max(ys) - min(ys)) > desloc_px:
            return False
    return True


def servico_valido(inicio_frame, ball_xy, player_boxes, fps) -> bool:
    """Validade do servico — regras recuperadas dos prompts v2/v3 (estavam perdidas na v9).

    SINAL-CHAVE codificavel: o servico BATE NO CHAO antes de ser batido
    (a bola cai da mao, RESSALTA no chao, e so' depois leva a raquetada). Isto distingue
    um servico de qualquer outra bola que sai da mao. Detetar: entre a bola sair da mao e o
    pico de velocidade (raquetada), a bola deve tocar a zona do solo uma vez.

    Regras completas (algumas precisam de homografia/zona; deixadas como TODO):
      POSICAO (v2/v3): servidor atras da linha de servico (FUNDO); parceiro na rede (REDE);
        adversarios na linha de servico ou atras.
      VALIDADE:
        - valido = bola cai no quadrado de servico CRUZADO, sem tocar na malha/rede.
        - let    = bola toca na tela da rede mas cai dentro do quadrado -> servico REPETE.
        - falta  = bola toca na malha e nao entra; OU o recetor nao jogou; OU muda o servidor.

    Por agora: se conseguirmos confirmar o ressalto-no-chao do servico, devolve True;
    caso contrario devolve True na mesma (nao filtrar) ate ligarmos a homografia.
    """
    # TODO: (1) confirmar ressalto no solo entre saida-da-mao e raquetada (precisa zona do solo);
    #       (2) validar quadrado cruzado + toque na rede (precisa homografia dos keypoints).
    return True


def segmentar_rallies_bola(
    ball_xy,
    player_boxes,
    fps,
    limiar_mao_px=60.0,      # bola "colada" a' box do jogador
    frames_mao=None,          # K frames para confirmar bola na mao (default ~0.4s)
    gap_fora_s=2.0,           # R2: bola sumida > isto = candidato a fim
    janela_fim_s=5.0,         # R5: esperar isto por nova pancada (Vasco: 5s)
    min_rally_s=1.0,          # R7
    margem_video_s=2.0,       # R8: so' para o clip de video
    audio_hits_s=None,        # R15: lista de timestamps (s) de pancada por AUDIO — REFERENCIA
    audio_tol_s=0.5,          # tolerancia do audio (pode estar atrasado)
):
    n = len(ball_xy)
    if frames_mao is None:
        frames_mao = max(1, int(0.4 * fps))
    gap = int(gap_fora_s * fps)
    jfim = int(janela_fim_s * fps)

    pancadas = detetar_pancadas(ball_xy, player_boxes, fps)
    pancadas_set = set(pancadas)
    # R15: pancadas por audio como REFERENCIA (nunca decidem sozinhas)
    audio_frames = set(int(round(t * fps)) for t in (audio_hits_s or []))
    audio_tol = int(audio_tol_s * fps)

    rallies, servicos = [], []
    estado = "FORA"
    inicio = None
    mao_desde = None          # frame em que a bola comecou a estar na mao
    ultima_bola = None        # ultimo frame com bola visivel/movel

    def bola_visivel(f):
        return ball_xy[f] is not None

    for f in range(n):
        boxes = player_boxes[f] if f < len(player_boxes) else []
        pj = _bola_perto(ball_xy[f], boxes, limiar_mao_px)
        v = _vel(ball_xy, f)
        na_mao = pj is not None and (v is None or v < 3.0)  # perto + ~parada

        if estado == "FORA":
            # R1: bola estava na mao e AFASTA-SE => servico => inicio
            if mao_desde is not None and (f - mao_desde) >= frames_mao and pj is None:
                # inicio = momento em que a bola sai (servico), com no maximo 1.5s de preparacao antes
                inicio_cand = max(mao_desde, f - int(1.5 * fps))
                if servico_valido(inicio_cand, ball_xy, player_boxes, fps):
                    inicio = inicio_cand
                    servicos.append(f)          # frame do servico (bola sai)
                    estado = "EM_JOGO"
                    ultima_bola = f
                mao_desde = None
            elif na_mao:
                mao_desde = mao_desde if mao_desde is not None else f
            else:
                mao_desde = None

        elif estado == "EM_JOGO":
            if bola_visivel(f):
                ultima_bola = f
            # R3: bola na mao e parada por >= frames_mao => fim candidato
            fim_por_mao = na_mao and mao_desde is not None and (f - mao_desde) >= frames_mao
            # R2: bola sumiu ha' mais de gap
            fim_por_gap = ultima_bola is not None and (f - ultima_bola) > gap
            # R5 do prompt: todos os jogadores parados ~3s => fim rapido
            fim_por_paragem = jogadores_parados(player_boxes, f, fps)
            if na_mao:
                mao_desde = mao_desde if mao_desde is not None else f
            else:
                mao_desde = None

            if fim_por_mao or fim_por_gap or fim_por_paragem:
                if fim_por_mao:
                    fim_cand, motivo, conf = mao_desde, "bola_na_mao", "alta"
                elif fim_por_paragem:
                    fim_cand, motivo, conf = f, "jogadores_parados", "alta"
                else:
                    fim_cand, motivo, conf = ultima_bola, "timeout_bola", "media"
                # R5: confirmar — ha' nova pancada (nao-servico) na janela?
                nova = [p for p in pancadas if fim_cand < p <= fim_cand + jfim and p not in servicos]
                if nova:
                    continue  # rally continua
                # fecha
                if (fim_cand - inicio) / fps >= min_rally_s:
                    rallies.append((inicio, fim_cand, motivo, conf))
                estado = "FORA"
                inicio = None
                mao_desde = None

    # fecho no fim do video
    if estado == "EM_JOGO" and inicio is not None and ultima_bola is not None:
        if (ultima_bola - inicio) / fps >= min_rally_s:
            rallies.append((inicio, ultima_bola, "fim_video", "media"))

    dur = [(b - a) / fps for a, b, _, _ in rallies]
    mv = int(margem_video_s * fps)
    clips = [(a, min(n - 1, b + mv)) for a, b, _, _ in rallies]  # R8

    # R7 do prompt: trocas de campo = pausa > 45s entre rallies (cor da camisola fica p/ o Gemini)
    trocas = []
    for i in range(1, len(rallies)):
        pausa_s = (rallies[i][0] - rallies[i - 1][1]) / fps
        if pausa_s > 45.0:
            trocas.append({"apos_rally": i, "timestamp_s": round(rallies[i - 1][1] / fps, 3),
                           "pausa_s": round(pausa_s, 1), "nota": "reavaliar cores/lado no Gemini"})

    # margem_ms por rally: incerteza aproximada (2 frames), maior se o fim foi por timeout
    margem_base_ms = round(2 * 1000.0 / fps)

    def _audio_no_intervalo(a, b):
        return sum(1 for t in (audio_hits_s or []) if a <= t * fps <= b)

    def _conf_final(conf, a, b):
        # audio SO' reforca: se houver picos de audio dentro do rally, sobe media->alta
        if conf == "media" and _audio_no_intervalo(a, b) >= 2:
            return "alta"
        return conf

    return {
        "rallies": [{"id": i + 1, "inicio_frame": a, "fim_frame": b,
                     "inicio_s": round(a / fps, 3), "fim_s": round(b / fps, 3),
                     "dur_s": round((b - a) / fps, 3),
                     "fim_por": motivo, "confianca": _conf_final(conf, a, b),
                     "pancadas_audio": _audio_no_intervalo(a, b),   # referencia
                     "margem_ms": margem_base_ms * (2 if conf == "media" else 1)}
                    for i, (a, b, motivo, conf) in enumerate(rallies)],
        "trocas_de_campo": trocas,
        "eventos": {"servicos": servicos, "pancadas": pancadas},
        "tempo_util_s": round(sum(dur), 1),
        "n_rallies": len(rallies),
        "clips_video": clips,   # com margem R8 (nao contar no tempo util)
    }
