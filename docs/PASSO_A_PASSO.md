# Passo a passo — 12 jul 2026

Objetivo: ter as **boxes dos 4 jogadores** vindas do `padel_analytics` (não improvisadas).
É o gargalo. Tudo o resto está escrito e à espera disto.

---

## 1 · Enviar o código para o GitHub  ⏱ 1 min

O Colab vai buscar o código ao GitHub, não ao teu Mac. Sem isto, corre a versão antiga.

**Duplo clique em `PUSH.command`** (está na pasta do projeto).
Abre uma janela preta → espera pelo ✅ → fecha.

> Se o macOS reclamar: botão direito → Abrir → Abrir.
> Alternativa: no Claude Code, escreve *"faz commit e push do padelpro-vision"*.

---

## 2 · Abrir o Colab  ⏱ 1 min

Cola isto na barra de endereço do browser:

```
https://colab.research.google.com/github/Vasco-Rocha/Modelo-Padel-VRO/blob/main/colab/colab_jogadores_padel_analytics.ipynb
```

Depois: **Runtime → Change runtime type → T4 GPU → Save**.
(Sem GPU demora horas em vez de minutos.)

---

## 3 · Correr — uma célula de cada vez  (Shift+Enter)

**Nunca "Run all"** — a célula 3 pára à tua espera.

| Célula | O que faz | Espera até |
|---|---|---|
| **1** | GPU + clona o repo do João + instala | imprimir `OK` (~2 min) |
| **2** | descarrega o `yolov8m.pt` | `Pesos OK: True` (~2 min) |
| **3** | ⏸ **upload do `Parada4.mp4`** | imprimir `960x540, ... 8741 frames` |
| **4** | zona = frame inteiro | `Zona de detecao: frame inteiro` (instantâneo) |
| **5** | **corre o detetor** | `frames processados: 8741` (**10–20 min**) |
| **6** | quantas pessoas detetou | vê os números |
| **6b** | **vídeo do rally com as caixas** | vê-o |
| **7** | descarrega o JSON | guarda o ficheiro |

> Na célula 3, se **não** disser `960x540`, para e avisa-me — a calibração é para essa resolução.
>
> A célula 5 é a longa. Vai fazendo scroll de vez em quando para o Colab não te desligar.

---

## 4 · Guardar o resultado

O ficheiro que a célula 7 descarrega chama-se **`players_detections_parada4.json`**.

Põe-no em:

```
Treino de Modelo de análise - Com Joao Santos/dados_parada4/
```

---

## 5 · Dizer-me duas coisas

1. **O vídeo da 6b** — são 4 caixas? os IDs mantêm-se quando os jogadores se cruzam?
2. **Que o JSON já está em `dados_parada4/`.**

A partir daí faço eu, no laboratório local (segundos, sem GPU):
limpo o público com a tua geometria → corro o M1 contra o ground-truth (12 rallies / 117 s)
→ trago recall, precisão e tempo útil.

---

## Em paralelo, se quiseres (outra conversa, também GPU)

A **bola** ainda está no ponto de operação antigo (46% de frames com bola).
No notebook do BlurBall: célula 6, `score_threshold=0.7` → **`0.4`** (passa a 76%).
Correr sobre o `Parada4.mp4`, guardar como `traj_frames_Parada4_thr04.csv`.

Bola e jogadores são **sinais independentes** — não competem, somam.
