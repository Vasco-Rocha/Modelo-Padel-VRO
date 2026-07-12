#!/usr/bin/env python3
"""
🔒 TESTE DE REGRESSÃO — TRAVA O ESTADO DE 12 JUL 2026.

    python3 teste_regressao.py

Corre em segundos, em CPU.

PORQUÊ ISTO EXISTE
------------------
O Vasco perguntou: *"porque é que algumas regras vão perdendo firmeza ao longo do dia?"*
A resposta honesta: porque eu re-afinava os limiares a cada regra nova, sem verificar se o que
já funcionava continuava a funcionar. **Não havia testes.** Uma regra firme às 15h aparecia
amolecida às 19h — não era a regra que enfraquecia, era eu a mexer-lhe por baixo.

E depois: *"NÃO INVENTAR NEM ATALHAR NADA DO QUE FOI FEITO ATÉ AGORA."*

Este ficheiro é a garantia. **Se alguém partir o que está feito, ISTO FALHA.**

REGRA DE USO
------------
- Correr ANTES e DEPOIS de qualquer alteração ao `gerar_tempo_util.py`.
- Se falhar, a alteração está errada — a não ser que o Vasco tenha decidido o contrário,
  EXPLICITAMENTE. Nesse caso, e só nesse caso, atualizam-se os valores travados aqui,
  com uma linha a dizer porquê.
- **Nenhum valor aqui se muda para "fazer o teste passar".**

ESTADO TRAVADO (12 jul 2026, com a bola a thr=0.4)
"""
import sys, json, pickle
import numpy as np
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos, pancadas,
                              rallies, avaliar, fim_certo, CAL, BOXES, FPS, N_FRAMES, GT)

# ---------------------------------------------------------------------------
#  OS NÚMEROS. Não se mexem sem o Vasco dizer.
# ---------------------------------------------------------------------------
TRAVADO = {
    "recall":    (96.2, 0.5),    # (valor, tolerância)
    "precisao":  (91.8, 0.5),
    "servicos":  (12,   0),      # 12/12. NUNCA menos.
    "n_pontos":  (13,   1),      # reais: 12  (12 inteiros + 1 falso aos 289s)
    "pancadas":  (133,  5),      # a 0.7 eram 57. O 0.4 foi buscá-las. (-2: as fantasma, sem jogador)
    "fim_certo": (19,   2),      # eventos rede/mão. ⚠️ 0 DENTRO de pontos reais. Ver abaixo.
    "fim_dentro":(0,    0),      # 🔒 NUNCA >0. Um fim certo a meio de um ponto CORTA-O AO MEIO.
}

# 🔒🔒 S17 — A REGRA DA REDE ESTÁ FECHADA.
#      "regra da rede está perfeita! fixa e não deixes mudar."  — Vasco, 13 jul 2026.
#      RED_DTHETA / RED_L_PARA / RED_DIST NÃO SE MEXEM. Nem para "afinar", nem para "melhorar",
#      nem para fazer passar outro teste. Se alguém precisar de lhes mexer, a alteração é que
#      está errada.

# ---------------------------------------------------------------------------
#  PORQUE MUDARAM OS VALORES TRAVADOS  (a ÚNICA forma legítima de lhes mexer)
# ---------------------------------------------------------------------------
#  13 jul 2026 — 93,2/89,4 (15 pontos) -> 97,0/87,2 (13 pontos).
#  DECISÃO EXPLÍCITA DO VASCO, depois de ver o TEMPO_UTIL_v12_S12.mp4.
#
#  Causa: a S12 estava no MAPA_DAS_REGRAS como LIGADA, mas fazia outra coisa. A regra do Vasco
#  diz "o ponto acaba 4s depois da última PANCADA"; o código agarrava-se ao último CRUZAMENTO da
#  rede e só ouvia pancadas até 1,5s depois. As pancadas seguintes (volta de parede, devolução
#  rente, bola que morre do mesmo lado) eram ignoradas.
#     ponto 3: pancadas em 84,0/84,9/85,1 ignoradas -> acabava 2,3s cedo
#     ponto 4: pancadas em 106,3/106,7 ignoradas   -> buraco 0,5s -> PARTIDO em 2
#     ponto 5: pancadas em 130,1/130,3/132,5       -> buraco 1,2s -> PARTIDO em 2
#  Não eram 3 bugs. Era 1: o fim do ponto estava agarrado à coisa errada.
#
#  A correção NÃO acrescenta números: o 1,5s (mágico, sem nome) passa a SILENCIO, que já existia
#  e já significa exactamente isto — "a bola deixou de ser batida".
#  Troco: +3,8 recall por -2,2 precisão, e os pontos partidos acabam (12 pontos = 12 segmentos).
#  Alinhado com a DIRETRIZ DE PRODUTO: nunca perder um ponto; mais lixo é preferível a menos
#  tempo útil.  ⚠️ Rejeitada a versão gulosa (cadeia infinita de pancadas): 96,9/72,0 — as
#  pancadas dos INTERVALOS puxavam o ponto 2 até ao 3.
#
#  13 jul 2026 (2) — 97,0/87,2 -> 96,2/91,3  (F1 91,8 -> 93,7, o melhor até hoje).
#  S17 + S18, o FIM CERTO. Regras do Vasco, dadas hoje. Corte a 0,5s.
#     S17: "a bola muda de direção (ou pára) NA REDE, LONGE de uma bounding box => ponto acabou."
#          A bola que PASSA por cima não vira. A que BATE, vira — ou morre. E se não há jogador
#          ao pé, não foi ninguém que lhe bateu: foi a rede.
#     S18: "BOLA PARADA dentro da bounding box, SEM MUDAR DE CAMPO => ponto terminado de certeza,
#          sem raquetada."  As três condições são precisas as três:
#            PARADA (L<=3) · DENTRO DA BOX · SEM MUDAR DE CAMPO (se atravessou a rede, foi BATIDA).
#          🔒 A DURAÇÃO (0,5s) NÃO SE BAIXA: a 0,3s a regra corta pontos a meio e o recall cai de
#             96,2 para 82. É a duração que separa a MÃO do LOB (o lob vai lento — mas um INSTANTE).
#  ⛔ NÃO usar a POSIÇÃO na rede: 60 de 94 candidatos caíam A MEIO de pontos reais. Nesta câmara
#     a bola que passa POR CIMA e a que BATE ocupam os MESMOS PÍXEIS (banda da rede = 35 px;
#     meio-campo do fundo = 100 px). Sem profundidade, a posição não distingue nada.
#  ⛔ NÃO usar "bola lenta junto a um jogador": 49 falsos a meio de pontos (o lob vai lento no
#     ponto alto). É a DURAÇÃO + a ausência de raquetada que os separam.
#  🔒 fim_dentro TEM de ser 0. Se subir, a regra está a cortar pontos reais ao meio — o pior
#     erro possível, contra a diretriz. Nesse caso: NÃO relaxar o teste, DESLIGAR a regra.
#
#  ⛔ S8 (fim = última pancada antes do serviço seguinte) — TENTADA E REJEITADA hoje: 98,9/47,1,
#     5 segmentos colados. As pancadas do INTERVALO entram pelo meio e esticam cada ponto até ao
#     seguinte. A S8 precisa de um DETETOR DE SERVIÇO a sério (M3) — está bloqueada pelo ressalto.
#     A regra é boa; o que falta é o serviço. NÃO voltar a tentar sem M3.
# ---------------------------------------------------------------------------

