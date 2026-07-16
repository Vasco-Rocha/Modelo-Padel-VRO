#!/usr/bin/env python3
"""Quanto encurtou CADA cauda com a S42? Corre o MESMO pipeline com a regra OFF e ON.
NAO altera nada. So mede."""
import sys, os, json, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_tempo_util as gt

VIDEO = sys.argv[1] if len(sys.argv) > 1 else "parada4"

if VIDEO == "barbosa":
    gt.FPS = 29.97002997002997
    gt.N_FRAMES = 16138
    gt.BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
    gt.BOXES = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl"
    gt.CAL = "calibracao_BarbosaMeireles.json"
    gt.GT = []
FPS = gt.FPS


def correr():
    R, prof = gt.carregar()
    R = gt.vai_e_vem(R)
    tks = gt.tracklets(R)
    CR = gt.cruzamentos(R, tks, prof)
    cal = json.load(open(gt.CAL))
    boxes = pickle.load(open(gt.BOXES, "rb"))["player_boxes"]
    PAN = gt.pancadas(R, cal, boxes)
    FIM = gt.fim_certo(R, cal, boxes)
    RES = gt.ressaltos(R, tks)
    return gt.rallies(CR, PAN, FIM, RES, R, prof)


gt.REGRAS["S42_CONFIRMA_FIM"] = False
OFF = correr()
gt.REGRAS["S42_CONFIRMA_FIM"] = True
ON = correr()

print(f"=== {VIDEO.upper()} — quanto encurtou a CAUDA ===")
print(f"{'#':>3} {'inicio':>8} {'fim OFF':>9} {'fim ON':>9} {'delta':>8}")
tot = 0.0
n = 0
for i, (o, m) in enumerate(zip(OFF, ON), 1):
    d = (m[1] - o[1]) / FPS
    tot += d
    if abs(d) > 0.01:
        n += 1
    flag = "  <<<" if d < -1.5 else ""
    print(f"{i:>3} {o[0]/FPS:>7.1f}s {o[1]/FPS:>8.1f}s {m[1]/FPS:>8.1f}s {d:>+7.1f}s{flag}")
print("-" * 48)
tu_o = sum(b - a for a, b in OFF) / FPS
tu_m = sum(b - a for a, b in ON) / FPS
print(f"segmentos: {len(OFF)} -> {len(ON)}   ({n} caudas mexeram, {len(OFF)-n} ficaram iguais)")
print(f"tempo util: {tu_o:.1f}s -> {tu_m:.1f}s   ({tu_m-tu_o:+.1f}s,  {100*(tu_m-tu_o)/tu_o:+.1f}%)")
print(f"cauda media encurtada: {tot/max(n,1):.1f}s  (nas que mexeram)")
