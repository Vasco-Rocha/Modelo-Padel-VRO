# PadelPro Vision — HANDOFF

**Estado: 13 jul 2026.**  `RECALL 96,3% · PRECISÃO 95,9% · F1 96,1 · 13/13 serviços`
*(de manhã estava em 72/63)*

---

# 🛑 REGRA ZERO — LER ANTES DE TUDO

## **NÃO ALTERAR NADA.**

**Ordem explícita do Vasco (13 jul):** *"quando abrir novas conversas, não quero qualquer tipo de alteração."*

O pipeline está **TRAVADO** e **FUNCIONA**. Numa conversa nova:

- ❌ **NÃO** mexer no `gerar_tempo_util.py`
- ❌ **NÃO** "melhorar", "afinar", "limpar" ou "refatorizar" nada
- ❌ **NÃO** mudar um único número
- ❌ **NÃO** alterar os valores travados no `teste_regressao.py`
- ✅ **LER**, explicar, diagnosticar, medir — à vontade
- ✅ Alterações **só** se o Vasco as pedir **explicitamente**, e **depois de as discutir com ele**

**Se o `teste_regressao.py` falhar, a alteração é que está errada. Nunca o teste.**

---

## Correr (tudo em CPU, em segundos — sem GPU, sem Colab)

```bash
cd padelpro-vision
python3 teste_regressao.py        # 🔒 confirma que nada se partiu. CORRER SEMPRE, ANTES E DEPOIS.
python3 gerar_tempo_util.py       # as métricas
python3 gerar_tempo_util.py --video   # + a compilação do tempo útil
python3 ablacao.py                # quanto vale CADA regra   ← correr SEMPRE que entra uma regra
python3 ressalto.py               # o detetor de ressalto (independente, não entra no pipeline)
python3 diag_pontos.py            # onde é que cada ponto perde
python3 diag_fim.py               # S17/S18 — os fins certos, e onde caem
```

## Guardar

**Duplo-clique no `GUARDAR_TUDO.command`** (na raiz do projeto). Desbloqueia o git, faz commit e
push. *(O Claude não consegue mexer no `.git` a partir do sandbox — permissões do macOS.)*

Duas cópias de segurança, ambas correm sozinhas:
`BACKUPS/M1_<data>/` · `padelpro-vision/snapshots/M1_<data>/`

---

## Ficheiros

| | |
|---|---|
| `padelpro-vision/gerar_tempo_util.py` | **o pipeline inteiro.** Interruptores (`REGRAS`) no topo. Atalhos declarados. |
| `padelpro-vision/teste_regressao.py` | 🔒 **trava o estado.** Correr sempre. |
| `padelpro-vision/ablacao.py` | quanto vale cada regra, medido |
| `padelpro-vision/ressalto.py` | detetor de ressalto **independente** (13/13 nos serviços) |
| `REGRAS_DO_VASCO.md` | **as regras — S1-S19, B1-B10, J1-J9, C1-C5.** A fonte. |
| `REGRAS_PERDIDAS_dos_prompts.md` | **9 regras dos prompts que NUNCA chegaram ao código** |
| `MAPA_DAS_REGRAS.md` | o que corre e o que não corre ⚠️ *(feito a partir do CÓDIGO — só vê o que sobreviveu)* |
| `ground_truth_parada4.md` | a verdade: **13 rallies / 119,6 s** |
| `dados_parada4/traj_frames_Parada4_thr04.csv` | a bola a thr=0.4 (76,1%). Tem a coluna `score` ⇒ **nunca mais correr o modelo** para mudar de threshold. |
| `dados_parada4/player_boxes_parada4.pkl` | os jogadores |
| `TEMPO_UTIL_v17_pausa_aprendida.mp4` | **o melhor resultado, em vídeo** |

---

## O que entrou hoje (TUDO regras do Vasco)

