#!/usr/bin/env python3
"""
Prova que o .pkl novo (Mac/mps) ENCAIXA no padrao-ouro (Colab/CUDA).

    python3 comparar_pkl.py  <novo.pkl>  <ouro.pkl>

Compara, sem encolher os ombros:
  - nº de frames
  - media de boxes por frame  (o ouro e a referencia)
  - % de frames com >=1 e com >=4
  - IoU box-a-box, frame a frame (emparelhamento guloso por maior IoU)
      -> mediana do IoU dos pares, e % de pares com IoU > 0.9
  - diferenca de CONTAGEM por frame (mps e CUDA podem divergir em floats,
    mas nao podem dar contagens de jogadores diferentes)
"""
import sys, pickle
import numpy as np


def carrega(p):
    d = pickle.load(open(p, "rb"))
    return d["player_boxes"], d.get("fps")


def iou(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


def empareilha(fa, fb):
    """Empareilhamento guloso por maior IoU. Devolve lista de IoUs dos pares."""
    pares = []
    usados = set()
    cand = []
    for i, a in enumerate(fa):
        for j, b in enumerate(fb):
            cand.append((iou(a, b), i, j))
    cand.sort(reverse=True)
    va, vb = set(), set()
    for v, i, j in cand:
        if i in va or j in vb:
            continue
        va.add(i); vb.add(j); pares.append(v)
    return pares


def stats(pb):
    n = len(pb)
    lens = [len(f) for f in pb]
    return {
        "frames": n,
        "media": sum(lens) / max(n, 1),
        "pct1": 100 * sum(1 for l in lens if l >= 1) / max(n, 1),
        "pct4": 100 * sum(1 for l in lens if l >= 4) / max(n, 1),
    }


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    novo, ouro = carrega(sys.argv[1])[0], carrega(sys.argv[2])[0]

    sN, sO = stats(novo), stats(ouro)
    print("=" * 62)
    print(f"{'metrica':<22}{'NOVO (mps)':>18}{'OURO (colab)':>20}")
    print("-" * 62)
    print(f"{'frames':<22}{sN['frames']:>18}{sO['frames']:>20}")
    print(f"{'media boxes/frame':<22}{sN['media']:>18.3f}{sO['media']:>20.3f}")
    print(f"{'% frames >=1':<22}{sN['pct1']:>18.1f}{sO['pct1']:>20.1f}")
    print(f"{'% frames >=4':<22}{sN['pct4']:>18.1f}{sO['pct4']:>20.1f}")
    print("-" * 62)

    m = min(len(novo), len(ouro))
    ious, difs, iguais = [], [], 0
    for i in range(m):
        difs.append(len(novo[i]) - len(ouro[i]))
        if len(novo[i]) == len(ouro[i]):
            iguais += 1
        ious.extend(empareilha(novo[i], ouro[i]))
    ious = np.array(ious) if ious else np.array([0.0])
    difs = np.array(difs)

    print(f"frames comparados      : {m}")
    print(f"contagem IGUAL por frame: {iguais} ({100*iguais/max(m,1):.1f}%)")
    print(f"dif. de contagem  media : {difs.mean():+.3f}  "
          f"(min {difs.min():+d}, max {difs.max():+d})")
    print(f"frames c/ contagem dif. : {int((difs!=0).sum())}")
    print(f"pares emparelhados      : {len(ious)}")
    print(f"IoU mediano dos pares   : {np.median(ious):.3f}")
    print(f"IoU medio dos pares     : {ious.mean():.3f}")
    print(f"% pares com IoU > 0.9   : {100*(ious>0.9).mean():.1f}%")
    print(f"% pares com IoU > 0.5   : {100*(ious>0.5).mean():.1f}%")
    print("=" * 62)


if __name__ == "__main__":
    main()
