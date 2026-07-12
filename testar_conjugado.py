#!/usr/bin/env python3
"""
A CONJUGAÇÃO DO VASCO (13 jul).   *** SÓ MEDE. Não altera o gerar_tempo_util.py. ***

    "Podes AMPLIAR o intervalo de passagem, mas para tirar aquele lixo ASSOCIAS as outras regras.
     Um ponto termina:
        (1) quando a bola tocar DUAS VEZES no chão                      [precisa do RESSALTO ⛔]
        (2) quando a travessia OU a alteração de direção da bola NÃO tenha estado em contacto
            ou PERTO de alguma bounding box — ou seja, NÃO tenha havido nenhuma pancada  ✅
        (3) ou quando a próxima pancada é um SERVIÇO                    [precisa do M3 ⛔]

     E por uma questão do que está CORRETO VISUALMENTE: para a bola atravessar a rede para o
     lado de cá, o limite é a PARTE DE CIMA da rede. Para o lado de lá, a mesma coisa."

DUAS COISAS AO MESMO TEMPO — e é isso que nunca foi testado:
    · AMPLIAR    -> baixar o MIN_PROF (a faixa cega à volta da rede encolhe)
    · CORRIGIR   -> o divisor CIMA/BAIXO passa a ser o TOPO da rede, não a base
      (testei o TOPO sozinho e não deu nada — mas com o MIN_PROF nos 0.35 o divisor estava
       DENTRO da zona deitada fora. Era um teste vazio.)
    · CONJUGAR   -> a regra (2) mata o lixo que a ampliação traz

A REGRA (2) = a S17 do Vasco SEM a restrição da rede.
    S17 (hoje):    virou/parou  DENTRO da faixa da rede  E longe de box  -> fim certo
    Regra (2):     virou/parou  EM QUALQUER SÍTIO        E longe de box  -> fim certo
    Mesmos números do Vasco: RED_DTHETA=60 · RED_L_PARA=2.0 · RED_DIST=0.10  (🔒 dele, não mexo)

⚠️ RISCO CONHECIDO: a bola a bater na PAREDE e no CHÃO também vira sem ninguém ao pé.
   Está registado que isso deu 49 falsos a meio de pontos. Mas TESTA-SE, não se raciocina.
"""
import json, pickle, math
import numpy as np
import gerar_tempo_util as G

ORIG_MP = G.MIN_PROF


def fazer_prof(cal, chave):
    ev = lambda c, t: float(np.polyval(c, t))
    y_div = lambda x: ev(cal[chave], x)
    y_sp  = lambda x: ev(cal["servico_perto_coef"], x)
    y_sl  = lambda x: ev(cal["servico_longe_coef"], x)

    def prof(x, y):
        yr = y_div(x)
        if y > yr:
            return "baixo", (y - yr) / max(y_sp(x) - yr, 1)
        return "cima", (yr - y) / max(yr - y_sl(x), 1)
    return prof


def fim_sem_rede(R, cal, boxes):
    """REGRA (2) do Vasco: VIROU (ou PAROU) e NÃO havia ninguém perto ⇒ não houve pancada
    ⇒ o ponto acabou. É a S17, mas SEM a restrição de ser na faixa da rede.
    Usa os MESMOS números do Vasco (RED_DTHETA / RED_L_PARA / RED_DIST). Zero números novos."""
    _, _, meio = G.campo(cal)
    fs = sorted(R)

    def dist_box(f):
        x, y = R[f][0], R[f][1]
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    out = []
    for a, b in zip(fs, fs[1:]):
        if b - a > 4:
            continue
        virou = abs(((R[b][3] - R[a][3] + 90) % 180) - 90) >= G.RED_DTHETA
        parou = R[b][2] <= G.RED_L_PARA
        if (virou or parou) and dist_box(b) >= G.RED_DIST:
            out.append(b)
    ag = []
    for f in out:
        if not ag or f - ag[-1] > 15:
            ag.append(f)
    return ag


