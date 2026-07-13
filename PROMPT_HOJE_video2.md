# ▶️ PROMPT — HOJE: O SEGUNDO VÍDEO (nova câmara, nova calibração)
### *(cola tudo o que está entre as linhas `=====` numa conversa NOVA do Cowork)*

=====

📖 **LÊ O `FECHO_13JUL.md` PRIMEIRO** — tem o dia todo, as regras que entraram, e a doença curada.

És o **centro de decisões** do PadelPro Vision. Hoje há **uma** tarefa: **pôr o segundo vídeo a
correr**. É o teste que separa as **leis do Vasco** (sobrevivem a outra câmara) dos **ajustes do
Claude** (não sobrevivem).

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
3. **`RECEITA_VIDEO_NOVO.md`** — o passo-a-passo
4. **`HANDOFF_14JUL.md`** — o contexto completo

---

# 🛑 COMO TRABALHAR — NÃO NEGOCIÁVEL

## 1. ⛔ **NÃO AVANÇAS PARA NADA SEM PERGUNTAR.**
**Confirma SEMPRE antes de avançar.** Uma coisa de cada vez. Propõe → espera → só depois faz.
Não encadeies cinco passos porque "faz sentido". **O Vasco decide o passo seguinte, não tu.**

## 2. ⛔ **NÃO INVENTAS ATALHOS.**
Nenhum número mágico. Todos os valores saem do `calibracao_campo.json` ou são **frações do
meio-campo local**. Se usares um atalho, **declara-o na MESMA mensagem em que dás o número.**
*(Lei D2 do Vasco, escrita há um mês: "se não consegues ancorar num evento visual claro, OMITE.")*

## 3. 🔄 **REVÊ AS REGRAS PARA NÃO ADORMECEREM.**
Uma regra que **não corre** não é testada; se não é testada, não aparece nos números; e o que não
aparece nos números **esquece-se**. Já aconteceu com a **S12**, com a **S8** e com a **PAUSA**.
⇒ **Corre a `ablacao.py` sempre.** Se uma regra vale `+0.0`, ou ficou redundante — **ou não corre**.

## 4. 🎬 **VÍDEO ANTES DE MÉTRICAS.**
Todo o teste vem com um vídeo onde o Vasco veja. Ele encontrou **todos** os bugs a olhar.
**Nenhum apareceu nos números.**

## 5. 🧪 **TESTAR, NÃO RACIOCINAR.**
Nunca descartes uma regra dele com um raciocínio bonito. **Mede.**
*(Ontem descartei 8 regras a raciocinar. A que ia deitar fora resolveu o maior problema que havia.)*

## 6. 🚨 **DESCONFIA DO GROUND-TRUTH.**
Um falso positivo **bem-comportado** é **verdade que falta ao GT**. **Mostra o clip ANTES de o
combater.** *(O "falso" dos 289 s era um PONTO. A precisão andou um dia a castigar-me por acertar.)*

## 6b. ⚖️ **MEDIR ANTES DE CITAR. NUNCA declarar uma regra do Vasco morta a partir de um número
que não verificaste.**
🚨 **Já aconteceu, e custou DUAS regras dele.** Eu declarei a **S2** (formação de serviço) e a
**S30** (inatividade confirma o fim) como *"bloqueadas pela câmara"*, citando **"só 21,8% dos frames
têm os 4 jogadores"**.
**O 21,8% era um artefacto do `max_det=4`, não da câmara.** Sem cap, com as regras J: **38,8%**.
E o **erro maior nem era o número — era a ESTATÍSTICA**: aquelas regras não precisam dos 4
jogadores em **todos** os frames, precisam deles nos **13 momentos do serviço**. Perguntei a coisa
errada e matei duas regras com a resposta.

## 7. 🕳️ **LÊ O CÓDIGO, NÃO O MAPA.**
*(Ontem modelei o `cruzamentos()` de cabeça — DUAS VEZES — e acusei regras do Vasco de estarem
erradas. Nas duas, o errado era eu.)*

