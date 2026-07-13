# ⚖️ PADELPRO VISION — A CONSTITUIÇÃO
### *(colar nas INSTRUÇÕES DO PROJETO. Carrega em TODAS as conversas.)*
### *Aqui só entra o que **NÃO MUDA**. O que muda vive em ficheiros — e diz-se ONDE.*

---

# 🧭 ANTES DE TUDO — os 4 comandos

```bash
cd padelpro-vision
python3 verificar_fonte.py     # 🐕 o GUARDA. Tem de dar ✅ FONTE LIMPA. Se der vermelho, PÁRA.
python3 teste_regressao.py     # 🔒 o ESTADO TRAVADO. Se falhar, a ALTERAÇÃO está errada — NUNCA o teste.
python3 ablacao.py             #    quanto vale CADA regra
python3 gerar_tempo_util.py --video
```
📖 **O estado de hoje está no `FECHO_13JUL.md`** *(ou no fecho mais recente)*.
**NÃO decores números. Corre o teste.** *(Números decorados apodrecem — foi assim que o
`MAPA_DAS_REGRAS`, os números de linha e o ground-truth do `docs/` começaram a mentir.)*

---

# 📍 ONDE VIVE A VERDADE

| | |
|---|---|
| **as REGRAS** | **`padelpro-vision/REGRAS_DO_VASCO.md`** — **a FONTE ÚNICA** |
| **o PIPELINE** | `padelpro-vision/gerar_tempo_util.py` |
| **o ESTADO TRAVADO** | `padelpro-vision/teste_regressao.py` |
| **o GROUND-TRUTH** | `padelpro-vision/data/ground_truth/` |
| **GUARDAR** | **duplo-clique no `GUARDAR_TUDO.command`** *(o Claude não mexe no `.git` — o macOS bloqueia)* |

⛔ **Só a pasta `padelpro-vision/` é um repo git — é a ÚNICA que vai para o GitHub.**
Um ficheiro na raiz **não é versionado**: se o Mac morrer, **perde-se**.
Qualquer `REGRAS_DO_VASCO.md` que encontres na raiz ou em `docs/` é um **PONTEIRO MORTO**.

🔑 **"RESSALTO" = "QUIQUE" = "BOLA NO CHÃO"** — três nomes, a mesma coisa. Se procurares só por
*"ressalto"* encontras as regras **bloqueadas** e concluis que **não funciona**. A que **funciona**
chama-se **"quique"**. **Procura pelos três.**

---

# 🛑 COMO TRABALHAR — NÃO NEGOCIÁVEL

### 1. ⛔ **NÃO AVANÇAS PARA NADA SEM PERGUNTAR.**
Propõe → espera → só depois faz. **Uma coisa de cada vez.** Não encadeies cinco passos porque "faz
sentido". **O Vasco decide o passo seguinte, não tu.**

### 2. ⛔ **NÃO INVENTAS ATALHOS.**
Nenhum número mágico. Os valores saem do `calibracao_campo.json` ou são **frações do meio-campo
local**. Se usares um atalho, **declara-o na MESMA mensagem em que dás o número.**

### 3. 🧪 **TESTAR, NÃO RACIOCINAR.**
Nunca descartes uma regra dele com um raciocínio bonito. **MEDE.**
*(Foram descartadas 8 regras a raciocinar. A que ia para o lixo resolveu o maior problema que havia.)*

### 4. 🎬 **VÍDEO ANTES DE MÉTRICAS.**
Todo o teste vem com um vídeo onde o Vasco veja. **Ele encontrou TODOS os bugs a olhar. Nenhum
apareceu nos números.**

### 5. 🚨 **DESCONFIA DO GROUND-TRUTH.**
Um falso positivo **bem-comportado** é **verdade que falta ao GT**. **Mostra o clip ANTES de o
combater.** *(O "falso" dos 289 s era um PONTO. A precisão andou um dia a castigar por ACERTAR.)*

### 6. ⚖️ **MEDIR ANTES DE CITAR.**
**Nunca declares uma regra dele morta a partir de um número que não verificaste.**
*(Custou duas regras — a S2 e a S30 — mortas com um "21,8%" que era um artefacto do `max_det=4`.)*

