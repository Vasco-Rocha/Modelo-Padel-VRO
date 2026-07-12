# PadelPro Vision — HANDOFF

**Estado: 13 jul 2026.**  RECALL 96,3% · PRECISÃO 95,9% · F1 96,1 · 13/13 serviços
(de manhã estava em 72/63)

===============================================================================
# 🛑 REGRA ZERO — NÃO ALTERAR NADA
===============================================================================

**Ordem explícita do Vasco (13 jul):** "quando abrir novas conversas, não quero
qualquer tipo de alteração."

O pipeline está TRAVADO e FUNCIONA. Numa conversa nova:
- ❌ NÃO mexer no gerar_tempo_util.py
- ❌ NÃO "melhorar", "afinar", "limpar" ou "refatorizar"
- ❌ NÃO mudar um único número
- ❌ NÃO alterar os valores travados no teste_regressao.py
- ✅ LER, explicar, diagnosticar, medir — à vontade
- ✅ Alterações SÓ se o Vasco as pedir EXPLICITAMENTE, e depois de as discutir

**Se o teste_regressao.py falhar, a alteração é que está errada. Nunca o teste.**

===============================================================================
## CORRER (tudo em CPU, em segundos — sem GPU, sem Colab)
===============================================================================

    cd padelpro-vision
    python3 teste_regressao.py      # 🔒 confirma que nada se partiu. SEMPRE, antes e depois.
    python3 gerar_tempo_util.py     # as métricas
    python3 gerar_tempo_util.py --video
    python3 ablacao.py              # quanto vale CADA regra ← SEMPRE que entra uma regra
    python3 ressalto.py             # detetor de ressalto (independente)
    python3 diag_pontos.py          # onde é que cada ponto perde
    python3 diag_fim.py             # S17/S18 — os fins certos

## GUARDAR
Duplo-clique no GUARDAR_TUDO.command (raiz do projeto). Desbloqueia o git, commit e push.
(O Claude não consegue mexer no .git a partir do sandbox — permissões do macOS.)

Cópias de segurança (correm sozinhas):
  BACKUPS/M1_<data>/  ·  padelpro-vision/snapshots/M1_<data>/  ·  Google Drive

===============================================================================
## O QUE ENTROU (TUDO regras do Vasco)
===============================================================================

| regra | ganho |
|---|---|
| GT CORRIGIDO — o Vasco acrescentou o 13.º rally (289,1s→fim) | precisão 91,8→93,9 SEM tocar no código |
| S12 À LETRA — o fim segue a ÚLTIMA PANCADA, não o último cruzamento | recall 93,2→97,0 · pontos partidos 2→0 |
| S17 REDE 🔒 — "vira (ou pára) na rede, LONGE de box → acabou" | +4 precisão. Pts 2,3,5,10 ao segundo. |
| S18 MÃO — "bola PARADA na box, SEM MUDAR DE CAMPO → acabou" | 0 cortes a meio |
| PAN_TEM_JOGADOR — uma raquetada tem de ter um jogador ao pé | mata pancadas-fantasma no público |
| PAUSA MÍNIMA APRENDIDA — "tem uma média por dupla, que vais notando" | +1,8 precisão. Cauda do pt1: 3,5s→1,2s |
| VMAX derivado — 180 km/h (lei do Vasco) ⇒ 70 px/frame | era 90, inventado (710 km/h ao fundo) |

===============================================================================
## 🔒 O QUE NÃO SE MEXE (ordens do Vasco)
===============================================================================
- S17 (rede) — "está perfeita! fixa e não deixes mudar." RED_DTHETA/RED_L_PARA/RED_DIST
- fim_dentro = 0 — nenhum "fim certo" pode cair A MEIO de um ponto real.
  Se subir: DESLIGAR a regra. NUNCA relaxar o teste.
- S18 duração 0,5s — a 0,3s corta pontos a meio e o recall cai para 82
- S16 — dúvida = mais margem; certeza = corte rente. NUNCA INVERTER (custou 12 pontos)
- Chão da pausa = 4s (Vasco)

===============================================================================
## ⛔ VIAS FECHADAS — MEDIDAS. Não repetir.
===============================================================================
| | porquê |
|---|---|
| S8 (fim = últ. pancada antes do serviço seguinte) | 98,9/47,1. Pancadas do INTERVALO esticam cada ponto até ao seguinte. |
| S18_MAO_PASSE (mão→adversário sem ser serviço) | só 2 dos 12 serviços se leem "cruzados" ⇒ vetava 10 dos 12 pontos |
| S19_2_TOQUES (2 toques sem mudar de campo) | 12 dos 14 eventos A MEIO de pontos. A PAREDE confunde-se com a raquete. |
| VIDRO DO FUNDO | a zona acima da linha de fundo É O CÉU. Tira jogo (96,3→92,8). E NÃO se resolve DESENHANDO — eventos bons e maus têm a MESMA distribuição de alturas. |
| BOLA SAI DE CAMPO | ⛔ o VASCO matou-a: há JOGO EXTERIOR, e o polígono é do CHÃO, não do vidro |
| SERVIÇO POR BAIXO / arranque horizontal | 3D ≠ imagem. Bola horizontal a afastar-se SOBE na imagem. Precisão 7-17%. |
| JOGADOR TOCA NA REDE | a box dos PÉS não vê a RAQUETE a tocar na rede. Precisa de pose. |
| R-PANCADA (mínimo local à box) | 96,5/90,4 — pior. Só 4 eventos em comum. |
| régua local aplicada à BOLA | A RÉGUA É DO CHÃO. A BOLA VOA. Recall 96→32. |
| fine-tune do YOLO da bola | best_v2 ficou pior que o best.pt |