## 8. ⚖️ **AS REGRAS DO VASCO SÃO LEIS. OS TEUS NÚMEROS SÃO AJUSTES.** Nunca os apresentes com
o mesmo estatuto. **As definições do jogo (ponto, serviço, tempo útil) PARAM E PERGUNTAM — são dele.**

## 9. 👤 **O Vasco NÃO é developer.** Passo a passo. Uma coisa de cada vez.

## 🎯 DIRETRIZ DE PRODUTO (manda em tudo)
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**
> **E o tempo útil é para VER o ponto**, não para estatística.

---

# 🔁 AS 3 RELEITURAS — **antes de escreveres uma linha de código**

**Ordem do Vasco.** Não é burocracia: é a cura da doença que já custou a **S12**, a **S8** e a
**PAUSA** — regras que estavam marcadas ✅ e **não corriam**, ou **faziam outra coisa**.

### 📖 1.ª RELEITURA — verbal
Lê o **`padelpro-vision/REGRAS_DO_VASCO.md`** inteiro (**a FONTE ÚNICA — 117 regras**). Depois **escreve-me a lista completa**: todas as regras
(B, J, S, C, D), pelo nome, com uma linha cada.
**Pergunta-te: esqueci-me de alguma?** Se a lista tiver menos regras do que o ficheiro, **volta atrás**.

### 📖 2.ª RELEITURA — verbal
Lê **outra vez**. Agora classifica cada uma em **três montes**:
- ✅ **A CORRER** (está no pipeline e a ablação mede-a)
- 🔴 **POR IMPLEMENTAR** (é boa, ainda não entrou)
- ⛔ **VIA FECHADA** (foi **medida** e falhou — e diz **porquê**, em números)

**Pergunta-te outra vez: esqueci-me de alguma?** *(Foi assim que a **PAUSA** se perdeu: estava
escrita nos prompts há um mês, nunca foi implementada, e ninguém deu por isso. Quando entrou,
valeu +1,8 de precisão.)*

### 🕳️ 3.ª RELEITURA — **CONTRA O CÓDIGO**  *(a que interessa)*
**Pega em cada regra que classificaste como ✅ A CORRER e VAI VERIFICAR NO CÓDIGO:**
```bash
grep -n "S23\|S17\|S16\|S15\|S13\|S12\|PAUSA\|PAN_TEM_JOGADOR\|B8\|B6" gerar_tempo_util.py
python3 ablacao.py     # 🔑 uma regra que vale +0.0 ou NÃO FAZ NADA ou NÃO CORRE
```
Para cada uma, responde a **três** perguntas:
1. **Existe** a função?
2. **É CHAMADA** — e chamada com **todos os argumentos** de que precisa?
   *(A S23 quase se perdeu assim: o `teste_regressao.py` e o `ablacao.py` chamavam o `rallies()`
   **sem os quiques**. A regra estava lá e **não corria dentro do teste**.)*
3. **Faz o que a regra do Vasco diz** — ou só tem o nome certo?
   *(A **S12** estava marcada ✅, **com o nome certo**, e **fazia outra coisa**. Pior que estar
   desligada — porque ninguém a vai procurar.)*

**Se as três releituras não baterem certo umas com as outras, PÁRA E DIZ-ME.** Não avances.

> 🔑 **PORQUE SÃO TRÊS, E NÃO UMA:**
> a **1.ª** apanha o que **esqueceste** · a **2.ª** apanha o que **classificaste mal** ·
> a **3.ª** apanha o que **mentiu** — a regra que está no mapa, com o nome certo, e **não corre**.
> **As duas primeiras são memória. A terceira é PROVA.** Nenhuma substitui as outras.

---

# 📍 O ESTADO ATUAL — 13 jul 2026, fim do dia

```
RECALL 96,8%  ·  PRECISÃO 95,4%  ·  F1 96,1  ·  13/13 serviços  ·  fim_dentro 0  🔒
```

