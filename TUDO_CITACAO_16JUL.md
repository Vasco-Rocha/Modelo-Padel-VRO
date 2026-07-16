# 🗂️ TUDO — O SISTEMA DE CITAÇÃO LITERAL (16 jul 2026)
### *Tudo o que foi produzido nesta conversa, junto e por inteiro. Nada atalhado.*
### *Montado a partir dos ficheiros REAIS — não é uma recópia à mão (isso seria a própria erosão).*

---

## 0) O PROBLEMA E A CURA
- **O problema:** a mesma regra ia **caindo em palavras** de conversa para conversa. Não é mentira (a regra corre) — é **erosão na escrita**, e o `auditar_mentiras.py` não a vê.
- **A cura:** citar deixa de ser "de memória". `citar.py` **extrai** a regra da fonte; `guarda_citacao.py` **dispara** se uma citação não bater, letra a letra. 9 regras trancadas têm as **palavras do Vasco marcadas** na fonte, invisíveis.

## AS PEÇAS
| ficheiro | o que é |
|---|---|
| `REGRAS_DO_VASCO.md` | a FONTE ÚNICA. Levou a cláusula LEI DE ESCRITA, 9 blocos-lei, e as leis **D21** (citação) e **D22** (argumento não usado). |
| `fonte_regras.py` | o LEITOR da fonte. Base das outras. |
| `citar.py` | cita uma regra À LETRA (`python3 citar.py S17`). |
| `guarda_citacao.py` | o GUARDA: verifica citações contra a fonte. |
| `GUARDA_CITACAO.command` | duplo-clique do guarda. |
| `DEMO_citacao.md` | teste que prova o guarda (falha de propósito). |
| `AGENTS.md` | o que um agente lê a frio (Antigravity/Claude). |
| `CLAUSULA_CITACAO_para_instrucoes.md` | bloco para colar nas Instruções do Projeto. |
| `../CITACAO_CORRER_TUDO.command` | corre tudo (ponto de entrada). |
| `../GUARDAR_TUDO.command` | guarda no git + corre o guarda. |
| `../CONSTITUICAO_15JUL.md` | recebeu o bloco CITAÇÃO LITERAL. |

## O QUE FALTA — e só o Vasco o pode fazer
1. **Colar** a `CONSTITUICAO_15JUL.md` nas Instruções do Projeto (⚙️).
2. **Correr** `GUARDAR_TUDO.command` (guarda no git — o Claude não mexe no `.git`).

---

## 1) A CLÁUSULA — a LEI DE ESCRITA na fonte (topo da REGRAS_DO_VASCO.md)

> ## ✍️ LEI DE ESCRITA — **QUANDO O VASCO ATUALIZA UMA REGRA, ESCREVE-SE INTEIRA, COM AS PALAVRAS DELE. NUNCA SE ATALHA.**
> *(Vasco, 14 jul: "sempre que eu atualizo, tu tentas atalhar.")*
>
> **Atalhar tira a NUANCE. E a nuance É a regra.** Uma regra resumida está a meio caminho de mentir
> — porque a próxima pessoa a ler já não tem a parte que fazia a regra funcionar.
> - ✅ **Cita-o à letra.** A explicação do Claude vem POR BAIXO da regra dele, nunca por cima nem no lugar dela.
> - ✅ **Se ficar longa, fica longa.** É para isso que o ficheiro serve. O curto é o `CONSTITUICAO.md`; aqui é o INTEIRO.
> - ⛔ **Nunca substituir a frase do Vasco por um resumo do Claude.** O resumo é do Claude; a LEI é dele.
>
> **É a irmã da lei "a verdade que se escreve APODRECE": aqui a verdade apodrece na ESCRITA, ao ser cortada.**
>
> ### 🔒 CITAÇÃO LITERAL — *(Vasco, 16 jul 2026)*
> **Em qualquer conversa deste projeto — este bloco de regras é para ser citado letra a letra,
> sempre que for solicitado pelo Vasco. As regras só podem ser alteradas, atalhadas ou atualizadas
> só e apenas sob a instrução clara e concisa do próprio Vasco.**
>
> ⇒ Quando o Vasco pede uma regra, o Claude **LÊ o bloco na `REGRAS_DO_VASCO.md` e cola-o tal e qual** —
> nunca a reescreve de memória. A explicação do Claude vem **por baixo**, separada, nunca no lugar dela.


