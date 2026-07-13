# 🏁 FECHO — 13 de julho de 2026

**O dia mais produtivo do projeto.** Entrou uma regra do Vasco que desbloqueou o M3, curou-se uma
doença estrutural que já tinha mordido três vezes, e o pipeline passou a correr **inteiramente no Mac**.

---

# 📍 O ESTADO

```
RECALL 96,8%  ·  PRECISÃO 95,4%  ·  F1 96,1  ·  13/13 serviços  ·  fim_dentro 0  🔒
```
*(de manhã: 72/63 — mas isso foi ontem. Ontem à noite: 96,3/95,9.)*

```bash
cd padelpro-vision
python3 teste_regressao.py     # 🔒 96,8 / 95,4 / 13 / 13 / 133 / 19 / 0
python3 verificar_fonte.py     # 🆕 o guarda: ✅ FONTE LIMPA
python3 ablacao.py             # quanto vale cada regra
python3 m3_candidatos.py       # 🆕 os candidatos a serviço: 13/13 = 100% recall
python3 gerar_tempo_util.py --video
python3 gerar_tempo_util.py --dados barbosa   # 🆕 o 2.º vídeo (GT ainda vazio)
```

---

# 🔴 A REGRA QUE ENTROU — **S23, O QUIQUE DO SERVIÇO** *(do Vasco)*

> *"Temos de matar este lixo pela **bola na mão do NÃO SERVIDOR — ANTES de bater no chão**."*
> *"Mesmo que tenha kick, **só o ÚLTIMO** antes da mudança de direção para o outro campo **conta**."*

## **A LEI: NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.**

- o **servidor** larga a bola → ela **QUICA** (na linha de serviço) → e **só depois** bate
- o **não-servidor** tem a bola na mão → **passa-a / atira-a** ⇒ **SEM QUIQUE**

**Medido:** os **13/13 pontos reais** têm quique fundo (`prof` 1,04–1,45) · **o lixo tem ZERO.**
**Separação perfeita, sem afinar um único número.** Vale **+3,5 de precisão**.

### 🔑 E POR QUE É QUE O RESSALTO FUNCIONOU AGORA, DEPOIS DE FALHAR TANTAS VEZES
**Não se afinou o detetor. É o MESMO. Mudou-se a PERGUNTA.**

| | |
|---|---|
| ❌ **S14** perguntava *"há dois quiques ⇒ acabou?"* | **em qualquer sítio, a qualquer hora** ⇒ o chão, a parede e a raquete confundem-se ⇒ **49 falsos** |
| ✅ **S23** pergunta *"há um quique **FUNDO**, na **LINHA DE SERVIÇO**, nos **3 s antes** da 1.ª travessia?"* | **um sítio · um instante · um ritual** ⇒ **13/13, zero falsos** |

> **FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA.**
> **O ressalto nunca esteve estragado. Estávamos a apontá-lo para o sítio errado.**

## 🔓 E ELA DESBLOQUEOU DUAS COISAS

### 1. A **B15 — a FAIXA CEGA** (`MIN_PROF` 0,35 → 0,15)
O Vasco: *"os de cá, perto da rede, devolvem a bola muito **alta e perto** — não dá tempo à bola de
passar, nos frames."* **Tinha razão:** havia uma faixa cega de 35% do meio-campo à volta da rede, e o
**volley à rede** atravessava e morria lá dentro, **invisível**. O código via **52%** das travessias.

⚠️ **A B15 e a S23 ANDAM JUNTAS.** Ampliar sem a S23 traz **um segmento falso**.
**O ganho real não são os 0,5 de recall** — é que os **pontos 10 e 11** estavam pendurados numa
**travessia ÚNICA**, e **medido: tirá-la ⇒ O PONTO DESAPARECE**. Agora têm 3.

