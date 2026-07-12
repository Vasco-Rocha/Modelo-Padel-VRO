# Retomar — PadelPro Vision (13 jul 2026)

Cola isto na conversa nova.

---

És o **centro de decisões** do PadelPro Vision. Lê a tua memória (`MEMORY.md`) e o
`REGRAS_DO_VASCO.md` na pasta do projeto. **Começa por `project_m1_estado_12jul`.**

## Onde estamos

**M1 (tempo útil): RECALL 93,2% · PRECISÃO 89,4%** — 15 pontos para 12 reais, 126 s para 117 s.
Ao início de ontem estava em 72/63. Os 12 serviços, todos apanhados.
O melhor vídeo: `TEMPO_UTIL_v11_thr04.mp4`.

**Corre tudo em CPU, em segundos.** Não precisa de Colab, Kaggle nem GPU.

Dados prontos, em `dados_parada4/`:
- `traj_frames_Parada4_thr04.csv` — a bola a **thr=0.4** (76,1% dos frames; **tem a coluna `score`
  contínua** ⇒ qualquer threshold futuro afina-se em CPU-segundos, **nunca mais correr o modelo**)
- `traj_frames_Parada4.csv` — a bola a 0.7 (referência)
- `player_boxes_parada4.pkl` — os jogadores

Código: `padelpro-vision/padelpro/modules/m1_tempo_util.py` e `m3_servico.py`
Verdade: `ground_truth_parada4.md` — 12 rallies, 117 s, anotados à mão pelo Vasco.

## As 3 tarefas, por ordem

### 1. 🎈 O BUG DO BALÃO  (parte os pontos 3 e 6→7)
A regra **mão-vs-raquete** (S15) mede o `L` **no cruzamento da rede**. Mas o balão **sai da raquete
depressa e CHEGA LENTO** — no cruzamento tem `L` baixo e é rejeitado como se fosse uma passagem à mão.
❌ **Já tentado e falhou:** medir o `L` máximo do tracklet. Não resolveu.
👉 **Olha aos pontos 3 e 6/7 DIRETAMENTE, com vídeo. Não às médias.**

### 2. 🔴 OS ATALHOS  (o Vasco apanhou-os e tem razão)
- **`vmax = 90 px/frame`** — píxeis absolutos. **Viola a lição da perspetiva que já mordeu 5 vezes.**
  Devia ser fração do `meio_campo_px`.
- `L≥11`, `sil=4s`, `pad=1,6s`, `min_prof=0,35`, pancada=`ΔTheta≥20° ∧ L≥7` — todos afinados ao F1
  **deste** vídeo, e contra o CSV do **0.7** (com o 0.4 mudou tudo por baixo). **Re-derivar da estrutura.**

### 3. 📊 TABELA DE ABLAÇÃO
O Vasco perguntou: *"porque é que algumas regras vão perdendo firmeza ao longo do dia?"*
**Porque não há testes de regressão.** Cada regra nova amolece as anteriores sem avisar.
Construir: cada regra ligada/desligada, contribuição isolada, corrida em cada versão.

## Regras do Vasco ainda por implementar
- **Duplo ressalto** (S10) + **fim = 2 ressaltos sem raquete** (S14) — o bloqueio único do M3
- **Bola na rede → fim certo**, corte a 0,5 s (S17)
- **Mão/corpo na bola → fim** — via postura corporal das boxes (S18)
- **Alternância** dos serviços (S6) — mas **pontua, não corta** (ponto de ouro, tie-break)

## ⚠️ COMO TRABALHAR (não negociável)

1. **SEM ATALHOS na geometria.** Números mágicos proibidos. Só do `calibracao_campo.json` ou frações
   do meio-campo. **Declarar o atalho na MESMA mensagem em que dás o número.**
2. **VÍDEO ANTES DE MÉTRICAS.** O Vasco encontrou TODOS os bugs a olhar para os vídeos — o espectador,
   o balão, os cortes prematuros, a regra invertida. **Nenhum apareceu nos números.**
3. **As regras do Vasco são LEIS** (sobrevivem à câmara nova). **Os meus números são AJUSTES** (não
   sobrevivem). Não os apresentar com o mesmo estatuto.
4. **Definições do jogo param e perguntam.** O que é "dentro do campo", "serviço", "ponto" — é dele.
5. O Vasco **não é developer**. Passo a passo, uma coisa de cada vez.

## Diretriz de produto (manda em tudo)
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**
