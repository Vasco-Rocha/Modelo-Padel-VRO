#!/usr/bin/env python3
"""
JSON dos jogadores (Colab / padel_analytics)  ->  o .pkl que o pipeline lê.

    python3 json_para_pkl.py  players_detections_X.json  ../dados_X/player_boxes_X.pkl

PORQUE ISTO EXISTE
------------------
Este passo foi feito À MÃO numa conversa antiga e o script PERDEU-SE. Ninguém sabia como o
`player_boxes_parada4.pkl` tinha nascido. É exactamente o tipo de buraco que come meia manhã.
(13 jul 2026 — a mesma doença das regras que se perdem entre a ideia e o código.)

O FORMATO QUE O PIPELINE ESPERA (não inventar — é este):
    { "player_boxes": [ [ (x1,y1,x2,y2), ... ]  por frame ],   # lista, 1 entrada por frame
      "fps": float }
"""
import sys, json, pickle


def extrair_boxes(obj, n_frames=None):
    """Aceita os feitios em que o JSON do padel_analytics pode vir. Não adivinha: falha alto."""
    # feitio A: já é uma lista por frame
    if isinstance(obj, list):
        def _box(b):
            # cada deteção pode ser uma lista [x1,y1,x2,y2,...] OU um dict do
            # PlayerTracker.serialize(): {"id":.., "xyxy":[...], "confidence":..}
            if isinstance(b, dict):
                v = b.get("xyxy", b.get("bbox", b.get("box", b.get("xyah"))))
                return tuple(map(float, v[:4]))
            return tuple(map(float, b[:4]))
        return [[_box(b) for b in (f or [])] for f in obj]

    if isinstance(obj, dict):
        # feitio B: {"0": [...], "1": [...]}  ou  {"frames": {...}}
        d = obj.get("frames", obj)
        if all(str(k).lstrip("-").isdigit() for k in d):
            n = (n_frames or max(int(k) for k in d) + 1)
            out = [[] for _ in range(n)]
            for k, v in d.items():
                i = int(k)
                if 0 <= i < n:
                    out[i] = [tuple(map(float, b[:4])) for b in (v or [])]
            return out
        # feitio C: {"detections": [{"frame": i, "bbox": [...]}]}
        for chave in ("detections", "players", "player_detections"):
            if chave in obj:
                det = obj[chave]
                n = (n_frames or max(int(x.get("frame", x.get("frame_id", 0)))
                                     for x in det) + 1)
                out = [[] for _ in range(n)]
                for x in det:
                    i = int(x.get("frame", x.get("frame_id", 0)))
                    b = x.get("bbox", x.get("box", x.get("xyxy")))
                    if b and 0 <= i < n:
                        out[i].append(tuple(map(float, b[:4])))
                return out

    raise SystemExit(
        "❌ Não reconheci o feitio deste JSON.\n"
        "   NÃO vou adivinhar (adivinhar é como se perdem as regras).\n"
        f"   Chaves de topo: {list(obj)[:8] if isinstance(obj, dict) else type(obj).__name__}\n"
        "   Mostra este output ao Claude e ele escreve o parser certo."
    )


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    fps = float(sys.argv[3]) if len(sys.argv) > 3 else None

    obj = json.load(open(src))
    if fps is None and isinstance(obj, dict):
        fps = float(obj.get("fps", 0) or 0)
    if not fps:
        fps = float(input("FPS do vídeo (ex: 29.97): ").strip())

    boxes = extrair_boxes(obj)
    pickle.dump({"player_boxes": boxes, "fps": fps}, open(dst, "wb"))

    com = sum(1 for f in boxes if f)
    quatro = sum(1 for f in boxes if len(f) >= 4)
    n = len(boxes)
    print(f"✅ {dst}")
    print(f"   frames: {n}   ·   fps: {fps}")
    print(f"   com jogadores: {com} ({100*com/max(n,1):.1f}%)")
    print(f"   com os 4:      {quatro} ({100*quatro/max(n,1):.1f}%)   "
          f"<- no Parada4 eram 21,8% (a câmara cortava os de baixo)")
    if quatro / max(n, 1) < 0.30:
        print("\n   ⚠️ A câmara continua a não ver os 4 jogadores na maior parte dos frames.")
        print("      Isso BLOQUEIA: formação de serviço (S2/S3), inatividade dos jogadores, e metade do M2.")


if __name__ == "__main__":
    main()
