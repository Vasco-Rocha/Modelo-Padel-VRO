#!/usr/bin/env python3
"""TESTE (Vasco, 16 jul): o kick tem de estar PERTO DA BOX DO SERVIDOR.
O detetor ja' diz o LADO que serve e o SERVIDOR (o atrasado da equipa que serve, que corre
para a rede depois). Re-escolho o kick como o mais PROXIMO do servidor, em MEIOS-CAMPOS locais
(nunca pixeis). Comparo com o pick antigo (ultimo kick, sem restricao)."""
import csv, json, os, sys, math
REPO = "/sessions/eager-serene-wozniak/mnt/Treino de Modelo de análise - Com Joao Santos"
os.chdir(os.path.join(REPO, "padelpro-vision")); sys.path.insert(0, "."); sys.argv = ['x']
import detetor_servico as D
import cascata_jogadores as C

FPS = D.FPS
QUIQUE_PROF, DY_MIN, K, JANELA = 0.7, 1.0, 3, 3.0
CAL = "calibracao_BarbosaMeireles.json"
BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
GT = [13.6,33.9,40.3,54.5,69.8,83.3,135.0,155.0,162.9,188.3,196.0,227.2,242.3,257.1,
      298.3,326.1,352.1,367.9,377.9,406.8,526.0]

cal = json.load(open(CAL))
ev = lambda c,t: float(sum(cf*t**(len(c)-1-i) for i,cf in enumerate(c)))
y_rb=lambda x:ev(cal["rede_base_coef"],x); y_sp=lambda x:ev(cal["servico_perto_coef"],x)
y_sl=lambda x:ev(cal["servico_longe_coef"],x)
def prof(x,y):
    yr=y_rb(x); return (y-yr)/max(y_sp(x)-yr,1) if y>yr else (yr-y)/max(yr-y_sl(x),1)

R={}
for r in csv.DictReader(open(BOLA)):
    if int(float(r["Visibility"])): R[int(r["Frame"])]=(float(r["X"]),float(r["Y"]))
fv=sorted(R); idx={f:i for i,f in enumerate(fv)}
def e_kick(b):
    xb,yb=R[b]
    if prof(xb,yb)<QUIQUE_PROF: return False
    i=idx[b]
    if i<K or i+K>=len(fv): return False
    return all(R[a][1]<yb-DY_MIN for a in fv[i-K:i]) and all(R[c][1]<yb-DY_MIN for c in fv[i+1:i+1+K])

pb=D.cascata('barbosa')                 # boxes por frame (cascata J1-J5)
C.configurar('barbosa')

def servidor_em(f, l):
    """box do servidor no frame f (ou no mais proximo com a equipa 'l' visivel)."""
    for df in range(0, 30):
        for ff in (f-df, f+df):
            if 0<=ff<len(pb):
                s=D.servidor(pb[ff], l)
                if s: return s
    return None

def dist_hc(kf, l):
    """distancia do kick ao servidor em MEIOS-CAMPOS locais (no sitio do kick)."""
    s=servidor_em(kf,l)
    if not s: return None
    xk,yk=R[kf]; xs,ys=C.pes(s)
    return math.hypot(xk-xs, yk-ys)/max(C.meio_campo_px(xk,yk),1)

S,_=D.servicos('barbosa')
saida=[]; print(f"{'cand':>4} {'tag':6} {'lado':5} | {'ANTIGO (ultimo)':>22} | {'NOVO (perto servidor)':>26}")
print("-"*84)
for n,(a,b,l) in enumerate(S,1):
    j0=b-int(JANELA*FPS)
    ks=[f for f in fv if j0<=f<=b and e_kick(f)]
    real=any(abs(b/FPS-g)<4 for g in GT) or any(a/FPS-1<=g<=b/FPS+1 for g in GT)
    tag="REAL" if real else "EXTRA"
    # antigo: o ultimo
    old=max(ks) if ks else None
    old_d=dist_hc(old,l) if old else None
    # novo: o mais PROXIMO do servidor
    kd=[(f,dist_hc(f,l)) for f in ks]; kd=[(f,d) for f,d in kd if d is not None]
    new,new_d=min(kd,key=lambda t:t[1]) if kd else (None,None)
    def fmt(f,d): return f"t={f/FPS:5.1f} d={d:4.1f}mc pf={prof(*R[f]):.2f}" if f else "—"
    print(f"{n:>4} {tag:6} {l:5} | {fmt(old,old_d):>22} | {fmt(new,new_d):>26}")
    saida.append({"cand":n,"bloco_a":a,"bloco_b":b,"lado":l,"real":real,
                  "t_bloco":round(b/FPS,1),"kick":new,"t_kick":round(new/FPS,2) if new else None,
                  "prof":round(prof(*R[new]),2) if new else None,"dist_mc":round(new_d,2) if new_d else None,
                  "x":round(R[new][0]) if new else None,"y":round(R[new][1]) if new else None,
                  "sx":round(C.pes(servidor_em(new,l))[0]) if new and servidor_em(new,l) else None,
                  "sy":round(C.pes(servidor_em(new,l))[1]) if new and servidor_em(new,l) else None})
json.dump({"fps":FPS,"kicks":saida},open("/sessions/eager-serene-wozniak/mnt/outputs/kicks_barbosa_servidor.json","w"),indent=1)

# sweep de limiar: quantos REAIS ficam, quantos EXTRAS caem
print("\nlimiar (mc) | REAIS c/ kick perto | EXTRAS c/ kick perto")
print("-"*54)
for thr in [0.5,0.75,1.0,1.5,2.0,3.0]:
    reais=sum(1 for r in saida if r["real"] and r["dist_mc"] is not None and r["dist_mc"]<=thr)
    extras=sum(1 for r in saida if not r["real"] and r["dist_mc"] is not None and r["dist_mc"]<=thr)
    print(f"   {thr:4.2f}     |      {reais:2d}/21           |      {extras}/2")