### 2. **O M3 ARRANCOU** *(`m3_candidatos.py`)*
Varrer **todos os quiques** do vídeo, **sem saber onde estão os pontos**:
```
   quiques FUNDOS (na linha de serviço) ......... 174
   ... com uma TRAVESSIA nos 3 s a seguir ........ 68
   ... agrupados (só o ÚLTIMO conta) ............. 37   ← CANDIDATOS
   >>> RECALL 13/13 = 100%  ✅   ·   PRECISÃO 35% (24 falsos por matar)
```
**Encontra os 13 serviços. Todos.** É a forma que a diretriz manda ter: **recall 100%, o lixo
limpa-se depois.** O M3 deixou de estar bloqueado — **passou a ser trabalho.**

---

# 🦠 A DOENÇA — **curada, e com guarda**

> **Uma regra pode estar no mapa, com o nome certo, e fazer outra coisa.**
> **Um ficheiro pode chamar-se "a fonte", e ser uma cópia morta.**

**Mordeu TRÊS vezes num dia:**
1. a **S12** marcada ✅, com o nome certo, **a fazer outra coisa** *(e a S8 marcada ✅ e a não correr)*
2. **duas regras diferentes chamadas `S23`** — uma no código (a correr), outra no ficheiro (nunca correu)
3. **DEZ documentos duplicados**, quatro já divergidos — incluindo o **ground-truth** *(o `docs/` tinha
   12 rallies; o certo tem 13)* e a `RECEITA_VIDEO_NOVO.md`, que ainda mandava pôr `MIN_PROF=0,35`

**E mordeu quem a estava a curar:** o Claude arrumou 10 duplicados **e criou 4 novos a seguir**.

## ✅ **`verificar_fonte.py`** — o guarda. **33 → 0 falhas.**
```
① duplicados      → qualquer nome repetido FALHA (exceto se um for PONTEIRO)
② ✅ que não corre → a função existe? é CHAMADA com TODOS os argumentos? o interruptor é LIDO?
③ ablação         → regra que vale +0,0 → AVISA (redundante OU não corre)
④ colisão de nomes → o mesmo ID duas vezes
⑤ sinónimos       → RESSALTO = QUIQUE = BOLA NO CHÃO
⑥ 🐕 a COLEIRA    → o GT do código vs o GT do .md. Se divergirem, FALHA.
```
**E o guarda foi testado contra as 4 doenças reais, injetadas numa cópia em `/tmp`. Apanhou as quatro.**
*(Um guarda que nunca dispara é indistinguível de um guarda que não existe.)*

## E o guarda disparou **contra quem o escreveu** — três bugs a sério
- procurava o ficheiro **só na raiz** ⇒ disse *"o `m1_tempo_util.py` não existe"* — **existia**
- a regex exigia `| **B6** |` e a **B6** está escrita `| B6 |` ⇒ **nunca a leu** ⇒ declarou *"não existe
  regra B6"*. **A B6 é uma regra do Vasco** *("dois cliques dão a direção")* e vale **+10,2 de recall**.
  A contagem passou de "83" para as **117 regras** reais.
- os ponteiros que ele escreveu **passaram das 30 linhas** ⇒ **`[PONTEIRO QUE CRESCEU]` contra ele próprio**

---

# ✅ O QUE FICOU ARRUMADO

| | |
|---|---|
| **A FONTE ÚNICA** | `padelpro-vision/REGRAS_DO_VASCO.md` — **117 regras**, zero nomes duplicados. O da raiz e o de `docs/` são **ponteiros**. *(É a única pasta que vai para o GitHub.)* |
| **O GROUND-TRUTH** | `padelpro-vision/data/ground_truth/` (13 rallies) — **com coleira**: se divergir do código, o guarda falha |
| **`m1_tempo_util.py`** | era um **engodo vivo** (a S12 velha, ninguém a importava, e 4 regras apontavam para lá). Virou **lápide**. |
| **`B8_VAI_E_VEM` → `B14_VAI_E_VEM`** | o interruptor tinha o nome de **outra** regra (a B8 = coerência temporal, por implementar). Colisão morta. |
| **`S18_MAO_PASSE` · `S19_2_TOQUES`** | **interruptores VAZIOS** (sem código atrás) — fora do `REGRAS`. *"Uma regra desligada é uma escolha. **Um interruptor vazio é uma armadilha.**"* |
| **S2 e S30 — REABERTAS** | 🚨 dei-as como *"bloqueadas pela câmara"* citando **"só 21,8% dos frames têm os 4 jogadores"**. **O 21,8% era um artefacto do `max_det=4`** (sem cap + regras J: **38,8%**). ⚖️ **MEDIR ANTES DE CITAR.** |
| **S36** | dizia *"por implementar"* — **metade JÁ CORRIA** (o chão = inversão vertical) |
| **Tudo no Mac** | bola (BlurBall) **e** jogadores (PlayerTracker), os dois em **`mps`**. **O Kaggle e o Colab acabaram.** |

