# 🕳️ Regras perdidas — AUDITORIA DOS PROMPTS **ORIGINAIS** (v2) — **FECHADA**

**13 jul 2026.** O Vasco: *"está tudo guardado nos registos. Se fores a fundo, sem pressa, a todos
os prompts — desde o prompt Gemini inicial ao v9 — **todas as regras que me fui lembrando passaram
por lá**."*

> ## 🚨 A 1.ª auditoria leu o ficheiro ERRADO.
> Confrontou o **`REGRAS_CONSOLIDADAS_todos_prompts.md`** — que é um **RESUMO** escrito por um
> Claude. **Um resumo também perde regras.** Um mapa feito a partir de um mapa.
> ⇒ **A FONTE são os prompts ORIGINAIS.** Esta auditoria leu-os **todos, inteiros**.

---

## ✅ AUDITADOS — **TODOS** (nada por ler)

| ficheiro | data | o que é |
|---|---|---|
| `prompt_gemini_analise_padel.md` **(v1)** | 14 jun | o mais antigo e o **mais detalhado** |
| `prompt_gemini_analise_padel_v3.md` **(v3)** | 16 jun | simplificou para 3 zonas |
| `prompt_padel_v7.1.md` | 16 jun | 3 módulos desacoplados · % de altura · **áudio** |
| `prompt_padel_v7.7.md` | 17 jun | % → **marcas físicas** |
| `prompt_padel_v8.0.md` | 17 jun | matriz de confronto |
| `prompt_padel_v9_MASTER.md` | 21 jun | **regra das 2 boxes** · 6 s · fim imediato |
| `prompt_analise_padel_v9.md` | 18 jun | v9 de referência (com o porquê) |
| `prompt_analise_padel_v9_GEMINI.md` | 21 jun | v9 pronto a colar |
| `prompt_modelo_hibrido_v9.md` | 17 jun | prompt vs modelo vs geometria |
| `REGRAS_BOLA_PARA_CODIGO.md` | 5 jul | v9 → código (R1–R16) |
| `AFINAR_TEMPO_UTIL.md` · `_v2.md` | 5/9 jul | os 3 botões |
| `PLANO_TEMPO_UTIL_pos_BlurBall.md` · `PLANO_DETETOR_TEMPORAL.md` | 10/11 jul | |
| `padelpro-vision/docs/` — **os 18 ficheiros** | | inclui o **`SPEC_M1_TEMPO_UTIL.md`** ⭐ |

⭐ **O achado maior não estava num prompt — estava no `docs/SPEC_M1_TEMPO_UTIL.md`.** Ver §1.

---

# 🔴 AS 4 REGRAS DA 1.ª PASSAGEM (v1 + v3)  — *já levadas ao inventário*

1. 👕 **A camisola muda UMA de cada vez** — *"pode mudar durante a pausa, **mas não de todos em
   simultâneo** — atualiza **só o jogador que mudou**"* (v1 §6) → **J10**
2. ↔️ **O lado não muda dentro do rally** — só em trocas de campo (v3, Geometria) → **J11**
3. 🤔 **Em dúvida, mantém o estado anterior** (v1 §3, v3 P4) → **D1**
4. 🚫 **Não inventar: se não ancora, omite** (v1/v3, Regras de Timestamp) → **D2**

---

# 🟥 AS REGRAS NOVAS DESTA PASSAGEM (v7.1 → v9 → docs)

## 1. ⭐⭐ A ALTERNÂNCIA DAS TRAVESSIAS — *a maior de todas, e nunca implementada*
> *"As pancadas **alternam** entre campo de baixo e campo de cima. Uma equipa **não bate 2x seguidas**.
> Logo **cada TRAVESSIA DA REDE implica uma pancada** no campo de origem — não é preciso *ver* a
> pancada; **a física garante-a**. Robusto a oclusão e a bola fora do frame. (…)
> **Travessias alternadas e sustentadas = rally em curso.** Entre pontos a bola cruza a rede **no
> máximo uma vez** (devolvida ao servidor), **não faz vaivém**.
> → **É o melhor sinal de jogo/não-jogo que temos** — melhor que presença ou velocidade da bola.
> Dá precisão **sem** sacrificar recall."*
> — `docs/SPEC_M1_TEMPO_UTIL.md`, "Regra da ALTERNÂNCIA"