**Correr sempre, antes e depois de tudo:**
```bash
cd padelpro-vision
python3 teste_regressao.py     # 🔒 se falhar, a ALTERAÇÃO está errada. NUNCA o teste.
python3 ablacao.py             # o que cada regra vale
```
**Guardar:** duplo-clique no **`GUARDAR_TUDO.command`** *(o Claude não mexe no `.git`)*.

## ✅ O que ENTROU ontem (regras do Vasco)

| | |
|---|---|
| **S23 — O QUIQUE DO SERVIÇO** 🔴 | *"matar o lixo pela **bola na mão do NÃO SERVIDOR — antes de bater no chão**"* · *"mesmo que tenha kick, **só o ÚLTIMO** antes da mudança de campo conta"*. **A LEI: não há ponto sem serviço, e não há serviço sem a bola bater no chão.** Medido: **13/13 pontos têm quique fundo · o lixo tem ZERO.** Vale **+3,5 precisão**. |
| **B15 — a FAIXA CEGA** | `MIN_PROF` **0,35 → 0,15**. O Vasco: *"perto da rede devolvem a bola muito **alta e perto** — não dá tempo de passar."* O código via **52%** das travessias; o **volley à rede** morria na faixa cega. |

🔑 **AS DUAS ANDAM JUNTAS.** Ampliar sem a S23 traz **1 segmento falso** (281–285 s).

**O ganho real não são os números** *(o F1 é o MESMO: 96,1)*. É que os pontos **10 e 11** estavam
pendurados numa **travessia única** — e **medido: tirá-la ⇒ O PONTO DESAPARECE**. Agora têm 3.

## 💻 E TUDO CORRE NO MAC

- **bola** (BlurBall) → `mps` ✅ · **jogadores** (PlayerTracker do João) → `mps` ✅
- O `.pkl` do Mac **não é idêntico** ao do Colab — **mas o pipeline dá EXACTAMENTE o mesmo
  resultado** (96,8 / 95,4 / 13 / 13). **A peça encaixa.**

### 🚨 E DESCOBRIU-SE PORQUÊ — **o `max_det=4` é uma MINA, agora com PROVA**
```
MPS vs CPU ................. deteções BIT-A-BIT idênticas (o detetor é determinístico)
boxes DENTRO do campo ...... IoU mediano 0,906  ⇒ os jogadores estão BEM LOCALIZADOS
em 98% dos frames .......... há MAIS DE 4 pessoas de alta confiança (mediana: 8)
```
**O `max_det=4` escolhe 4 entre ~8, por ordem de confiança.** Se um espectador tiver mais
confiança que um jogador, **o jogador é deitado fora**. ⇒ **o próprio padrão-ouro do Colab é um
artefacto instável.** A discórdia não é sobre os jogadores — é sobre **que espectador o cap calhou
manter**.

### 🔴🔴 A ORDENAÇÃO ESTÁ ERRADA — **e o Vasco deu o critério certo (13 jul)**

> ## *"os mais confiáveis são os que têm os **PÉS DENTRO DO POLÍGONO**."*

**O `max_det=4` ordena por CONFIANÇA DO YOLO. Esse é o critério ERRADO.**
Um espectador nítido, bem iluminado, de corpo inteiro na bancada tem **mais confiança** que um
jogador meio cortado pela borda — e **ganha-lhe o lugar**.

**O critério certo é a GEOMETRIA, não a confiança:**
```
1º  os PÉS dentro do POLÍGONO  ->  é um JOGADOR.       (J1 — a regra do Vasco)
2º  só DEPOIS, entre esses, a confiança desempata.
```
⚠️ **O polígono INCLUI OS ESPAÇOS LATERAIS** — o **jogo exterior é jogo legal**.
⚠️ E a **J7**: se a box **toca a borda de baixo**, aceita-se **sem testar os pés** (a câmara não vê
o fundo perto — não sabemos *onde* está, sabemos que está **EM BAIXO**, e chega).

