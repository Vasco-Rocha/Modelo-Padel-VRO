#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️  verificar_fonte.py — O GUARDA.

    python3 verificar_fonte.py              # tudo (corre a ablacao — ~1 min)
    python3 verificar_fonte.py --so-estrutura   # salta a ablacao (instantaneo)

========================================================================================
A DOENCA QUE ISTO CURA
========================================================================================
    Uma regra pode estar no mapa, com o NOME CERTO, e FAZER OUTRA COISA.
    Um ficheiro pode chamar-se "a fonte", e ser uma COPIA MORTA.

Ela NAO PARTE NADA. O pipeline corre, os numeros saem, ninguem da por nada.
So aparece quando alguem tropeca nela. A 13 jul 2026 mordeu TRES VEZES:

  1) a S12 estava ✅, com o nome certo, e agarrava-se ao ultimo CRUZAMENTO em vez da
     ultima PANCADA. A S8 estava ✅ e NEM SEQUER CORRIA.   (recall 93,2 -> 97,0)
  2) DUAS regras com o nome S23 (uma a correr, outra nunca). Idem B11, idem B8.
  3) DEZ documentos duplicados entre a raiz e o repo. QUATRO tinham divergido.

    🏃 A LEI DO VASCO: SO O QUE SE CORRE E' QUE CONTA.
       Uma cura feita a' mao nao se corre. Logo, nao conta.   >>> Por isso este ficheiro.

========================================================================================
A LEI DOS DUPLICADOS  (decidida pelo Vasco, 13 jul 2026)
========================================================================================
    "IDENTICO HOJE NAO E' UM ESTADO. E' UMA CONTAGEM DECRESCENTE."

Dos 10 duplicados de hoje, 4 ja tinham divergido e 6 ainda eram identicos. Um guarda que
so falhasse nos divergidos deixava passar os 6 -- que nao estavam bem: estavam A' ESPERA
DA VEZ. A RECEITA_VIDEO_NOVO.md foi copia inofensiva durante semanas; depois divergiu e
passou a mandar MIN_PROF=0,35, desligando metade da B15.

    >>> O objetivo do guarda nao e' apanhar o INCENDIO. E' apanhar o FOSFORO.

    mesmo nome em dois sitios .......... FALHA
      ...excepto se UM deles for um PONTEIRO (contem "ESTE FICHEIRO ESTA MORTO")
    um PONTEIRO que CRESCEU ............ FALHA   (alguem escreveu nele)
    snapshots/ e BACKUPS/ .............. IGNORA  (sao fotos do passado; e' o que devem ser)

🔑 A FONTE E' SEMPRE `padelpro-vision/`. E' a UNICA pasta que e' um repo git -- a unica que
   vai para o GitHub. Um ficheiro na raiz NAO e' versionado: se o Mac morrer, PERDE-SE.

========================================================================================
AS 5 VERIFICACOES
========================================================================================
  1. DUPLICADOS ................ dois ficheiros com o mesmo nome            -> FALHA
  2. ✅ QUE NAO CORRE .......... regra marcada ✅ que nao existe no codigo   -> FALHA
       2a. a funcao do "onde" existe?
       2b. e' CHAMADA -- e com TODOS os argumentos?  (a S23 quase se perdeu assim:
           o teste_regressao e o ablacao chamavam rallies() SEM os quiques.)
       2c. o interruptor REGRAS[...] existe, esta True, e e' LIDO no codigo?
       2d. o "onde" aponta para um ficheiro que EXISTE?
  3. ✅ QUE VALE +0,0 .......... a ablacao nao mexe um numero               -> AVISA
  4. COLISAO DE NOMES .......... o mesmo nome de regra usado duas vezes     -> FALHA
       + um interruptor vivo que a FONTE nunca nomeia (foi assim que a S23 se perdeu)
  5. SINONIMOS ................. "RESSALTO" = "QUIQUE" = "BOLA NO CHAO"     -> FALHA/mapa
       tres nomes, a mesma coisa. Procurar so por um da' a metade errada.

  Codigo de saida: 0 = limpo · 1 = ha FALHAS.   (os AVISOS nao fazem falhar)
