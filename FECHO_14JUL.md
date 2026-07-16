# 🌅 FECHO — 14 JUL 2026
### *O dia em que a GEOMETRIA mentiu. E o Vasco viu-a mentir, a olhar para um frame.*

> **Documento DATADO. É história, não é estado.**
> **O estado sai de `python3 teste_regressao.py` e de `python3 auditar_mentiras.py`. Nada mais.**

---

# 🛑 AS REGRAS DA CASA, HOJE   *(não negociáveis — vêm da outra caneta)*

```
⛔ NADA PESADO NO MAC — está a extrair PNGs. Escreve-se agora, corre-se depois.
⛔ NÃO TOCAR NO gerar_tempo_util.py — outra conversa está lá dentro.
   (não é medo de conflito: se o teste_regressao vier a 94, ninguém sabe de quem foi.
    Um teste com DUAS variáveis não prova nada. — foi o erro de 13 jul.)
🟢 LIVRE: padelpro/modules/servico.py · ficheiros NOVOS · os .md
```

**⚠️ NADA FOI TOCADO NO PIPELINE HOJE.** 5 ficheiros novos + edições só no `REGRAS_DO_VASCO.md`.

---
---

# 🩸 O BUG DO DIA — **o mais perigoso que já apareceu neste projeto**

Eu testava *"o jogador está à frente da linha de serviço?"* assim:

```python
abs(y - rede) < abs(y - linha)      # ⛔ isto é o PONTO MÉDIO, não a LINHA
```

**Um jogador um METRO à frente da linha era lido como ATRÁS.**
A formação dizia **"serve BAIXO" 20 vezes em 21** — um sinal **MORTO com ar de vivo**.

> ## **Não parte nada. Não dá exceção. Dá a RESPOSTA ERRADA, com CONFIANÇA.**
> ## 🎬 **O Vasco viu-o A OLHAR PARA UM FRAME. Não aparecia em número nenhum.**
>
> *"vê os pés do jogador de vermelho. Está claramente à frente da linha de serviço.
> **Porque não é detetado como estando à frente?** Este erro repete-se muitas vezes."*

---
---

# ⚖️ AS REGRAS NOVAS — **e todas nasceram deste frame**

## 📏 **D19 — A LINHA É A LINHA. NÃO SE PÕE UM LIMIAR EM CIMA DELA.**

*"Passou a linha?"* é **BINÁRIO**. ⛔ **NUNCA** substituir por *"está mais perto da linha A do que
da linha B"*, por uma **percentagem do meio-campo**, por uma **margem de tolerância**, nem por um
**ponto médio**. Isso **não é a linha — é uma linha INVENTADA**, algures a meio do campo.

👉 **A tolerância vive no TEMPO, NUNCA no ESPAÇO.** O tremor resolve-se com **histerese (D1)** e com
o **anti-jitter (F5)** — *"se a box só toca, treme ou oscila em cima da marca, não abras entrada"*.
**NÃO SE MOVE A LINHA PARA TAPAR O TREMOR.**

> ## 🔑 **ISTO MANDA EM TODO O M2.** A **F2** é a **MESMA comparação**, com outras linhas.
> **Um limiar em cima dessas linhas envenena as fases inteiras, em SILÊNCIO.**
> *(É a **D10** — «geometria > modelo» — levada até ao fim: **a geometria só é geometria se a linha
> for A LINHA**.)*

## 📏 **D20 — EM CIMA DA LINHA ⇒ CONTA COMO ATRÁS.**   *(Vasco)*

A fronteira pertence **SEMPRE à zona mais RECUADA**. *"Quem tem o pé **NA** linha **ainda não a
passou**."* *(É a **D1** — em dúvida, o estado mais conservador — aplicada ao **ESPAÇO**.)*

## 🦶 **J16 — A BOX TRANSBORDA POR BAIXO.**   *(Vasco)*

