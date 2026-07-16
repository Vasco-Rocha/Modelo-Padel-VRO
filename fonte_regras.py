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