🎯 **Isto ataca EXACTAMENTE o problema que está registado como insolúvel.** A memória diz:
*"45 % das deteções caem nos INTERVALOS e são bola a sério. **Nenhum detetor resolve.**"*
Certo — **nenhum DETETOR**. Mas isto não é um detetor: é uma **estrutura**. A bola do intervalo
(apanhar, passar, preparar) **não faz vaivém pela rede**. O jogo faz.
👉 **A regra existe, está escrita, e nunca correu.** → **S21**

## 2. 🎾 O LADO DO SERVIÇO — ace vs falta, **sem homografia**
> *"Depois de um **ponto concluído** (ace incluído) → o serviço seguinte vai para o **lado OPOSTO**.
> Depois de uma **FALTA** → repete-se para o **MESMO lado**. **É a única vez que isso acontece.**
> Logo: **falta + 2.º serviço = UM ponto, não dois** → corrige a sobre-contagem de rallies. (…)
> **Auto-verificação de graça:** a sequência de lados tem de alternar (exceto após falta). Se não
> alternar e não houver falta → detetámos um serviço a mais **ou perdemos um**. **Sinal de erro sem
> precisar do ground-truth.**
> Lado = `x` do centro da box do servidor vs `x` do meio do campo. **Sem calibração nova."*
> — `docs/SPEC_M1_TEMPO_UTIL.md` → **S22** *(a S6/S7 tinham só metade disto)*

## 3. 🖐️ FIM IMEDIATO — **um jogador TOCA NA REDE** (raquete ou corpo)
> *"se a bola **sai de campo** ou um jogador **toca na rede**, o ponto acaba aí (sem esperar os 6 s)"*
> — v9 MASTER M1.3 · v9 GEMINI r3 · v1 §5.4 · v3 P7.4 → **S25**
> ⚠️ Está nos prompts **desde o v1** (14 jun). Nunca foi implementada.

## 4. 🏓 FIM — **a mesma equipa bate DUAS VEZES seguidas** (toque duplo)
> *"a mesma equipa tocou nela duas vezes seguidas"* — v1 §5.1 · v3 P7.1
> *"Duas pancadas seguidas no mesmo campo = **impossível** → uma é espúria **OU o ponto acabou**"*
> — `SPEC_M1` · `REGRAS_BOLA_PARA_CODIGO.md` R13 → **S26**

## 5. ⏱️ A REGRA DOS 6 s — **aplica-se SEMPRE, mesmo sem ver a bola**
> *"Mais de **6 segundos** sem nenhuma pancada de nenhum jogador (…) **Aplica-se sempre,
> independentemente de a bola ser detetável ou não.**"* — v1 §5.2 · v3 P7.2
> *"a última pancada só é confirmada como fim depois de **esperar 6 s**. Nesses 6 s: se aparecer
> outra pancada que **não** seja serviço → o ponto **não tinha acabado**. (…) Os 6 s são uma **rede de
> segurança** para o caso de uma pancada de um dos lados **não ser detetada**."* — v9 M1.2
> *(O Vasco reduziu 6→5 s — `REGRAS_BOLA_PARA_CODIGO.md` R5.)* → **S29**
> 🔑 **É a peça que faltava à S8.** A S8 morreu (98,9 recall / **47,1** precisão) porque **esperava
> pelo serviço seguinte sem TETO**. Os 6 s são o teto. **A S8 nunca foi testada com a sua rede de
> segurança.**

## 6. 🚫 A BOLA FORA DO **ENQUADRAMENTO** NÃO TERMINA O RALLY
> *"«Inatividade» refere-se a **PANCADAS e JOGADORES**, **nunca** à bola estar fora do frame."*
> — v9 MASTER M1.4 · v9 GEMINI r4 · R4 → **B11**

## 7. 🧍 INATIVIDADE DOS JOGADORES — e **a proibição de adivinhar**
> *"se **TODOS** os jogadores estiverem visíveis e ~3 s parados, confirma o fim sem esperar os 6 s.
> **Se não vires todos, NÃO adivinhes** — usa só os 6 s."* — v9 M1.5 → **S30**

## 8. ✂️ A MARGEM DE +2 s É PARA **VER**, NÃO PARA **CONTAR**
> *"acrescenta **+2 s** depois desse ponto — **apenas como margem visual** (não é deteção)"* — v9 M1.6
> *"**Não conta** no tempo útil estatístico."* — R8 → **S31**
> *(Irmã da S16: "os 5 s são para DECIDIR, não para MOSTRAR". Esta é o inverso: para MOSTRAR, não
> para CONTAR.)*

## 9. 🕊️ A SALVAGUARDA DO SERVIÇO PERDIDO
> *"Se um serviço **não** for detetado mas houver **jogo evidente**, o segmento **entra na mesma**,
> marcado `confianca: baixa`. **Colar dois pontos é mau; perder um ponto é pior.**"* — `SPEC_M1`
> → **S32**

