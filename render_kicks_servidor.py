#!/usr/bin/env python3
"""Re-desenha os kicks COM A RESTRICAO do servidor. Marca o servidor, a linha ate' ao kick
com a distancia em meios-campos, e pinta o KICK de VERDE (<=2mc, confirmado) ou VERMELHO
(rejeitado). Video do Barbosa."""
import csv, json, cv2, os, math
REPO="/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
VIDEO=os.path.join(REPO,"BarbosaMeireles.mp4")
OUT="/sessions/eager-serene-wozniak/mnt/outputs/KICKS_perto_servidor_Barbosa_raw.mp4"
BOLA=os.path.join(REPO,"dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv")
d=json.load(open("/sessions/eager-serene-wozniak/mnt/outputs/kicks_barbosa_servidor.json"))
FPS=d["fps"]; KICKS=d["kicks"]; THR=2.0

R={}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])): R[int(r["Frame"])]=(float(r["X"]),float(r["Y"]))
fv=sorted(R); idx={f:i for i,f in enumerate(fv)}
ANTES,DEPOIS,HOLD=20,16,12
cap=cv2.VideoCapture(VIDEO); W,H=int(cap.get(3)),int(cap.get(4))
vw=cv2.VideoWriter(OUT,cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
F=cv2.FONT_HERSHEY_SIMPLEX
def bola(f): return (int(R[f][0]),int(R[f][1])) if f in R else None

def desenha(img,rec,fa):
    k=rec["kick"]; i=idx[k]; conf=rec["dist_mc"] is not None and rec["dist_mc"]<=THR
    cork=(80,230,80) if conf else (60,60,240)
    antes3,depois3=fv[i-3:i],fv[i+1:i+4]
    for f in [x for x in fv if k-ANTES<=x<=fa]:
        p=bola(f)
        if not p: continue
        if f in antes3: c,r=(80,230,80),6
        elif f in depois3: c,r=(240,180,60),6
        elif f==k: c,r=cork,11
        else: c,r=(200,200,200),3
        cv2.circle(img,p,r,c,2)
    # servidor + linha
    if rec.get("sx") is not None:
        sp=(rec["sx"],rec["sy"])
        cv2.drawMarker(img,sp,(255,120,255),cv2.MARKER_TRIANGLE_UP,22,2)
        cv2.putText(img,"servidor",(sp[0]-30,sp[1]+22),F,0.5,(255,120,255),1)
        if fa>=k and bola(k):
            cv2.line(img,bola(k),sp,(255,120,255),1)
            mx,my=(bola(k)[0]+sp[0])//2,(bola(k)[1]+sp[1])//2
            cv2.putText(img,f"{rec['dist_mc']}mc",(mx+4,my),F,0.55,(255,120,255),2)
    if fa>=k and bola(k):
        cv2.circle(img,bola(k),16,cork,2)
        cv2.putText(img,"KICK" if conf else "KICK REJEITADO",(bola(k)[0]+18,bola(k)[1]-8),F,0.7,cork,2)
    tag="REAL" if rec["real"] else "EXTRA"
    st="CONFIRMADO" if conf else "REJEITADO (kick longe do servidor)"
    cor=(120,255,120) if conf else (100,140,255)
    cv2.rectangle(img,(0,0),(W,70),(0,0,0),-1)
    cv2.putText(img,f"Servico {rec['cand']}/23  [{tag}]  ->  {st}",(15,28),F,0.8,cor,2)
    cv2.putText(img,f"serve t={rec['t_bloco']}s lado={rec['lado']}  KICK t={rec['t_kick']}s "
                    f"prof={rec['prof']}  dist ao servidor={rec['dist_mc']} meios-campos",
                (15,56),F,0.58,(230,230,230),1)

for rec in KICKS:
    k=rec["kick"]; cap.set(cv2.CAP_PROP_POS_FRAMES,k-ANTES)
    for f in range(k-ANTES,k+DEPOIS+1):
        ok,img=cap.read()
        if not ok: break
        desenha(img,rec,f); vw.write(img)
        if f==k:
            for _ in range(HOLD): vw.write(img)
cap.release(); vw.release(); print("OK",OUT,os.path.getsize(OUT)//1024,"KB")
