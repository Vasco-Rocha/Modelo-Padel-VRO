# ▶️ COMEÇAR AQUI — conversa nova, 13 jul 2026 (fim do dia)

**O Vasco está a trabalhar AGORA. Não é um retomar frio — é uma continuação.**

---

## 🛑 REGRA ZERO
> **NÃO ALTERAR NADA no pipeline.** *"quando abrir novas conversas, não quero qualquer tipo de
> alteração"* — Vasco.
> `gerar_tempo_util.py` está **TRAVADO** em `96,3 / 95,9 · F1 96,1 · 13/13`.
> ✅ LER, medir, diagnosticar, e **CRIAR FICHEIROS NOVOS** — à vontade.
> ❌ Mexer nas regras, nos limiares, nos valores travados — **só se ele pedir**.

Contexto completo: **`HANDOFF_14JUL.md`**. Receita do vídeo novo: **`RECEITA_VIDEO_NOVO.md`**.

---

# 🎯 A TAREFA IMEDIATA

## Pôr TUDO a correr no Mac. Dois duplo-cliques, zero nuvem.

O Vasco perguntou: *"não há forma de reduzir isto? um processo de 2/3 passos?"*
**Há. E está quase.**

### ✅ O QUE JÁ FUNCIONA LOCALMENTE (verificado, 13 jul)

**A BOLA (BlurBall) JÁ CORRE NO MAC, NA GPU DA APPLE.** Não é teoria — correu hoje às 18:55 e
produziu o CSV que o pipeline usou o dia todo.

Prova: `blurball/outputs/run_full/.hydra/overrides.yaml`
```
- runner.device=mps                    ← a GPU do Mac
- runner.vis_result=False
- runner.vis_hm=False
- detector.model_path=<...>/weights/blurball_models/blurball_best
- +input_vid=<...>/Parada4.mp4
- detector.step=1
- detector.postprocessor.score_threshold=0.4     ← 🔒 NÃO MEXER
```
Ambiente: `blurball/.venv/` (Python 3.9) · Pesos: `blurball/weights/blurball_models/blurball_best`
Sai: `blurball/run_parada4/frames_<video>/traj.csv`
Colunas: `Frame,X,Y,Visibility,L,Theta,score` — **exactamente o que o pipeline lê.**

**⇒ O KAGGLE NÃO É PRECISO PARA A BOLA. Nunca mais.**

### ❌ O QUE FALTA — a ÚNICA peça

**Os JOGADORES.** Correram no Colab, com o `PlayerTracker` do João (`padel_analytics`).
**Esse repo NÃO está clonado no Mac.**

O que já cá está: `yolov8m.pt` (52 MB, na raiz) · `padelpro-vision/padelpro/modules/players_io.py`
(o conversor JSON→boxes — **JÁ EXISTIA**, `carregar_players()`) ·
`padelpro-vision/colab/correr_jogadores_final.py` (a receita: `CONF=0.10`, `IMGSZ=1280`).

O que falta: clonar o `padel_analytics` + instalar `ultralytics` e `supervision` no Mac,
e correr com `device='mps'`.

> ⚠️ **NUNCA improvisar um detetor de jogadores.** Já se tentou um `yolov8n` à pressa e foi pior.
> **Usar o PlayerTracker do João, com `CONF=0.10` e `IMGSZ=1280`** — deteta generosamente, e a
> limpeza faz-se depois com as regras do Vasco (J1-J8).

### 🎬 O ALVO

1. **`NOVO_VIDEO.command`** (duplo-clique) → bola (MPS) + jogadores (MPS) + `verificar_video_novo.py`
2. **calibrar** no `calibrar_campo.html` *(à mão — regra C1 do Vasco. A auto-deteção pôs a linha de
   serviço 40 px ao lado.)*
3. **anotar** no `anotador_rallies.html` *(à mão — é a verdade dele. **CONTAR TODOS OS PONTOS**:
   no Parada4 faltava um.)*
4. **`CORRER.command`** (duplo-clique) → tempo útil + vídeo

> ⚠️ **Escrever e TESTAR com ele ao Mac.** Não entregar um script não testado a dizer "está feito".
> (O Claude não consegue testar o lado do Mac a partir do sandbox: Linux, sem MPS, sem o `.venv`.)

---

# 🔎 UM FIO POR PUXAR (pode devolver 2 regras do Vasco)

O `verificar_video_novo.py` diz que **52,6%** dos frames do Parada4 têm **≥4 boxes**.
Os documentos e a memória dizem **"só 21,8% têm os 4 jogadores"** — e eu usei esse número **o dia
todo** para declarar regras do Vasco como **"bloqueadas pela câmara"**:

- **S2/S3** — formação de serviço
- **v9 regra 5** — inatividade dos jogadores confirma o fim do ponto

**Hipótese (NÃO confirmada):** 52,6% são boxes **cruas** (incluem espectadores — no Parada4 o
espectador era a deteção **mais frequente**, 32% dos frames); os 21,8% serão os jogadores **reais**
depois dos filtros (J1 fora-do-campo, J2/J3 imóveis, J4 dois-por-lado), que vivem em
`padelpro/modules/servico.py` e **NÃO correm** no pipeline do tempo útil.

**Mas o 21,8% nunca foi re-verificado.** Se estiver errado, **essas regras não estão bloqueadas.**
É barato de medir. **Medir antes de citar.**

---

## As 3 lições de ontem (não repetir)
1. 🚨 **Desconfiar do ground-truth** — o "falso" dos 289s era um **ponto a sério**. Precisão
   91,8→93,9 sem mexer em código.
2. 🕳️ **Ler o código, não o mapa** — a S12 e a S8 estavam marcadas ✅ e **não corriam**.
3. 🧪 **Testar, não raciocinar** — descartei 8 regras com um raciocínio bonito; a que ia deitar
   fora (a **pausa**) resolveu o maior problema que havia.

> **Faixa fina = observável. Área grande = ambígua.**
> **E só o que se CORRE é que conta** — a lista de ficheiros dizia que o snapshot estava bom;
> só corrê-lo mostrou que estava partido.
