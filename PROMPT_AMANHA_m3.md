# ▶️ PROMPT — AMANHÃ: continuar o projeto (o M3 arrancou)
### *(cola tudo o que está entre as linhas `=====` numa conversa NOVA do Cowork)*

=====

📖 **LÊ O `FECHO_13JUL.md` PRIMEIRO** — tem o dia todo, as regras que entraram, e a doença curada.

És o **centro de decisões** do PadelPro Vision.

**Lê primeiro, por esta ordem:**
1. a tua memória — começa em **`project_s23_quique_servico`** (é o estado ATUAL)
2. 📍 **A FONTE ÚNICA DAS REGRAS: `padelpro-vision/REGRAS_DO_VASCO.md`** — **117 regras.**
   ⛔ **NÃO leias o `REGRAS_DO_VASCO.md` da RAIZ nem o de `docs/` — são PONTEIROS MORTOS.**
   *(13 jul: havia **DUAS fontes vivas a divergir**. A **S23** existia numa e **não na outra**.
   Quem lesse a errada concluía que ela não existia — e ia **implementá-la outra vez, por cima da
   que já corre**. É a doença da S12, **ao nível do FICHEIRO**. Fundidas: 0 perdidas.)*
   🔑 **"RESSALTO" = "QUIQUE" = "BOLA NO CHÃO"** — se procurares só por *"ressalto"* encontras a
   **S9/S14/S36** (bloqueadas) e concluis que **não funciona**. A que **funciona** chama-se
   **"quique"** (**S23**). **Procura pelos três nomes.**
3. **`HANDOFF_14JUL.md`** — o contexto completo
4. Se o 2.º vídeo já correu, o resultado dele **manda em tudo o que está aqui.** Pergunta.

---

# 🛑 COMO TRABALHAR — NÃO NEGOCIÁVEL

## 1. ⛔ **NÃO AVANÇAS PARA NADA SEM PERGUNTAR.**
**Confirma SEMPRE antes de avançar.** Uma coisa de cada vez. Propõe → espera → só depois faz.
Não encadeies cinco passos porque "faz sentido". **O Vasco decide o passo seguinte, não tu.**

## 2. ⛔ **NÃO INVENTAS ATALHOS.**
Nenhum número mágico. Todos os valores saem do `calibracao_campo.json` ou são **frações do
meio-campo local**. Se usares um atalho, **declara-o na MESMA mensagem em que dás o número.**
*(Lei **D2** do Vasco, escrita há um mês: "se não consegues ancorar num evento visual claro, OMITE.")*

## 3. 🔄 **REVÊ AS REGRAS PARA NÃO ADORMECEREM.**
Uma regra que **não corre** não é testada; se não é testada, não aparece nos números; e o que não
aparece nos números **esquece-se**. Já aconteceu com a **S12**, com a **S8** e com a **PAUSA**.
⇒ **Corre a `ablacao.py` sempre.** Se uma regra vale `+0.0`: ou ficou **redundante** — ou **não corre**.

## 4. 🎬 **VÍDEO ANTES DE MÉTRICAS.** Ele encontrou **todos** os bugs a olhar. **Nenhum estava nos números.**

## 5. 🧪 **TESTAR, NÃO RACIOCINAR.** Nunca descartes uma regra dele com um raciocínio bonito. **Mede.**

## 6. 🚨 **DESCONFIA DO GROUND-TRUTH.** Um falso **bem-comportado** é **verdade que falta ao GT**.
**Mostra o clip ANTES de o combater.**

## 7. 🕳️ **LÊ O CÓDIGO, NÃO O MAPA.**

## 8. ⚖️ **AS REGRAS DO VASCO SÃO LEIS. OS TEUS NÚMEROS SÃO AJUSTES.** Nunca com o mesmo estatuto.
**As definições do jogo (ponto, serviço, tempo útil) PARAM E PERGUNTAM — são dele.**

## 9. 👤 **O Vasco NÃO é developer.** Passo a passo.

## 🎯 DIRETRIZ DE PRODUTO (manda em tudo)
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**
> **E o tempo útil é para VER o ponto**, não para estatística.

---

# 🔁 AS 3 RELEITURAS — **antes de escreveres uma linha de código**

**Ordem do Vasco.** É a cura da doença que já custou a **S12**, a **S8** e a **PAUSA** — regras
marcadas ✅ que **não corriam**, ou que **faziam outra coisa**.