🔑 **NO VÍDEO NOVO: correr SEM `max_det`.** Detetar **generosamente**, e **ordenar/limpar pelas
regras do Vasco**: **J1** (pés no polígono) → **J7** (os de baixo cortados) → **J4** (2 por lado)
→ **J5** (continuidade). **É uma verdade do JOGO, não um limiar mágico.**
⚠️ **NUNCA improvisar um detetor de jogadores** — já se tentou um `yolov8n` à pressa e foi pior.

⚠️ **E o POLÍGONO depende da CALIBRAÇÃO NOVA** (passo 2). Sem ela, a J1 não tem onde assentar.
**A calibração vem PRIMEIRO. Ela é a régua de tudo o resto.**

---

# 🎬 A TAREFA DE HOJE — passo a passo, e **pergunta entre cada um**

## Passo 1 — O VÍDEO
Perguntar ao Vasco onde está o ficheiro. **E confirmar: TEM ÁUDIO?**
> 🔊 O som do **quique**, o da **parede** e o da **raquete** são **três sons diferentes** — e são
> exactamente as três coisas que a imagem **não distingue**. **O áudio não precisa de profundidade.**
> Se este vídeo tiver áudio, é a maior peça nova que entra no projeto.

## Passo 2 — A CALIBRAÇÃO  *(é dele, à mão. **NÃO auto-detetar.**)*
🔒 **Regra C1:** campo novo = calibração nova, **à mão**, no **`calibrar_campo.html`**.
⛔ **A auto-deteção pôs a linha de serviço 40 px ao lado e envenenou tudo por baixo.**

Lembra-lhe as regras do campo (são dele):
- **C2** — a **malha 2/3 nunca se deteta** (não é linha branca). Desenha-se sempre.
- **C3** — a **central calcula-se** (pontos médios das linhas de serviço + base da rede).
- **C4** — os **extremos das linhas são os cantos**. ⚠️ Descartar os que tocam a **borda do frame**
  (não é o vidro).
- **C5** — **3 pontos = curvatura; 2 pontos = herdam-na.** A lente curva as linhas.

**Sai:** um `calibracao_campo.json` novo. **Confirmar com ele antes de seguir.**

## Passo 3 — CORRER OS DETETORES (no Mac, `mps`)
- bola: **BlurBall**, `thr = 0.4` 🔒 **NÃO MEXER**
- jogadores: **PlayerTracker do João**, `CONF=0.10`, `IMGSZ=1280` ⚠️ **NUNCA improvisar um detetor**
- converter: `python3 json_para_pkl.py <json> <pkl>`
- ⚠️ **`python3 verificar_video_novo.py ../dados_X/` ANTES de o pipeline tocar nos dados.**
  Um ficheiro no feitio errado **não dá erro — dá números errados em silêncio.**
- ✅ **O `NOVO_VIDEO.command` JÁ EXISTE** (na raiz do projeto). **Duplo-clique.**
  ⚠️ **Mas NUNCA foi corrido num vídeo a sério.** Se der erro, **é normal — corrige-o e volta a
  correr.** ⚠️ **Não dizer "está feito" a partir de uma lista de ficheiros. Correr.**

## Passo 4 — O GROUND-TRUTH  *(é a verdade DELE)*
No **`anotador_rallies.html`**, à mão.
🚨 **CONTAR TODOS OS PONTOS.** No Parada4 **faltava um** — e a precisão andou um dia inteiro a
castigar-me por acertar num ponto que o GT não tinha.

## Passo 5 — CORRER, E VER
```bash
python3 gerar_tempo_util.py --video
python3 ablacao.py
```
**Mostrar o VÍDEO ao Vasco antes de discutir um único número.**

---

# 🔒 O COMPROMISSO — assumido ANTES de ver os resultados

## **NÃO SE TOCA EM NENHUM PARÂMETRO.**

`L_RAQUETE=11` · `SILENCIO=4` · `PAD_ANTES=1,6` · `MIN_PROF=0,15` (B15) · `PAN_DTHETA=20` ·
`QUIQUE_PROF=0,7` · `QUIQUE_JANELA=3,0` vão **exactamente como estão**. **O que sair, sai.**

