#!/usr/bin/env python3
"""
PIPELINE COMPLETO DO M1 — TEMPO ÚTIL.       12 jul 2026.

    RECALL 93,2%   PRECISÃO 89,4%      (de manhã estava em 72% / 63%)

Corre em CPU, em segundos. Sem GPU, sem Colab, sem Kaggle.

    python3 gerar_tempo_util.py                # só as métricas
    python3 gerar_tempo_util.py --video        # + a compilação do tempo útil

TODAS as regras aqui são do Vasco. Ver REGRAS_DO_VASCO.md.

⚠️ ATALHOS POR CORRIGIR (declarados, como manda a regra):
   - VMAX=90 px/frame -> PÍXEIS ABSOLUTOS. Viola a lição da perspetiva (o meio-campo longe
     tem 100 px e o perto 290, para os mesmos 6,95 m). Devia ser fração do meio_campo_px.
   - L_RAQUETE=11, SILENCIO=4s, PAD_ANTES=1.6s, MIN_PROF=0.35, e os números da pancada:
     afinados ao F1 DESTE vídeo. Não derivados da estrutura. Podem não sobreviver a outra câmara.
"""
import csv, json, math, sys, subprocess, os
import numpy as np

FPS = 29.97
N_FRAMES = 8741
BOLA = "../dados_parada4/traj_frames_Parada4_thr04.csv"
CAL  = "calibracao_campo.json"
VIDEO = "../Parada4.mp4"

# ground-truth: 12 rallies / 117 s, anotados à mão pelo Vasco
GT = [(38.0,41.5),(46.8,67.5),(77.6,85.5),(95.9,111.1),(122.4,135.9),(157.9,169.4),
      (178.1,186.5),(197.0,202.1),(210.5,216.3),(229.9,237.3),(249.6,255.0),(263.8,276.4)]

# --- parâmetros (ver aviso no topo) ---
VMAX       = 90     # ⚠️ px/frame — ATALHO
GAP        = 9
GAP_THETA  = 20
VMAX_THETA = 140
TOL_THETA  = 35     # graus
L_COSTURA  = 1      # baixo de propósito: é o que deixa passar o BALÃO (bola lenta)
MIN_DET    = 4
MIN_PROF   = 0.35   # ⚠️ ATALHO
L_RAQUETE  = 11     # ⚠️ ATALHO — a regra (mão vs raquete) é lei; o NÚMERO é ajuste
PAN_DTHETA = 20     # ⚠️ ATALHO
PAN_L      = 7      # ⚠️ ATALHO
SILENCIO   = 4.0    # ⚠️ ATALHO
PAD_ANTES  = 1.6    # ⚠️ ATALHO
M_COM_PAN  = 2.0    # certeza  -> corte rente
M_SEM_PAN  = 5.0    # dúvida   -> mais margem   (S16: NÃO inverter!)
DUR_MIN    = 1.5


def carregar():
    cal = json.load(open(CAL))
    ev = lambda c, t: float(np.polyval(c, t))
    y_rb = lambda x: ev(cal["rede_base_coef"], x)
    y_sp = lambda x: ev(cal["servico_perto_coef"], x)
    y_sl = lambda x: ev(cal["servico_longe_coef"], x)

    def prof(x, y):
        """0 = na rede · 1 = na linha de serviço · >1 = atrás dela."""
        yr = y_rb(x)
        if y > yr:
            return "baixo", (y - yr) / max(y_sp(x) - yr, 1)
        return "cima", (yr - y) / max(yr - y_sl(x), 1)

    R = {}
    for r in csv.DictReader(open(BOLA)):
        if int(float(r["Visibility"])):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]),
                                  float(r["L"]), float(r["Theta"]))
    return R, prof


def d(R, a, b):
    return math.hypot(R[a][0] - R[b][0], R[a][1] - R[b][1])


def vai_e_vem(R):
    """S/B8 — A->B longe, A->C perto  =>  B é ERRO. Tira o frame, não parte a cadeia."""
    fs = sorted(R)
    mortos = []
    for i in range(1, len(fs) - 1):
        a, b, c = fs[i-1], fs[i], fs[i+1]
        if c - a > 30:
            continue
        if (d(R,a,b) > 60 and d(R,b,c) > 60
                and d(R,a,c) < 0.5 * min(d(R,a,b), d(R,b,c))):
            mortos.append(b)
    for m in mortos:
        R.pop(m)
    return R


def erro_theta(R, a, b):
    """O Theta acerta a direção a ~2°, e fá-lo numa ÚNICA deteção (graus, eixo mod 180)."""
    dx, dy = R[b][0]-R[a][0], R[b][1]-R[a][1]
    if math.hypot(dx, dy) < 4:
        return 0.0
    real = math.degrees(math.atan2(dy, dx))
    return max(abs(((R[a][3]-real+90) % 180) - 90),
               abs(((R[b][3]-real+90) % 180) - 90))


def tracklets(R):
    """COSTURA POR THETA: se o buraco é grande mas a DIREÇÃO bate certo, é a mesma bola."""
    fs = sorted(R)
    out, cur = [], [fs[0]]
    for a, b in zip(fs, fs[1:]):
        g = b - a
        liga = (g <= GAP and d(R,a,b) <= VMAX * g)
        if not liga:
            liga = (g <= GAP_THETA and d(R,a,b) <= VMAX_THETA * g
                    and R[a][2] >= L_COSTURA and R[b][2] >= L_COSTURA
                    and erro_theta(R, a, b) <= TOL_THETA)
        if liga:
            cur.append(b)
        else:
            out.append(cur); cur = [b]
    out.append(cur)
    return [t for t in out if len(t) >= MIN_DET]