"""
import ast
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------------------
# ONDE
# ---------------------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent          # padelpro-vision/  <- A FONTE
RAIZ = REPO.parent                              # a pasta do projeto

FONTE_REGRAS = REPO / "REGRAS_DO_VASCO.md"      # as regras. A FONTE UNICA.
MODULO       = REPO / "gerar_tempo_util.py"     # o pipeline

# os RUNNERS: o que corre a serio. E' AQUI que uma chamada incompleta mata uma regra.
RUNNERS = ["gerar_tempo_util.py", "teste_regressao.py", "ablacao.py"]

# a marca de um PONTEIRO (ja e' a convencao do Vasco desde 13 jul)
MARCA_PONTEIRO = "ESTE FICHEIRO ESTA MORTO"
PONTEIRO_MAX_LINHAS = 30                        # um ponteiro que cresce = alguem escreveu nele

# pastas que NAO contam (fotos do passado, ambientes, codigo de terceiros)
IGNORAR_DIRS = {
    ".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules",
    "site-packages", ".claude", ".github", ".ipynb_checkpoints",
    "snapshots", "BACKUPS",                     # <- fotos do passado. E' o que devem ser.
    "padel_analytics", "pr_ball_detector", "blurball", "padelpro-analise-v9",
    "cortes_padel", "pesos", "outputs",
}
IGNORAR_PREFIXOS = ("cortes_", "dados_", "dataset_", "M1_")   # snapshots com data no nome

SINONIMOS = [("ressalto", "quique", "bola no chao", "bola no chão")]

FALHAS, AVISOS = [], []


def falha(cat, msg):
    FALHAS.append((cat, msg))


def aviso(cat, msg):
    AVISOS.append((cat, msg))


def sem_acentos(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def ignorada(p: Path) -> bool:
    for parte in p.parts:
        if parte in IGNORAR_DIRS or parte.startswith(IGNORAR_PREFIXOS):
            return True
    return False


def ficheiros(ext):
    for p in RAIZ.rglob(f"*{ext}"):
        if not p.is_file() or ignorada(p.relative_to(RAIZ)):
            continue
        # 🚨 FALSO POSITIVO apanhado pelo Vasco (13 jul): eu dizia que os 6 `__init__.py`
        #    eram "6 copias vivas que JA DIVERGIRAM". Nao sao copias -- sao os __init__ de
        #    PACOTES DIFERENTES. O nome e' igual porque TEM de ser.
        #    >>> "Um guarda que da' falsos positivos treina as pessoas a ignora-lo." (Vasco)
        #    Estes tratam-se pelo CAMINHO, nao pelo nome.
        if p.name.startswith("__") and p.name.endswith("__.py"):
            continue
        yield p


def rel(p: Path) -> str:
    return str(p.relative_to(RAIZ))


def achar_ficheiro(nome):
    """Procura o ficheiro em TODA a arvore -- nao so' na raiz do repo. (o bug do m1_tempo_util)"""
    alvo = Path(nome).name
    return [p for p in RAIZ.rglob(alvo)
            if p.is_file() and not ignorada(p.relative_to(RAIZ))]


def achar_classe(nome):
    """O "onde" pode citar uma CLASSE (`Campo.zona()`), nao um modulo. Procura-a."""
    pat = re.compile(rf"^\s*class\s+{re.escape(nome)}\b", re.M)
    return [p for p in RAIZ.rglob("*.py")
            if p.is_file() and not ignorada(p.relative_to(RAIZ))
            and pat.search(p.read_text(encoding="utf-8", errors="replace"))]


_IMPORTADOS = None


