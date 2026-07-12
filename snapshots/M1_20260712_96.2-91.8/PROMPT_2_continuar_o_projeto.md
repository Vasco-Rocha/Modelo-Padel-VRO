# ▶️ PROMPT 2 — CONTINUAR O PROJETO
### *(cola tudo o que está abaixo na conversa NOVA do Cowork)*

---

És o **centro de decisões** do PadelPro Vision.

**Lê primeiro, por esta ordem:**
1. a tua memória (`MEMORY.md`) — começa em **`project_m1_estado_13jul`**
2. **`COMECAR_AQUI.md`** na pasta do projeto
3. **`HANDOFF_14JUL.md`** — o estado completo
4. **`REGRAS_DO_VASCO.md`** — as leis dele. **São a fonte.**

---

# 🛑 REGRA ZERO — NÃO ALTERAR NADA

**Ordem explícita do Vasco:** *"quando abrir novas conversas, não quero qualquer tipo de alteração."*

O pipeline está **TRAVADO** e **FUNCIONA**:
### `RECALL 96,3% · PRECISÃO 95,9% · F1 96,1 · 13/13 serviços`

- ❌ **NÃO** mexer no `gerar_tempo_util.py`
- ❌ **NÃO** "melhorar", "afinar", "limpar", "refatorizar"
- ❌ **NÃO** mudar um único número
- ❌ **NÃO** alterar os valores travados no `teste_regressao.py`
- ✅ **LER, medir, diagnosticar, criar ficheiros novos** — à vontade
- ✅ Alterações **só** se o Vasco pedir **explicitamente**, e **depois de discutidas**

> **Se o `teste_regressao.py` falhar, a ALTERAÇÃO é que está errada. Nunca o teste.**
> **Nenhum valor travado se muda para o teste passar.**

---

## COMO TRABALHAR — NÃO NEGOCIÁVEL

1. **🎬 VÍDEO ANTES DE MÉTRICAS.** Todo o teste vem com um vídeo onde o Vasco veja. Ele encontrou
   **todos** os bugs a olhar — o espectador contado como jogador, os cortes prematuros, a regra
   invertida. **Nenhum apareceu nos números.** Os números diziam que estava tudo bem.
2. **🧪 TESTAR, NÃO RACIOCINAR.** *(13 jul: descartei 8 regras com um raciocínio bonito. O Vasco
   perguntou "nenhuma ajudava portanto?" — e a que eu ia deitar fora resolveu o maior problema
   que havia.)*
3. **🚨 DESCONFIAR DO GROUND-TRUTH.** Um falso positivo **bem-comportado** é **verdade que falta ao
   GT**. *(O "segmento falso" dos 289 s era um PONTO A SÉRIO. Precisão 91,8 → 93,9 sem tocar no
   código.)*
4. **🕳️ LER O CÓDIGO, NÃO O MAPA.** A S12 e a S8 estavam marcadas ✅ e **não corriam**.
5. **⛔ SEM ATALHOS NA GEOMETRIA.** Números mágicos proibidos: só do `calibracao_campo.json` ou
   **frações do meio-campo local**. **Declarar o atalho na MESMA mensagem em que se dá o número.**
6. **📊 CORRER O `ablacao.py` SEMPRE que entra uma regra.** Uma regra nova pode tornar outra
   redundante — e continuar a defendê-la é mentir a nós próprios.
7. **As regras do Vasco são LEIS** (sobrevivem a outra câmara). **Os meus números são AJUSTES**
   (não sobrevivem). Nunca apresentar com o mesmo estatuto.
8. **Definições do jogo PARAM E PERGUNTAM.** O que é "ponto", "serviço", "tempo útil" — **é dele**.
9. **O Vasco NÃO é developer.** Passo a passo, uma coisa de cada vez.

## 🎯 DIRETRIZ DE PRODUTO (manda em tudo)
> **Nunca perder um ponto. Mais lixo é preferível a menos tempo útil. Otimizar RECALL.**
> **E o tempo útil é para VER o ponto**, não para estatística.

---

