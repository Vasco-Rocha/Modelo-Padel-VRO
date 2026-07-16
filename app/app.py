#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PADELPRO VISION — A BANCADA.   (passo 1: o esqueleto)

  O QUE FAZ:  lista os vídeos · toca-os com SEEK · recebe vídeos novos ·
              BLOQUEIA quem não tem calibração.

  O QUE NÃO FAZ (de propósito):
      ⛔ NÃO EDITA O `gerar_tempo_util.py`. NEM NENHUM FICHEIRO DO PIPELINE.
         Esta app LÊ. Uma caneta de cada vez.
      ⛔ NÃO tem números do estado do modelo escritos aqui dentro.
         `python3 teste_regressao.py` é que diz o estado. Um número escrito APODRECE.

  ⚠️  C1 (LEI):  CAMPO NOVO = CALIBRAÇÃO NOVA, À MÃO.
      Um vídeo sem `calibracao_<nome>.json` NÃO TEM BOTÃO DE CORRER.
      Não é um aviso — é um BLOQUEIO. Correr com a calibração de outro campo
      não dá erro: dá NÚMEROS ERRADOS EM SILÊNCIO.

  arrancar:  duplo-clique no ABRIR_APP.command
"""

from flask import (Flask, render_template, send_file, abort, request,
                   redirect, url_for, jsonify)
from pathlib import Path
import subprocess
import shutil
import json
import time
import re

# ─────────────────────────────────────────────────────────────────────────
#  ONDE VIVEM AS COISAS.  Tudo relativo — nada de caminhos absolutos.
# ─────────────────────────────────────────────────────────────────────────
APP_DIR   = Path(__file__).resolve().parent          # .../padelpro-vision/app
REPO      = APP_DIR.parent                           # .../padelpro-vision   (o repo git)
PROJETO   = REPO.parent                              # .../Treino de Modelo…  (onde estão os vídeos)

GT_DIR    = REPO / "data" / "ground_truth"
FRAMES    = APP_DIR / "_frames"                      # thumbnails que a app gera
FRAMES.mkdir(exist_ok=True)

# Um vídeo pode estar na raiz do projeto OU dentro do repo.
PASTAS_DE_VIDEO = [PROJETO, REPO]

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 * 1024   # 8 GB — vídeos são grandes


# ─────────────────────────────────────────────────────────────────────────
#  A CALIBRAÇÃO — a régua de tudo.
# ─────────────────────────────────────────────────────────────────────────
def _slug(nome_do_ficheiro: str) -> str:
    """'Parada4.mp4' -> 'parada4'.  Minúsculas, sem extensão.

    Tem de ser à prova de maiúsculas: o ficheiro é `Parada4.mp4` mas a
    calibração dele chama-se `calibracao_parada4.json`. E a do
    `BarbosaMeireles.mp4` chama-se `calibracao_BarbosaMeireles.json`.
    Os dois têm de bater certo.
    """
    return Path(nome_do_ficheiro).stem.lower()


def calibracao_de(nome_do_ficheiro: str):
    """Devolve o Path da calibração deste vídeo — ou None se não existir.

    ⚠️ NUNCA devolve a calibração de OUTRO vídeo. Nem a `calibracao_campo.json`
    genérica. Um campo sem a SUA calibração é um campo NÃO CALIBRADO.
    """
    alvo = _slug(nome_do_ficheiro)
    for f in REPO.glob("calibracao_*.json"):
        if f.stem[len("calibracao_"):].lower() == alvo:
            return f
    return None


def poligono_de(nome_do_ficheiro: str):
    """O polígono dos jogadores (J15). Separado da calibração — pode faltar só ele."""
    alvo = _slug(nome_do_ficheiro)
    for f in REPO.glob("poligono_*.json"):
        if f.stem[len("poligono_"):].lower() == alvo:
            return f
    return None


def ground_truth_de(nome_do_ficheiro: str):
    """O ground-truth deste vídeo, se alguém já o anotou."""
    alvo = _slug(nome_do_ficheiro)
    if not GT_DIR.is_dir():
        return None
    for f in GT_DIR.glob("*.md"):
        if alvo in f.stem.lower():
            return f
    return None


# ─────────────────────────────────────────────────────────────────────────
#  ⚠️  A CALIBRAÇÃO NÃO CHEGA.
#
#  O `gerar_tempo_util.py` carrega TRÊS coisas antes de fazer seja o que for:
#       CAL   = a calibração          (o campo)
#       BOLA  = traj_frames_*.csv     (o BlurBall já correu?)
#       BOXES = player_boxes_*.pkl    (o YOLO dos jogadores já correu?)
#
#  A primeira versão desta app dizia "calibrado ⇒ pode correr". ERA MENTIRA.
#  Um vídeo calibrado sem a bola detetada não corre — rebenta com
#  FileNotFoundError. E um botão que promete e rebenta é pior que não haver botão.
# ─────────────────────────────────────────────────────────────────────────
PASTAS_DE_DADOS = ["dados_{}", "dados_{}_mac", "data/{}"]


def _dados_de(nome_do_ficheiro: str, padrao: str):
    """Procura um ficheiro de dados deste vídeo, em qualquer das pastas conhecidas."""
    alvo = _slug(nome_do_ficheiro)
    candidatos = []
    for raiz in (PROJETO, REPO):
        for molde in PASTAS_DE_DADOS:
            d = raiz / molde.format(alvo)
            if d.is_dir():
                candidatos += sorted(d.glob(padrao))
    return candidatos[0] if candidatos else None


def bola_de(nome):   return _dados_de(nome, "traj_frames_*.csv")      # o BlurBall
def boxes_de(nome):  return _dados_de(nome, "player_boxes_*.pkl")     # o YOLO


# ── QUEM SABE CORRER O QUÊ ───────────────────────────────────────────────
#  O pipeline NÃO é agnóstico ao vídeo: tem FPS, N_FRAMES e os caminhos
#  fixos no topo do ficheiro. Para cada vídeo existe (ou não) um "runner"
#  que aponta o MESMO pipeline àquele vídeo, por monkeypatch, SEM O EDITAR.
#
#  ⛔ Não invento runners. Se um vídeo não tem, a app DIZ que não tem.
RUNNERS = {
    "parada4":          "gerar_tempo_util.py",
    "barbosameireles":  "correr_tempo_util_barbosa.py",
}


def runner_de(nome):
    return RUNNERS.get(_slug(nome))


# ── O M2 (as fases) — corre noutra conversa, aponto-lhe sem o editar ──────
#  O M2 vive em `confrontos_m2.py <vid>` e cospe os clips M2_<FASE>_x_<FASE>_<vid>.mp4.
#  ⚠️ O <vid> do M2 NÃO é o meu slug: o BarbosaMeireles.mp4 é "barbosa" para o M2.
#     E o pipeline do M2 é a caneta da OUTRA conversa — eu só o CORRO. Nunca o edito.
RUNNERS_M2 = {
    "parada4":          ("confrontos_m2.py", "parada4"),
    "barbosameireles":  ("confrontos_m2.py", "barbosa"),
}


def runner_m2_de(nome):
    return RUNNERS_M2.get(_slug(nome))


def m2_videos_de(nome):
    """Os clips de fases que o M2 já produziu para este jogo. Vazio se ainda não correu."""
    r = runner_m2_de(nome)
    if not r:
        return []
    vid = r[1]
    fs = sorted(PROJETO.glob(f"M2_*_{vid}.mp4"), key=lambda f: f.name)
    return [f.name for f in fs]


# ─────────────────────────────────────────────────────────────────────────
#  A FICHA DO JOGO — duplas, vídeo da análise, relatórios.
#
#  ⚠️ O modelo NÃO SABE quem são os jogadores (a regra da cor, J6+, não corre).
#     Os nomes são ESCRITOS À MÃO — vivem num `jogo_<slug>.json` ao lado do vídeo.
#     A app não os inventa. Se não os escreveste, ficam vazios — e diz-se que estão.
#
#  Os RELATÓRIOS chegam como HTML, feitos noutra conversa. A app NÃO os gera —
#  hospeda-os. Cada coisa na sua caneta. Vivem em `relatorios/<slug>/`.
# ─────────────────────────────────────────────────────────────────────────
RELATORIOS = PROJETO / "relatorios"


def ficha_path(nome):
    return PROJETO / f"jogo_{_slug(nome)}.json"


def ler_ficha(nome):
    """Os nomes das duplas e a metadata. Vazio se ninguém escreveu ainda."""
    p = ficha_path(nome)
    base = {"duplaA": ["", ""], "duplaB": ["", ""],
            "data": "", "local": "", "resultado": "", "notas": ""}
    if p.is_file():
        try:
            base.update(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return base


def video_analise_de(nome):
    """O TEMPO_UTIL_<slug>.mp4 que o pipeline produziu — ligado pelo nome, sozinho.

    ⚠️ Aceita só o que casa com ESTE jogo. Um `TEMPO_UTIL_v14_FINAL.mp4` não é
       a análise de nenhum jogo — é uma versão antiga do Parada4. Não se liga.
    """
    alvo = _slug(nome)
    for cand in (PROJETO / f"TEMPO_UTIL_{Path(nome).stem}.mp4",
                 REPO / f"TEMPO_UTIL_{Path(nome).stem}.mp4"):
        if cand.is_file():
            return cand.name
    # o Parada4 tem o dele guardado como TEMPO_UTIL.mp4 dentro do repo
    if alvo == "parada4" and (REPO / "TEMPO_UTIL.mp4").is_file():
        return "::repo::TEMPO_UTIL.mp4"
    return None


def relatorios_de(nome):
    """Os .html largados em relatorios/<slug>/. Ordenados do mais recente."""
    pasta = RELATORIOS / _slug(nome)
    if not pasta.is_dir():
        return []
    fs = sorted(pasta.glob("*.html"), key=lambda f: -f.stat().st_mtime)
    return [{"ficheiro": f.name,
             "mod": time.strftime("%d/%m/%Y %H:%M", time.localtime(f.stat().st_mtime))}
            for f in fs]


# ─────────────────────────────────────────────────────────────────────────
#  OS VÍDEOS
# ─────────────────────────────────────────────────────────────────────────
def caminho_do_video(nome: str):
    """Resolve um nome de ficheiro para um caminho real.

    🔒 SEGURANÇA: só aceita o NOME. Nada de `../`, nada de caminhos absolutos.
    Sem isto, um pedido a /video/../../../etc/passwd servia o ficheiro.
    """
    nome = Path(nome).name                      # deita fora qualquer diretório
    for pasta in PASTAS_DE_VIDEO:
        p = (pasta / nome)
        if p.is_file() and p.suffix.lower() == ".mp4":
            return p
    return None


def duracao_segundos(caminho: Path):
    """Pergunta ao ffprobe. Se não houver ffprobe, diz que não sabe — não INVENTA.

    (D2: se não ancora num evento visual claro, OMITE.)
    """
    if not shutil.which("ffprobe"):
        return None
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(caminho)],
            capture_output=True, text=True, timeout=20,
        )
        return float(r.stdout.strip())
    except Exception:
        return None


def _mmss(segundos):
    if segundos is None:
        return "?"
    m, s = divmod(int(segundos), 60)
    return f"{m}:{s:02d}"


def listar_videos():
    """Todos os .mp4, com o estado REAL de cada um. Medido do disco, não decorado."""
    vistos, saida = set(), []

    for pasta in PASTAS_DE_VIDEO:
        for f in sorted(pasta.glob("*.mp4")):
            if f.name in vistos:
                continue
            vistos.add(f.name)

            calib  = calibracao_de(f.name)
            bola   = bola_de(f.name)
            boxes  = boxes_de(f.name)
            runner = runner_de(f.name)

            # ⛔ AS QUATRO CONDIÇÕES. Todas. Falta uma → não corre.
            faltam = []
            if not calib:  faltam.append("calibração do campo")
            if not bola:   faltam.append("trajetória da bola (BlurBall)")
            if not boxes:  faltam.append("boxes dos jogadores (YOLO)")
            if not runner: faltam.append("runner (quem aponta o pipeline a este vídeo)")

            saida.append({
                "nome":      f.name,
                "mb":        round(f.stat().st_size / 1_000_000),
                "calibrado": calib is not None,
                "calib":     calib.name if calib else None,
                "bola":      bola.name if bola else None,
                "boxes":     boxes.name if boxes else None,
                "runner":    runner,
                "poligono":  poligono_de(f.name) is not None,
                "gt":        ground_truth_de(f.name) is not None,
                "faltam":    faltam,
                "pode_correr": not faltam,
                # É um JOGO, ou é uma SAÍDA que o próprio modelo produziu?
                # Correr o M1 num vídeo que o M1 gerou não quer dizer nada.
                "derivado":  bool(re.match(
                    r"(TEMPO_UTIL|CHECK|Compilacao|Parada4_|DUVIDAS|M3_|OS_|O_|AS_|BOLA_|"
                    r"JOGADORES_|RESSALTOS|TRAVESSIAS|VIDRO|clip|cortes|TempoUtil)",
                    f.name)),
            })

    saida.sort(key=lambda v: (not v["pode_correr"], v["derivado"], -v["mb"]))
    return saida


# ─────────────────────────────────────────────────────────────────────────
#  AS PÁGINAS
# ─────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    videos = listar_videos()
    return render_template(
        "index.html",
        videos=videos,
        n_prontos=sum(1 for v in videos if v["pode_correr"]),
        n_bloqueados=sum(1 for v in videos if not v["pode_correr"]),
        pasta=PROJETO.name,
    )


@app.route("/ver/<nome>")
def ver(nome):
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    dur = duracao_segundos(p)
    calib = calibracao_de(nome)
    return render_template(
        "ver.html",
        nome=nome,
        mb=round(p.stat().st_size / 1_000_000),
        duracao=dur,
        duracao_txt=_mmss(dur),
        calibrado=calib is not None,
        calib=calib.name if calib else None,
        gt=ground_truth_de(nome) is not None,
        onde=str(p.parent.name),
    )


# ── O SEEK ───────────────────────────────────────────────────────────────
@app.route("/video/<nome>")
def video(nome):
    """Serve o MP4 — COM `Range`.

    🔑 É ISTO que faz a app inteira valer a pena.
       `conditional=True` diz ao Flask para responder `206 Partial Content`
       quando o browser pede um pedaço a meio do ficheiro.
       Sem isto, o browser tem de descarregar 543 MB antes de te mostrar
       o segundo 287 — e é exatamente por isso que um `.html` solto (file://)
       NÃO SERVE. Foi o critério que matou 3 das 5 opções do benchmark.
    """
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    return send_file(p, mimetype="video/mp4", conditional=True)


# ── O FRAME (para calibrar) ──────────────────────────────────────────────
@app.route("/frame/<nome>")
def frame(nome):
    """Extrai um frame limpo do vídeo — é o que se leva para o calibrar_campo.html."""
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    destino = FRAMES / f"{Path(nome).stem}.png"
    if not destino.exists():
        if not shutil.which("ffmpeg"):
            abort(503, "ffmpeg não está instalado")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", "5", "-i", str(p), "-frames:v", "1", str(destino)],
            capture_output=True, timeout=60,
        )
    if not destino.exists():
        abort(500)
    return send_file(destino, mimetype="image/png")


# ── A CALIBRAÇÃO (o bloqueio) ────────────────────────────────────────────
@app.route("/calibrar/<nome>")
def calibrar(nome):
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    return render_template(
        "calibrar.html",
        nome=nome,
        slug=Path(nome).stem,
        ja_calibrado=calibracao_de(nome) is not None,
        tem_ffmpeg=shutil.which("ffmpeg") is not None,
    )


# ── O UPLOAD ─────────────────────────────────────────────────────────────
@app.route("/upload", methods=["POST"])
def upload():
    """Recebe um vídeo novo.

    O `.save()` do Werkzeug escreve em PEDAÇOS, para disco. NÃO carrega os
    543 MB para memória — senão um vídeo de 1 GB rebentava com o Python.
    """
    f = request.files.get("video")
    if not f or not f.filename:
        return jsonify(erro="Nenhum ficheiro."), 400

    nome = Path(f.filename).name                     # 🔒 nunca confiar no nome do cliente
    if not nome.lower().endswith(".mp4"):
        return jsonify(erro="Só .mp4 por agora."), 400

    destino = PROJETO / nome
    if destino.exists():
        return jsonify(erro=f"Já existe um «{nome}». Muda-lhe o nome."), 409

    f.save(destino)
    return jsonify(
        ok=True,
        nome=nome,
        como="recebido",
        # ⚠️ O aviso é dado NO MOMENTO DO UPLOAD. Não à espera que ele repare.
        calibrado=calibracao_de(nome) is not None,
        proximo=url_for("calibrar", nome=nome),
    )


@app.route("/adicionar", methods=["POST"])
def adicionar():
    """Adiciona um vídeo que JÁ ESTÁ no disco, pelo caminho. Sem arrastar, sem enviar.

    🔑 PORQUE EXISTE: "enviar" um vídeo de 543 MB pelo browser é fazer uma
       CÓPIA de um ficheiro que já está no MESMO disco. É lento e é parvo.
       Aqui tento primeiro um HARD LINK: instantâneo, e não ocupa espaço
       nenhum a mais — é o mesmo ficheiro com dois nomes. Só copio se o
       ficheiro estiver noutro disco (uma pen, um disco externo), onde o
       hard link é impossível.
    """
    dados = request.get_json(silent=True) or {}
    bruto = (dados.get("caminho") or "").strip()
    if not bruto:
        return jsonify(erro="Cola o caminho do ficheiro."), 400

    # O ⌥⌘C do Finder e o arrastar-para-o-terminal deixam lixo à volta.
    bruto = bruto.strip('"').strip("'").replace("\\ ", " ")
    if bruto.startswith("file://"):
        from urllib.parse import unquote
        bruto = unquote(bruto[len("file://"):])

    origem = Path(bruto).expanduser()
    if not origem.is_file():
        return jsonify(erro=f"Não encontrei nenhum ficheiro em «{bruto}»."), 404
    if origem.suffix.lower() != ".mp4":
        return jsonify(erro="Só .mp4 por agora."), 400

    destino = PROJETO / origem.name
    if destino.exists():
        if destino.samefile(origem):
            # Já está na pasta. Não é um erro — é o caso normal.
            return jsonify(ok=True, nome=origem.name, como="já estava na pasta",
                           calibrado=calibracao_de(origem.name) is not None,
                           proximo=url_for("calibrar", nome=origem.name))
        return jsonify(erro=f"Já existe outro «{origem.name}» na pasta. Muda-lhe o nome."), 409

    try:
        destino.hardlink_to(origem)          # mesmo disco → instantâneo, 0 bytes
        como = "ligado (instantâneo, sem copiar)"
    except OSError:
        shutil.copy2(origem, destino)        # outro disco → não há alternativa
        como = "copiado"

    return jsonify(
        ok=True,
        nome=origem.name,
        como=como,
        calibrado=calibracao_de(origem.name) is not None,
        proximo=url_for("calibrar", nome=origem.name),
    )


@app.route("/estado")
def estado():
    """O estado, em JSON. Para eu conseguir TESTAR a app sem clicar em nada."""
    return jsonify(videos=listar_videos())


# ═════════════════════════════════════════════════════════════════════════
#   O RUNNER — correr o código de verdade, e mostrar a saída AO VIVO.
#
#   🏃 SÓ O QUE SE CORRE É QUE CONTA.
#      Esta app NÃO tem um único número do modelo escrito lá dentro.
#      Tudo o que vires sai de um `python3` que correu agora, à tua frente.
#
#   ⛔ E NÃO EDITA NADA. Chama os scripts que já existem, tal como estão.
# ═════════════════════════════════════════════════════════════════════════
import threading, time, shlex, queue

# Uma corrida de cada vez. Duas corridas ao mesmo tempo escrevem no mesmo
# ficheiro de saída e a última a gravar ganha — em silêncio.
_TRINCO = threading.Lock()

SCRIPTS = {
    "verificar_fonte": {
        "cmd":  "verificar_fonte.py",
        "nome": "🐕 O GUARDA",
        "desc": "Duplicados · ✅ que não correm · colisões de nomes · o GT do código vs o do .md.",
        "aviso": "Se der VERMELHO, PÁRA. Não corras mais nada.",
    },
    "teste_regressao": {
        "cmd":  "teste_regressao.py",
        "nome": "🔒 O ESTADO TRAVADO",
        "desc": "Recall, precisão, F1, fim_dentro. É ISTO que diz onde o modelo está — mais nada.",
        "aviso": "Se falhar, a ALTERAÇÃO está errada. NUNCA o teste.",
    },
    "ablacao": {
        "cmd":  "ablacao.py",
        "nome": "📊 A ABLAÇÃO",
        "desc": "Quanto vale CADA regra — o que se PERDE ao desligá-la.",
        "aviso": "Uma regra que vale +0,0: ou ficou redundante — ou NÃO CORRE.",
    },
}


def _correr(comando, cwd):
    """Corre um comando e cospe cada linha assim que ela sai. Sem esperar pelo fim."""
    inicio = time.time()
    yield f"$ {comando}\n"
    yield "─" * 60 + "\n"

    p = subprocess.Popen(
        shlex.split(comando),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,          # os erros também aparecem. Não se escondem.
        text=True,
        bufsize=1,
        env={**__import__("os").environ, "PYTHONUNBUFFERED": "1"},
    )
    for linha in p.stdout:
        yield linha
    p.wait()

    seg = time.time() - inicio
    yield "─" * 60 + "\n"
    # ⏱️ O CRONÓMETRO. Daqui a duas semanas, isto responde sozinho à pergunta
    #    "vale a pena uma GPU na net?" — com NÚMEROS, não com palpites.
    if p.returncode == 0:
        yield f"✅ terminou em {seg:.1f} s\n"
    else:
        yield f"❌ FALHOU (código {p.returncode}) — {seg:.1f} s\n"


def _stream(comando, cwd):
    """Server-Sent Events: cada linha chega ao browser no momento em que sai."""
    if not _TRINCO.acquire(blocking=False):
        yield "data: ⛔ Já está a correr outra coisa. Espera que acabe.\n\n"
        yield "data: [FIM]\n\n"
        return
    try:
        for linha in _correr(comando, cwd):
            # ⚠️ Cada linha vai em JSON.
            #    Porquê? Porque o SSE NÃO ENTREGA eventos com `data` vazia —
            #    as linhas em branco desapareciam e a saída chegava espremida,
            #    sem as separações da tabela. Em JSON, "" é um valor válido.
            #    (E de borla: aspas, acentos e barras deixam de poder partir o stream.)
            yield "data: " + json.dumps({"l": linha.rstrip("\n").replace("\r", "")}) + "\n\n"
    except Exception as e:
        yield "data: " + json.dumps({"l": f"❌ ERRO DA APP: {e}"}) + "\n\n"
    finally:
        _TRINCO.release()
        yield "data: " + json.dumps({"fim": True}) + "\n\n"


@app.route("/correr/<chave>")
def correr(chave):
    """Os scripts globais: o guarda, o teste travado, a ablação."""
    s = SCRIPTS.get(chave)
    if not s:
        abort(404)
    return app.response_class(
        _stream(f"python3 {s['cmd']}", REPO),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/correr_m1/<nome>")
def correr_m1(nome):
    """O M1 — o tempo útil — para UM vídeo.

    ⛔ Não invento como se corre um vídeo. Uso o runner que JÁ EXISTE para ele.
       Sem runner, não há botão. (Ver RUNNERS, lá em cima.)
    """
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    r = runner_de(nome)
    if not r:
        abort(400, "Este vídeo não tem runner.")

    # ?video=1 → também gera o MP4 anotado. 🎬 VÍDEO ANTES DE MÉTRICAS.
    extra = " --video" if request.args.get("video") else ""
    return app.response_class(
        _stream(f"python3 {r}{extra}", REPO),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/correr_m2/<nome>")
def correr_m2(nome):
    """O M2 — as fases — para UM jogo.

    ⛔ Não invento como corre. Uso o `confrontos_m2.py <vid>` que a outra conversa
       mantém — CORRO-O, nunca o edito. Sem mapeamento, não há botão vivo:
       o stream diz honestamente que o M2 ainda não está ligado a este jogo.
    """
    if not caminho_do_video(nome):
        abort(404)
    r = runner_m2_de(nome)
    if not r:
        def _msg():
            yield "data: " + json.dumps({"l": "⛔ O M2 ainda não tem runner para este jogo."}) + "\n\n"
            yield "data: " + json.dumps({"l": "   Vive em confrontos_m2.py — na outra conversa."}) + "\n\n"
            yield "data: " + json.dumps({"fim": True}) + "\n\n"
        return app.response_class(_msg(), mimetype="text/event-stream")
    script, vid = r
    return app.response_class(
        _stream(f"python3 {script} {vid}", REPO),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/m2_video/<nome>/<ficheiro>")
def m2_video(nome, ficheiro):
    """Serve um clip de fases do M2 — com Range."""
    if not caminho_do_video(nome):
        abort(404)
    ficheiro = Path(ficheiro).name
    if ficheiro not in m2_videos_de(nome):     # 🔒 só os que pertencem a este jogo
        abort(404)
    p = PROJETO / ficheiro
    if not p.is_file():
        abort(404)
    return send_file(p, mimetype="video/mp4", conditional=True)


@app.route("/painel")
def painel():
    videos = listar_videos()
    return render_template(
        "painel.html",
        scripts=SCRIPTS,
        jogos=[v for v in videos if v["pode_correr"]],
    )


# ═════════════════════════════════════════════════════════════════════════
#   A FICHA DO JOGO
# ═════════════════════════════════════════════════════════════════════════
@app.route("/jogo/<nome>")
def jogo(nome):
    p = caminho_do_video(nome)
    if not p:
        abort(404)
    return render_template(
        "jogo.html",
        nome=nome,
        slug=_slug(nome),
        ficha=ler_ficha(nome),
        video_analise=video_analise_de(nome),      # o TEMPO_UTIL (M1)
        tem_runner_m1=runner_de(nome) is not None,
        m2_videos=m2_videos_de(nome),              # os clips de fases (M2)
        tem_runner_m2=runner_m2_de(nome) is not None,
        relatorios=relatorios_de(nome),
        gt=ground_truth_de(nome) is not None,
    )


@app.route("/jogo/<nome>/guardar", methods=["POST"])
def jogo_guardar(nome):
    """Guarda os nomes das duplas. Escreve um ficheiro NOVO por jogo — nunca por cima de dados do pipeline."""
    if not caminho_do_video(nome):
        abort(404)
    dados = request.get_json(silent=True) or {}
    ficha = ler_ficha(nome)
    for k in ("duplaA", "duplaB", "data", "local", "resultado", "notas"):
        if k in dados:
            ficha[k] = dados[k]
    ficha_path(nome).write_text(
        json.dumps(ficha, ensure_ascii=False, indent=1), encoding="utf-8")
    return jsonify(ok=True)


@app.route("/video_analise/<nome>")
def video_analise(nome):
    """Serve o vídeo da análise — com Range, como qualquer outro."""
    v = video_analise_de(nome)
    if not v:
        abort(404)
    if v.startswith("::repo::"):
        p = REPO / v[len("::repo::"):]
    else:
        p = caminho_do_video(v)
    if not p or not p.is_file():
        abort(404)
    return send_file(p, mimetype="video/mp4", conditional=True)


@app.route("/relatorio/<slug>/<ficheiro>")
def relatorio(slug, ficheiro):
    """Serve um relatório HTML deste jogo.

    🔒 slug e ficheiro são limpos com `.name` — ninguém sai da pasta relatorios/<slug>/.
    """
    slug = _slug(slug)
    ficheiro = Path(ficheiro).name
    if not ficheiro.lower().endswith(".html"):
        abort(404)
    p = RELATORIOS / slug / ficheiro
    if not p.is_file():
        abort(404)
    return send_file(p, mimetype="text/html")


@app.route("/jogo/<nome>/relatorio", methods=["POST"])
def relatorio_add(nome):
    """Recebe um relatório HTML — arrastado, ou pelo caminho de um ficheiro no disco."""
    if not caminho_do_video(nome):
        abort(404)
    slug = _slug(nome)
    pasta = RELATORIOS / slug
    pasta.mkdir(parents=True, exist_ok=True)

    # a) ficheiro arrastado
    f = request.files.get("relatorio")
    if f and f.filename:
        alvo = Path(f.filename).name
        if not alvo.lower().endswith(".html"):
            return jsonify(erro="Um relatório é um ficheiro .html."), 400
        f.save(pasta / alvo)
        return jsonify(ok=True, ficheiro=alvo)

    # b) caminho colado
    dados = request.get_json(silent=True) or {}
    bruto = (dados.get("caminho") or "").strip().strip('"').strip("'").replace("\\ ", " ")
    if bruto.startswith("file://"):
        from urllib.parse import unquote
        bruto = unquote(bruto[len("file://"):])
    if not bruto:
        return jsonify(erro="Arrasta o .html ou cola o caminho."), 400
    origem = Path(bruto).expanduser()
    if not origem.is_file() or origem.suffix.lower() != ".html":
        return jsonify(erro=f"Não encontrei um .html em «{bruto}»."), 404
    shutil.copy2(origem, pasta / origem.name)
    return jsonify(ok=True, ficheiro=origem.name)


if __name__ == "__main__":
    print()
    print("  🎾  PADELPRO VISION — A BANCADA")
    print(f"      vídeos em:  {PROJETO}")
    print(f"      repo em:    {REPO}")
    print()
    print("  ▶  http://localhost:8000")
    print()
    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)
