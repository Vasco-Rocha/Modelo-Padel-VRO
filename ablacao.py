#!/usr/bin/env python3
"""
📊 ABLAÇÃO — quanto vale CADA regra, medido.

    python3 ablacao.py          # segundos, em CPU

PORQUÊ
------
O Vasco perguntou: *"porque é que algumas regras vão perdendo firmeza ao longo do dia?"*
E depois: *"podes confirmar regra a regra o que acontece aos números quando as utilizamos?"*

Sem isto, eu defendia regras pelo que elas valiam ONTEM. A ablação mostra o que valem HOJE.

⛔ NÃO ESCREVER OS RESULTADOS AQUI. Uma tabela num docstring APODRECE — e depois MENTE.
   (Esta tinha "BASE: 15 pontos · RECALL 93,2 · PRECISÃO 89,4" **muito depois de ser falso**.
    Hoje são 13 pontos. Quem lesse isto acreditava.)

   👉 OS NÚMEROS SAEM DE CORRER:   python3 ablacao.py

AS DESCOBERTAS QUE NÃO APODRECEM (são LIÇÕES, não números)
----------------------------------------------------------
⚠️ **min_det é um parâmetro MORTO.** MIN_DET=1 dá exactamente os mesmos números.
   Está lá a fingir que trabalha.

⚠️ **O vai-e-vem quase não faz nada — AGORA.** De manhã, com a bola a 0.7, valia +6 de precisão.
   Hoje custa 0,7 de recall e 0,1 de precisão.
   PORQUÊ: o `Theta` e o `thr=0.4` tornaram-no redundante — a costura por direção já rejeita os
   saltos incoerentes, e a bola a 0.4 já não tem os buracos que geravam os falsos saltos.
   **A regra não enfraqueceu. Deixou de ser PRECISA, porque o problema que resolvia desapareceu.**

   >>> É ESTA a resposta à pergunta do Vasco. E só a ablação a mostra.

REGRA DE USO
------------
Correr **sempre que se acrescentar uma regra**. Uma regra nova pode tornar outra redundante —
e continuar a defendê-la é mentir a nós próprios.
"""
import sys, json, pickle
import numpy as np
sys.path.insert(0, ".")
import gerar_tempo_util as G

CAL_J = json.load(open(G.CAL))
PB = pickle.load(open(G.BOXES, "rb"))["player_boxes"]

# o teste que MAIS importa: nenhum "fim certo" pode cair A MEIO de um ponto real
gt = np.zeros(G.N_FRAMES, bool)
fg = np.zeros(G.N_FRAMES, bool)
for a, b in G.GT:
    gt[int(a*G.FPS):int(b*G.FPS)+1] = True
    fg[int((b-1.5)*G.FPS):int(b*G.FPS)+1] = True


def corre(sem=None, flags=None, **over):
    """sem = passos removidos à mão · flags = interruptores REGRAS · over = parâmetros"""
    sem = sem or set()
    orig = {k: getattr(G, k) for k in over}
    oflags = dict(G.REGRAS)
    for k, v in over.items():
        setattr(G, k, v)
    for k, v in (flags or {}).items():
        G.REGRAS[k] = v

    R, prof = G.carregar()
    if "vai_e_vem" not in sem:
        R = G.vai_e_vem(R)

    tks = G.tracklets(R)
    if "theta" in sem:                       # tracklets SEM a costura por direção
        fs = sorted(R); out = []; cur = [fs[0]]
        for a, b in zip(fs, fs[1:]):
            if b - a <= G.GAP and G.d(R, a, b) <= G.VMAX * (b - a):
                cur.append(b)
            else:
                out.append(cur); cur = [b]
        out.append(cur)
        tks = [t for t in out if len(t) >= G.MIN_DET]

    CR = G.cruzamentos(R, tks, prof)
    PAN = [] if "pancadas" in sem else G.pancadas(R, CAL_J, PB)
    FIM = G.fim_certo(R, CAL_J, PB)
    RES = G.ressaltos(R, tks)        # 🔴 S23 — o quique do serviço (Vasco, 13 jul)
    r = G.avaliar(G.rallies(CR, PAN, FIM, RES, R, prof))
    r["pancadas"] = len(PAN)
    r["fim_dentro"] = sum(1 for f in FIM if gt[f] and not fg[f])

    for k, v in orig.items():
        setattr(G, k, v)
    G.REGRAS.clear(); G.REGRAS.update(oflags)
    return r


TESTES = [
    ("mao vs raquete (S15)",   dict(flags={"S15_MAO_RAQUETE": False})),
    ("costura por Theta (B6)", dict(sem={"theta"})),
    ("pancadas",               dict(sem={"pancadas"})),
    ("S12 ultima pancada",     dict(flags={"S12_ULT_PANCADA": False})),   # volta ao 1,5s antigo
    ("S16 INVERTIDA",          dict(over=dict(M_COM_PAN=5.0, M_SEM_PAN=2.0))),
    ("S13 timeline",           dict(flags={"S13_TIMELINE": False})),
    ("S17 REDE  🔒",           dict(flags={"S17_REDE": False})),
    ("S18 mao parada",         dict(flags={"S18_MAO_PARADA": False})),
    ("cruzamento profundo",    dict(over=dict(MIN_PROF=0.0))),
    ("vai-e-vem (B14)",         dict(sem={"vai_e_vem"})),
    ("min_det (tracklets)",    dict(over=dict(MIN_DET=1))),
    ("PAUSA MINIMA (prompts)",  dict(flags={"PAUSA_MINIMA": False})),
    # 🔴 S23 — o QUIQUE DO SERVIÇO (Vasco, 13 jul). Anda JUNTA com o MIN_PROF=0.15:
    #    desligá-la SEM repor o 0.35 deixa entrar o segmento falso dos 281s. É isso que se mede.
    ("S23 quique do servico", dict(flags={"S23_QUIQUE_SERV": False})),
    ("S23 OFF + MIN_PROF .35 (estado antigo)",
                             dict(flags={"S23_QUIQUE_SERV": False}, over=dict(MIN_PROF=0.35))),
]


def main():
    b = corre()
    print(f"\nBASE (tudo ligado): {b['n']} pontos | RECALL {b['recall']:.1f}%  "
          f"PRECISAO {b['precisao']:.1f}%  F1 {b['f1']:.1f} | servicos {b['servicos']}/12 | "
          f"cortes a meio {b['fim_dentro']}\n")
    print("O QUE ACONTECE SE DESLIGAR CADA REGRA:\n")
    print("  regra desligada         | pts | RECALL  (delta) | PRECISAO (delta) |  F1   | serv")
    print("  " + "-" * 84)
    for nome, kw in TESTES:
        r = corre(sem=kw.get("sem"), flags=kw.get("flags"), **kw.get("over", {}))
        dr = r["recall"] - b["recall"]
        dp = r["precisao"] - b["precisao"]
        print(f"  {nome:23s} | {r['n']:3d} | {r['recall']:5.1f}% ({dr:+5.1f}) | "
              f"{r['precisao']:5.1f}%  ({dp:+5.1f}) | {r['f1']:5.1f} | {r['servicos']:2d}/12")
    print("\n  (delta grande e NEGATIVO = a regra e' VALIOSA)")
    print("  (delta ~ZERO = a regra nao esta a fazer nada -- ou ficou redundante)")
    print("\n  DESLIGADAS por decisao (nao por falha):")
    for k, v in G.REGRAS.items():
        if not v:
            print(f"    ⛔ {k}  -- razao escrita no gerar_tempo_util.py")
    print()


if __name__ == "__main__":
    main()
