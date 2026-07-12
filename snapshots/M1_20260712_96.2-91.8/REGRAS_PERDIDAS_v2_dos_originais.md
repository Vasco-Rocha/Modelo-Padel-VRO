# 🕳️ Regras perdidas — AUDITORIA DOS PROMPTS **ORIGINAIS** (v2)

**13 jul 2026.** O Vasco: *"está tudo guardado nos registos. Se fores a fundo, sem pressa, a todos
os prompts — desde o prompt Gemini inicial ao v9 — **todas as regras que me fui lembrando passaram
por lá**."*

> ## 🚨 EU AUDITEI O FICHEIRO ERRADO.
> A primeira auditoria (`REGRAS_PERDIDAS_dos_prompts.md`) confrontou o
> **`REGRAS_CONSOLIDADAS_todos_prompts.md`** — que é um **RESUMO** que eu próprio escrevi.
> **Um resumo também perde regras.** É a mesma doença: um mapa feito a partir de um mapa.
> ⇒ **A FONTE são os prompts ORIGINAIS.** É lá que estão as regras do Vasco, na forma em que ele
> as pensou.

---

## ✅ AUDITADOS
- `prompt_gemini_analise_padel.md` **(v1)** — o mais antigo e o **mais detalhado**
- `prompt_gemini_analise_padel_v3.md` **(v3)**

## ⏳ POR AUDITAR — **a fazer, com calma**
`prompt_padel_v7.1.md` · `prompt_padel_v7.7.md` · `prompt_padel_v8.0.md` ·
`prompt_padel_v9_MASTER.md` · `prompt_analise_padel_v9.md` · `prompt_analise_padel_v9_GEMINI.md` ·
`prompt_modelo_hibrido_v9.md` · `REGRAS_BOLA_PARA_CODIGO.md` · `AFINAR_TEMPO_UTIL*.md` ·
`PLANO_*.md` · `docs/`

---

# 🔴 AS 4 REGRAS ENCONTRADAS (v1 + v3) — nenhuma está no `REGRAS_DO_VASCO.md`

### 1. 👕 **A CAMISOLA MUDA UMA DE CADA VEZ** ⭐ *(a mais valiosa)*
> *"A camisola de um jogador **pode mudar** durante a pausa, **mas não de todos em simultâneo** —
> **atualiza só o jogador que mudou**."* — v1 §6

**É a salvaguarda que falta à regra da COR** que o Vasco deu hoje *(seguir o jogador pela roupa)*.
Se a identidade passa a ser a **cor**, o perigo é a cor "saltar" de pessoa para pessoa quando o
detetor se engana. Esta regra fecha essa porta: **as 4 assinaturas não mudam todas ao mesmo tempo.**
Se o código acha que mudaram todas, **o código é que está errado.**
👉 **Implementar JUNTO com a regra da cor. Uma sem a outra é perigosa.**

### 2. ↔️ **O LADO NÃO MUDA DENTRO DO RALLY**
> *"O lado dos jogadores **não muda** ao longo do rally — só muda em **trocas de campo**
> (pausa longa)."* — v3, Geometria

**Um invariante forte, e nunca usado.** Dentro de um ponto, quem está em cima **fica** em cima.
Isso **resolve ambiguidades de identidade de graça** — e combina com a regra da cor e com a
"2 por lado". *(E a troca de campo é detetável: pausa > 45 s + jogadores do lado oposto.)*

### 3. 🤔 **EM DÚVIDA, MANTÉM O ESTADO ANTERIOR** *(lei de desenho)*
> *"A fase só muda quando a mudança é **visualmente clara** — **em dúvida, mantém a fase
> anterior**."* — v1 §3 · v3 Passo 4

**Histerese.** O estado tem **inércia**: não se muda de estado por causa de um frame duvidoso.
É a mesma família da S16 (*dúvida = mais margem*) — mas aplicada às **fases**, não ao tempo.
⚠️ E é o antídoto para o **jitter**, que é o inimigo nº 1 do M2.

### 4. 🚫 **NÃO INVENTAR. SE NÃO ANCORA, OMITE.** *(lei de desenho)*
> *"**Nunca** inventas timestamps por estimativa — se não consegues ancorar num **evento visual
> claro**, **omite o evento**."* — v1 e v3, "REGRAS DE TIMESTAMP"
> *"**Não inventas fases** em rallies onde os jogadores não se mexeram visivelmente."* — v3 Passo 10

**Escrito pelo Vasco há um mês.** É a mesma lei que ele impôs hoje — *"NÃO INVENTAR NEM ATALHAR"* —
e que me apanhou **três vezes** neste único dia (o ground-truth, o mapa das regras, as 8 regras que
descartei com um raciocínio).
👉 **Não é um detalhe do prompt. É a lei do projeto, e já estava escrita.**

---

# 🟡 Outras coisas dos originais que não estão registadas

| | onde | nota |
|---|---|---|
| **`confianca` 0.0–1.0 em cada entrada; < 0,6 quando há dúvida** | v3 P4 | disciplina de **incerteza explícita** — nunca implementada |
| **Rallies < 5 s: omite as FASES, mas NUNCA o RALLY** (`fases_omitidas: true`) | v3 P4/P10 | *"não omites rallies curtos"* — bate certo com a diretriz **nunca perder um ponto** |
| **DEFESA → ATAQUE sem TRANSIÇÃO é PROIBIDO** *(exceção: rápido demais para captar)* | v1 §3 · v3 P4 | uma **lei de máquina de estados** do M2 |
| **`VF1`–`VF5`** — o vidro de fundo dividido em **5 zonas**, da direita para a esquerda | v1 §2 | vocabulário espacial **perdido** quando a v3 simplificou para 3 zonas |
| **Referência de posição = base da box (pés/ténis). NUNCA a cabeça ou o tronco.** | v1 §1 · v3 P2 | está implícito no código, **não está escrito como lei** |
| **A câmara é FIXA, lateral, a meia altura** | v3, Geometria | o **pressuposto** de todo o sistema. Vale a pena escrevê-lo — o 2.º vídeo vai testá-lo. |
| **Taxonomia das pancadas** (smash vs overhead · víbora · bandeja · kick · `saida_vidro`) | v1 §7 · v3 P5 | **é o M3.** Guardado, por implementar. |
| **Vídeos > 40 min: detalha os primeiros 30, resume o resto — mas NÃO omitas rallies** | v3 P9 | escala |

---

## 📌 O MÉTODO, para a próxima
**A auditoria faz-se contra a FONTE, nunca contra um resumo.**
E a fonte das regras do Vasco **são os prompts** — v1 → v9 — porque *"todas as regras que me fui
lembrando passaram por lá"*.

**Ainda faltam ~10 ficheiros.** Ler **sem pressa**, um a um, e trazer o delta para o
`REGRAS_DO_VASCO.md`.
