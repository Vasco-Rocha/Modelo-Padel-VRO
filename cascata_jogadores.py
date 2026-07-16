#!/usr/bin/env python3
"""
👥 A CASCATA DOS JOGADORES  —  J1 → J5, PELA ORDEM DO VASCO   (14 jul 2026)

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py. Não corre modelo nenhum.
   Lê as boxes JÁ DETETADAS (.pkl) e aplica-lhes as REGRAS DO JOGO. Segundos.

A ORDEM É A LEI (REGRAS_DO_VASCO.md, "A CASCATA — a ORDEM importa"):

    1. 🦶 os PÉS no polígono          → LIMPA   (mata o público)
    2. 👀 os 2 de cima sempre visíveis → PERGUNTA (se só há um, o outro não desapareceu)
    3. 🔗 CONTINUIDADE                 → PREENCHE  ⚠️ NÃO é filtro. ACRESCENTA.
    4. 👥 nunca mais de 2 por lado     → CORTA    ← É O ÚLTIMO
    5. 🛡️ os de baixo invisíveis      → DEDUZ    (a AUSÊNCIA é o sinal: recuaram)

🚨 O «2 POR LADO» É O ÚLTIMO. Se cortarmos antes da continuidade, deitamos fora o
   jogador VERDADEIRO e ficamos com o FALSO.  (O servico.py tem a ordem TROCADA.)

🎯 A PERGUNTA QUE ISTO RESPONDE — e é a que matou a S2 e a S30:

       "só 21,8% dos frames têm os 4 jogadores"  →  logo a formação de serviço é cega

   Esse 21,8% era um ARTEFACTO do max_det=4 (que ordena por CONFIANÇA: um espectador
   nítido ganha a um jogador cortado). E o ERRO MAIOR era a ESTATÍSTICA: a regra não
   precisa dos 4 em TODOS os frames — precisa deles NOS 13 MOMENTOS DO SERVIÇO, que
   são o frame mais limpo do jogo.
                                                        ⚖️ MEDIR ANTES DE CITAR.
"""
import json, pickle, sys
from pathlib import Path
import numpy as np
from matplotlib.path import Path as Poly

RAIZ = Path(__file__).parent

# ⚠️ DOIS VÍDEOS, DUAS CÂMARAS. A calibração e o GT são POR VÍDEO (nunca se partilham).
VIDEOS = {
    "parada4": dict(
        boxes=RAIZ / "../dados_parada4/player_boxes_parada4_mac_nocap.pkl",  # SEM CAP (D9/J14)
        poli=RAIZ / "../poligono_parada4_v2.json",
        cal=RAIZ / "calibracao_parada4_v2.json",
        H=540, fps=29.97,
        # o INÍCIO de cada ponto real É um serviço (ground_truth_parada4.md — 13 pontos)
        gt=[38.0, 46.8, 77.6, 95.9, 122.4, 157.9, 178.1, 197.0, 210.5, 229.9, 249.6,
            263.8, 289.1],
    ),
    "barbosa": dict(
        boxes=RAIZ / "../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl",
        poli=RAIZ / "../poligono_barbosa_v2.json",
        cal=RAIZ / "calibracao_BarbosaMeireles.json",
        H=720, fps=29.97002997002997,
        # 21 pontos, anotados pelo Vasco (avaliar_barbosa.py) — só os INÍCIOS
        gt=[13.6, 33.9, 40.3, 54.5, 69.8, 83.3, 135.0, 155.0, 162.9, 188.3, 196.0,
            227.2, 242.3, 257.1, 298.3, 326.1, 352.1, 367.9, 377.9, 406.8, 526.0],
    ),
}

BORDA_BAIXO = 4      # ⚠️ AJUSTE (declarado): px. "a box toca a borda de baixo" (J7)
GAP_INTERP = 12      # ⚠️ AJUSTE (declarado): frames. Buraco que a J5 preenche (~0,4 s)

ev = lambda c, x: float(np.polyval(c, x))


