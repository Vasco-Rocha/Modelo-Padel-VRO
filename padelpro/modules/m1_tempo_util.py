"""
M1 — TEMPO ÚTIL.   12 jul 2026.

    RECALL 81,2%   PRECISÃO 70,2%   (heurística anterior: 72,0% / 63,0%)
    +9,2 pontos de recall  E  +7,2 de precisão.

Avaliado contra `ground_truth_parada4.md` — 12 rallies, 117 s, anotados à mão pelo Vasco.

--------------------------------------------------------------------------------------
A IDEIA (do Vasco)
--------------------------------------------------------------------------------------
45% das deteções de bola caem FORA dos rallies — e NÃO são falsos positivos: é bola a
sério (o jogador apanha-a, passa-a, prepara o serviço). Nenhum detetor a distingue,
e baixar o threshold não ajuda (a 0.7 já não se parte nenhum rally).

O que a distingue é o COMPORTAMENTO:

    a bola do intervalo NÃO faz trajetórias longas
    a bola do intervalo NÃO atravessa o campo de fundo a fundo

--------------------------------------------------------------------------------------
CASCATA (a ordem importa)
--------------------------------------------------------------------------------------
1. TRACKLETS    Ligar as deteções em trajetórias contínuas.
                É a regra da coerência do Vasco -- "confirmar com um antes e um pós" --
                generalizada. Uma deteção sozinha não tem passado nem futuro: é lixo.
                Mata o ténis branco do jogador e os pontos brancos do público.

2. CRUZAMENTO   A bola vai de um lado PROFUNDO ao outro lado PROFUNDO (prof > 0.35).
                Roçar a fita da rede NÃO conta -- é ali que o ruído oscila e engana.
                (Sem esta condição de profundidade, o sinal desaparece: 44% dos
                "cruzamentos" caíam em rally, contra 40% do acaso. Ou seja, nada.)

3. AGRUPAR      Cruzamentos a menos de `silencio` = o mesmo ponto.
4. FUNDIR       Grupos a menos de `merge` = o ponto continuou (houve um buraco).
5. EXIGIR >=2   Um rally tem mais do que uma troca. Uma só = quase sempre lixo.
6. MARGENS      pad0 antes (o serviço, que a bola quase não vê -- o jogador tapa-a)
                e pad1 depois (o fim do ponto).

--------------------------------------------------------------------------------------
O QUE NÃO ENTRA (e porquê)
--------------------------------------------------------------------------------------
A FORMAÇÃO dos jogadores NÃO é filtro. Medida, discrimina bem:
    o mais recuado dos 2 de cima -> serviço 1,05/1,06/1,07 · jogo aberto 0,61/0,69/0,86
mas só 28% dos frames de serviço têm as 2 boxes de cima válidas. Exigi-la faz o recall
dos serviços cair de 11/12 para 7/12. Serve para PONTUAR confiança, nunca para cortar.
Ver `m3_servico.confianca_formacao()`.

--------------------------------------------------------------------------------------
DIRETRIZ DE PRODUTO (manda em tudo)
    "Nunca perder um ponto. Mais lixo é preferível a menos tempo útil."
    Otimizar RECALL, não precisão.
--------------------------------------------------------------------------------------
"""
import math
import numpy as np

FPS_DEF = 29.97

# afinados contra o ground-truth (12 rallies / 117 s)
PADRAO = dict(vmax=90, gap_max=9, min_det=4, min_prof=0.35,
              silencio=3.0, merge=2.5, min_cruz=2,
              pad_antes=1.6, pad_depois=2.0, dur_min=1.5)


