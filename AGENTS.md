# AGENTS.md — PadelPro Vision
### O que um agente (Antigravity, Claude, qualquer um) lê ANTES de tocar em nada.
*(curto de propósito. O que muda vive em ficheiros — e diz-se ONDE. rev. 16 jul 2026)*

## COMO TRABALHAR — não negociável
- **Propõe → espera → só depois faz. Uma coisa de cada vez. O Vasco decide o passo seguinte.**
- **O Vasco NÃO é developer.** Passo a passo, sem atalhos de linguagem.
- **Uma caneta de cada vez no `gerar_tempo_util.py`.** As outras conversas leem, medem, criam ficheiros novos — **nunca editam o pipeline**.
- **Testar, não raciocinar.** Nunca descartar (nem dar por viva) uma regra com um raciocínio bonito — **MEDE**.
- **Vídeo antes de métricas.** Os piores bugs não partem nada e não aparecem nos números — só se veem a olhar. Dá exemplos visuais.
- **Sem atalhos na geometria.** Nada de números mágicos: só do `calibracao_<video>.json` ou frações do meio-campo local. Declara o atalho na mesma mensagem em que dás o número.
- **As definições do jogo (ponto, serviço, tempo útil) são do Vasco.** Param e perguntam.

## ONDE VIVE A VERDADE
- **as REGRAS:** `REGRAS_DO_VASCO.md` — a **FONTE ÚNICA**. Qualquer cópia na raiz ou em `docs/` é ponteiro morto.
- **o PIPELINE:** `gerar_tempo_util.py`
- **o ESTADO TRAVADO:** `teste_regressao.py`
- **os GUARDAS:** `verificar_fonte.py` + `auditar_mentiras.py` (corre SEMPRE os dois)

## O ESTADO CORRE-SE, NÃO SE DECORA
Não decores números deste ou de qualquer ficheiro. **O estado sai de `python3 teste_regressao.py` + `python3 auditar_mentiras.py`.** Um `.md` sem data apodrece; só o que se corre conta.

## CITAR UMA REGRA — obrigatório
- Para citar uma regra, corre **`python3 citar.py <ID>`** e **cola a saída tal e qual**. **Nunca de memória.** A explicação vem por baixo, separada.
- Antes de fechar/guardar, corre **`python3 guarda_citacao.py`** — dispara se uma citação não bater com a fonte.
- **As regras só mudam sob instrução clara do Vasco.** Não as resumas nem "melhores" por iniciativa própria (D21).

## O PRÓXIMO PASSO, ÚNICO
**B19 — os 9 candidatos da bola.** Correr `OS_9_CANDIDATOS.command`. Tudo o resto bate nesta porta.
