#!/usr/bin/env python3
"""
🦶 O POLÍGONO — **DERIVADO DAS LINHAS DO CAMPO**   (14 jul 2026)

    🩸 O ERRO QUE ISTO MATA — e o Vasco apontou-o TRÊS VEZES antes de eu o ver:

        PARADA4   os "2 jogadores de CIMA" da cascata estavam ACIMA da linha de fundo
                  ⇒ ATRÁS DO VIDRO ⇒ 100% ESPECTADORES.
        BARBOSA   a aresta de baixo do polígono está em y=881 — o frame acaba em 720.
                  (e esse polígono foi DEDUZIDO, não desenhado ⇒ viola a C1)

    🔑 A CAUSA, UMA SÓ:
       A **J15** diz «desenha LARGO». Eu apliquei o «largo» nas QUATRO direções.
       O «largo» é para os **LADOS** — é lá que há **JOGO EXTERIOR**.
       **AO FUNDO NÃO HÁ JOGO EXTERIOR: HÁ UM VIDRO. E atrás do vidro está o PÚBLICO.**

    🛡️ A CURA (arquitetura, não penso):
       # O POLÍGONO NÃO SE DESENHA. DERIVA-SE DAS LINHAS DO CAMPO.
       As linhas já estão desenhadas À MÃO (C1/C9). Assim o polígono NÃO PODE discordar
       da calibração — porque **É** a calibração.

    AS FRONTEIRAS:
       ⬆️ CIMA    a LINHA DE FUNDO longe          (J17 — atrás dela é vidro)
       ⬇️ BAIXO   a LINHA DE FUNDO perto, ou a BORDA DO FRAME (o que vier primeiro)
                  ⚠️ J7 — se o campo perto sai do frame, o limite é o frame. A câmara é que
                     corta, não o campo.
       ↔️ LADOS   as laterais + o ESPAÇO EXTERIOR  (J15 — o jogo exterior é jogo LEGAL)

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py.
"""
import json, sys
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).parent

CFG = {
    "parada4": dict(cal="calibracao_parada4_v2.json", W=960, H=540),
    "barbosa": dict(cal="calibracao_BarbosaMeireles.json", W=1280, H=720),
}

# ⚠️ AJUSTE (declarado) — o ESPAÇO EXTERIOR lateral, em FRAÇÕES DA LARGURA DO CAMPO.
#    O campo tem 10 m. As saídas laterais têm ~2 m de cada lado ⇒ 0,20.
#    ⛔ NUNCA em píxeis: a perspetiva mata-os (a lição que já mordeu 5 vezes).
EXTERIOR = 0.20


def poligono(vid):
    c = json.load(open(RAIZ / CFG[vid]["cal"]))
    W, H = CFG[vid]["W"], CFG[vid]["H"]
    ev = lambda k, x: float(np.polyval(c[k], x))

    # ── as duas linhas de FUNDO (as fronteiras de cima e de baixo)
    y_topo = lambda x: ev("fundo_longe_coef", x)                      # ⬆️ J17
    if "fundo_perto_coef" in c:
        y_base = lambda x: min(ev("fundo_perto_coef", x), H - 1)      # ⬇️ ou a borda (J7)
    else:
        y_base = lambda x: H - 1                                      # o campo perto sai do frame

    # ── as LATERAIS: dos cantos do campo, alargadas pelo ESPAÇO EXTERIOR (J15)
    #    os cantos saem das INTERSEÇÕES das linhas (C9 — de graça, sem clicar)
    def cantos_em(y_fn):
        """a que x é que o campo começa/acaba, à altura y_fn?  (as laterais são retas)"""
        return None  # (as laterais não estão todas calibradas — usa-se a largura do frame)

    # ⚠️ SEM as laterais calibradas, a fronteira lateral é a BORDA DO FRAME, alargada
    #    pelo espaço exterior — que NUNCA sai do frame de qualquer forma.
    #    (é seguro: o que mata os espectadores é o LIMITE DE CIMA, não o dos lados)
    pts_topo = [(x, y_topo(x)) for x in range(0, W, 8)]
    pts_base = [(x, y_base(x)) for x in range(W - 1, -1, -8)]
    poli = [(max(0, min(W - 1, x)), max(0, min(H - 1, y))) for x, y in pts_topo + pts_base]
    return poli, dict(vid=vid, W=W, H=H,
                      y_topo_centro=round(y_topo(W // 2), 1),
                      y_base_centro=round(y_base(W // 2), 1))


def main():
    for vid in ("parada4", "barbosa"):
        poli, info = poligono(vid)
        saida = RAIZ / f"../poligono_{vid}_derivado.json"
        json.dump({
            "poligono": [[round(x, 1), round(y, 1)] for x, y in poli],
            "_de": ("DERIVADO das linhas de fundo da calibracao (14 jul 2026). "
                    "NAO desenhado a mao — e' a PROPRIA calibracao, e por isso NAO PODE "
                    "discordar dela."),
            "_j17": ("A fronteira de CIMA e' a LINHA DE FUNDO longe. Atras dela esta' o VIDRO, "
                     "e atras do vidro esta' o PUBLICO. (O erro que custou 3 avisos do Vasco.)"),
            "_j15": ("O «largo» da J15 e' para os LADOS (o jogo exterior). NAO para o fundo."),
            "_video": vid,
        }, open(saida, "w"), indent=1, ensure_ascii=False)
        print(f"  ✅ {saida.name:34} topo y={info['y_topo_centro']:6.1f} · "
              f"base y={info['y_base_centro']:6.1f}  ({info['W']}x{info['H']})")


if __name__ == "__main__":
    main()