### 7. 🕳️ **LÊ O CÓDIGO, NÃO O MAPA.**

### 8. ⚖️ **AS REGRAS DO VASCO SÃO LEIS. OS NÚMEROS DO CLAUDE SÃO AJUSTES.**
**Nunca os apresentes com o mesmo estatuto.** As **leis** sobrevivem a outra câmara. Os **ajustes** não.

### 9. 🛑 **AS DEFINIÇÕES DO JOGO PARAM E PERGUNTAM.**
O que é *ponto*, *serviço*, *tempo útil* — **é dele.**

### 10. 📊 **CORRE A `ablacao.py` SEMPRE que entra uma regra.**
Uma regra nova pode tornar outra **redundante** — e continuar a defendê-la é mentir a nós próprios.
**Uma regra que vale `+0,0`: ou ficou redundante — ou NÃO CORRE.**

### 11. 👤 **O Vasco NÃO é developer.** Passo a passo. Uma coisa de cada vez.

---

# 🎯 A DIRETRIZ DE PRODUTO — **manda em tudo**

> ## **Nunca perder um ponto.**
> **Mais lixo é preferível a menos tempo útil. OTIMIZAR RECALL.**
> **E o tempo útil é para VER o ponto** — não para estatística.

---

# 🦠 A DOENÇA — **lê isto antes de acreditares em qualquer coisa**

> ## **Uma regra pode estar no mapa, com o nome certo, e fazer outra coisa.**
> ## **Um ficheiro pode chamar-se "a fonte", e ser uma cópia morta.**

Ela **não parte nada**: o pipeline corre, os números saem, **ninguém dá por nada**. Só aparece quando
alguém tropeça nela. **Em 13 jul mordeu TRÊS vezes:**

1. a **S12** marcada ✅, com o nome certo, **a fazer outra coisa** *(e a S8 ✅ e a não correr)*
2. **duas regras diferentes chamadas `S23`** — a que corre e a que nunca correu
3. **DEZ documentos duplicados**, 4 divergidos — incluindo o **ground-truth** *(uma cópia tinha 12
   rallies; a verdade tem 13)*

**E mordeu quem a estava a curar:** arrumaram-se 10 duplicados **e criaram-se 4 novos a seguir.**

## 🐕 A CURA: **`verificar_fonte.py`** — **CORRE-O. NÃO O REESCREVAS.**
```
① duplicados      → nome repetido FALHA (exceto se um for PONTEIRO)
                     ⚠️ "idêntico hoje NÃO é um estado — é uma contagem decrescente"
② ✅ que não corre → a função existe? é CHAMADA com TODOS os argumentos? o interruptor é LIDO?
③ ablação         → regra que vale +0,0 → AVISA
④ colisão de nomes → o mesmo ID de regra duas vezes
⑤ sinónimos       → RESSALTO = QUIQUE = BOLA NO CHÃO
⑥ 🐕 a COLEIRA    → o GT do código vs o GT do .md. Se divergirem, FALHA.
```
> **Um guarda que nunca dispara é indistinguível de um guarda que não existe.**
> Este foi testado contra as 4 doenças **reais**, injetadas numa cópia em `/tmp`. **Apanhou as quatro.**

---

# 🔁 AS 3 RELEITURAS — **antes de escreveres uma linha de código**

O guarda faz a 3.ª automaticamente. **As duas primeiras são tuas.**

**1.ª — verbal.** Lê o `REGRAS_DO_VASCO.md` inteiro. **Escreve a lista completa.**
*Esqueceste-te de alguma?* Se a lista for mais curta que o ficheiro, **volta atrás**.

**2.ª — verbal.** Lê **outra vez**. Classifica: ✅ **a correr** · 🔴 **por implementar** · ⛔ **via
fechada** *(com o porquê, em NÚMEROS)*. *Esqueceste-te de alguma?*

**3.ª — contra o CÓDIGO.** `python3 verificar_fonte.py`. Por cada regra ✅:
a função **existe**? é **CHAMADA com todos os argumentos**? **faz o que a regra diz** — ou só tem o **nome**?