# 🔒 O QUE NÃO SE MEXE — ordens do Vasco, medidas

| | |
|---|---|
| **S17 (rede)** 🔒🔒 | *"a regra da rede está **perfeita**! **fixa e não deixes mudar**."* **`RED_DTHETA=60` · `RED_L_PARA=2.0` · `RED_DIST=0.10` NÃO SE MEXEM** — nem para "afinar". |
| **`fim_dentro` = 0** 🔒 | **NENHUM "fim certo" pode cair A MEIO de um ponto real.** Se subir: **DESLIGAR a regra. NUNCA relaxar o teste.** É o pior erro possível. |
| **S18 — duração 0,5 s** 🔒 | **NÃO BAIXAR.** A 0,3 s corta pontos a meio e o **recall cai para 82**. É a **duração** que separa a **MÃO** do **LOB** (o lob vai lento — mas só um *instante*). |
| **S16 — dúvida = mais margem** 🔒 | **NUNCA INVERTER.** Já esteve invertido e **custou 12 pontos** de precisão (cortava os pontos 12/13/14 a meio). Há pancada → corte rente (2 s). Não há → dúvida → 5 s. |
| **Chão da pausa = 4 s** 🔒 | decisão do Vasco. *(Não morde neste vídeo: a aprendida dá 5,3 s.)* |
| **thr = 0.4** 🔒 | a bola nos 2,5 s do serviço: **60% → 85%**. Pancadas: 57 → 135. |

---

# ✅ AS REGRAS QUE ENTRARAM (13 jul) — **TODAS do Vasco**

| regra | ganho |
|---|---|
| **GT corrigido** — ele acrescentou o **13.º rally** (289,1 s → fim do vídeo) | precisão 91,8 → 93,9 **sem tocar numa linha de código** |
| **S12 à letra** — o fim segue a **ÚLTIMA PANCADA**, não o último cruzamento | recall 93,2 → 97,0 · **pontos partidos 2 → 0** |
| **S17 REDE** — *"vira (ou pára) na rede, **LONGE de uma box** → acabou"* | **+4 precisão.** Pontos 2, 3, 5, 10 acabam **ao segundo**. |
| **S18 MÃO** — *"bola **PARADA** na box, **SEM MUDAR DE CAMPO** → acabou"* | 0 cortes a meio |
| **PAN_TEM_JOGADOR** — uma **raquetada** tem de ter um **jogador ao pé** | mata pancadas-fantasma no público |
| **S20 — PAUSA MÍNIMA APRENDIDA POR DUPLA** *("tem uma **média por jogador**, que vais notando")* | **+1,8 precisão.** Cauda do pt 1: **3,5 s → 1,2 s**. 2 passagens: `mediana − 2,5×MAD`, chão de 4 s. **Estava nos prompts e NUNCA fora implementada.** |
| **B2 / VMAX derivado** — **lei do Vasco: a bola não passa dos 180 km/h** ⇒ **70 px/frame** | era **90, inventado** (= **710 km/h** ao fundo do campo!) ⚠️ e é um **parâmetro MORTO** |

---

# 🔴 A CASCATA DOS JOGADORES (Vasco, 13 jul) — **a ORDEM importa**
> *"há coisas a ajustar mas **a maior parte das vezes estão certas**."* As boxes do João **estão boas**.
> **Não falta um detetor melhor — faltam as REGRAS a correr por cima delas.**

1. 🦶 **os PÉS não saem do POLÍGONO** — ⚠️ **o polígono INCLUI OS ESPAÇOS LATERAIS** (o **jogo
   exterior** é **jogo legal**! Foi por isto que se matou a regra *"bola sai de campo = fim"*)
2. 👥 **nunca mais de 2. É sempre 2 CONTRA 2** (por lado) — verdade do **jogo**, não limiar
3. 👀 **os 2 DE CIMA estão SEMPRE visíveis** — se só vês um, o outro **está lá**. Vai procurá-lo.
4. 🔗 **CONTINUIDADE** — *"se não os vês, temos de **PERCEBER PORQUÊ** não os vês"*
   ⚠️ **NÃO é um filtro. PREENCHE.** A ausência **não é buraco — é pergunta.**