---

## 2) AS 9 REGRAS TRANCADAS — a LEI marcada na fonte (extraída, não recopiada)

- **B18** — O ponto decorre com a bola em movimento após o serviço. Tem de estar num **MOVIMENTO
> ### CONTÍNUO** que se ajuste ao **aproximar-se de pelo menos uma bounding box** — **até mudar
> ### de direção**.
- **B19** — Há 8 ténis num campo de padel.
- **D19** — vê os pés do jogador de vermelho. Está claramente à frente da linha de serviço. **Porque não é detetado como estando à frente?**
- **D20** — Quem tem o pé **NA** linha **ainda não a passou**.
- **S17** — se a bola **muda de direção** (ou **pára**) na rede, **longe de uma bounding box** → o ponto acabou.
- **S18** — bola PARADA dentro da bounding box, SEM MUDAR DE CAMPO → ponto terminado de certeza, sem raquetada.
- **S23** — NÃO HÁ PONTO SEM SERVIÇO. E NÃO HÁ SERVIÇO SEM A BOLA BATER NO CHÃO.
- **S42** — NÃO HÁ FIM DE PONTO SEM SERVIÇO A SEGUIR.
- **S43** — Dois pedaços só são pontos DIFERENTES se houver um SERVIÇO entre eles.

---

## 2b) AS DUAS LEIS NOVAS NA FONTE (extraídas)

**D21 — CITAÇÃO LITERAL:**

| **D21** | ✍️ **QUANDO O VASCO ATUALIZA UMA REGRA, ESCREVE-SE INTEIRA, COM AS PALAVRAS DELE. NUNCA SE ATALHA.** + 🔒 **CITAÇÃO LITERAL** *(Vasco, 16 jul)* — **o texto da lei, à letra, está no bloco LEI DE ESCRITA no topo deste ficheiro** (não se repete aqui, para não haver duas versões). ⇒ **cita-se** com `python3 citar.py <ID>` (extrai da fonte, sem retipar) e **confirma-se** com `python3 guarda_citacao.py` (dispara se não bater, letra a letra). **Atalhar tira a NUANCE — e a nuance É a regra.** | **14–16 jul · Vasco** |

**D22 — UM ARGUMENTO QUE NÃO SE USA É UMA MENTIRA À ESPERA:**

| **D22** | 🆕 🚪 **UM ARGUMENTO QUE NÃO SE USA É UMA MENTIRA À ESPERA.** *(Vasco, 15 jul)* **Se uma função pede um vídeo, TEM de usar esse vídeo — ou rebentar.** A configuração por-vídeo *(régua + polígono + boxes)* vive numa **PORTA ÚNICA** (`configurar(video)`); um vídeo desconhecido **FALHA**, não herda o anterior. *(O caso: a `cascata(video)` recebia o vídeo e ignorava-o — corria o Barbosa com os dados do Parada4, em silêncio: 23 serviços → 16. Apanhou-o um número que não fazia sentido, não um teste — "um detetor que acha 23 não colapsa para 16".)* | **15 jul · Vasco** |

---

## 3) FICHEIRO: AGENTS.md

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

---

## 4) FICHEIRO: CLAUSULA_CITACAO_para_instrucoes.md

# 🔒 CITAÇÃO LITERAL DAS REGRAS — NÃO NEGOCIÁVEL
### *(Vasco, 16 jul 2026 — colar nas INSTRUÇÕES DO PROJETO)*

> **Em qualquer conversa deste projeto — este bloco de regras é para ser citado letra a letra, sempre que for solicitado pelo Vasco. As regras só podem ser alteradas, atalhadas ou atualizadas só e apenas sob a instrução clara e concisa do próprio Vasco.**

## COMO CITAR UMA REGRA (obrigatório)

