#!/usr/bin/env python3
"""
🎬 VER UM PONTO — O M2 A CORRER, PELAS REGRAS DO VASCO        (14 jul 2026)

    python3 ver_ponto_m2.py barbosa 13

Pega num PONTO (do serviço ao fim, ground-truth do Vasco) e desenha, frame a frame:

  🧱 F2   as DUAS COSTURAS DA PAREDE, por lado.   ⚠️ NÃO é a linha de serviço.
          (a linha de serviço aparece a PONTILHADO, só para se VER que são outra coisa)
  🦶 F3+J16  o PÉ de cada jogador — a aresta inferior, com a margem da J16
  📏 D19  "passou a linha?" é BINÁRIO. Nenhum limiar, nenhum ponto médio.
  📏 D20  EM CIMA DA LINHA ⇒ conta como ATRÁS.
  👥 F1   a fase é da EQUIPA, nunca do jogador.
  🧱 F2   a REGRA DAS DUAS BOXES:  DEFESA só se forem OS DOIS atrás
                                   ATAQUE só se forem OS DOIS à frente
                                   TRANSIÇÃO = tudo o resto (o estado-resíduo)
  🚫 D2/D4  se não vejo os DOIS de uma equipa ⇒ escrevo "—". NÃO INVENTO.

E por baixo, a TIMELINE do ponto inteiro — a sequência de fases das duas equipas.

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py. Não corre modelo nenhum:
   lê as boxes JÁ DETETADAS (.pkl) e aplica-lhes as REGRAS DO JOGO.
"""
import sys, pickle
from pathlib import Path
import cv2, numpy as np

VID = sys.argv[1] if len(sys.argv) > 1 else "barbosa"
N_PT = int(sys.argv[2]) if len(sys.argv) > 2 else 13

sys.argv = [sys.argv[0], VID]          # a cascata lê o vídeo do argv
import cascata_jogadores as C
from fases_m2 import fase_do_jogador, fase_da_equipa, LINHAS

RAIZ = Path(__file__).parent

# ⚠️ os PONTOS (início, fim) — ground-truth do VASCO. Um por vídeo, nunca se partilham.
PONTOS = {
    "barbosa": [(13.6, 23.7), (33.9, 37.3), (40.3, 44.7), (54.5, 62.4), (69.8, 73.6),
                (83.3, 96.0), (135.0, 139.1), (155.0, 157.6), (162.9, 171.8),
                (188.3, 192.2), (196.0, 202.0), (227.2, 230.8), (242.3, 245.4),
                (257.1, 266.0), (298.3, 306.8), (326.1, 337.3), (352.1, 357.3),
                (367.9, 371.1), (377.9, 384.3), (406.8, 416.1), (526.0, 533.9)],
}
MP4 = {"barbosa": RAIZ / "../BarbosaMeireles.mp4", "parada4": RAIZ / "../Parada4.mp4"}

COR = {"DEFESA": (80, 200, 90), "TRANSICAO": (40, 190, 250), "ATAQUE": (70, 90, 240),
       None: (150, 150, 150)}          # BGR
F = cv2.FONT_HERSHEY_SIMPLEX


def curva(img, coef, cor, esp=2, pont=False):
    """Desenha uma linha da calibração (é uma PARÁBOLA em x — a curvatura da lente, C5/C10)."""
    W = img.shape[1]
    pts = [(x, int(C.ev(C.cal[coef], x))) for x in range(0, W, 6)]
    for i in range(len(pts) - 1):
        if pont and i % 2:
            continue
        cv2.line(img, pts[i], pts[i + 1], cor, esp, cv2.LINE_AA)