> 🔑 **PORQUE SÃO TRÊS:** a 1.ª apanha o que **esqueceste** · a 2.ª o que **classificaste mal** ·
> a 3.ª o que **MENTIU**. **As duas primeiras são memória. A terceira é PROVA.**

---

# 🚨 UMA CANETA DE CADA VEZ

**Só UMA conversa toca no `gerar_tempo_util.py` de cada vez.**
As outras **leem, medem, criam ficheiros novos.** **Nunca editam.**

*(13 jul: duas conversas escreveram no mesmo ficheiro ao mesmo tempo. Deu certo **por sorte**. Da
próxima, uma apaga o trabalho da outra e o `teste_regressao` **continua verde** — porque as duas
alterações eram, isoladamente, válidas. **O git não protege disto: a última a gravar ganha, em silêncio.**)*

---

---

# 🎾 AS REGRAS DO MODELO — **as que CORREM**   *(batidas contra o código, 13 jul)*

> ## ⚖️ **AS REGRAS DO VASCO SÃO LEIS. OS NÚMEROS DO CLAUDE SÃO AJUSTES.**
> Uma **LEI** é uma verdade do **JOGO** — sobrevive a outra câmara, a outro campo, a outra luz.
> Um **AJUSTE** é um limiar afinado a **UM VÍDEO** — e o 2.º vídeo vai parti-lo.
> **Nunca os apresentes com o mesmo estatuto.**

O valor de cada uma é o que se **PERDE** ao desligá-la (`ablacao.py`).
**Nenhum destes números se decora — correm-se.**

| regra | a LEI (dele) | o AJUSTE (meu) | vale |
|---|---|---|---|
| **S15** MÃO vs RAQUETE | *"só dispara se a bola vier da **mão → chão → raquete**"*. A bola da **mão é LENTA**; a da **raquete é RÁPIDA**. | `L_RAQUETE=11` | **+19,8 precisão** ⭐ |
| **B14** VAI-E-VEM | se A→B é **longe** e A→C é **perto**, **B é ERRO**. *(tira o frame, **não parte a cadeia**)* | — | **+10,2 recall** |
| **B6** DIREÇÃO | *"dois cliques dão a direção"*. O `Theta` do BlurBall dá-a a **2°**, numa **ÚNICA** deteção ⇒ **costura os buracos**. | `TOL_THETA=35` | **+7,7 recall** |
| **S12** O FIM | o ponto acaba **4 s depois da ÚLTIMA PANCADA** — **não** do último cruzamento. *(a bola pode andar e já ter batido duas vezes)* | `SILENCIO=4` | **+6,8 recall** |
| **S16** DÚVIDA | **há pancada ⇒ SEI que acabou ⇒ corte RENTE (2 s).** **Não há ⇒ DÚVIDA ⇒ mais margem (5 s).** 🔒 **NUNCA INVERTER** *(já esteve, custou 12 pontos)* | `2 s / 5 s` | **+9,9 precisão** |
| **S13** TIMELINE | **nunca anda para trás.** Dois segmentos que se **tocam** **SÃO O MESMO PONTO**. | — | **+6,5 precisão** |
| **S17** 🔒 A REDE | *"se a bola **muda de direção** (ou **pára**) na rede, **LONGE de uma bounding box** → acabou"*. A que **passa** não vira; a que **bate**, vira ou morre. E se não há ninguém ao pé, **foi a rede**. 🔒 **"está perfeita! fixa e não deixes mudar."** | `RED_DTHETA=60` | **+5,0 precisão** |
| **S23** O QUIQUE DO SERVIÇO | **NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.** O **servidor** larga a bola → ela **QUICA** → e só **depois** bate. O **não-servidor** **passa-a à mão** ⇒ **SEM QUIQUE**. 🔑 *"mesmo com kick, **só o ÚLTIMO** antes de mudar de campo conta"* | `QUIQUE_PROF=0,7`<br>`QUIQUE_JANELA=3` | **+3,5 precisão** |
| **S20** A PAUSA | *"tem uma **média por dupla**, que vais notando"*. Uma pausa **curta demais é IMPOSSÍVEL** — têm de ir **buscar a bola**. ⇒ **a CAUDA do anterior está esticada.** **Aprende-se do próprio vídeo** (`mediana − 2,5×MAD`). 🔒 **chão: 4 s.** ⚠️ **só apara a cauda — NUNCA toca no início seguinte** ⇒ **incapaz de perder um serviço.** | `PAUSA_K=2,5` | **+1,8 precisão** |
| **B13** CRUZAMENTO PROFUNDO | de **fundo a fundo**. **Roçar a fita NÃO conta** *(é onde o ruído oscila)*. | `MIN_PROF=0,15` | **+1,3 precisão** |
| **S37** RAQUETADA COM JOGADOR | *"uma **raquetada** tem de ter um **jogador ao pé**"*. A 6 meios-campos de toda a gente, **ninguém lhe bateu: é RUÍDO.** | `PAN_DIST_MAX=3` | **+0,5** |
| **B15** A FAIXA CEGA | *"perto da rede devolvem a bola muito **alta e perto** — não dá tempo de passar"*. ⚠️ **ANDA COM A S23** — ampliar sem ela traz lixo. | `MIN_PROF 0,35→0,15` | *(ver S23)* |
| ⚠️ **S18** MÃO PARADA | *"bola **PARADA** dentro da box, **SEM MUDAR DE CAMPO** ⇒ acabou, sem raquetada"*. 🔒 **duração 0,5 s NÃO SE BAIXA** *(a 0,3 s o recall cai para 82 — é a duração que separa a **MÃO** do **LOB**)* | `MAO_L=3` | **+0,0** ⚠️ **redundante NESTE vídeo** (a S17 e a S23 já matam os mesmos fins). **Fica LIGADA** — noutra câmara pode ser ela a segurar. |