O Claude **NÃO cita de memória** — é assim que a regra "cai em palavras" de conversa para conversa.

1. Corre **`python3 citar.py <ID>`** (ex.: `python3 citar.py S17`). Ele imprime o bloco da regra, e — se estiver marcada — **a LEI (as palavras do Vasco)**, extraída da `REGRAS_DO_VASCO.md`.
2. **Cola essa saída, tal e qual.** A explicação do Claude vem **POR BAIXO**, separada — nunca no lugar da regra.
3. Antes de fechar a conversa (ou de guardar), corre **`python3 guarda_citacao.py`**. Ele falha em barulho se alguma citação num `.md` não bater, letra a letra, com a fonte.

## AS OUTRAS REGRAS

- O Claude **NÃO altera, resume, atalha nem "melhora"** uma regra por iniciativa própria. Só o Vasco o autoriza, com instrução clara e concisa.
- **Atalhar tira a nuance — e a nuance É a regra.** *(É a D21.)*

**A fonte única das regras:** `padelpro-vision/REGRAS_DO_VASCO.md`. Qualquer outro `REGRAS_DO_VASCO.md` (na raiz, em `docs/`) é um **ponteiro morto** — não se lê nem se escreve nele.

---

## 5) FICHEIRO: DEMO_citacao.md (o teste — falha de propósito)

# DEMO — o guarda de citação a funcionar
*(ficheiro de teste. Corre: `python3 guarda_citacao.py --demo`)*

## 1) A LEI do Vasco, à letra (deve dar ✅ LEI)
<<CITA D20>>
Quem tem o pé **NA** linha **ainda não a passou**.
<<FIM>>

## 2) As MESMAS palavras da lei, sem formatação (deve dar ✅ LEI)
<<CITA D20>>
Quem tem o pé NA linha ainda não a passou.
<<FIM>>

## 3) Citação ERODIDA — falta uma palavra, muda a caixa (deve dar 🟥 EROSÃO)
<<CITA D20>>
Quem tem o pé na linha ainda não passou.
<<FIM>>

## 4) Texto certo, atribuído à REGRA ERRADA (deve dar 🟥 REGRA ERRADA)
<<CITA S17>>
Quem tem o pé **NA** linha **ainda não a passou**.
<<FIM>>

## 5) Texto REAL da fonte, mas é a MINHA prosa, não a lei marcada (deve dar ⚠️ PROSA)
<<CITA D19>>
A LINHA É A LINHA. NÃO SE PÕE UM LIMIAR EM CIMA DELA.
<<FIM>>

---

## 6) CÓDIGO: fonte_regras.py

