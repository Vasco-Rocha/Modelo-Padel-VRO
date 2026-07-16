#!/usr/bin/env python3
"""
DE QUE LADO DA LINHA DO MEIO (em largura) ESTÁ O SERVIDOR?   *** SÓ MEDE. Zero bola. ***

    python3 servidor_lado_centro.py [parada4|barbosa] [--frame N_do_servico]

Para cada SERVIÇO VALIDADO (o detetor de serviço, formação/jogadores):
  · o servidor = o jogador ATRASADO da equipa que serve (D.servidor)
  · o lado = os seus PÉS (F3) à ESQUERDA ou à DIREITA da linha central
    (a central é uma linha, não um x fixo: cx(y) = polyval(centro_coef_em_y, y))

⚖️ D19 — comparação BINÁRIA contra a linha. Nada de ponto médio nem margem.
⚠️ Leitura pura. O gerar_tempo_util.py NÃO é tocado.
"""
import sys, json, subprocess
import numpy as np

VIDEO = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "parada4"
import cascata_jogadores as C
C.configurar(VIDEO)
import detetor_servico as D

MP4 = {"parada4": "../Parada4.mp4", "barbosa": "../BarbosaMeireles.mp4"}[VIDEO]
cal = C.cal
cx = lambda y: float(np.polyval(cal["centro_coef_em_y"], y))


def servidores_validados():
    """Devolve [(n, t_gt, lado_serve, frame, box_servidor, px, py, cx_py, ESQ/DIR)]."""
    pb = D.cascata(VIDEO)
    S, _ = D.servicos(VIDEO, D.REGRAS, pb)
    out = []
    for n, t in enumerate(C.GT, 1):
        fa, fb = int((t - 3) * C.FPS), int((t + 0.5) * C.FPS)
        hit = next(((a, b, l) for a, b, l in S if not (b < fa or a > fb)), None)
        if not hit:
            out.append((n, t, None, None, None, None, None, None, "PERDIDO"))
            continue
        a, b, l = hit
        # servidor num frame estável: o fim do bloco (a formação já está montada)
        f = b
        srv = D.servidor(pb[f], l)
        if srv is None:                       # recua até haver box do lado que serve
            for g in range(b, a - 1, -1):
                srv = D.servidor(pb[g], l)
                if srv is not None:
                    f = g
                    break
        if srv is None:
            out.append((n, t, l, f, None, None, None, None, "SEM BOX"))
            continue
        px, py = C.pes(srv)
        cxy = cx(py)
        lado = "ESQUERDA" if px < cxy else "DIREITA"
        out.append((n, t, l, f, srv, px, py, cxy, lado))
    return out


def desenhar(reg, path_out):
    """Extrai o frame do servico `reg` e desenha a central + o servidor."""
    from PIL import Image, ImageDraw, ImageFont
    n, t, l, f, srv, px, py, cxy, lado = reg
    ts = f / C.FPS
    tmp = f"/tmp/_frame_{VIDEO}_{n}.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{ts:.3f}",
                    "-i", MP4, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB")
    d = ImageDraw.Draw(im)
    W, H = im.size
    # a LINHA CENTRAL (curva) — amarela
    pts = [(cx(y), y) for y in range(0, H)]
    d.line(pts, fill=(255, 220, 0), width=3)
    # todos os jogadores, ténue
    pb = D.cascata(VIDEO)
    for bx in pb[f]:
        d.rectangle(list(bx), outline=(90, 90, 90), width=1)
    # o SERVIDOR, forte
    d.rectangle(list(srv), outline=(255, 40, 40), width=4)
    fx, fy = px, py
    d.ellipse([fx - 6, fy - 6, fx + 6, fy + 6], fill=(255, 40, 40))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = fs = ImageFont.load_default()
    txt = f"SERVICO {n}  t={t:.1f}s  serve {l.upper()}  ->  SERVIDOR a {lado} da central"
    d.rectangle([0, 0, W, 30], fill=(0, 0, 0))
    d.text((6, 5), txt, fill=(255, 255, 255), font=font)
    d.text((min(px + 10, W - 160), max(py - 24, 34)), f"SERVIDOR\n{lado}", fill=(255, 40, 40), font=fs)
    im.save(path_out)
    return path_out


def main():
    regs = servidores_validados()
    print("\n" + "=" * 84)
    print(f"SERVIDOR — de que lado da LINHA CENTRAL (largura)?   {VIDEO.upper()}   (zero bola)")
    print("=" * 84)
    print(f"  {'#':>2} {'t(s)':>7} {'serve':>6} {'pe_x':>7} {'central_x':>10} {'LADO':>10}")
    print("  " + "-" * 60)
    for n, t, l, f, srv, px, py, cxy, lado in regs:
        if srv is None:
            print(f"  {n:>2} {t:>7.1f} {str(l):>6} {'—':>7} {'—':>10} {lado:>10}")
        else:
            print(f"  {n:>2} {t:>7.1f} {l:>6} {px:>7.0f} {cxy:>10.0f} {lado:>10}")
    esq = sum(1 for r in regs if r[8] == "ESQUERDA")
    dir_ = sum(1 for r in regs if r[8] == "DIREITA")
    print("  " + "-" * 60)
    print(f"  ESQUERDA: {esq}   ·   DIREITA: {dir_}   ·   validados: {esq+dir_}/{len(regs)}")

    # frame de amostra (--frame N, default o 1.º válido)
    alvo = None
    if "--frame" in sys.argv:
        alvo = int(sys.argv[sys.argv.index("--frame") + 1])
    reg = next((r for r in regs if (alvo and r[0] == alvo) or (not alvo and r[4] is not None)), None)
    if reg and reg[4] is not None:
        out = f"/sessions/upbeat-confident-cori/mnt/outputs/servidor_{VIDEO}_s{reg[0]}.png"
        desenhar(reg, out)
        print(f"\n  🖼️  frame de amostra (serviço {reg[0]}): {out}")


if __name__ == "__main__":
    main()