## 🔒 O QUE NÃO SE MEXE — **ordens dele, medidas**
- **S17 (a rede)** — *"está perfeita! fixa e não deixes mudar."*
- **`fim_dentro = 0`** — um "fim certo" **NUNCA** cai a meio de um ponto. **Se subir: DESLIGA a regra. NUNCA relaxes o teste.**
- **S16** — **nunca inverter.** · **S18** — **0,5 s não se baixa.** · **pausa** — **chão de 4 s.** · **bola** — `thr = 0.4`.
- **S23 + `MIN_PROF=0,15` andam JUNTAS.** Desligar uma sem repor a outra ⇒ **1 segmento falso**.

---

# 🔴 AS REGRAS DELE QUE **AINDA NÃO CORREM** — *(e é aí que está o trabalho)*

| | | bloqueada por |
|---|---|---|
| **S2 / S3** | **formação de serviço** *(um na rede + um atrás ⇒ eles **servem**; os dois atrás ⇒ eles **recebem**)*. A formação de uma dupla **DEDUZ** a da outra. | 🟢 **nada — foram REABERTAS.** Vivem em `padelpro/modules/servico.py` e **nunca foram ligadas.** |
| **S4 · S10** | o serviço cai no **quadrado CRUZADO** · é a **única** jogada que ressalta dos **DOIS lados** | o ressalto **fora** do serviço |
| **S6** | **alternância de lado** ⚠️ **NÃO é lei** *(no ponto de ouro quem recebe escolhe)* ⇒ **PONTUA** | por implementar |
| **S30** | **4 visíveis + ~3 s parados ⇒ confirma o fim.** *"Se não vires todos, **NÃO ADIVINHES**."* | 🟢 **REABERTA** |
| **J1→J5** | 🦶 **pés no polígono** *(inclui os **espaços laterais** — o **jogo exterior é LEGAL**)* → 👥 **2 por lado** → 👀 **os 2 de cima estão SEMPRE visíveis** → 🔗 **CONTINUIDADE** *(**não é filtro: PREENCHE**)* → 🛡️ **de baixo invisíveis ⇒ estão em DEFESA** *(**a ausência É o sinal**)* | **nenhuma corre.** ⚠️ **1 e 2 LIMPAM; 3, 4 e 5 ACRESCENTAM. Nenhuma descarta o frame.** |
| **J6+ · J10 · J9** | seguir o jogador pela **COR da roupa** *(o detetor só ARRANCA)* · ⚠️ **a camisola muda UMA de cada vez** *(a salvaguarda!)* · aprender as cores **no início de cada ponto** | J9 🟢 **desbloqueada** — o M1 dá **13/13 serviços** |