def importado(p: Path) -> bool:
    """Alguem importa este modulo? Um .py que ninguem importa NAO CORRE.

    Por AST, nao por texto: a primeira versao disto procurava o nome no texto dos .py e
    dava FALSO-POSITIVO -- encontrava-o num COMENTARIO (o meu, aqui neste ficheiro).
    Um guarda que se engana a si proprio nao vale nada.
    """
    global _IMPORTADOS
    if _IMPORTADOS is None:
        _IMPORTADOS = set()
        for q in RAIZ.rglob("*.py"):
            if not q.is_file() or ignorada(q.relative_to(RAIZ)):
                continue
            try:
                arv = ast.parse(q.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            for n in ast.walk(arv):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        _IMPORTADOS.add(a.name.split(".")[-1])
                elif isinstance(n, ast.ImportFrom):
                    if n.module:
                        _IMPORTADOS.add(n.module.split(".")[-1])
                    for a in n.names:
                        _IMPORTADOS.add(a.name)
    return p.stem in _IMPORTADOS


# =======================================================================================
# 1. DUPLICADOS   —   "identico hoje nao e' um estado. e' uma contagem decrescente."
# =======================================================================================
def v1_duplicados():
    print("\n① DUPLICADOS — dois ficheiros com o mesmo nome")
    por_nome = {}
    # 🚨 13 jul (o Vasco mandou rever "a fundo"): esta lista era só (".md", ".py").
    #    ⇒ O GUARDA NUNCA OLHOU PARA OS **DADOS**. E os dados são a coisa de que o
    #    `teste_regressao.py` DEPENDE. Duplicar o `traj_frames...csv` ou o `player_boxes...pkl`
    #    passava-lhe debaixo do nariz — e uma cópia velha da bola dá NÚMEROS ERRADOS EM SILÊNCIO.
    #
    #    >>> UM GUARDA COM UM PONTO CEGO É UM GUARDA QUE ENSINA A CONFIAR NO PONTO CEGO.
    for ext in (".md", ".py", ".csv", ".pkl"):   # ⚠️ .json NAO: o dataset_bola_637 tem milhares
                                                 #    e o guarda afogava-se (timeout). Estes dois sao
                                                 #    os que o teste_regressao LE — sao os que contam.
        for p in ficheiros(ext):
            por_nome.setdefault(p.name, []).append(p)

    n_dup = n_div = 0
    for nome, paths in sorted(por_nome.items()):
        if len(paths) < 2:
            continue
        n_dup += 1
        textos, ponteiros = [], []
        for p in paths:
            t = p.read_text(encoding="utf-8", errors="replace")
            textos.append(t)
            e_ponteiro = MARCA_PONTEIRO in sem_acentos(t).upper()
            ponteiros.append(e_ponteiro)
            if e_ponteiro and len(t.splitlines()) > PONTEIRO_MAX_LINHAS:
                falha("PONTEIRO QUE CRESCEU",
                      f"{rel(p)} e' um ponteiro com {len(t.splitlines())} linhas "
                      f"(max {PONTEIRO_MAX_LINHAS}). ALGUEM ESCREVEU NELE.")

        vivos = [p for p, e in zip(paths, ponteiros) if not e]
        divergiu = len(set(textos)) > 1
        if divergiu:
            n_div += 1

        if len(vivos) >= 2:                       # >=2 copias VIVAS => a doenca
            estado = "JA DIVERGIRAM" if len(set(
                textos[i] for i, e in enumerate(ponteiros) if not e)) > 1 else "identicos (ainda)"
            falha("DUPLICADO",
                  f"{nome} — {len(vivos)} copias VIVAS [{estado}]: "
                  + " · ".join(rel(p) for p in vivos)
                  + f"\n         👉 a fonte e' padelpro-vision/. A outra deve virar PONTEIRO "
                    f'(1.a linha: "# ⛔ ESTE FICHEIRO ESTÁ MORTO. NÃO ESCREVAS AQUI.")')
        else:
            print(f"   ✅ {nome:42s} ponteiro OK  ({len(paths)} sitios)")

    print(f"   → {n_dup} nomes duplicados · {n_div} com conteudo DIFERENTE")


# =======================================================================================
# leitura do CODIGO (nao do mapa)
# =======================================================================================
def ler_codigo():
    src = MODULO.read_text(encoding="utf-8")
    arv = ast.parse(src)

    defs = {}                                   # nome -> nº de parametros
    for n in arv.body:
        if isinstance(n, ast.FunctionDef):
            a = n.args
            defs[n.name] = len(a.posonlyargs) + len(a.args)

    regras = {}                                 # o dict REGRAS = {...}
    for n in ast.walk(arv):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "REGRAS" for t in n.targets):
            for k, v in zip(n.value.keys, n.value.values):
                regras[k.value] = bool(v.value)

    lidos = set()                               # interruptores LIDOS algures no codigo
    for p in RAIZ.rglob("*.py"):
        if p.is_file() and not ignorada(p.relative_to(RAIZ)):
            for m in re.finditer(r'REGRAS\[\s*[\'"]([A-Z0-9_]+)[\'"]\s*\]',
                                 p.read_text(encoding="utf-8", errors="replace")):
                lidos.add(m.group(1))
    return src, defs, regras, lidos