```python
#!/usr/bin/env python3
"""
📖 fonte_regras.py  —  o LEITOR da fonte única (16 jul 2026)

Uma pergunta só:  "onde, na REGRAS_DO_VASCO.md, vive o texto da regra X?"

NÃO decide nada. NÃO cita. Só localiza e devolve o TEXTO EXATO da fonte.
É a base partilhada do `citar.py` e do `guarda_citacao.py` — para os dois
verem a MESMA verdade, extraída do MESMO sítio.

⛔ A FONTE É `REGRAS_DO_VASCO.md`. Este módulo NUNCA a escreve. Só lê.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).parent
FONTE = RAIZ / "REGRAS_DO_VASCO.md"

ID_RE = r"(?:B|J|S|C|D|F|P)\d+b?"


def linhas_fonte():
    return FONTE.read_text(encoding="utf-8").splitlines()


def _id_da_celula(linha):
    """Uma linha de tabela | **S17** | ... |  →  'S17'  (ou None)."""
    if not linha.startswith("|"):
        return None
    cel = [c.strip() for c in linha.strip("|").split("|")]
    if len(cel) < 3:
        return None
    m = re.fullmatch(rf"\**~*({ID_RE})~*\**", cel[0])
    return m.group(1) if m else None


def _id_do_cabecalho(linha):
    """Um cabeçalho '## 🔴 B19 — OS 9 CANDIDATOS'  →  'B19'  (ou None).

    Só conta como DEFINIÇÃO se o ID aparecer logo no início do título
    (a seguir a emojis/símbolos), não no meio de uma frase.
    """
    m = re.match(r"^#{1,4}\s+(.*)$", linha)
    if not m:
        return None
    titulo = m.group(1)
    # tira emojis/símbolos/espaços da frente
    inicio = re.sub(r"^[^A-Za-z0-9]*", "", titulo)
    m2 = re.match(rf"({ID_RE})\b", inicio)
    return m2.group(1) if m2 else None


def blocos_por_id():
    """
    Devolve {id: [(l_ini, l_fim, texto), ...]}  — TODAS as regiões da fonte
    onde a regra está definida (linha de tabela + secção com cabeçalho).
    l_ini/l_fim são índices 0-based inclusive; texto é o RAW da fonte.
    """
    linhas = linhas_fonte()
    out = {}

    # 1) linhas de tabela  → cada uma é o seu próprio bloco (1 linha)
    for i, ln in enumerate(linhas):
        rid = _id_da_celula(ln)
        if rid:
            out.setdefault(rid, []).append((i, i, ln))

    # 2) secções com cabeçalho  → do cabeçalho até ao próximo cabeçalho '## '
    #    (ou '# ') ou até uma linha '---' isolada.
    for i, ln in enumerate(linhas):
        rid = _id_do_cabecalho(ln)
        if not rid:
            continue
        j = i + 1
        while j < len(linhas):
            nxt = linhas[j]
            if re.match(r"^#{1,2}\s", nxt) or nxt.strip() == "---":
                break
            j += 1
        texto = "\n".join(linhas[i:j])
        out.setdefault(rid, []).append((i, j - 1, texto))

    return out


def bloco(rid):
    """O texto RAW de todas as regiões da regra `rid`, concatenado (ou '')."""
    regioes = blocos_por_id().get(rid, [])
    return "\n\n".join(t for _, _, t in regioes)


# ---------------------------------------------------------------- os blocos-lei
# As PALAVRAS do Vasco marcadas na fonte com delimitadores INVISÍVEIS:
#     <!--LEI:S17-->…só as palavras dele…<!--/LEI:S17-->
# São comentários HTML: não aparecem quando se LÊ o markdown, mas o código vê-os.
# Servem para o guarda distinguir a LEI (dele) da PROSA (explicação do Claude).
LEI_RE = re.compile(r"<!--LEI:(" + ID_RE + r")-->(.*?)<!--/LEI:\1-->", re.S)


def lei_spans():
    """{id: [texto-lei RAW, …]} — só as palavras do Vasco marcadas na fonte."""
    txt = FONTE.read_text(encoding="utf-8")
    out = {}
    for m in LEI_RE.finditer(txt):
        out.setdefault(m.group(1), []).append(m.group(2).strip())
    return out


def bloco_lei(rid):
    """O texto RAW da(s) lei(s) marcada(s) da regra `rid` (ou '' se não houver)."""
    return "\n".join(lei_spans().get(rid, []))


def todos_os_ids():
    return sorted(blocos_por_id().keys(), key=lambda s: (s[0], int(re.search(r"\d+", s).group())))


# ---------------------------------------------------------------- normalização
def normalizar(t):
    """
    'As PALAVRAS', sem o ruído da formatação markdown.
    Tira: **negrito**, *itálico*, `código`, <br>, &nbsp;, aspas curvas,
    e colapsa espaços. NÃO mexe em maiúsculas — o "PARADA" dele é a regra.
    """
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)          # delimitadores LEI / comentários
    t = t.replace("<br>", " ").replace("&nbsp;", " ")
    linhas = [re.sub(r"^[\s>#]+", "", l) for l in t.splitlines()]  # tira prefixos > e #
    t = " ".join(linhas)
    t = re.sub(r"[*_`]", "", t)
    t = (t.replace("“", '"').replace("”", '"')
           .replace("’", "'").replace("‘", "'"))
    t = re.sub(r"\s+", " ", t).strip()
    return t


