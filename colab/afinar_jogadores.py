# =============================================================================
#  JOGADORES — detetor generoso + as 4 REGRAS DO VASCO   (~3 min, um só rally)
#  Corre DEPOIS da célula 4 (usa VIDEO_PATH e CAMPO). Pede o calibracao_campo.json.
#
#  CASCATA (a ordem importa):
#     detetar GENEROSAMENTE (CONF baixo, IMGSZ alto)
#        -> 1. FORA DO CAMPO  (os pés nunca passam do vidro)
#        -> 2. IMÓVEIS        (só mata quem está FORA — dentro é IMUNE)
#        -> 3. CONTINUIDADE   (preenche buracos — a única que ACRESCENTA informação)
#        -> 4. COR DA ROUPA   (identidade sem depender dos pés) + 2 POR LADO
#
#  Lê só a coluna "=4" no fim.
# =============================================================================
import os, math, json, itertools
import cv2, numpy as np, supervision as sv
from trackers.players_tracker.players_tracker import PlayerTracker

# ---------- geometria do campo (a tua calibração) ----------------------------
if not os.path.exists('/content/calibracao_campo.json'):
    from google.colab import files
    print('Escolhe o calibracao_campo.json (pasta padelpro-vision/)')
    up = files.upload()
    os.rename(list(up.keys())[0], '/content/calibracao_campo.json')

CAL = json.load(open('/content/calibracao_campo.json'))
P = CAL['pontos']
ev = lambda c, t: float(np.polyval(c, t))

y_serv_perto = lambda x: ev(CAL['servico_perto_coef'], x)
y_serv_longe = lambda x: ev(CAL['servico_longe_coef'], x)
y_rede_base  = lambda x: ev(CAL['rede_base_coef'], x)
y_fundo      = lambda x: ev(CAL['fundo_longe_coef'], x)

_e, _d = [], []
for k in ('fundo_longe','servico_longe','rede_base','servico_perto','juncao_longe','juncao_perto'):
    if k not in P or len(P[k]) < 2: continue
    q = sorted(P[k], key=lambda t: t[0])
    for lado, pt in (('e', q[0]), ('d', q[-1])):
        if pt[0] < 4 or pt[0] > 956: continue      # borda do frame != vidro
        (_e if lado == 'e' else _d).append((pt[1], pt[0]))
c_esq = np.polyfit(np.array(_e)[:,0], np.array(_e)[:,1], 2)
c_dir = np.polyfit(np.array(_d)[:,0], np.array(_d)[:,1], 2)

video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)
W, H = video_info.resolution_wh
FPS = video_info.fps

pes = lambda b: ((b[0]+b[2])/2.0, b[3])

def lado_de(b):
    x, y = pes(b)
    if y >= H-2: return 'baixo'                # pés cortados pela borda -> fundo perto
    return 'baixo' if y > y_rede_base(x) else 'cima'

def meio_campo_px(x, lado):
    if lado == 'baixo': return abs(y_serv_perto(x) - y_rede_base(x))
    return abs(y_rede_base(x) - y_serv_longe(x))

def dentro_do_campo(b, margem=35, margem_fundo=4):
    x, y = pes(b)
    if y < y_fundo(x) - margem_fundo: return False
    if x < ev(c_esq, y) - margem:     return False
    if x > ev(c_dir, y) + margem:     return False
    return True

dentro_estrito = lambda b: dentro_do_campo(b, margem=0, margem_fundo=0)

# ---------- frames do rally --------------------------------------------------
T_INI, T_FIM = 46.8, 67.5                      # rally #2 do ground-truth
f0, f1 = int(T_INI*FPS), int(T_FIM*FPS)
cap = cv2.VideoCapture(VIDEO_PATH); cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
FRAMES = []
for _ in range(f1-f0):
    ok, im = cap.read()
    if not ok: break
    FRAMES.append(im)
cap.release()
print(f'rally: {len(FRAMES)} frames ({T_INI}s-{T_FIM}s)\n')