⚠️ **`padelpro/modules/servico.py` NÃO SE APAGA.** Parece morto (ninguém o importa) — **mas tem
regras dele que nunca correram.** *(Ao contrário do `m1_tempo_util.py`, que era só uma cópia velha.)*

---

# ⛔ VIAS FECHADAS — **MEDIDAS. Não repetir.**

| | porquê, em números |
|---|---|
| **S8** *(fim = última pancada antes do serviço seguinte)* | 98,9 / **47,1** — sem M3, as pancadas do **INTERVALO** esticam cada ponto até ao seguinte |
| **S14** *(duplo quique = fim)* | **49 falsos** a meio de pontos |
| **"virou longe de box ⇒ acabou"** *(a S17 generalizada)* | **74 fins a meio de pontos**, recall **40**. É a **PAREDE** e o **CHÃO**. |
| **S21** *(alternância das travessias)* | **redundante** — 0 grupos de intervalo. E o **ACE** é um ponto real com **UMA** travessia ⇒ como veto, **mata pontos**. |
| **S19** *(2 toques)* | a **PAREDE** confunde-se com a raquete |
| **ler a travessia pelo TOPO da rede** | **certo, mas nulo** — as duas linhas estão a 35 px, **ambas dentro da faixa cega** |
| **VIDRO DO FUNDO** | **é o CÉU** — e **não se resolve desenhando** *(bons e maus têm a mesma distribuição de alturas)* |
| **BOLA SAI DE CAMPO** | ⛔ **o Vasco matou-a: há JOGO EXTERIOR** |
| **JOGADOR TOCA NA REDE** | a box dos **PÉS** não vê a **RAQUETE**. Precisa de **pose**. |
| **régua local aplicada à BOLA** | **A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96 → **32** |
| **fine-tune do YOLO da bola** | `best_v2` ficou **pior** |
| **auto-detetar o campo** | a linha de serviço saiu **40 px** ao lado |
| **`max_det=4` nos jogadores** | ordena por **CONFIANÇA** — um espectador nítido **ganha** a um jogador cortado. 🔑 **O critério é a GEOMETRIA: os PÉS no polígono.** |

> ### 🚪 **O BLOQUEIO ÚNICO: distinguir RAQUETE / PAREDE / CHÃO.**
> **Quatro regras dele param na mesma porta.** O `ressaltos()` já resolve **o CHÃO** (inversão
> **VERTICAL**) — falta a **PAREDE** (inversão **HORIZONTAL**) e a **RAQUETE** (**com jogador ao pé**).
> 🔊 **E o ÁUDIO resolvia as três de uma vez:** o som do **quique**, o da **parede** e o da **raquete**
> são **três sons diferentes**. **O áudio não precisa de profundidade.** — **GRAVAR COM ÁUDIO.**

---

---

# 📐 O CAMPO — **A CALIBRAÇÃO É A RÉGUA DE TUDO**   *(e é a 1.ª coisa do vídeo novo)*

> **Um erro aqui envenena TUDO o que está por baixo — e não dá erro. Dá números errados em silêncio.**

| | |
|---|---|
| **C1** 🔒 | **CAMPO NOVO = CALIBRAÇÃO NOVA, À MÃO**, no `calibrar_campo.html`. ⛔ **NÃO AUTO-DETETAR** *(a auto-deteção pôs a linha de serviço **40 px** ao lado)* |
| **C2** | **a malha 2/3 NUNCA se deteta** — não é linha branca. **Desenha-se sempre.** |
| **C3** | **a central CALCULA-SE** (pontos médios das linhas de serviço + base da rede). **Não se marca.** |
| **C4** | os **extremos das linhas são os cantos** ⚠️ **descartar os que tocam a BORDA DO FRAME** — a borda **não é o vidro** |
| **C5** | **3 pontos = curvatura · 2 pontos = herdam-na.** A lente **curva** as linhas. |
| **C6** | **a câmara é FRONTAL** — fixa, **atrás do vidro de fundo**, a meia altura. **É o pressuposto de todo o sistema.** |
| **C11** | **o campo é 20 × 10 m.** É a régua de todas as conversões. |
| **C9** | ✏️ **ANOTA POLILINHAS, NÃO PONTOS.** *"Os cantos desaparecem; **as linhas não**."* |
| **C10** | 🔭 **A DISTORÇÃO DE LENTE NÃO É OPCIONAL.** Sob distorção de barril, **uma homografia planar é matematicamente incapaz** de bater certo em todo o campo. |

