#!/usr/bin/env python3
"""
O 14.º SEGMENTO — o que aparece quando se baixa o MIN_PROF.  *** SÓ LÊ. ***

Toda a queda de precisão (95,9 -> 91,9) vem de UM segmento novo.
⚠️ NÃO LHE CHAMAR LIXO ANTES DE O VER. O "falso" dos 289s era um PONTO A SÉRIO — e a precisão
   andou um dia inteiro a castigar-nos por ACERTAR.  (feedback_desconfiar_do_ground_truth)

Isto: encontra-o, diz o que tem lá dentro (travessias, pancadas), e corta o CLIP para o Vasco ver.
"""
import json, pickle, subprocess
import gerar_tempo_util as G

MP_NOVO = 0.15
ORIG = G.MIN_PROF


def segs(mp, R2, tks, prof, PAN, FIM):
    G.MIN_PROF = mp
    CR = G.cruzamentos(R2, tks, prof)
    return G.rallies(CR, PAN, FIM), CR


def main():
    R, prof = G.carregar()
    cal = json.load(open(G.CAL))
    R2  = G.vai_e_vem(R)
    tks = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R2, cal, boxes)
    FIM = G.fim_certo(R2, cal, boxes)

    M_a, CR_a = segs(ORIG,    R2, tks, prof, PAN, FIM)
    M_b, CR_b = segs(MP_NOVO, R2, tks, prof, PAN, FIM)

    print(f"\nMIN_PROF {ORIG}: {len(M_a)} segmentos   |   MIN_PROF {MP_NOVO}: {len(M_b)} segmentos\n")

    # que segmento do B não tem correspondente no A?
    def sobrepoe(s, lista):
        a, b = s
        return any(a <= d and b >= c for c, d in lista)

    novos = [s for s in M_b if not sobrepoe(s, M_a)]
    print("=" * 82)
    for a, b in M_b:
        t0, t1 = a / G.FPS, b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        n_cr  = sum(1 for c in CR_b if a <= c <= b)
        n_pan = sum(1 for q in PAN if a <= q <= b)
        etiq = f"ponto {gt} do GT" if gt else "🚨 NÃO ESTÁ NO GROUND-TRUTH"
        novo = "  ⬅️ NOVO" if (a, b) in [tuple(s) for s in novos] else ""
        print(f"  {t0:7.1f}s – {t1:7.1f}s  ({t1-t0:5.1f}s)  travessias {n_cr:>2}  "
              f"pancadas {n_pan:>3}   {etiq}{novo}")
    print("=" * 82)

    G.MIN_PROF = ORIG

    if not novos:
        print("\n(nenhum segmento novo — a diferença está nas fronteiras dos existentes)\n")
        return

    print(f"\n⇒ {len(novos)} segmento(s) fora do GT. A cortar o clip para o Vasco VER...\n")
    for i, (a, b) in enumerate(novos, 1):
        t0, t1 = a / G.FPS, b / G.FPS
        # 3s de contexto antes e depois
        ini, dur = max(0, t0 - 3), (t1 - t0) + 6
        out = f"../O_14o_SEGMENTO_{t0:.0f}s.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ini:.2f}",
                        "-t", f"{dur:.2f}", "-i", G.VIDEO, "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "23", "-an", "-vf",
                        f"drawtext=text='SEGMENTO {t0:.0f}-{t1:.0f}s   (3s de contexto antes/depois)"
                        f"':x=10:y=10:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.7",
                        out], check=True)
        print(f"   -> {out}")
    print("\n👀 É um PONTO A SÉRIO que falta ao ground-truth, ou é lixo? Só o Vasco sabe.\n")


if __name__ == "__main__":
    main()
