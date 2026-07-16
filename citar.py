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
