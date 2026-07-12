#!/usr/bin/env python3
"""
🎯 M3 — GERADOR DE CANDIDATOS A SERVIÇO.   *** SÓ MEDE. Não altera o pipeline. ***

    python3 m3_candidatos.py

O M3 esteve BLOQUEADO meses por não haver **por onde começar**. Agora há.

A REGRA DO VASCO (S23, 13 jul):
    "NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO."
    "Mesmo que tenha kick, SÓ O ÚLTIMO antes da mudança de direção para o outro campo CONTA."

⚠️ A DIFERENÇA PARA A S23 DO PIPELINE:
    a S23 **valida** um segmento que já existe (usa a 1.ª travessia do grupo para abrir a janela).
    ISTO **procura os serviços do zero** — varre TODOS os quiques do vídeo, SEM saber onde estão
    os pontos. É o que o M3 precisa: um **gerador de candidatos**, não um validador.

RESULTADO MEDIDO (Parada4, 13 jul):
    quiques ..................................... 251
    ... FUNDOS (na linha de serviço, prof>=0.7) . 174
    ... com uma TRAVESSIA nos 3 s a seguir ....... 68
    ... agrupados (só o ÚLTIMO conta) ............ 37   <- CANDIDATOS
    >>> RECALL 13/13 = 100%   ·   PRECISÃO 35% (24 falsos)

🎯 É EXACTAMENTE A FORMA QUE A DIRETRIZ MANDA TER:
   **recall 100%, e o lixo limpa-se depois.** Nunca perder um ponto.

➡️ O TRABALHO A SEGUIR: matar os 24 falsos, com as regras do Vasco que ainda NÃO CORREM:
     S3  — formação lida só nos 2 de cima (um na rede + um atrás => eles SERVEM)
     S4  — o ressalto do serviço cai no quadrado CRUZADO (na diagonal)
     S10 — duplo ressalto: o serviço é a única jogada que ressalta dos DOIS lados
     S6  — alternância de lado  ⚠️ NÃO é lei (ponto de ouro) => PONTUA
     S20 — a pausa aprendida: dois serviços não podem estar a 2 s um do outro
⚖️ **LEI DE DESENHO DO VASCO: as regras PONTUAM, NÃO VETAM.** Há sempre uma exceção legítima.
"""
import json, pickle
import gerar_tempo_util as G


def candidatos(R, prof, tks, CR, RES):
    """Varre TODOS os quiques. Devolve [(frame_do_quique, frame_da_travessia)] — os candidatos.
    🔑 "só o ÚLTIMO antes da mudança de campo conta" (Vasco): se vários quiques apontam para a
       MESMA travessia, é UM serviço — e o que vale é o ÚLTIMO."""
    pares = []
    for q in RES:
        if q not in R:
            continue
        if prof(R[q][0], R[q][1])[1] < G.QUIQUE_PROF:      # tem de ser FUNDO (linha de serviço)
            continue
        tr = [c for c in CR if q < c <= q + int(G.QUIQUE_JANELA * G.FPS)]
        if tr:
            pares.append((q, min(tr)))

    por_travessia = {}
    for q, c in pares:
        por_travessia.setdefault(c, []).append(q)
    return sorted((max(qs), c) for c, qs in por_travessia.items())   # ← o ÚLTIMO


def main():
    R, prof = G.carregar()
    R = G.vai_e_vem(R)
    tks = G.tracklets(R)
    CR  = G.cruzamentos(R, tks, prof)
    RES = G.ressaltos(R, tks)

    fundos = [q for q in RES if q in R and prof(R[q][0], R[q][1])[1] >= G.QUIQUE_PROF]
    cand = candidatos(R, prof, tks, CR, RES)

    print("\n" + "=" * 82)
    print("M3 — CANDIDATOS A SERVIÇO   (varridos do ZERO: sem saber onde estão os pontos)")
    print("=" * 82)
    print(f"\n  quiques no vídeo ............................. {len(RES)}")
    print(f"  ... FUNDOS (prof >= {G.QUIQUE_PROF}, na linha de serviço)  {len(fundos)}")
    print(f"  ... com uma TRAVESSIA nos {G.QUIQUE_JANELA:.0f} s a seguir ...... "
          f"{sum(1 for q in RES if q in R and prof(R[q][0],R[q][1])[1] >= G.QUIQUE_PROF and any(q < c <= q+int(G.QUIQUE_JANELA*G.FPS) for c in CR))}")
    print(f"  ... agrupados (só o ÚLTIMO conta) ............ {len(cand)}   ← CANDIDATOS")
    print(f"  serviços reais ............................... {len(G.GT)}\n")
    print("-" * 82)

    acertos = 0
    for k, (g0, g1) in enumerate(G.GT, 1):
        hit = [q for q, c in cand if g0 - 3.0 <= q / G.FPS <= g0 + 3.0]
        acertos += bool(hit)
        m = "✅" if hit else "❌"
        txt = f"candidato a {hit[0]/G.FPS:.1f}s" if hit else "NÃO ENCONTRADO"
        print(f"  ponto {k:>2} (começa {g0:6.1f}s):  {m}  {txt}")

    fp = len(cand) - acertos
    print("-" * 82)
    print(f"\n  >>> RECALL:   {acertos}/{len(G.GT)} = {100*acertos/len(G.GT):.0f}%"
          f"   {'✅ NÃO PERDE NENHUM PONTO' if acertos == len(G.GT) else '🚨 PERDE PONTOS'}")
    print(f"  >>> PRECISÃO: {100*acertos/max(len(cand),1):.0f}%   ({fp} falsos por matar)")
    print("\n  ⚖️ As regras que faltam (S3/S4/S10/S6/S20) PONTUAM os candidatos. NÃO OS VETAM.")
    print("\n⚠️ Leitura pura. O gerar_tempo_util.py NÃO foi alterado.\n")


if __name__ == "__main__":
    main()
