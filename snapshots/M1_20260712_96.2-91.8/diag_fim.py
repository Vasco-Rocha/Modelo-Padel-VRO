#!/usr/bin/env python3
"""
S17 + S18 — MEDIR, NÃO CORTAR.   13 jul 2026.

O Vasco: "mal detetes que toca na mão, corpo ou rede, máximo 0,5s quero o ponto terminado."

Antes de cortar seja o que for, isto MEDE os candidatos e diz onde caem:
  - DENTRO de um ponto real  -> cortaria o ponto a meio.  ⛔ PROIBIDO (contra a diretriz).
  - no FIM (ultimo 1,5s) ou DEPOIS -> e' um fim verdadeiro. ✅ e' o que queremos.
  - no INTERVALO -> inofensivo (o ponto ja acabou).

RÉGUA: tudo em frações do MEIO-CAMPO LOCAL (rede -> linha de serviço, naquele x).
       Zero píxeis absolutos. (feedback_sem_atalhos)

    python3 diag_fim.py
"""
import sys, json, math, pickle
import numpy as np
sys.path.insert(0, ".")
from gerar_tempo_util import carregar, vai_e_vem, FPS, N_FRAMES, GT, L_RAQUETE

cal = json.load(open("calibracao_campo.json"))
ev = lambda c, x: float(np.polyval(c, x))
y_topo = lambda x: ev(cal["rede_topo_coef"], x)     # topo da rede
y_tape = lambda x: ev(cal["rede_tape_coef"], x)     # a fita
y_base = lambda x: ev(cal["rede_base_coef"], x)     # base da rede
y_sp   = lambda x: ev(cal["servico_perto_coef"], x)
y_sl   = lambda x: ev(cal["servico_longe_coef"], x)


def meio_campo_px(x, y):
    """A RÉGUA LOCAL: quantos píxeis vale o meio-campo (6,95 m) naquele x, naquele lado."""
    yb = y_base(x)
    return abs(y_sp(x) - yb) if y > yb else abs(yb - y_sl(x))


R, prof = carregar()
R = vai_e_vem(R)
PB = pickle.load(open("../dados_parada4/player_boxes_parada4.pkl", "rb"))["player_boxes"]

gt = np.zeros(N_FRAMES, bool)
fim_gt = np.zeros(N_FRAMES, bool)      # o último 1,5s de cada ponto
for a, b in GT:
    gt[int(a*FPS):int(b*FPS)+1] = True
    fim_gt[int((b-1.5)*FPS):int(b*FPS)+1] = True


def onde(f):
    if not gt[f]:
        return "INTERVALO"
    return "FIM do ponto" if fim_gt[f] else "⛔ DENTRO"


# ---------------------------------------------------------------- S17: bola na rede
def cand_rede(banda):
    """Bola dentro da BANDA da rede (topo..base), alargada por <banda> x meio-campo local."""
    out = []
    for f in sorted(R):
        x, y, L, th = R[f]
        m = meio_campo_px(x, y)
        if y_topo(x) - banda*m <= y <= y_base(x) + banda*m:
            out.append(f)
    # agrupar em eventos (>=0,5s de intervalo = evento novo)
    ev_ = []
    for f in out:
        if ev_ and f - ev_[-1][-1] <= 15:
            ev_[-1].append(f)
        else:
            ev_.append([f])
    return [g[0] for g in ev_]


# ---------------------------------------------------------------- S18: mão / corpo
def cand_mao(raio):
    """Bola LENTA (L < L_RAQUETE = mão, não raquete) e JUNTO a um jogador.
       'junto' = a menos de <raio> x meio-campo local do centro da box."""
    out = []
    for f in sorted(R):
        x, y, L, th = R[f]
        if L >= L_RAQUETE:
            continue
        if f >= len(PB):
            continue
        m = meio_campo_px(x, y)
        for (x1, y1, x2, y2) in PB[f]:
            if x1 - raio*m <= x <= x2 + raio*m and y1 - raio*m <= y <= y2 + raio*m:
                out.append(f)
                break
    ev_ = []
    for f in out:
        if ev_ and f - ev_[-1][-1] <= 15:
            ev_[-1].append(f)
        else:
            ev_.append([f])
    return [g[0] for g in ev_]


def tabela(nome, cands):
    c = {"⛔ DENTRO": 0, "FIM do ponto": 0, "INTERVALO": 0}
    dentro = []
    for f in cands:
        k = onde(f)
        c[k] += 1
        if k == "⛔ DENTRO":
            dentro.append(round(f/FPS, 1))
    tot = max(len(cands), 1)
    print(f"  {nome:<28} {len(cands):>4} eventos | "
          f"DENTRO {c['⛔ DENTRO']:>3} ({100*c['⛔ DENTRO']/tot:>4.0f}%) | "
          f"FIM {c['FIM do ponto']:>3} | INTERVALO {c['INTERVALO']:>3}")
    if dentro:
        print(f"      cortaria a meio em: {dentro[:14]}{' ...' if len(dentro) > 14 else ''}")
    return c


print("=" * 96)
print("S17 — BOLA NA REDE   (banda = topo..base da rede, alargada por f x meio-campo local)")
print("=" * 96)
for b in [0.0, 0.05, 0.10, 0.20]:
    tabela(f"banda +{b:.2f} x meio-campo", cand_rede(b))

print()
print("=" * 96)
print("S18 — MÃO / CORPO   (bola com L<%d  E  junto a um jogador)" % L_RAQUETE)
print("=" * 96)
for r in [0.0, 0.05, 0.10, 0.20]:
    tabela(f"raio {r:.2f} x meio-campo", cand_mao(r))

print()
print("LEITURA: qualquer linha com DENTRO > 0 CORTA pontos reais a meio.")
print("         A diretriz do Vasco proíbe: nunca perder um ponto.")