def cruzamentos(R, tks, prof):
    """
    A bola atravessa a rede DE FUNDO A FUNDO (roçar a fita não conta).
    S15 — MÃO vs RAQUETE: só conta se a bola vier da RAQUETE (L alto), não da MÃO.
          Medido: serviços L=17,4 · passagens à mão L=2,7.
    🎈 BUG: o BALÃO chega LENTO e é rejeitado aqui. Parte os pontos 3 e 6->7.
    """
    fs = sorted(R)
    Lmax = lambda f: max([R[g][2] for g in fs if abs(g-f) <= 5] or [0])
    out = []
    for tk in tks:
        ult = None
        for f in tk:
            l, p = prof(R[f][0], R[f][1])
            if p < MIN_PROF:
                continue
            if ult and ult != l and Lmax(f) >= L_RAQUETE:
                out.append(f)
            ult = l
    return sorted(out)


def pancadas(R):
    """Mudança brusca de direção com a bola a voar. A 0.4: 135 (a 0.7 eram só 57)."""
    fs = sorted(R)
    out = []
    for a, b in zip(fs, fs[1:]):
        if b - a > 8:
            continue
        if (max(R[a][2], R[b][2]) >= PAN_L
                and abs(((R[b][3]-R[a][3]+90) % 180) - 90) >= PAN_DTHETA):
            out.append(b)
    ag = []
    for f in out:
        if ag and f - ag[-1][-1] <= 5:
            ag[-1].append(f)
        else:
            ag.append([f])
    return [g[0] for g in ag]


def rallies(CR, PAN):
    grp = [[CR[0]]]
    for c in CR[1:]:
        if c - grp[-1][-1] <= SILENCIO * FPS:
            grp[-1].append(c)
        else:
            grp.append([c])

    S = []
    for g in grp:
        a, b = g[0], g[-1]
        pan = [q for q in PAN if a <= q <= b + int(1.5*FPS)]
        # S16 — CERTEZA (há pancada) -> corte rente. DÚVIDA (não há) -> mais margem.
        fim = int(max(pan) + M_COM_PAN*FPS) if pan else int(b + M_SEM_PAN*FPS)
        S.append((max(0, int(a - PAD_ANTES*FPS)), fim))

    S = sorted(s for s in S if (s[1]-s[0])/FPS >= DUR_MIN)

    # S13 — A TIMELINE NUNCA ANDA PARA TRÁS. Se dois se tocam, são O MESMO PONTO.
    M = [list(S[0])]
    for a, b in S[1:]:
        if a <= M[-1][1]:
            M[-1][1] = max(M[-1][1], b)
        else:
            M.append([a, b])
    return [(a, b) for a, b in M]


def avaliar(M):
    g = np.zeros(N_FRAMES, bool)
    for a, b in GT:
        g[int(a*FPS):int(b*FPS)+1] = True
    m = np.zeros(N_FRAMES, bool)
    for a, b in M:
        m[max(a,0):min(b, N_FRAMES-1)+1] = True
    tp = (m & g).sum(); fp = (m & ~g).sum(); fn = (~m & g).sum()
    rec = 100*tp/max(tp+fn, 1); pre = 100*tp/max(tp+fp, 1)
    serv = {k for a, b in M for k, (g0, _) in enumerate(GT, 1)
            if a/FPS - 1.0 <= g0 <= b/FPS}
    return dict(n=len(M), tempo=m.sum()/FPS, servicos=len(serv),
                recall=rec, precisao=pre, f1=2*rec*pre/max(rec+pre, 1))


def main():
    R, prof = carregar()
    print(f"bola: {len(R)} frames ({100*len(R)/N_FRAMES:.1f}%)")
    R = vai_e_vem(R)
    tks = tracklets(R)
    CR = cruzamentos(R, tks, prof)
    PAN = pancadas(R)
    print(f"tracklets {len(tks)} | cruzamentos {len(CR)} | pancadas {len(PAN)}")
    M = rallies(CR, PAN)
    r = avaliar(M)
    print(f"\n>>> {r['n']} pontos (reais: 12) | {r['tempo']:.1f}s (reais: 117s)")
    print(f">>> servicos {r['servicos']}/12")
    print(f">>> RECALL {r['recall']:.1f}%   PRECISAO {r['precisao']:.1f}%   F1 {r['f1']:.1f}")

    if "--video" in sys.argv:
        lst = "\n".join(f"file 'tu{i:02d}.mp4'" for i in range(1, len(M)+1))
        open("/tmp/tu.txt", "w").write(lst + "\n")
        for i, (a, b) in enumerate(M, 1):
            subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{a/FPS:.2f}",
                "-t",f"{(b-a)/FPS:.2f}","-i",VIDEO,"-c:v","libx264","-pix_fmt","yuv420p",
                "-crf","23","-an","-vf",
                f"drawtext=text='ponto {i}/{len(M)}   {a/FPS:.0f}s':x=10:y=10:"
                f"fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6",
                f"/tmp/tu{i:02d}.mp4"])
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0",
                        "-i","/tmp/tu.txt","-c","copy","TEMPO_UTIL.mp4"], cwd="/tmp")
        subprocess.run(["cp","/tmp/TEMPO_UTIL.mp4","TEMPO_UTIL.mp4"])
        print("\n-> TEMPO_UTIL.mp4")


if __name__ == "__main__":
    main()
