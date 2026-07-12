# 🎬 RECEITA — um VÍDEO NOVO, do zero até ao tempo útil

**Para o 2.º vídeo (outra câmara).** Escrita em 13 jul 2026, com o pipeline em `96,3 / 95,9`.

---

## 🛑 ANTES DE COMEÇAR — O COMPROMISSO

> **NÃO SE TOCA EM NENHUM PARÂMETRO.**
> `L_RAQUETE=11` · `SILENCIO=4` · `PAD_ANTES=1,6` · `MIN_PROF=0,35` · `PAN_DTHETA=20` · `PAN_L=7`
> `RED_DTHETA=60` · `MAO_L=3` · `MAO_DUR=15` · `PAUSA_K=2,5` — **vão exactamente como estão.**
>
> **Afiná-los ao vídeo novo torna o teste INÚTIL** — passamos a ter dois vídeos decorados em vez
> de um. O que sair, sai. **É esse o objetivo: descobrir o que é LEI e o que é AJUSTE.**

**PREVISÃO ESCRITA (13 jul, antes de ver o resultado):**

| | previsão |
|---|---|
| **LEIS do Vasco** (mão vs raquete, rede, Theta, timeline, última pancada, pausa) | **aguentam** |
| **AJUSTES do Claude** (`L_RAQUETE`, `PAD_ANTES`, `MIN_PROF`) | **partem** |
| `PAD_ANTES=1,6s` — é a **duração do ritual do serviço** | muda com a câmara |
| `SILENCIO=4s` — é **tempo de jogo**, não píxeis | o mais provável de sobreviver |

**A ÚNICA alteração permitida ao `gerar_tempo_util.py`:** os **caminhos**, o `FPS`, o `N_FRAMES`
e o `GT`. **Nunca uma regra. Nunca um limiar.**

---

## 🔊 O QUE PEDIR À CAPTURA (mais importante que o ângulo)

# **1. ÁUDIO.**
O som do **quique**, o da **parede** e o da **raquete** são **três sons diferentes** — e são
exactamente as três coisas que a imagem **não distingue**. O áudio **não precisa de profundidade**.
É o que desbloqueia o ressalto, a S8, a S9, a S10, a S14 e as regras do Vasco de 13 jul.
*(Estava nos prompts — v7.1, R15 — e nunca foi usado.)*

**2. A CÂMARA MAIS ALTA.** A do Parada4 é baixa e **corta os jogadores de baixo**: só **21,8%**
dos frames têm os 4 visíveis. Isso bloqueia a formação de serviço (S2), a inatividade dos
jogadores, e metade do M2.

**3. Resolução.** 960×540 chegou para a bola (o BlurBall aguenta). Mais é melhor, não é crítico.

---

## PASSO 1 — A BOLA  (Kaggle, GPU, ~20 min)

Notebook: **`BlurBall_thr04_KAGGLE.ipynb`** (na pasta do projeto).

1. **kaggle.com** → *Code* → *New Notebook* → *File → Import Notebook* → escolhe o ficheiro.
2. **Painel direito → Add Input → Upload** → o teu vídeo novo.
3. **Settings → Accelerator → GPU T4**.
4. Na célula do vídeo, troca o nome:
   ```python
   src = glob.glob('/kaggle/input/**/O_TEU_VIDEO*.mp4', recursive=True)
   ```
5. Corre célula a célula (**Shift+Enter**, nunca "Run All").
6. **⚠️ O threshold fica em `0.4`.** Não mexer. *(A 0.7 só 46% dos frames têm bola; a 0.4 sobem
   para 76% — e são as deteções DIFÍCEIS que interessam: serviço, remate, bola borrada.)*

**Sai:** `traj.csv` com as colunas `Frame,X,Y,Visibility,L,Theta,score`
→ descarrega e guarda em `dados_<video>/traj_frames_<video>_thr04.csv`

> 🔑 **A coluna `score` é contínua** ⇒ qualquer threshold futuro afina-se em **CPU-segundos**.
> **NUNCA MAIS correr o modelo só para mudar de threshold.**

---

## PASSO 2 — OS JOGADORES  (Colab, GPU, ~25 min)

Notebook: **`padelpro-vision/colab/colab_jogadores_padel_analytics.ipynb`**
Guia: **`GUIA_COLAB_JOGADORES.md`**

1. **Push primeiro** (`GUARDAR_TUDO.command`) — senão o Colab clona uma versão antiga do repo.
2. colab.research.google.com → separador **GitHub** → `https://github.com/Vasco-Rocha/Modelo-Padel-VRO`
   → `colab/colab_jogadores_padel_analytics.ipynb`
3. **Runtime → Change runtime type → T4 GPU**.
4. Upload do vídeo. Corre célula a célula.