try:
    pz = sv.PolygonZone(CAMPO, frame_resolution_wh=video_info.resolution_wh)
except TypeError:
    pz = sv.PolygonZone(CAMPO)

def detetar(conf, imgsz):
    PlayerTracker.CONF = conf
    PlayerTracker.IMGSZ = imgsz
    tr = PlayerTracker('weights/players_detection/yolov8m.pt', pz, batch_size=8)
    tr.video_info_post_init(video_info)
    res, lote = [], []
    for im in FRAMES:
        lote.append(im)
        if len(lote) == 8:
            res.extend(tr.predict_sample(lote)); lote = []
    if lote: res.extend(tr.predict_sample(lote))
    out = []
    for players in res:
        d = {}
        for p in players:
            pid = p.id if p.id is not None else -len(d)-1
            d[pid] = (tuple(float(v) for v in p.xyxy), float(p.confidence))
        out.append(d)
    return out

# =============================================================================
#  REGRA 1 — FORA DO CAMPO
# =============================================================================
def r1_fora_do_campo(fr):
    return [{i:v for i,v in d.items() if dentro_do_campo(v[0])} for d in fr]

# =============================================================================
#  REGRA 2 — IMÓVEIS (com a salvaguarda: dentro do campo = IMUNE)
#  Um jogador MOVE-SE; um espectador NÃO. Mas um jogador de fundo quase não se
#  mexe EM PÍXEIS (25 px lá valem ~1,7 m) — por isso quem está dentro é imune.
#  Por construção, esta regra nunca pode matar um jogador.
# =============================================================================
def r2_imoveis(fr, tol=25, max_frac=0.25):
    n = len(fr); cont = {}
    for d in fr:
        vistos = set()
        for i, (b, c) in d.items():
            if dentro_estrito(b): continue                     # IMUNE
            x, y = pes(b); cel = (int(x//tol), int(y//tol))
            if cel not in vistos:
                cont[cel] = cont.get(cel, 0) + 1; vistos.add(cel)
    mortos = {k for k, v in cont.items() if v > max_frac*n}
    out = []
    for d in fr:
        keep = {}
        for i, (b, c) in d.items():
            if dentro_estrito(b): keep[i] = (b, c); continue   # IMUNE
            x, y = pes(b)
            if (int(x//tol), int(y//tol)) not in mortos: keep[i] = (b, c)
        out.append(keep)
    return out

# =============================================================================
#  REGRA 3 — CONTINUIDADE
#  Um jogador não se teletransporta NEM desaparece a meio do ponto.
#  1) rejeita saltos impossíveis   2) PREENCHE buracos (interpola)
#  A velocidade fala em m/s e converte-se localmente: 9 m/s valem ~12 px/frame
#  à frente e ~4 px/frame ao fundo.
# =============================================================================
def r3_continuidade(fr, v_max_ms=9.0, max_buraco=15):
    n = len(fr); out = [dict(d) for d in fr]
    ids = set()
    for d in fr: ids |= set(d)
    saltos = cheios = 0
    for pid in ids:
        vis = [f for f in range(n) if pid in out[f]]
        if len(vis) < 2: continue
        anc = vis[0]
        for b in vis[1:]:
            ba = out[anc][pid][0]
            x, y = pes(ba)
            ppm = max(meio_campo_px(x, lado_de(ba))/6.95, 1.0)
            lim = v_max_ms * ppm * ((b-anc)/FPS) * 1.5
            pa, pb = pes(ba), pes(out[b][pid][0])
            if math.hypot(pb[0]-pa[0], pb[1]-pa[1]) > lim:
                del out[b][pid]; saltos += 1
            else:
                anc = b
        vis = [f for f in range(n) if pid in out[f]]
        for a, b in zip(vis, vis[1:]):
            gap = b - a - 1
            if not (0 < gap <= max_buraco): continue
            (ba, ca), (bb, cb) = out[a][pid], out[b][pid]
            for k in range(1, gap+1):
                t = k/(gap+1)
                out[a+k][pid] = (tuple(ba[i] + t*(bb[i]-ba[i]) for i in range(4)), min(ca, cb))
                cheios += 1
    return out, saltos, cheios

# =============================================================================
#  REGRA 4 — COR DA ROUPA + 2 POR LADO           <<< a ideia nova do Vasco
#
#  PORQUE: o desempate por CONFIANÇA do detetor escolhe contra nós justamente
#  nos casos difíceis — um espectador nítido e inteiro tem MAIS confiança do que
#  um jogador cortado ao meio pela borda. A cor não depende de estar cortado,
#  nem de estar longe, nem dos pés.
#
#  COMO: assinatura = 4 faixas do corpo -- TORSO (camisola), CALÇÕES, PERNAS e
#  TÉNIS. Cada faixa dá matiz (16 bins) + brilho (4 bins) -- o brilho é preciso
#  porque branco e preto NÃO têm matiz nenhuma, e são as cores mais comuns em ténis.
#  Aprendem-se as 4 assinaturas dos jogadores (as deteções DENTRO do campo,
#  agrupadas em 4). Depois cada deteção é pontuada pela parecença com a mais
#  próxima. "Se uma camisola apareceu demasiadas vezes, só pode voltar a ser essa."
#
#  Os TÉNIS só existem quando os pés estão no frame. No jogador cortado pela borda
#  essa faixa vem a zeros -- é informação a MENOS, não informação ERRADA.
#
#  DEGRADA BEM: se duas equipas vestirem cores parecidas, a cor deixa de
#  desempatar e caímos de volta na confiança — não parte.
# =============================================================================
def assinatura(img, b):
    """Assinatura de cor de UMA detecao: 4 faixas do corpo.

      TORSO    (15-50%)  camisola     -- a mais informativa
      CALCOES  (50-72%)  calcoes      -- em padel sao muitas vezes de outra cor
      PERNAS   (72-88%)  pele/meias   -- ajuda a separar quem tem meias altas
      TENIS    (88-100%) sapatilhas   -- muitas vezes a peca MAIS distintiva
                                         (branco vs preto vs cor viva)

    Cada faixa da: histograma de MATIZ (16 bins, ignorando cinzentos) +
    histograma de BRILHO (4 bins -- e' o que separa "branco" de "preto",
    que nao tem matiz nenhum). 20 numeros por faixa, 80 no total.

    NOTA: os TENIS so' existem se os pes estiverem no frame. Quando o jogador de
    baixo esta' cortado pela borda, essa faixa vem a zeros -- e' informacao a
    menos, nao informacao errada. As outras faixas seguram a identidade.
    """
    x1, y1, x2, y2 = [int(v) for v in b]
    x1, y1 = max(x1, 0), max(y1, 0)
    x2, y2 = min(x2, W-1), min(y2, H-1)
    if x2-x1 < 4 or y2-y1 < 10:
        return None
    h = y2 - y1
    FAIXAS = ((.15, .50),   # torso
              (.50, .72),   # calcoes
              (.72, .88),   # pernas
              (.88, 1.00))  # tenis
    sig = []
    for a, z in FAIXAS:
        roi = img[y1+int(a*h):y1+int(z*h), x1:x2]
        if roi.size == 0:
            sig.append(np.zeros(20, np.float32)); continue
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        m = ((hsv[:, :, 1] > 40) & (hsv[:, :, 2] > 40)).astype(np.uint8)
        hh = cv2.calcHist([hsv], [0], m, [16], [0, 180]).flatten()   # matiz
        vv = cv2.calcHist([hsv], [2], None, [4], [0, 256]).flatten() # brilho
        v = np.concatenate([hh, vv]).astype(np.float32)
        sv_ = v.sum()
        sig.append(v/sv_ if sv_ > 0 else v)
    return np.concatenate(sig)   # 80 numeros

def aprender_assinaturas(fr, k=4, amostras=400):
    X = []
    passo = max(1, len(fr)//(amostras//4 + 1))
    for f in range(0, len(fr), passo):
        for i, (b, c) in fr[f].items():
            if not dentro_estrito(b): continue
            s = assinatura(FRAMES[f], b)
            if s is not None: X.append(s)
    if len(X) < k*5: return None
    X = np.array(X, dtype=np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, _, centros = cv2.kmeans(X, k, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    return centros

def parecenca(sig, centros):
    """1.0 = igual a um dos 4 jogadores; 0.0 = nada a ver."""
    if sig is None or centros is None: return 0.0
    d = np.linalg.norm(centros - sig, axis=1).min()
    return float(np.exp(-3.0 * d))

def r4_cor_e_dois_por_lado(fr, centros, peso_cor=1.0):
    out = []
    for f, d in enumerate(fr):
        cima, baixo = [], []
        for i, (b, c) in d.items():
            s = assinatura(FRAMES[f], b)
            score = c + peso_cor * parecenca(s, centros)      # confiança + cor
            (baixo if lado_de(b) == 'baixo' else cima).append((score, i, b, c))
        keep = {}
        for g in (cima, baixo):
            g.sort(key=lambda t: -t[0])
            for score, i, b, c in g[:2]: keep[i] = (b, c)
        out.append(keep)
    return out

# =============================================================================
#  TABELA
# =============================================================================
print(f'{"CONF":>5} {"IMG":>5} | {"bruto":>11} | {"+campo":>7} | {"+contin":>15} | '
      f'{"conf":>6} | {"COR":>6}')
print(f'{"":>5} {"":>5} | {">=4":>5} {"med":>4} | {">=4":>6} | {">=4":>6} {"cheios":>7} | '
      f'{"=4":>6} | {"=4":>6}')
print('-'*70)

melhor = None
for conf, imgsz in itertools.product([0.5, 0.3, 0.2, 0.1], [640, 960, 1280]):
    fr = detetar(conf, imgsz)
    nb = np.array([len(d) for d in fr])

    a = r2_imoveis(r1_fora_do_campo(fr))
    na = np.array([len(d) for d in a])

    b, saltos, cheios = r3_continuidade(a)
    nbb = np.array([len(d) for d in b])

    # desempate por CONFIANCA (o antigo)
    velho = []
    for d in b:
        cima, baixo = [], []
        for i, (bx, c) in d.items():
            (baixo if lado_de(bx) == 'baixo' else cima).append((c, i, bx))
        keep = {}
        for g in (cima, baixo):
            g.sort(key=lambda t: -t[0])
            for c, i, bx in g[:2]: keep[i] = (bx, c)
        velho.append(keep)
    nv = np.array([len(d) for d in velho])

    # desempate por COR (o novo)
    centros = aprender_assinaturas(b)
    novo = r4_cor_e_dois_por_lado(b, centros)
    nn = np.array([len(d) for d in novo])

    e4_cor = (nn == 4).mean()*100
    marca = '  <- default' if (conf, imgsz) == (0.5, 640) else ''
    print(f'{conf:5.2f} {imgsz:5d} | {(nb>=4).mean()*100:4.0f}% {nb.mean():4.1f} | '
          f'{(na>=4).mean()*100:5.0f}% | {(nbb>=4).mean()*100:5.0f}% {cheios:7d} | '
          f'{(nv==4).mean()*100:5.1f}% | {e4_cor:5.1f}%{marca}')
    if melhor is None or e4_cor > melhor[0]:
        melhor = (e4_cor, conf, imgsz)

print()
print(f'>>> MELHOR: 4 jogadores em {melhor[0]:.1f}% do rally  '
      f'com CONF={melhor[1]} IMGSZ={melhor[2]}')
print('    (o default do Joao, sem regras, dava 9.5%)')
print()
print('Colunas "conf" vs "COR": se a COR ganhar, e porque o desempate por confianca')
print('estava a escolher o espectador nitido em vez do jogador cortado ao meio.')
