#!/usr/bin/env python3
"""BARBOSA — agora COM GROUND-TRUTH (anotado pelo Vasco, 13 jul, 21 pontos).
Julga: boxes sujas vs limpas (J1) · B16 (o ténis) · S42 (a confirmação do fim).
NÃO altera o gerar_tempo_util.py."""
import sys, json, pickle
sys.path.insert(0, ".")
import gerar_tempo_util as gt

GT_VASCO = [(13.6,23.7),(33.9,37.3),(40.3,44.7),(54.5,62.4),(69.8,73.6),(83.3,96.0),
            (135.0,139.1),(155.0,157.6),(162.9,171.8),(188.3,192.2),(196.0,202.0),
            (227.2,230.8),(242.3,245.4),(257.1,266.0),(298.3,306.8),(326.1,337.3),
            (352.1,357.3),(367.9,371.1),(377.9,384.3),(406.8,416.1),(526.0,533.9)]

gt.FPS = 29.97002997002997
gt.N_FRAMES = 16138
gt.BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
gt.CAL = "calibracao_BarbosaMeireles.json"
gt.GT = GT_VASCO
F = gt.FPS

SUJAS = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl"
LIMPAS = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles_J1.pkl"
PE_FRAC, L_PARADO, N_SEG = 0.18, 4.0, 5


def nos_pes(f, x, y, boxes):
    if f >= len(boxes) or not boxes[f]:
        return False
    return any(x1 <= x <= x2 and y1 <= y <= y2 and (y2-y)/max(y2-y1, 1) <= PE_FRAC
               for x1, y1, x2, y2 in boxes[f])


def b16(R, boxes, modo):
    if modo == "-":
        return R
    pes = {f for f in R if nos_pes(f, R[f][0], R[f][1], boxes)}
    if modo == "A":
        mata = pes
    elif modo == "B":
        mata = {f for f in pes if R[f][2] <= L_PARADO}
    else:
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
    return {f: v for f, v in R.items() if f not in mata}


def fim_dentro(M, FIM):
    """🔒 D15 — um fim certo NUNCA pode cair a meio de um ponto REAL."""
    return sum(1 for f in FIM for a, b in GT_VASCO
               if a*F + 15 < f < b*F - 15)


R0, prof = gt.carregar()
cal = json.load(open(gt.CAL))
print("BARBOSA — contra o ground-truth do Vasco (21 pontos, 138,0 s)\n")
print(f"{'boxes':>8} {'B16':>4} {'S42':>4} | {'pts':>4} {'tempo':>7} | {'RECALL':>7} {'PRECIS':>7} {'F1':>6} | fim_dentro")
print("-" * 78)
melhor = None
for bx, bxp in [("sujas", SUJAS), ("J1", LIMPAS)]:
    boxes = pickle.load(open(bxp, "rb"))["player_boxes"]
    for modo in ["-", "A", "B", "C"]:
        for s42 in [False, True]:
            gt.REGRAS["S42_CONFIRMA_FIM"] = s42
            R = b16(dict(R0), boxes, modo)
            R = gt.vai_e_vem(R); tks = gt.tracklets(R)
            CR = gt.cruzamentos(R, tks, prof)
            PAN = gt.pancadas(R, cal, boxes); FIM = gt.fim_certo(R, cal, boxes)
            RES = gt.ressaltos(R, tks)
            M = gt.rallies(CR, PAN, FIM, RES, R, prof)
            r = gt.avaliar(M)
            fd = fim_dentro(M, FIM)
            mark = ""
            if melhor is None or r["recall"] > melhor[0]:
                melhor = (r["recall"], bx, modo, s42)
            print(f"{bx:>8} {modo:>4} {'ON' if s42 else 'off':>4} | {r['n']:>4} {r['tempo']:>6.0f}s | "
                  f"{r['recall']:>7.1f} {r['precisao']:>7.1f} {r['f1']:>6.1f} | {fd:>3}{mark}")
gt.REGRAS["S42_CONFIRMA_FIM"] = False
print("-" * 78)
print(f"melhor RECALL: {melhor[0]:.1f}  (boxes={melhor[1]} · B16={melhor[2]} · S42={'ON' if melhor[3] else 'off'})")
print("\nGT: 21 pontos.  A diretriz manda no RECALL.")
