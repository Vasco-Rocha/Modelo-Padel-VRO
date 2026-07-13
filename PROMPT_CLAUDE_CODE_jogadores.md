# ▶️ PROMPT PARA O CLAUDE CODE — pôr os JOGADORES a correr no Mac

*(abrir o Claude Code na pasta `Treino de Modelo de análise - Com Joao Santos` e colar tudo o que está abaixo)*

---

## 🛑 REGRA ZERO — LER PRIMEIRO

**NÃO ALTERAR NADA do que já existe e funciona.**

O pipeline `padelpro-vision/gerar_tempo_util.py` está **TRAVADO** em
`RECALL 96,3 · PRECISÃO 95,9 · F1 96,1 · 13/13 serviços`.

- ❌ **NÃO** mexer no `gerar_tempo_util.py`
- ❌ **NÃO** mexer no `teste_regressao.py` nem nos valores travados lá dentro
- ❌ **NÃO** "melhorar", "afinar", "limpar" ou "refatorizar" nada
- ✅ **CRIAR ficheiros novos** — à vontade
- ✅ **Instalar** dependências, clonar repos, correr coisas — à vontade

**Correr `python3 padelpro-vision/teste_regressao.py` ANTES e DEPOIS.** Se falhar no fim,
a alteração é que está errada — nunca o teste.

---

# 🎯 A TAREFA

**Pôr o detetor de JOGADORES a correr no Mac, na GPU (`mps`).**

É a **única peça** que ainda depende da nuvem. A bola (BlurBall) **já corre no Mac** —
verificado, com `runner.device=mps`. Os jogadores ainda corriam no Colab.

## O que já cá está

| | |
|---|---|
| `yolov8m.pt` (52 MB) | na raiz do projeto |
| `padelpro-vision/padelpro/modules/players_io.py` | o leitor — `carregar_players()` |
| `padelpro-vision/json_para_pkl.py` | o conversor JSON → `.pkl` (**ler o docstring: tem o formato exato que o pipeline espera**) |
| `padelpro-vision/colab/correr_jogadores_final.py` | **a receita que funcionou no Colab** — `CONF=0.10`, `IMGSZ=1280` |
| `dados_parada4/player_boxes_parada4.pkl` | **o resultado do Colab — é o PADRÃO-OURO para comparar** |
| `Parada4.mp4` | o vídeo |

## O que falta

O repo `padel_analytics` (do João) **não está clonado no Mac**.
Está forkado em: **`https://github.com/Vasco-Rocha/padel_analytics`** ← clonar **este** (o fork
do Vasco, não o original — assim qualquer alteração para `mps` fica registada).

---

# OS PASSOS

## 1. Clonar o fork, ao lado dos outros

```bash
cd "/Users/vascorocha/Documents/Claude/Projects/Treino de Modelo de análise - Com Joao Santos"
git clone https://github.com/Vasco-Rocha/padel_analytics.git
```

Fica assim:
```
Treino de Modelo de análise/
├── padelpro-vision/     ← o pipeline
├── blurball/            ← a bola   (já corre em mps ✅)
└── padel_analytics/     ← os jogadores  (a instalar)
```

## 2. Ambiente próprio (não contaminar o do BlurBall)

O BlurBall tem o seu `.venv` em Python 3.9 — **não lhe tocar**.
Criar um `.venv` separado dentro do `padel_analytics/`. Instalar `ultralytics` e `supervision`.

## 3. Correr o `PlayerTracker` no `Parada4.mp4`, com `device='mps'`

> ⚠️ **USAR O `PlayerTracker` DO JOÃO. NUNCA improvisar um detetor.**
> Já se tentou um `yolov8n` à pressa e **ficou pior**.

**A receita (do `colab/correr_jogadores_final.py` — não inventar outra):**
- modelo: `yolov8m.pt`
- `CONF = 0.10`  ← **deteta GENEROSAMENTE.** A limpeza faz-se depois, com as regras do Vasco
  (J1 fora-do-campo, J4 dois-por-lado, J5 continuidade). **Baixar o CONF é intencional.**
- `IMGSZ = 1280`
- `device = 'mps'`

Sai um JSON → passar pelo `json_para_pkl.py` → dá o `.pkl` que o pipeline lê.

## 4. 🔑 O PASSO QUE INTERESSA — **PROVAR QUE ENCAIXA**

> **Não basta correr. Tem de dar o MESMO que o Colab deu.**
> *(Lição do projeto: "só o que se CORRE é que conta". Uma lista de ficheiros já disse
> que estava tudo bem quando estava partido.)*

Comparar o `.pkl` novo (Mac/mps) com o `dados_parada4/player_boxes_parada4.pkl` (Colab/CUDA):

- **nº de frames** — igual?
- **nº médio de boxes por frame** — igual? *(o do Colab é a referência)*
- **IoU** das boxes, frame a frame — se >0,9 na esmagadora maioria, é a mesma coisa
- Se houver diferença: **dizer o número, não encolher os ombros.** `mps` e `CUDA` podem
  divergir ligeiramente em floats — mas **não podem dar contagens diferentes de jogadores**.

## 5. 🎬 E O VÍDEO — **sempre**

**Gerar um MP4 com as boxes desenhadas por cima do Parada4.** O Vasco vê com os olhos dele;
os números escondem os bugs. *(Foi a olhar que ele encontrou o espectador contado como jogador.)*

## 6. Empacotar num duplo-clique

Criar o **`NOVO_VIDEO.command`** na raiz do projeto (executável, `chmod +x`):

```
recebe:  o caminho de um vídeo novo
faz:     1. bola      → BlurBall, mps, thr=0.4  🔒 (NÃO mexer no threshold)
         2. jogadores → PlayerTracker, mps, CONF=0.10, IMGSZ=1280
         3. converte  → json_para_pkl.py
         4. verifica  → python3 padelpro-vision/verificar_video_novo.py ../dados_X/
```

**Testar o `.command` a sério, com duplo-clique.** Não entregar um script não testado a
dizer "está feito".

---

# NO FIM, RESPONDER A ISTO

1. O `padel_analytics` correu em `mps`? **Sim/não.** Quanto tempo demorou?
2. O `.pkl` do Mac bate certo com o do Colab? **Com que números?**
3. O `teste_regressao.py` continua a dar `96,3 / 95,9 / 13 / 13 / 133 / 19 / 0`?
4. Onde está o vídeo com as boxes desenhadas?

**Se alguma coisa não correu — DIZER. Não arredondar, não fingir.**