### 🦶 E O POLÍGONO DOS JOGADORES — **duas regras que mordem no vídeo novo**
| | |
|---|---|
| **J15** | 🔲 **O POLÍGONO DESENHA-SE LARGO, NÃO APERTADO.** *"Se ficar apertado, corta jogadores encostados ao vidro."* ⚠️ **INCLUI OS ESPAÇOS LATERAIS — o JOGO EXTERIOR é jogo LEGAL.** *(Foi por isto que se matou a regra "bola sai de campo = fim".)* |
| **J14** | 🎣 **DETETAR GENEROSAMENTE, LIMPAR PELA ESTRUTURA.** `CONF` **baixo** + `IMGSZ` **alto**; **as regras do JOGO é que limpam** — não um limiar do detetor. ⛔ **É por isto que o `max_det=4` está errado:** ele ordena por **confiança**; o critério certo é a **GEOMETRIA (os pés no polígono)**. |

⚠️ **A calibração e o ground-truth são POR VÍDEO.** Nunca escrever por cima da do Parada4 — **é a base
do `teste_regressao`.** Campo novo ⇒ `calibracao_<video>.json`, **ficheiro NOVO**.

---

# ⚪ AS REGRAS DA BOLA QUE TAMBÉM CORREM

| | a LEI (dele) |
|---|---|
| **B1** | **objetos imóveis não são a bola.** *"A bola nunca pousa duas vezes no mesmo sítio."* |
| **B2** | **a bola não se teletransporta.** 🔑 **LEI: a bola de padel não passa dos 180 km/h** ⇒ `VMAX=70 px/frame` *(era 90, inventado — que ao fundo do campo permitia **710 km/h**)*. ⚠️ **e é um parâmetro MORTO**: quem trabalha é a **costura por Theta (B6)**. |
| **B2b** | ⚠️ **A RÉGUA É DO CHÃO. A BOLA VOA.** O meio-campo local vale para os **PÉS** e os **RESSALTOS**; **NÃO** para a bola em voo *(aplicá-lo à bola: recall 96 → **32**)*. **A régua do chão dá um MÍNIMO, não um máximo.** |
| **B7** | **bola fora > 2 s ⇒ vem aí um serviço** |
| **S1** | a **zona de serviço** aprende-se **dos dados** *(bola no chão junto a um jogador atrás da linha)* |
| **S5** | **o serviço é MULTI-FATOR.** **Nenhum sinal sozinho chega. Combinar.** |

---

# 🚨 A ARMADILHA DOS JOGADORES — **"✅" no mapa, mas NÃO CORREM no pipeline**

**As regras J2, J3, J4, J7, J8** estão marcadas **✅ implementadas** — e estão. **Em `padelpro/modules/servico.py`.**
**Que o pipeline do tempo útil NÃO IMPORTA.**

> ## **"Implementada" ≠ "a correr".**
> **O pipeline dos 96,8% usa SÓ A BOLA.** As boxes dos jogadores servem apenas para responder a
> *"havia alguém ao pé?"* (S37, S17, S18).

⚠️ **`servico.py` NÃO SE APAGA** — parece morto (ninguém o importa), **mas tem regras dele que nunca
correram**. *(Ao contrário do `m1_tempo_util.py`, que era só uma cópia velha do que já corre.)*
**Pôr a cascata J a correr é trabalho por fazer, não trabalho perdido.**

---

---

# 🔎 AS OUTRAS QUE CORREM — *(menos visíveis, igualmente vivas)*

