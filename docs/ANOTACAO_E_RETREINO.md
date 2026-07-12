# Via A — Anotar a bola + re-treinar o detetor (passo a passo)

Objetivo: subir o recall da bola dos ~72% anotando os frames onde ela se perde, e re-treinar.
Frames prontos: 637 nos buracos de deteção, na Drive em `PadelPro_Vision/anotacao_buracos/`
(nome = `gap{i}_f{frame}_t{segundos}s.jpg`). Prioridade: SERVIÇOS no primeiro plano + fundo perto do vidro + remates.

## PARTE 1 — Anotar (Roboflow, grátis)
1. Vai a **roboflow.com**, cria conta grátis, **Create New Project**:
   - Tipo: **Object Detection**
   - Classe única: **ball**
2. **Upload** dos 637 frames (arrasta a pasta `anotacao_buracos` ou o zip).
3. **Annotate**: em cada frame, desenha uma caixa pequena à volta da bola (ou usa o modo de clique).
   - Se **não vires a bola**, deixa o frame **sem anotação** (é informação útil — diz ao modelo "aqui não há bola clara").
   - Não precisas de fazer os 637 de uma vez. **100-150 bem anotados já ajudam muito.** Começa pelos de serviço/primeiro plano.
4. **Generate** um dataset version (sem augmentations pesadas para já).
5. **Export** em formato **YOLOv8** → copia o snippet de download (dá-te uma linha `!pip install roboflow` + código).

## PARTE 2 — Re-treinar (Colab, GPU)
1. Novo notebook (ou reaproveita o de treino da bola). Liga GPU (T4).
2. Descarrega o dataset novo (o snippet do Roboflow).
3. Continua o treino a partir do `last.pt` que já tens na Drive
   (`PadelPro_Vision/weights/ball_yolo/last.pt`), juntando os frames novos:
   ```python
   from ultralytics import YOLO
   m = YOLO('/content/drive/MyDrive/PadelPro_Vision/weights/ball_yolo/last.pt')
   m.train(data='data.yaml', epochs=30, imgsz=960, batch=8, resume=False)  # fine-tune
   ```
   (usa o `data.yaml` do Roboflow; junta os teus frames aos do PadelTracker100 se quiseres mais base.)
4. Guarda o `best.pt` novo na Drive (por cima ou com outro nome, ex. `best_v2.pt`).

## PARTE 3 — Validar (medir contra a verdade)
1. Re-corre o pipeline com o `best_v2.pt` (célula 2 do `colab_pipeline_tempo_util.ipynb`, muda o `BALL_PT`).
2. Guarda o `.pkl` novo das deteções.
3. Corre a segmentação e compara com o ground-truth:
   - Alvo: **117s / ~12 rallies** (o jogo real anotado).
   - Mede recall/precisão (script em `ground_truth_parada4.md`).
4. Se o recall subiu (menos "começa tarde", menos rallies partidos), o re-treino funcionou.
   Aí sim podes afinar `margem_fim_s`/`gap_max_s` como polimento, não como muleta.

## Ordem prática
- Frente 1 (Claude Code, em paralelo): commitar as regras novas + re-correr a heurística (penso rápido, ~110s).
- Frente 2 (tu, o salto real): anotar → re-treinar → validar. É esta que sobe o recall.

## Estado das regras (já no código, por commitar/rodar)
serve estrito, filtro fragmentos, min_gap_rallies_s (funde divisão falsa), rally-sem-pancada=falso,
zonas_cegas_y + gap_zona_cega_s (não corta se bola some em zona cega). Serviço = bola sai da box +
SERVIDOR sobe à rede (no padel a bola NÃO sobe — serviço por baixo).
Chamada: `segmentar_rallies_bola(..., gap_max_s=4.0, min_rally_s=1.5, margem_fim_s=2.5, min_gap_rallies_s=2.5, gap_zona_cega_s=7.0)`
