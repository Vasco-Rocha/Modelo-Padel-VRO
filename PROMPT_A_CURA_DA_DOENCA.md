# ▶️ PROMPT — A CURA DA DOENÇA
### *(cola tudo o que está entre as linhas `=====` numa conversa NOVA do Cowork)*

=====

**Tens UMA tarefa. Só uma. Não faças mais nada.**

# Escrever o `verificar_fonte.py` — o guarda que apanha a doença antes de ela morder.

---

# 🦠 A DOENÇA

**Uma regra pode estar no mapa, com o nome certo, e fazer outra coisa.**
**Um ficheiro pode chamar-se "a fonte", e ser uma cópia morta.**

Ela **não parte nada**. O pipeline corre, os números saem, ninguém dá por nada.
**Só aparece quando alguém tropeça nela.** E no dia 13 de julho de 2026 **mordeu TRÊS VEZES**:

| # | o caso | como se descobriu | o que custou |
|---|---|---|---|
| **1** | A **S12** estava marcada ✅ no `MAPA_DAS_REGRAS.md`, **com o nome certo**, e **fazia outra coisa** — agarrava-se ao último **CRUZAMENTO** em vez da última **PANCADA**. A **S8** estava ✅ e **nem sequer corria**. | por acaso, a ler o código | pontos partidos ao meio durante semanas. Corrigida: **recall 93,2 → 97,0** |
| **2** | **Duas regras diferentes com o nome `S23`**: *"o quique do serviço"* (no código, a correr, **+3,5 de precisão**) e *"as 6 condições do serviço"* (no ficheiro, **nunca correu**). Idem para o **`B11`** e para o **`B8`**. | o **Vasco** perguntou *"a nova conversa diz que não existe"* | uma conversa nova ia **implementar a S23 outra vez, diferente, por cima da que já corre** |
| **3** | **DEZ documentos duplicados** entre a raiz e o `padelpro-vision/`. **Quatro tinham divergido.** A `RECEITA_VIDEO_NOVO.md` da raiz ainda mandava pôr `MIN_PROF=0,35` — o que **desliga metade da B15**, que anda de par com a S23. | outra conversa tropeçou | duas conversas a escrever em ficheiros diferentes, **cada uma convencida de que o seu era a verdade** |

**Três instâncias. Três curas À MÃO. E nada impede a quarta.**

> ## 🏃 **A LEI DO VASCO: SÓ O QUE SE CORRE É QUE CONTA.**
> **Uma cura feita à mão não se corre. Logo, não conta.**

---

# 🎯 O QUE TENS DE ESCREVER

## `padelpro-vision/verificar_fonte.py`

Corre em **CPU, em segundos**. **Falha ALTO** (código de saída ≠ 0). Quatro verificações:

### ✅ 1. **DOIS FICHEIROS COM O MESMO NOME** → FALHA
Varre a pasta do projeto. Se o mesmo nome de ficheiro (`.md`, `.py`) existir em **mais do que um
sítio** fora de `snapshots/` e `BACKUPS/` — **falha**, e **diz se o conteúdo difere**.
🔑 **A FONTE É SEMPRE `padelpro-vision/`.** É a **única pasta que é um repo git** — a única que vai
para o GitHub. Um ficheiro na raiz **não é versionado**: se o Mac morrer, **perde-se**.
*(Os da raiz devem ser **PONTEIROS** — ficheiros de uma página a dizer "a fonte é X". Se um ponteiro
crescer, alguém escreveu nele. **Falha.**)*

### ✅ 2. **REGRA MARCADA ✅ QUE NÃO EXISTE NO CÓDIGO** → FALHA
Lê o **`padelpro-vision/REGRAS_DO_VASCO.md`** (**a FONTE ÚNICA — 117 regras**). Para cada regra cujo
estado diga **implementada / a correr / ✅**, confirma no código:
1. a **função existe**?
2. é **CHAMADA** — e com **todos os argumentos** de que precisa?
   *(A **S23** quase se perdeu assim: o `teste_regressao.py` e o `ablacao.py` chamavam o `rallies()`
   **sem os quiques**. A regra estava lá e **não corria dentro do teste**.)*
3. o **interruptor** (`REGRAS[...]`) existe e está `True`?

### ✅ 3. **REGRA ✅ QUE VALE +0,0 NA ABLAÇÃO** → AVISA (não falha)
Corre a `ablacao.py`. Uma regra que, ao ser desligada, **não muda um único número**, é uma de duas:
**ficou redundante** — **ou não corre**. **As duas precisam de ser ditas em voz alta.**
*(Hoje: a **S18** e o **`min_det`**. A S18 está escrita como se estivesse a trabalhar, e **não está**.
É a forma **mais suave** da doença: uma regra que não mente sobre **o que faz**, mente sobre
**quanto vale**.)*