# As REGRAS que produzem estes números. Cada uma já valeu pontos, medidos.
# (Se uma destas desaparecer do pipeline, os números caem e o teste falha.)
REGRAS_VIVAS = """
  B8/vai-e-vem      A->B longe, A->C perto => B e' ERRO. Tira o frame, nao parte a cadeia. (+6 precisao)
  Theta/costura     Direcao a 2 graus, numa UNICA detecao => os buracos deixam de partir.  (+10 recall)
  cruzamento fundo  De fundo a fundo. Rocar a fita NAO conta (e' onde o ruido oscila).
  S15 mao/raquete   L: servico 17,4 · passagem a mao 2,7. So dispara se veio da RAQUETE.  (+18 precisao)
  S16 duvida        HA pancada -> corte rente (2s). NAO ha -> duvida -> mais margem (5s).  (+9 precisao)
                    ⚠️ NUNCA INVERTER. Ja esteve invertido e cortava os pontos 12/13/14 a meio.
  S13 timeline      Nunca anda para tras. Segmentos que se tocam SAO O MESMO PONTO.
  thr=0.4           A bola nos 2,5s do servico: 60% -> 85%. Pancadas: 57 -> 135.
"""


def main():
    print(__doc__)
    print("REGRAS QUE TEM DE ESTAR VIVAS:")
    print(REGRAS_VIVAS)

    R, prof = carregar()
    R = vai_e_vem(R)
    tks = tracklets(R)
    CR = cruzamentos(R, tks, prof)
    PAN = pancadas(R, json.load(open(CAL)), pickle.load(open(BOXES,"rb"))["player_boxes"])
    FIM = fim_certo(R, json.load(open(CAL)),
                    pickle.load(open(BOXES, "rb"))["player_boxes"])
    M = rallies(CR, PAN, FIM)
    r = avaliar(M)
    r["pancadas"] = len(PAN)
    r["n_pontos"] = r["n"]
    r["fim_certo"] = len(FIM)

    # 🔒 O TESTE QUE MAIS IMPORTA: nenhum "fim certo" pode cair A MEIO de um ponto real.
    # (o último 1,5s de um ponto conta como fim, não como meio)
    gt = np.zeros(N_FRAMES, bool)
    fg = np.zeros(N_FRAMES, bool)
    for a, b in GT:
        gt[int(a*FPS):int(b*FPS)+1] = True
        fg[int((b-1.5)*FPS):int(b*FPS)+1] = True
    r["fim_dentro"] = sum(1 for f in FIM if gt[f] and not fg[f])

    print("-" * 62)
    print(f"{'metrica':<12} {'travado':>9} {'agora':>9}   estado")
    print("-" * 62)
    falhou = []
    for k, (esperado, tol) in TRAVADO.items():
        v = r[k]
        ok = abs(v - esperado) <= tol
        if not ok:
            falhou.append((k, esperado, v))
        print(f"{k:<12} {esperado:>9} {v:>9.1f}   {'OK' if ok else '<<< PARTIU'}")
    print("-" * 62)

    if falhou:
        print("\n❌ REGRESSAO. Alguma coisa se perdeu:\n")
        for k, e, v in falhou:
            print(f"   {k}: era {e}, esta {v:.1f}")
        print("\n   Nao alterar os valores travados para o teste passar.")
        print("   Encontrar o que se partiu. E se foi decisao do Vasco, escrever PORQUE.")
        sys.exit(1)

    print("\n✅ Tudo no sitio. Nada se perdeu.")


if __name__ == "__main__":
    main()