---

# 🚨 O PROBLEMA NOVO — **CUSTO E ESPAÇO**

```
Parada4     960×540   ·  8.741 frames  ·  4:52  ·   89 MB
Barbosa    1280×720   · 16.138 frames  ·  8:58  ·  544 MB
                        ↑ 1,78× píxeis   ↑ 1,85× frames  =  3,3× o trabalho

os jogadores no Mac (mps):  12,5 min para o Parada4  ⇒  ~40 min para o Barbosa
blurball/run_BarbosaMeireles/ ..... 26 GB   ← 16.138 ficheiros PNG, um por frame
o que o pipeline REALMENTE usa ....  522 KB  (traj.csv)
```

> ## **26 GB de lixo intermédio para produzir 500 KB de sinal.**
> **Não é a GPU que é lenta. É o disco a escrever 16 mil PNGs sem compressão.**

**9 minutos de vídeo custam ~50 minutos de máquina.** Uma hora de padel custaria **~5,5 horas**.
**Não escala.** E o Vasco tem razão: **isto tem de se resolver antes de crescer.**

## As alavancas, por retorno — **medir, não adivinhar**

| # | alavanca | ganho esperado | risco |
|---|---|---|---|
| **1** | **APAGAR os PNGs no fim do run** *(o `traj.csv` é tudo o que interessa)* | **26 GB → 0** | **nenhum** |
| **2** | **PNG → JPEG** (ou ler o vídeo direto, sem extrair frames) | ~10× menos disco **e I/O** ⇒ mais rápido | mínimo (medir) |
| **3** | **Baixar a resolução para 960×540** (a do Parada4) | **1,78× menos trabalho** | ⚠️ **A BOLA FICA MAIS PEQUENA.** Pode custar recall. |
| **4** | `step`, `fp16`, `batch` no BlurBall | por medir | por medir |
| **5** | **GPU na nuvem** — estudar preços a sério (Colab Pro, Kaggle, aluguer) | por estudar | ⚠️ **não inventar preços. PROCURAR.** |

### 🔑 **O TESTE ELEGANTE DA #3 — e é de graça**
**Não adivinhes se baixar a resolução estraga a bola. TESTA NO PARADA4** — é o único vídeo onde
temos **régua** (ground-truth, 13 rallies, 96,8/95,4).

```
1. baixa o Parada4 de 960×540 para 640×360  (e 480×270)
2. corre o BlurBall
3. corre o teste_regressao
4. se o recall aguentar ⇒ ganhaste 2× a 4× de velocidade, DE GRAÇA, e sabes o preço exacto
   se cair ⇒ sabes exactamente quanto custa cada píxel, e paras onde deves
```
**É a mesma lei de sempre: só o que se corre é que conta.**

---

# ➡️ O QUE VEM A SEGUIR

## 1. 🎬 **O 2.º VÍDEO — `BarbosaMeireles.mp4`** *(está a meio)*
```
✅ o bloco --dados barbosa       — só troca DADOS. NENHUM limiar muda. 🔒
🔴 calibracao_BarbosaMeireles.json   — POR FAZER (à mão, no calibrar_campo.html — regra C1)
🔴 GT = []                            — POR ANOTAR (anotador_rallies.html) 🚨 CONTAR TODOS OS PONTOS
🔴 bola + jogadores                   — NOVO_VIDEO.command
```
> 🔒 **O COMPROMISSO, assumido ANTES de ver os resultados: NÃO SE TOCA EM NENHUM PARÂMETRO.**
> `L_RAQUETE=11` · `SILENCIO=4` · `PAD_ANTES=1,6` · `MIN_PROF=0,15` · `QUIQUE_PROF=0,7` vão como estão.
> **Afiná-los ao vídeo novo torna o teste INÚTIL** — passamos a ter dois vídeos decorados.
>
> **Previsão escrita:** as **LEIS** do Vasco aguentam · os **AJUSTES** do Claude partem.
> 🚨 **Se se perderem pontos: DESLIGAR A S23 PRIMEIRO** (`--sem S23_QUIQUE_SERV` + repor `MIN_PROF=0.35`).
> É a peça mais nova e a menos testada — **1.ª vez que o ressalto entra no pipeline.**

