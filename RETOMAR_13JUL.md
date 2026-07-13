# PadelPro Vision — retomar (13 jul 2026)

**Cola tudo o que está abaixo na conversa nova do Cowork.**

---

És o **centro de decisões** do PadelPro Vision. Lê a tua memória (`MEMORY.md`) — começa pela
entrada **`project_m1_estado_12jul`** — e o **`REGRAS_DO_VASCO.md`** na pasta do projeto.

## ONDE ESTAMOS

**M1 (tempo útil): RECALL 93,2% · PRECISÃO 89,4% · 12/12 serviços.**
15 pontos para 12 reais · 122 s para 117 s. De manhã estava em **72/63**.

**Corre tudo em CPU, em segundos.** Sem GPU, sem Colab, sem Kaggle.

```bash
cd padelpro-vision
python3 teste_regressao.py            # 🔒 confirma que nada se partiu
python3 gerar_tempo_util.py           # as métricas
python3 gerar_tempo_util.py --video   # + a compilação do tempo útil
```

### Ficheiros
| | |
|---|---|
| `padelpro-vision/gerar_tempo_util.py` | **o pipeline inteiro**, com os atalhos declarados no topo |
| `padelpro-vision/teste_regressao.py` | 🔒 **corre SEMPRE antes e depois de mexer em algo** |
| `dados_parada4/traj_frames_Parada4_thr04.csv` | a bola a **thr=0.4** (76,1%). **Tem a coluna `score` contínua** ⇒ qualquer threshold futuro afina-se em CPU-segundos, **nunca mais correr o modelo** |
| `dados_parada4/player_boxes_parada4.pkl` | os jogadores |
| `ground_truth_parada4.md` | a verdade: 12 rallies, 117 s, anotados à mão pelo Vasco |
| `REGRAS_DO_VASCO.md` | **as regras — S1 a S18, B1 a B10, J1 a J9, C1 a C5** |
| `TEMPO_UTIL_v11_thr04.mp4` | o melhor resultado, em vídeo |

## AS 3 TAREFAS, POR ORDEM

### 1. 🎈 O BUG DO BALÃO — parte os pontos 3 e 6→7
A regra **mão-vs-raquete** (S15) mede o `L` **no cruzamento da rede**. Mas o balão **sai da raquete
depressa e CHEGA LENTO** — ao cruzar tem `L` baixo e é rejeitado como se fosse passagem à mão.
❌ **Já tentado e FALHOU:** medir o `L` máximo do tracklet (a raquetada na origem). Não resolveu.
👉 **Olhar aos pontos 3 e 6/7 DIRETAMENTE, com vídeo. Não às médias.**

### 2. 🔴 OS ATALHOS — o Vasco apanhou-os e tem razão
- **`VMAX = 90 px/frame`** ← **o pior.** Píxeis absolutos: **viola a lição da perspetiva que já
  mordeu 5 vezes** (meio-campo longe = 100 px; perto = 290 px, para os mesmos 6,95 m).
  Devia ser **fração do `meio_campo_px`**.
- `L_RAQUETE=11`, `SILENCIO=4s`, `PAD_ANTES=1.6s`, `MIN_PROF=0.35`, `PAN_DTHETA=20`, `PAN_L=7`
  — todos afinados ao **F1 deste vídeo**, e contra o CSV do **0.7** (com o 0.4 mudou tudo por baixo).
  **Re-derivar a partir da estrutura.** As regras são leis; os números são ajustes.

### 3. 📊 TABELA DE ABLAÇÃO
O Vasco perguntou: *"porque é que algumas regras vão perdendo firmeza ao longo do dia?"*
**Porque não havia testes.** O `teste_regressao.py` resolve metade. Falta a outra: cada regra
ligada/desligada, contribuição isolada, corrida em cada versão.

## REGRAS DO VASCO AINDA POR IMPLEMENTAR
- **S10 duplo ressalto** + **S14 fim = 2 ressaltos sem raquete** — *o bloqueio único do M3*
- **S17** bola na rede → fim certo, corte a **0,5 s**
- **S18** mão/corpo na bola → fim (via **postura corporal** das boxes)
- **S6 alternância** dos serviços — **pontua, não corta** (ponto de ouro, tie-break)

---

## ⚠️ COMO TRABALHAR — NÃO NEGOCIÁVEL

1. **NÃO INVENTAR NEM ATALHAR NADA DO QUE JÁ ESTÁ FEITO.** Corre o `teste_regressao.py` antes e
   depois de qualquer alteração. Se falhar, a alteração está errada.
   **Nenhum valor travado se muda para o teste passar.**
2. **SEM ATALHOS NA GEOMETRIA.** Números mágicos proibidos: só do `calibracao_campo.json` ou frações
   do meio-campo. **Declarar o atalho na MESMA mensagem em que se dá o número.**
3. **VÍDEO ANTES DE MÉTRICAS.** O Vasco encontrou **todos** os bugs a olhar para os vídeos — o
   espectador contado como jogador, o balão, os cortes prematuros, a regra invertida.
   **Nenhum apareceu nos números.** Os números diziam que estava tudo bem.
4. **As regras do Vasco são LEIS** (sobrevivem a outra câmara). **Os meus números são AJUSTES**
   (não sobrevivem). Nunca os apresentar com o mesmo estatuto.
5. **Definições do jogo PARAM e PERGUNTAM.** O que é "dentro do campo", "serviço", "ponto",
   "tempo útil" — é dele. Eu implemento; não decido.
6. O Vasco **não é developer**. Passo a passo, uma coisa de cada vez.
7. **Alterações debatem-se primeiro.** Nada entra sem passar pelo teste.

## DIRETRIZ DE PRODUTO (manda em tudo)
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL, não precisão.**

## CONTEXTO DA CÂMARA
Esta é a **pior câmara** que vamos ter (960×540, baixa, corta os jogadores de baixo — só 21,8% dos
frames têm os 4). **Decisão do Vasco: vamos até ao fim com esta.** Só depois se passa a vídeo decente.
⇒ **Não afinar limiares a este vídeo** — o que se afina a esta câmara morre na próxima.