def chamadas_nos_runners(defs):
    """{funcao: [(runner, n_args)]} — so nos RUNNERS. E' onde uma regra morre em silencio."""
    out = {}
    for nome in RUNNERS:
        p = REPO / nome
        if not p.exists():
            falha("RUNNER EM FALTA", f"{nome} nao existe")
            continue
        arv = ast.parse(p.read_text(encoding="utf-8"))
        for n in ast.walk(arv):
            if isinstance(n, ast.Call):
                f = n.func
                alvo = f.attr if isinstance(f, ast.Attribute) else (
                    f.id if isinstance(f, ast.Name) else None)
                if alvo in defs:
                    out.setdefault(alvo, []).append(
                        (nome, len(n.args) + len(n.keywords)))
    return out


# =======================================================================================
# as regras do REGRAS_DO_VASCO.md  (a FONTE UNICA)
# =======================================================================================
# ⚠️ os ** sao OPCIONAIS. A B6 esta escrita "| B6 |" (sem negrito) e a minha 1.a versao,
#    que exigia "| **B6** |", NUNCA A LEU — e eu conclui que "nao existe regra B6".
#    Um guarda que nao le' uma regra e' pior do que um guarda que nao existe: da' a
#    ILUSAO de que aquilo foi verificado.
LINHA = re.compile(r"^\|\s*\*{0,2}([A-Z]+\d+[a-z]?)\*{0,2}\s*\|(.*)$")
RE_FUNC = re.compile(r"`([a-zA-Z_][\w]*)\.([a-zA-Z_]\w*)\(\)`")
RE_FICH = re.compile(r"`([\w/\.\-]+\.py)`")
IMPLEMENTADA = re.compile(r"✅|implementada|a correr|já corre|ja corre|é a arquitetura|é a spec",
                          re.I)
NAO_IMPL = re.compile(r"por implementar|bloqueada|registar", re.I)


def ler_regras():
    regras, ordem = {}, []
    for i, linha in enumerate(FONTE_REGRAS.read_text(encoding="utf-8").splitlines(), 1):
        m = LINHA.match(linha)
        if not m:
            continue
        rid, resto = m.group(1), m.group(2)
        cel = [c.strip() for c in resto.split("|")]
        while cel and not cel[-1]:
            cel.pop()
        if len(cel) >= 3:                       # | ID | desc | estado | onde |
            onde, estado, desc = cel[-1], cel[-2], " | ".join(cel[:-2])
        else:                                   # tabelas de 2 colunas (D, C): | ID | desc |
            onde, estado, desc = "", "", " | ".join(cel)
        ordem.append((rid, i))
        if rid in regras:
            falha("COLISAO DE NOMES",
                  f"a regra {rid} aparece DUAS VEZES no REGRAS_DO_VASCO.md "
                  f"(linhas {regras[rid]['linha']} e {i}). Foi assim com a S23, a B11 e a B8.")
        else:
            regras[rid] = dict(linha=i, desc=desc, estado=estado, onde=onde)
    return regras