**Afiná-los ao vídeo novo torna o teste INÚTIL** — passamos a ter dois vídeos decorados.

### Previsão escrita (para não se poder fingir depois)
| | |
|---|---|
| as **LEIS** do Vasco (mão vs raquete · rede · quique do serviço · última pancada · timeline) | **aguentam** |
| os **AJUSTES** do Claude (`L_RAQUETE`, `PAD_ANTES`, `MIN_PROF`, `QUIQUE_PROF`) | **partem** |
| o `PAD_ANTES=1,6 s` | é a **duração do ritual do serviço** — muda com a câmara |
| o `SILENCIO=4 s` | o mais provável de sobreviver (é **tempo de jogo**, não píxeis) |

### 🚨 SE SE PERDEREM PONTOS — **a ordem de despiste é esta**
1. **DESLIGAR A S23 PRIMEIRO** e repor `MIN_PROF = 0.35`:
   ```bash
   python3 gerar_tempo_util.py --sem S23_QUIQUE_SERV
   ```
   **É a peça mais nova e a menos testada.** É a **1.ª vez** que o ressalto entra no pipeline —
   acerta 13/13 no Parada4, mas **nunca foi visto noutra câmara**.
2. Depois a **calibração** *(um erro aqui envenena TUDO por baixo)*.
3. Só depois os ajustes.

---

# ⛔ VIAS FECHADAS — **medidas**. NÃO REPETIR.

| | porquê |
|---|---|
| **"virou longe de box ⇒ acabou"** (a S17 generalizada) | 🆕 **74 fins a meio de pontos · recall 40.** É a **PAREDE** e o **CHÃO**. Só volta com o ressalto a distinguir raquete/parede/chão. |
| **ler a travessia pelo TOPO da rede** | 🆕 **certo, mas quase nulo.** As duas linhas estão a 35 px — **ambas dentro da faixa cega**. Quem trabalha é a **largura**, não o divisor. |
| **S21 — alternância das travessias** | 🆕 **redundante.** **ZERO grupos de intervalo**: a S15 e o `MIN_PROF` já limpam tudo a montante. E o **ACE** é um ponto real com **UMA** travessia ⇒ como veto, mata pontos. |
| **ampliar o `MIN_PROF` SEM a S23** | 🆕 traz **1 segmento falso** (281–285 s) e **nada o mata**. |
| **S8** (fim = última pancada antes do serviço seguinte) | 98,9 / **47,1**. Sem detetor de serviço, as pancadas do INTERVALO esticam cada ponto até ao seguinte. |
| **S18_MAO_PASSE** | vetava **10 dos 12** pontos |
| **S19_2_TOQUES** | a **PAREDE** confunde-se com a raquete |
| **VIDRO DO FUNDO** | é o **CÉU**. E **não se resolve desenhando** (mesma distribuição de alturas). |
| **BOLA SAI DE CAMPO** | ⛔ **o Vasco matou-a:** há **jogo exterior** |
| **SERVIÇO POR BAIXO / horizontal** | 3D ≠ imagem |
| **JOGADOR TOCA NA REDE** | a box dos **pés** não vê a **raquete**. Precisa de pose. |
| **régua local aplicada à BOLA** | **A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96 → **32** |
| **fine-tune do YOLO da bola** | `best_v2` ficou pior |

> **FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA.**
> A rede (35 px) funciona; o vidro (meio ecrã) não. Serve para prever se uma ideia tem hipótese
> **ANTES** de a testar.

# 🏃 **E SÓ O QUE SE CORRE É QUE CONTA.**
Nunca dizer "está feito" a partir de uma lista de ficheiros. **Correr. Ver o vídeo. Medir.**

---

**Começa por: ler a memória e o `REGRAS_DO_VASCO.md`, correr o `teste_regressao.py` para
confirmares que está tudo de pé — e depois PERGUNTA-ME onde está o vídeo. Não avances sozinho.**

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
