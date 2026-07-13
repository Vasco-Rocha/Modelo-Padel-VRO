# As regras do Vasco — inventário completo

> # 📍 **ESTE É O ÚNICO FICHEIRO. A FONTE ÉNICA.**
> **Vive em `padelpro-vision/REGRAS_DO_VASCO.md`** — dentro do repo, **é o único que vai para o
> GitHub**. Qualquer outro `REGRAS_DO_VASCO.md` que encontres (na raiz, em `docs/`, em `snapshots/`)
> é uma **CÓPIA MORTA** ou um **ponteiro**. **Não escrevas neles.**
> *(13 jul: havia **DUAS** fontes vivas a divergir. Duas conversas escreviam em ficheiros diferentes,
> cada uma convencida de que era a verdade. A S23 existia numa e não na outra. **Nunca mais.**)*

---

> # 🔴 LÊ ISTO ANTES DE PROCURAR: **"RESSALTO" = "QUIQUE" = "BOLA NO CHÃO"**
> **São TRÊS NOMES PARA A MESMA COISA.** Se procurares só por um deles, **encontras a metade errada.**
>
> | procuras por... | encontras... | e concluis (ERRADO) |
> |---|---|---|
> | **"ressalto"** | a **S9**, a **S14**, a **S36** — falam todas de **bloqueio** | *"o ressalto não funciona"* |
> | **"quique"** | a **S23** — ✅ **A CORRER, 13/13, no pipeline** | **a verdade** |
>
> ## ✅ **O DETETOR DE RESSALTO EXISTE, FUNCIONA, E ESTÁ NO PIPELINE.**
> - a função: **`ressaltos()`** em **`gerar_tempo_util.py`** *(o `ressalto.py` importa-a — **uma só definição**)*
> - a regra: **`quique_do_servico()`** — a **S23**
> - o interruptor: **`REGRAS["S23_QUIQUE_SERV"]`**
> - acerta **13/13 quiques do serviço** · e sozinho gera **candidatos a serviço com 100 % de recall**
>   (`m3_candidatos.py`) ⇒ **o M3 arrancou.**
>
> ### 🔑 **NÃO SE AFINOU O DETETOR. MUDOU-SE A PERGUNTA.**
> - ❌ **S9 / S14** perguntam *"há um (ou dois) quiques?"* — **em qualquer sítio, a qualquer hora**.
>   Aí o **CHÃO**, a **PAREDE** e a **RAQUETE** confundem-se ⇒ **49 falsos**. **Continuam bloqueadas.**
> - ✅ **S23** pergunta *"há um quique **FUNDO**, na **LINHA DE SERVIÇO**, nos **3 s ANTES** da 1.ª
>   travessia?"* — **um sítio, um instante, um ritual** ⇒ **13/13, zero falsos.**
>
> > **FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA** *(D13)*.
> > **O ressalto nunca esteve estragado. Estávamos a apontá-lo para o sítio errado.**

Todas as regras que vieram do Vasco, o que fazem, e onde estão.
**As melhores ideias do projeto vieram daqui.** Não perder nenhuma.

Última atualização: **13 jul 2026 — auditoria COMPLETA dos prompts originais (v1 → v9) + `docs/`.**

> ## ✅ AUDITORIA FECHADA
> Lidos, **inteiros**, os **9 prompts** (v1 · v3 · v7.1 · v7.7 · v8.0 · v9×4) + `REGRAS_BOLA_PARA_CODIGO`
> + `AFINAR_*` + `PLANO_*` + os **18 ficheiros** de `padelpro-vision/docs/`.
> **Nada ficou por ler.** Detalhe e citações: `REGRAS_PERDIDAS_v2_dos_originais.md`.
>
> **+38 regras novas** · **5 contradições** com o código/inventário · **1 achado grande**: a **S21**.
>
> 🚨 **5 CONTRADIÇÕES — não mexi em nada, decides tu:**
> ① a **C6** (câmara "lateral") estava **errada** → corrigida para **FRONTAL**
> ② a **ordem da cascata** dos jogadores estava **trocada** → o *2-por-lado* é o **ÚLTIMO**
> ③ o **serviço** é **ATAQUE** (v1/v3) ou **TRANSIÇÃO** (v9)? — os prompts contradizem-se
> ④ `min_rally_s` **descarta** rallies curtos; o v3 diz **"não omites rallies curtos"** — e o **ponto 1 do GT tem 3,5 s**
> ⑤ **duas regras chamadas B8** (coerência temporal *vs* vai-e-vem) — a doença da S12 outra vez

---

## BOLA

| # | Regra | Estado | Onde |
|---|---|---|---|
| B1 | **Objetos imóveis** — um objeto no mesmo píxel, espalhado por >35% do vídeo, não é a bola. A bola nunca pousa duas vezes no mesmo sítio. | ✅ implementada. Apanha 4 objetos. **Sobe a precisão sem custar recall.** | `filtrar_objetos_imoveis()` |
| B2 | **Continuidade** — a bola não se teletransporta. Salto impossível = outro objeto. **LEI DO VASCO (13 jul): a bola de padel não passa dos 180 km/h.** ⇒ 1,67 m/frame ⇒ **70 px/frame** no meio-campo mais perto (291 px = 6,95 m). *(Estava `VMAX=90`, inventado — que ao fundo do campo permitia **710 km/h**.)* | ✅ **derivado (13 jul)**. ⚠️ **mas é um parâmetro MORTO**: de 60 a 117 px os números não mexem. Quem trabalha é a **costura por Theta**. | `gerar_tempo_util` |
| **B2b** | ⚠️ **A RÉGUA É DO CHÃO. A BOLA VOA.** ⛔ **NÃO** aplicar o meio-campo local (no `y` da bola) para a limitar: uma bola **alta e à frente** aparece nos mesmos píxeis que uma bola **rasteira ao fundo**, e a régua do fundo (23 px/frame) **corta-lhe a cadeia**. Testado: **recall 96,2 → 32,1**. E o "pior caso do chão" (70 px) também não chega para a **costura**: a bola a 3 m de altura está **mais perto da câmara que qualquer ponto do chão**, logo aparece **maior**. **A régua do chão dá um MÍNIMO, não um máximo.** ⇒ vale para os **PÉS** e os **RESSALTOS** (que estão no chão), **não** para a bola em voo. | 🔴 **LIÇÃO NOVA (13 jul)** — o reverso da lição da perspetiva. `VMAX_THETA=140` = **2 × VMAX**; o "2" é o **fator da altura**, e **não é derivável só da calibração** (faltaria a altura da câmara). | — |
| B3 | **Velocidade por 2 frames** — a velocidade da bola calcula-se em 2 frames, não em 1. | 📋 por implementar | — |
| B4 | **Estados da bola** — a bola tem estados (no ar, no chão, na mão, parada). | 📋 por formalizar | — |
| B5 | **Cima vs baixo** — a bola alta e a bola rasteira são coisas diferentes. | 📋 por formalizar | — |
| B6 | **2 cliques = direção** — dois pontos dão a direção (o BlurBall já dá `L` e `Theta`). | ✅ **RESOLVIDO — e melhor do que pedias**: o `Theta` dá a direção com **2° de erro numa ÚNICA deteção**, sem precisar de dois pontos. **+10,2 recall e +2,5 precisão** no M1 (74,1/66,6 → **84,3/69,1**). Estava no CSV desde o 1.º dia. | **`gerar_tempo_util.erro_theta()`** + **`.tracklets()`** · interruptor `REGRAS["B6_THETA"]` |
| B7 | **Bola fora >2s = serviço** | ✅ nas regras v9 | — |
| B8 | **Coerência temporal** — uma deteção sozinha, sem vizinho compatível em ±2 frames (raio 45px/frame), é lixo. *"Confirmar com um antes e um pós."* Apanha os ténis brancos e os pontos brancos no público. | 🧪 **testada 12 jul**: mata 275 frames de lixo por 99 de rally (2,8:1). Custo no recall: -2,8 pp. **Vale a pena.** | por implementar |
| B9 | **Não inventar perto dos cegos** — ao contrário dos jogadores, na bola **não se interpola** por cima de buracos. Ausência é ausência. | 📋 por implementar | — |
| B10 | **`L` ≈ 0 é suspeito** — a bola em jogo está borrada; um ténis parado não. Medido: L mediana 2,5 / p90 12,4. **Sinal fraco isolado** (34% das deteções têm L<2), só serve combinado com B8. | 🧪 medido, não conclusivo sozinho | — |

