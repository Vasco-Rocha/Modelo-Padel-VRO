#!/usr/bin/env python3
"""
VÍDEO — os segundos ANTES de cada serviço validado, com a CENTRAL e o SERVIDOR marcados.
    *** SÓ MEDE / SÓ VÊ. Zero bola. O gerar_tempo_util.py NÃO é tocado. ***

    python3 servidor_video.py [parada4|barbosa]

Para cada serviço validado (detetor de formação): janela [t-3s, t+0,7s].
  · linha CENTRAL a amarelo  (cx(y) = polyval(centro_coef_em_y, y))
  · TODOS os jogadores a cinzento; o SERVIDOR (atrasado da equipa que serve) a vermelho
  · cabeçalho: nº, t, que campo serve, e o veredito ESQUERDA/DIREITA (no fim do bloco)
"""
import sys, json, subprocess
import numpy as np, cv2

VIDEO = sys.argv[1] if len(sys.argv) > 1 else "parada4"
import cascata_jogadores as C
C.configurar(VIDEO)
import detetor_servico as D

# --serves A-B  → só esses serviços · --out PATH → destino
SA, SB = 1, 999
if "--serves" in sys.argv:
    SA, SB = (int(x) for x in sys.argv[sys.argv.index("--serves") + 1].split("-"))
OUT = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
       else f"/sessions/upbeat-confident-cori/mnt/outputs/SERVIDORES_{VIDEO}.mp4")
MP4 = {"parada4": "../Parada4.mp4", "barbosa": "../BarbosaMeireles.mp4"}[VIDEO]
cal = C.cal
cx = lambda y: float(np.polyval(cal["centro_coef_em_y"], y))
FPS = C.FPS
PRE, POS = 3.0, 0.7          # s antes / depois (ATALHO DECLARADO: janela de revisão)


def lado_de(box):
    px, py = C.pes(box)
    return "ESQUERDA" if px < cx(py) else "DIREITA"


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
    n_val = 0
    for n, t in enumerate(C.GT, 1):
        fa, fb = int((t - 3) * FPS), int((t + 0.5) * FPS)
        hit = next(((a, b, l) for a, b, l in S if not (b < fa or a > fb)), None)
        if not hit:
            continue
        a, b, l = hit
        srv_b = D.servidor(pb[b], l)
        verdict = lado_de(srv_b) if srv_b is not None else "?"
        n_val += 1
        if not (SA <= n_val <= SB):        # fora do lote pedido
            continue
        f0, f1 = max(0, int((t - PRE) * FPS)), min(len(pb), int((t + POS) * FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)      # procura UMA vez; depois lê em sequência
        for f in range(f0, f1):
            ok, img = cap.read()
            if not ok:
                break
            cv2.polylines(img, [linha], False, (0, 220, 255), 2)      # central (amarelo em BGR)
            for bx in pb[f]:
                x1, y1, x2, y2 = map(int, bx)
                cv2.rectangle(img, (x1, y1), (x2, y2), (150, 150, 150), 1)
            srv = D.servidor(pb[f], l)
            if srv is not None:
                x1, y1, x2, y2 = map(int, srv)
                cv2.rectangle(img, (x1, y1), (x2, y2), (40, 40, 255), 3)
                px, py = C.pes(srv)
                cv2.circle(img, (int(px), int(py)), 6, (40, 40, 255), -1)
            cv2.rectangle(img, (0, 0), (W, 34), (0, 0, 0), -1)
            cv2.putText(img, f"SERVICO {n_val}  t={t:.1f}s  serve {l.upper()}  ->  SERVIDOR: {verdict}",
                        (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait(); cap.release()
    print(f"OK — {n_val} serviços · {OUT}")


if __name__ == "__main__":
    main()
