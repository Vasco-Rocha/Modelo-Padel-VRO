# CONTEXTO DO PROJETO — Modelo de Análise de Padel (handoff)

> Documento para arrancar uma conversa nova dentro deste projeto. Resume o
> estado, as decisões e os ficheiros. Lê isto primeiro.

## 1. O que é o projeto
Análise automática de jogos de padel por visão computacional (projeto **PadelPro
Vision**, repo `github.com/joaoms17/Padelpro`). Câmara FRONTAL, fixa, atrás do
vidro de fundo. Objetivo: extrair rallies, confrontos táticos por fase e pancadas,
em JSON, para análise e geração de clips.

Duas vias que coexistem:
- **Prompt (Gemini):** rápido, sem dados, mas inconsistente — usado para arrancar e como auto-labeler.
- **Modelo + geometria (PadelPro):** determinístico, preciso, barato — o destino a prazo.

## 2. Os 3 módulos (pipeline em cadeia)
1. **Batedor** — vídeo COMPLETO → lista de rallies (início/fim). Depois cortam-se clips de 1 rally.
2. **Estratega** — 1 clip de rally → micro-clips de confronto por fase (A vs B).
3. **Técnico** — 1 clip de rally → pancadas (tipo, contexto, resultado) de uma equipa.

Fluxo: jogo completo → Prompt 1 → tempos → cortar em clips de 1 rally → Prompt 2 e 3 por clip.

## 3. Regras-chave da v9 (decisões fechadas)
- **Fase por DUAS boxes:** posição = aresta inferior da bounding box. DEFESA = ambos atrás da linha de serviço; ATAQUE = ambos à frente da interceção malha 3/2; TRANSIÇÃO = tudo o resto (estado-resíduo).
- **Nomenclatura:** "linha de serviço" e "interceção malha 3 / malha 2" (substituiu "junção Parede/VL1").
- **Módulo 2:** corta clip a cada mudança de fase de qualquer equipa (conta por transições; entradas = transições + 1); cruzamento confirmado (anti-jitter); análise frame-a-frame por dentro, apresentação por clip; granularidade máxima na transição.
- **Módulo 3:** `tipo` e `contexto` separados (saida_vidro é contexto); resultado ancorado ao fim do rally.
- **Tolerância:** `margem_ms` (não frames — independente do FPS).
- **Bola fora do frame NÃO corta o rally.** Só há novo rally quando há ausência de bola > 2s **seguida de um SERVIÇO**. Sem serviço a seguir, continua o mesmo rally.

## 4. Ficheiros do projeto (nesta pasta)
**Prompts v9:**
- `prompt_analise_padel_v9.md` — referência (com o porquê de cada regra).
- `prompt_analise_padel_v9_GEMINI.md` — 3 prompts prontos a colar no Gemini.
- `prompt_modelo_hibrido_v9.md` — arquitetura híbrida prompt/modelo/geometria.

**Código do pipeline (testado):**
- `geometria_fases.py` — Módulo 2 em geometria determinística (boxes → fase → clips de confronto). Reproduz o exemplo da v9 (4 clips, 3 transições).
- `deteccao_rallies.py` — Módulo 1 (presença da bola → rallies), com a regra bola fora >2s + serviço.
- `analisar_jogo_v9.py` — ORQUESTRADOR: aplica os prompts v9 ao jogo INTEIRO em lote (Prompt 1 → corta rallies → Prompt 2 e 3 por clip → agrega em analise_jogo.json). Lê os prompts do ficheiro v9; usa google-genai + GEMINI_API_KEY. Base no padrão do `analisar_video.py`.

**Calibração (vídeo "Analise Padel Modelo - Parada 4 min.mp4", frame 960×540):**
- `frame_0001.png`, `overlay_zonas_v9.png`, `overlay_zonas_v9.svg`.
- Âncoras: rede y≈138 (alta conf.), linha de serviço (60,452)→(952,461) (alta), junção das malhas y≈358 (ESTIMADA — confirmar poste).

**Treino do modelo:**
- `train_tcn_kaggle.ipynb` / `.py` — treino do TCN de pancadas no Kaggle (GPU grátis), compatível com `classifier_novo.py`.
- `classifier_novo.py` — TCN real (Conv1d dilatado ×3 → pool → linear; 13 classes; janela 16; features pos/posvel). Pesos: `stroke_tcn.pth` + `stroke_tcn.pth.meta.json`.
- Dados de pancadas do Manel: `shots_manel_completo.csv` (455 rótulos: ts, tipo Direita/Esquerda, subtipo), PDFs de anotação.

## 5. Stack e infraestrutura (do PadelPro)
- Deteção jogadores: torchvision Faster R-CNN (não precisa retreino).
- Tracking: ByteTrack/supervision. Pose: RTMPose (rtmlib/ONNX). Pancadas: TCN próprio. Campo: homografia 4 pontos.
- **YOLO PROIBIDO** (licença AGPL/NonCommercial).
- Treino corre no **Modal** (GPU). Alternativa gratuita: **Kaggle** (dual T4, ~30h/semana). GitHub = repo/fonte de verdade.
- Vasco tem acesso de escrita ao repo. Secrets do Modal no PC do João.

## 6. Plano híbrido / ordem de migração
1. Confirmar Âncora 3 → passar fases do Módulo 2 para **geometria** (maior ganho, sem dataset).
2. Detetor de jogadores/bola alimenta a geometria e o Módulo 1.
3. Gemini como auto-labeler → confirmação humana → dataset de pancadas.
4. Treinar TCN (Módulo 3) e reduzir dependência do prompt.

## 7. Tarefas em aberto
1. **Confirmar Âncora 3** (junção das malhas) no frame — dar o y real do poste.
2. Generalizar fronteiras com a homografia 4 pontos (em vez de linhas fixas).
3. Validar a classificação de fase em vários frames.
4. Integrar a geometria no Módulo 2 do pipeline.
5. Definir `LABEL_MAP` (CSV Manel → 13 classes do TCN) + extração de pose para o dataset Kaggle.

## 8. Estado imediato
Prompts v9 finalizados e prontos a testar no Gemini. À espera dos outputs do
Gemini para validar consistência. Notebook Kaggle pronto (falta o dataset de
features e o mapeamento de labels).