| | |
|---|---|
| **P5** | 🔎 **A PANCADA, EM CÓDIGO:** a bola **aproxima-se** da box (mínimo local) **e depois a trajetória MUDA** (afasta-se noutra direção). **Não é a proximidade — é a proximidade SEGUIDA de mudança.** |
| **S33** | 🎾 **VALIDADE DO SERVIÇO:** ✅ **válido** = cai no quadrado **CRUZADO** sem tocar na malha · 🔄 **LET** = toca na fita **e cai dentro** · ❌ **falta** = o resto |
| **D6** | ✅ **AUTO-VERIFICAÇÃO ANTES DE EMITIR.** Os totais batem certo? `fim > início`? Sem sobreposições? **Verifica ANTES de mostrar.** |
| **F2 · F3** *(M2)* | 🧱 a fase é da **EQUIPA**, pela **regra das DUAS BOXES** *(só é DEFESA se estiverem **ambos** atrás)* · 📍 **a posição é a ARESTA INFERIOR da box** (o contacto com o **solo**) — **nunca** a cabeça, o tronco ou a raquete |

---

# 📖 E ESTA CONSTITUIÇÃO **NÃO SUBSTITUI** O `REGRAS_DO_VASCO.md`

**São 117 regras.** Aqui estão **as que mandam no dia-a-dia** — as que correm, as que estão fechadas,
e as leis que não se negoceiam. **As outras estão lá. Vai lá lê-las.**

---

---

# ⚖️ AS LEIS DE DESENHO — **D1 a D18.**   *(as mais valiosas e as mais invisíveis)*

**Estas não são tarefas. São como se PENSA.** Valem para tudo o que se fizer neste projeto.

| | |
|---|---|
| **D1** | 🤔 **EM DÚVIDA, MANTÉM O ESTADO ANTERIOR.** O estado tem **INÉRCIA** (histerese). ⚠️ **É o antídoto para o JITTER** — o inimigo nº 1 do M2. |
| **D2** | 🚫 **NÃO INVENTAR. SE NÃO ANCORA NUM EVENTO VISUAL CLARO, OMITE.** *(Escrita pelo Vasco há um mês. **É a lei que rege o projeto todo.**)* |
| **D3** | 📏 **PRECISÃO HONESTA.** *"Não finjas precisão absoluta."* Incerteza grande ⇒ **diz que é grande.** |
| **D4** | 🗣️ **A DÚVIDA TEM NOME.** Não consegues classificar? ⇒ **`indeterminado`.** Não inventes uma categoria. |
| **D5** | 👁️ **OBSERVAR ANTES DE CLASSIFICAR.** O raciocínio vem **ANTES** da resposta — nunca a justificar uma resposta já dada. |
| **D6** | ✅ **AUTO-VERIFICAÇÃO ANTES DE EMITIR.** Os totais batem certo? `fim > início`? Sem sobreposições? |
| **D7** | 🚫 **NUNCA OMITIR UM *RALLY*** *(≠ omitir um EVENTO)*. Ambíguo ⇒ **marca `confiança: baixa`** — mas **não o deites fora.** |
| **D8** | 📉 **`confiança` 0,0–1,0 em cada entrada.** Incerteza **explícita**, não escondida. |
| **D9** | 🎣 **RECALL PELA DETEÇÃO · PRECISÃO PELA ESTRUTURA.** **Detetar generosamente; limpar com as REGRAS DO JOGO** — nunca com um limiar do detetor. |
| **D10** | 📐 **GEOMETRIA > MODELO.** *"Sempre que algo se reduz a **comparar posições com linhas**, faz-se com **geometria** — não com um modelo."* ⚠️ **É a lição do `max_det=4`:** ele ordenava por **confiança** quando o critério certo era **os pés no polígono.** |
| **D11** | 🩼 **AS REGRAS DE GAP ERAM MULETA DO DETETOR FRACO.** Com um detetor forte, o que separa é a **ESTRUTURA**, não o buraco. |
| **D12** | 🛑 **"NÃO ESCREVER MAIS REGRAS. MELHORAR O SINAL."** ⚠️ **É o contrapeso de tudo isto.** Quando as regras já dão 0 falsos e o problema continua, **o problema é o SINAL** — não faltam regras. |
| **D13** | 📊 **FAIXA FINA = OBSERVÁVEL · ÁREA GRANDE = AMBÍGUA.** A rede (35 px) funciona; o vidro (meio ecrã) não. **Serve para prever se uma ideia tem hipótese ANTES de a testar.** |
| **D14** | 🤝 **DUAS LEITURAS INDEPENDENTES; SE SE CONTRADIZEM, NÃO INVENTA.** *(Diz que não sabe.)* |
| **D15** | 🔒 **UM "FIM CERTO" NUNCA PODE CAIR A MEIO DE UM PONTO** (`fim_dentro = 0`). **Se subir: DESLIGA a regra. NUNCA relaxes o teste.** É o **pior erro possível**. |
| **D16** | ➕ **SINAIS INDEPENDENTES SOMAM.** A bola e os jogadores **não competem — SOMAM.** |
| **D17** | 🧐 **CONFIRMAR A PREMISSA ANTES DE ACEITAR A CONCLUSÃO.** *(Uma conclusão bonita em cima de uma premissa não verificada é como se perderam duas regras hoje.)* |
| **D18** | ⚖️ **NENHUMA REGRA DO JOGO PODE VETAR UM CANDIDATO.** Há sempre uma **exceção legítima** (ponto de ouro, tie-break, let). **Todas PONTUAM. Nenhuma CORTA.** Escolhe-se a **sequência globalmente mais consistente**. |

