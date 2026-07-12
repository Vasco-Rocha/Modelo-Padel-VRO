# M1 — Tempo útil · estado travado (13 jul 2026)

**RECALL 96,2% · PRECISÃO 91,8% · F1 93,9 · 12/12 serviços · 13 segmentos (12 reais + 1 falso)**
De manhã (12 jul) estava em 72/63. Corre tudo em **CPU, em segundos**.

```bash
python3 teste_regressao.py     # 🔒 trava o estado. Correr ANTES e DEPOIS de mexer.
python3 gerar_tempo_util.py    # as métricas
python3 ablacao.py             # quanto vale CADA regra, medido
python3 diag_pontos.py         # onde é que cada ponto perde
python3 diag_fim.py            # S17/S18: os fins certos, e onde caem
```

## O que entrou hoje (TUDO regras do Vasco)

| regra | ganho |
|---|---|
| **S12 à letra** — o fim segue a **última PANCADA**, não o último cruzamento | recall 93,2 → **97,0**, pontos partidos 2 → **0** |
| **S17 REDE** 🔒 — *"muda de direção (ou pára) na rede, LONGE de uma box → acabou"* | **+4,1 precisão**. Pontos 2, 3, 5, 10 acabam **ao segundo**. |
| **S18 MÃO** — *"bola PARADA na box, SEM MUDAR DE CAMPO → acabou"* | 0 cortes a meio. Segura. |
| **PAN_TEM_JOGADOR** — uma raquetada TEM de ter um jogador ao pé | **+0,5 precisão** (mata pancadas-fantasma no público) |
| **B2 / VMAX derivado** — 180 km/h (lei do Vasco) ⇒ 70 px/frame | corrige o atalho (era 90, = **710 km/h** ao fundo) |

## 🔒 O que NÃO se mexe
- **S17 (rede)** — *"está perfeita! fixa e não deixes mudar."* (Vasco). `RED_DTHETA`/`RED_L_PARA`/`RED_DIST`.
- **`fim_dentro` = 0** — nenhum "fim certo" pode cair **a meio** de um ponto real. Se subir:
  **DESLIGAR a regra, nunca relaxar o teste.**
- **S18 duração 0,5 s** — a 0,3 s corta pontos a meio e o recall cai para **82**.
- Os valores travados no `teste_regressao.py` **só** se mudam com decisão **explícita** do Vasco,
  **com a razão escrita ao lado**.

## ⛔ VIAS FECHADAS (medidas hoje — não repetir)
| | porquê |
|---|---|
| **S8** — fim = última pancada antes do serviço seguinte | 98,9/**47,1**. Sem detetor de serviço, as pancadas do INTERVALO esticam cada ponto até ao seguinte. |
| **S18_MAO_PASSE** — mão→adversário sem ser serviço | só **2 dos 12** serviços se leem como "cruzados" na rede. **Vetava 10 dos 12 pontos.** |
| **S19_2_TOQUES** — 2 toques sem mudar de campo | **12 dos 14** eventos a meio de pontos reais. A **PAREDE** confunde-se com a raquete. |
| **VIDRO DO FUNDO** | a zona acima da linha de fundo **é o CÉU**, não o vidro. Tira jogo (96,2 → 92,8). ⚠️ **E não se resolve DESENHANDO** — os eventos bons e maus têm a **mesma** distribuição de alturas. Falta **profundidade**. |
| **régua local aplicada à BOLA** | **A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96,2 → **32,1**. Vale para pés e ressaltos; não para a bola em voo. |

## 🚪 O BLOQUEIO ÚNICO: o RESSALTO
As **4** regras acima pararam **todas na mesma porta**: não sei distinguir **RAQUETE / PAREDE / CHÃO**.
O ressalto destranca a S8, S9, S10, S14, e as duas regras do Vasco de hoje.

## A lição do dia
**S12 e S8 estavam marcadas ✅ no `MAPA_DAS_REGRAS.md` e NÃO CORRIAM.**
A S12 estava lá **com o nome certo a fazer outra coisa** — pior do que estar desligada, porque
ninguém a vai procurar. **Ao retomar: não confiar no mapa. LER O CÓDIGO.**

> **Faixa fina = observável. Área grande = ambígua.**
> A rede (35 px) funciona; o vidro (meio ecrã) não. Serve para prever se uma ideia tem hipótese.