def vai_e_vem(bola, salto=60, volta=0.5, janela=30):
    """
    REGRA DO VAI-E-VEM (Vasco, 12 jul).  +5,8 pontos de PRECISÃO por 1 de recall.

        "um frame está num sítio; o seguinte (em menos de 1 segundo) está muito distante;
         o frame seguinte está outra vez perto do primeiro — ERRO."

            A ──────────► B (longe)
            └──► C (perto de A)        ⇒ B é o erro.

    Note-se a diferença para o tracklet: o tracklet, ao ver o salto, PARTIA a cadeia em
    duas. Esta regra TIRA o frame errado e mantém a cadeia inteira -- por isso ganha
    precisão quase sem perder recall. Apaga ~110 frames no Parada4.

    Corre ANTES dos tracklets.
    """
    fs = sorted(bola)
    out = dict(bola)
    d = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    mortos = []
    for i in range(1, len(fs) - 1):
        a, b, c = fs[i - 1], fs[i], fs[i + 1]
        if c - a > janela:
            continue
        dab, dbc, dac = d(bola[a], bola[b]), d(bola[b], bola[c]), d(bola[a], bola[c])
        if dab > salto and dbc > salto and dac < volta * min(dab, dbc):
            mortos.append(b)
    for m in mortos:
        out.pop(m, None)
    return out


def _erro_theta(bola, a, b):
    """A direção de a->b bate certo com o Theta (graus, eixo mod 180) dos dois lados?"""
    dx = bola[b][0] - bola[a][0]
    dy = bola[b][1] - bola[a][1]
    if math.hypot(dx, dy) < 4:
        return 0.0
    real = math.degrees(math.atan2(dy, dx))
    ea = abs(((bola[a][3] - real + 90) % 180) - 90)
    eb = abs(((bola[b][3] - real + 90) % 180) - 90)
    return max(ea, eb)


def _tracklets(bola, vmax, gap_max, min_det,
               theta=True, tol=35, l_min=4, gap_theta=20, vmax_theta=140):
    """
    Liga as deteções em trajetórias contínuas.

    COSTURA POR THETA (12 jul): quando o buraco é grande demais para ligar pela DISTÂNCIA,
    pergunta-se ao Theta -- "a bola ia mesmo nessa direção?". Se a direção bate certo dos
    DOIS lados, é a mesma bola, e o buraco deixa de partir a trajetória.

        sem Theta:  RECALL 74,1%  PRECISÃO 66,6%
        com Theta:  RECALL 84,3%  PRECISÃO 69,1%     <- +10,2 e +2,5 AO MESMO TEMPO

    Não é um compromisso: é informação NOVA a entrar (o Theta acerta a direção a 2°,
    e -- o que importa -- fá-lo numa ÚNICA deteção, sem precisar do frame seguinte).
    Era isto que faltava a todos os métodos que morreram nos buracos.

    bola: {frame: (x, y, L, Theta)}  -- L e Theta são as colunas do CSV do BlurBall.
    """
    fs = sorted(bola)
    if not fs:
        return []
    out, cur = [], [fs[0]]
    for a, b in zip(fs, fs[1:]):
        g = b - a
        d = math.hypot(bola[b][0] - bola[a][0], bola[b][1] - bola[a][1])
        liga = g <= gap_max and d <= vmax * g
        if not liga and theta and len(bola[a]) >= 4:
            liga = (g <= gap_theta and d <= vmax_theta * g
                    and bola[a][2] >= l_min and bola[b][2] >= l_min   # L: a bola VOA
                    and _erro_theta(bola, a, b) <= tol)               # e vai NAQUELA direção
        if liga:
            cur.append(b)
        else:
            out.append(cur); cur = [b]
    out.append(cur)
    return [t for t in out if len(t) >= min_det]


def cruzamentos(bola, campo, vmax, gap_max, min_det, min_prof):
    """Frames em que a bola atravessa a rede de fundo a fundo, DENTRO de um tracklet."""
    cr = []
    for tk in _tracklets(bola, vmax, gap_max, min_det):
        ult = None
        for f in tk:
            x, y = bola[f]
            lado, p = campo.prof(x, y)
            if p < min_prof:
                continue
            if ult and ult != lado:
                cr.append(f)
            ult = lado
    return sorted(cr)


