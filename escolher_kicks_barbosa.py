#!/usr/bin/env python3
"""Para cada CANDIDATO do detetor de servico (Barbosa), escolhe O kick anterior:
o ULTIMO kick fundo 3+3 nos 3s antes do fim do bloco de formacao (S23: 'so' o ultimo conta').
Grava a lista em JSON para o renderizador."""
import csv, json, os, sys
REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
os.chdir(os.path.join(REPO, "padelpro-vision"))
sys.path.insert(0, ".")
sys.argv = ['x']
import detetor_servico as D

FPS = D.FPS
QUIQUE_PROF, DY_MIN, K, JANELA = 0.7, 1.0, 3, 3.0
CAL = "calibracao_BarbosaMeireles.json"
BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
GT = [13.6,33.9,40.3,54.5,69.8,83.3,135.0,155.0,162.9,188.3,196.0,227.2,242.3,257.1,
      298.3,326.1,352.1,367.9,377.9,406.8,526.0]

cal = json.load(open(CAL))
ev = lambda c, t: float(sum(cf*t**(len(c)-1-i) for i, cf in enumerate(c)))
y_rb = lambda x: ev(cal["rede_base_coef"], x); y_sp = lambda x: ev(cal["servico_perto_coef"], x)
y_sl = lambda x: ev(cal["servico_longe_coef"], x)
def prof(x, y):
    yr = y_rb(x)
    return (y-yr)/max(y_sp(x)-yr,1) if y > yr else (yr-y)/max(yr-y_sl(x),1)

R = {}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])):
        R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))
fv = sorted(R); idx = {f:i for i,f in enumerate(fv)}

def e_kick(b):
    xb, yb = R[b]
    if prof(xb, yb) < QUIQUE_PROF: return False
    i = idx[b]
    if i < K or i+K >= len(fv): return False
    return all(R[a][1] < yb-DY_MIN for a in fv[i-K:i]) and \
           all(R[c][1] < yb-DY_MIN for c in fv[i+1:i+1+K])

def kick_anterior(bloco_b):
    j0 = bloco_b - int(JANELA*FPS)
    cands = [f for f in fv if j0 <= f <= bloco_b and e_kick(f)]
    return max(cands) if cands else None   # o ULTIMO

S, _ = D.servicos('barbosa')
saida = []
for n, (a, b, l) in enumerate(S, 1):
    k = kick_anterior(b)
    t_serv = b / FPS
    real = any(abs(t_serv - g) < 4 for g in GT) or any(a/FPS-1 <= g <= b/FPS+1 for g in GT)
    rec = {"cand": n, "bloco_a": a, "bloco_b": b, "lado": l,
           "t_bloco": round(t_serv,1), "real": real,
           "kick": k, "t_kick": round(k/FPS,2) if k else None,
           "prof": round(prof(*R[k]),2) if k else None,
           "x": round(R[k][0]) if k else None, "y": round(R[k][1]) if k else None}
    saida.append(rec)
    tag = "REAL" if real else "EXTRA"
    kk = f"kick f{k} t={k/FPS:5.1f}s prof={prof(*R[k]):.2f}" if k else "SEM KICK"
    print(f"cand {n:2d} [{tag:5s}] bloco {a/FPS:5.1f}-{b/FPS:5.1f}s ({l:5s}) -> {kk}")

json.dump({"fps": FPS, "kicks": saida}, open("/sessions/eager-serene-wozniak/mnt/outputs/kicks_barbosa.json","w"), indent=1)
com = sum(1 for r in saida if r["kick"])
print(f"\n{com}/{len(saida)} candidatos com kick anterior. JSON gravado.")
