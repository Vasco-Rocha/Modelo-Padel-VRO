#!/usr/bin/env python3
"""CHECK — a linha da REDE está no sítio?   *** SÓ LÊ. ***

Desenha, no mesmo frame:
  🟢 VERDE   = rede_topo   (o cimo da rede / a fita)
  🟡 AMARELO = rede_base   (a base da rede — a linha que separa CIMA de BAIXO)
  🔵 AZUL    = servico_longe   ⬛ ROXO = servico_perto
  ⚪ os PONTOS que o Vasco marcou à mão no calibrar_campo.html

Se o AMARELO não estiver onde a rede toca o chão, o 'lado' (cima/baixo) de TODAS as bolas
está deslocado — e o `prof` sai dele.
"""
import cv2, numpy as np, json, sys
import gerar_tempo_util as G

T = float(sys.argv[1]) if len(sys.argv) > 1 else 230.3   # o instante do L=3.0
cal = json.load(open(G.CAL))

cap = cv2.VideoCapture(G.VIDEO)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
ESC = W / cal["resolucao"][0]
cap.set(cv2.CAP_PROP_POS_FRAMES, int(T * G.FPS))
ok, im = cap.read()
assert ok

LINHAS = [("rede_topo_coef",     (0, 255, 0),   "REDE TOPO (fita)"),
          ("rede_base_coef",     (0, 220, 255), "REDE BASE  <- separa CIMA de BAIXO"),
          ("servico_longe_coef", (255, 120, 0), "servico LONGE"),
          ("servico_perto_coef", (255, 0, 255), "servico PERTO")]

for chave, cor, nome in LINHAS:
    pts = [(x, int(np.polyval(cal[chave], x / ESC) * ESC)) for x in range(0, W, 6)]
    cv2.polylines(im, [np.array(pts, np.int32)], False, cor, 2)
    y = pts[len(pts)//2][1]
    cv2.putText(im, nome, (W//2 - 120, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.55, cor, 2, cv2.LINE_AA)

# os pontos marcados à mão
for chave in ("rede_topo", "rede_base", "servico_longe", "servico_perto"):
    for px, py in cal["pontos"][chave]:
        cv2.drawMarker(im, (int(px*ESC), int(py*ESC)), (255, 255, 255),
                       cv2.MARKER_CROSS, 16, 2)

# a bola nesse instante
R, prof = G.carregar()
f = int(T * G.FPS)
viz = [g for g in R if abs(g - f) <= 2]
if viz:
    g = min(viz, key=lambda g: abs(g - f))
    x, y, L, th = R[g]
    lado, p = prof(x, y)
    cv2.circle(im, (int(x*ESC), int(y*ESC)), 10, (0, 0, 255), 2)
    cv2.putText(im, f"BOLA  L={L:.1f}  lado={lado}  prof={p:.2f}",
                (int(x*ESC)+14, int(y*ESC)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 0, 255), 2, cv2.LINE_AA)

cv2.putText(im, f"t = {T:.1f}s", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            (255, 255, 255), 2, cv2.LINE_AA)
out = f"../CHECK_rede_{T:.0f}s.png"
cv2.imwrite(out, im)
print(f"-> {out}   (video {W}x{H}, calibracao {cal['resolucao']}, escala {ESC:.2f})")
