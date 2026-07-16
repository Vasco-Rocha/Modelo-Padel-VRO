#!/usr/bin/env python3
"""
🎾 O DETETOR DE SERVIÇO   —   14 jul 2026   (Vasco)

    ⚠️ QUATRO REGRAS DELE. ZERO BOLA.   É um GERADOR DE CANDIDATOS, não um veredito (D18).
    🔬 Cada regra é um INTERRUPTOR (REGRAS) — liga/desliga e mede uma a uma (a ablação, em baixo).
    ⛔ Os números CORREM-SE, não se decoram:  python3 detetor_servico.py [barbosa|parada4]

Nasceu de UMA pergunta dele, que INVERTEU o pipeline:

    "e se for ao contrário — testares o tempo útil PARTINDO DA S2, e confirmando com as
     restantes regras de serviço?"

    HOJE:  a BOLA gera os pontos  →  o serviço confirma
           ⚠️ e a bola está agarrada a roupa branca (B19) — 830 teletransportes medidos

    ELE:   a FORMAÇÃO gera os candidatos  →  as outras regras confirmam
           ✅ e os jogadores estão CERTOS (medido, 14 jul)

────────────────────────────────────────────────────────────────────────────────────────
A CASCATA — quatro regras, todas dele, nenhuma delas correu alguma vez:

  ⓵ S2  · A FORMAÇÃO DIZ QUEM SERVE            gerador       46 blocos · recall 21/21
        "no momento do serviço SÓ PODE ESTAR UM JOGADOR ADIANTADO"
        ⚠️ ADIANTADO = SAIU DA DEFESA (transição OU rede).
           Exigir «rede» dá 11/21 — o parceiro está em TRANSIÇÃO em metade dos serviços.
           (ele já o tinha dito: "no máximo perto da zona de transição")

  ⓶ F5  · O ADIANTADO TEM DE SER ESTÁVEL       anti-jitter   ~1,2 s
        "se a box só TOCA, TREME ou OSCILA em cima da marca, NÃO abras entrada"
        🔑 lá em cima a faixa de transição tem 12 PÍXEIS — a perspetiva esmaga-a.
           Um tremor de 5 px atravessa-a. A tolerância vive no TEMPO, nunca no ESPAÇO (D19).
        ⚠️ PLANALTO medido: 1,0 → 1,6 s dão o mesmo. Não é um número mágico.

  ⓷ S2b · DEPOIS DO SERVIÇO, O SERVIDOR CORRE   confirmação   matou 20 · perdeu 0
        "depois do serviço, o servidor corre para transição/rede"   (Vasco, 14 jul)

  ⓸ S30 · A FORMAÇÃO ESTÁ PARADA                confirmação   matou 3 · perdeu 0
        "TODOS visíveis + ~3 s parados"   ⚠️ medido DENTRO da formação, não antes dela
        (antes, eles ainda estão a CAMINHAR para a posição — foi o meu 1.º erro)
        4× de separação: 0,088 (antes do serviço) vs 0,353 (a meio de um rally)

────────────────────────────────────────────────────────────────────────────────────────
⚠️ E A BOLA? — NÃO ENTRA. Ainda não pode.
   A S23-sequência (ver `s23_sequencia.py`) é a LEI CERTA — mas o sinal está em 817 pedaços,
   com 830 saltos ATRAVÉS DA REDE. Testado: a "confirmação" da bola era 88 % ACASO.
   🔑 Quando o sinal limpar, ela SOMA (D16). NUNCA VETA (D18).

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py.
   ⛔ E ainda NÃO ESTÁ NO PIPELINE — «corre» ≠ «corre no PIPELINE».
"""
import pickle, statistics as st, sys

import cascata_jogadores as C
import fases_m2 as M

FPS = C.FPS