| regra | ganho |
|---|---|
| **GT corrigido** — o Vasco acrescentou o **13.º rally** (289,1s → fim do vídeo) | precisão 91,8 → 93,9 **sem mexer numa linha de código** |
| **S12 à letra** — o fim segue a **última PANCADA**, não o último cruzamento | recall 93,2 → 97,0 · pontos partidos **2 → 0** |
| **S17 REDE** 🔒 — *"vira (ou pára) na rede, LONGE de uma box → acabou"* | **+4 precisão.** Pontos 2, 3, 5, 10 acabam **ao segundo**. |
| **S18 MÃO** — *"bola PARADA na box, SEM MUDAR DE CAMPO → acabou"* | 0 cortes a meio |
| **PAN_TEM_JOGADOR** — uma raquetada tem de ter um jogador ao pé | mata pancadas-fantasma no público |
| **PAUSA MÍNIMA APRENDIDA** — *"tem uma média por dupla, que vais notando"* | **+1,8 precisão.** Cauda do ponto 1: **3,5s → 1,2s** |
| **VMAX derivado** — 180 km/h (lei do Vasco) ⇒ 70 px/frame | era 90, inventado (**710 km/h** ao fundo) |

---

## 🔒 O que NÃO se mexe (ordens do Vasco)

- **S17 (rede)** — *"está perfeita! fixa e não deixes mudar."* `RED_DTHETA`/`RED_L_PARA`/`RED_DIST`.
- **`fim_dentro` = 0** — nenhum "fim certo" pode cair **a meio** de um ponto real.
  Se subir: **DESLIGAR a regra. NUNCA relaxar o teste.**
- **S18 duração 0,5 s** — a 0,3 s corta pontos a meio e o recall cai para **82**.
- **S16** — dúvida = mais margem; certeza = corte rente. **NUNCA INVERTER** (já esteve, custou 12 pontos).
- **Chão da pausa = 4 s** (Vasco). *(Não morde neste vídeo: a aprendida dá 5,3 s.)*

---

## ⛔ VIAS FECHADAS — MEDIDAS. Não repetir.

