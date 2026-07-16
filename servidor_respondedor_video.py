#!/usr/bin/env python3
"""
TESTE — servidor (medido) + RESPONDEDOR (DEDUZIDO: o de trás CRUZADO).   *** SÓ VÊ. Zero bola. ***

    python3 servidor_respondedor_video.py [parada4|barbosa] [--serves A-B] [--out PATH]

Ancorado nos serviços em GROUND-TRUTH (o gabarito). Para cada serviço:
  · SERVIDOR  (vermelho)  = o atrasado da equipa que serve            (o que já medimos)
  · RESPONDEDOR (azul)    = o de trás da OUTRA equipa, na METADE OPOSTA (a diagonal, S4)
                            ⇒ DEDUZIDO do lado do servidor. Não é detetado — é inferido.
  · se o respondedor não aparece → 'NAO DETETADO' (o fundo cortado da câmara, C6)

⚖️ D19 — lado = pés contra a linha central, BINÁRIO. A regra PONTUA, aqui só se MOSTRA para testar.
⚠️ Leitura pura. O gerar_tempo_util.py NÃO é tocado.
"""
import sys, subprocess
import numpy as np, cv2

VIDEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "parada4"
import cascata_jogadores as C
C.configurar(VIDEO)
import detetor_servico as D

SA, SB = 1, 999
if "--serves" in sys.argv:
    SA, SB = (int(x) for x in sys.argv[sys.argv.index("--serves") + 1].split("-"))
OUT = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
       else f"/sessions/upbeat-confident-cori/mnt/outputs/RESPONDEDOR_{VIDEO}.mp4")
MP4 = {"parada4": "../Parada4.mp4", "barbosa": "../BarbosaMeireles.mp4"}[VIDEO]
cal = C.cal
cx = lambda y: float(np.polyval(cal["centro_coef_em_y"], y))
FPS = C.FPS
PRE, POS = 3.0, 0.7


def metade(box):
    px, py = C.pes(box)
    return "ESQ" if px < cx(py) else "DIR"


def recuo(box):
    px, py = C.pes(box)
    return abs(py - C.y_base(px))


def respondedor(fr, serve_side, serv_half):
    """O de trás da equipa que RECEBE, na metade OPOSTA ao servidor (a diagonal)."""
    recv = "cima" if serve_side == "baixo" else "baixo"
    diag = [b for b in fr if C.lado(b) == recv and metade(b) != serv_half]
    if not diag:
        return None
    return max(diag, key=recuo)                       # o mais recuado dos diagonais


def main():
    pb = D.cascata(VIDEO)
    S, _ = D.servicos(VIDEO, D.REGRAS, pb)
    cap = cv2.VideoCapture(MP4)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{W}x{H}", "-r", f"{FPS:.4f}", "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
        stdin=subprocess.PIPE)
    linha = np.array([[int(cx(y)), y] for y in range(0, H)], np.int32)

    def box(img, b, cor, w):
        x1, y1, x2, y2 = map(int, b)
        cv2.rectangle(img, (x1, y1), (x2, y2), cor, w)
        px, py = C.pes(b)
        cv2.circle(img, (int(px), int(py)), 6, cor, -1)

    n_val = 0
    for n, t in enumerate(C.GT, 1):
        fa, fb = int((t - 3) * FPS), int((t + 0.5) * FPS)
        hit = next(((a, b, l) for a, b, l in S if not (b < fa or a > fb)), None)
        if not hit:
            continue
        a, b, l = hit
        n_val += 1
        if not (SA <= n_val <= SB):
            continue
        f0, f1 = max(0, int((t - PRE) * FPS)), min(len(pb), int((t + POS) * FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        for f in range(f0, f1):
            ok, img = cap.read()
            if not ok:
                break
            cv2.polylines(img, [linha], False, (0, 220, 255), 2)
            for bx in pb[f]:
                cv2.rectangle(img, tuple(map(int, bx[:2])), tuple(map(int, bx[2:])), (150, 150, 150), 1)
            srv = D.servidor(pb[f], l)
            sh = metade(srv) if srv is not None else "?"
            resp = respondedor(pb[f], l, sh) if srv is not None else None
            if resp is not None:
                box(img, resp, (255, 150, 0), 3)           # RESPONDEDOR — azul
            if srv is not None:
                box(img, srv, (40, 40, 255), 3)            # SERVIDOR — vermelho
            rh = metade(resp) if resp is not None else "NAO DETETADO"
            cv2.rectangle(img, (0, 0), (W, 34), (0, 0, 0), -1)
            cv2.putText(img, f"SERVICO {n_val}  t={t:.1f}s  serve {l.upper()}   "
                        f"SERVIDOR(verm)={sh}   RESPONDEDOR(azul)={rh}",
                        (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait(); cap.release()
    print(f"OK — {n_val} serviços GT · {OUT}")


if __name__ == "__main__":
    main()