# ---------- os AJUSTES, todos declarados (as LEIS são dele) ----------
F5_ESTAVEL = 1.2   # ⚠️ AJUSTE — segundos. PLANALTO medido: 1,0–1,6 dão o mesmo.
DUR_MIN    = 0.3   # ⚠️ AJUSTE — segundos. duração mínima do bloco de formação.
CORRE_SEG  = 2.0   # ⚠️ AJUSTE — segundos. janela para o servidor arrancar.
PARADO     = 0.20  # ⚠️ AJUSTE — meios-campos/s. medido: 0,088 (serviço) vs 0,353 (rally).
GAP        = 5     # ⚠️ AJUSTE — frames. buraco tolerado dentro de um bloco.

# ---------- OS INTERRUPTORES — uma regra de cada vez (para testar regra a regra) ----------
#    ⚠️ Cada chave é uma REGRA DELE. Desliga UMA, corre, vê o que se perde/ganha.
#    (é o mesmo espírito da ablacao.py: uma regra que vale +0,0 ou ficou redundante ou NÃO CORRE)
REGRAS = {
    "S2_nivel2":  True,   # ② S2 — deduzir com só os 2 de cima (câmara baixa). Sem isto: só leitura direta dos 4.
    "F5_estavel": True,   # ⓶ F5 — a formação tem de ser ESTÁVEL no tempo (anti-jitter, D19).
    "S2b_corre":  True,   # ⓷ S2b — depois do serviço, o SERVIDOR CORRE para transição/rede.
    "S30_parados": True,  # ⓸ S30 — a formação está PARADA (medido DENTRO do bloco).
}


def cascata(video):
    """A cascata dos jogadores J1→J5, pela ORDEM dele.
    🩸 FIX (15 jul): CONFIGURA a régua/polígono/boxes para ESTE vídeo. Antes ignorava o
       argumento e usava o do último import (default parada4) — o bug dos 23→16 serviços."""
    global FPS
    C.configurar(video)          # ⬅️ a porta única: boxes + calibração + polígono, do MESMO vídeo
    FPS = C.FPS
    pb0 = pickle.load(open(C.BOXES, "rb"))["player_boxes"]
    return C.j4_dois_por_lado(C.j5_continuidade(C.j1_pes_no_poligono(pb0))[0])


def adiantado(b):
    """⚠️ A FRONTEIRA É «SAIR DA DEFESA», não «a rede». (medido: exigir rede ⇒ 11/21)"""
    return M.fase_do_jogador(b) != "DEFESA"


def leitura(fr, regras=None):
    """⚖️ A S2, COM OS DOIS NÍVEIS.  Devolve o LADO que serve, ou None.

    ① VEJO OS 4          ⇒ leitura DIRETA: exatamente UM adiantado ⇒ é o parceiro do servidor
    ② SÓ VEJO OS 2 DE CIMA ⇒ DEDUZO:
         · os dois de cima ATRÁS   ⇒ eles RECEBEM  ⇒ serve BAIXO
         · um deles ADIANTADO      ⇒ eles SERVEM   ⇒ serve CIMA
      🔑 «o nível ② NÃO é um plano B: com a câmara baixa é a ÚNICA leitura possível»
         (a decisão do Vasco, 12 jul — marcada ✅ e nunca correu)
    """
    regras = regras if regras is not None else REGRAS
    cima = [b for b in fr if C.lado(b) == "cima"]
    baixo = [b for b in fr if C.lado(b) == "baixo"]

    # ── ① os 4 estão à vista
    if len(cima) == 2 and len(baixo) == 2:
        adi = [b for b in fr if adiantado(b)]
        return C.lado(adi[0]) if len(adi) == 1 else None

    # ── ② só vejo os 2 de CIMA  (a câmara não vê os de baixo — J8: a AUSÊNCIA é o sinal)
    if regras["S2_nivel2"] and len(cima) == 2:
        n = sum(adiantado(b) for b in cima)
        if n == 0:
            return "baixo"      # os dois atrás ⇒ RECEBEM ⇒ o serviço vem de baixo
        if n == 1:
            return "cima"       # um adiantado  ⇒ SERVEM
    return None                 # 🚫 D2/D4 — não vejo os 2 de cima ⇒ NÃO INVENTO