if __name__ == "__main__":
    idx = blocos_por_id()
    print(f"fonte: {FONTE.name} · {len(idx)} regras com bloco localizável")
    print(", ".join(todos_os_ids()))
```

---

## 7) CÓDIGO: citar.py

```python
#!/usr/bin/env python3
"""
📎 citar.py  —  CITAR À LETRA, SEM RETIPAR (16 jul 2026)

    python3 citar.py S17      → imprime o bloco da regra S17, TAL E QUAL está na fonte
    python3 citar.py          → lista as regras e diz quais têm bloco localizável

PORQUÊ ISTO EXISTE:
    A erosão ("a mesma regra a cair em palavras" — Vasco) acontece quando a regra
    é reescrita DE MEMÓRIA. Este script tira a memória do caminho: a citação é
    EXTRAÍDA da fonte, nunca digitada. Sem retipar, não há como raspar a nuance.

    Cita-se assim: corre `citar.py <ID>`, cola a saída marcada entre <<CITA>>…<<FIM>>,
    e a explicação do Claude vem POR BAIXO (a LEI DE ESCRITA / D21).

⛔ Só lê a `REGRAS_DO_VASCO.md`. Nunca a escreve.
"""
import sys
import fonte_regras as fr


def citar(rid):
    regioes = fr.blocos_por_id().get(rid)
    if not regioes:
        print(f"❌ '{rid}' não tem bloco localizável na fonte.")
        print("   (ou o ID está errado, ou a regra não está numa linha de tabela "
              "nem numa secção com cabeçalho — nesse caso precisa do Vasco a ditá-la.)")
        return 1
    print("=" * 92)
    print(f"📎 {rid} — CITAÇÃO LITERAL (extraída de {fr.FONTE.name}, sem retipar)")
    print("=" * 92)
    lei = fr.bloco_lei(rid)
    if lei:
        print("\n⚖️  A LEI (as palavras do Vasco, marcadas na fonte) — é ISTO que se cita:")
        for span in fr.lei_spans().get(rid, []):
            print(f'    "{span}"')
    for (a, b, texto) in regioes:
        onde = f"linha {a + 1}" if a == b else f"linhas {a + 1}–{b + 1}"
        print(f"\n── {onde} " + "─" * (78 - len(onde)))
        print(texto)
    print("\n" + "=" * 92)
    print("⇒ Cola isto entre  <<CITA " + rid + ">>  e  <<FIM>>.  A tua explicação vem POR BAIXO.")
    return 0