### 📖 1.ª RELEITURA — verbal
Lê o **`padelpro-vision/REGRAS_DO_VASCO.md`** inteiro (**a FONTE ÚNICA — 117 regras**). **Escreve-me a lista completa** — todas as regras
(B, J, S, C, D), pelo nome, uma linha cada. **Esqueceste-te de alguma?** Se a lista for mais curta
que o ficheiro, **volta atrás**.

### 📖 2.ª RELEITURA — verbal
Lê **outra vez**. Classifica cada uma em três montes:
- ✅ **A CORRER** (no pipeline, e a ablação mede-a)
- 🔴 **POR IMPLEMENTAR** (boa, ainda não entrou)
- ⛔ **VIA FECHADA** (**medida** e falhada — diz **porquê**, em números)

**Esqueceste-te de alguma?** *(Foi assim que a **PAUSA** se perdeu: escrita nos prompts há um mês,
nunca implementada, ninguém deu por isso. Quando entrou, valeu **+1,8 de precisão**.)*

### 🕳️ 3.ª RELEITURA — **CONTRA O CÓDIGO** *(a que interessa)*
Pega em **cada** regra que classificaste como ✅ e **vai verificar no código**:
```bash
grep -n "S23\|S17\|S16\|S15\|S13\|S12\|PAUSA\|PAN_TEM_JOGADOR\|B8\|B6" gerar_tempo_util.py
python3 ablacao.py       # 🔑 uma regra que vale +0.0: ou não FAZ nada, ou não CORRE
```
Três perguntas por regra:
1. **Existe** a função?
2. **É CHAMADA** — com **todos os argumentos**?
   *(A **S23** quase se perdeu assim: o `teste_regressao.py` e o `ablacao.py` chamavam o `rallies()`
   **sem os quiques**. A regra estava lá e **não corria dentro do teste**.)*
3. **Faz o que a regra do Vasco diz** — ou só tem o **nome** certo?
   *(A **S12** estava ✅, **com o nome certo**, e **fazia outra coisa**. Pior que estar desligada —
   porque ninguém a vai procurar.)*

**Se as três releituras não baterem certo, PÁRA E DIZ-ME.** Não avances.

> 🔑 **PORQUE SÃO TRÊS, E NÃO UMA:**
> a **1.ª** apanha o que **esqueceste** · a **2.ª** apanha o que **classificaste mal** ·
> a **3.ª** apanha o que **mentiu** — a regra que está no mapa, com o nome certo, e **não corre**.
> **As duas primeiras são memória. A terceira é PROVA.** Nenhuma substitui as outras.

## ⚖️ E A QUARTA CONFIRMAÇÃO, QUE VALE PELAS TRÊS:
# **MEDIR ANTES DE CITAR.**
**Nunca declares uma regra do Vasco morta a partir de um número que não verificaste.**
🚨 Já custou **DUAS** regras dele (a **S2** e a **S30**) — mortas com um **"21,8%"** que era um
**artefacto do `max_det=4`**, não da câmara. Ver abaixo.

---

# 📍 O ESTADO — 13 jul 2026, fim do dia

```
RECALL 96,8%  ·  PRECISÃO 95,4%  ·  F1 96,1  ·  13/13 serviços  ·  fim_dentro 0  🔒
```

```bash
cd padelpro-vision
python3 teste_regressao.py    # 🔒 se falhar, a ALTERAÇÃO está errada. NUNCA o teste.
python3 gerar_tempo_util.py --video
python3 ablacao.py
python3 ressalto.py           # o detetor de quique
```
**Guardar:** duplo-clique no **`GUARDAR_TUDO.command`**.
⚠️ A **mensagem** do commit ainda diz `96,3/95,9` (está fixa dentro do script) — **corrigir**.

## ✅ O que entrou (regras do Vasco)
| | |
|---|---|
| **S23 — O QUIQUE DO SERVIÇO** 🔴 | *"matar o lixo pela **bola na mão do NÃO SERVIDOR — antes de bater no chão**"* · *"mesmo que tenha kick, **só o ÚLTIMO** antes da mudança de campo conta"*. **A LEI: não há ponto sem serviço, e não há serviço sem a bola bater no chão.** **13/13 pontos têm quique fundo · o lixo tem ZERO.** Vale **+3,5 precisão**. |
| **B15 — a FAIXA CEGA** | `MIN_PROF` **0,35 → 0,15**. O volley à rede morria na faixa cega; o código via **52%** das travessias. |