# ------------------------------------------------ ⚙️ A CONFIGURAÇÃO POR VÍDEO — UMA PORTA SÓ
# 🩸 O BUG (15 jul, o Vasco apanhou-o): isto era feito UMA vez no import, com o VID de
#    sys.argv (default parada4). A `cascata(video)` do detetor IGNORAVA o argumento e usava
#    estes globais — logo pedir "barbosa" corria com os jogadores, a régua e o polígono do
#    PARADA4, em SILÊNCIO. Os 23 serviços viravam 16.  A régua, o polígono e as boxes TÊM de
#    vir todos do MESMO vídeo — por isso vivem numa porta só, que se chama de propósito.
def configurar(video):
    """Reconfigura TODOS os globais por-vídeo (boxes + calibração + polígono + régua).
       ⚠️ Chamar SEMPRE antes de correr a cascata noutro vídeo. É a ÚNICA porta."""
    global VID, CFG, BOXES, POLI, CAL, H, FPS, GT, cal, y_base, poli
    if video not in VIDEOS:
        raise ValueError(f"vídeo desconhecido: {video!r}. Conhecidos: {list(VIDEOS)}")
    VID = video
    CFG = VIDEOS[video]
    BOXES, POLI, CAL = CFG["boxes"], CFG["poli"], CFG["cal"]
    H, FPS, GT = CFG["H"], CFG["fps"], CFG["gt"]
    cal = json.load(open(CAL))                        # a régua
    y_base = lambda x: ev(cal["rede_base_coef"], x)
    _p = json.load(open(POLI))                        # o polígono (J1)
    if isinstance(_p, dict):
        _p = _p["poligono"]                           # o do Barbosa vem embrulhado
    poli = Poly(np.array(_p))


configurar(sys.argv[1] if len(sys.argv) > 1 else "parada4")


def meio_campo_px(x, y):
    """A RÉGUA LOCAL. Longe ~95 px · perto ~275 px. Píxeis absolutos não sobrevivem."""
    yb = y_base(x)
    return (abs(ev(cal["servico_perto_coef"], x) - yb) if y > yb
            else abs(yb - ev(cal["servico_longe_coef"], x)))


MARGEM_PES = 0.03    # ⚠️ AJUSTE MEU (declarado) — e MEDIDO a não fazer diferença:
                     #    de k=0,00 a k=0,10 → 0 dos 21 serviços mudam de fase.
                     #    ⛔ É uma FRAÇÃO DA ALTURA DA BOX, nunca píxeis (encolhe com a
                     #       perspetiva sozinho: ~4 px numa box de baixo, ~1 px numa de cima).


def pes(b):
    """F3 — a posição é a ARESTA INFERIOR da box (o contacto com o SOLO).
    Nunca a cabeça, o tronco, a raquete, nem um pé isolado.

    🦶 J16 (Vasco, 14 jul): "temos de dar uma margem em baixo — a bounding box termina
       LIGEIRAMENTE ABAIXO dos pés." A caixa TRANSBORDA. O contacto com o solo está um
       pouco ACIMA da aresta inferior.
       ⚠️ ISTO NÃO É UM LIMIAR EM CIMA DA LINHA (D19 continua intacta). A linha não se mexe.
          O que se corrige é ONDE ESTÃO OS PÉS — é a MEDIÇÃO, não a RÉGUA."""
    x1, y1, x2, y2 = b
    return (x1 + x2) / 2, y2 - MARGEM_PES * (y2 - y1)


def lado(b):
    """De que lado da REDE? (a base da rede, no x dele)"""
    x, y = pes(b)
    return "baixo" if y > y_base(x) else "cima"


# ---------------------------------------------------------------- 1 · J1 + J7 + J15
#   (o polígono `poli` é carregado em configurar() — a porta única por vídeo)
def j1_pes_no_poligono(pb):
    """🦶 Os pés NUNCA saem do polígono. O polígono INCLUI os espaços laterais
       (o jogo exterior é jogo LEGAL — foi por isto que morreu a regra "bola sai = fim").
       J7 — SALVAGUARDA: se a box toca a borda de BAIXO, os pés estão CORTADOS.
            Não sabemos ONDE está; sabemos que está EM BAIXO, e chega. ACEITA-SE."""
    out = []
    for fr in pb:
        keep = []
        for b in fr:
            if b[3] >= H - BORDA_BAIXO:      # J7 — pés cortados pela borda ⇒ imune
                keep.append(b)
            elif poli.contains_point(pes(b)):
                keep.append(b)
        out.append(keep)
    return out


