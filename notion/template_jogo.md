# 🎾 Jogo — {Dupla A} vs {Dupla B} — {AAAA-MM-DD}

> Como usar no Notion: cria uma base de dados "Jogos" (vista Tabela). Abre **Novo ▾ → + Novo template**, e cola lá o conteúdo abaixo. A partir daí, cada jogo novo nasce com esta estrutura. As linhas "Propriedades" devem virar campos da base de dados (Data, Court, etc.).

---

## Propriedades (campos da base de dados)

| Campo | Valor |
|---|---|
| Data | {AAAA-MM-DD} |
| Court / Local | {ex.: MATCHi — Court 3} |
| Câmara | {MATCHi TV / transmissão} |
| Duração total | {mm:ss} |
| Resultado | {6-4, 6-3} |
| Estado da análise | 🟡 Por processar / 🟢 Concluída |
| Link do CSV | {url do data.csv} |

---

## 🎥 Vídeo anotado

> Cola aqui o link do vídeo com as bounding boxes (Drive/YouTube) — o Notion embebe automaticamente.

{colar_link_do_video}

---

## ⏱️ 1. Tempo útil

| Métrica | Valor |
|---|---|
| Tempo total | {mm:ss} |
| Tempo útil (bola em jogo) | {mm:ss} |
| Rácio jogo/pausa | {xx %} |
| Nº de rallies | {n} |
| Duração média do ponto | {x.x s} |
| Ponto mais longo | {x.x s} |

---

## 🧭 2. Fases de jogo

Tempo passado em cada formação das duas duplas.

| Fase | Tempo | % do jogo útil |
|---|---|---|
| Ambas na rede | {mm:ss} | {xx %} |
| Ambas no fundo | {mm:ss} | {xx %} |
| Transição | {mm:ss} | {xx %} |
| Ataque vs defesa | {mm:ss} | {xx %} |

---

## 🏓 3. Pancadas por jogador

| Jogador | Total | Drives | Voleios | Bandejas | Remates | Winners | Erros forçados | Erros não forçados |
|---|---|---|---|---|---|---|---|---|
| Jogador 1 | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| Jogador 2 | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| Jogador 3 | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| Jogador 4 | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |

---

## 🔥 4. Posicionamento / Heatmap

> Cola aqui a imagem do heatmap de cada dupla (gerada a partir do data.csv).

{colar_imagem_heatmap}

---

## 📝 5. Notas do treinador

- {observação tática 1}
- {padrão a corrigir}
- {pontos fortes do jogo}

---

## ⚙️ Origem dos dados

- Pipeline: `padel_analytics` (Colab, GPU) → `data.csv`
- Análise: `padelpro analyze --players data.csv` → tempo útil, fases, pancadas
- Gerado em: {data de processamento}