===============================================================================
## 🚪 O BLOQUEIO ÚNICO: O RESSALTO
===============================================================================
QUATRO regras do Vasco pararam NA MESMA PORTA: não sei distinguir RAQUETE / PAREDE / CHÃO.

BOA NOTÍCIA (13 jul): o ressalto.py (independente) acerta 13/13 NOS SERVIÇOS.
A S9 do Vasco CONFIRMOU-SE nos dados — e os quiques caem em prof ≈ 1,0, EM CIMA DA LINHA DE
SERVIÇO, que é exactamente onde o servidor larga a bola. NÃO AFINEI NADA para isso acontecer.
(O duplo-quique para o FIM (S14) ainda não presta: 49 falsos a meio de pontos.)

===============================================================================
# ➡️ PRÓXIMO PASSO: O SEGUNDO VÍDEO. OUTRA CÂMARA.
===============================================================================
É o único teste que separa as LEIS do Vasco (sobrevivem) dos AJUSTES do Claude (não sobrevivem).

COMPROMISSO ASSUMIDO, ANTES DE VER OS RESULTADOS:
  NÃO SE TOCA EM NENHUM PARÂMETRO. L_RAQUETE=11, SILENCIO=4, PAD_ANTES=1,6, MIN_PROF=0,35,
  PAN_DTHETA=20 vão EXACTAMENTE como estão. O que sair, sai.
  Afiná-los ao vídeo novo torna o teste INÚTIL — passamos a ter dois vídeos decorados.

PREVISÃO ESCRITA (para não se poder fingir depois):
  - as LEIS (mão vs raquete, rede, Theta, timeline, última pancada) → AGUENTAM
  - os AJUSTES (L_RAQUETE, PAD_ANTES, MIN_PROF) → PARTEM
  - PAD_ANTES=1,6s é a DURAÇÃO DO RITUAL DO SERVIÇO — muda com a câmara
  - SILENCIO=4s é o mais provável de sobreviver (é tempo de jogo, não píxeis)

## 🔊 PEDIDO DE CAPTURA — mais importante que o ângulo da câmara

# GRAVAR COM ÁUDIO.

O som do QUIQUE, o da PAREDE e o da RAQUETE são TRÊS SONS DIFERENTES — e são exactamente as três
coisas que a imagem não distingue. O ÁUDIO NÃO PRECISA DE PROFUNDIDADE.
Estava nos prompts (v7.1, R15) e nunca foi usado.

O que o VASCO tem de fazer: o vídeo · a CALIBRAÇÃO (à mão, no calibrar_campo.html — regra C1
dele) · o GROUND-TRUTH (no anotador_rallies.html — E CONTAR TODOS OS PONTOS).
O que o CLAUDE faz: a bola (BlurBall) e os jogadores (YOLO), no Colab/Kaggle.

===============================================================================
## AS 3 LIÇÕES DO DIA (custaram caro — não repetir)
===============================================================================

1. 🚨 DESCONFIAR DO GROUND-TRUTH. O "falso" dos 289s ERA UM PONTO A SÉRIO. A precisão andou o dia
   a castigar-me por ACERTAR. Um falso positivo BEM-COMPORTADO (com cruzamentos, pancadas, duração
   normal) é VERDADE QUE FALTA AO GT. Mostrar o clip ao Vasco ANTES de o combater.

2. 🕳️ UM MAPA FEITO A PARTIR DO CÓDIGO SÓ VÊ O QUE SOBREVIVEU. A S12 e a S8 estavam marcadas ✅ e
   NÃO CORRIAM. A S12 estava lá COM O NOME CERTO A FAZER OUTRA COISA — pior que estar desligada,
   porque ninguém a vai procurar. LER O CÓDIGO, NÃO O MAPA.

3. 🧪 TESTAR, NÃO RACIOCINAR. Testei 1 das 9 regras perdidas e descartei as outras 8 com um
   raciocínio bonito ("tudo precisa de profundidade"). O Vasco perguntou "nenhuma ajudava
   portanto?" — e a que eu ia deitar fora (a PAUSA) foi a que resolveu o ponto 1.

> FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA.
> A rede (35 px) funciona; o vidro (meio ecrã) não.
> Serve para prever se uma ideia tem hipótese ANTES de a testar.
