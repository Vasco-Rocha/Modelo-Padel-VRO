#!/usr/bin/env python3
"""Desenha, para cada candidato do detetor, o KICK anterior ao servico no video do Barbosa.
Verde = 3 frames a DESCER · circulo grande = o KICK fundo · Azul = 3 frames a SUBIR.
Legenda: candidato, REAL/EXTRA, tempo do servico, lado, prof do kick."""
import csv, json, cv2, numpy as np, os
REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
VIDEO = os.path.join(REPO, "BarbosaMeireles.mp4")
OUT   = "/sessions/eager-serene-wozniak/mnt/outputs/KICKS_servico_Barbosa_raw.mp4"
BOLA  = os.path.join(REPO, "dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv")
d = json.load(open("/sessions/eager-serene-wozniak/mnt/outputs/kicks_barbosa.json"))
FPS = d["fps"]; KICKS = d["kicks"]

R = {}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])):
        R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]))
fv = sorted(R); idx = {f:i for i,f in enumerate(fv)}

ANTES, DEPOIS, HOLD = 20, 16, 10   # frames de contexto e de pausa no kick
cap = cv2.VideoCapture(VIDEO)
W, H = int(cap.get(3)), int(cap.get(4))
vw = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
F = cv2.FONT_HERSHEY_SIMPLEX

def bola_em(f):
    return (int(R[f][0]), int(R[f][1])) if f in R else None

def desenha(img, rec, f_atual):
    k = rec["kick"]; i = idx[k]
    antes3 = fv[i-3:i]; depois3 = fv[i+1:i+4]
    # trilho: bolas detetadas na vizinhanca ate' ao frame atual
    viz = [f for f in fv if k-ANTES <= f <= f_atual]
    for f in viz:
        p = bola_em(f)
        if not p: continue
        if f in antes3:   cor, rad = (80,230,80), 6      # verde = a descer
        elif f in depois3:cor, rad = (240,180,60), 6     # azul  = a subir
        elif f == k:      cor, rad = (0,215,255), 11     # amarelo = o KICK
        else:             cor, rad = (200,200,200), 3
        cv2.circle(img, p, rad, cor, 2 if f != k else 3)
    # o KICK em destaque quando ja' passou
    if f_atual >= k:
        pk = bola_em(k)
        if pk:
            cv2.circle(img, pk, 16, (0,215,255), 2)
            cv2.putText(img, "KICK", (pk[0]+18, pk[1]-8), F, 0.7, (0,215,255), 2)
    # banner
    tag = "REAL" if rec["real"] else "EXTRA (falso do detetor)"
    cor_tag = (120,255,120) if rec["real"] else (100,140,255)
    cv2.rectangle(img, (0,0), (W,70), (0,0,0), -1)
    cv2.putText(img, f"Servico {rec['cand']}/23   [{tag}]", (15,28), F, 0.8, cor_tag, 2)
    cv2.putText(img, f"serve t={rec['t_bloco']}s  lado={rec['lado']}   "
                     f"KICK t={rec['t_kick']}s  prof={rec['prof']}  (3 desce / 3 sobe)",
                (15,56), F, 0.6, (230,230,230), 1)

for rec in KICKS:
    k = rec["kick"]
    cap.set(cv2.CAP_PROP_POS_FRAMES, k-ANTES)   # UM seek por clip
    for f in range(k-ANTES, k+DEPOIS+1):
        ok, img = cap.read()                    # depois, leitura sequencial (rapida)
        if not ok: break
        desenha(img, rec, f)
        vw.write(img)
        if f == k:
            for _ in range(HOLD): vw.write(img)
cap.release(); vw.release()
print("OK", OUT, os.path.getsize(OUT)//1024, "KB")