# =======================================================================================
# 2. REGRA ✅ QUE NAO EXISTE / NAO CORRE
# =======================================================================================
def v2_marcadas_mas_mortas(regras, defs, switches, lidos, calls):
    print("\n② REGRA MARCADA ✅ QUE NAO CORRE NO CODIGO")
    n = 0
    for rid, r in regras.items():
        if not IMPLEMENTADA.search(r["estado"]) or NAO_IMPL.search(r["estado"]):
            continue
        n += 1
        # 2a/2b — a funcao citada no "onde"
        #
        # 🚨 BUG APANHADO PELO VASCO (13 jul), o SEGUNDO: eu so' validava o "onde" quando o
        #    modulo era o `gerar_tempo_util`. Tudo o que apontasse para OUTRO modulo passava
        #    SEM SER LIDO. E a B6 ("2 cliques = direcao") apontava para
        #    `m1_tempo_util._tracklets()` -- o ficheiro-engodo. Resultado: o guarda disse
        #    "nao existe regra B6" quando ela existia, na linha 67.
        #    >>> O MEU FILTRO ESCONDEU A REGRA QUE O "ONDE" MORTO TINHA FEITO DESAPARECER.
        #    Agora valida-se QUALQUER modulo.
        for mod, fn in RE_FUNC.findall(r["onde"]):
            if mod == MODULO.stem:                          # o pipeline: temos o AST
                alvo, existe = MODULO, fn in defs
                corre = fn in calls
            else:                                           # outro modulo -- ou uma CLASSE
                achados = achar_ficheiro(mod + ".py") or achar_classe(mod)
                if not achados:
                    falha("✅ ONDE SEM DESTINO",
                          f"{rid} esta marcada implementada e cita `{mod}.{fn}()` "
                          f"— nao existe nem o modulo `{mod}.py` nem a classe `{mod}`. "
                          f"(linha {r['linha']})")
                    continue
                alvo = achados[0]
                txt = alvo.read_text(encoding="utf-8", errors="replace")
                existe = re.search(rf"^\s*def\s+{re.escape(fn)}\s*\(", txt, re.M) is not None
                corre = importado(alvo)
            if not existe:
                falha("✅ SEM FUNCAO",
                      f"{rid} esta marcada implementada e cita `{mod}.{fn}()` "
                      f"— essa funcao NAO EXISTE em {rel(alvo)}. (linha {r['linha']})")
            elif not corre:
                falha("✅ NUNCA CHAMADA",
                      f"{rid}: `{mod}.{fn}()` existe mas NAO CORRE "
                      f"(nenhum runner a chama / ninguem importa o modulo). "
                      f"Existe e nao corre. (linha {r['linha']})")
        # 2d — o "onde" aponta para um ficheiro que existe? E esse ficheiro CORRE?
        #
        # 🚨 BUG APANHADO PELO VASCO (13 jul): eu procurava o ficheiro SO' na raiz do repo.
        #    O `m1_tempo_util.py` EXISTIA — em padelpro/modules/ — e eu disse "nao existe".
        #    E um ponteiro para um ficheiro REAL QUE NAO CORRE e' MUITO PIOR do que um
        #    ponteiro morto: o morto da' erro e alguem corrige; o vivo leva-te a LER A
        #    VERSAO ERRADA DA REGRA — e a acreditar nela.
        for fich in RE_FICH.findall(r["onde"]):
            achados = achar_ficheiro(fich)
            if not achados:
                falha("✅ ONDE MORTO",
                      f"{rid} esta marcada implementada e aponta para `{fich}` "
                      f"— esse ficheiro NAO EXISTE em lado nenhum. (linha {r['linha']})")
                continue
            vivos = [p for p in achados if importado(p)]
            if not vivos:
                falha("✅ ONDE = ENGODO VIVO",
                      f"{rid} esta marcada implementada e aponta para `{fich}` "
                      f"({', '.join(rel(p) for p in achados)}) — esse ficheiro EXISTE "
                      f"mas NINGUEM O IMPORTA. NAO CORRE.\n"
                      f"         👉 quem for la' procurar a regra le' a VERSAO ERRADA e "
                      f"acredita nela. E' PIOR que um ponteiro morto. (linha {r['linha']})")
    print(f"   → {n} regras marcadas implementadas, verificadas contra o codigo")

    # 2b — chamadas INCOMPLETAS nos runners (foi assim que a S23 quase se perdeu)
    print("\n②b CHAMADAS INCOMPLETAS NOS RUNNERS (a regra esta la' e NAO corre dentro do teste)")
    for fn, usos in sorted(calls.items()):
        for runner, nargs in usos:
            if nargs < defs[fn]:
                falha("CHAMADA INCOMPLETA",
                      f"{runner}: {fn}() chamada com {nargs} argumentos, "
                      f"mas a definicao tem {defs[fn]}. "
                      f"Os argumentos que faltam SAO REGRAS que nao vao correr. "
                      f"(foi exactamente isto com o rallies() e os quiques da S23)")
    print(f"   → {sum(len(v) for v in calls.values())} chamadas verificadas nos runners")

    # 2c — os interruptores
    print("\n②c INTERRUPTORES REGRAS[...]")
    for k, v in switches.items():
        if k not in lidos and v:
            falha("INTERRUPTOR MORTO",
                  f'REGRAS["{k}"] esta LIGADO mas NUNCA E\' LIDO no codigo. '
                  f"Esta la' a fingir que trabalha.")
        elif k not in lidos:
            aviso("INTERRUPTOR SEM CODIGO",
                  f'REGRAS["{k}"] esta DESLIGADO e nao e\' lido em lado nenhum. '
                  f"⚠️ Liga-lo NAO FAZ NADA — nao ha codigo por tras. "
                  f"E' um interruptor a fingir que a regra existe.")
        else:
            print(f"   {'✅' if v else '⛔'} {k:18s} {'ligado' if v else 'DESLIGADO por decisao'}"
                  f"{'' if v else ' (razao no gerar_tempo_util.py)'}")