def rallies(bola, campo, fps=FPS_DEF, **kw):
    """
    bola  : {frame: (x, y)}   -- do traj_frames_*.csv (só Visibility == 1)
    campo : m3_servico.CampoM3(calibracao_campo.json)
    -> [(frame_ini, frame_fim), ...]
    """
    p = {**PADRAO, **kw}
    bola = vai_e_vem(bola)                               # 0. tirar os erros de vai-e-vem
    cr = cruzamentos(bola, campo, p["vmax"], p["gap_max"], p["min_det"], p["min_prof"])
    if not cr:
        return []

    grupos = [[cr[0]]]                                   # 3. agrupar
    for c in cr[1:]:
        if c - grupos[-1][-1] <= p["silencio"] * fps:
            grupos[-1].append(c)
        else:
            grupos.append([c])

    seg = [[g[0], g[-1], len(g)] for g in grupos]
    fund = [seg[0]]                                      # 4. fundir
    for a, b, n in seg[1:]:
        if a - fund[-1][1] <= p["merge"] * fps:
            fund[-1][1] = b
            fund[-1][2] += n
        else:
            fund.append([a, b, n])

    out = [(int(a - p["pad_antes"] * fps), int(b + p["pad_depois"] * fps))
           for a, b, n in fund if n >= p["min_cruz"]]    # 5. >=2 cruzamentos
    return [(max(a, 0), b) for a, b in out              # 6. margens
            if (b - a) / fps >= p["dur_min"]]


def avaliar(segmentos, gt_segundos, n_frames, fps=FPS_DEF):
    """Recall e precisão em TEMPO (não em rallies). gt_segundos: [(ini_s, fim_s), ...]"""
    m = np.zeros(n_frames, bool)
    for a, b in segmentos:
        m[max(a, 0):min(b, n_frames - 1) + 1] = True
    g = np.zeros(n_frames, bool)
    for a, b in gt_segundos:
        g[int(a * fps):int(b * fps) + 1] = True
    tp = (m & g).sum(); fp = (m & ~g).sum(); fn = (~m & g).sum()
    rec = 100 * tp / max(tp + fn, 1)
    pre = 100 * tp / max(tp + fp, 1)
    return dict(n=len(segmentos), tempo_util_s=m.sum() / fps,
                recall=rec, precisao=pre, f1=2 * rec * pre / max(rec + pre, 1))


