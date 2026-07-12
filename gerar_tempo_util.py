#!/usr/bin/env python3
"""
PIPELINE COMPLETO DO M1 — TEMPO ÚTIL.       12 jul 2026.

    RECALL 93,2%   PRECISÃO 89,4%      (de manhã estava em 72% / 63%)

Corre em CPU, em segundos. Sem GPU, sem Colab, sem Kaggle.

    python3 gerar_tempo_util.py                # só as métricas
    python3 gerar_tempo_util.py --video        # + a compilação do tempo útil

TODAS as regras aqui são do Vasco. Ver REGRAS_DO_VASCO.md.

⚠️ ATALHOS POR CORRIGIR (declarados, como manda a regra):
   - VMAX=90 px/frame -> PÍXEIS ABSOLUTOS. Viola a lição da perspetiva (o meio-campo longe
     tem 100 px e o perto 290, para os mesmos 6,95 m). Devia ser fração do meio_campo_px.
   - L_RAQUETE=11, SILENCIO=4s, PAD_ANTES=1.6s, MIN_PROF=0.35, e os números da pancada:
     afinados ao F1 DESTE vídeo. Não derivados da estrutura. Podem não sobreviver a outra câmara.
"""
import csv, json, math, sys, subprocess, os, pickle
import numpy as np

FPS = 29.97
N_FRAMES = 8741
BOLA = "../dados_parada4/traj_frames_Parada4_thr04.csv"
CAL  = "calibracao_campo.json"
VIDEO = "../Parada4.mp4"
BOXES = "../dados_parada4/player_boxes_parada4.pkl"

# ground-truth: 13 rallies / 119,6 s, anotados à mão pelo Vasco
# ⚠️ 13 jul: o Vasco ACRESCENTOU o 13.º (289,1s -> fim do vídeo). Faltava. O que eu chamava
#    'segmento FALSO' era um PONTO A SÉRIO — e a precisão estava a castigar-me por ACERTAR.
GT = [(38.0,41.5),(46.8,67.5),(77.6,85.5),(95.9,111.1),(122.4,135.9),(157.9,169.4),
      (178.1,186.5),(197.0,202.1),(210.5,216.3),(229.9,237.3),(249.6,255.0),(263.8,276.4),
      (289.1,291.7)]   # 13.º: o Vasco confirmou (13 jul) — é serviço, e fica CORTADO pelo fim do vídeo

# ===========================================================================================
#  🎛️  OS INTERRUPTORES.   Qualquer regra se desliga aqui, sem tocar em código.
#
#  "deixa estas regras aptas a serem mudadas / recuperadas para a antiga caso não funcionem"
#                                                                        — Vasco, 13 jul 2026
#      python3 gerar_tempo_util.py --sem S18_MAO_PASSE      # desliga UMA regra
#      python3 ablacao.py                                   # a contribuição de CADA uma
#
#  🔒 S17_REDE está FECHADA pelo Vasco. Desliga-se para medir, NUNCA se afina.
# ===========================================================================================
REGRAS = {
    "B8_VAI_E_VEM":   True,   # A->B longe, A->C perto => B é erro
    "B6_THETA":       True,   # costura os buracos pela direção (2°)
    "S15_MAO_RAQUETE":True,   # só cruza quem veio da RAQUETE (L alto)
    "S12_ULT_PANCADA":True,   # o fim segue a última PANCADA (não o último cruzamento)
    "S16_DUVIDA":     True,   # há pancada -> corte rente; não há -> mais margem
    "S13_TIMELINE":   True,   # a timeline nunca anda para trás
    "S17_REDE":       True,   # 🔒 FECHADA — vira/pára na rede, longe de box => fim certo
    "S18_MAO_PARADA": True,   # bola parada na box, sem mudar de campo => fim certo
    "PAN_TEM_JOGADOR":True,   # 🆕 uma raquetada TEM de ter um jogador ao pé. Senão, ninguém bateu.
    "PAUSA_MINIMA":   True,   # 🆕 regra PERDIDA dos prompts (v7.1/v7.7/v8) — ver abaixo
    "S23_QUIQUE_SERV":True,   # 🆕🔴 O QUIQUE DO SERVIÇO. A regra do Vasco (13 jul) — ver abaixo.
    "S18_MAO_PASSE":  False,  # ⛔ BLOQUEADA PELO RESSALTO (M3) — ver abaixo
    "S19_2_TOQUES":   False,  # ⛔ BLOQUEADA PELA PAREDE — ver abaixo
}

