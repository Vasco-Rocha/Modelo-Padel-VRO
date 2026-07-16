#!/usr/bin/env python3
"""
👁️ VER A CASCATA  —  o teste VISUAL   (14 jul 2026)

    🎬 VÍDEO ANTES DE MÉTRICAS. Ele encontrou TODOS os bugs a olhar.
       Nenhum apareceu nos números.                        — a lei do Vasco

Faz UMA folha de contacto: o frame de CADA SERVIÇO, com as boxes da cascata desenhadas.
O Vasco olha e diz se as regras estão certas. Os números não chegam.

    🟩 verde  = jogador de CIMA   (a câmara vê-os sempre)
    🟦 azul   = jogador de BAIXO  (é aqui que a S2 vive ou morre)
    🟨 amarelo= box INTERPOLADA pela J5 (inventada — "a única regra que ACRESCENTA")
    ⬜ branco = o POLÍGONO (J1/J15: LARGO, inclui os espaços laterais)
    🔴 vermelho = uma box que a cascata DEITOU FORA (público, espectadores)

    canto: FORMAÇÃO lida só nos 2 de CIMA  (S3)  →  quem SERVE?
           um na REDE + um ATRÁS  ⇒  eles SERVEM      (o serviço vem de CIMA)
           os DOIS atrás          ⇒  eles RECEBEM     (o serviço vem de BAIXO)

Corre em segundos. Só lê o vídeo em 13/21 instantes. Não corre modelo nenhum.

    python3 ver_cascata.py parada4
    python3 ver_cascata.py barbosa
"""
import sys
import cv2
import numpy as np

import cascata_jogadores as C

VID = C.VID
VIDEO = {"parada4": "../Parada4.mp4", "barbosa": "../BarbosaMeireles.mp4"}[VID]
SAIDA = f"../VER_CASCATA_{VID}.png"

VERDE, AZUL, AMARELO, VERMELHO, BRANCO = (
    (80, 220, 80), (255, 170, 60), (60, 230, 255), (60, 60, 240), (235, 235, 235))


def formacao_de_cima(fr):
    """S3 — a formação lê-se SÓ nos 2 de cima. A de uma dupla DEDUZ a da outra.
       'na rede' = à frente da linha de serviço do lado de cima."""
    cima = [b for b in fr if C.lado(b) == "cima"]
    if len(cima) < 2:
        return "?", "não vejo os 2 de cima"
    na_rede = []
    for b in cima:
        x, y = C.pes(b)
        y_serv = C.ev(C.cal["servico_longe_coef"], x)      # a linha de serviço de cima
        y_rede = C.y_base(x)
        na_rede.append(y > (y_serv + y_rede) / 2)          # entre a linha e a rede
    if sum(na_rede) == 1:
        return "CIMA", "1 na rede + 1 atras  =>  ELES SERVEM"
    if sum(na_rede) == 0:
        return "BAIXO", "os 2 atras  =>  ELES RECEBEM"
    return "?", "os 2 na rede  =>  nao e' formacao de servico"


def main():
    pb0 = __import__("pickle").load(open(C.BOXES, "rb"))["player_boxes"]
    limpo = C.j1_pes_no_poligono(pb0)
    interp, _ = C.j5_continuidade(limpo)
    final = C.j4_dois_por_lado(interp)

    cap = cv2.VideoCapture(VIDEO)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    Hh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    esc = 640 / W
    cw, ch = 640, int(Hh * esc) + 34

    cartas = []
    for i, t in enumerate(C.GT, 1):
        f = int(t * C.FPS)
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ok, img = cap.read()
        if not ok:
            continue

        cv2.polylines(img, [np.array(C._p, np.int32)], True, BRANCO, 2)

        deitadas = [b for b in pb0[f] if b not in final[f]]
        for b in deitadas:                                   # o que a cascata MATOU
            x1, y1, x2, y2 = map(int, b)
            cv2.rectangle(img, (x1, y1), (x2, y2), VERMELHO, 1)

        for b in final[f]:
            x1, y1, x2, y2 = map(int, b)
            inventada = b not in limpo[f]                    # veio da J5
            cor = AMARELO if inventada else (VERDE if C.lado(b) == "cima" else AZUL)
            cv2.rectangle(img, (x1, y1), (x2, y2), cor, 3)
            px, py = map(int, C.pes(b))
            cv2.circle(img, (px, py), 5, cor, -1)            # F3 — os PÉS

        n = len(final[f])
        serve, porque = formacao_de_cima(final[f])
        img = cv2.resize(img, (640, int(Hh * esc)))
        carta = np.zeros((ch, cw, 3), np.uint8)
        carta[34:, :] = img
        bom = (0, 160, 0) if n == 4 else (0, 90, 190)
        cv2.rectangle(carta, (0, 0), (cw, 34), bom, -1)
        cv2.putText(carta, f"#{i:2}  t={t:6.1f}s   {n} jogadores   S3: serve {serve}",
                    (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cartas.append(carta)
        print(f"  #{i:2}  t={t:6.1f}s  {n} jogadores  ·  S3 → serve de {serve:5}  ({porque})")

    cap.release()
    cols = 3
    linhas = [np.hstack(cartas[k:k + cols] + [np.zeros((ch, cw, 3), np.uint8)] *
                        (cols - len(cartas[k:k + cols]))) for k in range(0, len(cartas), cols)]
    cv2.imwrite(SAIDA, np.vstack(linhas))
    print(f"\n👁️  {SAIDA}   ({len(cartas)} serviços)")
    print("   verde=cima · azul=baixo · AMARELO=inventada pela J5 · vermelho=DEITADA FORA")


if __name__ == "__main__":
    main()
