# Handoff — Conversa "Jogadores" (execução)

**Cola isto no início da conversa nova.** É a conversa de EXECUÇÃO do Colab dos jogadores.
As decisões continuam na conversa "Centro de Decisões".

---

## O PROJETO (30 segundos)

Análise de vídeo de padel com o João Santos. Câmara Court-Master **fixa**, **960×540**.
Repo: `padelpro-vision` → GitHub `Vasco-Rocha/Modelo-Padel-VRO`.
Três módulos: **M1 tempo útil**, **M2 fases**, **M3 pancadas**.

**Ground-truth (a verdade):** `ground_truth_parada4.md` — **117 s / 12 rallies** no `Parada4.mp4`.

**Diretriz de produto (manda em tudo):**
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**

**Como trabalhar com o Vasco:** não é developer. Passo a passo, um de cada vez. As melhores ideias
do projeto vieram dele — ouvir e formalizar, não atropelar.

---

## A TAREFA DESTA CONVERSA

Ter as **boxes dos 4 jogadores** em píxeis, vindas do `padel_analytics` do João Silva.
É o **gargalo**. Tudo o resto está escrito e à espera disto.

**Notebook:** `colab/colab_jogadores_padel_analytics.ipynb`
**Script de afinação:** `colab/afinar_jogadores.py`
**Guia:** `PASSO_A_PASSO.md`

---

## ESTADO (12 jul 2026)

### Feito
- **Calibração do campo** — MANUAL, no `calibrar_campo.html`. 7 linhas + central, validadas.
  Está em `padelpro-vision/calibracao_campo.json`. **NÃO se mexe.**
- **`PlayerTracker` do João a correr** no Colab sobre o Parada4 (8741 frames).
- **3 regras do Vasco** implementadas em `padelpro/modules/servico.py`:
  `filtrar_espectadores()` · `dois_por_lado()` · `continuidade_jogadores()`

### O número atual (mau)
Com o default do João (`CONF=0.5`, `IMGSZ=640`): **4 jogadores em só 9,5 %** do rally #2.

### Porquê — diagnóstico do Vasco (confirmado)
Os jogadores de baixo têm os **pés cortados pela borda inferior** do frame. Meia pessoa = confiança
baixa → o `CONF=0.5` deita-os fora. E os do fundo longe são minúsculos a `IMGSZ=640`.

### O passo seguinte, exato
Correr `colab/afinar_jogadores.py` (2 min, só um rally). Testa `CONF` × `IMGSZ` e mostra o efeito
**cumulativo** das 3 regras. **Ler só a coluna `=4` no fim.**

No Colab, depois da célula 4:
```python
!curl -sO https://raw.githubusercontent.com/Vasco-Rocha/Modelo-Padel-VRO/main/colab/afinar_jogadores.py
exec(open('afinar_jogadores.py').read())
```

Depois: correr o vídeo todo com o melhor `CONF`/`IMGSZ`, gravar
`players_detections_parada4.json` em `dados_parada4/`, e **devolver à conversa de decisões**.

---

## AS 3 REGRAS DO VASCO (a ordem importa)

```
detetar GENEROSAMENTE (CONF baixo, IMGSZ alto)
   ↓
1. FORA DO CAMPO + IMÓVEIS   → tira o público
   ↓
2. CONTINUIDADE              → PREENCHE buracos   ← a única que ACRESCENTA informação
   ↓
3. 2 POR LADO                → corta o que sobra
```

A continuidade tem de vir **antes** do "2 por lado": se cortarmos primeiro, podemos deitar fora o
jogador verdadeiro e ficar com o falso.

1. **Fora do campo** — os pés nunca passam do vidro. (No Parada4 a deteção mais frequente do vídeo
   inteiro era um espectador sentado, em 32 % dos frames.)
2. **Imóveis** — um jogador move-se; um espectador não.
3. **Continuidade** — um jogador não se teletransporta *nem desaparece a meio do ponto*. Com os IDs
   do ByteTrack: se o #3 aparece no frame 100 e no 104, interpola 101–103.