| | porquê |
|---|---|
| **S8** (fim = última pancada antes do serviço seguinte) | 98,9/**47,1**. Sem detetor de serviço, as pancadas do INTERVALO esticam cada ponto até ao seguinte. |
| **S18_MAO_PASSE** (mão→adversário sem ser serviço) | só **2 dos 12** serviços se leem como "cruzados" na rede ⇒ **vetava 10 dos 12 pontos** |
| **S19_2_TOQUES** (2 toques sem mudar de campo) | **12 dos 14** eventos a meio de pontos reais. A **PAREDE** confunde-se com a raquete. |
| **VIDRO DO FUNDO** | a zona acima da linha de fundo **é o CÉU**. Tira jogo (96,3 → 92,8). ⚠️ **E NÃO se resolve DESENHANDO** — eventos bons e maus têm a **mesma distribuição de alturas**. |
| **BOLA SAI DE CAMPO** | ⛔ **o Vasco matou-a:** há **jogo exterior**, e o **polígono é do chão, não do vidro** |
| **SERVIÇO POR BAIXO / arranque horizontal** | 3D ≠ imagem. Uma bola horizontal a afastar-se **sobe** na imagem. Precisão 7-17%. |
| **JOGADOR TOCA NA REDE** | a box dos **pés** não vê a **raquete** a tocar na rede. Precisa de pose. |
| **R-PANCADA (mínimo local à box)** | 96,5/**90,4**, pior que o atual. Só 4 eventos em comum. |
| **régua local aplicada à BOLA** | **A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96 → **32**. |
| **fine-tune do YOLO da bola** | `best_v2` ficou pior que o `best.pt` |

---

## 🚪 O BLOQUEIO ÚNICO: o RESSALTO

**Quatro** regras do Vasco pararam **na mesma porta**: não sei distinguir **RAQUETE / PAREDE / CHÃO**.

**Boa notícia (13 jul):** o `ressalto.py` (independente, não entra no pipeline) acerta
**13/13 nos serviços**. A **S9 do Vasco confirmou-se nos dados** — e os quiques caem em
`prof ≈ 1,0`, **em cima da linha de serviço**, que é exactamente onde o servidor larga a bola.
**Não afinei nada para isso acontecer.**
*(O duplo-quique para o FIM (S14) ainda não presta: 49 falsos a meio de pontos.)*

---

# ➡️ O PRÓXIMO PASSO (decidido pelo Vasco)

## **O SEGUNDO VÍDEO. Outra câmara.**

É o único teste que separa as **LEIS do Vasco** (sobrevivem) dos **AJUSTES do Claude** (não sobrevivem).

**COMPROMISSO ASSUMIDO, ANTES DE VER OS RESULTADOS:**
> **Não se toca em NENHUM parâmetro.** `L_RAQUETE=11`, `SILENCIO=4`, `PAD_ANTES=1,6`,
> `MIN_PROF=0,35`, `PAN_DTHETA=20` vão **exactamente como estão**. O que sair, sai.
> Afiná-los ao vídeo novo torna o teste **inútil** — passamos a ter dois vídeos decorados.

**Previsão escrita (para não se poder fingir depois):**
| | |
|---|---|
| as **LEIS** (mão vs raquete, rede, Theta, timeline, última pancada) | **aguentam** |
| os **AJUSTES** (`L_RAQUETE`, `PAD_ANTES`, `MIN_PROF`) | **partem** |
| o `PAD_ANTES=1,6s` | é a **duração do ritual do serviço** — muda com a câmara |
| o `SILENCIO=4s` | o mais provável de sobreviver (é tempo de jogo, não píxeis) |

## 🔊 PEDIDO DE CAPTURA — mais importante que o ângulo da câmara

# **GRAVAR COM ÁUDIO.**

O som do **quique**, o da **parede** e o da **raquete** são **três sons diferentes** — e são
exactamente as três coisas que a imagem não distingue. **O áudio não precisa de profundidade.**
Estava nos prompts (v7.1, R15) e nunca foi usado.

**O que o Vasco tem de fazer:** o vídeo · a **calibração** (à mão, no `calibrar_campo.html` — regra
C1 dele) · o **ground-truth** (no `anotador_rallies.html` — **e contar TODOS os pontos**).
**O que o Claude faz:** a bola (BlurBall) e os jogadores (YOLO), no Colab/Kaggle.

---

## As 3 lições do dia (custaram caro — não repetir)

1. 🚨 **DESCONFIAR DO GROUND-TRUTH.** O "falso" dos 289s **era um ponto a sério**. A precisão andou
   o dia a castigar-me por **acertar**. Um falso positivo **bem-comportado** (com cruzamentos,
   pancadas, duração normal) é **verdade que falta ao GT**. Mostrar o clip ao Vasco **antes** de o
   combater.
2. 🕳️ **UM MAPA FEITO A PARTIR DO CÓDIGO SÓ VÊ O QUE SOBREVIVEU.** A **S12** e a **S8** estavam
   marcadas ✅ e **não corriam**. A S12 estava lá **com o nome certo a fazer outra coisa** — pior
   que estar desligada, porque ninguém a vai procurar. **Ler o código, não o mapa.**
3. 🧪 **TESTAR, NÃO RACIOCINAR.** Testei **1** das 9 regras perdidas e descartei as outras 8 com um
   raciocínio bonito ("tudo precisa de profundidade"). O Vasco perguntou *"nenhuma ajudava
   portanto?"* — e a que eu ia deitar fora (a **pausa**) foi a que resolveu o ponto 1.

> **Faixa fina = observável. Área grande = ambígua.**
> A rede (35 px) funciona; o vidro (meio ecrã) não. Serve para prever se uma ideia tem hipótese
> **antes** de a testar.
