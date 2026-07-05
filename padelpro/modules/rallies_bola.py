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


def detetar_pancadas(ball_xy, player_boxes, fps, limiar_px=80.0, pico_vel=25.0,
                     ang_min_deg=55.0, max_gap_f=None):
    """Deteção de pancada pela TRAJETORIA da bola (metodo inspirado no paper de tenis de
    mesa 'Stroke Detection Using Ball Trajectory Data', arxiv 2302.09657): uma pancada e' uma
    MUDANCA BRUSCA de direcao/velocidade da bola (contacto com a raquete/parede).

    Sinais combinados:
      (a) angulo entre o vetor de entrada (i-1->i) e de saida (i->i+1) > ang_min_deg (a bola 'dobra');
      (b) OU pico de velocidade junto a uma box de jogador (contacto).
    Usa so' frames com bola detetada (salta gaps ate max_gap_f) para ser robusto ao recall baixo.
    """
    import math
    if max_gap_f is None:
        max_gap_f = int(0.5 * fps)
    n = len(ball_xy)
    pts = [(f, ball_xy[f][0], ball_xy[f][1]) for f in range(n) if ball_xy[f] is not None]
    pancadas = []
    for k in range(1, len(pts) - 1):
        (f0, x0, y0), (f1, x1, y1), (f2, x2, y2) = pts[k - 1], pts[k], pts[k + 1]
        if f1 - f0 > max_gap_f or f2 - f1 > max_gap_f:
            continue
        vin = (x1 - x0, y1 - y0); vout = (x2 - x1, y2 - y1)
        nin = math.hypot(*vin); nout = math.hypot(*vout)
        if nin < 1e-6 or nout < 1e-6:
            continue
        cos = (vin[0] * vout[0] + vin[1] * vout[1]) / (nin * nout)
        ang = math.degrees(math.acos(max(-1.0, min(1.0, cos))))
        # (a) a trajetoria dobra o suficiente
        dobra = ang >= ang_min_deg
        # (b) ou pico de velocidade perto de um jogador
        pj = _bola_perto((x1, y1), player_boxes[f1] if f1 < len(player_boxes) else [], limiar_px)
        pico = pj is not None and nout / max(1, (f2 - f1)) >= pico_vel
        if dobra or pico:
            if not pancadas or f1 - pancadas[-1] > int(0.3 * fps):   # anti-duplicado
                pancadas.append(f1)
    return pancadas


