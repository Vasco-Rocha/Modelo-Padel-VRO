#!/usr/bin/env python3
"""
O VÍDEO das travessias — pontos 10 e 11 (os frágeis).  *** SÓ LÊ. Não altera nada. ***

O Vasco vê com os olhos dele. Os números escondem isto.
(⚠️ script de DIAGNÓSTICO, escrito a 13 jul quando o estado era 96,3/95,9. NÃO é o estado atual
 — esse sai de `python3 teste_regressao.py`.)

O QUE ESTÁ DESENHADO:
  🟡 linha amarela .... a REDE (base), da calibração
  🟢 bola VERDE ....... detetada E dentro de um tracklet          (o código "vê-a")
  🔴 bola VERMELHA .... detetada mas FORA de tracklet             (o código IGNORA-A)
  ⚪ rasto ............ as últimas 12 posições
  ✅ TRAVESSIA CONTADA  o código contou a passagem pela rede
  💀 TRAVESSIA PERDIDA  a bola atravessou e o código NÃO contou — e diz-se PORQUÊ
  canto ............... L (borrão = velocidade) e prof (0=rede, 1=linha de serviço)
"""
import cv2, numpy as np, subprocess, sys
import gerar_tempo_util as G

SAIDA = "../TRAVESSIAS_pt10_pt11.mp4"
PONTOS = [10, 11]          # os frágeis
PAD = 1.5                  # segundos antes/depois, para dar contexto


def main():
    R, prof = G.carregar()
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    fs  = sorted(R2)
    Lmax = lambda f: max([R2[g][2] for g in fs if abs(g - f) <= 5] or [0])
    em_tk = {f for tk in tks for f in tk}

    # replicar cruzamentos() e guardar CONTADAS e PERDIDAS, com o motivo
    contadas, perdidas = {}, {}
    for tk in tks:
        ult = None
        for f in tk:
            l, p = prof(R2[f][0], R2[f][1])
            if p < G.MIN_PROF:
                continue
            L = Lmax(f)
            if ult and ult != l:
                if L >= G.L_RAQUETE:
                    contadas[f] = L
                else:
                    perdidas[f] = f"L={L:.1f} < {G.L_RAQUETE}  (S15: 'veio da MAO')"
            ult = l
    def prim_prof(tk, rev=False):
        for f in (reversed(tk) if rev else tk):
            l, p = prof(R2[f][0], R2[f][1])
            if p >= G.MIN_PROF:
                return f, l
        return None, None
    for t1, t2 in zip(tks, tks[1:]):
        fa, la = prim_prof(t1, rev=True)
        fb, lb = prim_prof(t2)
        if la and lb and la != lb:
            perdidas[fb] = "QUEBRA DE TRACKLET (a bola perdeu-se e voltou do outro lado)"

    cap = cv2.VideoCapture(G.VIDEO)
    W  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ESC = W / 960.0                      # a calibração é em 960x540
    vw = cv2.VideoWriter("/tmp/trav.mp4", cv2.VideoWriter_fourcc(*"mp4v"), G.FPS, (W, H))

    cal = __import__("json").load(open(G.CAL))
    rede = lambda x: float(np.polyval(cal["rede_base_coef"], x / ESC)) * ESC

    F = cv2.FONT_HERSHEY_SIMPLEX
    for k in PONTOS:
        t0, t1 = G.GT[k - 1]
        f0, f1 = int((t0 - PAD) * G.FPS), int((t1 + PAD) * G.FPS)
        n_cont = sum(1 for f in contadas if int(t0*G.FPS) <= f <= int(t1*G.FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        rasto = []
        for f in range(f0, f1 + 1):
            ok, im = cap.read()
            if not ok:
                break
            # a rede
            pts = [(x, int(rede(x))) for x in range(0, W, 8)]
            cv2.polylines(im, [np.array(pts, np.int32)], False, (0, 220, 255), 2)

            if f in R2:
                x, y, L, th = R2[f]
                px, py = int(x * ESC), int(y * ESC)
                rasto.append((px, py))
                rasto = rasto[-12:]
                for i, (rx, ry) in enumerate(rasto[:-1]):
                    cv2.circle(im, (rx, ry), 2, (200, 200, 200), -1)
                cor = (0, 255, 0) if f in em_tk else (0, 0, 255)
                cv2.circle(im, (px, py), 9, cor, 2)
                _, p = prof(x, y)
                cv2.putText(im, f"L={L:.1f}  prof={p:.2f}", (px + 14, py - 8),
                            F, 0.5, cor, 1, cv2.LINE_AA)

            if f in contadas:
                cv2.putText(im, "TRAVESSIA CONTADA", (W//2 - 190, 60), F, 1.0,
                            (0, 255, 0), 3, cv2.LINE_AA)
            if f in perdidas:
                cv2.rectangle(im, (0, 0), (W, H), (0, 0, 255), 6)
                cv2.putText(im, "TRAVESSIA PERDIDA", (W//2 - 200, 60), F, 1.0,
                            (0, 0, 255), 3, cv2.LINE_AA)
                cv2.putText(im, perdidas[f], (30, 100), F, 0.6, (0, 0, 255), 2, cv2.LINE_AA)

            cv2.rectangle(im, (0, H - 34), (W, H), (0, 0, 0), -1)
            dentro = t0 <= f / G.FPS <= t1
            cv2.putText(im, f"PONTO {k}  ({t0:.1f}-{t1:.1f}s, {t1-t0:.1f}s)   "
                            f"travessias contadas no ponto: {n_cont}   "
                            f"t={f/G.FPS:.1f}s" + ("" if dentro else "   [fora do ponto]"),
                        (12, H - 11), F, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
            vw.write(im)

        # separador preto
        for _ in range(int(0.7 * G.FPS)):
            im = np.zeros((H, W, 3), np.uint8)
            cv2.putText(im, f"fim do ponto {k}", (W//2 - 120, H//2), F, 0.9,
                        (255, 255, 255), 2, cv2.LINE_AA)
            vw.write(im)

    vw.release(); cap.release()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/trav.mp4",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", SAIDA], check=True)
    print(f"\n-> {SAIDA}")
    print(f"   travessias CONTADAS: {len(contadas)}   PERDIDAS: {len(perdidas)}")
    print("\n⚠️ Nada foi alterado. Leitura pura.\n")


if __name__ == "__main__":
    main()
