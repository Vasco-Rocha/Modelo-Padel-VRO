# Plano — Detetor de bola TEMPORAL (nível 2, o salto real)

## Porquê
Um detetor de frame único (o nosso YOLO) vai SEMPRE perder a bola rápida (remates, serviços) — num
frame só, o risco borrado é ambíguo. A solução conhecida: um detetor que vê VÁRIOS frames consecutivos
e apanha a bola pelo MOVIMENTO. É a família TrackNet (é para isto que existe).

## BENCHMARK das alternativas (pesquisa jul 2026)
| Opção | O que é | Prós | Contras |
|-------|---------|------|---------|
| **WASB** ⭐ (NTT, BMVC2023) | HRNet → heatmap, "strong baseline" p/ 5 desportos | **Mesmo grupo do PadelTracker100**; código+dados públicos; generaliza bem | recall é o ponto fraco (=nossa dor) |
| **TrackNetV3** | heatmap + trajectory inpainting/rectification | **recall quase perfeito** (o nosso problema!) | menos generalista |
| **TrackNetV4** | + motion attention (frame diff) | realça o movimento | intermédio |
| **TrackNetV5** (2025) | transformer spatio-temporal + motion decoupling | **SOTA** F1 0.986, recupera oclusões, tempo real | muito novo, menos maduro |
| **BlurBall** (2025) | estima bola + BORRÃO de movimento em conjunto | ataca DIRETO o risco desfocado (nosso modo de falha) | novo, orientado a ténis de mesa |
| **YO-CSA-T** (2025) | YOLO + atenção contextual/espacial | leve, família YOLO (perto do que temos) | menos recall que heatmap |
| **RacketVision** (AAAI2026) | benchmark bola+raquete unificado | insight: raquete ajuda trajetória (futuro M3) | sem padel; é dataset, não detetor |

## RECOMENDAÇÃO (revista jul 2026 — decisão resolvida)
**Primária: BlurBall** (github.com/cogsys-tuebingen/blurball, CVPRW 2026). É **WASB + tratamento do borrão** e resolve tudo de uma vez:
- **Licença MIT** ✅ — uso COMERCIAL OK (crítico; o projeto evita AGPL). Decisão nº1 resolvida.
- Construído POR CIMA do WASB (herda a base HRNet multi-frame) + atenção SE; prevê posição + orientação + extensão do borrão.
- **Ataca a nossa dor exata** (bola rápida borrada = recall baixo).
- **Pesos pré-treinados** de BlurBall E baselines (WASB, TrackNetV2, Monotrack, DeepBall, BallSeg) -> testar OUT-OF-BOX no vídeo antes de treinar.
- **Fine-tune no nosso dataset** suportado (imagens + CSV) e inferência direta em vídeo (CLI hydra).
- **Convenção de anotação = bola no CENTRO do risco + comprimento + orientação** = EXATAMENTE os 2 cliques do anotador_bola.html (as 2 pontas do risco). A anotação do Vasco já está no formato certo.
- CAVEAT: dataset é ténis de mesa (domain gap p/ padel) -> fine-tune com frames Court-Master + treinar no PadelTracker100.
- NOTA de inferência: sensível a frames duplicados (vídeos re-encodados) — o script gera frames únicos automaticamente.

Alternativas se preciso: WASB puro (mesma base, sem borrão), TrackNetV3 (recall via inpainting), TrackNetV5 (SOTA 2025).

## Nada do que temos se perde
O detetor é uma peça SUBSTITUÍVEL. O TrackNet só produz um `ball_xy` melhor por frame — que entra no
MESMO `rallies_bola.py` e nas mesmas regras. Tudo o resto (segmentação, tempo útil, fases, ground-truth,
anotações, mapas de zona) fica igual. Só melhora a entrada.

## Dados (já existem)
- **PadelTracker100** (Zenodo 14653706, CC-BY-4.0) — TEM trajetória da bola anotada, padel, ângulo único.
  É o dataset de treino ideal para o TrackNet (mesmo grupo NTT que fez o WASB/estes trackers).
- **Frames Court-Master anotados por ti** — para adaptação de domínio (a tua câmara 540p). Não se perdem.

## Caminho (quando fechares o YOLO)
1. **Código base:** começar pelo **WASB** (github.com/nttcom/WASB-SBDT) — tem GET_STARTED e datasets.
   Alternativa se o recall desiludir: TrackNetV3. Confirmar LICENÇA (código + pesos) antes de uso comercial.
2. **Preparar dados:** converter a trajetória do PadelTracker100 para o formato do TrackNet (heatmaps
   gaussianos na posição da bola; sequências de 3 frames).
3. **Treinar no Colab (GPU):** treinar o TrackNet no PadelTracker100.
4. **Adaptar ao domínio:** fine-tune com os teus frames Court-Master (os mesmos que anotaste para o YOLO).
5. **Inferência:** correr o TrackNet no vídeo → `ball_xy` por frame (do pico do heatmap).
6. **Ligar ao pipeline:** meter esse `ball_xy` no `segmentar_rallies_bola` (sem mudar mais nada) e medir
   contra o ground-truth (117s / 12 rallies). Recall esperado: bem acima dos 72% atuais.

## Trade-offs / avisos
- É um build maior que afinar o `best.pt` (arquitetura + treino próprios), mas terreno conhecido.
- Precisa de GPU para treino (Colab, como antes).
- Confirmar licenças (código TrackNet + PadelTracker100 é CC-BY-4.0, uso comercial OK com atribuição).

## Referências
- **WASB** (recomendado, código+dados): https://github.com/nttcom/WASB-SBDT · paper https://arxiv.org/abs/2311.05237
- TrackNetV5 (SOTA 2025): https://arxiv.org/pdf/2512.02789
- TrackNetV4 (motion attention): https://arxiv.org/pdf/2409.14543
- TrackNet PyTorch (implementação): https://github.com/yastrebksv/TrackNet
- BlurBall (bola + borrão de movimento): https://arxiv.org/pdf/2509.18387
- YO-CSA-T (YOLO + atenção, tempo real): https://arxiv.org/pdf/2501.06472
- RacketVision (bola+raquete, AAAI2026): https://github.com/OrcustD/RacketVision
- PadelTracker100 (dados de treino): https://zenodo.org/records/14653706

## Estado
Preparado enquanto o Vasco anota + re-treina o YOLO de frame único (nível atual).
Arrancar assim que o YOLO estiver fechado e validado.