*"Temos de dar uma margem em baixo — a bounding box termina **ligeiramente abaixo** dos pés."*
⇒ a **F3** *(a posição é a aresta inferior)* leva uma **margem**.
⛔ **É uma FRAÇÃO DA ALTURA DA BOX, nunca píxeis** — encolhe sozinha com a perspetiva.
⚠️ **NÃO VIOLA A D19:** não se mexe na **LINHA**; corrige-se **onde estão os PÉS**. É a **MEDIÇÃO**,
não a **RÉGUA**.

**MEDIDO:** de `k=0,00` a `k=0,10` ⇒ **0 dos 21 serviços mudam de fase.**
**A lei é dele. O número (`0,03`) é meu — e está medido a ser inofensivo.**

---

# 🔴 **F2 — CORRIGIDA. ESTAVA ERRADA NA FONTE.**

> **TRANSIÇÃO = a faixa entre as duas COSTURAS DA PAREDE** (`vidro|malha3` → `malha2|malha3`).
> **NÃO é a linha de serviço.** A linha de serviço vale para o **SERVIÇO** (S1/S9) — **é outra coisa.**

⚠️ **O Vasco escreveu isto dentro do `calibracao_BarbosaMeireles.json`, a 13 jul**, com o aviso
literal ***"CONTRADIZ a F2 escrita — a F2 é que está errada"*** — **e a fonte continuou a mentir
mais um dia.** As **4 costuras já estavam calibradas e NUNCA tinham sido usadas.**

> ## 🦠 **A doença: a verdade escrita em DOIS sítios — e o sítio ERRADO é o que toda a gente lê.**

---
---

# ⚖️ **S2 ⊕ S3 = UMA LEI** — fundidas, com o texto dele

> ## 🔑 **NO MOMENTO DO SERVIÇO SÓ PODE ESTAR UM JOGADOR ADIANTADO.**
> ## **É o parceiro do servidor. A equipa dele SERVE.**
> *"Se estiver confuso — no momento de serviço **SÓ PODE estar UM jogador na rede**."*
> **Uma pergunta só. Sem ambiguidade possível.**

| | |
|---|---|
| **quem SERVE** | **1 atrás + o parceiro ADIANTADO** *(na rede, ou **no máximo perto da zona de transição**)*. 🏃 **E depois do serviço, o SERVIDOR CORRE** para transição/rede. |
| **quem RECEBE** | **os 2 ATRÁS.** Um pode estar **EM CIMA da linha** *(⇒ **D20**: conta como atrás)*. **No máximo, no início da zona de transição.** |

⇒ as configurações são **incompatíveis** ⇒ **a formação de uma dupla DEDUZ a da outra.**

### E lê-se com a luz que houver *(era a S3 — a decisão dele de 12 jul)*
```
①  vejo os 4                   ⇒  aplico a formação DIRETA
②  só vejo os 2 de CIMA        ⇒  deduzo que os de baixo estão em DEFESA
                                  ⇒ os de cima TÊM de ter um em TRANSIÇÃO ou na REDE
③  vejo um de BAIXO na rede    ⇒  os de baixo SERVEM  ⇒  os de cima estão ATRÁS
```

## 📊 MEDIDO — **acerta nos DOIS vídeos, cada um no nível que a câmara permite**

```
BARBOSA (courtsmaster)   nível ①  21/21  ✅   "exatamente UM dos 4 não está em DEFESA"
                                              quem recebe: DEF+DEF nas 21
                                              quem serve:  DEF + (TRANSIÇÃO ou ATAQUE)

PARADA4 (MATCHi)         nível ①   3/13  🔴   não vê o parceiro de baixo (cortado pela borda)
                         nível ②  13/13  ✅   os 2 de cima DEF+DEF em 13/13 ⇒ SERVE BAIXO
```

> ## 🔑 **O NÍVEL ② NÃO É UM PLANO B. Com a câmara baixa é a ÚNICA leitura possível — e acerta em TODAS.**
> **Era a decisão do Vasco de 12 jul. Ficou marcada ✅ — e NUNCA CORREU UMA LINHA.**

