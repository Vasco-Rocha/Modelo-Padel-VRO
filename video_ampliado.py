#!/usr/bin/env python3
"""
O TEMPO ÚTIL COM A REGRA AMPLIADA (MIN_PROF 0.35 -> 0.15).  *** SÓ LÊ. ***

O Vasco quer VER o que muda. Este script gera a compilação do tempo útil com a faixa de
passagem ampliada — exatamente o que o pipeline produziria SE mudássemos.

⚠️ O gerar_tempo_util.py NÃO é alterado. Isto é uma cópia em memória e escreve um ficheiro NOVO.

O QUE MUDA:
   · 13 -> 14 segmentos  (aparece o de 281–285s, que o Vasco já viu e disse ser lixo)
   · os pontos 10 e 11 deixam de estar pendurados numa travessia única (1 -> 3)
   · recall 96,3 -> 96,8   ·   precisão 95,9 -> 91,9

Cada clip vem etiquetado: quantas travessias tem, e se é ponto real ou LIXO.
"""
import subprocess, json, pickle, os
import gerar_tempo_util as G

MP = 0.15
SAIDA = "../TEMPO_UTIL_AMPLIADO_MINPROF015.mp4"


def main():
    R, prof = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN   = G.pancadas(R2, cal, boxes)
    FIM   = G.fim_certo(R2, cal, boxes)

    orig = G.MIN_PROF
    G.MIN_PROF = MP
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    r  = G.avaliar(M)
    G.MIN_PROF = orig

    print(f"\nMIN_PROF {orig} -> {MP}")
    print(f">>> {r['n']} segmentos (reais: {len(G.GT)}) | {r['tempo']:.1f}s")
    print(f">>> RECALL {r['recall']:.1f}%  PRECISAO {r['precisao']:.1f}%  F1 {r['f1']:.1f}\n")

    partes = []
    for i, (a, b) in enumerate(M, 1):
        t0, t1 = a / G.FPS, b / G.FPS
        gt = next((k for k, (g0, g1) in enumerate(G.GT, 1) if t0 <= g1 and t1 >= g0), None)
        n_cr = sum(1 for c in CR if a <= c <= b)
        if gt:
            txt = f"ponto {gt}/13   {t0:.0f}s   travessias: {n_cr}"
            cor, caixa = "white", "black@0.6"
        else:
            txt = f"*** LIXO ***   {t0:.0f}s   travessias: {n_cr}   (o segmento NOVO)"
            cor, caixa = "yellow", "red@0.8"
        out = f"/tmp/amp{i:02d}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                        "-ss", f"{t0:.2f}", "-t", f"{t1-t0:.2f}", "-i", G.VIDEO,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-an",
                        "-vf", f"drawtext=text='{txt}':x=10:y=10:fontsize=22:"
                               f"fontcolor={cor}:box=1:boxcolor={caixa}", out], check=True)
        partes.append(out)
        print(f"  {i:>2}. {t0:6.1f}–{t1:6.1f}s  ({t1-t0:4.1f}s)  travessias {n_cr:>2}  "
              f"{'ponto '+str(gt) if gt else '🚨 LIXO'}")

    lst = "\n".join(f"file '{p}'" for p in partes)
    open("/tmp/amp.txt", "w").write(lst + "\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", "/tmp/amp.txt", "-c", "copy", SAIDA], check=True)
    print(f"\n-> {SAIDA}")
    print("\n⚠️ O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