# ===========================================================================================
# 🔴🔴 S23 — O QUIQUE DO SERVIÇO.   REGRA DO VASCO, 13 jul 2026.   ⚠️ NÃO PERDER ESTA REGRA.
#
#   "Temos de matar este lixo pela BOLA NA MÃO DO NÃO SERVIDOR — ANTES DE BATER NO CHÃO."
#   "Mesmo que tenha kick, SÓ O ÚLTIMO antes da mudança de direção para o outro campo CONTA."
#
# A LEI (é do jogo, não é um limiar — sobrevive a outra câmara):
#
#       NÃO HÁ PONTO SEM SERVIÇO.   E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.
#
#       o SERVIDOR      larga a bola  ->  ela QUICA (na linha de serviço)  ->  e SÓ DEPOIS bate
#       o NÃO SERVIDOR  tem a bola na mão  ->  PASSA-A / ATIRA-A     ⇒  **SEM QUIQUE**
#
#   ⇒ um segmento que arranca SEM um quique FUNDO antes da 1.ª travessia **NÃO É UM PONTO**.
#
# 🔑 "SÓ O ÚLTIMO CONTA" (Vasco): a bola pode quicar várias vezes no intervalo (o kick, o
#    jogador a apanhá-la). O quique do SERVIÇO é o ÚLTIMO antes de a bola mudar de campo.
#    Medido: com o PRIMEIRO, os inícios fugiam até 2 s para trás. Com o ÚLTIMO, ficam a <1 s.
#
# MEDIDO (13 jul), com o detetor do `ressalto.py` (que já acertava 13/13 nos serviços):
#       os 13 pontos REAIS ....... 13/13 têm quique fundo antes  (prof 1,04 a 1,45)
#       o segmento de LIXO ....... 0 quiques.  ZERO.
#   Separação PERFEITA, sem afinar nada. Os quiques caem todos EM CIMA DA LINHA DE SERVIÇO —
#   exactamente onde a S9 do Vasco diz que o servidor larga a bola.
#
# 🔓 O QUE ISTO DESBLOQUEIA: é o que permite AMPLIAR a faixa de passagem (MIN_PROF 0.35 -> 0.15)
#    sem trazer lixo. E a ampliação tira os pontos 10 e 11 de cima de UMA travessia única
#    (1 -> 3) — que era o risco real para o 2.º vídeo (uma travessia falha, o ponto DESAPARECE).
#
# ⚠️ É a 1.ª vez que o RESSALTO entra no pipeline. Acerta 13/13 aqui; noutro vídeo, não se sabe.
#    Se o 2.º vídeo perder pontos, DESLIGA-SE ISTO PRIMEIRO (`--sem S23_QUIQUE_SERV`).
QUIQUE_JANELA = 3.0   # ⚠️ ATALHO MEU (declarado): onde procurar o quique antes da 1.ª travessia.
                      #    (o ressalto.py mediu os 13 quiques a 0,0–2,9 s antes)
QUIQUE_PROF   = 0.7   # ⚠️ ATALHO MEU (declarado): "fundo" = lá atrás, na linha de serviço.
                      #    Os 13 serviços deram prof 1,04–1,45 ⇒ folga enorme sobre o corte.
DY_MIN        = 1.0   # ⚠️ AJUSTE (vinha do ressalto.py): píxeis de descida/subida da inversão.


def ressaltos(R, tks):
    """O QUIQUE — a inversão VERTICAL: a bola vinha a DESCER e passa a SUBIR. É o chão.
    (O `Theta` do BlurBall dá a direção a ~2° numa ÚNICA deteção ⇒ vê-se a componente vertical.)
        o CHÃO    inverte na VERTICAL    (desce -> sobe)   <- é ISTO
        a PAREDE  inverte na HORIZONTAL  (vai -> volta)
        a RAQUETE inverte em qualquer direção — mas tem um JOGADOR ao pé
    ⚠️ DEFINIDA AQUI, UMA SÓ VEZ. O `ressalto.py` importa-a daqui — não duplicar
       (duas cópias da mesma regra é a doença da S12: uma delas fica para trás em silêncio)."""
    out = []
    for tk in tks:
        for i in range(1, len(tk) - 1):
            a, b, c = tk[i-1], tk[i], tk[i+1]
            if c - a > 8:
                continue
            if R[b][1] - R[a][1] > DY_MIN and R[c][1] - R[b][1] < -DY_MIN:
                out.append(b)
    g = []
    for f in out:
        if not g or f - g[-1][-1] > 3:
            g.append([f])
        else:
            g[-1].append(f)
    return [x[0] for x in g]


def quique_do_servico(a, b, CR, R, RES, prof):
    """S23 — o quique do SERVIÇO deste segmento, ou None se não houver (⇒ não é um ponto).
    🔑 O ÚLTIMO quique FUNDO antes da 1.ª travessia (Vasco: "só o último conta")."""
    cs = [c for c in CR if a <= c <= b]
    if not cs:
        return None
    c0 = min(cs)
    j0 = c0 - int(QUIQUE_JANELA * FPS)
    qs = [q for q in RES if j0 <= q <= c0 and q in R
          and prof(R[q][0], R[q][1])[1] >= QUIQUE_PROF]
    return max(qs) if qs else None