# =======================================================================================
# 3. ABLACAO — a regra ✅ que vale +0,0
# =======================================================================================
LINHA_ABL = re.compile(
    r"^\s{2}(\S.*?)\s*\|\s*\d+\s*\|\s*[\d.]+%\s*\(\s*([-+][\d.]+)\)\s*\|"
    r"\s*[\d.]+%\s*\(\s*([-+][\d.]+)\)")


def v3_ablacao():
    print("\n③ ABLACAO — uma regra ✅ que vale +0,0 ficou REDUNDANTE... OU NAO CORRE")
    try:
        r = subprocess.run([sys.executable, "ablacao.py"], cwd=REPO,
                           capture_output=True, text=True, timeout=900)
    except Exception as e:                                   # noqa: BLE001
        aviso("ABLACAO", f"nao correu: {e}")
        return
    if r.returncode != 0:
        aviso("ABLACAO", f"ablacao.py saiu com {r.returncode}:\n{r.stderr[-500:]}")
        return
    nulas = 0
    for linha in r.stdout.splitlines():
        m = LINHA_ABL.match(linha)
        if not m:
            continue
        nome, dr, dp = m.group(1).strip(), float(m.group(2)), float(m.group(3))
        if abs(dr) < 0.05 and abs(dp) < 0.05:
            nulas += 1
            aviso("VALE +0,0",
                  f"'{nome}' — desliga-la nao muda UM UNICO NUMERO. "
                  f"Ou ficou REDUNDANTE, ou NAO CORRE. As duas precisam de ser ditas em voz alta.")
        else:
            print(f"   ✅ {nome:38s} recall {dr:+5.1f} · precisao {dp:+5.1f}")
    print(f"   → {nulas} regras a valer +0,0")


