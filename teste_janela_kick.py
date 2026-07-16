#!/usr/bin/env python3
"""
TESTE (Vasco, 16 jul): quantos FRAMES de janela preciso para apanhar SEMPRE o kick
(a inversao VERTICAL da bola no chao) antes da raquete, nos servicos conhecidos?

⚠️ NAO toca no pipeline. Le a MESMA bola (traj thr04) e a MESMA calibracao (prof).
⚠️ Os servicos = os 13 inicios de rally do ground_truth_parada4 (a raquetada do servico).
   O kick esta ANTES desse instante, dentro da janela de 3s (QUIQUE_JANELA do pipeline).

O que varia (a tua ideia): o GAP maximo, em frames, entre o ponto de quique 'b' e as
deteccoes que o suportam (uma a DESCER antes, uma a SUBIR depois). GAP=1 = frames
consecutivos (o que o codigo quase exige). Aumentar o GAP = "contar mais frames".
"""
import csv, json, math, os

REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos/padelpro-vision"
BOLA = os.path.join(REPO, "data/parada4/traj_frames_Parada4_thr04.csv")
CAL  = os.path.join(REPO, "calibracao_parada4.json")

FPS           = 29.97
QUIQUE_JANELA = 3.0    # s antes do servico onde procurar o kick (igual ao pipeline)
QUIQUE_PROF   = 0.7    # "fundo" = na linha de servico ou atras (igual ao pipeline)
DY_MIN        = 1.0    # px de descida/subida da inversao (igual ao pipeline)

# 13 servicos = inicio de cada rally (ground_truth_parada4.md)
GT_INICIOS = [38.0, 46.8, 77.6, 95.9, 122.4, 157.9, 178.1, 197.0,
              210.5, 229.9, 249.6, 263.8, 289.1]

# ---------- carregar bola + prof (copia fiel do gerar_tempo_util) ----------
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
    """Ha um kick (Y local-max, fundo) na janela [f_serv-3s, f_serv],
       suportado por uma det. a DESCER <=gap antes e uma a SUBIR <=gap depois?
       Devolve (frame_b, prof_b, gap_antes, gap_depois) do melhor, ou None."""
    j0 = f_serv - int(QUIQUE_JANELA * FPS)
    cand = [f for f in frames_vis if j0 <= f <= f_serv]
    melhor = None
    for b in cand:
        xb, yb = R[b]
        if prof(xb, yb) < QUIQUE_PROF:          # tem de ser FUNDO
            continue
        # deteccao a DESCER para b: existe a<b, a>=b-gap*passo, com Y menor (mais alto)
        antes = [a for a in frames_vis if 0 < b - a <= gap and R[a][1] < yb - DY_MIN]
        depois = [c for c in frames_vis if 0 < c - b <= gap and R[c][1] < yb - DY_MIN]
        if antes and depois:
            ga = b - max(antes)     # gap real ao vizinho descendente
            gd = min(depois) - b    # gap real ao vizinho ascendente
            prof_b = prof(xb, yb)
            if melhor is None or prof_b > melhor[1]:
                melhor = (b, prof_b, ga, gd)
    return melhor

# ---------- 1) VARREDURA: quantos servicos com kick por GAP ----------
print("GAP (frames) | servicos c/ kick | recall")
print("-" * 45)
gap_para_todos = None
for gap in range(1, 31):
    apanha = sum(kick_na_janela(int(t*FPS), gap) is not None for t in GT_INICIOS)
    marca = "  <-- 13/13" if apanha == 13 and gap_para_todos is None else ""
    if apanha == 13 and gap_para_todos is None:
        gap_para_todos = gap
    print(f"    {gap:3d}      |      {apanha:2d}/13       |  {100*apanha/13:5.1f}%{marca}")

print(f"\n>>> GAP minimo para 13/13: {gap_para_todos} frames "
      f"({gap_para_todos/FPS*1000:.0f} ms)\n" if gap_para_todos else
      "\n>>> NUNCA chega a 13/13 mesmo com 30 frames de janela\n")

# ---------- 2) DETALHE por servico (com janela generosa) ----------
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