| **B11** | 🚫 **A bola fora do ENQUADRAMENTO NÃO termina o rally** (lob alto, bola ao fundo). *"«Inatividade» refere-se a **PANCADAS e JOGADORES**, **nunca** à bola estar fora do frame."* (v9 M1.4 · R4) | ⚠️ **parcial** — existe como `zonas_cegas_y`/`gap_zona_cega_s`, mas **não está escrita como lei** | `rallies_bola.py` |
| **B12** | ⏳ **Ausência de bola só é CANDIDATA a fim se durar >2 s *E* for seguida de um SERVIÇO.** Se a pancada seguinte não for serviço, **é o MESMO rally**. (v9 M1 2b/3) | 📋 por implementar (depende do M3) | — |
| **B13** | 🥅 **Cruzamento PROFUNDO** — a bola tem de ir de fundo a fundo; **roçar a fita não conta**. | ✅ implementada | `gerar_tempo_util.cruzamentos()` |
| **B15** | 🕳️ **A FAIXA CEGA À VOLTA DA REDE** *(Vasco, 13 jul: "os de cá, perto da rede, devolvem a bola muito **alta e perto da rede** — não dá tempo à bola de passar, nos frames")*. O `MIN_PROF` ignorava tudo num raio de **35 % do meio-campo** à volta da rede ⇒ o **VOLLEY à rede** atravessava e **morria lá dentro, invisível**. **O código via 52 % das travessias.**<br>⛔ **Ler a travessia pelo TOPO da rede (em vez da base) está CERTO mas é quase nulo** — as duas linhas estão a 35 px, **ambas dentro da faixa cega**. Quem trabalha é a **LARGURA**, não o divisor. | ✅ **`MIN_PROF` 0,35 → 0,15 (13 jul).** ⚠️ **SÓ porque a S23 mata o lixo que isto trazia. AS DUAS ANDAM JUNTAS** — ampliar sem a S23 traz um segmento falso. **Tira os pontos 10 e 11 de cima de uma travessia ÚNICA** (1→3): medido, **tirar essa travessia ⇒ O PONTO DESAPARECE**. | `gerar_tempo_util` |
| **B14** | 🔄 **Vai-e-vem** — se A→B é longe e A→C é perto, **B é erro**. *(Estava marcada como "B8" no `MAPA_DAS_REGRAS.md` — **colisão de nomes** com a B8 real. Renumerada.)* | ✅ implementada | **`gerar_tempo_util.vai_e_vem()`** · interruptor `REGRAS["B14_VAI_E_VEM"]` *(chamava-se `B8_VAI_E_VEM` até 13 jul — renomeado)* |

> ⛔ **B-nota (12 jul):** **45% das deteções de bola caem FORA dos rallies — e são bola A SÉRIO** (o intervalo entre pontos: apanhar, passar, preparar). **Nenhuma regra de bola resolve isto.** Só o M3. Ver `project_threshold_04_fechado`.
>
> ✅ **CORREÇÃO (13 jul, auditoria dos originais):** *nenhum **DETETOR** resolve* — mas a **S21
> (alternância das travessias)** não é um detetor, é uma **estrutura**: a bola do intervalo **não faz
> vaivém pela rede**. **Estava escrita no `SPEC_M1_TEMPO_UTIL.md` e nunca correu.**

---

## JOGADORES

| # | Regra | Estado | Onde |
|---|---|---|---|
| J1 | **Fora do campo** — os pés de um jogador **nunca** passam para lá do vidro. No máximo vão aos espaços laterais. Tudo o que tenha os pés fora **não é jogador**. | ✅ implementada. Descarta o espectador que era a deteção **mais frequente do vídeo** (32% dos frames). | `Campo.dentro_do_campo()` |
| J2 | **Imóveis (jogadores)** — um jogador **move-se**; um espectador **não**. | ✅ implementada, **com a tua salvaguarda** (ver J3) | `filtrar_espectadores()` |
| J3 | **Salvaguarda dos imóveis** — a regra só pode matar quem está **fora** do campo. Quem está **dentro é IMUNE**. Por construção, nunca pode matar um jogador — parado ou não, de cima ou de baixo. | ✅ implementada. **Resolveu um bug que estava a matar os jogadores do fundo.** | idem |
| J4 | **2 por lado** — são sempre **2 contra 2**. No máximo 2 de cada lado da rede. É uma verdade do **jogo**, não um threshold. Como limpa o excesso, deixa **baixar o `CONF`** do detetor sem pagar precisão. | ✅ implementada | `dois_por_lado()` |
| J5 | **Continuidade (jogadores)** — um jogador não se teletransporta **nem desaparece a meio do ponto**. Visto no frame 100 e no 104 → **interpola** 101-103. **A única regra que ACRESCENTA informação.** | ✅ implementada | `continuidade_jogadores()` |
| J6 | **Cor da roupa** — se uma camisola apareceu demasiadas vezes, só pode voltar a ser essa. Assinatura por **torso + calções + pernas + ténis**. Identidade **sem depender dos pés**. | ✅ implementada (a testar) | `assinatura()` no script |
| J7 | **Permissão para os de baixo** — a câmara não vê o fundo perto. Se a box toca a borda de baixo, **aceita-se sem testar pés nem laterais**. Não sabemos *onde* está; sabemos que está **em baixo**, e chega. | ✅ implementada (12 jul) | `Campo.dentro_do_campo()` |
| J8 | **Pés cortados ⇒ fundo perto ⇒ DEFESA** — a informação não se perde, **muda de forma**. | ✅ implementada | `Campo.zona()` |
| **J9** | **Cor reiniciada por ponto** — aprender as cores no **início de cada ponto** (jogadores separados, parados, em formação = **o frame mais limpo do jogo**). | 🟢 **DESBLOQUEADA (13 jul)!** Estava ⛔ por **dependência circular** (precisava de saber onde começam os pontos). **JÁ NÃO É CIRCULAR: o M1 dá 13/13 serviços.** Sabemos onde cada ponto começa, **treze vezes**. **PRONTA A IMPLEMENTAR.** | — |
| **J12** | 👕 **A assinatura visual tem CINCO elementos: camisola · calções · MEIAS · ténis · RAQUETE.** (v1 §1, v3 P2) ⚠️ A **J6** escreveu *"torso+calções+pernas+ténis"* e **perdeu as MEIAS e a RAQUETE** — e a raquete é o que **não muda** quando o jogador troca de camisola. | 🔴 por implementar (com a J6+) | — |
| **J13** | 🔀 **Jogadores parecidos ⇒ distingue pela COMBINAÇÃO dos restantes fatores.** *"Se dois jogadores tiverem elementos similares, usa a combinação dos restantes."* (v1 §1) | 🔴 por implementar | — |
| **J14** | 🎣 **Detetar GENEROSAMENTE, limpar pela ESTRUTURA.** `CONF` baixo + `IMGSZ` alto; as regras do jogo é que limpam. → **"RECALL pela DETEÇÃO, PRECISÃO pela ESTRUTURA."** (`docs/HANDOFF_JOGADORES.md`) | ✅ é a arquitetura | — |
| **J15** | 🔲 **O polígono do campo desenha-se LARGO, não apertado.** *"Se ficar apertado, corta jogadores encostados ao vidro — e a diretriz é nunca perder um jogador. **Melhor largo do que apertado.**"* (`docs/GUIA_COLAB_JOGADORES.md`) | ✅ | `poligono_campo.json` |

---

## 🔴 A CASCATA DOS JOGADORES — a ORDEM importa   *(Vasco, 13 jul 2026, depois de ver as boxes do repo do João)*