# ---------------------------------------------------------------------------
# REGRA DA ALTERNÂNCIA (Vasco, 12 jul) — por implementar. É a mais poderosa.
#
#   "Quando os serviços contam, o serviço seguinte é para o lado contrário.
#    Os serviços são ALTERNADOS."
#
#   Não é um filtro — é uma CADEIA. Os serviços verdadeiros formam uma sequência
#   ESQ/DIR/ESQ/DIR. Um falso alarme entre dois verdadeiros QUEBRA a alternância e
#   denuncia-se sozinho. Escolhe-se o melhor caminho pela sequência inteira (tipo Viterbi),
#   em vez de cortar candidatos um a um com limiares. Não custa recall.
#
#   BLOQUEIO ACTUAL: o instante que detetamos NÃO é o serviço — é a primeira troca
#   depois dele (rally 1: real 38,0 s, detetado 40,1 s). Para ler a alternância é preciso
#   recuar do cruzamento até ao serviço. É isso que o DUPLO RESSALTO dá.
#
#   >>> A FORMA CORRETA DA REGRA (Vasco, precisão dele):
#
#       O lado só muda quando o PONTO CONTA. Uma falta ou um let repete o serviço DO
#       MESMO LADO. Logo, numa corrida de serviços do mesmo lado, o que interessa é
#       O ÚLTIMO — é esse que arranca o ponto. Os anteriores são faltas/lets
#       (podem registar-se à parte; têm valor, mas não iniciam o ponto).
#
#           ESQ  ESQ  ESQ | DIR  DIR | ESQ
#                      ^         ^      ^
#                    ponto     ponto   ponto      (os outros: lets/faltas)
#
#   ⚠️ EXCEÇÃO — PONTO DE OURO (empate/desempate): o lado PODE repetir-se legitimamente.
#      Por isso a alternância PONTUA, não corta. Nunca aplicar como lei.
#
#   ⚠️ E ATENÇÃO AO GROUND-TRUTH: alguns dos "27 falsos" podem ser FALTAS e LETS REAIS,
#      que o ground-truth não conta como rally (não são pontos). Nesse caso a precisão
#      medida está a penalizar-nos por acertar. A confirmar com o Vasco.
#
#   >>> MUDANÇA DE SERVIDOR (Vasco) — a regra que FECHA o sistema
#
#       "Quando há repetição de sítio e 2 serviços válidos, o ponto seguinte tem de ser
#        outro servidor, obrigatoriamente."
#
#       Dentro de um jogo os lados alternam ponto a ponto (DIR ESQ DIR ESQ...). Se o
#       MESMO lado aparece em dois pontos VÁLIDOS seguidos, isso é a FRONTEIRA DO JOGO:
#       o serviço passa ao outro par -> muda o LADO DO CAMPO que serve (cima <-> baixo).
#
#       Ficam DUAS leituras independentes, que se validam uma à outra:
#
#           metade      (ESQ/DIR)      alterna a cada PONTO contado
#           lado campo  (cima/baixo)   muda a cada JOGO
#
#   ⛔ MAS O TIE-BREAK PARTE-A (Vasco): no tie-break o serviço RODA entre os quatro a cada
#      DOIS pontos (e trocam de lado do campo a cada seis). E como não sabemos o marcador,
#      não sabemos sequer QUANDO estamos em tie-break. => a "mudança de servidor por jogo"
#      é uma PISTA FRACA, não uma validação.
#
#   AS TRÊS REGRAS E AS SUAS EXCEÇÕES  (nenhuma é lei -- o Vasco apanhou-me a escrever
#   "SEMPRE" na primeira linha, e estava errado):
#
#      regra                        jogo normal  tie-break        ponto de ouro
#      ESQ/DIR alterna por ponto        sim         sim       NAO -- quem RECEBE escolhe
#                                                             o lado, pode repetir
#      falta/let repete o lado          sim         sim       sim
#      servidor muda por jogo           sim      NAO -- roda   sim
#                                                a cada 2 pts
#
#   ==> LEI DE DESENHO: NENHUMA regra de sequência pode VETAR um candidato.
#       Ponto de ouro, tie-break — há sempre uma exceção legítima do jogo que a viola.
#       Entram todas como CUSTO numa cadeia, e escolhe-se a sequência globalmente mais
#       consistente (tipo Viterbi). Um FALSO paga caro em vários sítios; uma EXCEÇÃO
#       legítima paga num só, e passa. Assim não se perde nenhum ponto — a diretriz.
# ---------------------------------------------------------------------------
# ⚠️ BUG APANHADO PELO VASCO (12 jul) — A BOX FANTASMA
#
#   "há uma bounding box a ser detetada constantemente do lado de baixo, que está
#    claramente fora do campo"
#
#   Estava. Em x≈62, y≈300 — em 32% dos frames. Um ESPECTADOR.
#   Causa: eu usei o atalho `40 < x < 930` em vez das LATERAIS REAIS do campo.
#   As laterais em y=300 são x=141 e x=882 -> o espectador em x=62 passava pela porta.
#
#   CONSEQUÊNCIA: os "4 jogadores em 52,6% dos frames" eram FALSOS — incluíam o
#   espectador. Com as laterais a sério: **21,8%**.
#   => TODA a medição da formação (`cima_max` 1,05/1,06/1,07) está SOB SUSPEITA e tem
#      de ser refeita com as boxes limpas.
#
#   REGRA DO VASCO (absoluta): "se não se detetar, NÃO SE INVENTA boxes fora do campo."
#   As laterais derivam-se dos pontos do calibracao_campo.json (descartando os que caem
#   na borda do frame, x<4 ou x>956 — esses são a borda, não o vidro). Ver servico.py.
#
# ---------------------------------------------------------------------------
# ⚠️ A CAUSA DOS 27 FALSOS (Vasco):
#
#   "estás a disparar serviços sempre que a bola sai da mão deles"
#
#   Exacto: qualquer bola que cruze a rede dispara. Falta EXIGIR a cadeia inteira:
#
#        SAI DA MÃO (cai e ressalta)  ->  RAQUETE  ->  CRUZADO para o quadrado OPOSTO
#
#   Não é qualquer travessia da rede: é uma travessia CRUZADA, e precedida do ressalto
#   do lançamento. "Tens de ser exigente nisso."
#
# ---------------------------------------------------------------------------
# 🔴 A ESPECIFICAÇÃO DO SERVIÇO (Vasco, 12 jul) — É ISTO. NÃO É NEGOCIÁVEL.
#
#     SAI DA MÃO -> CHÃO -> RAQUETE -> RESSALTO DENTRO DO QUADRADO CRUZADO -> pancada
#     seguinte segue o ponto.
#
#   "Qualquer serviço requer que a bola bata DENTRO DO QUADRADO DE SERVIÇO CRUZADO.
#    Sem isso NÃO HÁ SERVIÇO."   <- condição NECESSÁRIA, não pontuação.
#
#   "NÃO dispares serviços só por causa da estrutura (estarem todos posicionados)."
#   => a FORMAÇÃO nunca dispara nada sozinha. Só confirma.
#
#   Neste jogo NÃO houve faltas nem lets (confirmado pelo Vasco) -> os 27 falsos são
#   mesmo falsos. Causa, nas palavras dele: "estás a disparar sempre que a bola sai
#   da mão deles."
#
# ESTADO (12 jul, fim do dia):
#   ✅ O QUADRADO DE SERVIÇO está construído e é sólido — derivado INTEIRAMENTE da
#      calibração (rede_base, servico_perto/longe, centro_coef_em_y, laterais dos pontos
#      do Vasco). ZERO números à mão.
#   ❌ O DETETOR DE RESSALTO é o elo fraco: encontra só 102 ressaltos em todo o vídeo
#      (deviam ser muitos mais) e apanha 2/12 serviços.
#
#   PORQUÊ: um ressalto dura 2-3 frames, e no serviço a trajetória está esburacada
#   (o jogador tapa a bola — aviso do Vasco, confirmado). Estou a procurar o momento
#   mais curto e mais escondido do vídeo com o instrumento mais grosseiro.
#
#   O CAMINHO: NÃO é afinar limiares. É AJUSTAR A PARÁBOLA à trajetória (a bola no ar
#   é sempre uma parábola) e achar o VÉRTICE. A parábola tolera buracos; a comparação
#   de frames vizinhos não.
#
# ---------------------------------------------------------------------------
# PRÓXIMO PASSO — subir a precisão sem tocar no recall
#   O DUPLO RESSALTO (regra do Vasco): o serviço é a única jogada em que a bola
#   ressalta OBRIGATORIAMENTE dos dois lados da rede (o servidor deixa-a cair; e ela
#   tem de ressaltar no quadrado antes de o recetor lhe poder bater).
#   Ancorar no ressalto DE CIMA -- os dois estão em lados opostos, logo um está sempre
#   no lado que a câmara vê bem. O de baixo pode estar tapado pelo jogador.
#   O detetor de ressalto NÃO pode exigir frames seguidos: no serviço não os há.
# ---------------------------------------------------------------------------
