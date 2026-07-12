# Handoff — Centro de Decisões, PadelPro Vision (11 jul 2026)

Estado completo para retomar. Ler isto + a memória (`project_blurball_result`, `project_serve_detection`, `project_tempo_util_diretriz`, `project_via_a_result`).

---

## OS REPOS (importante — não confundir)
- **NOSSO (é aqui que trabalhamos):** https://github.com/Vasco-Rocha/Modelo-Padel-VRO
  Localmente: pasta **`padelpro-vision/`** dentro de *Documents/Claude/Projects/Treino de Modelo de análise - Com Joao Santos*.
- **DE BASE (do João Silva, que consumimos):** https://github.com/Joao-M-Silva/padel_analytics
  É **daqui que vêm os JOGADORES** (deteção + tracking). Não improvisar outro detetor — ver o erro assinalado abaixo.
- **BlurBall (detetor de bola, externo):** https://github.com/cogsys-tuebingen/blurball (MIT)

## O PROJETO
Análise de vídeo de padel (com o João Santos). Câmara Court-Master **fixa**, **960×540** nativo.
Três módulos: **M1 tempo útil** (rallies), **M2 fases de jogo**, **M3 pancadas**.

**Conjunto de avaliação permanente:** `ground_truth_parada4.md` — **117s / 12 rallies**, anotado à mão pelo Vasco. É a verdade. (O corte manual do WhatsApp de 132.2s tinha margens do editor — ignorar.)

---

## DIRETRIZ DE PRODUTO (manda em tudo)
> **Nunca deixar um ponto de fora. Mais lixo é preferível a menos tempo útil.**

O custo é assimétrico: um ponto perdido é informação perdida para sempre; lixo a mais é só um incómodo a saltar. **Otimizar RECALL, não precisão.**

---

## O QUE ACONTECEU HOJE

### 1. Via A (fine-tune do YOLO da bola) — **MORREU**. Não repetir.
`best_v2` ficou **pior** que o `best.pt`: recall 57% vs 67%, precisão 39% vs 73%. Treinar só nos 637 frames difíceis (metade negativos) colapsou a confiança do modelo. Um YOLO de-um-frame não resolve a bola borrada — num único frame ela é genuinamente ambígua.

### 2. BlurBall (detetor temporal) — **GANHOU**. É o novo detetor de bola.
Out-of-box (sem treino), recall da bola dentro dos rallies: **85.6%** (thr 0.4) vs 67% do YOLO.
Integração: `padelpro/modules/blurball_io.py` (`traj.csv` → `ball_xy`).

### 3. O gargalo MUDOU: do detetor → para a SEGMENTAÇÃO.
As regras v9 mediam "jogo" pela **ausência de bola** — muleta do detetor fraco. Com um detetor forte a bola está quase sempre visível (**também entre pontos, onde é bola REAL**) → a regra fundia tudo em mega-rallies.
**Correção que funcionou:** desligar o merge-por-serviço (`serve_zone_y=None`) + filtrar por velocidade + cortar nos gaps.

### 4. Regras do Vasco que FUNCIONAM (implementadas em `padelpro/modules/servico.py`)
- **Objetos imóveis:** deteções no mesmo píxel espalhadas por >35% do vídeo não são a bola. Apanha 4 objetos. **Sobe a precisão sem custar recall.**
- **Continuidade:** a bola **não se teletransporta** (`vmax=80 px/frame` ≈ 100 km/h). Salto impossível = outro objeto. Não precisa de conhecer o inimigo.
- **Zona de serviço aprendida dos dados:** a bola no chão junto a um jogador atrás da linha → **10/12 serviços reais**. Bom gerador de candidatos.
- **Formação** (parceiro na rede + adversário cruzado atrás) → **0 falsos** ✓
- **Quadrado de serviço cruzado** (a bola cai na diagonal) → **0 falsos** ✓

### 5. ⚠️ A CONCLUSÃO DO DIA: **as regras estão certas; o SINAL é que falta.**
A formação e o quadrado cruzado dão **zero falsos quando conseguem ver** — mas rejeitam serviços verdadeiros por **falta de dados**:
- **Bola:** 46% visível (thr 0.7) → o ressalto do serviço quase nunca se vê.
- **Jogadores:** os 4 presentes em só **53%** dos frames.

**Não escrever mais regras. Melhorar o sinal.**

### 6. BUG encontrado e corrigido
A `serve_zone` antiga `(335,421)` estava **ACIMA** da linha de serviço real (~462) → **o servidor de baixo NUNCA podia ser detetado.** Geometria agora auto-detetada em `calibracao_campo.json` (linhas brancas sobre azul, mediana de frames, parábola por linha porque a lente curva-as): linha de serviço perto (432→462), longe (~117), rede (~139), centro x=511.