def blocos_de_formacao(pb, regras=None):
    """⓵ S2 (os dois níveis) + ⓶ F5 — a formação, e tem de ser ESTÁVEL."""
    regras = regras if regras is not None else REGRAS
    L = [leitura(fr, regras) for fr in pb]
    if regras["F5_estavel"]:
        w = int(F5_ESTAVEL * FPS)
        # 🧊 F5 — só conta se TODOS os frames da janela disserem O MESMO LADO
        #    (não «toca, treme, oscila»: a tolerância vive no TEMPO — D19)
        ok = [1 if (j := L[max(0, i - w // 2): i + w // 2 + 1]) and j[0] is not None
              and all(v == j[0] for v in j) else 0
              for i in range(len(pb))]
    else:
        ok = [1 if L[i] is not None else 0 for i in range(len(pb))]
    lado = [L[i] if ok[i] else None for i in range(len(pb))]
    bl, ini, fim = [], None, None
    for i, m in enumerate(ok):
        if m:
            if ini is None:
                ini = i
            fim = i
        elif ini is not None and i - fim > GAP:
            bl.append((ini, fim)); ini = None
    if ini is not None:
        bl.append((ini, fim))
    return [(a, b) for a, b in bl if (b - a) / FPS >= DUR_MIN], lado


def servidor(fr, l):
    """O SERVIDOR = o jogador ATRASADO da equipa que serve (o parceiro é o adiantado)."""
    eq = [b for b in fr if C.lado(b) == l]
    return max(eq, key=lambda b: abs(C.pes(b)[1] - C.y_base(C.pes(b)[0]))) if eq else None


def o_servidor_corre(pb, a, b, l):
    """⓷ «depois do serviço, o SERVIDOR CORRE para transição/rede» (Vasco, 14 jul)."""
    return any((s := servidor(pb[f], l)) and adiantado(s)
               for f in range(b, min(len(pb), b + int(CORRE_SEG * FPS))))


def velocidade(pb, f, cache={}):
    """meios-campos por segundo. ⛔ NUNCA píxeis (não sobrevivem à perspetiva)."""
    if f in cache:
        return cache[f]
    A, B = pb[f], pb[f + 1]
    r = None
    if len(A) >= 2 and len(B) >= 2:
        vs = []
        for p in A:                     # ⚠️ emparelhar pelo MAIS PRÓXIMO, não pela ordem de y
            x, y = C.pes(p)             #    (ordenar por y troca identidades e dispara a velocidade)
            q = min(B, key=lambda z: (C.pes(z)[0] - x) ** 2 + (C.pes(z)[1] - y) ** 2)
            x2, y2 = C.pes(q)
            vs.append(((x2 - x) ** 2 + (y2 - y) ** 2) ** .5 / C.meio_campo_px(x, y) * FPS)
        r = st.median(vs)
    cache[f] = r
    return r


def estao_parados(pb, a, b):
    """⓸ S30 — o meio-segundo mais CALMO **DENTRO** da formação.
    ⚠️ NÃO antes dela: antes, eles ainda estão a CAMINHAR para a posição."""
    vs = [v for f in range(a, b) if (v := velocidade(pb, f)) is not None]
    if not vs:
        return False
    w = max(3, int(0.5 * FPS))
    return min(st.median(vs[i:i + w]) for i in range(0, max(1, len(vs) - w + 1))) < PARADO


def servicos(video, regras=None, pb=None):
    """Devolve [(frame_inicio, frame_fim, lado_que_serve)] — os CANDIDATOS a serviço.
    ⚠️ CANDIDATOS, não veredito (D18). Cada regra é um interruptor (REGRAS) — testa-se uma a uma.
    ⚡ passa-se `pb` já calculado para não recorrer a cascata a cada ablação."""
    regras = regras if regras is not None else REGRAS
    if pb is None:
        pb = cascata(video)
    else:
        C.configurar(video)      # 🩸 mesmo com pb já feito, a régua TEM de ser deste vídeo
        global FPS; FPS = C.FPS
    bl, lado = blocos_de_formacao(pb, regras)
    out = []
    for a, b in bl:
        l = lado[b] or lado[a]
        if not l:
            continue
        if regras["S2b_corre"] and not o_servidor_corre(pb, a, b, l):
            continue
        if regras["S30_parados"] and not estao_parados(pb, a, b):
            continue
        out.append((a, b, l))
    return out, pb


def avaliar(S, GT):
    """recall (quantos GT tocados) e extras (candidatos que não tocam GT nenhum)."""
    us = set()
    for t in GT:
        fa, fb = int((t - 3) * FPS), int((t + 0.5) * FPS)
        h = next((j for j, (a, b, _) in enumerate(S) if not (b < fa or a > fb)), None)
        if h is not None:
            us.add(h)
    return len(us), len(S) - len(us)


def main():
    vid = sys.argv[1] if len(sys.argv) > 1 else "barbosa"
    GT = {"barbosa": [13.6,33.9,40.3,54.5,69.8,83.3,135.0,155.0,162.9,188.3,196.0,227.2,
                      242.3,257.1,298.3,326.1,352.1,367.9,377.9,406.8,526.0],
          "parada4": [38.0,46.8,77.6,95.9,122.4,157.9,178.1,197.0,210.5,229.9,249.6,263.8,
                      289.1]}[vid]
    pb = cascata(vid)                       # ⚡ a cascata é o pesado — corre-se UMA vez

    # ── config completa: o detalhe candidato a candidato
    S, _ = servicos(vid, REGRAS, pb)
    print("=" * 74)
    print(f"🎾 O DETETOR DE SERVIÇO — {vid.upper()}   (candidatos · ZERO bola)")
    print("=" * 74)
    print(f"   candidatos: {len(S)}   ·   serviços reais (GT): {len(GT)}\n")
    us = set()
    for i, t in enumerate(GT, 1):
        fa, fb = int((t - 3) * FPS), int((t + 0.5) * FPS)
        h = next((j for j, (a, b, _) in enumerate(S) if not (b < fa or a > fb)), None)
        if h is not None:
            us.add(h)
        print(f"   {i:2}  t={t:6.1f}s   " +
              (f"✅  serve {S[h][2].upper():5}  (bloco {S[h][0]/FPS:.1f}s)" if h is not None
               else "🔴  PERDIDO"))
    ex = len(S) - len(us)
    print(f"\n   📈 RECALL:  {len(us)}/{len(GT)}  ({len(us)/len(GT)*100:.0f}%)")
    print(f"   🎯 EXTRAS:  {ex}   {'✅ ZERO FALSOS' if ex == 0 else '⚠️ (o intervalo tem a MESMA formação)'}")

    # ── ABLAÇÃO — cada interruptor desligado, um de cada vez (regra #10)
    print("\n" + "-" * 74)
    print("🔬 ABLAÇÃO — cada regra DESLIGADA, uma de cada vez")
    print("   (Δrecall alto = a regra segura pontos · Δextras baixo = a regra limpa lixo)")
    print("-" * 74)
    br, be = avaliar(S, GT)
    print(f"   {'TODAS ligadas':22}  recall {br:2}/{len(GT)}   extras {be}")
    for k in REGRAS:
        r = dict(REGRAS); r[k] = False
        Sk, _ = servicos(vid, r, pb)
        rr, ee = avaliar(Sk, GT)
        print(f"   {('sem ' + k):22}  recall {rr:2}/{len(GT)}   extras {ee}"
              f"   Δrecall {rr-br:+d}  Δextras {ee-be:+d}")
    print("\n   ⚠️ CANDIDATO. NÃO está no pipeline. «corre» ≠ «corre no PIPELINE».")


if __name__ == "__main__":
    main()
