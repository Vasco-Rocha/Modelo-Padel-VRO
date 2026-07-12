# As regras do Vasco — inventário completo

Todas as regras que vieram do Vasco, o que fazem, e onde estão.
**As melhores ideias do projeto vieram daqui.** Não perder nenhuma.

Última atualização: 13 jul 2026.

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
| B6 | **2 cliques = direção** — dois pontos dão a direção (o BlurBall já dá `L` e `Theta`). | ✅ **RESOLVIDO — e melhor do que pedias**: o `Theta` dá a direção com **2° de erro numa ÚNICA deteção**, sem precisar de dois pontos. **+10,2 recall e +2,5 precisão** no M1 (74,1/66,6 → **84,3/69,1**). Estava no CSV desde o 1.º dia. | `m1_tempo_util._tracklets()` |
| B7 | **Bola fora >2s = serviço** | ✅ nas regras v9 | — |
| B8 | **Coerência temporal** — uma deteção sozinha, sem vizinho compatível em ±2 frames (raio 45px/frame), é lixo. *"Confirmar com um antes e um pós."* Apanha os ténis brancos e os pontos brancos no público. | 🧪 **testada 12 jul**: mata 275 frames de lixo por 99 de rally (2,8:1). Custo no recall: -2,8 pp. **Vale a pena.** | por implementar |
| B9 | **Não inventar perto dos cegos** — ao contrário dos jogadores, na bola **não se interpola** por cima de buracos. Ausência é ausência. | 📋 por implementar | — |
| B10 | **`L` ≈ 0 é suspeito** — a bola em jogo está borrada; um ténis parado não. Medido: L mediana 2,5 / p90 12,4. **Sinal fraco isolado** (34% das deteções têm L<2), só serve combinado com B8. | 🧪 medido, não conclusivo sozinho | — |

> ⛔ **B-nota (12 jul):** **45% das deteções de bola caem FORA dos rallies — e são bola A SÉRIO** (o intervalo entre pontos: apanhar, passar, preparar). **Nenhuma regra de bola resolve isto.** Só o M3. Ver `project_threshold_04_fechado`.

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

---

## 🔴 A CASCATA DOS JOGADORES — a ORDEM importa   *(Vasco, 13 jul 2026, depois de ver as boxes do repo do João)*

> *"há coisas a ajustar mas a maior parte das vezes estão certas."*
> As boxes do `PlayerTracker` do João **estão boas**. O que falta não é um detetor melhor — é
> **aplicar-lhes as regras do jogo, por esta ordem**:

