#!/usr/bin/env python3
"""
Desenha as boxes dos jogadores por cima do video. O Vasco ve com os olhos dele.

    python3 desenhar_boxes.py  <video.mp4>  <player_boxes.pkl>  <saida.mp4>  [--max N]

Le o .pkl { "player_boxes": [ [(x1,y1,x2,y2),...] por frame ], "fps": float }
e escreve um MP4 com um retangulo por deteccao (BRUTO, ainda com publico -- e para
o Vasco ver o que o detetor apanhou, incluindo o que as regras vao limpar depois).
"""
import sys, pickle
import cv2


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 3:
        print(__doc__); sys.exit(1)
    video, pkl, out = args[0], args[1], args[2]
    maxn = None
    if "--max" in sys.argv:
        maxn = int(sys.argv[sys.argv.index("--max") + 1])

    boxes = pickle.load(open(pkl, "rb"))["player_boxes"]

    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vw = cv2.VideoWriter(out, cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if maxn is not None and i >= maxn:
            break
        fb = boxes[i] if i < len(boxes) else []
        for b in fb:
            x1, y1, x2, y2 = [int(v) for v in b[:4]]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.putText(frame, f"frame {i}  jogadores(bruto): {len(fb)}",
                    (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        vw.write(frame)
        i += 1

    cap.release(); vw.release()
    print(f"✅ video: {out}  ({i} frames desenhados, fps {fps:.2f})")


if __name__ == "__main__":
    main()
