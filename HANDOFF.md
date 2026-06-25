# Handoff — Modelo-Padel-VRO (padelpro-vision)

Contexto para retomar o desenvolvimento (ex.: no Claude Code).

## O que é
Camada de análise de padel que corre **por cima** do output do repo
[`padel_analytics`](https://github.com/Joao-M-Silva/padel_analytics) (do João Silva).
Não modifica esse repo: consome o `data.csv` (posições dos jogadores em metros +
cinemática) e artefactos de bola/pose que ele gera.

## 3 módulos (objetivo do projeto)
1. **Tempo útil** — rallies vs. pausas (regra: bola parada/fora >2s fecha o rally).
2. **Fases de jogo** — formação das duas duplas (rede / fundo / transição) por posições.
3. **Pancadas e erros** — winner / erro forçado / não forçado por cima das pancadas detetadas.

## Estrutura
- `padelpro/io/` — `loader.py` (lê CSV do padel_analytics → GameData), `synthetic.py` (dados fake p/ testar sem GPU).
- `padelpro/core/` — `schema.py` (dataclasses), `court.py` (geometria/zonas).
- `padelpro/modules/` — `active_time.py`, `phases.py`, `shots.py` (heurística em `classify_outcome`).
- `padelpro/labeling/` — auto-labeling Gemini: `clips.py` (recorta pancadas + features), `prompt.py`
  (enums fechados, JSON estrito), `gemini.py` (real ou mock), `store.py` (JSONL), `dataset.py`
  (`build_training_table`), `run.py`.
- `padelpro/pipeline.py`, `padelpro/cli.py` (`analyze`, `label`).
- `colab/colab_padel_analytics.ipynb` — gera o `data.csv` numa GPU do Colab.
- `tests/` — 9 testes (passam todos). CI em `.github/workflows/tests.yml`.

## Estado
- Repo com commit inicial em `main`. Remote: `https://github.com/Vasco-Rocha/Modelo-Padel-VRO.git`.
- Tempo útil e fases: funcionam (regras calibráveis).
- Pancadas: heurística placeholder, **a substituir** por classificador treinado.
- Gemini = auto-labeler (gera dados de treino), NÃO entra na inferência.

## Tarefa imediata
`git push -u origin main` para o remote acima (auth via `gh auth login`).

## Próxima tarefa
Treinar o classificador de pancadas: `build_training_table` (labels confirmados) →
modelo (ex.: sklearn) → ligar em `padelpro/modules/shots.py:classify_outcome`.

## Notas
- Macs (Apple Silicon) não correm o `padel_analytics` (sem CUDA) → essa parte é Colab/cloud.
- Confirmar `LICENSE` do `padel_analytics` antes de uso comercial.
- Correr testes: `pip install -r requirements.txt && pytest -q`.
- Demo offline: `python examples/run_synthetic.py`.