⚠️ **A FRONTEIRA NÃO É "A REDE" — É "SAIR DA DEFESA".**
Exigir **ATAQUE** dá só **8/21**. Em **13** deles o parceiro está em **TRANSIÇÃO** — que é
**exactamente** o *"no máximo perto da zona de transição"* dele. **A cláusula dele explicava o número.**

📐 **E É A MESMA LINHA NAS DUAS CÂMARAS:**
```
BARBOSA  trans_perto_tras  →  0,78 do meio-campo
PARADA4  juncao_perto      →  0,76 do meio-campo
```
> ## ⇒ **A FRONTEIRA É DO JOGO, NÃO DO VÍDEO.**
> *(Cheguei a dizer que a costura "não existia no Parada4". **Existe.** — **D17**: confirmar a
> premissa antes de aceitar a conclusão. Falhei-a duas vezes hoje.)*

⚠️ **O que o Parada4 falha NÃO é geometria — é CÂMARA.** **Nenhuma regra cura isso.**

### 📎 NOTA À S2 *(achado meu — **NÃO é lei nova**: é a ponte entre a S2 e a F2)*

| quem **SERVE** | quem **RECEBE** |
|---|---|
| um adiantado + um atrás ⇒ **TRANSIÇÃO** | os dois atrás ⇒ **DEFESA** |

> **A formação de serviço e as fases do M2 são A MESMA GEOMETRIA. Não são dois sistemas.**

**Vale porque dá ao detetor de serviço uma 2.ª leitura INDEPENDENTE, de graça:** as duas concordam
**21/21**, e **viram as duas ao mesmo tempo no ponto 15** *(a mudança de dupla)*, **sem nada em
comum** ⇒ a **S22** (a alternância) **auto-verifica-se sem custo.** *(D14 ✅ · D16 ✅)*

⚠️ **E a 2.ª leitura NÃO pode vir do tracker da bola:** no instante do serviço ele está agarrado a
um **TÉNIS** (**B19**) — discorda **8 em 21**, e está **errado nas 8**. **Tem de vir do QUIQUE (S23).**

---
---

# 👥 A CASCATA DOS JOGADORES — **a correr, pela ORDEM dele**

```
1. 🦶 os PÉS no polígono           LIMPA      (mata o público)
2. 👀 os 2 de cima sempre visíveis PERGUNTA   (se só há um, o outro NÃO desapareceu)
3. 🔗 CONTINUIDADE                 PREENCHE   ⚠️ NÃO é filtro. ACRESCENTA.
4. 👥 nunca mais de 2 por lado     CORTA      ← É O ÚLTIMO
5. 🛡️ os de baixo invisíveis      DEDUZ      (a AUSÊNCIA é o sinal: recuaram)
```
**🚨 O «2 POR LADO» É O ÚLTIMO.** Cortar antes da continuidade ⇒ **deita fora o jogador VERDADEIRO
e fica com o FALSO.** *(O `servico.py` tem a ordem **TROCADA**.)*

```
PARADA4    4/13 serviços com os 4  ·  43,6% dos frames    (era 21,8% com max_det=4)
BARBOSA   21/21 serviços com os 4  ·  67,1%
os 2 DE CIMA:  13/13  e  21/21.  SEMPRE.
```

⚠️ **O critério do «2 por lado» é a GEOMETRIA** *(o tamanho que um jogador TEM de ter naquele ponto
do campo)*, **NUNCA a confiança** — foi o erro do `max_det=4`, e é a **D10**.

## 🔑 E O ACHADO QUE VALE MAIS DO QUE A CASCATA

**O polígono do Barbosa está MAL** — foi **DEDUZIDO** (não desenhado à mão, ⇒ viola a **C1** e a
**J15**), e a **aresta de baixo está em y≈881** quando **o frame acaba em 720**. ⇒ **toda a faixa de
baixo da imagem conta como "dentro"** e **o público entra como candidato.**

# **E A CASCATA ACERTA À MESMA.**