## 10. 🎯 O SERVIÇO — **as 6 condições** (A–F), e a que faltava
> A. bola na mão · B. **desce e RESSALTA aos pés do servidor** · C. raquetada · D. servidor atrás da
> linha · E. formação · **F. o servidor ARRANCA a seguir (sobe à rede)** — `SPEC_M1`
> *"É o **ressalto (B)** que distingue um serviço de qualquer outra bola que sai de uma mão."*
> **A F nunca esteve registada.** → **S23**

## 11. ⬇️ O SERVIÇO É **POR BAIXO** — a bola **não sobe**
> *"No padel o serviço é **por baixo** — a bola **não sobe**. O sinal é o **arranque horizontal**
> **depois** do ressalto."* — `SPEC_M1` · `PLANO_TEMPO_UTIL_pos_BlurBall` · `ANOTACAO_E_RETREINO`
> → **S24**

## 12. 🧭 DISTINGUIR RESSALTO / PANCADA **SEM PLANO DO SOLO**
> | evento | sinal |
> |---|---|
> | **Ressalto no chão** | inversão da velocidade vertical **SEM jogador perto** |
> | **Pancada** | mudança brusca de direção **COM jogador perto** |
> | **Ressalto do serviço** | inversão vertical **com** jogador perto, a **baixa velocidade**, seguida de pico |
>
> *"Referência do chão **para o serviço** = a **base da box do servidor** (`y2`) — a bola ressalta aos
> pés dele. **Poupa uma calibração** e é mais robusto."* — `SPEC_M1` → **S35 · S36**
> ⚠️ **Confronta com o bloqueio de 13 jul** (*"o ressalto não se resolve desenhando — falta
> profundidade"*). Esta tabela **não usa profundidade nenhuma** — usa a **proximidade a um jogador**.
> **Nunca foi tentada assim.**

## 13. 🔊 O ÁUDIO
> *"Usa o **som de impacto de raquete** na bola ou o **bounce** da bola no chão para confirmar que o
> rally está a decorrer. **Ignora conversas entre jogadores — estas ocorrem entre pontos.**"*
> — v7.1 M1.4 · v7.7 M1.4 · R15 → **P6**
> *(Desapareceu na v8.0 e nunca voltou. O MATCHi TV não tinha áudio — **o 2.º vídeo vai ter**.)*

## 14. 📸 A ANCORAGEM DA PANCADA É NO **CORPO**, NÃO NO IMPACTO
> *"O timestamp deve coincidir com o **movimento biomecânico** (preparação/extensão do braço),
> **não com o impacto da bola, que é demasiado rápido para ser capturado com precisão**."*
> — v7.1 M3.5 · v7.7 → **P4**

## 15. 📏 PRECISÃO HONESTA — `margem_ms`
> *"**Não finjas precisão absoluta.** Para cada timestamp dá também `margem_ms` (…). Se a incerteza
> for grande, **aumenta a margem e baixa a `confianca`**. (Usa-se ms e não frames para ser
> **independente do FPS**.)"* — v9 §0.1b → **D3**

## 16. 🗣️ O VOCABULÁRIO É FECHADO — e a dúvida tem nome
> *"Se não conseguires classificar com segurança, devolve **`indeterminado`** e **`confianca: baixa`**.
> **Nunca inventes uma entrada, pancada ou transição sem uma âncora visual.**"* — v9 §0.3 → **D4**

## 17. 👁️ OBSERVAR ANTES DE CLASSIFICAR
> *"Descreve segundo a segundo apenas o que **observas visualmente**. **Não classifiques ainda a
> fase**; isso é feito depois no JSON."* — v7.1 M2.2
> *"O bloco de raciocínio é obrigatório e **precede sempre** o JSON. **O JSON tem de ser consistente
> com o raciocínio.**"* — v9 §0.5 → **D5**
> *(E os módulos são **desacoplados** "para evitar alucinações" — v7.1, Contexto.)*

## 18. ✅ AUTO-VERIFICAÇÃO OBRIGATÓRIA ANTES DE EMITIR
> Checklists explícitas em todos os v9: `total_rallies` = nº de entradas · `fim > inicio` · sem
> sobreposições · cada rally começa num serviço · *"não declaraste inatividade sem todos os jogadores
> visíveis"*. → **D6**  *(a S13 — "a timeline nunca anda para trás" — é **um item desta checklist**,
> que já lá estava escrito em junho.)*

