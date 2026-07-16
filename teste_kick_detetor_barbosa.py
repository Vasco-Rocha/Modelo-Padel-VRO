#!/usr/bin/env python3
"""D22 — o kick 3+3 e' um DETETOR ou so' um invariante?  (Barbosa, vasco 16 jul)
Ja' sei que o kick FUNDO 3+3 existe nos 21 servicos (recall 21/21).
AGORA corro-o no VIDEO INTEIRO e conto quantas vezes dispara — e quantas FORA de servico.
   NECESSARIO (esta nos servicos) != SUFICIENTE (so' nos servicos).  NAO toca no pipeline."""
import csv, json, os

REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
BOLA = os.path.join(REPO, "dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv")
CAL  = os.path.join(REPO, "padelpro-vision/calibracao_BarbosaMeireles.json")
FPS  = 29.97002997002997
QUIQUE_PROF = 0.7
DY_MIN = 1.0
K = 3

# 21 servicos (inicio) e fins de rally, para classificar cada kick
GT = [(13.6,23.7),(33.9,37.3),(40.3,44.7),(54.5,62.4),(69.8,73.6),(83.3,96.0),
      (135.0,139.1),(155.0,157.6),(162.9,171.8),(188.3,192.2),(196.0,202.0),
      (227.2,230.8),(242.3,245.4),(257.1,266.0),(298.3,306.8),(326.1,337.3),
      (352.1,357.3),(367.9,371.1),(377.9,384.3),(406.8,416.1),(526.0,533.9)]
INICIOS = [a for a, _ in GT]

cal = json.load(open(CAL))
ev = lambda c, t: float(sum(cf*t**(len(c)-1-i) for i, cf in enumerate(c)))
y_rb = lambda x: ev(cal["rede_base_coef"], x)
y_sp = lambda x: ev(cal["servico_perto_coef"], x)
y_sl = lambda x: ev(cal["servico_longe_coef"], x)
def prof(x, y):
    yr = y_rb(x)
    if y > yr: return (y-yr)/max(y_sp(x)-yr, 1)
    return (yr-y)/max(yr-y_sl(x), 1)

R = {}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])):
        R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))
fv = sorted(R)
idx = {f: i for i, f in enumerate(fv)}

def e_kick(b):
    xb, yb = R[b]
    if prof(xb, yb) < QUIQUE_PROF:
        return False
    i = idx[b]
    if i < K or i + K >= len(fv):
        return False
    antes = fv[i-K:i]; depois = fv[i+1:i+1+K]
    return all(R[a][1] < yb - DY_MIN for a in antes) and \
           all(R[c][1] < yb - DY_MIN for c in depois)

# todos os kicks no video inteiro
kicks = [b for b in fv if e_kick(b)]
# agrupar (kicks a <=5 frames = o mesmo ressalto)
grupos = []
for b in kicks:
    if grupos and b - grupos[-1][-1] <= 5:
        grupos[-1].append(b)
    else:
        grupos.append([b])
eventos = [g[0] for g in grupos]

def classifica(f):
    t = f / FPS
    # dentro de um rally do GT?
    for a, b in GT:
        if a <= t <= b:
            return "RALLY"
    # nos 3s antes de um servico? (onde vive o kick do servico)
    for a in INICIOS:
        if a - 3.0 <= t < a:
            return "PRE-SERVICO"
    return "INTERVALO"

from collections import Counter
c = Counter(classifica(f) for f in eventos)
dur_video = fv[-1] / FPS

print(f"Video: {dur_video:.0f}s ({fv[-1]} frames, {len(fv)} bola visivel)")
print(f"Kicks FUNDOS 3+3 no video inteiro: {len(eventos)} eventos "
      f"({len(eventos)/dur_video*60:.1f} por minuto)\n")
print("Onde caem os", len(eventos), "kicks:")
for k in ("PRE-SERVICO", "RALLY", "INTERVALO"):
    print(f"   {k:12s}: {c.get(k,0):3d}  ({100*c.get(k,0)/len(eventos):4.1f}%)")

# quantos servicos tem um kick nos 3s antes (recall, sanity)
tem = sum(any(a-3.0 <= f/FPS < a for f in eventos) for a in INICIOS)
print(f"\nSanity: servicos com >=1 kick nos 3s antes: {tem}/21")

# a metrica que importa: se eu usar 'ha kick fundo 3+3' como detetor de servico,
# quantos FALSOS (fora de pre-servico) tenho por cada servico verdadeiro?
falsos = c.get("RALLY",0) + c.get("INTERVALO",0)
print(f"\nD22 — se 'kick fundo 3+3' fosse o detetor de servico:")
print(f"   candidatos totais : {len(eventos)}")
print(f"   em zona de servico: {c.get('PRE-SERVICO',0)}")
print(f"   FALSOS (rally+intervalo): {falsos}   ->  {falsos/max(c.get('PRE-SERVICO',0),1):.1f} falsos por bom")