**Quem limpou não foi o polígono (J1) — foi a ESTRUTURA (J4, pela geometria).**

> ## **D9, À LETRA: RECALL PELA DETEÇÃO · PRECISÃO PELA ESTRUTURA.**
> **O polígono falhou. As REGRAS DO JOGO salvaram. É a prova de que a arquitetura está certa.**

*(Continua a valer redesenhá-lo à mão — **C1** — mas **não é ele que segura a casa**.)*

---
---

# 🔴 AS 11 MENTIRAS — regras **✅ na fonte** que **NÃO CORREM no pipeline**

```
B1   objetos imóveis          "✅ apanha 4 objetos"     →  NUNCA correu um frame
S1   zona de serviço          "✅ implementada"          →  NUNCA correu
S3   formação só dos 2 de cima  "✅ (12 jul)"            →  NUNCA correu   ⭐ era "a decisão do dia"
S33  validade do serviço      "✅"                       →  é um STUB VAZIO
J1 J2 J4 J5 J6 J7 J8          "✅ ✅ ✅ ✅ ✅ ✅ ✅"      →  a cascata INTEIRA. Nenhuma corre.
```

> ## 🔑 **O PADRÃO:** as mentiras **não estão espalhadas ao acaso**. São **a BOLA (1)**, **os
> JOGADORES (7)** e **o SERVIÇO (3)**. **TUDO o que não é a trajetória da bola está marcado ✅ e
> morto.** O pipeline dos 96,8 % é, **literalmente, só a bola** — **e a fonte finge que não.**

## 🐕 E O GUARDA TEM UM PONTO CEGO — **a B1 passou por baixo dele**

O `verificar_fonte.py` diz **✅ FONTE LIMPA**. A `filtrar_objetos_imoveis()` **é chamada** — na
**linha 73 do `servico.py`**, **por código morto que ninguém importa**. O guarda vê a chamada e
dá-a por boa.

> ## **O guarda pergunta: "alguém a chama?"**
> ## **A pergunta certa é: "o PIPELINE a chama?"**
> *"Um guarda com um ponto cego ensina a confiar no ponto cego."* — Vasco, 13 jul

👉 **Corre o `auditar_mentiras.py`.** *(segundos, zero carga no Mac — só lê o código como texto)*

---
---

# 🚪 O QUE FICA PROVADO SOBRE O BARBOSA