| # | regra | porquê |
|---|---|---|
| **1** | 🦶 **OS PÉS NÃO PODEM SAIR DO POLÍGONO.** O polígono é o **CHÃO do campo — e INCLUI OS ESPAÇOS LATERAIS** (é por lá que eles saem no **jogo exterior**). | mata os espectadores. ⚠️ **NÃO é só a área das linhas** — se fosse, cortava os jogadores em jogo exterior, que é jogo legal. |
| **2** | 👥 **NUNCA MAIS DE DOIS. E são sempre 2 CONTRA 2** *(por LADO da rede)*. | é uma verdade do **jogo**, não um limiar. Permite **baixar o `CONF`** do detetor sem pagar precisão. |
| **3** | 👀 **OS DOIS DE CIMA TÊM DE ESTAR SEMPRE VISÍVEIS.** | a câmara vê-os sempre. Se só aparece **um**, o outro **não desapareceu** — está lá. **Vai procurá-lo** *(ver 4)*. |
| **4** | 🔗 **CONTINUIDADE** *(J5 — "a única regra que ACRESCENTA informação")*. **"Se não os vês, temos de PERCEBER PORQUÊ não os vês."** Visto no frame 100 e no 104 ⇒ **interpola** 101-103. | **A ausência NÃO é um buraco. É uma pergunta.** ⚠️ **NÃO é um filtro** — não se descarta o frame. **PREENCHE-SE.** |
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
| S2 | **Formação de serviço** — parceiro na rede + adversário cruzado atrás. **0 falsos.** | ⚠️ correta mas **cega**: exige ver os 4 jogadores, e a câmara não vê os de baixo. Substituída por S3. | `formacao_servico()` |
| S3 | **Formação lida SÓ nos 2 de cima** ← **a decisão de hoje** | ✅ implementada (12 jul) | `formacao_de_cima()` |
| S4 | **Quadrado de serviço cruzado** — a bola do serviço cai na **diagonal**. **0 falsos.** | ⚠️ implementada, mas precisa do ressalto (bola a 46% → subir para 76% com thr=0.4) | — |
| S5 | **Serviço multi-fator** — nenhum sinal sozinho chega; combinar. | ✅ é a arquitetura atual | — |
| S6 | **Alternância** — os serviços alternam de lado. **Mas o lado só muda quando o PONTO CONTA**: falta/let repete o mesmo lado ⇒ numa corrida do mesmo lado, o que vale é **o ÚLTIMO**. | 📋 por implementar. ⚠️ **NÃO é lei** — no **ponto de ouro** quem recebe escolhe o lado e pode repetir. | `m1_tempo_util.py` |
| S7 | **Lado do serviço** distingue **ace** de **falta**. | 📋 por implementar | `SPEC_M1_TEMPO_UTIL.md` |
| S8 | **Ponto só acaba se a próxima pancada for serviço** | ⛔ **BLOQUEADA pelo M3.** Tentada a sério (13 jul) e **rejeitada**: 98,9 recall mas **47,1 precisão**, 5 segmentos colados. Sem detetor de serviço, as **pancadas do INTERVALO** entram pelo meio e esticam cada ponto até ao seguinte. **A regra é boa — o que falta é o serviço.** Não voltar a tentar sem M3. *(Estava marcada "✅ nas regras v9" e NUNCA correu.)* | — |
| **S9** | 🔴 **A SEQUÊNCIA DO SERVIÇO** (12 jul) — `SAI DA MÃO → CHÃO → RAQUETE → RESSALTO DENTRO DO QUADRADO CRUZADO → pancada seguinte segue o ponto`. **Sem ressalto no quadrado cruzado NÃO HÁ SERVIÇO** (condição necessária, não pontuação). E: **não disparar serviços só pela estrutura** (estarem todos posicionados). | 🔴 **é a especificação**. Bloqueada pelo detetor de ressalto (4/12). | `m1_tempo_util.py` |
| S10 | **Duplo ressalto** — o serviço é a **única** jogada em que a bola ressalta **obrigatoriamente dos dois lados** da rede (o servidor deixa-a cair; e tem de ressaltar no quadrado antes de o recetor lhe bater). **Corolário:** os dois ressaltos estão em lados opostos ⇒ **um está SEMPRE em cima** (o lado que a câmara vê). O de baixo pode estar **tapado pelo jogador** — não invalida. | 📋 por implementar | — |
| S11 | **Mudança de servidor** — 2 pontos válidos seguidos do mesmo lado ⇒ mudou o jogo ⇒ serve o outro par. | ⚠️ **pista fraca**: no **tie-break** o serviço roda a cada 2 pontos e isto não vale. | — |

| **S12** | **FIM DO PONTO — 4 s depois da última PANCADA.** Se não se detetar pancada nenhuma, corta com **2-3 s** de margem. *(Substitui os dois erros anteriores: cortar quando a bola deixa de cruzar = **cedo demais**; esticar enquanto a bola andar = **tarde demais** — "a bola pode andar e já ter batido duas vezes".)* | ✅ implementada (v7/v8) | `m1_tempo_util.py` |
| **S13** | ⏱️ **A TIMELINE NUNCA ANDA PARA TRÁS.** Um segmento nunca se sobrepõe ao anterior nem repõe um frame já usado. **Se dois segmentos se tocam, são O MESMO PONTO** — fundem-se. | ✅ implementada (v8). Corrigiu **6 saltos para trás** e arrumou 21 segmentos em **15 pontos** (os reais são 12). | `m1_tempo_util.py` |
| S14 | **Fim verdadeiro do ponto** = a bola bate **DUAS VEZES no chão sem ninguém lhe tocar**. | 📋 a regra certa, **bloqueada** pelo detetor de ressalto (7/12). O S12 é a aproximação enquanto isso. | — |