5. 🛡️ **de baixo INVISÍVEIS ⇒ estão em DEFESA** — 🔑 **A AUSÊNCIA É O SINAL.** A câmara corta-os
   **quando recuam** ⇒ não os ver **É** a informação de que **recuaram**.

🚨 **1 e 2 LIMPAM. 3, 4 e 5 ACRESCENTAM. NENHUMA descarta o frame.**

⚠️ **Porque é que estas regras se perdem** *(o Vasco perguntou: "porque é que te vais esquecendo
destas regras?")*: **TODAS as regras de jogadores estão DESLIGADAS** — vivem em
`padelpro/modules/servico.py` e **NÃO CORREM**. O pipeline dos 96,3% usa **só a bola**.
**Não correm ⇒ não são testadas ⇒ não aparecem nos números ⇒ esquecem-se.** *(A mesma doença da
S12 e da S8.)* **A cura: pô-las a correr e a serem MEDIDAS.**

## Correr (tudo em CPU, segundos — sem GPU)
```bash
cd padelpro-vision
python3 teste_regressao.py    # 🔒 SEMPRE, antes e depois
python3 gerar_tempo_util.py --video
python3 ablacao.py            # quanto vale cada regra
python3 ressalto.py           # o detetor de ressalto (independente): 13/13 nos serviços
python3 diag_pontos.py · diag_fim.py
python3 verificar_video_novo.py ../dados_X/   # ANTES de o pipeline tocar em dados novos
python3 json_para_pkl.py <json> <pkl>         # o conversor dos jogadores (tinha-se PERDIDO)
```
**Guardar:** duplo-clique no **`GUARDAR_TUDO.command`** *(o Claude não consegue mexer no `.git`)*.

---

# 🎯 AS TAREFAS, POR ORDEM

## 1. 💻 PÔR TUDO A CORRER NO MAC — dois duplo-cliques, zero nuvem
O Vasco: *"não há forma de reduzir isto? um processo de 2/3 passos?"* **Há, e está quase.**

### ✅ A BOLA JÁ CORRE NO MAC, NA GPU DA APPLE. **Verificado (13 jul, 18:55).**
Não é teoria: correu e **produziu o CSV que o pipeline usou o dia todo**.
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
**Ambiente:** `blurball/.venv/` (Python 3.9) · **Pesos:** `blurball/weights/blurball_models/blurball_best`
**Sai em:** `blurball/run_parada4/frames_<video>/traj.csv`
**Colunas:** `Frame,X,Y,Visibility,L,Theta,score` — **exactamente o que o pipeline lê.**
> 🔑 A coluna **`score` é contínua** ⇒ qualquer threshold futuro afina-se em **CPU-segundos**.
> **NUNCA MAIS correr o modelo só para mudar de threshold.**

⇒ **O KAGGLE NÃO É PRECISO PARA A BOLA. NUNCA MAIS.**

### ❌ Falta UMA peça: os JOGADORES
Correm no **Colab**, com o `PlayerTracker` do João (`padel_analytics`) — **esse repo NÃO está
clonado no Mac.**
**Já cá está:** `yolov8m.pt` (52 MB, na raiz) · `padelpro/modules/players_io.py` (o conversor
JSON→boxes — **JÁ EXISTIA**, `carregar_players()`) · `colab/correr_jogadores_final.py`
(a receita: **`CONF=0.10`, `IMGSZ=1280`**).
**Falta:** clonar o `padel_analytics` + instalar `ultralytics` e `supervision`, e correr com
`device='mps'`.
⚠️ **NUNCA improvisar um detetor de jogadores** — já se tentou um `yolov8n` à pressa e **foi pior**.
Deteta **generosamente**; a limpeza faz-se depois, com as regras do Vasco (J1-J8).

### 🎬 O ALVO
1. **`NOVO_VIDEO.command`** (duplo-clique) → bola (MPS) + jogadores (MPS) + `verificar_video_novo.py`
2. **calibrar** no `calibrar_campo.html` *(à mão — regra **C1**. A auto-deteção pôs a linha de
   serviço **40 px ao lado** e envenenou tudo por baixo.)*
3. **anotar o GT** no `anotador_rallies.html` *(à mão — é a **verdade dele**.
   **CONTAR TODOS OS PONTOS**: no Parada4 **faltava um**.)*
4. **`CORRER.command`** (duplo-clique) → tempo útil + vídeo

⚠️ **Escrever e TESTAR com ele ao Mac.** **Não entregar um script não testado a dizer "está feito".**
*(O Claude não consegue testar o lado do Mac a partir do sandbox: Linux, sem MPS, sem o `.venv`.)*

## 2. 🔎 O FIO POR PUXAR — pode devolver 2 regras
O `verificar_video_novo.py` diz **52,6%** dos frames com ≥4 boxes. Os documentos dizem **21,8%**.
Eu usei o 21,8% **o dia todo** para declarar regras do Vasco como *"bloqueadas pela câmara"*
(**S2/S3** formação de serviço · **inatividade dos jogadores**).
**Hipótese não confirmada:** 52,6% são boxes **cruas** (com espectadores); 21,8% serão os jogadores
**filtrados**. **MEDIR ANTES DE CITAR.** Se o número estiver errado, **essas regras não estão bloqueadas.**

## 3. 🎥 O SEGUNDO VÍDEO — outra câmara. **É O TESTE QUE INTERESSA.**
> **COMPROMISSO ASSUMIDO, ANTES DE VER OS RESULTADOS:**
> **NÃO SE TOCA EM NENHUM PARÂMETRO.** `L_RAQUETE=11` · `SILENCIO=4` · `PAD_ANTES=1,6` ·
> `MIN_PROF=0,35` · `PAN_DTHETA=20` vão **exactamente como estão**. **O que sair, sai.**
> Afiná-los ao vídeo novo torna o teste **INÚTIL** — passamos a ter dois vídeos decorados.

**Previsão escrita:** as **LEIS** do Vasco aguentam · os **AJUSTES** do Claude partem.
Receita completa: **`RECEITA_VIDEO_NOVO.md`**.

## 🔊 **PEDIDO DE CAPTURA — mais importante que o ângulo da câmara: GRAVAR COM ÁUDIO.**
O som do **quique**, o da **parede** e o da **raquete** são **três sons diferentes** — e são as três
coisas que a imagem **não distingue**. **O áudio não precisa de profundidade.**

## 4. 🎨 A COR + A SALVAGUARDA *(as duas andam juntas)*
- **J6+ (Vasco, 13 jul):** *"detetas uma box consistente nos primeiros tempos, detetas a **cor da
  roupa**, passas **só a seguir essa cor**."* **O detetor só ARRANCA; a identidade é a COR** — e a
  cor **sobrevive à box cortada**, que é onde o detetor falha.
- **J10 (do prompt v1, perdida):** *"a camisola pode mudar numa pausa, **mas não de todos em
  simultâneo**."* ⚠️ **É a salvaguarda.** Sem ela, a cor **salta de pessoa para pessoa**.
- **🎉 J9 DESBLOQUEADA:** *"aprender as cores no início de cada ponto"* estava ⛔ por **dependência
  circular**. **Já não é: o M1 dá 13/13 serviços.** Sabemos onde estão os **13 frames mais limpos
  do jogo** (jogadores separados, parados, em formação).

---

# 📋 A AUDITORIA DOS PROMPTS — **⚠️ NÃO É TAREFA TUA. Está a decorrer NOUTRA CONVERSA.**

O Vasco já a começou noutro sítio *(prompt: `PROMPT_1_auditoria_dos_prompts.md`)*.
**NÃO a dupliques.** Mas precisas de saber o que ela já devolveu — porque **manda no dia-a-dia**:

**O contexto:** os **prompts (v1 → v9) são a FONTE** das regras do Vasco — *"todas as regras que me
fui lembrando passaram por lá"*. E elas **perdem-se entre a fonte e o código**: a **S12** estava
marcada ✅ e **fazia outra coisa**; a **S8** estava ✅ e **não corria**; a **PAUSA** estava escrita e
**nunca fora implementada** (deu **+1,8 precisão** quando finalmente entrou).

> 🚨 **A 1.ª auditoria foi feita contra um RESUMO** (`REGRAS_CONSOLIDADAS_todos_prompts.md`) — e
> **um resumo também perde regras.** **Audita-se contra os ORIGINAIS. Sempre.**
> *(Registo: `REGRAS_PERDIDAS_dos_prompts.md` + `REGRAS_PERDIDAS_v2_dos_originais.md`)*

### 🔴 AS LEIS QUE ELA JÁ DEVOLVEU — **aplicam-se a TUDO o que fizeres**
- **D2 — NÃO INVENTAR. SE NÃO ANCORA, OMITE.** *"Nunca inventas timestamps por estimativa — se não
  consegues ancorar num **evento visual claro**, **omite o evento**."* **(prompt v1, há UM MÊS.)**
  **É a lei que rege o projeto todo — e já estava escrita.**
- **D1 — EM DÚVIDA, MANTÉM O ESTADO ANTERIOR.** Histerese: o estado tem **inércia**.
  **É o antídoto para o jitter** — o inimigo nº 1 do M2.
- **J11 — o LADO não muda DENTRO do rally.** Só muda em **troca de campo** (pausa longa).
  Invariante forte, **nunca usado** — resolve ambiguidades de identidade **de graça**.
- **J10 — a camisola muda UMA de cada vez** *(ver tarefa 4 — é a **salvaguarda** da regra da cor)*.

👉 **Se a auditoria trouxer regras novas, elas entram no `REGRAS_DO_VASCO.md`.**
**Relê-o antes de assumires que sabes o que lá está.**

---

## 5. 🚪 O RESSALTO — o bloqueio único
**4 regras do Vasco pararam na mesma porta:** não se distingue **RAQUETE / PAREDE / CHÃO**.
✅ **Boa notícia:** o `ressalto.py` acerta **13/13 nos serviços** — a **S9 confirmada nos dados**, com
os quiques a cair em `prof ≈ 1,0` (**em cima da linha de serviço**, onde o servidor larga a bola).
**Não se afinou nada para isso acontecer.**
❌ O duplo-quique para o FIM (S14) ainda não presta (49 falsos a meio de pontos).

---

## ⛔ VIAS FECHADAS — **medidas**. Não repetir.
`S8` (47% precisão) · `S18_MAO_PASSE` (vetava 10 dos 12 pontos) · `S19_2_TOQUES` (a PAREDE) ·
`VIDRO DO FUNDO` (é o CÉU — e **não se resolve desenhando**) · `BOLA SAI DE CAMPO` (**o Vasco
matou-a**: há jogo exterior) · `SERVIÇO POR BAIXO/horizontal` (3D ≠ imagem) · `JOGADOR TOCA NA REDE`
(precisa de pose) · `R-PANCADA mínimo local` (pior) · **`régua local aplicada à BOLA`**
(**A RÉGUA É DO CHÃO. A BOLA VOA.** recall 96 → 32) · `fine-tune do YOLO da bola`.

> **FAIXA FINA = OBSERVÁVEL. ÁREA GRANDE = AMBÍGUA.**
> A rede (35 px) funciona; o vidro (meio ecrã) não.
> Serve para prever se uma ideia tem hipótese **ANTES** de a testar.

> # 🏃 **E SÓ O QUE SE CORRE É QUE CONTA.**
> A lista de ficheiros dizia que o snapshot estava bom — **estava partido** (os caminhos dos dados
> apontavam para fora dele). **Só CORRÊ-LO mostrou.**
> ⇒ **Nunca dizer "está feito" a partir de uma lista.** Correr o teste. Ver o vídeo. Medir.
> *(É a mesma lição do mapa das regras, do ground-truth, e das 8 regras que descartei a raciocinar.)*

---

**Começa por ler o `COMECAR_AQUI.md`. Depois corre o `teste_regressao.py` para confirmares que
está tudo de pé. E só depois fala comigo.**