# ---------------------------------------------------------------- 3 · J5
def j5_continuidade(pb):
    """🔗 A ÚNICA REGRA QUE ACRESCENTA INFORMAÇÃO.
       Visto no frame 100 e no 104 ⇒ INTERPOLA 101-103.
       ⚠️ NÃO é um filtro. Não descarta o frame. PREENCHE.
       "Se não os vês, temos de PERCEBER PORQUÊ não os vês." """
    pb = [list(f) for f in pb]
    n_add = 0
    for l in ("cima", "baixo"):
        vistos = [i for i, f in enumerate(pb) if any(lado(b) == l for b in f)]
        for a, c in zip(vistos, vistos[1:]):
            if not (1 < c - a <= GAP_INTERP):
                continue
            ba = [b for b in pb[a] if lado(b) == l][0]
            bc = [b for b in pb[c] if lado(b) == l][0]
            for f in range(a + 1, c):
                t = (f - a) / (c - a)
                pb[f].append(tuple(ba[k] + t * (bc[k] - ba[k]) for k in range(4)))
                n_add += 1
    return pb, n_add


# ---------------------------------------------------------------- 4 · J4  (O ÚLTIMO)
def j4_dois_por_lado(pb):
    """👥 NUNCA MAIS DE DOIS. E são sempre 2 CONTRA 2, por LADO da rede.
       É uma verdade do JOGO, não um limiar.
       ⚠️ O critério NÃO é a confiança (foi o erro do max_det=4) — é a GEOMETRIA (D10).
          Um jogador ocupa a ALTURA que a perspetiva manda no sítio onde está.
          Fico com os 2 cujo tamanho mais se aproxima do esperado NAQUELE ponto."""
    out = []
    for fr in pb:
        keep = []
        for l in ("cima", "baixo"):
            cand = [b for b in fr if lado(b) == l]
            if len(cand) > 2:
                # altura esperada ≈ 1,80 m ⇒ ~0,26 × meio-campo local (6,95 m)
                erro = lambda b: abs((b[3] - b[1]) - 0.26 * meio_campo_px(*pes(b)))
                cand = sorted(cand, key=erro)[:2]
            keep += cand
        out.append(keep)
    return out


# ---------------------------------------------------------------- o veredito
def conta(pb, nome):
    m = sum(len(f) for f in pb) / len(pb)
    q4 = sum(len(f) == 4 for f in pb) / len(pb) * 100
    c2 = sum(sum(lado(b) == "cima" for b in f) == 2 for f in pb) / len(pb) * 100
    print(f"  {nome:36} {m:5.2f} boxes/frame   4 jogadores: {q4:5.1f}%   "
          f"2 em cima: {c2:5.1f}%")
    return q4


def main():
    pb0 = pickle.load(open(BOXES, "rb"))["player_boxes"]
    print("=" * 92)
    print("👥 A CASCATA DOS JOGADORES — pela ORDEM do Vasco")
    print("=" * 92)
    print(f"  vídeo:   {VID.upper()}  ({H}p)\n  entrada: {BOXES.name}  ({len(pb0)} frames)\n")

    conta(pb0, "0 · CRU (nocap, generoso)")
    pb = j1_pes_no_poligono(pb0)
    conta(pb, "1 · J1+J7  pés no polígono")
    pb, n = j5_continuidade(pb)
    conta(pb, f"3 · J5     continuidade (+{n} boxes)")
    pb = j4_dois_por_lado(pb)
    q4 = conta(pb, "4 · J4     2 por lado  ← O ÚLTIMO")

    print("\n" + "=" * 92)
    print("🎯 O NÚMERO QUE MATOU A S2 E A S30 — medido outra vez, no sítio certo")
    print("=" * 92)
    print(f"  em TODOS os frames ................. {q4:.1f}%  têm os 4")
    print("  (o 21,8% que as matou era com max_det=4 — que ordena por CONFIANÇA)\n")

    ok = 0
    print("  NOS 13 MOMENTOS DO SERVIÇO — que é onde a regra PRECISA deles:")
    for i, t in enumerate(GT, 1):
        f = int(t * FPS)
        # a janela do serviço: 1 s à volta do início do ponto
        jan = range(max(0, f - 15), min(len(pb), f + 15))
        melhor = max((len(pb[k]) for k in jan), default=0)
        cima = max((sum(lado(b) == "cima" for b in pb[k]) for k in jan), default=0)
        bom = melhor >= 4
        ok += bom
        print(f"    ponto {i:2}  t={t:6.1f}s   melhor no frame: {melhor} jogadores "
              f"({cima} em cima)   {'✅' if bom else '🔴'}")
    print(f"\n  ⇒ {ok}/{len(GT)} serviços com os 4 jogadores visíveis   ({ok/len(GT)*100:.0f}%)")
    print("\n  🔑 A S2 (formação de serviço) e a S30 (inatividade) precisam dos 4")
    print("     NESTES 13 momentos — não em todos os frames do vídeo.")


if __name__ == "__main__":
    main()
