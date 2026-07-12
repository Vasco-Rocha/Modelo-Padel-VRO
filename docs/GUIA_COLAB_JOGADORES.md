# Guia — Colab dos JOGADORES (padel_analytics)

**Objetivo:** obter as boxes dos 4 jogadores **em píxeis, com tracking**, vindas do detetor do
João Silva. Substitui o `yolov8n` improvisado (que só via os 4 jogadores em **53%** dos frames).

**Ficheiro:** `padelpro-vision/colab/colab_jogadores_padel_analytics.ipynb`
**Vídeo:** `Parada4.mp4` (o do ground-truth: 12 rallies / 117s)
**Tempo:** ~20–30 min, quase tudo à espera.
**Resultado:** um ficheiro `players_detections_parada4.json`.

---

## Antes de abrir

1. Faz o **push** primeiro (senão o Colab clona uma versão antiga do nosso repo):
   ```
   cd "/Users/vascorocha/Documents/Claude/Projects/Treino de Modelo de análise - Com Joao Santos/padelpro-vision" && rm -f .git/*.lock && git add -A && git commit -m "Jogadores do padel_analytics" && git push origin main
   ```
2. Tem o `Parada4.mp4` à mão (está na pasta do projeto) — vais fazer upload dele.

---

## Abrir o notebook

- Vai a **colab.research.google.com** → separador **GitHub** → cola:
  `https://github.com/Vasco-Rocha/Modelo-Padel-VRO`
  → escolhe `colab/colab_jogadores_padel_analytics.ipynb`
- **Runtime → Change runtime type → T4 GPU** → Save.
  (Sem isto demora horas em vez de minutos.)

---

## Correr, célula a célula

Corre **uma de cada vez** (Shift+Enter). Não uses "Run all".

### Célula 1 — GPU + clonar + instalar
Espera ~2 min. **Deve acabar a imprimir `OK`.**
Se `nvidia-smi -L` não mostrar uma GPU → voltaste a esquecer-te do T4.

### Célula 2 — Pesos
Descarrega o `yolov8m.pt` da Drive do João. ~1–2 min.
**Deve imprimir `Pesos OK: True`.**
Se der erro a dizer que falta o `yolov8m.pt`, para e diz-me.

### Célula 3 — Upload do vídeo
Abre um botão **"Escolher ficheiros"** → escolhe o **`Parada4.mp4`**.
Upload demora alguns minutos (é um ficheiro grande — não fecha o separador).
**Deve imprimir algo como:** `960x540, 25.00 fps, 8741 frames (350s)`.

### Célula 4 — Os 4 cantos (a única parte manual)
Aparece o 1.º frame do vídeo. **Clica nos 4 cantos do campo, por esta ordem:**

```
        3 ------------------- 4     (fundo LONGE, ao fundo da imagem)
        |                     |
        |        rede         |
        |                     |
        2 ------------------- 1     (fundo PERTO, junto à câmara)
```

- **1** = canto de baixo à **DIREITA**
- **2** = canto de baixo à **ESQUERDA**
- **3** = canto de cima à **ESQUERDA**
- **4** = canto de cima à **DIREITA**

**Clica um pouco POR FORA das linhas brancas** (uns 10–20 píxeis para fora).
Este polígono serve só para descartar quem está **fora** do campo (público, treinadores).
Se ficar apertado, corta jogadores encostados ao vidro — e a diretriz é **nunca perder um jogador**.
Melhor largo do que apertado.

- O botão **"Anular último"** desfaz o último clique.
- Ao 4.º clique grava sozinho e imprime `Cantos guardados: [[...]]`.
- **Confirma que apareceu essa linha antes de avançar.** Se não apareceu, os cliques falharam
  → usa a célula **4b** (fallback: preenche as coordenadas à mão, descomentando as linhas).

### Célula 5 — Correr o detetor
É a que demora: **~10–20 min** com a T4 (8741 frames).
Mostra uma barra de progresso. Vai fazendo scroll de vez em quando para o Colab não te desligar.
**Deve acabar a imprimir:** `frames processados: 8741`.

### Célula 6 — ⭐ O NÚMERO QUE INTERESSA
Imprime:
```
com os 4 jogadores: XX%   <-- o numero que interessa (yolov8n improvisado: 53%)
```

**É este número que decide o dia.**
- **~85%+** → excelente. A `formacao_servico()` passa a conseguir decidir, os 13 serviços falsos
  morrem, a precisão sobe sem custar recall.
- **60–80%** → melhorou, mas ainda há gargalo. Traz o número na mesma.
- **≈53% ou menos** → algo está mal (provavelmente o polígono dos cantos ficou apertado, ou os
  cliques trocaram a ordem). **Para e diz-me.**

### Célula 7 — Descarregar
Descarrega o `players_detections_parada4.json`.
**Guarda-o na pasta:**
```
Documents/Claude/Projects/Treino de Modelo de análise - Com Joao Santos/dados_parada4/
```

---

## Depois

Diz-me só duas coisas:
1. **A percentagem** da célula 6.
2. Que o **JSON já está na pasta `dados_parada4/`**.

Eu corro a avaliação no laboratório local (segundos, sem GPU) contra o ground-truth
(12 rallies / 117s) e trago os números novos de recall / precisão / tempo útil.

---

## Em paralelo (outra conversa, também GPU)

Enquanto este corre, mete o **BlurBall thr=0.4** a correr:
> Notebook do BlurBall, célula 6: `score_threshold=0.7` → `0.4`. Correr sobre o `Parada4.mp4`.
> Guardar o resultado como `traj_frames_Parada4_thr04.csv`.

Os dois sinais (jogadores e bola) são **independentes** — não competem, somam.
