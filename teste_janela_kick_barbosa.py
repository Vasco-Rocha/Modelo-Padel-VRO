#!/usr/bin/env python3
"""TESTE (Vasco, 16 jul) — o MESMO teste do kick, agora no BARBOSA (21 servicos).
Mesma logica, mesmos numeros do pipeline (DY_MIN, QUIQUE_JANELA, QUIQUE_PROF).
Bola/calib/GT do Barbosa. NAO toca no pipeline."""
import csv, json, os

REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
BOLA = os.path.join(REPO, "dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv")
CAL  = os.path.join(REPO, "padelpro-vision/calibracao_BarbosaMeireles.json")

FPS           = 29.97002997002997
QUIQUE_JANELA = 3.0
QUIQUE_PROF   = 0.7
DY_MIN        = 1.0

# 21 servicos = inicio de cada rally (GT_VASCO, avaliar_barbosa.py, 13 jul)
GT_INICIOS = [13.6, 33.9, 40.3, 54.5, 69.8, 83.3, 135.0, 155.0, 162.9, 188.3, 196.0,
              227.2, 242.3, 257.1, 298.3, 326.1, 352.1, 367.9, 377.9, 406.8, 526.0]

cal = json.load(open(CAL))
ev = lambda c, t: float(sum(cf * t**(len(c)-1-i) for i, cf in enumerate(c)))
y_rb = lambda x: ev(cal["rede_base_coef"], x)
y_sp = lambda x: ev(cal["servico_perto_coef"], x)
y_sl = lambda x: ev(cal["servico_longe_coef"], x)

def prof(x, y):
    yr = y_rb(x)
    if y > yr:
        return (y - yr) / max(y_sp(x) - yr, 1)
    return (yr - y) / max(yr - y_sl(x), 1)

R = {}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])):
        R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))

frames_vis = sorted(R)
print(f"Bola: {len(frames_vis)} frames visiveis de {frames_vis[-1]} totais "
      f"({100*len(frames_vis)/frames_vis[-1]:.1f}% de cobertura)\n")

def kick_na_janela(f_serv, gap):
    j0 = f_serv - int(QUIQUE_JANELA * FPS)
    cand = [f for f in frames_vis if j0 <= f <= f_serv]
    melhor = None
    for b in cand:
        xb, yb = R[b]
        if prof(xb, yb) < QUIQUE_PROF:
            continue
        antes = [a for a in frames_vis if 0 < b - a <= gap and R[a][1] < yb - DY_MIN]
        depois = [c for c in frames_vis if 0 < c - b <= gap and R[c][1] < yb - DY_MIN]
        if antes and depois:
            ga = b - max(antes); gd = min(depois) - b
            prof_b = prof(xb, yb)
            if melhor is None or prof_b > melhor[1]:
                melhor = (b, prof_b, ga, gd)
    return melhor

print("GAP (frames) | servicos c/ kick | recall")
print("-" * 45)
gap_todos = None
for gap in range(1, 31):
    apanha = sum(kick_na_janela(int(t*FPS), gap) is not None for t in GT_INICIOS)
    marca = f"  <-- {apanha}/21" if apanha == 21 and gap_todos is None else ""
    if apanha == 21 and gap_todos is None:
        gap_todos = gap
    print(f"    {gap:3d}      |      {apanha:2d}/21       |  {100*apanha/21:5.1f}%{marca}")

print(f"\n>>> GAP minimo para 21/21: {gap_todos} frames ({gap_todos/FPS*1000:.0f} ms)\n"
      if gap_todos else "\n>>> NUNCA chega a 21/21 mesmo com 30 frames\n")

print("Detalhe por servico (GAP=30, o mais generoso):")
print(" #  | t(s)  | kick? | frame_b | prof | gap_antes | gap_depois")
print("-" * 66)
for i, t in enumerate(GT_INICIOS, 1):
    m = kick_na_janela(int(t*FPS), 30)
    if m:
        b, p, ga, gd = m
        print(f"{i:2d}  | {t:5.1f} |  SIM  | {b:6d}  | {p:.2f} |   {ga:3d}     |   {gd:3d}")
    else:
        print(f"{i:2d}  | {t:5.1f} |  NAO  |   -     |  -   |    -      |    -")