🔑 **AS DUAS ANDAM JUNTAS.** ⚠️ **É a 1.ª vez que o RESSALTO entra no pipeline.** Se algo correr mal
no vídeo novo, **desligar isto PRIMEIRO** (`--sem S23_QUIQUE_SERV` + repor `MIN_PROF=0.35`).

---

# 🎯 A TAREFA: **O M3 — DETEÇÃO DE SERVIÇO**

## 🔓 Deixou de estar bloqueado. **Passou a ser trabalho.**

O M3 estava travado por não haver **por onde começar**. **Agora há.** Medido (13 jul):

```
varrer TODOS os 251 quiques do vídeo, SEM saber onde estão os pontos:
   quiques FUNDOS (na linha de serviço) ......... 174
   ... com uma TRAVESSIA nos 3 s a seguir ........ 68
   ... agrupados (só o ÚLTIMO conta — regra do Vasco)   37   ← CANDIDATOS A SERVIÇO

   >>> RECALL:    13/13 = 100%   ✅✅
   >>> PRECISÃO:  35%   (24 falsos)
```

**Encontra os 13 serviços. Todos. Sem saber onde estão os pontos.**

É **exactamente** a forma que a diretriz manda ter: **recall 100%, e o lixo limpa-se depois.**
✅ **O script EXISTE e CORRE: `python3 m3_candidatos.py`.**
⚠️ **NÃO o reescrevas de memória.** *(Este prompt já dizia "recria-o se não existir" — e é assim que
as coisas se duplicam e divergem. **Corre-o primeiro. Só o que se corre é que conta.**)*

## ➡️ O trabalho: **matar os 24 falsos.** E há regras dele à espera há semanas.

⚖️ **LEI DE DESENHO DO VASCO: as regras PONTUAM, NÃO VETAM.** Há sempre uma exceção legítima
(ponto de ouro, tie-break, let). Escolhe-se a **sequência globalmente mais consistente**.
Um falso paga caro em vários sítios; uma exceção paga num só, e passa.

| regra dele | o que faz | estado |
|---|---|---|
| **S3** — formação lida **só nos 2 de cima** | *um na rede + um atrás ⇒ eles SERVEM · os dois atrás ⇒ eles RECEBEM*. A formação de uma dupla **deduz** a da outra. | ✅ existe em `padelpro/modules/servico.py` — **NÃO CORRE** |
| **S4** — quadrado de serviço **cruzado** | o ressalto do serviço cai na **diagonal**. **0 falsos** quando testada. | 🔴 precisa do ressalto — **e agora temos** |
| **S10** — **duplo ressalto** | o serviço é a **única** jogada que ressalta **obrigatoriamente dos dois lados**. Um deles está **sempre em cima** (o lado que a câmara vê). | 🔴 por implementar |
| **S6** — **alternância de lado** | ⚠️ **NÃO é lei** (ponto de ouro: quem recebe escolhe). **Pontua.** | 🔴 por implementar |
| **S20** — a **pausa aprendida** | dois serviços não podem estar a 2 s um do outro | ✅ já corre — **usar como pontuação no M3** |
| **J-cascata** | os jogadores em **formação de serviço** — parados, separados | ⚠️ **NÃO CORRE** (ver abaixo) |

## 🚨 DUAS REGRAS DO VASCO FORAM DADAS COMO MORTAS — **e não estavam.** *(resolvido, 13 jul)*

Eu declarei-as *"bloqueadas pela câmara"* citando **"só 21,8% dos frames têm os 4 jogadores"**.

# **O 21,8% ERA UM ARTEFACTO DO `max_det=4`. NÃO ERA A CÂMARA.**

```
max_det=4  + regras J .....  21,4% dos frames com os 4     ← o "21,8" histórico. VEIO DAQUI.
SEM CAP    + regras J .....  38,8% dos frames com os 4     ← quase o DOBRO
```
O cap **já tinha deitado fora jogadores reais** (para meter espectadores no top-4) **antes** de as
regras J poderem correr. **As regras J não conseguem recuperar quem o cap apagou.**

