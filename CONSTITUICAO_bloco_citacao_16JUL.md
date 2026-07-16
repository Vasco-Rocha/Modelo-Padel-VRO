# ✍️ ENXERTOS PARA A CONSTITUIÇÃO — a citação literal *(16 jul 2026)*
*(Não recopiar a constituição à mão — isso É a erosão. Só se acrescentam estes dois blocos.)*

---

## ENXERTO 1 — no bloco `# 🧭 ANTES DE TUDO — os comandos`
**Acrescenta estas duas linhas ao bloco ```bash``` (a seguir à `ablacao.py`):**

```bash
python3 citar.py <ID>          # 📎 citar uma regra À LETRA (ex.: python3 citar.py S17)
python3 guarda_citacao.py      # 🐕 as citações batem com a fonte? DISPARA se não.
```

---

## ENXERTO 2 — secção nova, LOGO A SEGUIR a `# 🛑 COMO TRABALHAR — NÃO NEGOCIÁVEL`
*(antes de `# 🎯 A DIRETRIZ DE PRODUTO`. É a irmã operacional da D21.)*

```markdown
# ✍️ CITAÇÃO LITERAL — NÃO NEGOCIÁVEL   *(Vasco, 16 jul)*

> **Em qualquer conversa deste projeto — este bloco de regras é para ser citado letra a letra,
> sempre que for solicitado pelo Vasco. As regras só podem ser alteradas, atalhadas ou
> atualizadas só e apenas sob a instrução clara e concisa do próprio Vasco.**

**Como se cita uma regra — obrigatório:**
- **NUNCA de memória.** Corre `python3 citar.py <ID>` e **cola a saída tal e qual**. A explicação
  do Claude vem POR BAIXO, separada — nunca no lugar da regra. *(É a D21, agora com ferramenta.)*
- Antes de guardar/fechar: `python3 guarda_citacao.py` — **DISPARA** se uma citação num `.md` não
  bater, letra a letra, com a `REGRAS_DO_VASCO.md`. O `GUARDAR_TUDO.command` já o corre.
- **9 regras trancadas têm a LEI marcada na fonte** (S17, S18, S23, D19, D20, S42, S43, B18, B19)
  com delimitadores invisíveis — o guarda distingue a **LEI** (dele) da **PROSA** (do Claude).
  As restantes citam-se contra o bloco inteiro da regra.

> **A EROSÃO NÃO É UMA MENTIRA — é a mesma regra a cair em palavras, de conversa para conversa.**
> **O `auditar_mentiras.py` vê se a regra CORRE. O `guarda_citacao.py` vê se ela ainda DIZ o que dizia.**
```

---

## (opcional) ENXERTO 3 — o cabeçalho e o "o que mudou"
- No topo, muda `rev. 15 jul 2026` → **`rev. 16 jul 2026`**, e acrescenta a linha:
  `##### *(a rev. 15 jul fica em CONSTITUICAO_15JUL.md — datada, é história.)*`
- Na tabela `# 📝 O QUE MUDOU NESTA REVISÃO`, uma linha nova no topo:

| | |
|---|---|
| ✍️ ➕ **CITAÇÃO LITERAL** | `citar.py` extrai a regra da fonte (sem retipar); `guarda_citacao.py` **dispara** se uma citação não bater. 9 regras trancadas com a LEI marcada. **Ataca a erosão — a regra a cair em palavras — que não é mentira e o `auditar_mentiras` não vê.** |
