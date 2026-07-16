#!/usr/bin/env python3
"""
🔒 TESTE DE REGRESSÃO — TRAVA O ESTADO. (a data e os números vivem no dict TRAVADO, em baixo)

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

⛔ O ESTADO TRAVADO **NÃO SE ESCREVE AQUI EM PROSA** — está no dict TRAVADO, em baixo, que é
   o que o teste LÊ. Um número escrito num docstring apodrece; um número que CORRE, não.
   (Este cabeçalho dizia "12 jul" muito depois de o estado ter mudado duas vezes.)
"""
import sys, json, pickle
import numpy as np
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos, pancadas,
                              rallies, avaliar, fim_certo, ressaltos, CAL, BOXES, FPS,
                              N_FRAMES, GT)

# ---------------------------------------------------------------------------
#  OS NÚMEROS. Não se mexem sem o Vasco dizer.
# ---------------------------------------------------------------------------
TRAVADO = {
    "recall":    (96.8, 0.5),    # (valor, tolerância)   ⬆️ 96,3 -> 96,8  (S23, 13 jul)
    "precisao":  (95.4, 0.5),    #                        ⬇️ 95,9 -> 95,4  (margens, não lixo)
    "servicos":  (13,   0),      # 13/13. NUNCA menos.
    "n_pontos":  (13,   1),      # reais: 13
    "pancadas":  (133,  5),      # a 0.7 eram 57. O 0.4 foi buscá-las. (-2: as fantasma, sem jogador)
    "fim_certo": (16,   2),      # eventos rede/mão. ⚠️ 0 DENTRO de pontos reais. Ver abaixo.
                                 # ⬇️ 19 -> 16  (RED_DIST 0,10 -> 0,17 · 13 jul · DECISÃO DO VASCO)
    "fim_dentro":(0,    0),      # 🔒 NUNCA >0. Um fim certo a meio de um ponto CORTA-O AO MEIO.
}

# ---------------------------------------------------------------------------
#  13 jul 2026 (fim do dia) — 96,3/95,9  ->  96,8/95,4   ·  F1 96,1 (igual)  ·  13/13
#  DECISÃO EXPLÍCITA DO VASCO: "podes avançar sim."
#
#  ENTROU A **S23 — O QUIQUE DO SERVIÇO** (regra do Vasco):
#     "matar o lixo pela BOLA NA MÃO DO NÃO SERVIDOR — ANTES de bater no chão."
#     "mesmo que tenha kick, SÓ O ÚLTIMO antes da mudança de campo conta."
#
#     A LEI:  NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.
#             o servidor larga a bola e ela QUICA · o não-servidor PASSA-A à mão (sem quique).
#
#  E, POR CAUSA DELA, foi possível AMPLIAR a faixa de passagem: MIN_PROF 0.35 -> 0.15.
#  ⚠️ AS DUAS ANDAM JUNTAS. A ampliação sozinha trazia um segmento FALSO (281–285s).
#     A S23 mata-o: 13/13 pontos reais têm quique fundo · o falso tem ZERO. Separação perfeita.
#
#  O QUE SE GANHOU (e é a razão de fundo, não os 0,5 de recall):
#     os pontos 10, 11 e 13 estavam pendurados numa ÚNICA travessia. Medido: tirando-a,
#     **O PONTO DESAPARECE**. Com o 0.15, o 10 e o 11 passam a ter 3. Saem do fio.
#
#  O QUE SE PAGOU: 0,5 de precisão = +2s de MARGEM nos MESMOS 13 pontos. ZERO segmentos falsos.
#  (E a cauda do ponto 1 — +2,1s — foi aparada para +1,2s pela PAUSA APRENDIDA do Vasco, que
#   corre DEPOIS da S23: sem o lixo a envenenar a mediana, ela aprendeu 4,9s. Chão dele: 4s.)
#
#  ⚠️ É A 1.ª VEZ QUE O RESSALTO ENTRA NO PIPELINE. Acerta 13/13 aqui; noutro vídeo, não se sabe.
#     SE O 2.º VÍDEO PERDER PONTOS, DESLIGAR ISTO PRIMEIRO:
#         python3 gerar_tempo_util.py --sem S23_QUIQUE_SERV     (e repor MIN_PROF = 0.35)
# ---------------------------------------------------------------------------

# 🔒🔒 S17 — A REGRA DA REDE ESTÁ FECHADA.
#      "regra da rede está perfeita! fixa e não deixes mudar."  — Vasco, 13 jul 2026.
#      RED_DTHETA / RED_L_PARA / RED_DIST NÃO SE MEXEM. Nem para "afinar", nem para "melhorar",
#      nem para fazer passar outro teste. Se alguém precisar de lhes mexer, a alteração é que
#      está errada.

