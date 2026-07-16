#!/usr/bin/env python3
"""
🔎 AUDITAR AS MENTIRAS  —  14 jul 2026

A pergunta, uma só:

    "Uma regra marcada ✅ no REGRAS_DO_VASCO.md — corre MESMO no pipeline?"

⚠️ E a pergunta é PRECISA. O verificar_fonte.py pergunta "alguém chama esta função?".
   A B1 (objetos imóveis) passa nesse teste — porque é chamada na linha 73 do
   padelpro/modules/servico.py, POR CÓDIGO QUE NINGUÉM IMPORTA.

       O guarda pergunta:   "alguém a chama?"
       A pergunta certa é:  "o PIPELINE a chama?"

   Um guarda com um ponto cego ensina a confiar no ponto cego. — Vasco, 13 jul

Este script NÃO corre o modelo, NÃO lê vídeo, NÃO toca em ficheiro nenhum.
Lê o código como TEXTO (AST) e responde. Segundos, zero RAM.
"""
import ast, re, sys
from pathlib import Path

RAIZ = Path(__file__).parent
PIPELINE = RAIZ / "gerar_tempo_util.py"
FONTE = RAIZ / "REGRAS_DO_VASCO.md"


# ---------------------------------------------------------------- o pipeline
def alcancavel_do_main(path):
    """Que funções é que o main() consegue mesmo alcançar? (grafo de chamadas)"""
    arv = ast.parse(path.read_text())
    defs = {n.name: n for n in ast.walk(arv) if isinstance(n, ast.FunctionDef)}

    def chamadas(no):
        out = set()
        for n in ast.walk(no):
            if isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    out.add(f.id)
                elif isinstance(f, ast.Attribute):
                    out.add(f.attr)
        return out

    vivas, fila = set(), ["main"]
    while fila:
        nome = fila.pop()
        if nome in vivas or nome not in defs:
            continue
        vivas.add(nome)
        fila += [c for c in chamadas(defs[nome]) if c in defs]
    return defs, vivas, arv


def interruptores_lidos(arv):
    """REGRAS["X"] — quais é que o código LÊ mesmo? (um interruptor que ninguém lê é decoração)"""
    lidos = set()
    for n in ast.walk(arv):
        if (isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
                and n.value.id == "REGRAS"):
            k = n.slice
            if isinstance(k, ast.Constant):
                lidos.add(k.value)
    return lidos


def interruptores_declarados(path):
    txt = path.read_text()
    m = re.search(r"REGRAS\s*=\s*\{(.*?)\n\}", txt, re.S)
    if not m:
        return {}
    return {k: v == "True" for k, v in re.findall(r'"([A-Z0-9_]+)"\s*:\s*(True|False)', m.group(1))}


# ---------------------------------------------------------------- a fonte
def regras_da_fonte(path):
    """Cada linha de tabela | ID | regra | estado | onde |  →  (id, estado, funções citadas)"""
    out = {}
    for linha in path.read_text().splitlines():
        if not linha.startswith("|"):
            continue
        cel = [c.strip() for c in linha.strip("|").split("|")]
        if len(cel) < 3:
            continue
        rid = re.fullmatch(r"\**((?:B|J|S|C|D|F|P)\d+b?)\**", cel[0])
        if not rid:
            continue
        rid = rid.group(1)
        # 🩸 14 jul — o ESTADO lê-se da CÉLULA DO ESTADO, nunca da prosa.
        #    Um "✅" DENTRO de uma frase ("um ✅ aqui seria uma mentira") era lido como estado.
        #    O guarda leu o AVISO e tomou-o por um FACTO. A doença, em ponto pequeno.
        estado_cel = cel[2] if len(cel) >= 4 else " ".join(cel[1:])
        resto = " ".join(cel[1:])
        if "✅" in estado_cel:
            estado = "✅"
        elif "⛔" in estado_cel:
            estado = "⛔"
        elif "🔴" in estado_cel or "📋" in estado_cel:
            estado = "🔴"
        elif "⚠️" in estado_cel or "🧪" in estado_cel or "🟢" in estado_cel or "🟡" in estado_cel:
            estado = "⚠️"
        else:
            estado = "?"
        funcs = set(re.findall(r"`([a-z_0-9]+)\(\)`", resto)) | \
                set(re.findall(r"\.([a-z_0-9]+)\(\)", resto))
        chaves = set(re.findall(r'REGRAS\[["\']([A-Z0-9_]+)["\']\]', resto))
        out[rid] = dict(estado=estado, funcs=funcs, chaves=chaves, txt=resto[:90])
    return out


# ---------------------------------------------------------------- o veredito
def main():
    defs, vivas, arv = alcancavel_do_main(PIPELINE)
    lidos = interruptores_lidos(arv)
    declarados = interruptores_declarados(PIPELINE)
    regras = regras_da_fonte(FONTE)

    print("=" * 92)
    print("🔎 AS MENTIRAS — regras marcadas ✅ que o PIPELINE não corre")
    print("=" * 92)
    print(f"pipeline: {PIPELINE.name} · {len(defs)} funções · "
          f"{len(vivas)} alcançáveis a partir do main()")
    print(f"fonte:    {FONTE.name} · {len(regras)} regras em tabela\n")

    mentiras, orfas, ok = [], [], []
    for rid, r in sorted(regras.items()):
        if r["estado"] != "✅":
            continue
        if not r["funcs"] and not r["chaves"]:
            orfas.append(rid)          # ✅ sem prova nenhuma: nem função, nem interruptor
            continue
        corre = any(f in vivas for f in r["funcs"]) or any(c in lidos for c in r["chaves"])
        (ok if corre else mentiras).append(rid)

    print("🔴 MENTIRAS  (✅ na fonte · a função NÃO é alcançável a partir do main())")
    for rid in mentiras:
        r = regras[rid]
        onde = ", ".join(sorted(r["funcs"] | r["chaves"])) or "—"
        print(f"   {rid:5} {onde:38} {r['txt']}")
    if not mentiras:
        print("   (nenhuma)")

    print("\n⚪ ✅ SEM PROVA  (marcadas ✅ mas a fonte não diz QUE função nem QUE interruptor)")
    print(f"   {', '.join(orfas) if orfas else '(nenhuma)'}")

    print("\n✅ CONFIRMADAS  (a função corre mesmo, a partir do main())")
    print(f"   {', '.join(ok)}")

    print("\n" + "-" * 92)
    print("🔌 OS INTERRUPTORES")
    vazios = [k for k in declarados if k not in lidos]
    print(f"   declarados: {len(declarados)} · lidos pelo código: {len(lidos)}")
    print(f"   ⚠️ VAZIOS (declarados e NUNCA lidos — armadilhas): "
          f"{', '.join(vazios) if vazios else 'nenhum ✅'}")
    print(f"   🟢 ligados:  {', '.join(k for k, v in declarados.items() if v)}")
    print(f"   ⛔ desligados: {', '.join(k for k, v in declarados.items() if not v)}")

    print("\n" + "-" * 92)
    print("🕳️ FUNÇÕES ÓRFÃS do pipeline (definidas no gerar_tempo_util.py e NUNCA chamadas)")
    print(f"   {', '.join(sorted(set(defs) - vivas)) or 'nenhuma ✅'}")


if __name__ == "__main__":
    main()