## 2. ⚡ **O CUSTO** (ver acima) — começar pelo **#1** e pelo teste de resolução no Parada4

## 3. 🎯 **O M3** — matar os 24 falsos, com as regras dele que **ainda não correm**:
**S3** (formação nos 2 de cima) · **S4** (quadrado cruzado) · **S10** (duplo ressalto) ·
**S6** (alternância — ⚠️ **não é lei**: no ponto de ouro quem recebe escolhe) · **S2** e **S30** (reabertas)
⚖️ **LEI DE DESENHO: as regras PONTUAM, NÃO VETAM.** Há sempre uma exceção legítima.

## 4. 🎨 **A COR** — J6+ (seguir pela roupa) + **J10** (a salvaguarda: *"a camisola não muda em todos ao
mesmo tempo"*) + **J9** (aprender as cores no início de cada ponto — **desbloqueada**: o M1 dá 13/13)

## 5. 🔊 **GRAVAR COM ÁUDIO** — o som do **quique**, o da **parede** e o da **raquete** são **três sons
diferentes**, e são exactamente as três coisas que a imagem **não distingue**.
**O áudio não precisa de profundidade.**

---

# 🚨 A REGRA NOVA — **UMA CANETA DE CADA VEZ**

Hoje **duas conversas escreveram no `gerar_tempo_util.py` ao mesmo tempo.** Deu certo **por sorte**
(mexeram em sítios diferentes). Da próxima, **uma apaga o trabalho da outra e o `teste_regressao`
continua verde** — porque as duas alterações eram, isoladamente, válidas.

> **Só UMA conversa toca no `gerar_tempo_util.py` de cada vez.**
> As outras **leem, medem, e criam ficheiros novos.** Nunca editam.

**O git não protege disto: a última a gravar ganha, em silêncio.**

---

# 📐 AS LEIS (não se negoceiam)

1. 🎯 **Nunca perder um ponto.** Mais lixo > menos tempo útil. **Otimizar RECALL.** E o tempo útil é para **VER** o ponto.
2. 🎬 **VÍDEO antes de métricas.** Ele encontrou **todos** os bugs a olhar. **Nenhum estava nos números.**
3. 🧪 **TESTAR, não raciocinar.** *(Descartei 8 regras com um raciocínio bonito. A que ia deitar fora resolveu o maior problema que havia.)*
4. 🚨 **DESCONFIAR do ground-truth.** Um falso **bem-comportado** é **verdade que falta ao GT**.
5. ⚖️ **MEDIR ANTES DE CITAR.** *(Custou-me a **S2** e a **S30** — mortas com um número que era um artefacto.)*
6. 🕳️ **LER O CÓDIGO, NÃO O MAPA.**
7. ⛔ **SEM ATALHOS.** Números mágicos proibidos. **Declarar o atalho na MESMA mensagem em que se dá o número.**
8. 📊 **FAIXA FINA = OBSERVÁVEL · ÁREA GRANDE = AMBÍGUA.**
9. ⚠️ **Nada em píxeis absolutos sobrevive à perspetiva.** Tolerâncias = **frações do meio-campo local**.
10. ⚖️ **As regras do Vasco são LEIS. Os números do Claude são AJUSTES.** Nunca com o mesmo estatuto.
11. 🛑 **As definições do jogo PARAM E PERGUNTAM.** O que é *ponto*, *serviço*, *tempo útil* — **é dele**.
12. 🏃 **SÓ O QUE SE CORRE É QUE CONTA.**