**As boxes dos jogadores estão CERTAS no Barbosa** *(o Vasco confirmou a olhar: "a cascata está
sempre bem")*. **E o tempo útil continua MAU: 81,9 / 65,7.**

> # ⇒ **O PROBLEMA DO BARBOSA NÃO SÃO OS JOGADORES. É A BOLA.**
> # **É a B19 — o tracker agarra-se a um TÉNIS e a bola a sério NUNCA É DETETADA.**

**Ele disse-o ontem, a olhar. Hoje está medido.**

---
---

# ⏭️ O PRÓXIMO PASSO — **A ARQUITETURA**

**Tudo o que partiu hoje era A MESMA pergunta:**

> # **"ESTE PÉ PASSOU ESTA LINHA?"**

Ela está escrita em **4 sítios**, cada um com a **sua versão**. **Por isso mentiram todas ao mesmo
tempo — e em silêncio.**

```
campo.py       A RÉGUA — o ÚNICO ficheiro com direito a ver um PÍXEL
                 linha(nome, x) · pes(box) [F3+J16] · lado() · passou() [D19+D20]
                 · meio_campo_px()
jogadores.py   A CASCATA J1→J5, pela ordem dele. Uma regra = uma função.
fases.py       F1 + F2 — três chamadas a campo.passou(). Mais nada.
servico.py     A S2 — as fases, lidas no instante do serviço.
```

### As três leis que isto impõe

1. ⛔ **Nenhum ficheiro fora do `campo.py` vê um PÍXEL.** Um `y` noutro sítio é **um bug à espera**.
2. **Uma regra = uma função = um ID = um interruptor = uma linha na ablação.**
   **Se não tem as cinco, não é uma regra — é código.**
3. 📄 **O `REGRAS_DO_VASCO.md` passa a ser GERADO a partir do código.**
   > **Um `.md` escrito à mão é uma OPINIÃO. Um `.md` GERADO é um RELATÓRIO — e não pode mentir.**
   *(Hoje o guarda deu ✅ FONTE LIMPA e havia **11 mentiras**. Um guarda que lê um `.md` está a
   auditar **uma opinião**.)*

### O que É dados — e o que NÃO é

```
📐 as LINHAS    →  calibracao_<video>.json    (já é. UMA POR VÍDEO — nunca se partilham.)
🔢 os AJUSTES   →  ajustes.json               (os números do Claude, num sítio só, para o 2.º
                                               vídeo os poder partir sem ninguém os ir caçar)
⚖️ as LEIS      →  CÓDIGO. Uma função cada.   (as do Vasco. NÃO são configuráveis.)
```

> ## ⛔ **NUNCA GERAR CÓDIGO A PARTIR DE UM JSON DE REGRAS.**
> As regras dele **não são dados — são GEOMETRIA.** Enfiá-las em configuração **esconde-as atrás
> de um ficheiro**, e ele deixa de as poder **VER**. **E o bug de hoje nunca teria aparecido.**

⚠️ **A reescrita NÃO garante "sem erros". Vai ter bugs novos.**
**Garante outra coisa — e é a que interessa: o erro passa a ter MORADA.**

⚠️ **O `campo.py`, o `jogadores.py` e o `fases.py` são ficheiros NOVOS ⇒ escrevem-se JÁ, não partem
nada.** **Só o último passo — o `gerar_tempo_util.py` IMPORTAR o `campo.py` — espera pela outra
caneta, e faz-se com o `teste_regressao` VERDE a validar CADA passo (96,8 / 95,4).**

---

# 🔴 E DUAS COISAS DELE, POR RESOLVER   *(nenhuma é a formação)*

| | |
|---|---|
| **1. O ponto 13 do Barbosa — o serviço apanhado CEDO DEMAIS** | *"Detetou o início do serviço quando o jogador ainda estava a bater a bola antes de preparar a raquete. **Só o ÚLTIMO toque no chão — antes de tocar na raquete — interessa.**"* ⇒ **É a S23.** E a cláusula dele — *"mesmo com kick, **só o ÚLTIMO** conta"* — **já está escrita, e não está a ser cumprida.** |
| **2. O passe à mão entre colegas** | se quem **larga** e quem **apanha** estão do **MESMO lado da rede**, **não houve mudança de campo ⇒ NÃO É SERVIÇO.** A guarda que falta é **GEOMETRIA**. |

---

# 📁 FICHEIROS NOVOS   *(todos em `padelpro-vision/` · todos correm em SEGUNDOS · zero carga no Mac)*

```
auditar_mentiras.py    🔎 as 11 mentiras. "o PIPELINE chama esta função?"
cascata_jogadores.py   👥 a cascata J1→J5, pela ordem dele (+ pes() com a J16)
lei_da_formacao.py     ⚖️ a S2, com as DUAS leituras independentes
fases_m2.py            🎬 o M2 (F1+F2) com as COSTURAS DA PAREDE
ver_cascata.py         🎬 O TESTE VISUAL — folhas de contacto dos 13/21 serviços
```
```
🖼️ na raiz:  VER_CASCATA_FINAL_barbosa.png · VER_FASES_M2_barbosa.png
             VER_FORMACAO_17_CORRIGIDO.png · O_POLIGONO_MENTE.png
```

---
---

---
---
---

# 🎾 A TARDE — **O VASCO INVERTEU O PIPELINE. E o M3 saiu de lá.**

> ### *"E se for ao contrário — testares o tempo útil **PARTINDO DA S2**, e confirmando com
> ### as restantes regras de serviço?"* — Vasco, 14 jul

```
ATÉ HOJE:   a BOLA gera os pontos  →  o serviço confirma
            ⚠️ e a bola está agarrada a roupa branca (B19)

ELE:        a FORMAÇÃO gera os candidatos  →  as outras regras confirmam
            ✅ e os jogadores estão CERTOS (medido esta manhã)
```

> ## 🎣 **É a D9, à letra: DETETAR GENEROSAMENTE, LIMPAR PELA ESTRUTURA.**
> **Ele trocou um sinal PODRE por um LIMPO. E isso saltou por cima do bloqueio que nos prendia há dois dias.**

## 🏆 O RESULTADO — `detetor_servico.py`

```
BARBOSA:   21 candidatos · 21 serviços · RECALL 21/21 · ZERO falsos · ZERO bola
```

| | | mede |
|---|---|---|
| **⓵ S2** | **a FORMAÇÃO diz quem serve.** *"no momento do serviço só pode estar UM jogador adiantado"* | gerador: **46 blocos · recall 21/21** |
| **⓶ F5** | **o adiantado tem de ser ESTÁVEL** *(~1,2 s)*. *"se a box só toca, treme ou oscila, não abras entrada"* | **anti-jitter** |
| **⓷ S2b** | 🏃 **depois do serviço, o SERVIDOR CORRE** para transição/rede *(regra dele, 14 jul)* | **matou 20 · perdeu 0** |
| **⓸ S30** | **a formação está PARADA** | **matou 3 · perdeu 0** |

**Quatro regras. Todas dele. NENHUMA delas tinha corrido alguma vez.**

> ## 🔑 **A S42 e a S43 estavam desligadas à espera de um detetor de serviço a 100 %.**
> ## **Ele existe — e NÃO PASSA PELA BOLA.**
> *(o do pipeline está em 12/13 · este em 21/21)*

## 🩸 E TRÊS ERROS MEUS, todos apanhados por ele, todos a OLHAR

| | |
|---|---|
| **① «adiantado» = só a REDE?** | ⛔ **VIA FECHADA (medida).** Dá **11/21** — **perde 10 serviços**, e os extras **sobem de 2 para 8**. Em **13 dos 21** o parceiro está em **TRANSIÇÃO**. *"no máximo perto da zona de transição"* — **a cláusula dele explicava o número.** ⇒ **a fronteira é SAIR DA DEFESA.** |
| **② a S30 medida ANTES da formação** | 🔴 matava **os 21**. Antes do bloco eles ainda estão **a CAMINHAR para a posição**. **Mede-se DENTRO.** *(4× de separação: **0,088** antes do serviço · **0,353** a meio de um rally)* |
| **③ os 2 extras «a meio de um ponto»** | **NÃO eram falsos.** Um deles **era um serviço REAL, falhado (fora)**. ⇒ 🆕 **UMA FALTA É UM SERVIÇO. O detetor de serviço NÃO CONTA PONTOS** — um ponto pode ter **DOIS** serviços. *(É a **S22**.)* |
| **④ os últimos 2 extras** | **jitter numa faixa de 12 PÍXEIS.** Lá em cima a perspetiva esmaga a zona de transição — **um tremor de 5 px atravessa-a.** ⇒ **F5**. **Não se move a linha para tapar o tremor (D19).** |

---

# ⚪ E A BOLA — **a lei está certa. O sinal está partido.**

Ele reescreveu a **S23** como **UMA SEQUÊNCIA** *(`s23_sequencia.py`)*:

```
⓪ NÃO é roupa branca (B16)   ① FUNDA (na linha de serviço)
② QUICA NO CHÃO — inversão VERTICAL      (ele larga a bola)
③ BATE NA RAQUETE — inversão HORIZONTAL, EM DIREÇÃO AO CAMPO ADVERSÁRIO
④ 🔑 só conta o ÚLTIMO **ANTES DE A BOLA MUDAR DE CAMPO**
⑤ e a travessia só vale se vier da RAQUETE (L alto)
```

**As duas correções DELE levaram o recall de 71 % → 95 %:**
- ❌ *"o ténis está PARADO"* → **FALSO. Um ténis mexe-se.** A verdade dele é **GEOMÉTRICA**.
- ❌ *"o último de uma fila de quiques"* → **sem âncora.** **O último é o último ANTES DA MUDANÇA DE CAMPO.** *(ele tinha dito a âncora; eu apaguei-a)*

## 🔴 MAS A CONFIRMAÇÃO PELA BOLA **ERA ACASO** — e testei-a

```
a sequência dispara 181 vezes em 538 s   →   UMA A CADA 3,0 s
21 instantes AO ACASO "confirmam" ......... 18,4/21   (88 %)
os 21 blocos dos jogadores ................ 21/21    (100 %)
probabilidade de 21/21 por PURO ACASO ..... 6,4 %    🔴
```

> ## **Ia dar-lhe um «confirmado pelos dois sinais, 21/21» que era, quase todo, SORTE.**
> **Um dado que sai 6 em quase todas as jogadas não confirma nada quando sai 6.**

---

# 🔴 E A B19 GANHOU UM NÚMERO — e um NOME NOVO

**A imagem que ele mandou:** a bola está **em BAIXO**; o sistema deteta-a **em CIMA**, na **camisola branca** de um jogador do outro campo.

```
deteções que MUDAM DE CAMPO em ≤3 frames ............... 964
   ...com um salto > 100 px (fisicamente impossível) ...... 830   🔴 TELETRANSPORTE
tracklets num vídeo de 9 min ........................... 817   (a trajetória em MIGALHAS)
```

> ## 🚫 **B2 — A BOLA NÃO SE TELETRANSPORTA. E teletransporta-se 830 vezes.**
>
> ## ⚠️ **E NÃO É «O TRACKER SENTA-SE NUM TÉNIS».**
> ## **É: «o tracker salta para QUALQUER COISA BRANCA num jogador» — camisola, meias, ténis.**
> ## **E salta ATRAVÉS DA REDE.**
>
> *(A **B16** — «no limite inferior da box» — apanha só **49 %** do que está dentro das boxes.
> A **camisola** está **a meio**. ⇒ **a B16 tem de generalizar.**)*

⚠️ **E cortar «tudo o que está dentro de uma box» MATA O PRÓPRIO SERVIÇO** — o quique do serviço
acontece **aos pés do servidor**, ou seja **dentro da box dele** *(recall 21 → 14)*.
👉 **Falta a outra metade da regra: «e MOVE-SE COM a box».** A roupa **viaja com** o jogador;
a bola **ATRAVESSA-O**.

---

# 🏁 ONDE ISTO DEIXA O PROJETO

| | |
|---|---|
| ✅ **O DETETOR DE SERVIÇO** | **21/21, zero falsos, ZERO bola.** `detetor_servico.py` |
| ✅ **A S42 e a S43** | **DESTRAVADAS** — já não esperam pela bola |
| 🟡 **A S23-sequência** | **lei certa, escrita, medida.** À espera de **sinal limpo** |
| 🔴 **A B19** | **continua a ser a raiz da BOLA — mas já NÃO bloqueia o M3** |

---
---

# 🩸 A LIÇÃO DE HOJE

## **O erro não estava na regra. Estava na PERGUNTA que o código fazia à regra.**

A lei dele — *"está à frente da linha de serviço"* — estava **certa, escrita, e clara**.
O código perguntava outra coisa. **E a resposta errada saía com toda a confiança, sem partir nada.**

> # 🎬 **VÍDEO ANTES DE MÉTRICAS.** Ele encontrou-o **A OLHAR**. Não aparecia em número nenhum.
> # 📐 **GEOMETRIA > MODELO — mas só se a LINHA for A LINHA.**
> # 🧐 **CONFIRMAR A PREMISSA.** Hoje afirmei **três** coisas sem medir. **Caíram as três.**
