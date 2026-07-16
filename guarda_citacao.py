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