# =======================================================================================
# 4. COLISAO DE NOMES  (a colisao regra-a-regra ja' foi apanhada no ler_regras)
# =======================================================================================
def v4_colisoes(regras, switches):
    print("\n④ COLISAO DE NOMES — a S23 era duas regras. A B11 era duas. A B8 era duas.")
    texto = FONTE_REGRAS.read_text(encoding="utf-8")
    for k in switches:
        if k not in texto:
            falha("A FONTE NAO CONHECE O INTERRUPTOR",
                  f'REGRAS["{k}"] corre no codigo, mas o nome "{k}" NAO APARECE em '
                  f"{FONTE_REGRAS.name}. "
                  f"Quem procurar a regra pelo nome do interruptor NAO A ENCONTRA — "
                  f"e implementa-a OUTRA VEZ, por cima. Foi assim que a S23 se duplicou.")
    print(f"   → {len(regras)} regras · {len(switches)} interruptores verificados")


# =======================================================================================
# 5. SINONIMOS — "RESSALTO" = "QUIQUE" = "BOLA NO CHAO"
# =======================================================================================
def v5_sinonimos(regras, defs, calls):
    print("\n⑤ SINONIMOS — 'RESSALTO' = 'QUIQUE' = 'BOLA NO CHAO' (tres nomes, a mesma coisa)")
    for grupo in SINONIMOS:
        achadas = {}
        for rid, r in regras.items():
            txt = sem_acentos((r["desc"] + " " + r["estado"]).lower())
            hits = [t for t in grupo if sem_acentos(t) in txt]
            if hits:
                achadas[rid] = (hits, r)
        impl = [k for k, (_, r) in achadas.items() if IMPLEMENTADA.search(r["estado"])
                and not NAO_IMPL.search(r["estado"])]
        print(f"   grupo {'/'.join(grupo[:3])}: {len(achadas)} regras "
              f"— a CORRER: {', '.join(sorted(impl)) or 'NENHUMA'}")
        for rid, (hits, r) in sorted(achadas.items()):
            marca = "✅" if rid in impl else "🔴"
            print(f"      {marca} {rid:5s} (encontra-se por: {', '.join(hits)})")
        if len(grupo) > 1 and impl:
            texto = sem_acentos(FONTE_REGRAS.read_text(encoding="utf-8")).lower()
            for t in grupo:
                if sem_acentos(t).lower() not in texto:
                    falha("SINONIMO PERDIDO",
                          f'o termo "{t}" nao aparece em {FONTE_REGRAS.name}. '
                          f"Quem procurar por ele conclui que a regra nao existe.")

        # o reverso: uma regra dada como MORTA que aponta para codigo VIVO
        for rid, (_, r) in achadas.items():
            if NAO_IMPL.search(r["estado"]) and not IMPLEMENTADA.search(r["estado"]):
                for mod, fn in RE_FUNC.findall(r["onde"]):
                    if fn in defs and fn in calls:
                        falha("MAPA MENTE PARA BAIXO",
                              f"{rid} diz 'por implementar' mas cita `{fn}()`, que EXISTE "
                              f"e E' CHAMADA. O codigo corre; o mapa diz que nao.")


# =======================================================================================
# 6. O GROUND-TRUTH — a COLEIRA
#
#    A regua que CORRE e' o `GT = [...]` HARD-CODED no gerar_tempo_util.py.
#    Os .md do ground-truth NAO SAO LIDOS POR NINGUEM ⇒ podem apodrecer anos sem nada gritar.
#    Foi o que aconteceu: DUAS das tres copias tinham 12 rallies (a verdade sao 13), e as
#    duas erradas eram justamente as que iam para o GitHub.
#
#        "Um documento que ninguem le' nao tem como estar certo. So' tem como estar
#         desatualizado."   — Vasco, 13 jul 2026
#
#    Isto NAO E' A CURA (a cura e' o codigo LER o ficheiro — fica para o VIDEO 2, junto com
#    a calibracao). E' a COLEIRA: obriga o .md a concordar com o codigo, senao FALHA.
# =======================================================================================
RE_GT_MD = re.compile(r"GT\s*=\s*\[(.*?)\]", re.S)
RE_PAR = re.compile(r"\(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)")