## 19. 🚫 NUNCA OMITIR UM **RALLY** *(≠ omitir um EVENTO)*
> *"Se um segmento for ambíguo, marca-o com `confianca: baixa` **em vez de o omitir ou duplicar**."*
> — v9 M1.5 · *"**Não omites rallies curtos**"* — v3 P10 → **D7**
> 🔑 **Resolve a tensão com a D2.** *Omite o **evento** que não ancoras. **Nunca** omitas o **ponto**.*

## 20. 🧱 A REGRA DAS DUAS BOXES + TRANSIÇÃO É O **ESTADO-RESÍDUO**
> *"Só é DEFESA se forem **ambos** atrás da linha de serviço; só é ATAQUE se forem **ambos** à frente
> da interceção malha 3/2. **Qualquer outra configuração = TRANSIÇÃO.**"* — v9 §1 → **F2**
> E: *"a posição é sempre a **aresta inferior da box** — **nunca** cabeça, tronco ou raquete"* → **F3**

## 21. 🧊 ANTI-JITTER — o cruzamento tem de ser **CLARO**
> *"Se a box apenas **toca, treme ou oscila** em cima da marca sem a atravessar de forma **estável**,
> **NÃO** abras nova entrada."* — v9 M2.6 → **F5** *(irmã da D1: o estado tem inércia)*

## 22. 🔍 MAXIMIZA A GRANULARIDADE *(só nas FASES)*
> *"Na dúvida entre **fundir ou separar**, **SEPARA**. É preferível um clip a mais do que perder uma
> transição."* — v9 M2.5 → **F9**
> ⚠️ **É o CONTRÁRIO da S13** (*"se dois segmentos se tocam, são o mesmo ponto — fundem-se"*).
> **Não é contradição: são domínios diferentes.** Nos **PONTOS** funde-se (um ponto é um ponto). Nas
> **FASES** separa-se (uma transição perdida não se recupera).

## 23. 👕 A ASSINATURA VISUAL TEM **CINCO** ELEMENTOS — não quatro
> *"camisola · **calções** · **meias** · **ténis** · **RAQUETE**"* (v1 §1, v3 P2).
> A **J6** registou *"torso + calções + pernas + ténis"* — **perdeu as MEIAS e a RAQUETE**.
> E: *"Se dois jogadores tiverem elementos similares, usa a **combinação dos restantes fatores**."*
> → **J12 · J13**

## 24. ⏸️ A PAUSA > 45 s TEM **QUATRO** SIGNIFICADOS — não um
> `troca_de_campo` (jogadores do lado oposto) · `discussao`/timeout (mesmo lado, reagrupados) ·
> `lesao` (dispersos, câmara foca um) · `indefinido` — v1 §6 · v3 P8 → **S38**
> *(O inventário só tinha "pausa > 45 s ⇒ troca de campo". **Nem toda a pausa longa é uma troca.**)*

## 25. 🎾 VALIDADE DO SERVIÇO — **let** e **falta**
> ✅ **Válido:** cai no quadrado cruzado sem tocar na malha · 🔄 **Let:** toca na tela **e cai dentro**
> → **repete** · ❌ **Falta:** toca na malha e não entra; **ou o recetor não jogou**; ou muda o servidor
> — v1 §4 · v3 P6 · R12 → **S33**

## 26. 🥈 A "2.ª BOLA"
> *"A **primeira pancada da equipa recetora após o serviço** é a «2.ª bola». `segunda_bola: true`."*
> — v1 §3 → **S34** *(marca analítica; não afeta o timing)*

## 27. 🏔️ **QUANDO O CHÃO FALHA, SOBE** *(a regra de ouro do padel)*
> *"O padel é o único desporto com uma **estrutura 3D rígida e normalizada**. (…) topos de vidro,
> cantos superiores, postes. **Estes pontos estão altos — são os últimos a sair do enquadramento e
> NUNCA são tapados por jogadores.** Quando os cantos do chão desaparecem, os cantos *superiores* das
> paredes ainda lá estão."* — `docs/BENCHMARK_calibracao_campo.md` §4.1 → **C7**
> 🎯 **É uma resposta possível ao bloqueio do RESSALTO** (*"falta profundidade"*): a profundidade que
> falta **não está no chão** — está nas **verticais**.

## 28. 📷 A CÂMARA PODE **DERIVAR**
> *"A FIFA **recalibra antes do jogo e ao intervalo** — para compensar a **dilatação térmica dos
> suportes**. «Câmara fixa = calibrar uma vez para sempre» **pode ser otimista demais**. Vale a pena
> verificar se a calibração do Parada4 ainda assenta **noutro vídeo do mesmo campo**."*
> — `docs/BENCHMARK_inferir_linhas.md` §1 → **C12** ⚠️ **O 2.º vídeo é o teste.**