def _centro(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _box_mais_proxima(boxes, ponto):
    if not boxes or ponto is None:
        return None
    return min(boxes, key=lambda b: _dist_ponto_box(ponto, b))


def _subida_apos_servico(player_boxes, f0, servidor, fps, center_y,
                         seg=1.5, min_aprox_px=20.0) -> bool:
    """Idea do Vasco: apos servir, o servidor CORRE para o interior (sobe a' rede).
    Segue a box mais proxima do servidor nos ~seg seguintes e ve se os pes se APROXIMAM
    do interior (center_y = entre as duas linhas de servico) pelo menos min_aprox_px."""
    n = len(player_boxes)
    if f0 >= n or center_y is None:
        return False
    ref = _centro(servidor)
    d0 = abs(servidor[3] - center_y)          # distancia inicial dos pes ao interior
    melhor = 0.0
    for f in range(f0 + 1, min(f0 + int(seg * fps), n)):
        bs = player_boxes[f]
        if not bs:
            continue
        b = min(bs, key=lambda b: (_centro(b)[0] - ref[0])**2 + (_centro(b)[1] - ref[1])**2)
        ref = _centro(b)
        melhor = max(melhor, d0 - abs(b[3] - center_y))
    return melhor >= min_aprox_px


def _formacao_servico(boxes, serve_zone_y, center_y, tol_rede_px=70.0) -> bool:
    """Formacao de servico (ideia do Vasco): 3 jogadores na/perto da linha de servico
    (incluindo o servidor) + o parceiro do servidor na REDE. Precisa das bandas calibradas."""
    if not boxes or not serve_zone_y or center_y is None:
        return False
    na_linha = sum(1 for b in boxes if any(ymin <= b[3] <= ymax for (ymin, ymax) in serve_zone_y))
    na_rede = sum(1 for b in boxes if abs(b[3] - center_y) <= tol_rede_px)
    return na_linha >= 3 and na_rede >= 1


def _box_parada_antes(player_boxes, f0, ponto, fps, seg=0.7, desloc_px=25.0) -> bool:
    """Idea B (parcial): o jogador de onde a bola sai estava ~PARADO (preparado) antes do
    servico. Sem IDs de tracking, aproxima pela box mais proxima frame a frame."""
    w = int(seg * fps)
    if f0 - w < 0 or f0 >= len(player_boxes):
        return False
    b0 = _box_mais_proxima(player_boxes[f0], ponto)
    if b0 is None:
        return False
    c0 = _centro(b0)
    for f in range(f0 - w, f0):
        bs = player_boxes[f] if f < len(player_boxes) else []
        if not bs:
            return False
        cn = min((_centro(b) for b in bs), key=lambda c: (c[0] - c0[0])**2 + (c[1] - c0[1])**2)
        if abs(cn[0] - c0[0]) > desloc_px or abs(cn[1] - c0[1]) > desloc_px:
            return False
    return True


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
    limiar_mao_px=60.0,      # bola "colada" a' box do jogador (fim: bola na mao)
    limiar_servico_px=90.0,  # bola SAI de perto de uma box (inicio: servico)
    frames_mao=None,          # K frames para confirmar bola na mao (default ~0.4s)
    gap_fora_s=2.0,           # R2: bola sumida > isto (usado so' sem serve_zone)
    gap_max_s=8.0,            # com serve_zone: junta corridas ate' este gap se a seguinte NAO for servico
    janela_fim_s=5.0,         # R5: esperar isto por nova pancada (Vasco: 5s)
    min_rally_s=1.0,          # R7
    margem_video_s=2.0,       # R8: so' para o clip de video
    audio_hits_s=None,        # R15: lista de timestamps (s) de pancada por AUDIO — REFERENCIA
    audio_tol_s=0.5,          # tolerancia do audio (pode estar atrasado)
    margem_fim_s=3.0,         # segundos apos a ultima pancada (o detetor perde os ultimos toques)
    serve_zone_y=None,        # bandas de servico (pixeis) p/ camara fixa: [(ymin,ymax),...]
                              #   os pes do servidor tem de estar numa banda. None = nao filtra.
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

    # ---- NUCLEO: esqueleto pela ATIVIDADE DA BOLA (robusto ao recall baixo) ----
    # A bola so' e' detetada em ~15% dos frames, por isso NAO se exige servico para
    # o rally existir. O rally = corrida de presenca da bola, unindo falhas <= gap.
    # O servico e a bola-na-mao servem so' para AFINAR as pontas (nao para gatear).
    present = [ball_xy[f] is not None for f in range(n)]
    runs = []
    i = 0
    while i < n:
        if not present[i]:
            i += 1; continue
        a = i
        while i + 1 < n and present[i + 1]:
            i += 1
        runs.append([a, i]); i += 1
    def _na_mao(f):
        boxes = player_boxes[f] if f < len(player_boxes) else []
        pj = _bola_perto(ball_xy[f], boxes, limiar_mao_px)
        v = _vel(ball_xy, f)
        return pj is not None and (v is None or v < 3.0)

    cy_zone = (sum((a + b) / 2.0 for (a, b) in serve_zone_y) / len(serve_zone_y)) if serve_zone_y else None

    def _comeca_com_servico(f0):
        """A bola EMERGE de perto de um jogador na zona de servico, parado/formacao = SERVICO."""
        if ball_xy[f0] is None or not serve_zone_y:
            return False
        boxes = player_boxes[f0] if f0 < len(player_boxes) else []
        sv = _box_mais_proxima(boxes, ball_xy[f0])
        if sv is None or _dist_ponto_box(ball_xy[f0], sv) >= limiar_servico_px:
            return False
        if not any(ymin <= sv[3] <= ymax for (ymin, ymax) in serve_zone_y):
            return False
        return (_box_parada_antes(player_boxes, f0, ball_xy[f0], fps)
                or _formacao_servico(boxes, serve_zone_y, cy_zone))

    # REGRA DO VASCO: o ponto so' acaba se a PROXIMA PANCADA for SERVICO.
    # -> junta corridas de bola separadas por um gap SE a seguinte NAO comeca por servico
    #    (o ponto continuou apos falha de detecao); so' separa quando a seguinte E' um servico.
    gap_max = int(gap_max_s * fps)
    merged = []
    for r in runs:
        if merged:
            gap_frames = r[0] - merged[-1][1] - 1
            if serve_zone_y:
                junta = (not _comeca_com_servico(r[0])) and gap_frames <= gap_max
            else:
                junta = gap_frames <= gap        # fallback sem serve_zone: gap fixo
            if junta:
                merged[-1][1] = r[1]
                continue
        merged.append(list(r))

    # evento global: bola-na-mao sustida (para afinar o FIM)
    hand_holds = []
    mao_desde = None
    for f in range(n):
        if _na_mao(f):
            if mao_desde is None:
                mao_desde = f
            if (f - mao_desde) == frames_mao:
                hand_holds.append(mao_desde)            # inicio de bola-na-mao sustida
        else:
            mao_desde = None

    pre = int(0.5 * fps)          # pequena preparacao antes do servico
    win_e = int(1.0 * fps)        # janela p/ associar bola-na-mao ao fim
    rallies, servicos = [], []
    for s, e in merged:
        if (e - s) / fps < min_rally_s:
            continue
        # SERVICO (ideia do Vasco): a bola COMECA a mover-se saindo de uma box de jogador,
        # mesmo que nao fosse detetada antes. => 1a aparicao da bola na corrida, perto de uma box.
        f0 = next((f for f in range(s, min(e + 1, n)) if present[f]), s)
        boxes0 = player_boxes[f0] if f0 < len(player_boxes) else []
        servidor = _box_mais_proxima(boxes0, ball_xy[f0])
        perto_jogador = servidor is not None and _dist_ponto_box(ball_xy[f0], servidor) < limiar_servico_px
        # servidor perto da LINHA DE SERVICO (camara fixa): pes (base da box) numa banda
        na_zona = True
        center_y = None
        if serve_zone_y:
            center_y = sum((a + b) / 2.0 for (a, b) in serve_zone_y) / len(serve_zone_y)
            if perto_jogador:
                na_zona = any(ymin <= servidor[3] <= ymax for (ymin, ymax) in serve_zone_y)
        if perto_jogador:
            preparado = _box_parada_antes(player_boxes, f0, ball_xy[f0], fps)      # parado antes
            subiu = _subida_apos_servico(player_boxes, f0, servidor, fps, center_y)  # corre p/ a rede
            formacao = _formacao_servico(boxes0, serve_zone_y, center_y)           # 3 na linha + parceiro na rede
            inicio = max(0, f0 - pre)
            # servico "de livro" = na zona + (parado antes / sobe a' rede / formacao correta)
            sinais = sum([preparado, na_zona, subiu, formacao])
            if na_zona and sinais >= 2:
                mo_i, conf = "servico", "alta"
            elif na_zona and (preparado or subiu):
                mo_i, conf = "servico", "media"
            elif na_zona:
                mo_i, conf = "servico?", "media"
            else:
                mo_i, conf = "bola_sai_jogador", "baixa"   # perto de jogador mas fora da zona
            servicos.append(f0)
        else:
            inicio = s; mo_i = "bola_ativa"; conf = "media"
        # afinar FIM: ULTIMA PANCADA detetada + margem_fim_s (o detetor perde os ultimos
        # toques, por isso a ultima pancada fica cedo; a margem cobre o resto do ponto).
        # Excecao: bola-na-mao (ponto apanhado) = fim limpo, sem margem.
        margem_fim = int(margem_fim_s * fps)
        pcs = [p for p in pancadas if inicio < p <= e]
        hc = [h for h in hand_holds if inicio < h <= e + win_e]
        if hc:
            fim = min(hc); mo_f = "bola_na_mao"
        elif pcs:
            fim = min(pcs[-1] + margem_fim, n - 1); mo_f = "ultima_pancada+margem"
        else:
            fim = min(e + margem_fim, n - 1); mo_f = "bola_parou+margem"
        if (fim - inicio) / fps >= min_rally_s:
            rallies.append((inicio, fim, f"{mo_i}/{mo_f}", conf))

    # --- REGRA DO VASCO: um SERVICO dentro de um rally => o ponto ANTERIOR acabou ---
    # Todo o servico marca o fim do ponto anterior (na ultima pancada antes do servico).
    # Isto separa rallies colados por engano (ex.: um rally de 30s que sao 2 pontos).
    def _e_servico_forte(f):
        if ball_xy[f] is None or not serve_zone_y:
            return False
        boxes = player_boxes[f] if f < len(player_boxes) else []
        sv = _box_mais_proxima(boxes, ball_xy[f])
        if sv is None or _dist_ponto_box(ball_xy[f], sv) >= limiar_servico_px:
            return False
        cy = sum((a + b) / 2.0 for (a, b) in serve_zone_y) / len(serve_zone_y)
        na_zona = any(ymin <= sv[3] <= ymax for (ymin, ymax) in serve_zone_y)
        return na_zona and _formacao_servico(boxes, serve_zone_y, cy)

    if serve_zone_y:
        sep = int(3.0 * fps)
        rallies2 = []
        for (a, b, mo, cf) in rallies:
            # servicos fortes DENTRO do rally (>3s depois do inicio)
            internos = []
            for f in range(a + sep, b):
                if _e_servico_forte(f) and (not internos or f - internos[-1] > sep):
                    internos.append(f)
            if not internos:
                rallies2.append((a, b, mo, cf)); continue
            ini = a
            for g in internos:
                pcs_prev = [p for p in pancadas if ini < p < g]     # ultima pancada antes do servico
                fim_prev = pcs_prev[-1] if pcs_prev else g - 1
                if (fim_prev - ini) / fps >= min_rally_s:
                    rallies2.append((ini, fim_prev, f"{mo}|split", cf))
                ini = max(g - pre, fim_prev + 1)                    # novo ponto comeca no servico
            if (b - ini) / fps >= min_rally_s:
                rallies2.append((ini, b, "servico|split", "alta"))
        rallies = rallies2

    # de-overlap: a margem de fim nao pode invadir o rally seguinte
    rallies.sort(key=lambda r: r[0])
    for i in range(len(rallies) - 1):
        a, b, mo, cf = rallies[i]
        a_next = rallies[i + 1][0]
        if b >= a_next:
            rallies[i] = (a, max(a, a_next - 1), mo, cf)

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