> ## 🚨 CORREÇÃO (auditoria 13 jul) — **A ORDEM ABAIXO ESTAVA TROCADA.**
> O `docs/HANDOFF_JOGADORES.md` diz, e diz **porquê**:
> > *"**1.** fora do campo + imóveis → **2. CONTINUIDADE** → **3. dois por lado**.
> > A continuidade tem de vir **antes** do «2 por lado»: **se cortarmos primeiro, podemos deitar fora
> > o jogador verdadeiro e ficar com o falso.**"*
>
> ⇒ **O «2 POR LADO» É O ÚLTIMO, NÃO O SEGUNDO.** Primeiro limpa-se o que está **fora**, depois
> **preenche-se** o que falta, e **só então** se corta o excesso. A tabela abaixo está pela ordem
> **corrigida**.

> *"há coisas a ajustar mas a maior parte das vezes estão certas."*
> As boxes do `PlayerTracker` do João **estão boas**. O que falta não é um detetor melhor — é
> **aplicar-lhes as regras do jogo, por esta ordem**:

| # | regra | porquê |
|---|---|---|
| **1** | 🦶 **OS PÉS NÃO PODEM SAIR DO POLÍGONO.** O polígono é o **CHÃO do campo — e INCLUI OS ESPAÇOS LATERAIS** (é por lá que eles saem no **jogo exterior**). | mata os espectadores. ⚠️ **NÃO é só a área das linhas** — se fosse, cortava os jogadores em jogo exterior, que é jogo legal. |
| **2** | 👀 **OS DOIS DE CIMA TÊM DE ESTAR SEMPRE VISÍVEIS.** | a câmara vê-os sempre. Se só aparece **um**, o outro **não desapareceu** — está lá. **Vai procurá-lo** *(ver 3)*. |
| **3** | 🔗 **CONTINUIDADE** *(J5 — "a única regra que ACRESCENTA informação")*. **"Se não os vês, temos de PERCEBER PORQUÊ não os vês."** Visto no frame 100 e no 104 ⇒ **interpola** 101-103. | **A ausência NÃO é um buraco. É uma pergunta.** ⚠️ **NÃO é um filtro** — não se descarta o frame. **PREENCHE-SE.** |
| **4** | 👥 **NUNCA MAIS DE DOIS. E são sempre 2 CONTRA 2** *(por LADO da rede)*. **← É O ÚLTIMO.** | é uma verdade do **jogo**, não um limiar. Permite **baixar o `CONF`** do detetor sem pagar precisão. ⚠️ **Depois da continuidade** — senão corta o jogador verdadeiro e fica com o falso. |
| **5** | 🛡️ **OS DE BAIXO INVISÍVEIS ⇒ ESTÃO EM ZONA DE DEFESA.** | 🔑 **A AUSÊNCIA É O SINAL.** A câmara é baixa e **corta os de baixo quando eles recuam**. Logo: **não os ver não é informação perdida — é a informação de que RECUARAM.** *(É a J7+J8, agora formalizada: a informação não se perde, **muda de forma**.)* |

> 🚨 **NÃO DESCARTAR FRAMES.** Nenhuma destas regras é um filtro que deita fora o frame. A #1 e a
> #2 **limpam**; a #3, a #4 e a #5 **ACRESCENTAM**. É a diferença entre um detetor e um modelo do jogo.