---

## ⚠️ ERRO A NÃO REPETIR — a deteção de JOGADORES
O `player_boxes` das experiências veio de um **`yolov8n` improvisado** dentro do notebook do BlurBall (o Claude mandou fazer isso porque o CSV do `padel_analytics` está em metros). **Foi um atalho errado — e criou o gargalo dos 53%.**

A deteção de jogadores **é do `padel_analytics`** (João Silva): já está definida, validada, e faz **tracking**. Este repo foi construído por cima dela. A objeção dos "metros" é fraca — ele deteta em **píxeis** e só depois converte por homografia. **Ir buscar as boxes em píxeis ANTES da conversão. Não é treinar outro modelo; é ligar o que já existe.**

---

## ESTADO NUMÉRICO (contra o GT: 12 rallies, 117s)

| | rallies | recall | precisão | tempo útil |
|---|---|---|---|---|
| baseline YOLO `best.pt` | 10 | 67% | 73% | 106s |
| BlurBall + limpeza | 16 | 93% | 69% | 158s |
| **+ âncora de serviço** | 22 | **91%** | **72%** | **148s** |

Recall muito acima do baseline. Sobra: **sobre-segmentação** (13 serviços falsos partem rallies) — que a **formação** mataria, se os jogadores estivessem lá.

---

## PRÓXIMOS PASSOS (por esta ordem)

1. **JOGADORES — ligar o `padel_analytics`** (boxes em píxeis, com tracking). O gargalo. Destranca a formação → mata os 13 serviços falsos → a âncora do serviço fica limpa.
2. **BOLA — `traj.csv` do thr=0.4** (76% visível vs os 46% atuais). Destranca o **ressalto** e o **quadrado cruzado**. (O Vasco pôs a correr; se não estiver feito, é mudar `score_threshold=0.7` → `0.4` na célula 6 do notebook do BlurBall, ~20 min.)
3. **MONTAR O PIPELINE ponta-a-ponta** — as peças estão no repo e provadas, mas o `pipeline.py` ainda corre o fluxo antigo. Não há um "vídeo → tempo útil". Montar: `vídeo → BlurBall → limpar() → detetar_servicos() → rallies → clips/JSON`. **Tudo em píxeis** (é onde vivem as regras).
4. **M2 (fases) sai quase de graça** — a `calibracao_campo.json` + a classe `Campo` já servem. Falta **UMA linha**: a interceção **malha 3 / malha 2** (fronteira do ATAQUE). Não é linha branca → gerar um frame com régua de `y` e o Vasco lê. Aí o M2 passa a **geometria pura** (sem IA, determinístico).

---

## LABORATÓRIO LOCAL (grande ganho — usar!)
Em `dados_parada4/` estão o `traj_frames_Parada4.csv` (bola) e o `player_boxes_parada4.pkl`. Com isso o pipeline **reproduz-se em segundos, sem GPU e sem Kaggle** (validado: dá exatamente os mesmos números). Permite iterar dezenas de variantes numa tarde.

## FICHEIROS-CHAVE
- `padelpro-vision/padelpro/modules/blurball_io.py` — integração BlurBall + ponto de operação + `avaliar()`
- `padelpro-vision/padelpro/modules/servico.py` — limpeza (imóveis, continuidade) + `Campo` + formação + deteção de serviço
- `padelpro-vision/calibracao_campo.json` — geometria auto-detetada
- `padelpro-vision/docs/SPEC_M1_TEMPO_UTIL.md` — **o desenho completo do M1** (serviço como fronteira, travessias alternadas, lado do serviço = ace vs falta, fins)
- `padelpro-vision/docs/REGRAS_CONSOLIDADAS_todos_prompts.md` — todas as regras v1→v9
- `ground_truth_parada4.md` — a verdade (117s / 12 rallies)

## COMO TRABALHAR COM O VASCO
Não é developer. Passo a passo, **um de cada vez**. Confirmar com screenshots. Explicar o "porquê" curto. As melhores ideias do projeto vieram dele (imóveis, continuidade, ressalto, alternância, lado do serviço) — **ouvir e formalizar**, não atropelar.

## DIVISÃO DE CONVERSAS
- **Decisões (esta):** rumo, interpretação de números, spec. Opus/Alto.
- **BlurBall (Opus):** execução, inferência, integração.
- **Sonnet:** mecânico (edições repetitivas, manifests).
Os cálculos em GPU **não gastam créditos de Claude** — o que gasta é o raciocínio. Escrever a receita uma vez aqui, iterar lá, trazer só o número.
