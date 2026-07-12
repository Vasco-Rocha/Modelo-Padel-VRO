# 📋 PROMPT 1 — AUDITORIA DOS PROMPTS
### *(cola tudo o que está abaixo numa conversa NOVA, dedicada só a isto)*

---

És o arqueólogo das regras do PadelPro Vision. **Esta conversa tem UMA tarefa e mais nenhuma.**

## 🛑 REGRA ZERO
**NÃO TOCAS EM CÓDIGO NENHUM.** O pipeline (`padelpro-vision/gerar_tempo_util.py`) está **TRAVADO**
em `RECALL 96,3% · PRECISÃO 95,9% · 13/13 serviços` e o Vasco proibiu alterações.
Nesta conversa **só se LÊ e só se ESCREVE em ficheiros `.md`**. Zero `.py`.

---

## O PROBLEMA

O Vasco (13 jul 2026):
> *"Está tudo guardado nos registos. Se fores a fundo, sem pressa, a todos os prompts — desde o
> prompt Gemini inicial ao v9 — **todas as regras que me fui lembrando passaram por lá**."*

**Os prompts são a FONTE das regras dele.** E as regras estão a perder-se entre a fonte e o código.
Já aconteceu, **medido**, várias vezes:

- a **S12** estava marcada ✅ no mapa e **fazia outra coisa** (custou um dia de caça a um bug morto)
- a **S8** estava marcada ✅ e **não corria**
- a regra da **cor da roupa** **não estava escrita em lado nenhum** — só apareceu porque o Vasco a
  mencionou de passagem
- a regra da **PAUSA entre pontos** estava nos prompts, **nunca foi implementada** — e quando
  finalmente foi (13 jul), deu **+1,8 de precisão** e resolveu um problema que nenhuma outra regra
  apanhava

> ## 🚨 E O ERRO QUE NÃO SE REPETE
> A 1.ª auditoria confrontou o **`REGRAS_CONSOLIDADAS_todos_prompts.md`** — que é um **RESUMO**,
> escrito por um Claude. **Um resumo também perde regras.** Um mapa feito a partir de um mapa.
> **A auditoria faz-se contra os ORIGINAIS. Sempre.**

---

## A TAREFA

**Ler, um a um, sem pressa, os prompts ORIGINAIS.** Para cada um, extrair **todas** as regras e
confrontá-las com o `REGRAS_DO_VASCO.md`. O que não estiver lá, **é uma regra perdida**.

### ✅ Já auditados (13 jul) — ver `REGRAS_PERDIDAS_v2_dos_originais.md`
- `prompt_gemini_analise_padel.md` **(v1)** — o mais antigo e o mais detalhado
- `prompt_gemini_analise_padel_v3.md` **(v3)**

**Deles saíram 4 regras que não estavam em lado nenhum** — incluindo a *"camisola muda uma de cada
vez"*, que é a **salvaguarda que faltava** à regra da cor.

### ⏳ POR AUDITAR — a tua tarefa
```
prompt_padel_v7.1.md
prompt_padel_v7.7.md
prompt_padel_v8.0.md
prompt_padel_v9_MASTER.md
prompt_analise_padel_v9.md
prompt_analise_padel_v9_GEMINI.md
prompt_modelo_hibrido_v9.md
REGRAS_BOLA_PARA_CODIGO.md
AFINAR_TEMPO_UTIL.md  ·  AFINAR_TEMPO_UTIL_v2.md
PLANO_TEMPO_UTIL_pos_BlurBall.md  ·  PLANO_DETETOR_TEMPORAL.md
padelpro-vision/docs/   (tudo)
```

---

## COMO FAZER

1. **`Read` o ficheiro INTEIRO.** Não `grep`. Não amostras. **Lê tudo.** Uma regra pode estar numa
   nota de rodapé, num exemplo negativo, ou dentro de um exemplo de JSON.
2. Para **cada afirmação normativa** (*"o rally acaba quando…"*, *"nunca faças…"*, *"em dúvida…"*),
   pergunta: **está no `REGRAS_DO_VASCO.md`?**
3. Se **não** estiver → escreve-a em `REGRAS_PERDIDAS_v2_dos_originais.md`, **com a citação exacta
   e a origem** (ficheiro + secção).
4. Depois **acrescenta-a ao `REGRAS_DO_VASCO.md`**, no bloco certo (BOLA / JOGADORES / SERVIÇO /
   CAMPO / LEIS DE DESENHO), com um **número** e o **estado** (implementada / por implementar /
   bloqueada — e **porquê**).
5. **Não avalies se a regra é boa.** Não é essa a tarefa. **Regista-a.** A avaliação faz-se depois,
   com medições e com o Vasco.

### 👀 O QUE PROCURAR — o que mais se perde
- **Exemplos NEGATIVOS** (*"❌ não faças X"*) — são regras disfarçadas, e escapam sempre
- **Notas de rodapé** e **parênteses**
- **Exceções** (*"…exceto quando…"*) — a exceção é tão regra como a regra
- **Definições do jogo** (o que é um ponto, um serviço, uma falta, um let)
- **Vocabulário perdido** (ex.: as zonas `VF1`–`VF5` do v1 desapareceram quando a v3 simplificou)
- **Pressupostos** (ex.: *"a câmara é fixa, lateral, a meia altura"*)
- **Leis de desenho** — as mais valiosas e as mais invisíveis. Ex., do v1:
  > *"Nunca inventas timestamps por estimativa — se não consegues ancorar, **omite o evento**."*
  Estava escrito **há um mês**. É a lei que rege o projeto todo. **Não estava no inventário.**

---

## NO FIM

- `REGRAS_DO_VASCO.md` **completo** — todas as regras, todas numeradas, todas com estado
- `REGRAS_PERDIDAS_v2_dos_originais.md` **fechado** — com a lista do que estava perdido e onde estava
- Um **resumo curto ao Vasco**: *"encontrei N regras perdidas; estas M parecem-me acionáveis já"*
- **`GUARDAR_TUDO.command`** (duplo-clique na raiz) para commit + push

## E SE ENCONTRARES UMA REGRA QUE CONTRADIZ O CÓDIGO
**NÃO alteres o código.** Escreve a contradição, mostra ao Vasco, e **deixa-o decidir.**
*(Foi assim que se descobriu que a S12 estava a fazer outra coisa com o nome certo.)*

---

**Começa pelo `REGRAS_DO_VASCO.md` e pelo `REGRAS_PERDIDAS_v2_dos_originais.md`, para saberes o que
já está registado. Depois abre o `prompt_padel_v7.1.md` e lê-o do princípio ao fim.**
