#!/usr/bin/env python3
"""
🔒 TESTE DE REGRESSÃO — TRAVA O ESTADO DE 12 JUL 2026.

    python3 teste_regressao.py

Corre em segundos, em CPU.

PORQUÊ ISTO EXISTE
------------------
O Vasco perguntou: *"porque é que algumas regras vão perdendo firmeza ao longo do dia?"*
A resposta honesta: porque eu re-afinava os limiares a cada regra nova, sem verificar se o que
já funcionava continuava a funcionar. **Não havia testes.** Uma regra firme às 15h aparecia
amolecida às 19h — não era a regra que enfraquecia, era eu a mexer-lhe por baixo.

E depois: *"NÃO INVENTAR NEM ATALHAR NADA DO QUE FOI FEITO ATÉ AGORA."*

Este ficheiro é a garantia. **Se alguém partir o que está feito, ISTO FALHA.**

REGRA DE USO
------------
- Correr ANTES e DEPOIS de qualquer alteração ao `gerar_tempo_util.py`.
- Se falhar, a alteração está errada — a não ser que o Vasco tenha decidido o contrário,
  EXPLICITAMENTE. Nesse caso, e só nesse caso, atualizam-se os valores travados aqui,
  com uma linha a dizer porquê.
- **Nenhum valor aqui se muda para "fazer o teste passar".**

ESTADO TRAVADO (12 jul 2026, com a bola a thr=0.4)
"""
import sys
sys.path.insert(0, ".")
from gerar_tempo_util import (carregar, vai_e_vem, tracklets, cruzamentos,
                              pancadas, rallies, avaliar)

# ---------------------------------------------------------------------------
#  OS NÚMEROS. Não se mexem sem o Vasco dizer.
# ---------------------------------------------------------------------------
TRAVADO = {
    "recall":    (93.2, 0.5),    # (valor, tolerância)
    "precisao":  (89.4, 0.5),
    "servicos":  (12,   0),      # 12/12. NUNCA menos.
    "n_pontos":  (15,   1),      # reais: 12
    "pancadas":  (135,  5),      # a 0.7 eram 57. O 0.4 foi buscá-las.
}

# As REGRAS que produzem estes números. Cada uma já valeu pontos, medidos.
# (Se uma destas desaparecer do pipeline, os números caem e o teste falha.)
REGRAS_VIVAS = """
  B8/vai-e-vem      A->B longe, A->C perto => B e' ERRO. Tira o frame, nao parte a cadeia. (+6 precisao)
  Theta/costura     Direcao a 2 graus, numa UNICA detecao => os buracos deixam de partir.  (+10 recall)
  cruzamento fundo  De fundo a fundo. Rocar a fita NAO conta (e' onde o ruido oscila).
  S15 mao/raquete   L: servico 17,4 · passagem a mao 2,7. So dispara se veio da RAQUETE.  (+18 precisao)
  S16 duvida        HA pancada -> corte rente (2s). NAO ha -> duvida -> mais margem (5s).  (+9 precisao)
                    ⚠️ NUNCA INVERTER. Ja esteve invertido e cortava os pontos 12/13/14 a meio.
  S13 timeline      Nunca anda para tras. Segmentos que se tocam SAO O MESMO PONTO.
  thr=0.4           A bola nos 2,5s do servico: 60% -> 85%. Pancadas: 57 -> 135.
"""


def main():
    print(__doc__)
    print("REGRAS QUE TEM DE ESTAR VIVAS:")
    print(REGRAS_VIVAS)

    R, prof = carregar()
    R = vai_e_vem(R)
    tks = tracklets(R)
    CR = cruzamentos(R, tks, prof)
    PAN = pancadas(R)
    M = rallies(CR, PAN)
    r = avaliar(M)
    r["pancadas"] = len(PAN)
    r["n_pontos"] = r["n"]

    print("-" * 62)
    print(f"{'metrica':<12} {'travado':>9} {'agora':>9}   estado")
    print("-" * 62)
    falhou = []
    for k, (esperado, tol) in TRAVADO.items():
        v = r[k]
        ok = abs(v - esperado) <= tol
        if not ok:
            falhou.append((k, esperado, v))
        print(f"{k:<12} {esperado:>9} {v:>9.1f}   {'OK' if ok else '<<< PARTIU'}")
    print("-" * 62)

    if falhou:
        print("\n❌ REGRESSAO. Alguma coisa se perdeu:\n")
        for k, e, v in falhou:
            print(f"   {k}: era {e}, esta {v:.1f}")
        print("\n   Nao alterar os valores travados para o teste passar.")
        print("   Encontrar o que se partiu. E se foi decisao do Vasco, escrever PORQUE.")
        sys.exit(1)

    print("\n✅ Tudo no sitio. Nada se perdeu.")


if __name__ == "__main__":
    main()
