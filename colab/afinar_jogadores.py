# =============================================================================
#  AFINAR O DETETOR + AS 3 REGRAS DO VASCO  — num só rally (~2 min)
#  Corre DEPOIS da célula 4 (precisa de VIDEO_PATH e CAMPO).
#  Pede o calibracao_campo.json (a geometria do campo).
#
#  CASCATA (a ordem importa):
#     detetar generosamente  ->  fora do campo + imóveis
#                            ->  CONTINUIDADE (preenche buracos)
#                            ->  2 por lado (corta o que sobra)
#
#  Olha só para a coluna "=4" no fim.
# =============================================================================
import os, math, json, itertools
import cv2, numpy as np, supervision as sv
from trackers.players_tracker.players_tracker import PlayerTracker

# ---------- 1. geometria do campo (a tua calibração) -------------------------
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
        if pt[0] < 4 or pt[0] > 956: continue     # borda do frame != vidro
        (_e if lado == 'e' else _d).append((pt[1], pt[0]))
_E, _D = np.array(_e), np.array(_d)
c_esq = np.polyfit(_E[:,0], _E[:,1], 2)
c_dir = np.polyfit(_D[:,0], _D[:,1], 2)

video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)
W, H = video_info.resolution_wh
FPS = video_info.fps

def pes(b):
    return ((b[0]+b[2])/2.0, b[3])

def lado_de(b):
    x, y = pes(b)
    if y >= H-2: return 'baixo'            # pés cortados pela borda -> fundo perto
    return 'baixo' if y > y_rede_base(x) else 'cima'

def meio_campo_px(x, lado):
    if lado == 'baixo': return abs(y_serv_perto(x) - y_rede_base(x))
    return abs(y_rede_base(x) - y_serv_longe(x))

def dentro_do_campo(b, margem=35, margem_fundo=4):
    x, y = pes(b)
    if y < y_fundo(x) - margem_fundo: return False        # atrás do vidro do fundo
    if x < ev(c_esq, y) - margem:     return False
    if x > ev(c_dir, y) + margem:     return False
    return True

# ---------- 2. correr o detetor ---------------------------------------------
T_INI, T_FIM = 46.8, 67.5                 # rally #2 do ground-truth
f0, f1 = int(T_INI*FPS), int(T_FIM*FPS)
cap = cv2.VideoCapture(VIDEO_PATH); cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
frames = []
for _ in range(f1-f0):
    ok, im = cap.read()
    if not ok: break
    frames.append(im)
cap.release()
print(f'rally: {len(frames)} frames ({T_INI}s-{T_FIM}s)\n')

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
    for im in frames:
        lote.append(im)
        if len(lote) == 8:
            res.extend(tr.predict_sample(lote)); lote = []
    if lote: res.extend(tr.predict_sample(lote))
    # -> lista por frame de {id: (box, conf)}
    out = []
    for players in res:
        d = {}
        for p in players:
            pid = p.id if p.id is not None else -len(d)-1
            d[pid] = (tuple(float(v) for v in p.xyxy), float(p.confidence))
        out.append(d)
    return out

# ---------- 3. as 3 regras do Vasco -----------------------------------------
def r1_fora_do_campo(fr):
    return [{i:v for i,v in d.items() if dentro_do_campo(v[0])} for d in fr]

def r1b_imoveis(fr, tol=25, max_frac=0.25):
    n = len(fr); cont = {}
    for d in fr:
        for i, (b, c) in d.items():
            x, y = pes(b); cont[(int(x//tol), int(y//tol))] = cont.get((int(x//tol), int(y//tol)), 0) + 1
    mortos = {k for k, v in cont.items() if v > max_frac*n}
    out = []
    for d in fr:
        keep = {}
        for i, (b, c) in d.items():
            x, y = pes(b)
            if (int(x//tol), int(y//tol)) not in mortos: keep[i] = (b, c)
        out.append(keep)
    return out

def r2_continuidade(fr, v_max_ms=9.0, max_buraco=15):
    n = len(fr)
    out = [dict(d) for d in fr]
    ids = set()
    for d in fr: ids |= set(d)
    saltos = cheios = 0
    for pid in ids:
        vis = [f for f in range(n) if pid in out[f]]
        if len(vis) < 2: continue
        for a, b in zip(vis, vis[1:]):
            ba = out[a][pid][0]
            x, y = pes(ba)
            ppm = max(meio_campo_px(x, lado_de(ba))/6.95, 1.0)
            lim = v_max_ms * ppm * ((b-a)/FPS) * 1.5
            pa, pb = pes(out[a][pid][0]), pes(out[b][pid][0])
            if math.hypot(pb[0]-pa[0], pb[1]-pa[1]) > lim:
                del out[b][pid]; saltos += 1
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

def r3_dois_por_lado(fr):
    out = []
    for d in fr:
        cima, baixo = [], []
        for i, (b, c) in d.items():
            (baixo if lado_de(b) == 'baixo' else cima).append((c, i, b))
        keep = {}
        for g in (cima, baixo):
            g.sort(key=lambda t: -t[0])
            for c, i, b in g[:2]: keep[i] = (b, c)
        out.append(keep)
    return out

# ---------- 4. tabela --------------------------------------------------------
print(f'{"CONF":>5} {"IMG":>5} | {"bruto":>12} | {"+campo":>7} | {"+contin.":>16} | {"+2/lado":>13}')
print(f'{"":>5} {"":>5} | {">=4":>5} {"med":>5} | {">=4":>6} | {">=4":>6} {"cheios":>8} | {"=4":>6} {">=3":>5}')
print('-'*72)
melhor = None
for conf, imgsz in itertools.product([0.5, 0.3, 0.2, 0.1], [640, 960, 1280]):
    fr = detetar(conf, imgsz)
    nb = np.array([len(d) for d in fr])
    a = r1b_imoveis(r1_fora_do_campo(fr))
    na = np.array([len(d) for d in a])
    b, saltos, cheios = r2_continuidade(a)
    nbb = np.array([len(d) for d in b])
    c = r3_dois_por_lado(b)
    nc = np.array([len(d) for d in c])
    e4 = (nc == 4).mean()*100
    marca = '  <- default' if (conf, imgsz) == (0.5, 640) else ''
    print(f'{conf:5.2f} {imgsz:5d} | {(nb>=4).mean()*100:4.0f}% {nb.mean():5.2f} | '
          f'{(na>=4).mean()*100:5.0f}% | {(nbb>=4).mean()*100:5.0f}% {cheios:8d} | '
          f'{e4:5.1f}% {(nc>=3).mean()*100:4.0f}%{marca}')
    if melhor is None or e4 > melhor[0]: melhor = (e4, conf, imgsz)

print()
print(f'>>> MELHOR: 4 jogadores em {melhor[0]:.1f}% do rally  com CONF={melhor[1]} IMGSZ={melhor[2]}')
print('    (o default do Joao, sem regras, dava 9.5%)')