def main():
    t0, t1 = PONTOS[VID][N_PT - 1]
    fps = C.FPS
    f0, f1 = int(t0 * fps), int(t1 * fps)

    # 👥 a cascata, pela ORDEM dele: J1 → J5 → J4 (o «2 por lado» é O ÚLTIMO)
    pb = C.j4_dois_por_lado(C.j5_continuidade(C.j1_pes_no_poligono(
        pickle.load(open(C.BOXES, "rb"))["player_boxes"]))[0])

    cap = cv2.VideoCapture(str(MP4[VID]))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    Hh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    BARRA = 74
    out = cv2.VideoWriter(str(RAIZ / f"../M2_PONTO{N_PT}_{VID}.mp4"),
                          cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, Hh + BARRA))

    cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
    serie = []                                    # (frame, fase_cima, fase_baixo)

    print("=" * 78)
    print(f"🎬 PONTO {N_PT} — {VID.upper()}   {t0:.1f}s → {t1:.1f}s   "
          f"({t1-t0:.1f}s · {f1-f0} frames)")
    print("=" * 78)
    print("   as linhas são as COSTURAS DA PAREDE (F2). D19: a linha é a linha.")
    print("   D20: em cima da linha ⇒ ATRÁS.  Se não vejo os DOIS ⇒ '—' (D2/D4).\n")
    print("      t       CIMA         BAIXO")
    print("   " + "-" * 40)

    for f in range(f0, f1 + 1):
        ok, img = cap.read()
        if not ok:
            break
        fr = pb[f] if f < len(pb) else []
        fc, fb = fase_da_equipa(fr, "cima"), fase_da_equipa(fr, "baixo")
        serie.append((f, fc, fb))

        # 🧱 F2 — as costuras da parede. A GROSSO, porque são ELAS que mandam.
        for l in ("cima", "baixo"):
            frente, tras = LINHAS[l]
            curva(img, tras, (90, 90, 90), 2)          # a costura de TRÁS
            curva(img, frente, (200, 200, 200), 2)     # a costura da FRENTE
        # ⚠️ a linha de SERVIÇO, a pontilhado — só para se VER que NÃO é esta
        curva(img, "servico_perto_coef", (110, 60, 160), 1, pont=True)
        curva(img, "servico_longe_coef", (110, 60, 160), 1, pont=True)
        curva(img, "rede_base_coef", (200, 120, 40), 1)

        # 🦶 os jogadores — box + o PÉ (F3 + J16) + a fase INDIVIDUAL
        for b in fr:
            x, y = C.pes(b)
            fj = fase_do_jogador(b)
            c = COR[fj]
            cv2.rectangle(img, (int(b[0]), int(b[1])), (int(b[2]), int(b[3])), c, 2)
            cv2.drawMarker(img, (int(x), int(y)), c, cv2.MARKER_CROSS, 13, 2)
            cv2.putText(img, fj[:3], (int(b[0]), int(b[1]) - 5), F, .45, c, 1, cv2.LINE_AA)

        # 👥 F1 — a fase da EQUIPA, em cima de tudo
        for i, (nome, fx) in enumerate((("CIMA", fc), ("BAIXO", fb))):
            cv2.putText(img, f"{nome}: {fx or '—  (nao vejo os 2)'}", (14, 28 + 26 * i),
                        F, .72, COR[fx], 2, cv2.LINE_AA)
        cv2.putText(img, f"ponto {N_PT}   t={f/fps:6.1f}s   +{f/fps-t0:4.1f}s",
                    (W - 300, 28), F, .6, (255, 255, 255), 2, cv2.LINE_AA)

        # 📊 a TIMELINE, por baixo — a sequência do ponto inteiro
        barra = np.full((BARRA, W, 3), 22, np.uint8)
        for k, (_, a, bq) in enumerate(serie):
            x = int(k / max(f1 - f0, 1) * W)
            xn = int((k + 1) / max(f1 - f0, 1) * W) + 1
            cv2.rectangle(barra, (x, 22), (xn, 40), COR[a], -1)
            cv2.rectangle(barra, (x, 46), (xn, 64), COR[bq], -1)
        cv2.putText(barra, "CIMA", (4, 18), F, .4, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(barra, "BAIXO", (4, 60), F, .4, (200, 200, 200), 1, cv2.LINE_AA)
        for i, (n, c) in enumerate((("DEFESA", "DEFESA"), ("TRANSICAO", "TRANSICAO"),
                                    ("ATAQUE", "ATAQUE"))):
            cv2.rectangle(barra, (W - 300 + i * 100, 6), (W - 288 + i * 100, 18), COR[c], -1)
            cv2.putText(barra, n[:5], (W - 284 + i * 100, 17), F, .38, (210, 210, 210), 1)
        out.write(np.vstack([img, barra]))

    cap.release()
    out.release()

    # ---- a timeline, em texto: só as MUDANÇAS (o que interessa ver)
    ant = None
    for f, a, b in serie:
        if (a, b) != ant:
            print(f"   {f/fps:6.1f}s   {str(a):11}  {str(b):11}")
            ant = (a, b)
    cego = sum(a is None or b is None for _, a, b in serie)
    print("   " + "-" * 40)
    print(f"   cego (não vejo os 2 de uma equipa) em {cego}/{len(serie)} frames "
          f"({cego/len(serie)*100:.0f}%)")
    print(f"\n🎬  ../M2_PONTO{N_PT}_{VID}.mp4")


if __name__ == "__main__":
    main()