# ⛔ S19_2_TOQUES — REGRA DO VASCO (13 jul), CERTA, MAS BLOQUEADA. NÃO LIGAR SEM O M3.
#    "2 toques na raquete sem mudança de campo/direção da bola para o outro campo = fim do ponto."
#    (É verdade no padel: dois toques seguidos sem devolver é falta. E no intervalo é o que os
#     jogadores fazem — a bola aos saltinhos na raquete.)
#    MEDIDO HOJE: 12 dos 14 eventos caem A MEIO de pontos reais.
#    CAUSA: **a bola a bater na PAREDE**. Muda de direção com força e vai depressa — para o meu
#    detetor é indistinguível de uma raquetada. E no padel joga-se de parede a toda a hora.
#    ⇒ É o MESMO bloqueio de sempre: não sei distinguir RAQUETE / PAREDE / CHÃO. É o RESSALTO.
#    A regra é boa. Falta-lhe o M3.

# ⚠️ PAN_TEM_JOGADOR — regra do Vasco aplicada às pancadas (a mesma lógica da rede: "longe de uma
#    bounding box => ninguém lhe tocou"). Uma raquetada a 6 meios-campos de qualquer jogador não é
#    uma raquetada: é RUÍDO (um ponto branco no público). Era ela que esticava o ponto 1 até 45,7s.
#    Medido: a 3 meios-campos rejeita 2 pancadas fantasma e NENHUMA dentro de um ponto real.
#    ⚠️ Não resolve o ponto 1 todo: a pancada que resta (~43s) TEM um jogador ao pé — é alguém a
#    bater na bola ENTRE os pontos. Para a distinguir era preciso saber que ali não decorre um
#    ponto ⇒ detetor de serviço ⇒ M3. Outra vez.
PAN_DIST_MAX = 3.0  # ✅ em MEIOS-CAMPOS locais (não são píxeis)

# 🕳️ PAUSA_MINIMA — REGRA PERDIDA DOS PROMPTS (v7.1/v7.7/v8), NUNCA IMPLEMENTADA.
#    "Pausa média entre pontos: 5–15 s."
#    Uma pausa CURTA DEMAIS é IMPOSSÍVEL: entre pontos, os jogadores têm de ir buscar a bola e
#    posicionar-se para o serviço. Se o pipeline produz uma pausa de 2,6 s, então a CAUDA do
#    segmento anterior está esticada — e NÃO É PRECISO SABER PORQUÊ para a aparar.
#    (Era o PONTO 1: cauda de 3,5 s. Nenhuma outra regra a apanhava — a raquetada que a esticava
#     era do INTERVALO, com um jogador ao pé, indistinguível de jogo. Só o M3 a mataria.
#     Esta regra mata-a de graça, sem saber o que lá está.)
#
#    ⚠️ SÓ APARA A CAUDA. NUNCA mexe no INÍCIO do segmento seguinte
#       ⇒ é ESTRUTURALMENTE INCAPAZ de perder um serviço. (Medido: recall intacto até aos 6 s.)
#
# 🧠 APRENDIDA POR DUPLA (Vasco, 13 jul):
#    "esta regra tem uma MÉDIA ASSOCIADA A CADA JOGADOR, que podes ir notando ao longo do vídeo"
#    ⇒ o número NÃO é meu. Sai do PRÓPRIO VÍDEO, em 2 passagens:
#         1ª — corre sem a regra e observa as pausas que ele próprio produziu
#         2ª — pausa mínima = mediana − K×MAD  (robusto a outliers; MAD, não desvio-padrão)
#    Neste jogo: mediana 10,9 s (a real é 10,5 — acertou) ⇒ mínima aprendida 5,3 s.
#    🔒 CHÃO DE SEGURANÇA (decisão do Vasco): NUNCA descer abaixo de 4 s, aprenda o que aprender.
PAUSA_CHAO = 4.0   # 🔒 chão do Vasco — a regra nunca apara abaixo disto
PAUSA_K    = 2.5   # ⚠️ AJUSTE — nº de MADs abaixo da mediana. 2,5 = limiar clássico de outlier.
                   #    (K=2,0 dava +0,8 de precisão e −0,1 de recall. A diretriz manda no recall.)


def pausa_aprendida(M):
    """1ª passagem: o RITMO DESTA DUPLA, lido do próprio vídeo. Nunca abaixo do chão do Vasco."""
    if len(M) < 3:
        return PAUSA_CHAO
    p = np.array([(M[i+1][0] - M[i][1]) / FPS for i in range(len(M) - 1)])
    med = np.median(p)
    mad = np.median(np.abs(p - med))
    return max(PAUSA_CHAO, med - PAUSA_K * mad)

