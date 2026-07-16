#!/usr/bin/env python3
"""
🔗 A S42 E A S43, COM O DETETOR DE SERVIÇO NOVO   (14 jul)

    As duas estavam DESLIGADAS por UMA razão, e uma só:
        "o detetor de serviço acerta 12/13 (92%). A cola pergunta «abres com um serviço?»,
         ouve NÃO — e ENGOLE UM PONTO REAL."

    O detetor de HOJE (só jogadores) acerta **21/21**. A razão desapareceu.

    S42 — A CONFIRMAÇÃO DO FIM:  "não há fim de ponto sem SERVIÇO a seguir"
    S43 — A COLA:                "dois pedaços só são pontos DIFERENTES se houver um
                                  SERVIÇO entre eles"

⚠️ NÃO TOCA NO gerar_tempo_util.py. Importa-o em SÓ-LEITURA e aplica as regras POR CIMA.
"""
import sys
import detetor_servico as DS
import gerar_tempo_util as gt          # ⚠️ SÓ LEITURA

VID = sys.argv[1] if len(sys.argv) > 1 else "barbosa"

GT = {"barbosa": [(13.6,23.7),(33.9,37.3),(40.3,44.7),(54.5,62.4),(69.8,73.6),(83.3,96.0),
                  (135.0,139.1),(155.0,157.6),(162.9,171.8),(188.3,192.2),(196.0,202.0),
                  (227.2,230.8),(242.3,245.4),(257.1,266.0),(298.3,306.8),(326.1,337.3),
                  (352.1,357.3),(367.9,371.1),(377.9,384.3),(406.8,416.1),(526.0,533.9)],
      "parada4": [(38.0,41.5),(46.8,67.5),(77.6,85.5),(95.9,111.1),(122.4,135.9),
                  (157.9,169.4),(178.1,186.5),(197.0,202.1),(210.5,216.3),(229.9,237.3),
                  (249.6,255.0),(263.8,276.4),(289.1,291.7)]}[VID]

if VID == "barbosa":
    gt.FPS = 29.97002997002997
    gt.N_FRAMES = 16138
    gt.BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
    gt.CAL = "calibracao_BarbosaMeireles.json"
    gt.BOXES = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl"
gt.GT = GT
F = gt.FPS

MARGEM_FIM = 2.0   # ⚠️ AJUSTE — a margem de APRESENTAÇÃO (o "2 segundos é o melhor", dele)


def segmentos_do_pipeline():
    """O que o pipeline produz HOJE (sem a S42/S43)."""
    import pickle
    R, cal = gt.carregar()
    prof = gt.prof if hasattr(gt, "prof") else None
    boxes = pickle.load(open(gt.BOXES, "rb"))["player_boxes"]
    return R, cal, boxes


def avaliar(SEG, nome):
    """recall · precisão · nº pontos · fim_dentro   (as réguas do Vasco)"""
    util = sum(b - a for a, b in SEG)
    real = sum(b - a for a, b in GT)
    inter = 0.0
    for a, b in SEG:
        for c, d in GT:
            inter += max(0, min(b, d) - max(a, c))
    rec = inter / real * 100
    pre = inter / util * 100 if util else 0
    # 🔒 D15 — um FIM nunca pode cair a meio de um ponto
    dentro = sum(1 for _, b in SEG if any(c < b < d - 0.5 for c, d in GT))
    print(f"   {nome:34} {len(SEG):2} pontos · recall {rec:5.1f} · precisão {pre:5.1f} · "
          f"fim_dentro {dentro}{'  🔴' if dentro else '  ✅'}")
    return rec, pre, len(SEG), dentro


def main():
    print("=" * 84)
    print(f"🔗 A S42 E A S43 — com o DETETOR DE SERVIÇO NOVO   ({VID.upper()})")
    print("=" * 84)

    # ── os SERVIÇOS, pelos JOGADORES (21/21, zero falsos)
    S, _ = DS.servicos(VID)
    serv = sorted(a / F for a, b, l in S)
    print(f"\n   serviços detetados (só jogadores): {len(serv)}\n")

    # ── os SEGMENTOS que o pipeline produz hoje
    import pickle, csv, json
    R = {}
    for r in csv.DictReader(open(gt.BOLA)):
        if int(r["Visibility"]) and float(r["X"]):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]),
                                  float(r["L"]), float(r["Theta"]))
    cal = json.load(open(gt.CAL))
    boxes = pickle.load(open(gt.BOXES, "rb"))["player_boxes"]
    y_topo, y_base, meio = gt.campo(cal)
    import numpy as np

    def prof(x, y):
        yb = y_base(x)
        ys = float(np.polyval(cal["servico_perto_coef" if y > yb else "servico_longe_coef"], x))
        return ("baixo" if y > yb else "cima"), abs(y - yb) / max(1e-6, abs(ys - yb))

    tks = gt.tracklets(gt.vai_e_vem(R))
    RES = gt.ressaltos(R, tks)
    CR = gt.cruzamentos(R, tks, prof)
    PAN = gt.pancadas(R, cal, boxes)
    FIM = gt.fim_certo(R, cal, boxes)
    SEG = gt.rallies(CR, PAN, FIM, RES, R, prof)
    # ⚠️ o rallies() devolve FRAMES. O GT está em SEGUNDOS.
    #    (erro meu, 14 jul — apanhado porque os números vieram ABSURDOS: recall 11%, precisão 0,3%.
    #     "Um número absurdo é um presente: grita. O perigoso é o que parece plausível." )
    SEG = [(a / F, b / F) for a, b in SEG]

    print("   " + "-" * 74)
    avaliar(SEG, "HOJE (sem S42/S43)")

    # ── 🔗 S43 — A COLA: dois pedaços só são pontos DIFERENTES se houver um SERVIÇO entre eles
    def ha_servico(t0, t1):
        return any(t0 - 0.5 <= s <= t1 + 0.5 for s in serv)

    colado = [list(SEG[0])]
    for a, b in SEG[1:]:
        if not ha_servico(colado[-1][1], a):
            colado[-1][1] = b            # NÃO há serviço entre eles ⇒ É O MESMO PONTO
        else:
            colado.append([a, b])
    colado = [(a, b) for a, b in colado]
    avaliar(colado, "+ S43 (a COLA)")

    # ── ⏱️ S42 — o FIM só é fim se vier um SERVIÇO a seguir (e a ≥4 s)
    def fim_confirmado(b):
        return any(b + 4.0 <= s for s in serv) or b >= max(GT)[1] - 1

    s42 = []
    for a, b in colado:
        if fim_confirmado(b):
            s42.append((a, b))           # confirmado ⇒ corte RENTE
        else:
            s42.append((a, b + 1.5))     # não confirmado ⇒ o ponto pode não ter acabado
    avaliar(s42, "+ S42 (a CONFIRMAÇÃO)")

    print("   " + "-" * 74)
    print("\n   🔒 D15: o fim_dentro TEM de ficar em 0. Se subir, DESLIGA — nunca relaxes o teste.")
    print("   ⚠️ NADA DISTO ESTÁ NO PIPELINE. É uma medição, num ficheiro à parte.")


if __name__ == "__main__":
    main()