4. **2 por lado** — são sempre 2 contra 2. Fica com os 2 melhores de cada lado da rede.
   Como limpa o excesso, deixa-nos baixar o `CONF` sem pagar precisão.
   **RECALL pela deteção, PRECISÃO pela estrutura.**

---

## ⚠️ ERROS JÁ COMETIDOS — NÃO REPETIR

1. **Nunca improvisar um detetor de jogadores.** Ontem alguém correu um `yolov8n` no notebook com
   `max_det=4` — o espectador ocupava uma vaga e sobrava lugar para 3 jogadores. Os jogadores vêm do
   `padel_analytics`. A objeção dos "metros" é **falsa**: o `PlayerTracker` grava `xyxy` em **píxeis**;
   o campo `projection` (metros) é separado e opcional.

2. **NADA em píxeis absolutos sobrevive à perspetiva.** Já mordeu 4 vezes hoje.
   O meio-campo longe tem **100 px**; o perto tem **290 px** — para os mesmos 6,95 m.
   Uma tolerância de 45 px vale 1,1 m de um lado e 3,1 m do outro.
   **Todas as tolerâncias têm de ser frações do meio-campo local** (`Campo.meio_campo_px`).

3. **Não auto-detetar o campo.** Falhou: marcou a linha de serviço longe 40 px no sítio errado.
   Novo campo = nova calibração à mão no `calibrar_campo.html`. (A FIFA faz o mesmo: pré-calibra
   com câmaras fixas. Ver `BENCHMARK_inferir_linhas.md`.)

4. **Confirmar a premissa antes de aceitar a conclusão.** Duas propostas externas bem argumentadas
   partiam de um pipeline que não é o nosso (assumiam homografia/metros; nós vivemos em píxeis).

---

## DEPENDÊNCIAS FRÁGEIS (tratar quando der)

- **Repo do João** (`github.com/Joao-M-Silva/padel_analytics`) — fazer **fork** e trocar `REPO_URL`
  no topo do notebook. 30 segundos.
- **Pesos** (`yolov8m.pt`, numa **Drive do João**) — é o risco **pior**: um repo recupera-se, um
  modelo treinado não. O notebook já guarda uma cópia na Drive do Vasco na 1.ª corrida
  (`GUARDAR_NA_DRIVE = True`).
- O `requirements.txt` do João **não fixa versões** → o Colab instala as mais recentes e parte.
  Já remendado: `parse`, `pims`, e o `PolygonZone` sem `frame_resolution_wh`.

---

## LABORATÓRIO LOCAL (usar!)

Em `dados_parada4/` estão o `traj_frames_Parada4.csv` (bola) e o `player_boxes_parada4.pkl` (jogadores,
**os velhos, do yolov8n — lixo, substituir**). Com isto o pipeline reproduz-se em **segundos, sem GPU**.
Iterar aqui, não no Colab.

---

## FICHEIROS-CHAVE

- `padelpro/modules/servico.py` — `Campo` (7 linhas + central + laterais) + as 3 regras + M1 + `zona()` do M2
- `padelpro/modules/players_io.py` — leitor do JSON do `padel_analytics` → boxes em píxeis
- `padelpro/modules/blurball_io.py` — bola (BlurBall)
- `calibracao_campo.json` — a geometria (desenhada à mão)
- `calibrar_campo.html` — o calibrador
- `docs/SPEC_M1_TEMPO_UTIL.md` — o desenho completo do M1
- `ground_truth_parada4.md` — a verdade

## GIT

O Vasco faz o push com `PUSH.command` (duplo clique) ou pelo Claude Code.
O sandbox do Cowork **não tem credenciais do GitHub** — commit sim, push não.

## EM PARALELO (por fazer, independente)

**Bola ainda a thr=0.7** (46 % de frames com bola). Passar a **0.4** (76 %) no notebook do BlurBall,
célula 6: `score_threshold=0.7` → `0.4`. Guardar como `traj_frames_Parada4_thr04.csv`.
Bola e jogadores são sinais **independentes** — não competem, somam.