# ⛔ S18_MAO_PASSE — REGRA DO VASCO (13 jul), CERTA, MAS BLOQUEADA. NÃO LIGAR SEM O M3.
#    "se vai da mão para o adversário SEM ser cruzado no quadrado de serviço, sem ser em regime
#     de serviço com posicionamentos de serviço — é LIXO (entre pontos)."
#    MEDIDO HOJE: dos 12 serviços REAIS, só 2 se leem como "cruzados" no momento em que a bola
#    passa a rede. Não é o teste que está mal — é que **o cruzado do serviço só se vê no
#    RESSALTO**, dentro do quadrado. Na rede, a bola ainda não atravessou a central.
#    ⇒ Ligar isto hoje VETARIA 10 DOS 12 PONTOS REAIS.
#    A regra é boa. Falta-lhe o RESSALTO (S4/S9/S10) — o bloqueio único do M3.
#    A outra metade (formação de serviço, S3, ler só os 2 de cima) EXISTE em
#    `padelpro/modules/servico.py::formacao_de_cima()` e está DESLIGADA. É o caminho.

# ===========================================================================================
#  B2 — A CONTINUIDADE DA BOLA.   "A bola não se teletransporta."   (regra do Vasco)
#  LEI DO VASCO (13 jul):  a bola de padel não passa dos 180 km/h.
#
#  A CONVERSÃO (sem números inventados):
#     180 km/h = 50 m/s = 1,67 m por frame (a 29,97 fps)
#     o maior meio-campo do campo = 291 px = 6,95 m   (o sítio mais perto da câmara)
#     => 1,67 m  =  70 px/frame  no pior caso do CHÃO
#
#  ⚠️ O QUE APRENDI HOJE, E ESTAVA ERRADO NA MINHA CABEÇA:
#     ❌ NÃO se pode usar a régua LOCAL (o meio-campo no `y` da bola) para limitar a bola.
#        A RÉGUA É DO CHÃO. A BOLA VOA. Uma bola alta à frente da câmara aparece nos mesmos
#        píxeis que uma bola rasteira ao fundo — aplicar-lhe a régua do fundo (23 px/frame)
#        corta-lhe a cadeia. Testado: RECALL 96,2 -> 32,1. A régua vale para os PÉS e os
#        RESSALTOS (que estão no chão), NÃO para a bola em voo.
#     ❌ E o "pior caso do chão" (70 px) também não chega para a COSTURA: a bola a 3 m de
#        altura está MAIS PERTO da câmara do que qualquer ponto do chão => aparece MAIOR.
#        A régua do chão dá um MÍNIMO, não um máximo. Testado: parte entre 78 e 100 px.
# ===========================================================================================
VMAX       = 70     # ✅ DERIVADO: 180 km/h (lei do Vasco) no meio-campo mais perto (291 px).
                    #    ⚠️ e é um parâmetro MORTO: de 60 a 117 px os números não mexem uma
                    #    décima. Quem faz o trabalho é a costura por Theta. Fica correto, não
                    #    fica importante.
GAP        = 9
VMAX_THETA = 140    # ⚠️ AJUSTE, com razão: 2 × VMAX. O "2" é o fator da ALTURA da bola — ela
                    #    voa acima do plano do chão, logo mais perto da câmara, logo maior.
                    #    NÃO é derivável só da calibração do campo (faltaria a altura da câmara).
                    #    É AQUI que a continuidade da bola realmente trabalha.
GAP_THETA  = 20
TOL_THETA  = 35     # graus
L_COSTURA  = 1      # baixo de propósito: é o que deixa passar o BALÃO (bola lenta)
MIN_DET    = 4
MIN_PROF   = 0.15   # ⚠️ ATALHO. 🔴 ERA 0.35 até 13 jul — A FAIXA CEGA À VOLTA DA REDE.
                    #    O Vasco: "os de cá, perto da rede, devolvem a bola muito ALTA e PERTO
                    #    da rede — não dá tempo à bola de passar, nos frames." Tinha razão:
                    #    a 0.35 o código ignorava tudo num raio de 35% do meio-campo à volta da
                    #    rede ⇒ o VOLLEY à rede atravessava e morria lá dentro, invisível.
                    #    A 0.35: 55 travessias, e os pontos 10/11/13 penduradas em UMA SÓ
                    #      (tirar essa travessia => O PONTO DESAPARECE. Medido.)
                    #    A 0.15: 65 travessias. Pontos 10 e 11 passam de 1 -> 3. Deixam o fio.
                    #    ⚠️ SÓ SE PODE BAIXAR PORQUE A S23 (quique do serviço) MATA O LIXO QUE
                    #       ISTO TRAZIA. As duas andam JUNTAS. Desligar a S23 sem repor o 0.35
                    #       traz de volta o segmento falso dos 281s.
L_RAQUETE  = 11     # ⚠️ ATALHO — a regra (mão vs raquete) é lei; o NÚMERO é ajuste
PAN_DTHETA = 20     # ⚠️ ATALHO
PAN_L      = 7      # ⚠️ ATALHO
SILENCIO   = 4.0    # ⚠️ ATALHO
PAD_ANTES  = 1.6    # ⚠️ ATALHO
M_COM_PAN  = 2.0    # certeza  -> corte rente
M_SEM_PAN  = 5.0    # dúvida   -> mais margem   (S16: NÃO inverter!)
DUR_MIN    = 1.5

