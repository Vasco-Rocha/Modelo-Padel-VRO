"""
M3 — DETEÇÃO DE SERVIÇO.   12 jul 2026.   RECALL 11/12 (92%), 27 falsos.

A IDEIA (do Vasco):
  A bola do INTERVALO é bola a sério — 45% das deteções caem fora dos rallies.
  Nenhum detetor a distingue. O que a distingue é o COMPORTAMENTO:

      a bola do intervalo NAO faz trajetorias longas e NAO atravessa o campo.

  O serviço é o primeiro cruzamento COERENTE da rede depois de um silêncio.

CASCATA:
  1. TRACKLETS   — ligar deteções em trajetórias contínuas (a regra da coerência do Vasco,
                   generalizada: "confirmar com um antes e um pós"). Mata o ténis branco,
                   o público, e os saltos entre objetos diferentes.
  2. CRUZAMENTO  — a bola vai de um lado PROFUNDO ao outro lado PROFUNDO (prof>0.35).
                   Roçar a fita da rede não conta: no intervalo a bola oscila ali e engana.
  3. SILÊNCIO    — serviço = 1º cruzamento após >=2,5 s sem nenhum.

A FORMAÇÃO NÃO ENTRA COMO FILTRO. Testado: exigi-la faz o recall cair de 11/12 para 7/12.
Serve para PONTUAR confiança, não para cortar.  (`confianca_formacao()`)

Tolerâncias: todas em FRAÇÕES do meio-campo local. Nada em píxeis absolutos.
"""
import math
import numpy as np

FPS_DEF = 29.97


class CampoM3:
    def __init__(self, cal):
        ev = lambda c, t: float(np.polyval(c, t))
        k = "rede_topo_coef" if "rede_topo_coef" in cal else "rede_tape_coef"
        self.y_rede = lambda x: ev(cal[k], x)
        self.y_sp   = lambda x: ev(cal["servico_perto_coef"], x)
        self.y_sl   = lambda x: ev(cal["servico_longe_coef"], x)
        self.y_fu   = lambda x: ev(cal["fundo_longe_coef"], x)
        self.H = cal.get("resolucao", [960, 540])[1]

    def prof(self, x, y):
        """0 = na rede · 1 = na linha de serviço · >1 = atrás dela."""
        yr = self.y_rede(x)
        if y > yr:
            return "baixo", (y - yr) / max(self.y_sp(x) - yr, 1)
        return "cima", (yr - y) / max(yr - self.y_sl(x), 1)

    def prof_box(self, b):
        x, y = (b[0] + b[2]) / 2, b[3]
        if y >= self.H - 2:          # pés cortados pela borda => fundo perto
            return "baixo", 1.6
        return self.prof(x, y)

    def dentro(self, b, margem=6):
        x, y = (b[0] + b[2]) / 2, b[3]
        if y >= self.H - 2:
            return True
        return y >= self.y_fu(x) - margem and 40 < x < 930


def tracklets(bola, vmax=90, gap_max=9, min_det=4):
    """Liga as deteções em trajetórias contínuas.  bola: {frame: (x, y)}"""
    fs = sorted(bola)
    if not fs:
        return []
    out, cur = [], [fs[0]]
    for a, b in zip(fs, fs[1:]):
        g = b - a
        d = math.hypot(bola[b][0] - bola[a][0], bola[b][1] - bola[a][1])
        if g <= gap_max and d <= vmax * g:
            cur.append(b)
        else:
            out.append(cur); cur = [b]
    out.append(cur)
    return [t for t in out if len(t) >= min_det]


def cruzamentos(bola, campo, min_prof=0.35, vmax=90, gap_max=9, min_det=4):
    """Frames em que a bola atravessa a rede DE FUNDO A FUNDO, dentro de um tracklet."""
    cr = []
    for tk in tracklets(bola, vmax, gap_max, min_det):
        ult = None
        for f in tk:
            x, y = bola[f]
            lado, p = campo.prof(x, y)
            if p < min_prof:          # perto da rede: ignora (é onde o ruído oscila)
                continue
            if ult and ult != lado:
                cr.append(f)
            ult = lado
    return sorted(cr)


def servicos(bola, campo, fps=FPS_DEF, silencio=2.5, **kw):
    """SERVIÇO = 1º cruzamento coerente após `silencio` segundos sem nenhum."""
    cr = cruzamentos(bola, campo, **kw)
    out, ult = [], -10 ** 9
    for c in cr:
        if c - ult > silencio * fps:
            out.append(c)
        ult = c
    return out


def confianca_formacao(f, player_boxes, campo, fps=FPS_DEF, janela=2.0):
    """
    NÃO é um filtro — é confiança. Os 2 recetores de cima estão AMBOS atrás da linha
    de serviço (o mais fundo > 1.00)? Medido: no serviço 1,05/1,06/1,07;
    em jogo aberto 0,61/0,69/0,86 (subiram à rede).

    Só 28% dos frames de serviço têm as 2 boxes de cima válidas -> por isso NÃO se exige.
    """
    j0 = max(0, f - int(janela * fps))
    n = 0
    for k in range(j0, min(f + 1, len(player_boxes))):
        C = sorted(p for l, p in (campo.prof_box(b) for b in player_boxes[k]
                                  if campo.dentro(b)) if l == "cima")
        if len(C) >= 2 and C[-1] > 1.00:
            n += 1
    return n / max(f - j0, 1)


# ---------------------------------------------------------------------------
# POR FAZER
#   - Limpar os 27 falsos. NÃO com a formação (corta recall de 11/12 -> 7/12).
#     Via: o DUPLO RESSALTO (regra do Vasco) -- o serviço é a única jogada em que a bola
#     ressalta obrigatoriamente dos DOIS lados da rede. Ancorar no ressalto DE CIMA:
#     os dois ressaltos estão em lados opostos, logo um está sempre no lado que a câmara vê.
#     O detetor de ressalto NÃO pode exigir frames seguidos (no serviço o jogador tapa a bola).
#   - Confirmação: o servidor SOBE à rede nos 2 s seguintes.
# ---------------------------------------------------------------------------