> ⚠️ **PORQUE É QUE ESTAS REGRAS SE PERDEM** (o Vasco perguntou, 13 jul: *"porque é que te vais
> esquecendo destas regras?"*): **TODAS as regras de jogadores estão DESLIGADAS.** Vivem em
> `padelpro/modules/servico.py` e **NÃO CORREM EM LADO NENHUM** — o pipeline que dá os 96,3% usa
> **só a bola**. Como não correm, não são testadas; como não são testadas, não aparecem nos
> números; e o que não aparece nos números, esquece-se.
> **É a mesma doença da S12 e da S8.** A cura é a mesma: **pô-las a correr e a serem medidas.**

---

### 🔴 J6+ — **SEGUIR O JOGADOR PELA ROUPA** *(Vasco, 13 jul — o MECANISMO, que faltava)*

> *"Detetas uma **bounding box consistente** nos primeiros tempos · detetas a **cor da roupa** ·
> passas **só a seguir essa cor da roupa**."*

**O detetor serve só para ARRANCAR. Depois a IDENTIDADE é a COR.**

```
1. ARRANQUE   — nos primeiros tempos, encontra uma box CONSISTENTE (estável, de confiança)
2. APRENDE    — tira dela a assinatura de cor  (torso + calções + pernas + ténis)
3. SEGUE      — a partir daí, segue a COR. Já não o detetor.
```

🔑 **PORQUE É QUE ISTO É FORTE:** a cor **não se perde** quando a box fica **cortada** pela borda,
**meia tapada**, ou com **confiança baixa** — que é **exactamente** onde o detetor falha (os
jogadores de baixo!). **A identidade sobrevive à falha da deteção.**
*(É a J6 — que só dizia "assinatura por torso+calções+pernas+ténis" — agora com o MECANISMO.)*

### ✅ E ISTO DESBLOQUEIA A **J9** — que estava dada como MORTA

A J9 (*"aprender as cores no início de cada ponto"*) estava **⛔ bloqueada por dependência
circular**: precisava de saber **onde começam os pontos**, e era isso que o M1 andava a descobrir.

# 🎉 **JÁ NÃO É CIRCULAR.** O M1 dá **13/13 serviços** (13 jul).

**Sabemos onde cada ponto começa, treze vezes.** E o início do ponto é **o frame mais limpo do
jogo**: jogadores **separados**, **parados**, **em formação**. É o melhor sítio possível para
aprender as cores — e agora é **encontrável**.
👉 **A J9 passa de ⛔ BLOQUEADA a 🟢 PRONTA A IMPLEMENTAR.**

---

## SERVIÇO / M1

| # | Regra | Estado | Onde |
|---|---|---|---|
| S1 | **Zona de serviço aprendida dos dados** — bola no chão junto a um jogador atrás da linha → 10/12 serviços reais. Bom gerador de candidatos. | ✅ implementada | `detetar_servicos()` |
| S2 | **Formação de serviço** — parceiro na rede + adversário cruzado atrás. **0 falsos.** | 🟢 **REABERTA (13 jul) — NUNCA ESTEVE BLOQUEADA.** Dei-a como *"cega"* citando **"só 21,8 % dos frames têm os 4"**. 🚨 **O 21,8 % era um ARTEFACTO DO `max_det=4`, não da câmara** (sem cap + regras J: **38,8 %**). E o **erro maior era a ESTATÍSTICA**: a regra não precisa dos 4 em **todos** os frames — precisa deles **nos 13 momentos do serviço**, que é **o frame mais limpo do jogo**. O M1 dá **13/13** ⇒ **sabemos onde olhar**. ⚖️ **MEDIR ANTES DE CITAR.** | `formacao_servico()` — **NÃO CORRE** |
| S3 | **Formação lida SÓ nos 2 de cima** ← **a decisão de hoje** | ✅ implementada (12 jul) | `formacao_de_cima()` |
| S4 | **Quadrado de serviço cruzado** — a bola do serviço cai na **diagonal**. **0 falsos.** | ⚠️ implementada, mas precisa do ressalto (bola a 46% → subir para 76% com thr=0.4) | — |
| S5 | **Serviço multi-fator** — nenhum sinal sozinho chega; combinar. | ✅ é a arquitetura atual | — |
| S6 | **Alternância** — os serviços alternam de lado. **Mas o lado só muda quando o PONTO CONTA**: falta/let repete o mesmo lado ⇒ numa corrida do mesmo lado, o que vale é **o ÚLTIMO**. | 📋 por implementar. ⚠️ **NÃO é lei** — no **ponto de ouro** quem recebe escolhe o lado e pode repetir. | `m1_tempo_util.py` |
| S7 | **Lado do serviço** distingue **ace** de **falta**. | 📋 por implementar | `SPEC_M1_TEMPO_UTIL.md` |
| S8 | **Ponto só acaba se a próxima pancada for serviço** | ⛔ **BLOQUEADA pelo M3.** Tentada a sério (13 jul) e **rejeitada**: 98,9 recall mas **47,1 precisão**, 5 segmentos colados. Sem detetor de serviço, as **pancadas do INTERVALO** entram pelo meio e esticam cada ponto até ao seguinte. **A regra é boa — o que falta é o serviço.** Não voltar a tentar sem M3. *(Estava marcada "✅ nas regras v9" e NUNCA correu.)* | — |
| **S9** | 🔴 **A SEQUÊNCIA DO SERVIÇO** (12 jul) — `SAI DA MÃO → CHÃO → RAQUETE → RESSALTO DENTRO DO QUADRADO CRUZADO → pancada seguinte segue o ponto`. **Sem ressalto no quadrado cruzado NÃO HÁ SERVIÇO** (condição necessária, não pontuação). E: **não disparar serviços só pela estrutura** (estarem todos posicionados). | 🔴 **é a especificação**. Bloqueada pelo detetor de ressalto (4/12). | `m1_tempo_util.py` |
| S10 | **Duplo ressalto** — o serviço é a **única** jogada em que a bola ressalta **obrigatoriamente dos dois lados** da rede (o servidor deixa-a cair; e tem de ressaltar no quadrado antes de o recetor lhe bater). **Corolário:** os dois ressaltos estão em lados opostos ⇒ **um está SEMPRE em cima** (o lado que a câmara vê). O de baixo pode estar **tapado pelo jogador** — não invalida. | 📋 por implementar | — |
| S11 | **Mudança de servidor** — 2 pontos válidos seguidos do mesmo lado ⇒ mudou o jogo ⇒ serve o outro par. | ⚠️ **pista fraca**: no **tie-break** o serviço roda a cada 2 pontos e isto não vale. | — |

| **S12** | **FIM DO PONTO — 4 s depois da última PANCADA.** Se não se detetar pancada nenhuma, corta com **2-3 s** de margem. *(Substitui os dois erros anteriores: cortar quando a bola deixa de cruzar = **cedo demais**; esticar enquanto a bola andar = **tarde demais** — "a bola pode andar e já ter batido duas vezes".)* | ✅ implementada (v7/v8) | **`gerar_tempo_util.rallies()`** · interruptor `REGRAS["S12_ULT_PANCADA"]` |
| **S13** | ⏱️ **A TIMELINE NUNCA ANDA PARA TRÁS.** Um segmento nunca se sobrepõe ao anterior nem repõe um frame já usado. **Se dois segmentos se tocam, são O MESMO PONTO** — fundem-se. | ✅ implementada (v8). Corrigiu **6 saltos para trás** e arrumou 21 segmentos em **15 pontos** (os reais são 12). | **`gerar_tempo_util.rallies()`** · interruptor `REGRAS["S13_TIMELINE"]` |
| S14 | **Fim verdadeiro do ponto** = a bola bate **DUAS VEZES no chão sem ninguém lhe tocar**. | 📋 a regra certa, **bloqueada** pelo detetor de ressalto (7/12). O S12 é a aproximação enquanto isso. | — |

| **S15** | 🔴 **MÃO vs RAQUETE** — *"NÃO DISPARAR SERVIÇOS. Só disparar se a bola vier da mão para o chão para a raquete."* A bola da **mão é LENTA**; a da **raquete é RÁPIDA**. Medido no `L` do BlurBall: **serviços L=17,4 · falsos (passagens à mão) L=2,7**. | ✅ implementada. **+18 pontos de PRECISÃO** (65,8% → 83,9%). Mata 24 dos 27 falsos. | **`gerar_tempo_util.cruzamentos()`** · interruptor `REGRAS["S15_MAO_RAQUETE"]` |
| **S16** | ⚖️ **DÚVIDA = MAIS MARGEM; CERTEZA = CORTE RENTE.** Se há pancada detetada → sei que acabou → corto a **2 s**. Se NÃO há pancada → estou na dúvida → dou **5 s**. *(Eu tinha implementado ao CONTRÁRIO — 4 s quando sabia, 2 s quando duvidava. Cortava os pontos 12/13/14 a meio.)* **Os 5 s são para DECIDIR, não para MOSTRAR.** | ✅ implementada. **+9 pontos de precisão** (83,9% → 92,9%). | **`gerar_tempo_util.rallies()`** · interruptor `REGRAS["S16_DUVIDA"]` |
| **S20** | ⏸️ **A PAUSA ENTRE PONTOS — 5 a 15 s.** *(estava nos prompts v7.1/v7.7/v8 e **NUNCA foi implementada** — ver `REGRAS_PERDIDAS_dos_prompts.md`)*. Uma pausa **curta demais é IMPOSSÍVEL**: entre pontos os jogadores têm de **ir buscar a bola** e **posicionar-se**. Se o pipeline produz uma pausa de **2,6 s**, a **CAUDA** do segmento anterior está esticada — **e não é preciso saber PORQUÊ para a aparar.** <br>🧠 **APRENDIDA POR DUPLA** *(Vasco, 13 jul: "tem uma **média associada a cada jogador**, que podes ir notando ao longo do vídeo")*: **2 passagens** — a 1.ª observa as pausas do **próprio vídeo**; a 2.ª usa `mediana − 2,5×MAD`. **Zero números meus.** <br>🔒 **Chão de segurança: 4 s** (Vasco). ⚠️ **SÓ APARA A CAUDA — nunca toca no INÍCIO do seguinte** ⇒ **estruturalmente incapaz de perder um serviço** (recall intacto até aos 6 s, medido). | ✅ **implementada (13 jul).** **+1,8 precisão** (93,9 → 95,7). **RESOLVEU A CAUDA DO PONTO 1** (3,5 s → 1,2 s) — que **nenhuma outra regra apanhava**: a raquetada que a esticava era do **INTERVALO**, com um jogador ao pé, **indistinguível de jogo**. Só o M3 a mataria. **Esta mata-a de graça, sem saber o que lá está.** | **`gerar_tempo_util.pausa_aprendida()`** · interruptor `REGRAS["PAUSA_MINIMA"]` |
| **S17** | 🔒🔒 **FECHADA — "a regra da rede está perfeita! fixa e não deixes mudar."** (Vasco, 13 jul) **`RED_DTHETA` / `RED_L_PARA` / `RED_DIST` NÃO SE MEXEM.**<br>**BOLA NA REDE → fim certo, corte a 0,5 s.** ⛔ **A POSIÇÃO NÃO SERVE** — nesta câmara a bola que passa POR CIMA e a que BATE ocupam **os mesmos píxeis** (banda da rede = 35 px; meio-campo do fundo = 100 px). 60 de 94 candidatos caíam **a meio de pontos reais**. ✅ **O que serve (Vasco, 13 jul):** *"se a bola **muda de direção** (ou **pára**) na rede, **longe de uma bounding box** → o ponto acabou."* A bola que passa **não vira**. A que bate, **vira ou morre**. E se não há jogador ao pé, **não foi ninguém: foi a rede.** | ✅ **implementada (13 jul)**. 0 eventos a meio de pontos · 4 no fim (pts 2,3,5,10). **+4,1 precisão.** | **`gerar_tempo_util.fim_certo()`** · interruptor `REGRAS["S17_REDE"]` |
| **S18** | 🔴 **MÃO/CORPO NA BOLA → fim certo, corte a 0,5 s.** *(Vasco, 13 jul: **"bola PARADA dentro da bounding box, SEM MUDAR DE CAMPO → ponto terminado de certeza, sem raquetada."**)* **As três condições são precisas as três:** **parada** (`L≤3`) · **dentro da box** (é a mão/corpo de alguém) · **sem mudar de campo** (se atravessou a rede, foi **batida**). ⛔ A bola lenta sozinha dá **49 falsos a meio de pontos** — o lob também vai lento no ponto alto. 🔒 **A DURAÇÃO (0,5 s) NÃO SE BAIXA:** a 0,3 s corta pontos a meio e o recall cai de 96,2 para **82**. **É a duração que separa a MÃO do LOB** (o lob vai lento — mas um *instante*). E: **jogadores a passar a bola com a mão ⇒ o ponto JÁ acabou e ainda NÃO começou.** | ⚠️ **implementada e A CORRER — mas vale +0,0 (ablação, 13 jul).** **0 eventos a meio de pontos** (é segura), **mas desligá-la não muda um único número**: a **S17** e a **S23** já matam os mesmos fins. 🔑 **REDUNDANTE NESTE VÍDEO — não necessariamente no próximo.** Fica **LIGADA** (não custa nada, e noutra câmara pode ser ela a segurar). **REAVALIAR no 2.º vídeo.** ⚠️ E é ela que **parte o ponto 5** se lhe derem boxes **INTERPOLADAS** (J5): *uma box inventada não é prova de que há uma mão ali.* | **`gerar_tempo_util.fim_certo()`** · interruptor `REGRAS["S18_MAO_PARADA"]` |

---

### 🟥 SERVIÇO / M1 — **AS REGRAS DOS ORIGINAIS** *(auditoria 13 jul — nenhuma estava aqui)*

| # | Regra | Estado | Origem |
|---|---|---|---|
| **S21** | ⭐⭐ **A ALTERNÂNCIA DAS TRAVESSIAS — o melhor sinal de jogo/não-jogo que temos.** As pancadas **alternam** entre o campo de baixo e o de cima; uma equipa **não bate 2× seguidas**. Logo **cada TRAVESSIA DA REDE implica uma pancada** no campo de origem — **não é preciso VER a pancada: a física garante-a.** Robusto a oclusão e a bola fora do frame. **Travessias alternadas e sustentadas = rally em curso.** ⇒ **Entre pontos a bola cruza a rede NO MÁXIMO UMA VEZ** (devolvida ao servidor) — **não faz vaivém.** *"Dá precisão SEM sacrificar recall."* | 🔴 **POR IMPLEMENTAR — e é a maior de todas.** Ataca **exactamente** os 45% de bola-do-intervalo que estavam dados como insolúveis. **Escrita há dias; nunca correu.** | `docs/SPEC_M1_TEMPO_UTIL.md` |
| **S22** | 🎾 **O LADO DO SERVIÇO — ace vs falta, SEM homografia.** Depois de um **ponto concluído** → o serviço vai para o **lado OPOSTO**. Depois de uma **FALTA** → **repete o MESMO lado**; **é a única vez que isso acontece**. ⇒ **falta + 2.º serviço = UM ponto, não dois** (corrige a sobre-contagem). ⇒ **auto-verificação de graça**: se a sequência de lados não alterna e não houve falta, **detetámos um serviço a mais ou perdemos um** — *sinal de erro **sem** ground-truth*. Lado = `x` do centro da box do servidor vs `x` do meio do campo. **Sem calibração nova.** | 🔴 por implementar. **Absorve e completa a S6/S7.** | `SPEC_M1` |
| **S41** | 🎯 **AS 6 CONDIÇÕES DO SERVIÇO.** *(era "S23" — **COLISÃO DE NOMES**, renumerada 13 jul. A S23 é o QUIQUE, que CORRE.)* **A.** bola na box de um jogador e ~parada (na mão) · **B.** ⭐ **desce e RESSALTA aos pés do servidor** *(nenhuma outra bola do jogo faz isto)* · **C.** raquetada (pico de velocidade) · **D.** servidor **atrás da linha** · **E.** formação · **F.** 🆕 **o servidor ARRANCA a seguir — sobe à rede.** | 🔴 por implementar. **A F nunca esteve registada.** (A S9 tinha a sequência; faltava-lhe o **depois**.) | `SPEC_M1` · `M3_SERVICO_estado.md` |
| **S23** | 🔴🔴 **O QUIQUE DO SERVIÇO** *(Vasco, 13 jul — **a regra que desbloqueou a faixa da rede E o M3**)*<br>*"Temos de matar este lixo pela **bola na mão do NÃO SERVIDOR — ANTES de bater no chão**."*<br>*"Mesmo que tenha kick, **só o ÚLTIMO** antes da mudança de direção para o outro campo **conta**."*<br>**A LEI: NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.**<br>• o **servidor** larga a bola → ela **QUICA** (na linha de serviço) → e **só depois** bate<br>• o **não-servidor** tem a bola na mão → **passa-a / atira-a** ⇒ **SEM QUIQUE**<br>⇒ um segmento **sem quique fundo** antes da 1.ª travessia **NÃO É UM PONTO**. | ✅ **implementada (13 jul).** **13/13 pontos reais têm quique fundo** (prof 1,04–1,45) · **o lixo tem ZERO.** **Separação perfeita, sem afinar nada.** Vale **+3,5 de precisão**. 🔓 **É ela que permite a B15** (ampliar o `MIN_PROF`). ⚠️ **1.ª vez que o RESSALTO entra no pipeline** — se o 2.º vídeo perder pontos, **DESLIGAR ISTO PRIMEIRO**. | **`gerar_tempo_util.quique_do_servico()`** |
| **S24** | ⬇️ **O SERVIÇO É POR BAIXO — A BOLA NÃO SOBE.** O sinal é o **arranque HORIZONTAL depois do ressalto**. *(Procurar um "toss" a subir é procurar o que não existe.)* | 📋 registar — **é um pressuposto, não um passo** | `SPEC_M1` · `PLANO_pos_BlurBall` |
| **S25** | 🖐️ **FIM IMEDIATO — JOGADOR TOCA NA REDE** (raquete **ou** corpo). O ponto acaba aí, **sem esperar os 6 s**. | 🔴 **por implementar — está nos prompts desde o v1 (14 jun) e NUNCA foi tocada.** | v1 §5.4 · v3 P7.4 · v9 M1.3 |
| **S26** | 🏓 **FIM — A MESMA EQUIPA BATE 2× SEGUIDAS** (toque duplo). *"Duas pancadas seguidas no mesmo campo = **impossível** → uma é espúria **OU o ponto acabou**."* | 🔴 por implementar. **Sai de graça da S21** (que já sabe de que lado veio cada pancada). | v1 §5.1 · v3 P7.1 · R13 |
| **S29** | ⏱️ **A REGRA DOS 6 s — a rede de segurança.** A última pancada só é fim depois de **6 s sem pancada**. Nesses 6 s: pancada que **não** é serviço → **o ponto não tinha acabado**. *"**Aplica-se SEMPRE, independentemente de a bola ser detetável ou não.**"* *(O Vasco reduziu 6→5 s.)* | 🔑 **É A PEÇA QUE FALTAVA À S8.** A S8 morreu (98,9 / **47,1**) porque esperava pelo serviço seguinte **sem TETO** — as pancadas do intervalo esticavam tudo. **Os 6 s são o teto. A S8 nunca foi testada com a sua rede de segurança.** | v1 §5.2 · v3 P7.2 · v9 M1.2 · R5 |
| **S30** | 🧍 **INATIVIDADE DOS JOGADORES — e a proibição de adivinhar.** **TODOS** visíveis + ~3 s parados ⇒ confirma o fim sem esperar os 6 s. **"Se não vires todos, NÃO adivinhes"** — usa só os 6 s. | 🟢 **REABERTA (13 jul)** — estava ⛔ pelo mesmo **21,8 % falso** da S2. Ver acima. **MEDIR ANTES DE CITAR.** | v9 M1.5 · R6 |
| **S31** | ✂️ **A MARGEM DE +2 s É PARA VER, NÃO PARA CONTAR.** *"apenas como margem visual (não é deteção)"*; **não conta no tempo útil estatístico**. | ⚠️ **verificar no código** — se a margem entra na estatística, o tempo útil está inflacionado | v9 M1.6 · R8 |
| **S32** | 🕊️ **SALVAGUARDA DO SERVIÇO PERDIDO.** Serviço **não** detetado mas **jogo evidente** ⇒ o segmento **entra na mesma**, com `confianca: baixa`. *"**Colar dois pontos é mau; perder um ponto é pior.**"* | 🔴 por implementar. **É a diretriz de produto aplicada ao M1.** | `SPEC_M1` |
| **S33** | 🎾 **VALIDADE DO SERVIÇO.** ✅ **Válido:** cai no quadrado **cruzado** sem tocar na malha · 🔄 **LET:** toca na tela **e cai dentro** ⇒ **REPETE** · ❌ **FALTA:** toca na malha e não entra; **ou o recetor não jogou**; ou muda o servidor. | 📋 por implementar (stub em `servico_valido()`). ⚠️ **O let é a exceção que quebra a S6/S22** — repete o mesmo lado **sem ser falta**. | v1 §4 · v3 P6 · R12 |
| **S34** | 🥈 **A "2.ª BOLA"** — a **1.ª pancada do recetor após o serviço**. Marca analítica (`segunda_bola: true`); **não afeta o timing**. | 📋 registar | v1 §3 |
| **S35** | 📐 **A RÉGUA DO SERVIÇO É A BASE DA BOX DO SERVIDOR (`y2`).** A bola ressalta **aos pés dele** ⇒ **não é preciso calibrar o plano do solo.** | 🔴 por implementar. **Poupa a calibração que está a bloquear o ressalto.** | `SPEC_M1` |
| **S36** | 🧭 **DISTINGUIR EVENTOS SEM PLANO DO SOLO** — **ressalto** = inversão vertical **SEM jogador perto** · **pancada** = mudança brusca **COM jogador perto** · **ressalto do serviço** = inversão **com** jogador perto, a **baixa velocidade**, seguida de **pico**. | ⚠️ **METADE JÁ CORRE (13 jul):** o **CHÃO = inversão VERTICAL** está implementado — é o `ressaltos()`, e é ele que dá a **S23** (13/13). **Falta a PAREDE** (inversão horizontal) e a **RAQUETE** (com jogador ao pé — essa já existe, é a S37). ⇒ **NÃO está "por implementar": está a MEIO, e a metade que existe é a que abriu o M3.** | **`gerar_tempo_util.ressaltos()`** |
| **S37** | 🏸 **UMA RAQUETADA TEM DE TER UM JOGADOR AO PÉ** (`PAN_TEM_JOGADOR`). Mata as pancadas-fantasma no público. | ✅ implementada (13 jul). **+0,5 precisão** | `gerar_tempo_util` |
| **S38** | ⏸️ **A PAUSA > 45 s TEM QUATRO SIGNIFICADOS** — `troca_de_campo` (jogadores do **lado oposto**) · `discussao`/timeout (**mesmo lado**, reagrupados) · `lesao` (dispersos, câmara foca um) · `indefinido`. | 📋 por implementar. ⚠️ O inventário só tinha *"pausa>45s ⇒ troca de campo"*. **Nem toda a pausa longa é uma troca.** | v1 §6 · v3 P8 |
| **S39** | 🧵 **STITCHING PROIBIDO** — nunca unir dois momentos com **> 2 s de inatividade** entre eles: **são rallies diferentes.** | ⚠️ era a muleta do detetor fraco (`gap_fora_s`). **Com o BlurBall, a inatividade mede-se em PANCADAS, não em bola.** | v7.1 M1.3 · v7.7 · v8.0 |
| **S40** | 📏 **DURAÇÃO PLAUSÍVEL** — *"sem rallies de ~30 s nem fragmentos de ~1 s"*; alvo **11-13 rallies**. ⚠️ **MAS o ponto 1 do ground-truth tem 3,5 s** ⇒ **`min_rally_s` acima de 3 s APAGA UM PONTO REAL.** | ⚠️ **contradição com a diretriz** — ver `REGRAS_PERDIDAS_v2` §④ | `AFINAR_TEMPO_UTIL_v2.md` |

> ✅ **O "BUG DO BALÃO" — RESOLVIDO, e NUNCA foi o balão** (13 jul).
> Os pontos 6 e 7 **já estavam inteiros**. O que estava partido era outra coisa, e era minha:
> **a S12 estava marcada como LIGADA e fazia outra coisa.** A regra do Vasco diz *"o ponto acaba 4 s
> depois da última PANCADA"*; o código agarrava-se ao último **CRUZAMENTO** da rede e só ouvia
> pancadas até 1,5 s depois. As seguintes (volta de parede, devolução rente, bola que morre do mesmo
> lado) eram **ignoradas** → ponto 3 acabava 2,3 s cedo, pontos 4 e 5 **partiam-se em dois**.
> **Não eram 3 bugs. Era 1: o fim do ponto estava agarrado à coisa errada.**
> A correção **não acrescenta números** — o `1.5` (mágico, sem nome) passou a `SILENCIO`, que já
> existia e já queria dizer isto. **Recall 93,2 → 97,0. Pontos partidos: 2 → 0.**
>
> ⚠️ **A LIÇÃO:** o `MAPA_DAS_REGRAS.md` listava a S12 como LIGADA. E a S8 também. **Uma regra pode
> estar no mapa, com o nome certo, e fazer outra coisa.** Pior do que estar desligada — porque
> ninguém a vai procurar. Os números diziam 93% e ninguém viu.

> ⚖️ **LEI DE DESENHO (12 jul):** **nenhuma regra do jogo pode VETAR um candidato** — há sempre uma
> exceção legítima (ponto de ouro, tie-break, let). Todas **pontuam**; nenhuma corta. Escolhe-se a
> **sequência** globalmente mais consistente. Um falso paga caro em vários sítios; uma exceção paga num só, e passa.

### S3 — porque funciona sem ver os de baixo

No serviço, as duas duplas estão em configurações **incompatíveis**:

| dupla que **SERVE** | dupla que **RECEBE** |
|---|---|
| servidor atrás + **parceiro NA REDE** | **os dois ATRÁS** |

Logo, olhando **só para os 2 de cima**:

- **os dois atrás** → eles **recebem** → **o serviço vem de baixo**
- **um na rede, um atrás** → eles **servem** → **o serviço vem de cima**

A formação de uma dupla **deduz** a da outra. Não é preciso ver os de baixo — e os de cima são precisamente os que o detetor vê quase sempre.

---

---

## 🔴 DOS PROMPTS ORIGINAIS (v1/v3) — REGRAS QUE NUNCA CHEGARAM A LADO NENHUM
*(13 jul: o Vasco — "todas as regras que me fui lembrando passaram pelos prompts". Eu tinha
auditado o RESUMO, não os ORIGINAIS. Um resumo também perde regras.)*
Ver `REGRAS_PERDIDAS_v2_dos_originais.md`. **Faltam ainda ~10 ficheiros por ler.**

| # | Regra | Estado | Onde |
|---|---|---|---|
| **J10** | 👕 **A CAMISOLA MUDA UMA DE CADA VEZ.** *"A camisola de um jogador pode mudar durante a pausa, **mas não de todos em simultâneo** — atualiza **só o jogador que mudou**."* (v1 §6) ⭐ **É A SALVAGUARDA QUE FALTA À REGRA DA COR** (J6+): se a identidade passa a ser a cor, o perigo é a cor **saltar de pessoa para pessoa** quando o detetor se engana. Esta regra fecha a porta: **as 4 assinaturas NÃO mudam todas ao mesmo tempo.** Se o código acha que mudaram todas, **o CÓDIGO é que está errado.** | 🔴 **por implementar — JUNTO com a J6+. Uma sem a outra é perigosa.** | — |
| **J11** | ↔️ **O LADO NÃO MUDA DENTRO DO RALLY.** *"O lado dos jogadores **não muda** ao longo do rally — só muda em **trocas de campo** (pausa longa)."* (v3) **Um invariante forte, nunca usado.** Dentro de um ponto, quem está em cima **fica** em cima ⇒ resolve ambiguidades de identidade **de graça**. Combina com a J6+ (cor) e a J4 (2 por lado). | 🔴 por implementar | — |
> **As restantes regras desta 1.ª passagem foram promovidas aos blocos próprios** *(criados na
> auditoria completa)*: a **D1** (em dúvida, mantém o estado) e a **D2** (não inventar) estão em
> **LEIS DE DESENHO**; a antiga **M2-1** (DEFESA→ATAQUE proibido) é a **F10**, a **M2-2** (confiança
> 0–1) é a **D8** e a **M2-3** (rallies curtos) é a **D7**; e a antiga **C6** — *"a câmara é lateral"* —
> **estava ERRADA** e foi corrigida no bloco **CAMPO**.

## 🎬 M2 / FASES — **AS REGRAS DOS PROMPTS** *(nunca inventariadas)*

| # | Regra | Estado | Origem |
|---|---|---|---|
| **F1** | 👥 **A fase é da EQUIPA, nunca do jogador.** *"A fase é determinada pela posição **colectiva da equipa** — nunca pelo jogador individual."* | 📋 | v1 §3 · v3 P4 |
| **F2** | 🧱 **A REGRA DAS DUAS BOXES · TRANSIÇÃO É O ESTADO-RESÍDUO.** Só é **DEFESA** se forem **ambos** atrás da linha de serviço; só é **ATAQUE** se forem **ambos** à frente da interceção malha 3/2. **Tudo o resto = TRANSIÇÃO** *(incluindo um no fundo e outro na rede)*. | ✅ é a spec v9 | v9 §1 |
| **F3** | 📍 **A posição é a ARESTA INFERIOR da box** (contacto com o solo) — **nunca** a cabeça, o tronco, a raquete **ou um pé isolado**. | ✅ | v1 §1 · v3 P2 · v9 §0.2 |
| **F4** | 🎾 **O SERVIÇO É UM MOMENTO DENTRO DO ATAQUE — não uma fase.** *"Quando o servidor está no FUNDO e o parceiro está na REDE, **a equipa está em ATAQUE**."* | 🚨 **CONTRADIZ A F2** (que classificaria isso como TRANSIÇÃO). **Decisão do Vasco.** Ver `REGRAS_PERDIDAS_v2` §③ | v1 §3 · v3 P4 |
| **F5** | 🧊 **ANTI-JITTER: o cruzamento tem de ser CLARO.** *"Se a box apenas **toca, treme ou oscila** em cima da marca sem a atravessar de forma **estável**, **NÃO** abras nova entrada."* | 🔴 por implementar | v9 M2.6 |
| **F6** | 🔬 **Raciocina ao FRAME, apresenta ao CLIP.** Percorre em resolução fina por dentro; consolida no output. *"A TRANSIÇÃO, por ser a mais dinâmica, é a que mais beneficia."* | 🔴 | v9 M2.7 |
| **F7** | 🔢 **Conta-se por TRANSIÇÕES, não por combinações.** `nº entradas = nº transições + 1`. A mesma combinação **repete-se** — cada ocorrência é uma entrada independente. | 🔴 | v8.0 · v9 M2.3 |
| **F8** | 🔗 **Sem buracos nem sobreposições:** `fim[i] == inicio[i+1]`; a 1.ª abre no início do rally, a última fecha no fim. | 🔴 | v9 M2.4 |
| **F9** | 🔍 **MAXIMIZA A GRANULARIDADE — na dúvida entre fundir e separar, SEPARA.** *"É preferível um clip a mais do que perder uma transição."* ⚠️ **É o CONTRÁRIO da S13** — mas **não é contradição**: nos **PONTOS** funde-se; nas **FASES** separa-se. | 🔴 | v9 M2.5 |
| **F10** | 🚦 **DEFESA → ATAQUE sem passar por TRANSIÇÃO é PROIBIDO.** *Exceção: se foi rápido demais para captar, aceita o salto.* *(= a antiga M2-1)* | 🔴 | v1 §3 · v3 P4 |
| **F11** | 🗺️ **O VOCABULÁRIO DE ZONAS DA v1 (perdido):** `ML1`·`ML2` (rede→ATAQUE) · `ML3` (3.ª malha→linha de serviço→TRANSIÇÃO) · `VL1`·`VL2` (laterais) · **`VF1`–`VF5`** (o vidro de fundo em **5 zonas**, da direita para a esquerda) → DEFESA. | 📋 registar — **desapareceu quando a v3 simplificou para 3 zonas** | v1 §2 |
| **F12** | 📐 **A marca do ATAQUE = interceção MALHA 3 / MALHA 2** *(era "junção Parede/VL1" na v7.7/v8)*. **Não é linha branca ⇒ tem de ser desenhada** *(é a C2)*. **Falta UMA linha para o M2 passar a geometria pura.** | ⬜ **falta calibrar** | v9 §1 · `HANDOFF_CENTRO_DECISOES` |

---

## 🏸 M3 / PANCADAS — **AS REGRAS DOS PROMPTS**

| # | Regra | Estado | Origem |
|---|---|---|---|
| **P1** | 🎯 **Taxonomia de DOIS EIXOS.** `tipo` (**como se bate**): serve · volley · forehand · backhand · overhead · **bandeja** · **vibora** · indeterminado. `contexto` (**situação da bola**): normal · saida_parede_fundo · saida_parede_lateral · contra_parede · indeterminado. *(O antigo `saida_vidro` é **contexto**, não tipo.)* | 📋 | v9 M3 |
| **P2** | 📖 **As definições (v1 §7):** **volley** = sem a bola tocar o chão · **forehand/backhand** = **depois** de tocar no chão **ou no vidro** · **smash** = **força máxima**, **acima** da cabeça, pós-balão · **overhead** = **ao lado** da cabeça, efeito lateral, **a recuar** (víbora · bandeja · kick) · **saida_vidro** = deixa a bola bater **alto no vidro de fundo** e bate-a no ressalto. | 📋 | v1 §7 |
| **P3** | 🏁 **O resultado está ancorado ao FIM.** **Só a ÚLTIMA pancada** pode ser `winner`/erro; as restantes são `neutro`. | 📋 | v9 M3 |
| **P4** | 📸 **O TIMESTAMP DA PANCADA É NO CORPO, NÃO NO IMPACTO.** *"Deve coincidir com o **movimento biomecânico** (preparação/extensão do braço), **não com o impacto da bola, que é demasiado rápido para ser capturado com precisão**."* | 🔴 **por registar como lei** — vale para o modelo e para o humano que anota | v7.1 M3.5 · v7.7 |
| **P5** | 🔎 **A pancada em código:** a bola **aproxima-se** da box (mínimo local) **e depois a trajetória muda** (afasta-se / pico de velocidade); reforçar com o **deslocamento da box**. | ✅ implementada | `gerar_tempo_util.pancadas()` |
| **P6** | 🔊 **O ÁUDIO.** *"Usa o **som de impacto de raquete** ou o **bounce** da bola para confirmar que o rally está a decorrer. **Ignora conversas — estas ocorrem entre pontos.**"* | 🔴 **por implementar.** Desapareceu na v8.0 e nunca voltou. O MATCHi TV **não tinha áudio** — **o 2.º vídeo vai ter.** | v7.1 M1.4 · v7.7 · R15 |

---

## ⚖️ LEIS DE DESENHO — *as mais valiosas e as mais invisíveis*

| # | Lei | Origem |
|---|---|---|
| **D1** | 🤔 **EM DÚVIDA, MANTÉM O ESTADO ANTERIOR.** O estado tem **inércia** (histerese). Antídoto do jitter. | v1 §3 · v3 P4 |
| **D2** | 🚫 **NÃO INVENTAR. SE NÃO ANCORA, OMITE (o EVENTO).** *"Nunca inventas timestamps por estimativa."* | v1 · v3 |
| **D3** | 📏 **PRECISÃO HONESTA — `margem_ms`.** *"**Não finjas precisão absoluta.** Incerteza grande ⇒ **aumenta a margem e baixa a confiança**."* Em **ms**, não frames — **independente do FPS**. | v9 §0.1b |
| **D4** | 🗣️ **VOCABULÁRIO FECHADO + A DÚVIDA TEM NOME.** Não consegues classificar ⇒ **`indeterminado`** + **`confianca: baixa`**. **Nunca uma entrada sem âncora visual.** | v9 §0.3 |
| **D5** | 👁️ **OBSERVAR ANTES DE CLASSIFICAR.** Bloco de raciocínio **obrigatório e ANTES** do JSON; *"o JSON tem de ser **consistente** com o raciocínio"*. *(E os módulos são desacoplados **"para evitar alucinações"**.)* | v7.1 · v9 §0.5 |
| **D6** | ✅ **AUTO-VERIFICAÇÃO ANTES DE EMITIR.** Checklist explícita: totais batem certo · `fim > inicio` · **sem sobreposições** · cada rally começa num serviço. *(A **S13** — "a timeline nunca anda para trás" — **é um item desta checklist**, escrito em junho.)* | v9 (todos os módulos) |
| **D7** | 🚫 **NUNCA OMITIR UM *RALLY*** *(≠ omitir um EVENTO)*. Ambíguo ⇒ **`confianca: baixa`**, *"em vez de o omitir **ou duplicar**"*. **Rallies < 5 s: omite as FASES, nunca o RALLY.** 🔑 **Resolve a tensão com a D2:** *omite o **evento** que não ancoras; **nunca** omitas o **ponto**.* | v3 P10 · v9 M1.5 |
| **D8** | 📉 **`confianca` 0.0–1.0 em cada entrada; < 0,6 quando há dúvida.** Incerteza **explícita**. | v3 P4 |
| **D9** | 🎣 **RECALL PELA DETEÇÃO, PRECISÃO PELA ESTRUTURA.** Detetar generosamente; limpar com as regras do jogo. | `HANDOFF_JOGADORES` |
| **D10** | 📐 **GEOMETRIA > MODELO.** *"Sempre que algo se reduz a **comparar posições com linhas** ou aplicar uma **regra fixa**, **não precisa nem de prompt nem de treino**."* | `prompt_modelo_hibrido_v9` |
| **D11** | 🩼 **AS REGRAS DE GAP ERAM MULETA DO DETETOR FRACO.** Com detetor forte, **o que separa os pontos é a ESTRUTURA** (serviço, alternância) — **não a ausência de bola**. | `PLANO_pos_BlurBall` |
| **D12** | 🛑 **"NÃO ESCREVER MAIS REGRAS. MELHORAR O SINAL."** Quando as regras dão **0 falsos** mas rejeitam verdadeiros **por falta de dados**, o problema **não são as regras**. | `HANDOFF_CENTRO_DECISOES` §5 |
| **D13** | 📊 **FAIXA FINA = OBSERVÁVEL · ÁREA GRANDE = AMBÍGUA.** A rede (35 px) funciona; o vidro (meio ecrã) não. **Serve para prever se uma ideia tem hipótese antes de a escrever.** | `ESTADO_13JUL` |
| **D14** | 🤝 **DUAS LEITURAS INDEPENDENTES; SE SE CONTRADIZEM, NÃO INVENTA.** *(`quem_serve()`)* | `MAPA_DAS_REGRAS` |
| **D15** | 🔒 **UM "FIM CERTO" NUNCA PODE CAIR A MEIO DE UM PONTO** (`fim_dentro = 0`). **Se subir: DESLIGA a regra — nunca relaxes o teste.** | `ESTADO_13JUL` |
| **D16** | ➕ **SINAIS INDEPENDENTES SOMAM.** Bola e jogadores **não competem — somam.** | `HANDOFF_JOGADORES` |
| **D17** | 🧐 **CONFIRMAR A PREMISSA ANTES DE ACEITAR A CONCLUSÃO.** *(Duas propostas externas bem argumentadas partiam de um pipeline que não é o nosso.)* | `HANDOFF_JOGADORES` |
| **D18** | ⚖️ **NENHUMA REGRA DO JOGO PODE VETAR UM CANDIDATO** — há sempre uma exceção legítima (ponto de ouro, tie-break, **let**). Todas **pontuam**; nenhuma corta. | 12 jul |

---

## CAMPO / GEOMETRIA

| # | Regra | Estado |
|---|---|---|
| C1 | **Novo campo = nova calibração** à mão, no `calibrar_campo.html`. Não auto-detetar. | ✅ |
| C2 | **A malha 2/3 nunca se deteta** — não é linha branca. Tem sempre de ser desenhada. | ✅ |
| C3 | **A central sai dos pontos do meio** das linhas de serviço + base da rede. Não se marca — calcula-se. | ✅ |
| C4 | **Os extremos das linhas são os cantos** — daí saem as laterais. (Cuidado: descartar os que tocam a **borda do frame**, que não é o vidro.) | ✅ |
| C5 | **3 pontos = curvatura; 2 pontos = herdam-na.** A lente curva as linhas. | ✅ |
| **C6** | 📷 **A CÂMARA É FRONTAL — fixa, atrás do VIDRO DE FUNDO, 960×540.** 🚨 **CORREÇÃO (13 jul):** o inventário dizia *"lateral, a meia altura"* — copiado da **v3**, que é a **única** versão que diz isso **e está errada**. A v1, a v7.1, a v7.7, a v8.0, a v9 e **todo o código** dizem **FRONTAL**. | ✅ **corrigida** |
| **C7** | 🏔️ **QUANDO O CHÃO FALHA, SOBE.** O padel é uma **caixa 3D rígida e normalizada**: topos de vidro, postes, rede. *"**Estes pontos estão altos — são os últimos a sair do enquadramento e NUNCA são tapados por jogadores.**"* 🎯 **Possível resposta ao bloqueio do RESSALTO** (*"falta profundidade"*): a profundidade que falta **não está no chão — está nas verticais**. | 📋 por explorar |
| **C8** | 🎞️ **Calibra com frames SEM JOGADORES** (entre pontos) — **oclusão zero**. Agrega N frames por mediana. A câmara é fixa: **calibra uma vez, valida sempre.** | 📋 |
| **C9** | ✏️ **ANOTA POLILINHAS, NÃO PONTOS.** *"Os cantos desaparecem; **as linhas não**."* Os pontos (**incluindo os que estão fora do frame**) saem de **interseções analíticas — de graça**. | ✅ é o que o `calibrar_campo.html` faz |
| **C10** | 🔭 **A DISTORÇÃO DE LENTE NÃO É OPCIONAL.** Sob distorção de barril, **uma homografia planar é matematicamente errada**. *(Já fechou a via do cross-ratio: −7% a +12%.)* | ⛔ via fechada, lição registada |
| **C11** | 📏 **Dimensões regulamentares (a régua de tudo):** campo **20×10 m** · **linha de serviço a 6,95 m da rede** · rede **0,88 m** ao centro / **0,92 m** nos postes · vidro de fundo **3 m**. | ✅ |
| **C12** | 🌡️ **A CÂMARA PODE DERIVAR.** A FIFA **recalibra antes do jogo e ao intervalo** — dilatação térmica dos suportes. *"«Câmara fixa = calibrar uma vez para sempre» **pode ser otimista demais.**"* ⚠️ **O 2.º vídeo é o teste:** ver se a calibração do Parada4 ainda assenta noutro vídeo do **mesmo campo**. | ⬜ **por testar** |

---

## ⚠️ A LIÇÃO QUE JÁ MORDEU 5 VEZES

> **Nada em píxeis absolutos sobrevive à perspetiva.**

O meio-campo **longe** tem **100 px**; o **perto** tem **290 px** — para os mesmos 6,95 m.

| erro | consequência |
|---|---|
| `tol=45px` (na rede) | 1,1 m de um lado, **3,1 m** do outro |
| `margem=40px` (fundo) | ~3 m de bancada a entrar |
| `tol=25px` (imóveis) | matava os jogadores do fundo |
| `vmax` em px/frame | rejeitaria jogadores reais ao fundo |
| linha de serviço longe | auto-detetada **40 px** ao lado |

**Todas as tolerâncias = frações do meio-campo local** (`Campo.meio_campo_px`).

---

## DIRETRIZ DE PRODUTO (manda em tudo)

> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**

Um ponto perdido é informação perdida **para sempre**. Lixo a mais é só um incómodo a saltar.