# --- S17 / S18 — FIM CERTO -> corte a 0,5 s  (regras do Vasco, 13 jul) ---
M_FIM_CERTO = 0.5   # "mal detetes que toca na rede/mão, máximo 0,5s e o ponto está terminado"

# 🔒🔒 S17 — A REGRA DA REDE. O VASCO DECLAROU-A PERFEITA (13 jul).
#      NÃO MEXER. NÃO "AFINAR". NÃO "MELHORAR". Pontos 2, 3, 5 e 10 acabam ao segundo.
RED_DTHETA  = 60    # ⚠️ ajuste — a viragem de uma bola que BATE. A que passa por cima quase não vira.
RED_L_PARA  = 2.0   # ⚠️ ajuste — a bola a PARAR
RED_DIST    = 0.10  # ✅ FRAÇÕES do meio-campo local (não são píxeis). "longe de qualquer box"

MAO_L       = 3.0   # ⚠️ ajuste — a bola PARADA
MAO_DUR     = 15    # frames (0,5 s). 🔒 NÃO BAIXAR: a 0,3 s a regra corta pontos a meio e o recall
                    #    cai de 96,2 para 82. A DURAÇÃO é o que separa a MÃO do LOB (que também vai
                    #    lento, mas só um INSTANTE, no ponto alto).
MAO_RAIO    = 0.10  # ✅ frações do meio-campo local


def carregar():
    cal = json.load(open(CAL))
    ev = lambda c, t: float(np.polyval(c, t))
    y_rb = lambda x: ev(cal["rede_base_coef"], x)
    y_sp = lambda x: ev(cal["servico_perto_coef"], x)
    y_sl = lambda x: ev(cal["servico_longe_coef"], x)

    def prof(x, y):
        """0 = na rede · 1 = na linha de serviço · >1 = atrás dela."""
        yr = y_rb(x)
        if y > yr:
            return "baixo", (y - yr) / max(y_sp(x) - yr, 1)
        return "cima", (yr - y) / max(yr - y_sl(x), 1)

    R = {}
    for r in csv.DictReader(open(BOLA)):
        if int(float(r["Visibility"])):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]),
                                  float(r["L"]), float(r["Theta"]))
    return R, prof


def d(R, a, b):
    return math.hypot(R[a][0] - R[b][0], R[a][1] - R[b][1])


# ===========================================================================================
#  S17 + S18 — O FIM CERTO DO PONTO.   Vasco, 13 jul 2026.
#
#  "Mal detetes que toca na mão, corpo ou rede, máximo 0,5s quero o ponto terminado."
#
#  ⚠️ O QUE NÃO SE PODE FAZER (medido — 60 de 94 candidatos caíam A MEIO de pontos reais):
#     usar a POSIÇÃO na rede. Nesta câmara (de lado, baixa, sem profundidade) a bola que passa
#     POR CIMA da rede e a bola que BATE na rede ocupam OS MESMOS PÍXEIS. A banda da rede tem
#     35 px; o meio-campo do fundo tem 100. Todas as bolas passam ali.
#
#  ✅ O QUE O VASCO DEU, e resolve:
#     "se a bola MUDA DE DIREÇÃO (ou PARA) na rede, LONGE de uma bounding box, o ponto acabou."
#     A bola que passa NÃO vira. A que bate, vira — ou morre. E se não há jogador ao pé,
#     não foi ninguém que lhe bateu: foi a REDE.
#     Medido: 0 eventos a meio de pontos reais · 4 no fim (pontos 2,3,5,10) · 11 nos intervalos.
#
#  ✅ E a MÃO: "a bola na mão fica lenta ou parada" (B10/S15/S18).
#     Sozinha não chega — a bola também vai lenta no ponto alto de um LOB (49 falsos a meio de
#     pontos). O que as separa é a DURAÇÃO: o lob está lento um INSTANTE; a mão SEGURA-A.
#     Medido com L<=3 sustentado 0,5s: 0 eventos a meio de pontos. Hoje não corta nada (a bola
#     na mão mal se vê), mas é segura e fica LIGADA — não guardada a apodrecer.
# ===========================================================================================
def campo(cal):
    ev = lambda c, x: float(np.polyval(c, x))
    y_topo = lambda x: ev(cal["rede_topo_coef"], x)
    y_base = lambda x: ev(cal["rede_base_coef"], x)

    def meio_campo_px(x, y):
        """A RÉGUA LOCAL: quantos píxeis vale o meio-campo (6,95 m) NAQUELE x, NAQUELE lado.
        Longe ~95 px · perto ~275 px. É por isto que píxeis absolutos não sobrevivem."""
        yb = y_base(x)
        return (abs(ev(cal["servico_perto_coef"], x) - yb) if y > yb
                else abs(yb - ev(cal["servico_longe_coef"], x)))

    return y_topo, y_base, meio_campo_px


