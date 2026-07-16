#!/usr/bin/env python3
"""👟 B16 — O TÉNIS.  (regra do Vasco, 13 jul, a VER o vídeo do Barbosa)

  "Se deteto uma bola ou duas semelhantes (ténis) no LIMITE INFERIOR da bounding box,
   e se É UMA CONSTANTE — tenho de verificar esta bola."

A regra tem DUAS partes. Testo as duas, e a versão bruta, nos DOIS vídeos.
NÃO altera o gerar_tempo_util.py. Só mede.

  A — BRUTA      : fora tudo o que cai nos 18% de baixo de uma box
  B — CONSTANTE  : só se a "bola" ESTIVER PARADA lá (L baixo)   <- o "é uma constante"
  C — PERSISTENTE: só se ficar na zona dos pés >= N frames seguidos
"""
import sys, json, pickle, math
sys.path.insert(0, ".")
import gerar_tempo_util as gt

PE_FRAC = 0.18     # ⚠️ AJUSTE MEU (declarado): 18% de baixo da box = a zona dos PÉS
L_PARADO = 4.0     # ⚠️ AJUSTE MEU: "constante" = borrão pequeno = não se move
N_SEG = 5          # ⚠️ AJUSTE MEU: frames seguidos na zona dos pés


def nos_pes(f, x, y, boxes):
    if f >= len(boxes) or not boxes[f]:
        return False
    for x1, y1, x2, y2 in boxes[f]:
        if x1 <= x <= x2 and y1 <= y <= y2 and (y2 - y) / max(y2 - y1, 1) <= PE_FRAC:
            return True
    return False


def filtrar(R, boxes, modo):
    if modo == "off":
        return R
    pes = {f for f in R if nos_pes(f, R[f][0], R[f][1], boxes)}
    if modo == "A":
        mata = pes
    elif modo == "B":
        mata = {f for f in pes if R[f][2] <= L_PARADO}
    else:  # C — persistente
        mata, run = set(), []
        for f in sorted(R):
            if f in pes and (not run or f - run[-1] <= 2):
                run.append(f)
            else:
                if len(run) >= N_SEG:
                    mata |= set(run)
                run = [f] if f in pes else []
        if len(run) >= N_SEG:
            mata |= set(run)
    return {f: v for f, v in R.items() if f not in mata}, len(mata)


def correr(video):
    if video == "barbosa":
        gt.FPS = 29.97002997002997; gt.N_FRAMES = 16138
        gt.BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
        gt.BOXES = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles_J1.pkl"
        gt.CAL = "calibracao_BarbosaMeireles.json"; gt.GT = []
    F = gt.FPS
    R0, prof = gt.carregar()
    cal = json.load(open(gt.CAL))
    boxes = pickle.load(open(gt.BOXES, "rb"))["player_boxes"]
    print(f"\n=== {video.upper()} ===")
    print(f"{'B16':>4} {'mortas':>7} {'bola':>6} {'cruz':>5} {'panc':>5} {'fins':>5} {'pts':>4} "
          f"{'tempo util':>11} {'recall':>7} {'precis':>7}")
    for modo in ["off", "A", "B", "C"]:
        out = filtrar(dict(R0), boxes, modo)
        R, mortas = (out, 0) if modo == "off" else out
        R = gt.vai_e_vem(R); tks = gt.tracklets(R)
        CR = gt.cruzamentos(R, tks, prof)
        PAN = gt.pancadas(R, cal, boxes); FIM = gt.fim_certo(R, cal, boxes)
        RES = gt.ressaltos(R, tks)
        M = gt.rallies(CR, PAN, FIM, RES, R, prof)
        tu = sum(b - a for a, b in M) / F
        if gt.GT:
            r = gt.avaliar(M)
            met = f"{r['recall']:7.1f} {r['precisao']:7.1f}"
        else:
            met = f"{'--':>7} {'--':>7}"
        print(f"{modo:>4} {mortas:>7} {len(R):>6} {len(CR):>5} {len(PAN):>5} {len(FIM):>5} "
              f"{len(M):>4} {tu:>9.1f}s {met}")


correr("parada4")
correr("barbosa")
print("\n  A = fora TUDO o que cai nos pés")
print("  B = só o que está PARADO nos pés  (o \"é uma constante\" do Vasco)")
print("  C = só o que fica >= 5 frames seguidos nos pés")