def gt_do_codigo():
    for n in ast.walk(ast.parse(MODULO.read_text(encoding="utf-8"))):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "GT" for t in n.targets):
            try:
                v = ast.literal_eval(n.value)
            except ValueError:
                continue
            if v:                                   # ignora o `GT = []` do video sem ground-truth
                return [(float(a), float(b)) for a, b in v]
    return None


def v6_ground_truth():
    print("\n⑥ GROUND-TRUTH — a COLEIRA (o .md tem de concordar com o codigo)")
    cod = gt_do_codigo()
    if cod is None:
        falha("GT SEM CODIGO", f"nao encontrei o `GT = [...]` em {MODULO.name}")
        return
    print(f"   codigo ({MODULO.name}): {len(cod)} rallies")

    pasta = REPO / "data" / "ground_truth"
    mds = sorted(pasta.glob("*.md")) if pasta.is_dir() else []
    if not mds:
        falha("GT SEM FICHEIRO",
              f"nao ha nenhum .md em {rel(pasta)}/ — a regua nao esta versionada.")
        return
    for md in mds:
        t = md.read_text(encoding="utf-8", errors="replace")
        m = RE_GT_MD.search(t)
        if not m:
            falha("GT SEM BLOCO",
                  f"{rel(md)} nao tem nenhum bloco `GT = [...]` para comparar com o codigo. "
                  f"Sem isso, este ficheiro e' ENFEITE — pode apodrecer sem nada gritar.")
            continue
        doc = [(float(a), float(b)) for a, b in RE_PAR.findall(m.group(1))]
        if doc == cod:
            print(f"   ✅ {rel(md)}: {len(doc)} rallies — CONCORDA com o codigo")
        else:
            falha("GT DIVERGENTE",
                  f"{rel(md)} tem {len(doc)} rallies; o codigo tem {len(cod)}. "
                  f"A REGUA E' DE TUDO — se ela esta errada, TUDO o que se mede esta torto.\n"
                  f"         doc: {doc}\n         cod: {cod}")


# =======================================================================================
def main():
    so_estrutura = "--so-estrutura" in sys.argv
    print("=" * 88)
    print("🛡️  VERIFICAR FONTE — o guarda")
    print(f"   fonte:  {rel(REPO)}/   (a unica pasta versionada -> GitHub)")
    print(f"   regras: {rel(FONTE_REGRAS)}")
    print("=" * 88)

    src, defs, switches, lidos = ler_codigo()
    regras = ler_regras()                       # (ja' falha nas colisoes)
    calls = chamadas_nos_runners(defs)

    v1_duplicados()
    v2_marcadas_mas_mortas(regras, defs, switches, lidos, calls)
    if so_estrutura:
        print("\n③ ABLACAO — SALTADA (--so-estrutura)")
    else:
        v3_ablacao()
    v4_colisoes(regras, switches)
    v5_sinonimos(regras, defs, calls)
    v6_ground_truth()

    print("\n" + "=" * 88)
    if AVISOS:
        print(f"🟠 {len(AVISOS)} AVISO(S) — nao fazem falhar, mas tem de ser ditos em voz alta:\n")
        for cat, m in AVISOS:
            print(f"   🟠 [{cat}] {m}\n")
    if FALHAS:
        print(f"🔴 {len(FALHAS)} FALHA(S):\n")
        for cat, m in FALHAS:
            print(f"   🔴 [{cat}] {m}\n")
        print("=" * 88)
        print("🔴 O GUARDA DISPAROU. Nada disto parte o pipeline — e' por isso que e' perigoso.")
        return 1
    print("=" * 88)
    print("✅ FONTE LIMPA. Uma fonte, um nome por regra, e tudo o que esta ✅ corre mesmo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
