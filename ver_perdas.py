#!/usr/bin/env python3
"""
AS PERDAS — o Vasco vê com os olhos dele.   *** SÓ LÊ. Não altera nada. ***

Compila as 8 PANCADAS que caem na FAIXA junto à rede, do lado de CIMA — as candidatas à regra
do Vasco ("volley à rede = travessia dupla"). Nenhuma delas está DENTRO de uma box (mediana:
0,41 meios-campos ≈ 2,8 m), e por isso a regra não dispara.

A PERGUNTA PARA O VASCO:
   👀 São VOLLEYS à rede? (⇒ a regra está certa e o teste da box é que está mal posto)
   👀 Ou são outra coisa?  (⇒ a regra não se aplica aqui)

O QUE ESTÁ DESENHADO:
   🟡 amarelo ...... a faixa da rede (topo + base)
   🔵 azul ......... as BOUNDING BOXES dos jogadores (todas, cruas)
   🔴 bola grande .. a PANCADA (o instante do evento)
   ⚪ rasto ........ as posições da bola à volta
   texto ........... distância à box mais próxima, em meios-campos · L · profundidade
"""
import cv2, numpy as np, json, pickle, math, subprocess
import gerar_tempo_util as G

SAIDA = "../AS_PERDAS_volley_rede.mp4"
PAD = 1.6      # segundos de contexto antes/depois


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    y_topo, y_base, meio = G.campo(cal)

    def dist_box(f):
        x, y = R2[f][0], R2[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    # as 8: pancada na faixa junto à rede, lado de CIMA
    ev = []
    for f in PAN:
        if f not in R2:
            continue
        lado, p = prof(R2[f][0], R2[f][1])
        if lado == "cima" and p < G.MIN_PROF:
            ev.append((f, p, dist_box(f)))

    print(f"\n{len(ev)} eventos (pancada na faixa da rede, lado de CIMA)\n")

    cap = cv2.VideoCapture(G.VIDEO)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vw = cv2.VideoWriter("/tmp/perdas.mp4", cv2.VideoWriter_fourcc(*"mp4v"), G.FPS, (W, H))
    F = cv2.FONT_HERSHEY_SIMPLEX

    for i, (fev, pev, dev) in enumerate(ev, 1):
        t = fev / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if g0 <= t <= g1), None)
        etiq = f"dentro do ponto {gt}" if gt else "NO INTERVALO (entre pontos)"

        # cartão
        for _ in range(int(1.1 * G.FPS)):
            im = np.zeros((H, W, 3), np.uint8)
            cv2.putText(im, f"EVENTO {i}/{len(ev)}   t = {t:.1f}s", (40, H//2 - 40),
                        F, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(im, f"distancia a box: {dev:.2f} meios-campos"
                            f"   ({'DENTRO' if dev <= G.MAO_RAIO else 'FORA'} do raio da regra)",
                        (40, H//2 + 5), F, 0.7, (0, 200, 255), 2, cv2.LINE_AA)
            cv2.putText(im, etiq, (40, H//2 + 45), F, 0.7,
                        (0, 255, 0) if gt else (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(im, "E' um VOLLEY a rede?", (40, H//2 + 95), F, 0.8,
                        (255, 255, 0), 2, cv2.LINE_AA)
            vw.write(im)

        f0, f1 = int(fev - PAD*G.FPS), int(fev + PAD*G.FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
        rasto = []
        for f in range(f0, f1 + 1):
            ok, im = cap.read()
            if not ok:
                break
            # a faixa da rede
            for coef, cor in (("rede_topo_coef", (0, 220, 255)), ("rede_base_coef", (0, 220, 255))):
                pts = [(x, int(np.polyval(cal[coef], x))) for x in range(0, W, 8)]
                cv2.polylines(im, [np.array(pts, np.int32)], False, cor, 1)
            # as boxes dos jogadores (cruas)
            if f < len(boxes):
                for x1, y1, x2, y2 in boxes[f]:
                    cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), (255, 160, 0), 2)
            # a bola
            if f in R2:
                x, y, L, th = R2[f]
                rasto.append((int(x), int(y))); rasto = rasto[-14:]
                for rx, ry in rasto[:-1]:
                    cv2.circle(im, (rx, ry), 2, (220, 220, 220), -1)
                grande = abs(f - fev) <= 2
                cv2.circle(im, (int(x), int(y)), 14 if grande else 8,
                           (0, 0, 255) if grande else (0, 255, 0), 3 if grande else 2)
                _, p = prof(x, y)
                cv2.putText(im, f"L={L:.1f} prof={p:.2f} dist_box={dist_box(f):.2f}",
                            (int(x)+18, int(y)-10), F, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
            if abs(f - fev) <= 3:
                cv2.rectangle(im, (0, 0), (W, H), (0, 0, 255), 6)
                cv2.putText(im, "PANCADA", (W//2 - 80, 46), F, 1.0, (0, 0, 255), 3, cv2.LINE_AA)

            cv2.rectangle(im, (0, H-32), (W, H), (0, 0, 0), -1)
            cv2.putText(im, f"evento {i}/{len(ev)}   t={f/G.FPS:.1f}s   "
                            f"dist a box no impacto: {dev:.2f} meios-campos   {etiq}",
                        (12, H-10), F, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            vw.write(im)

    vw.release(); cap.release()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/perdas.mp4",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", SAIDA], check=True)
    print(f"-> {SAIDA}\n")
    for i, (f, p, dd) in enumerate(ev, 1):
        t = f / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if g0 <= t <= g1), None)
        print(f"  {i}. t={t:7.1f}s   prof={p:.2f}   dist_box={dd:.2f}   "
              f"{'ponto '+str(gt) if gt else 'INTERVALO'}")
    print("\n⚠️ Leitura pura. Nada foi alterado.\n")


if __name__ == "__main__":
    main()