| **S15** | 🔴 **MÃO vs RAQUETE** — *"NÃO DISPARAR SERVIÇOS. Só disparar se a bola vier da mão para o chão para a raquete."* A bola da **mão é LENTA**; a da **raquete é RÁPIDA**. Medido no `L` do BlurBall: **serviços L=17,4 · falsos (passagens à mão) L=2,7**. | ✅ implementada. **+18 pontos de PRECISÃO** (65,8% → 83,9%). Mata 24 dos 27 falsos. | `m1_tempo_util.py` |
| **S16** | ⚖️ **DÚVIDA = MAIS MARGEM; CERTEZA = CORTE RENTE.** Se há pancada detetada → sei que acabou → corto a **2 s**. Se NÃO há pancada → estou na dúvida → dou **5 s**. *(Eu tinha implementado ao CONTRÁRIO — 4 s quando sabia, 2 s quando duvidava. Cortava os pontos 12/13/14 a meio.)* **Os 5 s são para DECIDIR, não para MOSTRAR.** | ✅ implementada. **+9 pontos de precisão** (83,9% → 92,9%). | `m1_tempo_util.py` |
| **S20** | ⏸️ **A PAUSA ENTRE PONTOS — 5 a 15 s.** *(estava nos prompts v7.1/v7.7/v8 e **NUNCA foi implementada** — ver `REGRAS_PERDIDAS_dos_prompts.md`)*. Uma pausa **curta demais é IMPOSSÍVEL**: entre pontos os jogadores têm de **ir buscar a bola** e **posicionar-se**. Se o pipeline produz uma pausa de **2,6 s**, a **CAUDA** do segmento anterior está esticada — **e não é preciso saber PORQUÊ para a aparar.** <br>🧠 **APRENDIDA POR DUPLA** *(Vasco, 13 jul: "tem uma **média associada a cada jogador**, que podes ir notando ao longo do vídeo")*: **2 passagens** — a 1.ª observa as pausas do **próprio vídeo**; a 2.ª usa `mediana − 2,5×MAD`. **Zero números meus.** <br>🔒 **Chão de segurança: 4 s** (Vasco). ⚠️ **SÓ APARA A CAUDA — nunca toca no INÍCIO do seguinte** ⇒ **estruturalmente incapaz de perder um serviço** (recall intacto até aos 6 s, medido). | ✅ **implementada (13 jul).** **+1,8 precisão** (93,9 → 95,7). **RESOLVEU A CAUDA DO PONTO 1** (3,5 s → 1,2 s) — que **nenhuma outra regra apanhava**: a raquetada que a esticava era do **INTERVALO**, com um jogador ao pé, **indistinguível de jogo**. Só o M3 a mataria. **Esta mata-a de graça, sem saber o que lá está.** | `gerar_tempo_util.pausa_aprendida()` |
| **S17** | 🔒🔒 **FECHADA — "a regra da rede está perfeita! fixa e não deixes mudar."** (Vasco, 13 jul) **`RED_DTHETA` / `RED_L_PARA` / `RED_DIST` NÃO SE MEXEM.**<br>**BOLA NA REDE → fim certo, corte a 0,5 s.** ⛔ **A POSIÇÃO NÃO SERVE** — nesta câmara a bola que passa POR CIMA e a que BATE ocupam **os mesmos píxeis** (banda da rede = 35 px; meio-campo do fundo = 100 px). 60 de 94 candidatos caíam **a meio de pontos reais**. ✅ **O que serve (Vasco, 13 jul):** *"se a bola **muda de direção** (ou **pára**) na rede, **longe de uma bounding box** → o ponto acabou."* A bola que passa **não vira**. A que bate, **vira ou morre**. E se não há jogador ao pé, **não foi ninguém: foi a rede.** | ✅ **implementada (13 jul)**. 0 eventos a meio de pontos · 4 no fim (pts 2,3,5,10). **+4,1 precisão.** | `gerar_tempo_util.fim_certo()` |
| **S23** | 🔴🔴 **O QUIQUE DO SERVIÇO** *(Vasco, 13 jul — **a regra que desbloqueou a faixa da rede**)*<br>*"Temos de matar este lixo pela **bola na mão do NÃO SERVIDOR — ANTES de bater no chão**."*<br>*"Mesmo que tenha kick, **só o ÚLTIMO** antes da mudança de direção para o outro campo **conta**."*<br>**A LEI:** **NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.**<br>• o **servidor** larga a bola → ela **QUICA** (na linha de serviço) → e **só depois** bate<br>• o **não-servidor** tem a bola na mão → **passa-a / atira-a** ⇒ **SEM QUIQUE**<br>⇒ um segmento **sem quique fundo** antes da 1.ª travessia **NÃO É UM PONTO**.<br>🔑 **"Só o último conta"**: a bola quica várias vezes no intervalo. O quique do **serviço** é o **último antes de mudar de campo**. *(Com o primeiro, os inícios fugiam 2 s para trás.)* | ✅ **implementada (13 jul).** **13/13 pontos reais têm quique fundo** (prof 1,04–1,45) · **o lixo tem ZERO**. **Separação perfeita, sem afinar nada.** Vale **+3,5 de precisão**. 🔓 **É ela que permite AMPLIAR o `MIN_PROF` (0,35→0,15)** — e a ampliação tira os pontos 10 e 11 de cima de **uma travessia única** (1→3), que era o **risco real** para o 2.º vídeo. ⚠️ **1.ª vez que o RESSALTO entra no pipeline.** Se o 2.º vídeo perder pontos, **desligar isto primeiro**. | `gerar_tempo_util.quique_do_servico()` |
| **B11** | 🕳️ **A FAIXA CEGA À VOLTA DA REDE** *(Vasco, 13 jul: "os de cá, perto da rede, devolvem a bola muito **alta e perto da rede** — não dá tempo à bola de passar, nos frames")*. O `MIN_PROF` ignorava tudo num raio de **35% do meio-campo** à volta da rede ⇒ o **VOLLEY à rede** atravessava e **morria lá dentro, invisível**. **O código via 52% das travessias.**<br>⛔ **A correção geométrica (ler a travessia pelo TOPO da rede em vez da base) está CERTA mas quase não muda nada** — as duas linhas estão a 35 px, **ambas dentro da faixa cega**. Quem faz o trabalho é a **largura da faixa**, não o divisor. | ✅ **`MIN_PROF` 0,35 → 0,15 (13 jul).** ⚠️ **SÓ porque a S23 mata o lixo que isto trazia. AS DUAS ANDAM JUNTAS.** | `gerar_tempo_util` |
| **S18** | 🔴 **MÃO/CORPO NA BOLA → fim certo, corte a 0,5 s.** *(Vasco, 13 jul: **"bola PARADA dentro da bounding box, SEM MUDAR DE CAMPO → ponto terminado de certeza, sem raquetada."**)* **As três condições são precisas as três:** **parada** (`L≤3`) · **dentro da box** (é a mão/corpo de alguém) · **sem mudar de campo** (se atravessou a rede, foi **batida**). ⛔ A bola lenta sozinha dá **49 falsos a meio de pontos** — o lob também vai lento no ponto alto. 🔒 **A DURAÇÃO (0,5 s) NÃO SE BAIXA:** a 0,3 s corta pontos a meio e o recall cai de 96,2 para **82**. **É a duração que separa a MÃO do LOB** (o lob vai lento — mas um *instante*). E: **jogadores a passar a bola com a mão ⇒ o ponto JÁ acabou e ainda NÃO começou.** | ✅ **implementada (13 jul)**. **0 eventos a meio de pontos.** | `gerar_tempo_util.fim_certo()` |

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
| **D1** | 🤔 **EM DÚVIDA, MANTÉM O ESTADO ANTERIOR** *(lei de desenho)*. *"A fase só muda quando a mudança é **visualmente clara** — em dúvida, **mantém a fase anterior**."* (v1 §3, v3 P4) **Histerese: o estado tem INÉRCIA.** Mesma família da S16 (dúvida = mais margem), mas aplicada às **fases**. ⚠️ É o **antídoto para o jitter** — o inimigo nº 1 do M2. | 🔴 por implementar | — |
| **D2** | 🚫 **NÃO INVENTAR. SE NÃO ANCORA, OMITE.** *(lei de desenho)*. *"**Nunca** inventas timestamps por estimativa — se não consegues ancorar num **evento visual claro**, **omite o evento**."* (v1, v3) **O Vasco escreveu isto há um MÊS.** É a mesma lei que impôs hoje — *"NÃO INVENTAR NEM ATALHAR"* — e que me apanhou **três vezes num só dia**. **Não é um detalhe do prompt: é a LEI DO PROJETO, e já estava escrita.** | ✅ **é a lei que rege tudo** | — |
| **M2-1** | 🚦 **DEFESA → ATAQUE sem passar por TRANSIÇÃO é PROIBIDO.** *Exceção: se foi rápido demais para captar, aceita o salto.* (v1 §3, v3 P4) | 🔴 por implementar (M2) | — |
| **M2-2** | 📉 **`confianca` 0.0–1.0 em cada entrada; < 0,6 quando há dúvida.** (v3 P4) Disciplina de **incerteza explícita**. | 🔴 por implementar | — |
| **M2-3** | ⏱️ **Rallies < 5 s: omite as FASES, mas NUNCA o RALLY.** *"Não omites rallies curtos."* (v3 P10) Bate certo com a diretriz: **nunca perder um ponto**. | 🔴 por implementar | — |
| **C6** | 📷 **A câmara é FIXA, lateral, a meia altura.** (v3, Geometria) **É o PRESSUPOSTO de todo o sistema.** O 2.º vídeo vai testá-lo. | 📋 registar | — |

## CAMPO / GEOMETRIA

| # | Regra | Estado |
|---|---|---|
| C1 | **Novo campo = nova calibração** à mão, no `calibrar_campo.html`. Não auto-detetar. | ✅ |
| C2 | **A malha 2/3 nunca se deteta** — não é linha branca. Tem sempre de ser desenhada. | ✅ |
| C3 | **A central sai dos pontos do meio** das linhas de serviço + base da rede. Não se marca — calcula-se. | ✅ |
| C4 | **Os extremos das linhas são os cantos** — daí saem as laterais. (Cuidado: descartar os que tocam a **borda do frame**, que não é o vidro.) | ✅ |
| C5 | **3 pontos = curvatura; 2 pontos = herdam-na.** A lente curva as linhas. | ✅ |

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