---

# 🚨 CONTRADIÇÕES ENCONTRADAS — **não mexi em nada. Decide o Vasco.**

### ① A C6 ESTÁ ERRADA — a câmara **não** é lateral
| fonte | diz |
|---|---|
| **v3** (Geometria) | *"A câmara está fixa no **lado longo** do campo (**lateral**), a **meia altura**"* |
| **v1** §1 · **v7.1** · **v7.7** · **v8.0** · **v9** (todos) | *"A câmara é **FRONTAL**"* / *"SEMPRE posicionada no **vidro de fundo**"* |
| **o `calibracao_campo.json` e todo o código** | **frontal** |

A **C6** do inventário — *"a câmara é FIXA, **lateral**, a meia altura"* — copiou a **v3**, que é a
**única** versão que diz isso, e **está errada**. A v3 é de 16 jun; a v7.1 (mesmo dia) já corrige
para frontal. **Proposta: C6 → "FRONTAL, fixa, atrás do vidro de fundo, 960×540".**

### ② A ORDEM DA CASCATA DOS JOGADORES ESTÁ TROCADA
| fonte | ordem |
|---|---|
| **`REGRAS_DO_VASCO.md`** (a cascata) | 1 pés · **2 nunca mais de dois** · 3 os de cima visíveis · **4 continuidade** |
| **`docs/HANDOFF_JOGADORES.md`** | 1 fora do campo + imóveis · **2 CONTINUIDADE** · **3 dois por lado** |

E o handoff diz **porquê**, explicitamente:
> *"A continuidade tem de vir **antes** do «2 por lado»: **se cortarmos primeiro, podemos deitar fora
> o jogador verdadeiro e ficar com o falso**."*

**O inventário tem a ordem ao contrário — e a ordem é a regra.** *(A memória do projeto também diz
"fora-do-campo → continuidade → 2-por-lado".)* **Proposta: corrigir a cascata.**

### ③ O SERVIÇO É "ATAQUE" (v1/v3) OU "TRANSIÇÃO" (v9)?
> **v1 §3 / v3 P4:** *"O serviço **não é uma fase separada** — é um **momento dentro do ATAQUE**.
> **Quando o servidor está no FUNDO e o parceiro está na REDE, a equipa está em ATAQUE.**"*
>
> **v9 §1:** *"só é ATAQUE se forem **ambos** à frente da interceção malha 3/2"* ⇒ servidor no fundo +
> parceiro na rede = **TRANSIÇÃO**.

**Contradizem-se de frente.** A v9 substituiu a regra sem registar a exceção do serviço. Se a regra
das 2 boxes correr no M2, **todos os serviços vão ser rotulados TRANSIÇÃO**. Decide o Vasco.

### ④ RALLIES CURTOS: DESCARTAR (código) ou NUNCA OMITIR (prompt)?
> **v3 P10:** *"❌ **Não omites rallies curtos** — rallies com menos de 5 s **entram no JSON**"*
> **`REGRAS_BOLA_PARA_CODIGO.md` R7 / `AFINAR_TEMPO_UTIL_v2`:** *"`min_rally_s=1.5` — **descarta**
> rallies mais curtos que isto"*

O código **deita fora** o que o prompt manda **guardar** — e o ponto 1 do ground-truth tem **3,5 s**.
⚠️ Um `min_rally_s` a 4,0 **apagava um ponto real**. Bate de frente com a **diretriz de produto**.

### ⑤ A NUMERAÇÃO **B8** ESTÁ A SER USADA POR DUAS REGRAS
- `REGRAS_DO_VASCO.md` **B8** = *coerência temporal* (vizinho em ±2 frames) — 🧪 por implementar
- `MAPA_DAS_REGRAS.md` **B8** = *vai-e-vem* (A→B longe, A→C perto ⇒ B é erro) — 🟢 **a correr**

**Duas regras, o mesmo nome.** É exactamente a doença da S12. → renumerei o *vai-e-vem* para **B14**.

---

## 📌 O MÉTODO, para a próxima
**A auditoria faz-se contra a FONTE, nunca contra um resumo.** E a fonte não são só os prompts:
**o `docs/SPEC_M1_TEMPO_UTIL.md` tinha a regra maior de todas** (a alternância) e **nunca foi lido
por ninguém desde que foi escrito**.

> Um documento que ninguém lê é igual a uma regra que não corre.