---

# 📚 E O RESTO — **69 regras POR IMPLEMENTAR** *(o M2, o M3, as pancadas, a cor)*

**Não estão aqui de propósito.** Isto é a **constituição**, não o inventário.
👉 **Estão TODAS em `REGRAS_DO_VASCO.md`.** *(B3-B12 · C7-C12 · F1-F12 · J11-J13 · P1-P6 · S7, S9,
S11, S22, S24-S26, S29, S31-S41.)*

> **Se vais trabalhar numa área, VAI LÊ-LAS PRIMEIRO.** É o que a **1.ª e a 2.ª releitura** existem
> para garantir. **Não assumas que sabes o que lá está.**

---

# 📐 AS 8 LIÇÕES QUE CUSTARAM MAIS CARO   *(as que se pagaram em DIAS)*

1. 🏃 **SÓ O QUE SE CORRE É QUE CONTA.** Nunca dizer *"está feito"* a partir de uma lista de ficheiros.
   **Correr. Ver o vídeo. Medir.**
2. 📊 **FAIXA FINA = OBSERVÁVEL · ÁREA GRANDE = AMBÍGUA.** A rede (35 px) funciona; o vidro (meio ecrã)
   não. **Serve para prever se uma ideia tem hipótese ANTES de a testar.**
3. ⚠️ **NADA EM PÍXEIS ABSOLUTOS SOBREVIVE À PERSPETIVA.** O meio-campo longe tem 100 px; o perto, 290 —
   para os **mesmos 6,95 m**. **Todas as tolerâncias = frações do meio-campo local.**
4. 🎾 **A RÉGUA É DO CHÃO. A BOLA VOA.** O meio-campo local vale para os **pés** e os **ressaltos**;
   **NÃO** para a bola em voo. *(Aplicá-lo à bola: recall 96 → 32.)*
5. ⚖️ **NENHUMA REGRA DO JOGO PODE VETAR UM CANDIDATO.** Há sempre uma exceção legítima (ponto de ouro,
   tie-break, let). **Todas PONTUAM. Nenhuma CORTA.**
6. 🚫 **NÃO INVENTAR. SE NÃO ANCORA NUM EVENTO VISUAL CLARO, OMITE.** *(Lei do Vasco, escrita há um mês.)*
7. 🔒 **UM "FIM CERTO" NUNCA PODE CAIR A MEIO DE UM PONTO** (`fim_dentro = 0`). Se subir: **DESLIGA a
   regra. NUNCA relaxes o teste.** É o pior erro possível.
8. 🔑 **NÃO SE AFINA O DETETOR — MUDA-SE A PERGUNTA.** *(O ressalto falhou meses a perguntar "há dois
   quiques?" em toda a parte. Acertou 13/13 à primeira quando lhe perguntámos "há um quique FUNDO, na
   LINHA DE SERVIÇO, nos 3 s antes do ponto?". **O detetor era o mesmo.**)*
