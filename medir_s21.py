#!/usr/bin/env python3
"""
MEDIR a S21 — a ALTERNÂNCIA DAS TRAVESSIAS.   *** SÓ MEDE. NÃO LIGA NADA. ***

A regra (Vasco, docs/SPEC_M1_TEMPO_UTIL.md):
    "Cada travessia da rede implica uma pancada — a FÍSICA garante-a.
     Travessias alternadas e sustentadas = RALLY.
     ENTRE PONTOS a bola cruza a rede no MÁXIMO UMA VEZ (devolvida ao servidor).
     Não faz vaivém."

REDUÇÃO (13 jul): a alternância é AUTOMÁTICA. A bola não pode cruzar a rede duas vezes no
mesmo sentido sem ter voltado pelo meio. ⇒ não é preciso saber direções.
    **A S21 reduz-se a UMA CONTAGEM: quantas travessias tem este grupo?**

O QUE ISTO MEDE:
  para cada grupo de travessias que o `rallies()` já forma (mesmo agrupamento, mesmo SILENCIO),
  quantas travessias tem, e se cai DENTRO de um ponto real do GT ou FORA (intervalo).

A PERGUNTA QUE DECIDE:  ** algum PONTO REAL tem <= 1 travessia? **
  - se NÃO tiver nenhum  -> a S21 separa jogo de intervalo LIMPAMENTE
  - se tiver (o ACE!)    -> a S21 tem de PONTUAR, nunca VETAR   (lei D18 do Vasco)

⛔ NÃO altera o gerar_tempo_util.py. Importa-o e usa as funções DELE, tal como estão.
"""
import numpy as np
import json, pickle
import gerar_tempo_util as G


def grupos_de_travessias(CR):
    """O MESMO agrupamento do rallies() — copiado à letra, para medir o que ele vê."""
    grp = [[CR[0]]]
    for c in CR[1:]:
        if c - grp[-1][-1] <= G.SILENCIO * G.FPS:
            grp[-1].append(c)
        else:
            grp.append([c])
    return grp


def ponto_do_gt(a, b):
    """Este grupo (frames a..b) sobrepõe-se a que ponto real? Devolve o nº, ou None."""
    ta, tb = a / G.FPS, b / G.FPS
    for k, (g0, g1) in enumerate(G.GT, 1):
        if ta <= g1 and tb >= g0:          # há sobreposição
            return k
    return None


def main():
    R, prof = G.carregar()
    R   = G.vai_e_vem(R)
    tks = G.tracklets(R)
    CR  = G.cruzamentos(R, tks, prof)
    cal = json.load(open(G.CAL))
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]
    PAN = G.pancadas(R, cal, boxes)

    grp = grupos_de_travessias(CR)

    print(f"\ncruzamentos: {len(CR)}   |   grupos formados: {len(grp)}   |   pontos reais: {len(G.GT)}\n")
    print("=" * 78)
    print(f"{'grupo':>5} {'inicio':>8} {'fim':>8} {'dur':>6} {'TRAVESSIAS':>11} {'pancadas':>9}  ponto real?")
    print("=" * 78)

    dentro, fora = [], []
    for i, g in enumerate(grp, 1):
        a, b = g[0], g[-1]
        n_cr = len(g)
        n_pan = sum(1 for q in PAN if a <= q <= b + G.SILENCIO * G.FPS)
        k = ponto_do_gt(a, b)
        dur = (b - a) / G.FPS
        etiqueta = f"✅ ponto {k}" if k else "❌ INTERVALO"
        print(f"{i:>5} {a/G.FPS:>7.1f}s {b/G.FPS:>7.1f}s {dur:>5.1f}s {n_cr:>11} {n_pan:>9}  {etiqueta}")
        (dentro if k else fora).append((n_cr, k, a / G.FPS))

    print("=" * 78)

    # ---- A PERGUNTA QUE DECIDE -------------------------------------------------
    cr_dentro = [n for n, _, _ in dentro]
    cr_fora   = [n for n, _, _ in fora]

    print(f"\nGRUPOS EM PONTO REAL ({len(dentro)}):  travessias  "
          f"min={min(cr_dentro) if cr_dentro else '-'}  "
          f"mediana={np.median(cr_dentro):.0f}  max={max(cr_dentro) if cr_dentro else '-'}")
    print(f"GRUPOS DE INTERVALO  ({len(fora)}):  travessias  "
          f"min={min(cr_fora) if cr_fora else '-'}  "
          f"mediana={np.median(cr_fora):.0f}  max={max(cr_fora) if cr_fora else '-'}")

    print("\n" + "-" * 78)
    print("A PERGUNTA:  algum PONTO REAL tem <= 1 travessia?")
    culpados = [(n, k, t) for n, k, t in dentro if n <= 1]
    if culpados:
        print(f"\n  🚨 SIM — {len(culpados)}:")
        for n, k, t in culpados:
            print(f"      ponto {k} (t={t:.1f}s) tem {n} travessia(s)   <- ACE? falta? ponto curto?")
        print("\n  ⇒ A S21 NÃO PODE VETAR. Tem de PONTUAR.  (lei D18 do Vasco)")
    else:
        print("\n  ✅ NÃO — nenhum ponto real tem <=1 travessia.")
        print("     ⇒ o limiar 'travessias >= 2' NÃO custaria recall NESTE vídeo.")
        print("     ⚠️ MAS: o ACE é um ponto real com UMA travessia. Se não há ace neste vídeo,")
        print("        a ausência de contra-exemplo NÃO é prova. Continua a PONTUAR, não a vetar.")

    # ---- quanto lixo mataria, para cada limiar --------------------------------
    print("\n" + "-" * 78)
    print("SE FOSSE VETO (só para saber o que está em jogo — NÃO é para ligar assim):\n")
    print(f"  {'limiar':>16} {'intervalos mortos':>19} {'pontos reais mortos':>21}")
    for lim in (2, 3, 4, 5):
        mortos_fora   = sum(1 for n in cr_fora if n < lim)
        mortos_dentro = sum(1 for n in cr_dentro if n < lim)
        aviso = "  <-- CUSTA PONTOS" if mortos_dentro else ""
        print(f"  travessias >= {lim:<2} {mortos_fora:>13}/{len(fora):<5} "
              f"{mortos_dentro:>14}/{len(dentro):<5}{aviso}")

    print("\n⚠️ Nem uma linha do gerar_tempo_util.py foi tocada. Isto é só leitura.\n")


if __name__ == "__main__":
    main()
