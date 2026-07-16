#!/usr/bin/env python3
"""
TESTE — a PANCADA DO RESPONDEDOR (a devolução).   *** SÓ VÊ / SÓ MEDE. ***

    python3 pancada_respondedor_video.py [--serves A-B] [--out PATH]    (Parada4 — é onde há bola)

A HIPÓTESE (Vasco): um serviço a sério é DEVOLVIDO pelo respondedor; um candidato de
intervalo NÃO é. ⇒ para cada CANDIDATO a servir (detetor de formação, inclui os extras):

  · serviço ≈ fim do bloco de formação (b)
  · devolução = a 1.ª PANCADA no lado que RECEBE, depois do serviço (janela 3 s)
  · marca-se a BOLA (amarelo) e o RESPONDEDOR = a box mais perto da bola (vermelho)
  · se não há pancada do lado que recebe ⇒ 'SEM DEVOLUCAO' (candidato provavelmente falso)

⚠️ USA A BOLA (a pancada, P5) — não o quique. Só corre no Parada4.
⚠️ Leitura pura. O gerar_tempo_util.py NÃO é tocado.
"""
import sys, json, pickle, subprocess, math
import numpy as np, cv2

VIDEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "parada4"
import cascata_jogadores as C
C.configurar(VIDEO)
import detetor_servico as D
import gerar_tempo_util as G

# 🩸 o pipeline da bola (G) está FIXO no Parada4 — aponto-o ao vídeo pedido (a bola é POR VÍDEO)
FICH = {
    "parada4": dict(bola="data/parada4/traj_frames_Parada4_thr04.csv",
                    boxes="data/parada4/player_boxes_parada4.pkl",
                    cal="calibracao_parada4.json", mp4="../Parada4.mp4"),
    "barbosa": dict(bola="../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv",
                    boxes="../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl",
                    cal="calibracao_BarbosaMeireles.json", mp4="../BarbosaMeireles.mp4"),
}[VIDEO]
G.BOLA, G.BOXES, G.CAL, G.FPS = FICH["bola"], FICH["boxes"], FICH["cal"], C.FPS

SA, SB = 1, 999
if "--serves" in sys.argv:
    SA, SB = (int(x) for x in sys.argv[sys.argv.index("--serves") + 1].split("-"))
OUT = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
       else f"/sessions/upbeat-confident-cori/mnt/outputs/PANCADA_RESPONDEDOR_{VIDEO}.mp4")
MP4 = FICH["mp4"]
cal = C.cal
cx = lambda y: float(np.polyval(cal["centro_coef_em_y"], y))
FPS = C.FPS
JAN = 3.0        # s — janela depois do serviço onde procurar a devolução (ATALHO DECLARADO)
GTs = C.GT


def main():
    pb = D.cascata(VIDEO)
    S, _ = D.servicos(VIDEO, D.REGRAS, pb)
    R, prof = G.carregar(); R = G.vai_e_vem(R)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R, cal, boxes)

    def e_gt(tb):
        return any(abs(tb - g) <= 3.5 for g in GTs)

    # ---- por candidato: encontrar a 1.ª pancada do lado que recebe depois do serviço ----
    itens = []
    for a, b, l in S:
        recv = "cima" if l == "baixo" else "baixo"
        p = next((q for q in PAN if b < q <= b + int(JAN * FPS)
                  and q in R and prof(R[q][0], R[q][1])[0] == recv), None)
        itens.append((a, b, l, recv, p))

    reais = [it for it in itens if e_gt(it[1] / FPS)]
    extras = [it for it in itens if not e_gt(it[1] / FPS)]
    print(f"\n  candidatos: {len(itens)}  ·  reais: {len(reais)}  ·  extras: {len(extras)}")
    print(f"  reais COM devolução:  {sum(bool(it[4]) for it in reais)}/{len(reais)}")
    print(f"  extras COM devolução: {sum(bool(it[4]) for it in extras)}/{len(extras)}  (queremos 0)\n")

    cap = cv2.VideoCapture(MP4)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{W}x{H}", "-r", f"{FPS:.4f}", "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT],
        stdin=subprocess.PIPE)
    linha = np.array([[int(cx(y)), y] for y in range(0, H)], np.int32)

    n = 0
    for a, b, l, recv, p in itens:
        n += 1
        if not (SA <= n <= SB):
            continue
        tb = b / FPS
        tag = "GT" if e_gt(tb) else "EXTRA"
        if p is not None:
            f0, f1 = int(p / 1 - 1.0 * FPS), int(p / 1 + 0.7 * FPS)
            titulo = f"CAND {n} [{tag}] serve {l.upper()}  ->  DEVOLUCAO t={p/FPS:.1f}s"
        else:
            f0, f1 = b, b + int(2.5 * FPS)
            titulo = f"CAND {n} [{tag}] serve {l.upper()}  ->  SEM DEVOLUCAO (lado {recv})"
        f0 = max(0, f0); f1 = min(len(pb), f1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        for f in range(f0, f1):
            ok, img = cap.read()
            if not ok:
                break
            cv2.polylines(img, [linha], False, (0, 220, 255), 2)
            for bx in pb[f]:
                cv2.rectangle(img, tuple(map(int, bx[:2])), tuple(map(int, bx[2:])), (150, 150, 150), 1)
            # a bola
            if f in R:
                bx_, by_ = R[f][0], R[f][1]
                cv2.circle(img, (int(bx_), int(by_)), 7, (0, 255, 255), -1)
                # o respondedor = a box mais perto da bola
                if pb[f]:
                    rr = min(pb[f], key=lambda z: math.hypot(C.pes(z)[0] - bx_, C.pes(z)[1] - by_))
                    cv2.rectangle(img, tuple(map(int, rr[:2])), tuple(map(int, rr[2:])), (40, 40, 255), 3)
            # marca o instante EXATO da pancada
            if p is not None and abs(f - p) <= 1:
                cv2.circle(img, (int(R[p][0]), int(R[p][1])), 16, (0, 0, 255), 3)
            cv2.rectangle(img, (0, 0), (W, 34), (0, 0, 0), -1)
            cv2.putText(img, titulo, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait(); cap.release()
    print(f"OK · {OUT}")


if __name__ == "__main__":
    main()