### As duas regras injustiçadas — **REABRIR**
| | a regra | o que eu disse (errado) |
|---|---|---|
| **S2** | **Formação de serviço** — *parceiro na rede + adversário cruzado atrás*. **0 falsos** quando testada. | *"cega — exige ver os 4"* ⇒ substituí-a pela **S3** (só os 2 de cima). ⚠️ **E a S3 TAMBÉM NÃO CORRE** — vive em `padelpro/modules/servico.py`. |
| **S30** | **Inatividade dos jogadores confirma o fim** — *"4 jogadores visíveis e ~3 s parados → confirma o fim sem esperar"* (v9, regra 5) | ⛔ *"bloqueada: só 21,8% têm os 4"* |

### 🔑 E O ERRO MAIOR NÃO É O NÚMERO — **É A ESTATÍSTICA**
Usei uma percentagem sobre **TODOS os frames**. **As regras não precisam disso:**
- a **S2** só precisa dos 4 **no momento do SERVIÇO** — são **13 instantes**, não 8741 frames
- a **S30** só precisa deles **no FIM do ponto** — outros 13

**A pergunta certa não é "em quantos frames se veem os 4?" — é "veem-se os 4 NOS 13 MOMENTOS QUE
INTERESSAM?"** E o início do ponto é **o frame mais limpo do jogo**: jogadores **separados, parados,
em formação**. O M1 dá **13/13 serviços** ⇒ **sabemos exactamente onde olhar.**

👉 **MEDIR ISSO PRIMEIRO.** É barato, e pode devolver duas regras.
**⚖️ MEDIR ANTES DE CITAR. Nunca declarar uma regra do Vasco morta a partir de um número que não
verificaste.**

### ⚠️ MAS ATENÇÃO — o `.pkl` SEM CAP **CRU** NÃO SE LIGA AO PIPELINE. **Medido:**
```
pkl                      boxes/frame   segm   RECALL   PRECISÃO
  Colab (max_det=4)            3,37     13     96,8      95,4
  Mac SEM CAP, CRU            13,95     14     93,2      94,8   💀
```
**Porquê:** com o público todo dentro, a **S17** morre — a regra diz *"vira na rede **LONGE de uma
box** ⇒ foi a rede"*, mas **nunca há nada longe de uma box**. A regra deixa de disparar, **em silêncio**.
⇒ **Só entra o SEM CAP + as REGRAS J aplicadas** (J1 → J7 → J4 → J5). Esse `.pkl` tem de ser
**produzido e TESTADO contra o pipeline** antes de se ligar. **É uma alteração de pipeline ⇒ decisão
do Vasco.**

---

# 🔴 A CASCATA DOS JOGADORES — **a ORDEM importa** *(e NENHUMA destas corre)*

> O Vasco, ao ver as boxes do João: *"há coisas a ajustar mas **a maior parte das vezes estão
> certas**."* **Não falta um detetor melhor — faltam as REGRAS a correr por cima delas.**

1. 🦶 **os PÉS não saem do POLÍGONO** — ⚠️ o polígono **INCLUI OS ESPAÇOS LATERAIS** (o **jogo
   exterior** é jogo **legal**! Foi por isto que se matou a regra *"bola sai de campo = fim"*)
2. 👥 **nunca mais de 2. É sempre 2 CONTRA 2** (por lado) — verdade do **jogo**, não limiar
3. 👀 **os 2 DE CIMA estão SEMPRE visíveis** — se só vês um, o outro **está lá**. Vai procurá-lo.
4. 🔗 **CONTINUIDADE** — *"se não os vês, temos de **PERCEBER PORQUÊ**"*. ⚠️ **NÃO é um filtro.
   PREENCHE.** A ausência **não é buraco — é pergunta.**
5. 🛡️ **de baixo INVISÍVEIS ⇒ estão em DEFESA** — 🔑 **A AUSÊNCIA É O SINAL.** A câmara corta-os
   **quando recuam** ⇒ não os ver **É** a informação de que recuaram.

🚨 **1 e 2 LIMPAM. 3, 4 e 5 ACRESCENTAM. NENHUMA descarta o frame.**

### 🚨 O `max_det=4` é uma MINA — **com prova (13 jul)**
```
MPS vs CPU ............ deteções BIT-A-BIT idênticas (o detetor é determinístico)
boxes DENTRO do campo . IoU mediano 0,906  ⇒ os jogadores estão BEM LOCALIZADOS
em 98% dos frames ..... há MAIS de 4 pessoas de alta confiança (mediana: 8)
```
**O cap escolhe 4 entre ~8 por ordem de confiança.** Se um espectador ganhar a um jogador, **o
jogador é deitado fora.** ⇒ **o padrão-ouro do Colab é ele próprio um artefacto instável.**