def listar():
    idx = fr.blocos_por_id()
    print(f"fonte: {fr.FONTE.name} · {len(idx)} regras com bloco localizável\n")
    linha = []
    for rid in fr.todos_os_ids():
        linha.append(rid)
        if len(linha) == 12:
            print("   " + "  ".join(f"{x:5}" for x in linha))
            linha = []
    if linha:
        print("   " + "  ".join(f"{x:5}" for x in linha))
    print("\nUsa:  python3 citar.py <ID>   (ex.: python3 citar.py S17)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        listar()
        sys.exit(0)
    sys.exit(citar(sys.argv[1].strip().upper()))
```

---

## 8) CÓDIGO: guarda_citacao.py

```python
#!/usr/bin/env python3
"""
🐕 guarda_citacao.py  —  O GUARDA DE CITAÇÃO (16 jul 2026)

    "Uma regra citada neste projeto é MESMO o que o Vasco escreveu — letra a letra?"

Procura, nos ficheiros, citações marcadas assim:

        <<CITA S17>>
        …o texto da regra…
        <<FIM>>

e verifica cada uma contra a `REGRAS_DO_VASCO.md`:

    ✅ VERBATIM     — o texto está, tal e qual, DENTRO do bloco da regra citada
    🟡 PALAVRAS     — as palavras batem (só muda a formatação markdown)
    🟥 REGRA ERRADA — o texto existe na fonte… mas NOUTRA regra
    🟥 EROSÃO       — o texto NÃO está na fonte: alguém o reescreveu de memória

Se houver UM 🟥, o guarda FALHA (exit≠0). Como os outros guardas do projeto:
NÃO relaxes o guarda — corrige a citação.

USO:
    python3 guarda_citacao.py <ficheiro.md> [outro.md …]
    python3 guarda_citacao.py            → varre todos os .md desta pasta
    python3 guarda_citacao.py --demo     → corre o exemplo (DEMO_citacao.md)

⛔ Só lê. Não escreve nada. Não corre o modelo. Segundos, zero RAM.
"""
import re
import sys
import difflib
from pathlib import Path
import fonte_regras as fr

RAIZ = Path(__file__).parent
CITA_RE = re.compile(r"<<CITA\s+(" + fr.ID_RE + r")>>\s*(.*?)\s*<<FIM>>", re.S)


def verificar_ficheiro(path, fonte_norm, blocos_norm, lei_norm):
    txt = path.read_text(encoding="utf-8")
    resultados = []
    for m in CITA_RE.finditer(txt):
        rid, corpo = m.group(1), m.group(2)
        corpo_norm = fr.normalizar(corpo)
        bloco_raw = fr.bloco(rid)
        bloco_n = blocos_norm.get(rid, "")
        lei_raw = fr.bloco_lei(rid)
        lei_n = lei_norm.get(rid, "")

        if not corpo_norm:
            estado = "VAZIA"
        elif not bloco_raw and not lei_raw:
            estado = "SEM_BLOCO"
        elif lei_raw and corpo.strip() in lei_raw:
            estado = "LEI"                       # à letra, dentro das palavras do Vasco
        elif lei_n and corpo_norm in lei_n:
            estado = "LEI_PALAVRAS"              # as palavras dele batem (só muda formatação)
        elif corpo_norm in bloco_n:
            # está na fonte, dentro da regra certa…
            if lei_raw:
                estado = "PROSA"                 # …mas é prosa/explicação, não a LEI marcada
            elif corpo.strip() in bloco_raw:
                estado = "VERBATIM"
            else:
                estado = "PALAVRAS"
        elif corpo_norm in fonte_norm:
            estado = "REGRA_ERRADA"
        else:
            estado = "EROSAO"
        resultados.append((rid, corpo, corpo_norm, estado))
    return resultados


def id_onde_esta(corpo_norm, blocos_norm):
    for rid, bn in blocos_norm.items():
        if corpo_norm and corpo_norm in bn:
            return rid
    return "?"


def diff_mais_proximo(corpo_norm, bloco_norm):
    """Mostra, palavra a palavra, o que difere face ao trecho mais parecido da regra."""
    if not bloco_norm:
        return "   (a regra não tem bloco na fonte para comparar)"
    # janela do bloco com o tamanho da citação, mais parecida
    palavras_b = bloco_norm.split()
    palavras_c = corpo_norm.split()
    n = len(palavras_c)
    melhor, melhor_r = None, -1.0
    for k in range(max(1, len(palavras_b) - n + 1)):
        janela = " ".join(palavras_b[k:k + n])
        r = difflib.SequenceMatcher(None, corpo_norm, janela).ratio()
        if r > melhor_r:
            melhor_r, melhor = r, janela
    if melhor is None:
        return "   (sem trecho comparável)"
    out = ["   trecho mais próximo na fonte:", f"     «{melhor}»",
           "   a tua citação:", f"     «{corpo_norm}»", "   diferença:"]
    d = difflib.ndiff(melhor.split(), corpo_norm.split())
    muda = [x for x in d if x[0] in "+-"]
    out.append("     " + "  ".join(muda[:20]) if muda else "     (só formatação)")
    return "\n".join(out)


def main(args):
    demo = "--demo" in args
    args = [a for a in args if not a.startswith("--")]
    if demo:
        alvos = [RAIZ / "DEMO_citacao.md"]
    elif args:
        alvos = [Path(a) for a in args]
    else:
        # varre os .md da pasta, MENOS os de teste/relatório (que embebem exemplos
        # que falham DE PROPÓSITO: o DEMO_ e o TUDO_ que mostra o DEMO lá dentro).
        alvos = [p for p in sorted(RAIZ.glob("*.md"))
                 if not p.name.startswith(("DEMO_", "TUDO_"))]

    fonte_norm = fr.normalizar(fr.FONTE.read_text(encoding="utf-8"))
    blocos_norm = {rid: fr.normalizar(fr.bloco(rid)) for rid in fr.todos_os_ids()}
    lei_norm = {rid: fr.normalizar(fr.bloco_lei(rid)) for rid in fr.lei_spans()}

    print("=" * 92)
    print("🐕 GUARDA DE CITAÇÃO — as regras citadas batem, letra a letra, com a fonte?")
    print("=" * 92)
    print(f"fonte: {fr.FONTE.name}\n")

    total = 0
    falhas = 0
    for path in alvos:
        if not path.exists():
            print(f"⚠️  {path.name}: não existe")
            continue
        res = verificar_ficheiro(path, fonte_norm, blocos_norm, lei_norm)
        if not res:
            continue
        print(f"── {path.name} " + "─" * (86 - len(path.name)))
        for rid, corpo, corpo_norm, estado in res:
            total += 1
            trecho = (corpo_norm[:70] + "…") if len(corpo_norm) > 70 else corpo_norm
            if estado == "LEI":
                print(f"   ✅ {rid:5} LEI        «{trecho}»  (palavras do Vasco, à letra)")
            elif estado == "LEI_PALAVRAS":
                print(f"   ✅ {rid:5} LEI        «{trecho}»  (palavras do Vasco; só muda a formatação)")
            elif estado == "PROSA":
                print(f"   ⚠️  {rid:5} PROSA      «{trecho}»  (está na fonte, mas é explicação — NÃO é a LEI marcada)")
            elif estado == "VERBATIM":
                print(f"   ✅ {rid:5} VERBATIM   «{trecho}»")
            elif estado == "PALAVRAS":
                print(f"   🟡 {rid:5} PALAVRAS   «{trecho}»  (bate; só muda a formatação)")
            elif estado == "VAZIA":
                print(f"   ⚪ {rid:5} VAZIA      (citação sem texto)")
            elif estado == "SEM_BLOCO":
                print(f"   ⚪ {rid:5} SEM BLOCO  a regra {rid} não tem bloco localizável na fonte")
            elif estado == "REGRA_ERRADA":
                falhas += 1
                real = id_onde_esta(corpo_norm, blocos_norm)
                print(f"   🟥 {rid:5} REGRA ERRADA  este texto é da regra {real}, não da {rid}")
                print(f"          «{trecho}»")
            else:  # EROSAO
                falhas += 1
                print(f"   🟥 {rid:5} EROSÃO  este texto NÃO está na fonte (reescrito de memória)")
                print(diff_mais_proximo(corpo_norm, blocos_norm.get(rid, "")))
        print()

    print("-" * 92)
    if total == 0:
        print("ℹ️  Nenhuma citação marcada <<CITA …>> encontrada.")
        print("   (Marca as citações com <<CITA S17>> … <<FIM>> para o guarda as poder verificar.)")
        return 0
    print(f"citações verificadas: {total} · 🟥 falhas: {falhas}")
    if falhas:
        print("\n🚨 O GUARDA DISPAROU. Há citações que NÃO são as palavras do Vasco.")
        print("   ⛔ Não relaxes o guarda — corrige a citação (usa: python3 citar.py <ID>).")
        return 1
    print("\n✅ Todas as citações batem com a fonte.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

---

## 9) COMANDO: GUARDA_CITACAO.command

```bash
#!/bin/bash
# 🐕 GUARDA DE CITAÇÃO — duplo-clique
# Verifica que as regras citadas (<<CITA ID>> … <<FIM>>) nos .md desta pasta
# são, letra a letra, as palavras do Vasco na REGRAS_DO_VASCO.md.
cd "$(dirname "$0")"
echo
python3 guarda_citacao.py "$@"
codigo=$?
echo
if [ $codigo -ne 0 ]; then
  echo "🚨 O GUARDA DISPAROU (código $codigo). Há citações fora da fonte — corrige antes de seguir."
else
  echo "✅ Guarda passou."
fi
echo
echo "Podes fechar esta janela."
```

---

## 10) COMANDO: CITACAO_CORRER_TUDO.command (na raiz)

```bash
#!/bin/bash
# ============================================================================
#  SISTEMA DE CITAÇÃO — CORRER TUDO   (16 jul 2026)
#  Duplo-clique. Mostra, de uma só vez, tudo o que foi montado:
#    1) o guarda de citação a DISPARAR (demo)
#    2) o citar.py a extrair uma regra À LETRA
#    3) a cobertura (que regras têm bloco / quais têm LEI marcada)
#    4) o guarda nos ficheiros a sério (limpo)
#    5) a CLÁUSULA de citação
#    6) o AGENTS.md (o que cada conversa lê a frio)
#    7) o passo que FALTA — e só tu o podes fazer
# ============================================================================
cd "$(dirname "$0")/padelpro-vision" || { echo "não encontrei padelpro-vision"; exit 1; }

barra() { printf '%.0s─' {1..76}; echo; }

echo
echo "############################################################################"
echo "#  SISTEMA DE CITAÇÃO DAS REGRAS DO VASCO — a correr tudo                   #"
echo "############################################################################"
echo
echo "As peças, e onde vivem (tudo em padelpro-vision/):"
echo "   REGRAS_DO_VASCO.md ....... a FONTE ÚNICA (as regras + as LEIs marcadas)"
echo "   citar.py ................. extrai uma regra à letra  (python3 citar.py S17)"
echo "   guarda_citacao.py ........ verifica que as citações batem com a fonte"
echo "   AGENTS.md ................ o que um agente lê antes de tocar em nada"
echo "   CLAUSULA_CITACAO_para_instrucoes.md . o bloco para colar nas INSTRUÇÕES"
echo "   DEMO_citacao.md .......... o teste (falha de propósito, para provar o guarda)"
echo

echo; barra; echo "1) O GUARDA A DISPARAR  —  python3 guarda_citacao.py --demo"; barra
python3 guarda_citacao.py --demo

echo; barra; echo "2) CITAR À LETRA  —  python3 citar.py D20"; barra
python3 citar.py D20

echo; barra; echo "3) COBERTURA — as 9 LEIS já marcadas"; barra
python3 -c "import fonte_regras as fr; s=fr.lei_spans(); print('regras com LEI marcada (', len(s), '):', ', '.join(sorted(s)))"
echo "   (lista completa das regras localizáveis:  python3 citar.py )"

echo; barra; echo "4) O GUARDA NOS FICHEIROS A SÉRIO (deve estar limpo)"; barra
python3 guarda_citacao.py

echo; barra; echo "5) A CLÁUSULA DE CITAÇÃO"; barra
cat CLAUSULA_CITACAO_para_instrucoes.md

echo; barra; echo "6) O AGENTS.md"; barra
cat AGENTS.md

echo; barra; echo "7) ⚠️  O QUE FALTA — E SÓ TU O PODES FAZER"; barra
cat <<'FIM'
Esta app-Claude NÃO lê o AGENTS.md automaticamente — lê as INSTRUÇÕES DO PROJETO.
Para a regra de citação carregar em TODAS as conversas novas:

   1. Abre as definições deste projeto (⚙️) → INSTRUÇÕES DO PROJETO
   2. Cola lá o conteúdo de:  padelpro-vision/CLAUSULA_CITACAO_para_instrucoes.md
      (aparece impresso na secção 5, aqui em cima)

No Antigravity isto não é preciso — lá o AGENTS.md carrega sozinho.

A partir daí, em qualquer conversa:
   • para citar uma regra:      python3 citar.py <ID>      (e colas a saída)
   • antes de guardar/fechar:    python3 guarda_citacao.py   (dispara se algo não bater)
   • o GUARDAR_TUDO.command já corre o guarda sozinho.
FIM

echo
echo "############################################################################"
echo "#  FEITO. Falta só o passo 7 (colar a cláusula nas instruções).            #"
echo "############################################################################"
echo
read -p "Enter para fechar..."
```
