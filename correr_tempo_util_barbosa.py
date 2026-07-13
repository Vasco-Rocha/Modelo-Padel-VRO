#!/usr/bin/env python3
"""
Tempo util do BARBOSA MEIRELES, SEM tocar no gerar_tempo_util.py (Regra Zero).

    python3 correr_tempo_util_barbosa.py            # so os numeros
    python3 correr_tempo_util_barbosa.py --video    # + gera TEMPO_UTIL_BarbosaMeireles.mp4

Faz monkeypatch das constantes (BOLA, BOXES, CAL, N_FRAMES, FPS, VIDEO, GT) e corre
o MESMO pipeline travado. Nao ha ground-truth do Barbosa -> saem os SEGMENTOS
(rallies) e o TEMPO UTIL, mas NAO recall/precisao (nao ha regua para pontuar).
"""
import sys, os, json, pickle, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_tempo_util as gt

# ---- apontar o pipeline ao Barbosa (monkeypatch, nao se edita o ficheiro) ----
gt.FPS = 29.97002997002997
gt.N_FRAMES = 16138
gt.BOLA = "../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv"
gt.BOXES = "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl"
gt.CAL = "calibracao_BarbosaMeireles.json"
gt.VIDEO = "../BarbosaMeireles.mp4"
gt.GT = []  # sem anotacao -> sem recall/precisao

FPS = gt.FPS


def main():
    R, prof = gt.carregar()
    R = gt.vai_e_vem(R)
    tks = gt.tracklets(R)
    CR = gt.cruzamentos(R, tks, prof)
    cal = json.load(open(gt.CAL))
    boxes = pickle.load(open(gt.BOXES, "rb"))["player_boxes"]
    PAN = gt.pancadas(R, cal, boxes)
    FIM = gt.fim_certo(R, cal, boxes)
    RES = gt.ressaltos(R, tks)
    M = gt.rallies(CR, PAN, FIM, RES, R, prof)

    dur_video = gt.N_FRAMES / FPS
    tu = sum(b - a for a, b in M) / FPS

    print("=" * 60)
    print("TEMPO UTIL — BarbosaMeireles  (sem ground-truth: so segmentacao)")
    print("=" * 60)
    print(f"bola: {len(R)} frames com deteccao")
    print(f"tracklets {len(tks)} · cruzamentos {len(CR)} · pancadas {len(PAN)} · "
          f"fins certos {len(FIM)} · quiques {len(RES)}")
    print("-" * 60)
    print(f"{'#':>3}  {'inicio':>8}  {'fim':>8}  {'dur':>6}")
    for i, (a, b) in enumerate(M, 1):
        print(f"{i:>3}  {a/FPS:>7.1f}s  {b/FPS:>7.1f}s  {(b-a)/FPS:>5.1f}s")
    print("-" * 60)
    print(f">>> {len(M)} pontos · tempo util {tu:.1f}s de {dur_video:.0f}s "
          f"({100*tu/dur_video:.0f}%)")
    print("    (sem GT -> nao ha recall/precisao; isto e' a segmentacao crua)")
    print("=" * 60)

    if "--video" in sys.argv:
        out = "../TEMPO_UTIL_BarbosaMeireles.mp4"
        lst = "/tmp/tu_barbosa.txt"
        parts = []
        print("\na gerar o video condensado...")
        # NB: este ffmpeg (Mac) NAO tem o filtro `drawtext` (falta libfreetype),
        # por isso NAO se poe etiqueta -- so se corta e concatena.
        for i, (a, b) in enumerate(M, 1):
            o = f"/tmp/tub{i:02d}.mp4"
            r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                "-ss", f"{a/FPS:.2f}", "-t", f"{(b-a)/FPS:.2f}", "-i", gt.VIDEO,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-an", o],
                capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(o):
                print(f"   ⚠️ falhou o segmento {i}: {r.stderr[:200]}")
                continue
            parts.append(o)
        if not parts:
            print("   ❌ nenhum segmento gerado — aborto o video."); return
        open(lst, "w").write("\n".join(f"file '{p}'" for p in parts) + "\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", lst, "-c", "copy", "/tmp/TEMPO_UTIL_Barbosa.mp4"])
        subprocess.run(["cp", "/tmp/TEMPO_UTIL_Barbosa.mp4", out])
        print(f"-> {out}")


if __name__ == "__main__":
    main()
