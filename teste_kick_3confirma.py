#!/usr/bin/env python3
"""TESTE (Vasco, 16 jul): o kick so conta se tiver PELO MENOS K detecoes a DESCER antes
e K a SUBIR depois do vertice (prova mais dura — rejeita o quique de 1 frame de ruido).
K=3 e' o pedido. Mostro K=1..4 para ver o custo. Corre nos DOIS videos. NAO toca no pipeline."""
import csv, json, os

REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
FPS_P = 29.97
FPS_B = 29.97002997002997
QUIQUE_JANELA = 3.0
QUIQUE_PROF   = 0.7
DY_MIN        = 1.0

VIDEOS = {
 "PARADA4": dict(
    bola=os.path.join(REPO, "padelpro-vision/data/parada4/traj_frames_Parada4_thr04.csv"),
    cal =os.path.join(REPO, "padelpro-vision/calibracao_parada4.json"),
    fps =FPS_P,
    gt  =[38.0,46.8,77.6,95.9,122.4,157.9,178.1,197.0,210.5,229.9,249.6,263.8,289.1]),
 "BARBOSA": dict(
    bola=os.path.join(REPO, "dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"),
    cal =os.path.join(REPO, "padelpro-vision/calibracao_BarbosaMeireles.json"),
    fps =FPS_B,
    gt  =[13.6,33.9,40.3,54.5,69.8,83.3,135.0,155.0,162.9,188.3,196.0,227.2,242.3,
          257.1,298.3,326.1,352.1,367.9,377.9,406.8,526.0]),
}

def carregar(bola, cal_path):
    cal = json.load(open(cal_path))
    ev = lambda c, t: float(sum(cf*t**(len(c)-1-i) for i, cf in enumerate(c)))
    y_rb = lambda x: ev(cal["rede_base_coef"], x)
    y_sp = lambda x: ev(cal["servico_perto_coef"], x)
    y_sl = lambda x: ev(cal["servico_longe_coef"], x)
    def prof(x, y):
        yr = y_rb(x)
        if y > yr: return (y-yr)/max(y_sp(x)-yr, 1)
        return (yr-y)/max(yr-y_sl(x), 1)
    R = {}
    for r in csv.DictReader(open(bola)):
        if int(float(r["Visibility"])):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))
    return R, prof

def kick_kconfirma(R, frames_vis, prof, f_serv, K):
    """Ha um b FUNDO na janela cujas K det. mais proximas ANTES estao todas mais altas
       (desce), e as K mais proximas DEPOIS tambem (sobe)? Devolve (b, prof, span) ou None.
       span = nº de frames entre a K-esima antes e a K-esima depois (a largura real)."""
    j0 = f_serv - int(QUIQUE_JANELA*FPS_P)
    cand = [f for f in frames_vis if j0 <= f <= f_serv]
    melhor = None
    for b in cand:
        xb, yb = R[b]
        if prof(xb, yb) < QUIQUE_PROF:
            continue
        antes = [a for a in frames_vis if a < b][-K:]
        depois = [c for c in frames_vis if c > b][:K]
        if len(antes) < K or len(depois) < K:
            continue
        if all(R[a][1] < yb - DY_MIN for a in antes) and \
           all(R[c][1] < yb - DY_MIN for c in depois):
            span = depois[-1] - antes[0]
            p = prof(xb, yb)
            if melhor is None or p > melhor[1]:
                melhor = (b, p, span)
    return melhor

for nome, v in VIDEOS.items():
    R, prof = carregar(v["bola"], v["cal"])
    fv = sorted(R); n = len(v["gt"])
    print(f"\n===== {nome}  ({n} servicos) =====")
    print("K (frames a descer E a subir) | servicos c/ kick | recall")
    print("-"*58)
    for K in range(1, 5):
        ap = sum(kick_kconfirma(R, fv, prof, int(t*v["fps"]), K) is not None for t in v["gt"])
        star = "  <== K=3" if K == 3 else ""
        print(f"           {K}                |     {ap:2d}/{n:<2d}       |  {100*ap/n:5.1f}%{star}")
    # detalhe a K=3
    print(f"\nDetalhe a K=3 (span = largura real do ressalto, em frames):")
    print(" #  | t(s)  | kick? | frame_b | prof | span")
    print("-"*46)
    for i, t in enumerate(v["gt"], 1):
        m = kick_kconfirma(R, fv, prof, int(t*v["fps"]), 3)
        if m:
            b, p, sp = m
            print(f"{i:2d}  | {t:5.1f} |  SIM  | {b:6d}  | {p:.2f} | {sp:3d} ({sp/v['fps']*1000:.0f}ms)")
        else:
            print(f"{i:2d}  | {t:5.1f} |  NAO  |   -     |  -   |  -")
