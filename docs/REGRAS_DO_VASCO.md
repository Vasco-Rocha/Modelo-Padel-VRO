# As regras do Vasco — inventário completo

Todas as regras que vieram do Vasco, o que fazem, e onde estão.
**As melhores ideias do projeto vieram daqui.** Não perder nenhuma.

Última atualização: 12 jul 2026.

---

## BOLA

| # | Regra | Estado | Onde |
|---|---|---|---|
| B1 | **Objetos imóveis** — um objeto no mesmo píxel, espalhado por >35% do vídeo, não é a bola. A bola nunca pousa duas vezes no mesmo sítio. | ✅ implementada. Apanha 4 objetos. **Sobe a precisão sem custar recall.** | `filtrar_objetos_imoveis()` |
| B2 | **Continuidade** — a bola não se teletransporta (`vmax=80 px/frame` ≈ 100 km/h). Salto impossível = outro objeto. *Não precisa de conhecer o inimigo.* | ✅ implementada | `filtrar_continuidade()` |
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
| J9 | **Cor reiniciada por ponto** — aprender as cores no **início de cada ponto** (jogadores separados, parados, em formação = o frame mais limpo do jogo). | ⛔ **bloqueada**: precisa de saber onde começam os pontos, que é o que o M1 tenta descobrir. **Dependência circular.** Fazer em 2.ª passagem. | — |

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
| S8 | **Ponto só acaba se a próxima pancada for serviço** | ✅ nas regras v9 | — |
| **S9** | 🔴 **A SEQUÊNCIA DO SERVIÇO** (12 jul) — `SAI DA MÃO → CHÃO → RAQUETE → RESSALTO DENTRO DO QUADRADO CRUZADO → pancada seguinte segue o ponto`. **Sem ressalto no quadrado cruzado NÃO HÁ SERVIÇO** (condição necessária, não pontuação). E: **não disparar serviços só pela estrutura** (estarem todos posicionados). | 🔴 **é a especificação**. Bloqueada pelo detetor de ressalto (4/12). | `m1_tempo_util.py` |
| S10 | **Duplo ressalto** — o serviço é a **única** jogada em que a bola ressalta **obrigatoriamente dos dois lados** da rede (o servidor deixa-a cair; e tem de ressaltar no quadrado antes de o recetor lhe bater). **Corolário:** os dois ressaltos estão em lados opostos ⇒ **um está SEMPRE em cima** (o lado que a câmara vê). O de baixo pode estar **tapado pelo jogador** — não invalida. | 📋 por implementar | — |
| S11 | **Mudança de servidor** — 2 pontos válidos seguidos do mesmo lado ⇒ mudou o jogo ⇒ serve o outro par. | ⚠️ **pista fraca**: no **tie-break** o serviço roda a cada 2 pontos e isto não vale. | — |

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