### ✅ 4. **O MESMO NOME DE REGRA USADO DUAS VEZES** → FALHA
`S23` era duas regras. `B11` era duas. `B8` era duas. **Nunca mais.**
Varre o `REGRAS_DO_VASCO.md` **e** os nomes dos interruptores `REGRAS[...]` no código.

---

# 🚨 O TESTE DO TESTE — **e é isto que decide se o trabalho presta**

## **Um guarda que nunca dispara é indistinguível de um guarda que não existe.**

**NÃO basta o script passar no estado atual.** Tens de **PROVAR que ele apanha as três doenças reais**.

Reproduz cada uma delas — **numa cópia, nunca no original** — e mostra ao Vasco que o guarda **FALHA**:

| | injeta... | o guarda TEM de... |
|---|---|---|
| **1** | uma regra marcada ✅ cuja função **não existe** no código | **FALHAR** (verificação 2) |
| **2** | duas regras com o **mesmo nome** no `REGRAS_DO_VASCO.md` | **FALHAR** (verificação 4) |
| **3** | um `RECEITA_VIDEO_NOVO.md` **na raiz** com conteúdo diferente do do repo | **FALHAR** (verificação 1) |
| **4** | o `rallies()` chamado **sem os quiques** no `teste_regressao.py` | **FALHAR** (verificação 2.2) |

**Se o guarda não apanhar as quatro, não está feito.** Volta atrás.
**Depois repõe tudo e confirma que ele PASSA no estado limpo.**

---

# 🛑 COMO TRABALHAR — NÃO NEGOCIÁVEL

## 1. ⛔ **NÃO AVANÇAS PARA NADA SEM PERGUNTAR.** Propõe → espera → só depois faz.

## 2. 🔒 **NÃO TOCAS NO PIPELINE.**
```
gerar_tempo_util.py   ❌ não se mexe
teste_regressao.py    ❌ não se mexe (a não ser para o TESTE DO TESTE, e repõe-se)
ablacao.py            ❌ não se mexe — só se CORRE
```
**Correr `python3 teste_regressao.py` ANTES e DEPOIS.** Estado travado:
```
RECALL 96,8 · PRECISÃO 95,4 · F1 96,1 · 13/13 serviços · fim_dentro 0
```
**Se falhar no fim, a alteração é que está errada. Nunca o teste.**

## 3. ⛔ **NÃO INVENTAS ATALHOS.** Se usares um, **declara-o na MESMA mensagem em que dás o número.**

## 4. 🧪 **TESTAR, NÃO RACIOCINAR.** Não digas *"o guarda apanharia isto"*. **Injeta a falha e mostra.**

## 5. 🕳️ **LÊ O CÓDIGO, NÃO O MAPA.** *(É literalmente a doença que estás a curar.)*

## 6. 👤 **O Vasco NÃO é developer.** Passo a passo, uma coisa de cada vez.

---

# 📍 ONDE ESTÁ TUDO

```
padelpro-vision/                     ← 🔑 A FONTE. A única pasta versionada (GitHub).
├── REGRAS_DO_VASCO.md               ← as 117 regras. A FONTE ÚNICA.
├── gerar_tempo_util.py              ← o pipeline (🔒 não tocar)
├── teste_regressao.py               ← o estado travado (🔒 não tocar)
├── ablacao.py                       ← quanto vale cada regra
├── m3_candidatos.py                 ← o gerador de candidatos a serviço (13/13)
└── verificar_fonte.py               ← 🆕 O QUE VAIS ESCREVER

./  (a raiz)                         ← ⛔ tudo aqui devia ser PONTEIRO
```

🔑 **"RESSALTO" = "QUIQUE" = "BOLA NO CHÃO"** — três nomes, a mesma coisa. Se procurares só por
*"ressalto"* encontras a **S9/S14/S36** (bloqueadas) e concluis que **não funciona**. A que
**funciona** chama-se **"quique"** (a **S23**). **É exatamente o tipo de coisa que o guarda tem de
apanhar** — considera uma verificação **5** para **sinónimos conhecidos**.

---

# ✅ NO FIM, RESPONDE A ISTO

1. O `verificar_fonte.py` **passa** no estado atual? *(Devia.)*
2. **Apanhou as quatro doenças injetadas?** **Mostra o output de cada uma.**
3. O `teste_regressao.py` continua a dar `96,8 / 95,4 / 13 / 13 / 133 / 19 / 0`?
4. Quantos ficheiros duplicados/divergidos encontrou **a sério**, hoje, na pasta?

**Se alguma coisa não correu — DIZ. Não arredondes, não finjas.**

**Guardar:** duplo-clique no **`GUARDAR_TUDO.command`** *(o Claude não mexe no `.git`)*.

=====