**Sai:** `players_detections_<video>.json`
→ converte com: `python3 padelpro-vision/json_para_pkl.py <json> <pkl>`
→ guarda em `dados_<video>/player_boxes_<video>.pkl`

---

## PASSO 3 — A CALIBRAÇÃO DO CAMPO  (à mão — **é regra do Vasco, C1**)

> **"Campo novo = calibração nova, à mão. NÃO auto-detetar."**
> *(A auto-deteção pôs a linha de serviço longe **40 px** ao lado. Ver `BENCHMARK_CALIBRACAO_CAMPO.md`.)*

1. Abre **`calibrar_campo.html`** no browser.
2. Carrega um frame limpo do vídeo novo (sem jogadores a tapar as linhas).
3. Marca, por esta ordem: **rede (topo, fita, base)** · **linhas de serviço (perto e longe)** ·
   **fundo longe** · **junções das malhas**.
   - **C5:** 3 pontos por linha (a lente curva-as). 2 pontos herdam a curvatura.
   - **C2:** a junção da malha 2/3 **nunca se deteta** — não é linha branca. Desenha-a.
   - **C3:** a central **calcula-se** dos pontos médios. Não se marca.
   - **C4:** os extremos das linhas são os cantos. **Descarta os que tocam a borda do frame** —
     isso é o limite da imagem, não o vidro.
4. **Guarda** → `calibracao_campo.json`

---

## PASSO 4 — O GROUND-TRUTH  (à mão — **é teu, Vasco**)

1. Abre **`anotador_rallies.html`**.
2. Marca **início (serviço) → fim** de cada ponto.

> 🚨 **CONTA TODOS OS PONTOS.**
> No Parada4 faltava **um** (o 13.º, aos 289s). Passei um dia inteiro a chamar-lhe "segmento
> falso" — **era um ponto a sério**, e a precisão andou a castigar-me por **acertar**.
> **O ground-truth é a régua de tudo. Se está incompleto, TUDO o que se mede está torto.**
> Inclui os pontos que ficam **cortados pelo fim do vídeo**.

---

## PASSO 5 — VERIFICAR ANTES DE CORRER

```bash
cd padelpro-vision
python3 verificar_video_novo.py ../dados_<video>/
```

Confirma que os três ficheiros existem, têm as colunas certas, o mesmo nº de frames, e que a
calibração é coerente. **Se isto falhar, o pipeline vai dar erros misteriosos.**

---

## PASSO 6 — CORRER  (CPU, segundos)

No `gerar_tempo_util.py`, **só** estas linhas mudam:

```python
BOLA  = "../dados_<video>/traj_frames_<video>_thr04.csv"
BOXES = "../dados_<video>/player_boxes_<video>.pkl"
CAL   = "calibracao_<video>.json"
VIDEO = "../<video>.mp4"
FPS      = <do vídeo>
N_FRAMES = <do vídeo>
GT = [ ... ]   # o teu ground-truth
```

**Mais nada. Nem um limiar.**

```bash
python3 gerar_tempo_util.py --video    # e VÊ O VÍDEO. Sempre.
python3 diag_pontos.py                 # onde é que cada ponto perde
python3 ablacao.py                     # ⭐ quais regras sobreviveram e quais partiram
```

---

## PASSO 7 — LER O RESULTADO **SEM RACIONALIZAR**

**A tabela de ablação é o resultado do teste.** É ela que diz o que é lei e o que é decoração.

| se… | então |
|---|---|
| as **regras do Vasco** continuam a valer (S15, Theta, rede, S12) | ✅ **são leis. Sobrevivem à câmara.** |
| os **limiares** partem (`L_RAQUETE`, `MIN_PROF`, `PAD_ANTES`) | ✅ **era o esperado.** Re-derivar da ESTRUTURA — não afinar ao vídeo. |
| **uma regra do Vasco parte** | 🔴 **é a descoberta mais valiosa do teste.** Não a "consertar" — **perceber PORQUÊ.** |

> ⚠️ **A tentação vai ser afinar os números até os resultados ficarem bonitos. NÃO FAZER.**
> Um número afinado a dois vídeos continua a ser um número afinado. **O resultado feio é o dado.**

---

## As 3 lições que este teste existe para não repetir

1. 🚨 **Desconfiar do GROUND-TRUTH.** Um falso positivo **bem-comportado** é **verdade que falta
   ao GT**. Mostrar o clip ao Vasco **antes** de o combater.
2. 🕳️ **Ler o CÓDIGO, não o mapa.** A S12 e a S8 estavam marcadas ✅ e **não corriam**.
3. 🧪 **TESTAR, não raciocinar.** Descartei 8 regras com um raciocínio bonito. A que ia deitar
   fora resolveu o maior problema que tinha.

> **Faixa fina = observável. Área grande = ambígua.**
> Serve para prever se uma ideia tem hipótese **antes** de a testar.