def fim_certo(R, cal, boxes):
    """Devolve os frames em que o ponto ACABOU DE CERTEZA (rede ou mão). Corte a 0,5s."""
    y_topo, y_base, meio = campo(cal)
    fs = sorted(R)

    def dist_box(f, x, y):
        """distância ao jogador mais próximo, em FRAÇÕES do meio-campo local."""
        if f >= len(boxes) or not boxes[f]:
            return 99.0
        m = max(meio(x, y), 1)
        return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                   for x1, y1, x2, y2 in boxes[f])

    # --- S17: vira (ou pára) NA REDE, LONGE de qualquer box ---
    rede = []
    for a, b in zip(fs, fs[1:]):
        if b - a > 4:
            continue
        x, y = R[b][0], R[b][1]
        if not (y_topo(x) <= y <= y_base(x)):
            continue
        virou = abs(((R[b][3] - R[a][3] + 90) % 180) - 90) >= RED_DTHETA
        parou = R[b][2] <= RED_L_PARA
        if (virou or parou) and dist_box(b, x, y) >= RED_DIST:
            rede.append(b)

    # --- S18 (Vasco, 13 jul): "BOLA PARADA dentro da bounding box, SEM MUDAR DE CAMPO
    #     => ponto terminado de certeza, sem raquetada."
    #     TRÊS condições, e são precisas as três:
    #       PARADA          -> L <= MAO_L   (⛔ lenta sozinha não chega: o lob vai lento no ponto
    #                                        alto — 49 falsos a meio de pontos reais)
    #       DENTRO DA BOX   -> é a mão/corpo de alguém, não uma bola qualquer no chão
    #       SEM MUDAR DE CAMPO -> se atravessou a rede, foi BATIDA. Se fica do mesmo lado,
    #                             ninguém lhe bateu.
    #     Medido: 0 eventos a meio de pontos reais.
    lado = lambda f: "baixo" if R[f][1] > y_base(R[f][0]) else "cima"
    parada = [f for f in fs
              if R[f][2] <= MAO_L and dist_box(f, R[f][0], R[f][1]) <= MAO_RAIO]
    runs = []
    for f in parada:
        if runs and f - runs[-1][-1] <= 3:
            runs[-1].append(f)
        else:
            runs.append([f])
    mao = [r[0] for r in runs
           if r[-1] - r[0] + 1 >= MAO_DUR                    # ficou lá
           and len({lado(f) for f in r}) == 1]               # SEM MUDAR DE CAMPO

    if not REGRAS["S17_REDE"]:
        rede = []
    if not REGRAS["S18_MAO_PARADA"]:
        mao = []
    ev_ = sorted(set(rede) | set(mao))
    out = []
    for f in ev_:
        if not out or f - out[-1] > 15:
            out.append(f)
    return out


def vai_e_vem(R):
    """S/B8 — A->B longe, A->C perto  =>  B é ERRO. Tira o frame, não parte a cadeia."""
    if not REGRAS["B8_VAI_E_VEM"]:
        return R
    fs = sorted(R)
    mortos = []
    for i in range(1, len(fs) - 1):
        a, b, c = fs[i-1], fs[i], fs[i+1]
        if c - a > 30:
            continue
        if (d(R,a,b) > 60 and d(R,b,c) > 60
                and d(R,a,c) < 0.5 * min(d(R,a,b), d(R,b,c))):
            mortos.append(b)
    for m in mortos:
        R.pop(m)
    return R


def erro_theta(R, a, b):
    """O Theta acerta a direção a ~2°, e fá-lo numa ÚNICA deteção (graus, eixo mod 180)."""
    dx, dy = R[b][0]-R[a][0], R[b][1]-R[a][1]
    if math.hypot(dx, dy) < 4:
        return 0.0
    real = math.degrees(math.atan2(dy, dx))
    return max(abs(((R[a][3]-real+90) % 180) - 90),
               abs(((R[b][3]-real+90) % 180) - 90))


def tracklets(R):
    """COSTURA POR THETA: se o buraco é grande mas a DIREÇÃO bate certo, é a mesma bola."""
    fs = sorted(R)
    out, cur = [], [fs[0]]
    for a, b in zip(fs, fs[1:]):
        g = b - a
        liga = (g <= GAP and d(R,a,b) <= VMAX * g)
        if not liga and REGRAS["B6_THETA"]:
            liga = (g <= GAP_THETA and d(R,a,b) <= VMAX_THETA * g
                    and R[a][2] >= L_COSTURA and R[b][2] >= L_COSTURA
                    and erro_theta(R, a, b) <= TOL_THETA)
        if liga:
            cur.append(b)
        else:
            out.append(cur); cur = [b]
    out.append(cur)
    return [t for t in out if len(t) >= MIN_DET]