## 🔴🔴 A ORDENAÇÃO ESTÁ ERRADA — **e o Vasco deu o critério certo (13 jul)**

> ### *"os mais confiáveis são os que têm os **PÉS DENTRO DO POLÍGONO**."*

**O `max_det=4` ordena por CONFIANÇA DO YOLO. Esse é o critério ERRADO.**
Um espectador nítido, bem iluminado, de corpo inteiro na bancada tem **mais confiança** que um
jogador meio cortado pela borda — e **ganha-lhe o lugar**.

**O critério certo é a GEOMETRIA, não a confiança:**
```
1º  os PÉS dentro do POLÍGONO  ->  é um JOGADOR.        (J1 — a regra do Vasco)
2º  só DEPOIS, entre esses, a confiança desempata.
```
⚠️ **O polígono INCLUI OS ESPAÇOS LATERAIS** — o **jogo exterior é jogo legal**.
⚠️ E a **J7**: se a box **toca a borda de baixo**, aceita-se **sem testar os pés** (a câmara não vê
o fundo perto — não sabemos *onde* está, sabemos que está **EM BAIXO**, e chega).

🔑 **Correr SEM `max_det`.** Detetar **generosamente**, e **ordenar/limpar pelas regras do Vasco**:
**J1** (pés no polígono) → **J7** (os de baixo cortados) → **J4** (2 por lado) → **J5** (continuidade).
⚠️ **NUNCA improvisar um detetor de jogadores.**

---

# 🎨 DEPOIS DO M3: A COR + A SALVAGUARDA *(andam JUNTAS)*
- **J6+** *(Vasco)*: *"detetas uma box consistente nos primeiros tempos, detetas a **cor da roupa**,
  passas **só a seguir essa cor**."* **O detetor só ARRANCA; a identidade é a COR** — e a cor
  **sobrevive à box cortada**, que é onde o detetor falha.
- **J10** *(dos prompts, perdida)*: *"a camisola pode mudar numa pausa, **mas não de todos em
  simultâneo**."* ⚠️ **É A SALVAGUARDA.** Sem ela, a cor **salta de pessoa para pessoa**.
- **J11**: **o LADO não muda DENTRO do rally.** Invariante forte, nunca usado.
- **🎉 J9 DESBLOQUEADA:** *"aprender as cores no início de cada ponto"* — o M1 dá **13/13 serviços**
  ⇒ sabemos onde estão os **13 frames mais limpos do jogo** (jogadores separados, parados, em formação).

---

# ⛔ VIAS FECHADAS — **medidas**. NÃO REPETIR.

| | porquê |
|---|---|
| **"virou longe de box ⇒ acabou"** (S17 generalizada) | **74 fins a meio de pontos · recall 40.** É a **PAREDE** e o **CHÃO**. |
| **ler a travessia pelo TOPO da rede** | **certo, mas quase nulo** — as duas linhas estão a 35 px, **ambas dentro da faixa cega**. |
| **S21 — alternância das travessias** | **redundante**: **ZERO grupos de intervalo** (a S15 e o `MIN_PROF` já limpam a montante). E o **ACE** é um ponto real com **UMA** travessia ⇒ como veto, mata pontos. |
| **ampliar o `MIN_PROF` SEM a S23** | traz **1 segmento falso** e nada o mata |
| **S8** | 98,9 / **47,1** — sem serviço, as pancadas do intervalo esticam tudo. **Reabrir quando o M3 estiver feito.** |
| **S14 — duplo quique = fim** | **49 falsos a meio de pontos.** *(O quique só é fiável **no serviço**: sítio fixo, instante fixo, bola lenta e destapada.)* |
| **S18_MAO_PASSE** | vetava **10 dos 12** pontos |
| **S19_2_TOQUES** | a **PAREDE** confunde-se com a raquete |
| **VIDRO DO FUNDO** | é o **CÉU** — e **não se resolve desenhando** |
| **BOLA SAI DE CAMPO** | ⛔ **o Vasco matou-a:** há **jogo exterior** |
| **JOGADOR TOCA NA REDE** | a box dos **pés** não vê a **raquete**. Precisa de pose. |
| **régua local aplicada à BOLA** | **A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96 → **32** |
| **fine-tune do YOLO da bola** | `best_v2` ficou pior |

