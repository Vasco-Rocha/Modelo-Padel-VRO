# PadelPro Vision — módulos de análise

Camada de análise que corre **por cima** do output do
[`padel_analytics`](https://github.com/Joao-M-Silva/padel_analytics) (do João Silva).
Não modifica esse repo: trata-o como um *extrator de features* que produz
deteções (posições dos jogadores, bola, pose) e consome esses dados aqui.

## Os 3 módulos

1. **Tempo útil** (`padelpro.modules.active_time`) — segmenta o jogo em rallies
   vs. pausas e calcula tempo efetivo, rácio jogo/pausa, duração de pontos.
2. **Fases de jogo** (`padelpro.modules.phases`) — classifica cada instante pela
   formação das duas duplas (rede / fundo / transição) a partir das posições.
3. **Pancadas e erros** (`padelpro.modules.shots`) — a partir das pancadas
   detetadas, classifica resultado (winner / erro forçado / não forçado) e
   produz estatísticas por jogador.

## Fluxo de dados

```
vídeo MATCHi TV
      │
      ▼
padel_analytics (repo do João)  ──►  CSV de jogadores + artefactos de bola/pose
      │                                         │
      └─────────────────────────────────────────┘
                          │
                          ▼
            padelpro.io.loader  →  GameData (tabela única por frame)
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  active_time          phases             shots
        └─────────────────┼─────────────────┘
                          ▼
                  padelpro.pipeline  →  MatchAnalysis (JSON/relatório)
```

## O que o `padel_analytics` produz (e o que este repo espera)

- **CSV principal** (`COLLECT_DATA_PATH` no `config.py` do João): uma linha por
  frame com `player{1..4}_x/y` em metros (já projetados pela homografia) e
  cinemática (`player{id}_Vnorm1`, etc.). É a entrada obrigatória.
- **Bola** (opcional): trajetória da bola por frame. O loader aceita um CSV/parquet
  com colunas `frame, ball_x, ball_y` e, se existir, `ball_hit`.
- **Pancadas** (opcional): pancadas detetadas/classificadas. CSV com
  `frame, player_id, stroke` (e opcionalmente `incoming_ball_speed`).

Os nomes das colunas são configuráveis em `config.example.yaml` — ajusta ao que
o teu pipeline gerar.

## Começar sem dados reais

Há um gerador sintético para testar os módulos sem GPU nem vídeo:

```bash
pip install -r requirements.txt
python examples/run_synthetic.py
pytest -q
```

## Com dados reais

```bash
python -m padelpro.cli analyze \
    --players data/jogo01_players.csv \
    --ball    data/jogo01_ball.csv \
    --shots   data/jogo01_shots.csv \
    --fps 30 \
    --out data/jogo01_analysis.json
```

## Auto-labeling com Gemini (treino do módulo de pancadas)

O Gemini **não** entra na inferência — entra a gerar dados de treino para o
classificador de resultado (winner / forçado / não-forçado). Fluxo:

```bash
# modo mock (offline, sem API key) — para testar o pipeline
python -m padelpro.cli label --players data.csv --shots shots.csv --mock --out labels.jsonl

# modo real (corta clips do vídeo e chama o Gemini)
python -m padelpro.cli label --players data.csv --shots shots.csv \
    --video jogo01.mp4 --api-key $GOOGLE_API_KEY --out labels.jsonl
```

Depois confirmas/corriges os labels e exportas o dataset de treino com
`padelpro.labeling.build_training_table`, que alimenta o classificador que vai
substituir a heurística em `padelpro/modules/shots.py:classify_outcome`.

## Estado

- Tempo útil e fases: regras calibráveis, funcionam já.
- Pancadas/erros: motor de regras (placeholder) pronto a substituir por um
  classificador treinado, alimentado pelo auto-labeling com Gemini.

> Nota de licença: confirmar os termos do `LICENSE` do `padel_analytics` antes de
> uso comercial. Este repo só consome o output, não redistribui código de lá.