def cruzamentos(R, tks, prof):
    """
    A bola atravessa a rede DE FUNDO A FUNDO (roçar a fita não conta).
    S15 — MÃO vs RAQUETE: só conta se a bola vier da RAQUETE (L alto), não da MÃO.
          Medido: serviços L=17,4 · passagens à mão L=2,7.
    🎈 BUG: o BALÃO chega LENTO e é rejeitado aqui. Parte os pontos 3 e 6->7.
    """
    fs = sorted(R)
    Lmax = lambda f: max([R[g][2] for g in fs if abs(g-f) <= 5] or [0])
    out = []
    for tk in tks:
        ult = None
        for f in tk:
            l, p = prof(R[f][0], R[f][1])
            if p < MIN_PROF:
                continue
            raq = Lmax(f) >= L_RAQUETE if REGRAS["S15_MAO_RAQUETE"] else True
            if ult and ult != l and raq:
                out.append(f)
            ult = l
    return sorted(out)


def pancadas(R, cal=None, boxes=None):
    """Mudança brusca de direção com a bola a voar. A 0.4: 135 (a 0.7 eram só 57).

    PAN_TEM_JOGADOR (Vasco, 13 jul) — uma RAQUETADA tem de ter um JOGADOR ao pé.
    A 6 meios-campos de toda a gente, ninguém lhe bateu: é ruído."""
    fs = sorted(R)
    out = []
    for a, b in zip(fs, fs[1:]):
        if b - a > 8:
            continue
        if (max(R[a][2], R[b][2]) >= PAN_L
                and abs(((R[b][3]-R[a][3]+90) % 180) - 90) >= PAN_DTHETA):
            out.append(b)
    if REGRAS["PAN_TEM_JOGADOR"] and cal and boxes:
        _, _, meio = campo(cal)

        def dist_box(f):
            x, y = R[f][0], R[f][1]
            if f >= len(boxes) or not boxes[f]:
                return 99.0
            m = max(meio(x, y), 1)
            return min(math.hypot(max(x1-x, 0, x-x2), max(y1-y, 0, y-y2)) / m
                       for x1, y1, x2, y2 in boxes[f])

        out = [f for f in out if dist_box(f) <= PAN_DIST_MAX]

    ag = []
    for f in out:
        if ag and f - ag[-1][-1] <= 5:
            ag[-1].append(f)
        else:
            ag.append([f])
    return [g[0] for g in ag]


def rallies(CR, PAN, FIM=(), RES=(), R=None, prof=None):
    grp = [[CR[0]]]
    for c in CR[1:]:
        if c - grp[-1][-1] <= SILENCIO * FPS:
            grp[-1].append(c)
        else:
            grp.append([c])

    S = []
    for g in grp:
        a, b = g[0], g[-1]
        # S12 À LETRA (13 jul) — o fim do ponto segue a ÚLTIMA PANCADA, não o último CRUZAMENTO.
        # ANTES: janela = b + 1.5s  <- número mágico meu, sem nome. O ponto continua depois de a
        # bola deixar de cruzar a rede (volta de parede, devolução rente, bola que morre do mesmo
        # lado) e essas pancadas eram IGNORADAS. Partia os pontos 4 e 5 e cortava o 3 a meio.
        # AGORA: a janela é o SILENCIO — o parâmetro que já significa "a bola deixou de ser batida".
        # Não acrescenta nenhum número. Recall 93,2 -> 97,0. Pontos partidos: 2 -> 0.
        # S12 — a janela é o SILENCIO (a última PANCADA manda). Desligada: volta ao 1,5s antigo.
        jan = SILENCIO if REGRAS["S12_ULT_PANCADA"] else 1.5
        pan = [q for q in PAN if a <= q <= b + jan*FPS]
        # S16 — CERTEZA (há pancada) -> corte rente. DÚVIDA (não há) -> mais margem.
        if REGRAS["S16_DUVIDA"]:
            fim = int(max(pan) + M_COM_PAN*FPS) if pan else int(b + M_SEM_PAN*FPS)
        else:
            fim = int((max(pan) if pan else b) + M_COM_PAN*FPS)
        # S17/S18 — FIM CERTO (rede ou mão/corpo parada): não há dúvida a gerir.
        # Corte a 0,5s. Só conta DEPOIS do início do ponto, logo NUNCA pode cortar um a meio.
        fc = [f for f in FIM if a < f <= fim]
        if fc:
            fim = min(fim, int(fc[0] + M_FIM_CERTO*FPS))
        S.append((max(0, int(a - PAD_ANTES*FPS)), fim))

    S = sorted(s for s in S if (s[1]-s[0])/FPS >= DUR_MIN)
    if not REGRAS["S13_TIMELINE"]:
        return [(a, b) for a, b in S]

    # S13 — A TIMELINE NUNCA ANDA PARA TRÁS. Se dois se tocam, são O MESMO PONTO.
    M = [list(S[0])]
    for a, b in S[1:]:
        if a <= M[-1][1]:
            M[-1][1] = max(M[-1][1], b)
        else:
            M.append([a, b])

    # 🔴 S23 — O QUIQUE DO SERVIÇO (Vasco, 13 jul).  "NÃO HÁ PONTO SEM SERVIÇO, E NÃO HÁ
    #    SERVIÇO SEM A BOLA BATER NO CHÃO." Um segmento sem quique FUNDO antes da 1.ª travessia
    #    não é um ponto — é o NÃO-SERVIDOR a passar a bola à mão (não a deixa quicar).
    #    ⚠️ CORRE ANTES DA PAUSA: se o lixo entrasse na mediana das pausas, envenenava-a.
    #    Medido: 13/13 pontos reais têm quique fundo · o lixo tem ZERO. Separação perfeita.
    if REGRAS["S23_QUIQUE_SERV"] and RES and R is not None and prof is not None:
        M = [s for s in M if quique_do_servico(s[0], s[1], CR, R, RES, prof) is not None]

    # PAUSA MÍNIMA (regra perdida dos prompts + a nota do Vasco: aprender por dupla).
    # Uma pausa curta demais entre pontos é IMPOSSÍVEL: a CAUDA do anterior está esticada.
    # 2 passagens: aprende o ritmo DESTE jogo, depois apara. Só a cauda; nunca o início.
    if REGRAS["PAUSA_MINIMA"]:
        pmin = pausa_aprendida(M)
        for i in range(len(M) - 1):
            if (M[i+1][0] - M[i][1]) / FPS < pmin:
                novo = M[i+1][0] - int(pmin * FPS)
                if novo > M[i][0] + DUR_MIN * FPS:      # nunca matar o segmento
                    M[i][1] = novo

    return [(a, b) for a, b in M]