# ---------------------------------------------------------------------------
#  PORQUE MUDARAM OS VALORES TRAVADOS  (a ÚNICA forma legítima de lhes mexer)
# ---------------------------------------------------------------------------
#  13 jul 2026, à NOITE — fim_certo: 19 -> 16.   RED_DIST: 0,10 -> 0,17.
#  DECISÃO EXPLÍCITA DO VASCO, depois do 2.º vídeo (BarbosaMeireles) ganhar ground-truth.
#
#  A LEI:  A BOX É O CORPO. A RAQUETE CHEGA A MAIS DE UM METRO.
#
#  A S17 (a rede) só dispara se a bola virar "LONGE de qualquer box". "Longe" eram 70 cm.
#  Mas uma bola batida à VOLEIA sai da raquete e fica a 70 cm–1,2 m do CORPO: "longe" pela
#  regra — e no entanto FOI BATIDA. A S17 lia isso como "bateu na rede" e MATAVA O PONTO A MEIO.
#     Barbosa, contra o GT do Vasco: 4 dos 5 fins-a-meio-de-ponto eram VOLEIAS.
#     A bola virava 70°, 75°, 77°, 86° ao pé da rede — com um jogador a ~1 m.
#
#  ⚠️ E EIS PORQUE ISTO É LEGÍTIMO, e não uma erosão do teste:
#       recall     96,8 -> 96,8   (IGUAL)
#       precisao   95,4 -> 95,4   (IGUAL)
#       n_pontos     13 -> 13     ·  servicos 13/13  ·  fim_dentro 0 🔒
#       ablação: a S17 continua a valer -5,0 de precisão. NÃO PERDEU VALOR.
#     NENHUM RESULTADO MEXEU. Os 3 "fins certos" que deixaram de disparar eram REDUNDANTES —
#     outra regra já os cobria. O `fim_certo` é um CONTADOR INTERNO, não um resultado.
#  E o que se ganha, no vídeo NOVO: recall 79,6 -> 81,9 · fim_dentro 5 -> 3.
#
#  ⚠️ 0,17 NÃO É UM NÚMERO MÁGICO: é (braço + raquete ≈ 1,2 m) / (meio-campo = 6,95 m).
#     É o ALCANCE DE UMA RAQUETADA. Sobrevive a outra câmara. NÃO CURA o fundo — a box dos
#     PÉS continua a não ver a RAQUETE. É um penso. A cura é a POSE ou o ÁUDIO.
#
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
#  13 jul 2026 (3) — O GROUND-TRUTH ESTAVA INCOMPLETO. 96,2/91,8 -> 96,3/93,9 (F1 95,1).
#  O VASCO ACRESCENTOU O 13.º RALLY (289,1s -> fim do vídeo). Confirmou: "é serviço, começa onde
#  está destacado e acaba pelo fim do vídeo".
#  ⚠️ O QUE EU CHAMAVA "SEGMENTO FALSO" ERA UM PONTO A SÉRIO. A precisão andou o dia a castigar-me
#     por ACERTAR. NADA no código mudou — só a régua.
#  🚨 A LIÇÃO: o ground-truth é a régua de TUDO. Se ele está incompleto, todas as medições estão
#     tortas — e posso ter REJEITADO regras boas por "aumentarem o lixo" que afinal era JOGO.
#     Ao retomar: DESCONFIAR do GT antes de desconfiar do código.
#
#  ⛔ S8 (fim = última pancada antes do serviço seguinte) — TENTADA E REJEITADA hoje: 98,9/47,1,
#     5 segmentos colados. As pancadas do INTERVALO entram pelo meio e esticam cada ponto até ao
#     seguinte. A S8 precisa de um DETETOR DE SERVIÇO a sério (M3) — está bloqueada pelo ressalto.
#     A regra é boa; o que falta é o serviço. NÃO voltar a tentar sem M3.
# ---------------------------------------------------------------------------

# As REGRAS que produzem estes números. Cada uma já valeu pontos, medidos.
# (Se uma destas desaparecer do pipeline, os números caem e o teste falha.)
REGRAS_VIVAS = """
  B14/vai-e-vem     A->B longe, A->C perto => B e' ERRO. Tira o frame, nao parte a cadeia.
                    (era "B8" ate 13 jul — a B8 REAL e' outra regra: coerencia temporal.)
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
    RES = ressaltos(R, tks)          # 🔴 S23 — sem isto, a regra do QUIQUE não corre aqui
    M = rallies(CR, PAN, FIM, RES, R, prof)
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