def avaliar_cfg(mp, chave, regra2, R2, tks, cal, boxes):
    prof = fazer_prof(cal, chave)
    PAN  = G.pancadas(R2, cal, boxes)
    FIM  = list(G.fim_certo(R2, cal, boxes))
    if regra2:
        FIM = sorted(set(FIM) | set(fim_sem_rede(R2, cal, boxes)))
    G.MIN_PROF = mp
    CR = G.cruzamentos(R2, tks, prof)
    M  = G.rallies(CR, PAN, FIM)
    r  = G.avaliar(M)
    G.MIN_PROF = ORIG_MP

    lixo = [s for s in M
            if not any(s[0]/G.FPS <= g1 and s[1]/G.FPS >= g0 for g0, g1 in G.GT)]
    # 🔒 O TESTE QUE NÃO SE RELAXA: nenhum "fim certo" pode cair A MEIO de um ponto real
    dentro = sum(1 for f in FIM
                 if any(g0 + 1.0 <= f/G.FPS <= g1 - 1.0 for g0, g1 in G.GT))
    pp = [sum(1 for c in CR if t0 <= c/G.FPS <= t1) for t0, t1 in G.GT]
    return len(CR), r, len(lixo), dentro, pp, len(FIM)


def main():
    R, _  = G.carregar()
    cal   = json.load(open(G.CAL))
    R2    = G.vai_e_vem(R)
    tks   = G.tracklets(R2)
    boxes = pickle.load(open(G.BOXES, "rb"))["player_boxes"]

    print("\n" + "=" * 108)
    print("AMPLIAR a passagem + divisor no TOPO + a REGRA (2) do Vasco  —  todas as combinações")
    print("=" * 108)
    print(f"\n{'divisor':>8} {'MIN_PROF':>9} {'regra2':>7} │ {'trav':>5} {'segm':>5} {'serv':>5} "
          f"{'RECALL':>8} {'PRECISAO':>9} {'F1':>7} {'lixo':>5} {'fim_dentro':>11}")
    print("-" * 108)

    guard = {}
    for chave, nome in (("rede_base_coef", "BASE"), ("rede_topo_coef", "TOPO")):
        for mp in (0.35, 0.25, 0.15):
            for regra2 in (False, True):
                n_cr, r, lixo, dentro, pp, n_fim = avaliar_cfg(mp, chave, regra2, R2, tks, cal, boxes)
                guard[(nome, mp, regra2)] = pp
                base = (nome == "BASE" and mp == 0.35 and not regra2)
                marca = "  <- HOJE 🔒" if base else ""
                alarme = "  🚨" if dentro > 0 else ""
                print(f"{nome:>8} {mp:>9.2f} {'SIM' if regra2 else '-':>7} │ "
                      f"{n_cr:>5} {r['n']:>5} {r['servicos']:>5} "
                      f"{r['recall']:>8.1f} {r['precisao']:>9.1f} {r['f1']:>7.1f} "
                      f"{lixo:>5} {dentro:>11}{marca}{alarme}")
            print()

    print("-" * 108)
    print("🔒 fim_dentro = quantos 'fins certos' caem A MEIO de um ponto real.")
    print("   O Vasco: 'se subir, DESLIGAR a regra. NUNCA relaxar o teste.' É o pior erro possível.")

    print("\n" + "-" * 108)
    print("TRAVESSIAS POR PONTO — os frágeis (10, 11, 13) deixam de estar por um fio?\n")
    cols = [("BASE", 0.35, False), ("TOPO", 0.15, False), ("TOPO", 0.15, True)]
    cab = ["hoje", "TOPO+0.15", "+regra2"]
    print(f"  {'pt':>3}{'dur':>7}" + "".join(f"{c:>11}" for c in cab))
    for k in range(13):
        t0, t1 = G.GT[k]
        m = "  <--" if k+1 in (10, 11, 13) else ""
        print(f"  {k+1:>3}{t1-t0:>6.1f}s" + "".join(f"{guard[c][k]:>11}" for c in cols) + m)

    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