> ### 🔑 **PORQUE É QUE O RESSALTO FUNCIONOU AGORA, DEPOIS DE FALHAR TANTAS VEZES**
> **Não se afinou NADA. O detetor é o mesmo. Mudou a PERGUNTA.**
> ❌ antes: *"há dois quiques ⇒ o ponto acabou?"* — **em qualquer sítio, a qualquer hora** ⇒ 49 falsos
> ✅ agora: *"há um quique **FUNDO**, na **linha de serviço**, nos **3 s antes** da 1.ª travessia?"*
>
> **FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA.**
> Serve para prever se uma ideia tem hipótese **ANTES** de a testar.

## 🔊 **PEDIDO DE CAPTURA — mais importante que o ângulo da câmara: GRAVAR COM ÁUDIO.**
O som do **quique**, o da **parede** e o da **raquete** são **três sons diferentes** — e são as três
coisas que a imagem **não distingue**. **O áudio não precisa de profundidade.**

# 🏃 **E SÓ O QUE SE CORRE É QUE CONTA.**
Nunca dizer "está feito" a partir de uma lista de ficheiros. **Correr. Ver o vídeo. Medir.**

---

**Começa pelas 3 RELEITURAS. Depois corre o `teste_regressao.py`. E só depois fala comigo —
não avances para nada sem me perguntares.**

---

# ⚡ O PROBLEMA DO CUSTO — **medido, e é sério**

```
Parada4     960×540   ·  8.741 frames  ·  4:52  ·   89 MB
Barbosa    1280×720   · 16.138 frames  ·  8:58  ·  544 MB
                        ↑ 1,78× píxeis   ↑ 1,85× frames  =  3,3× o trabalho

jogadores (mps): 12,5 min no Parada4  ⇒  ~40 min no Barbosa
blurball/run_BarbosaMeireles/ .... 26 GB   ← 16.138 PNGs, um por frame
o que o pipeline USA ............   522 KB  (traj.csv)
```

## **26 GB de lixo intermédio para 500 KB de sinal.**
**Não é a GPU que é lenta — é o disco a escrever 16 mil PNGs sem compressão.**
9 min de vídeo ⇒ ~50 min de máquina. **Uma hora de padel ⇒ ~5,5 horas. NÃO ESCALA.**

### As alavancas — **medir, não adivinhar**
| # | | ganho | risco |
|---|---|---|---|
| **1** | **APAGAR os PNGs no fim** (o `traj.csv` é tudo) | **26 GB → 0** | **nenhum** |
| **2** | **PNG → JPEG**, ou ler o vídeo direto | ~10× menos disco **e I/O** | mínimo |
| **3** | **Baixar para 960×540** | **1,78× menos trabalho** | ⚠️ a bola fica mais pequena |
| **4** | `step` · `fp16` · `batch` | por medir | por medir |
| **5** | **GPU na nuvem** — preços | por estudar | ⚠️ **NÃO INVENTAR PREÇOS. PROCURAR.** |

### 🔑 O TESTE ELEGANTE DA #3 — **e é de graça**
**Não adivinhes se baixar a resolução estraga a bola. TESTA NO PARADA4** — é o único vídeo com **RÉGUA**
(ground-truth, 13 rallies, 96,8/95,4).
```
baixa o Parada4 para 640×360 (e 480×270) → corre o BlurBall → corre o teste_regressao
   aguenta o recall?  ⇒ ganhaste 2-4× de velocidade DE GRAÇA, e sabes o preço exacto
   cai?               ⇒ sabes quanto custa cada píxel, e paras onde deves
```

---

# 🚨 UMA CANETA DE CADA VEZ

Hoje **duas conversas escreveram no `gerar_tempo_util.py` ao mesmo tempo.** Deu certo **por sorte**.
Da próxima, **uma apaga o trabalho da outra e o `teste_regressao` continua VERDE** — porque as duas
alterações eram, isoladamente, válidas. **O git não protege disto: a última a gravar ganha, em silêncio.**

> **Só UMA conversa toca no `gerar_tempo_util.py` de cada vez.**
> As outras **leem, medem, criam ficheiros novos.** **Nunca editam.**

---

# 🛡️ E ANTES DE TUDO: **CORRE O GUARDA**
```bash
python3 verificar_fonte.py      # tem de dar ✅ FONTE LIMPA (exit 0)
```
Ele faz **automaticamente** a 3.ª releitura (bate as regras contra o código). **Se der vermelho, PÁRA.**


=====