def avaliar(M):
    g = np.zeros(N_FRAMES, bool)
    for a, b in GT:
        g[int(a*FPS):int(b*FPS)+1] = True
    m = np.zeros(N_FRAMES, bool)
    for a, b in M:
        m[max(a,0):min(b, N_FRAMES-1)+1] = True
    tp = (m & g).sum(); fp = (m & ~g).sum(); fn = (~m & g).sum()
    rec = 100*tp/max(tp+fn, 1); pre = 100*tp/max(tp+fp, 1)
    serv = {k for a, b in M for k, (g0, _) in enumerate(GT, 1)
            if a/FPS - 1.0 <= g0 <= b/FPS}
    return dict(n=len(M), tempo=m.sum()/FPS, servicos=len(serv),
                recall=rec, precisao=pre, f1=2*rec*pre/max(rec+pre, 1))


def main():
    R, prof = carregar()
    print(f"bola: {len(R)} frames ({100*len(R)/N_FRAMES:.1f}%)")
    R = vai_e_vem(R)
    tks = tracklets(R)
    CR = cruzamentos(R, tks, prof)
    cal = json.load(open(CAL))
    boxes = pickle.load(open(BOXES, "rb"))["player_boxes"]
    PAN = pancadas(R, cal, boxes)
    FIM = fim_certo(R, cal, boxes)
    RES = ressaltos(R, tks)                      # 🔴 S23 — os quiques (o chão)
    print(f"tracklets {len(tks)} | cruzamentos {len(CR)} | pancadas {len(PAN)} | "
          f"fins certos (rede/mão) {len(FIM)} | quiques {len(RES)}")
    M = rallies(CR, PAN, FIM, RES, R, prof)
    r = avaliar(M)
    print(f"\n>>> {r['n']} pontos (reais: {len(GT)}) | {r['tempo']:.1f}s (reais: {sum(b-a for a,b in GT):.1f}s)")
    print(f">>> servicos {r['servicos']}/{len(GT)}")
    print(f">>> RECALL {r['recall']:.1f}%   PRECISAO {r['precisao']:.1f}%   F1 {r['f1']:.1f}")

    if "--video" in sys.argv:
        lst = "\n".join(f"file 'tu{i:02d}.mp4'" for i in range(1, len(M)+1))
        open("/tmp/tu.txt", "w").write(lst + "\n")
        for i, (a, b) in enumerate(M, 1):
            subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",f"{a/FPS:.2f}",
                "-t",f"{(b-a)/FPS:.2f}","-i",VIDEO,"-c:v","libx264","-pix_fmt","yuv420p",
                "-crf","23","-an","-vf",
                f"drawtext=text='ponto {i}/{len(M)}   {a/FPS:.0f}s':x=10:y=10:"
                f"fontsize=20:fontcolor=white:box=1:boxcolor=black@0.6",
                f"/tmp/tu{i:02d}.mp4"])
        subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0",
                        "-i","/tmp/tu.txt","-c","copy","TEMPO_UTIL.mp4"], cwd="/tmp")
        subprocess.run(["cp","/tmp/TEMPO_UTIL.mp4","TEMPO_UTIL.mp4"])
        print("\n-> TEMPO_UTIL.mp4")


if __name__ == "__main__":
    main()
