# Handoff — Modelo-Padel-VRO (padelpro-vision)

Contexto para retomar o desenvolvimento (ex.: no Claude Code).

---
## ⚡ ESTADO ATUAL (11 jul 2026) — LER PRIMEIRO

**Detetor de bola: mudou.** O YOLO (`best.pt`, recall 67%) foi substituído pelo **BlurBall**
(detetor temporal, recall 85.6% out-of-box). Integração em `padelpro/modules/blurball_io.py`.
- ❌ **Via A (fine-tune do YOLO) FALHOU e está fechada** — `best_v2` ficou PIOR que o `best.pt`
  (recall 57%, precisão 39%). **Não repetir.**
- ✅ Ponto de operação validado: `PONTO_OPERACAO` em `blurball_io.py`
  (`vmin=6, gap_fora_s=1.0, serve_zone_y=None`) → **13 rallies, recall 99%**, 205s.
  (baseline YOLO: 10 rallies, recall 67%, 106s.) Ground-truth: **117s / 12 rallies**.

**O gargalo mudou de sítio:** já não é o detetor — é a **SEGMENTAÇÃO**. As regras v9 mediam
"jogo" pela *ausência de bola*, uma muleta do detetor fraco. Com um detetor forte a bola está
quase sempre visível (também entre pontos, onde é bola REAL) e a regra funde tudo.

**⚠️ ERRO A NÃO REPETIR — jogadores:** o `player_boxes` usado nas experiências veio de um
`yolov8n` improvisado dentro do notebook do BlurBall (só vê os 4 jogadores em **53%** dos frames).
**Foi um atalho errado.** A deteção de jogadores **é do `padel_analytics`** (João Silva) — já está
definida, validada, e faz **tracking**; este repo foi construído por cima dela. A objeção dos
"metros" é fraca: ele deteta em **píxeis** e só depois converte por homografia → ir buscar as boxes
em píxeis **antes** da conversão. **Não é treinar outro modelo — é ligar o que já existe.**
Isto destranca a regra da FORMAÇÃO (parceiro na rede + adversário cruzado), que dá **0 falsos**.

**➡ Falta a MONTAGEM ponta-a-ponta.** As peças estão no repo e provadas, mas o `pipeline.py`
ainda corre o fluxo antigo. Não há um "vídeo → tempo útil". Montar:
`vídeo → BlurBall (traj.csv) → limpar() → detetar_servicos() → rallies → clips/JSON`.
Tudo em **píxeis** (é onde vivem as regras: linhas do campo, ressalto, formação).

**➡ Próximo trabalho: implementar `docs/SPEC_M1_TEMPO_UTIL.md`** — serviço como fronteira do
ponto (bola na mão → ressalta aos pés → raquetada → servidor arranca), travessias alternadas da
rede como pancadas (inferidas, robusto a oclusão), e fins por rede/duplo-toque/6s.
**Falta uma calibração: o `y` da linha da rede** (um número, desbloqueia 3 regras).

**Diretriz de produto:** *nunca perder um ponto; mais lixo é preferível a menos tempo útil.*
Otimizar **recall**, não precisão.

Docs: `docs/SPEC_M1_TEMPO_UTIL.md` (o desenho), `docs/PLANO_TEMPO_UTIL_pos_BlurBall.md` (o plano),
`docs/REGRAS_CONSOLIDADAS_todos_prompts.md` (todas as regras v1→v9), `docs/ground_truth_parada4.md`.

---

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
