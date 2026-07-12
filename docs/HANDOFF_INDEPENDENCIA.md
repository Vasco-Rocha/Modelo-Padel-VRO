# Handoff — Conversa "Independência" (garantir que não perdemos o trabalho)

**Cola isto no início da conversa nova.** É uma tarefa fechada, de ~30 minutos, sem GPU.

---

## O PROBLEMA

O PadelPro Vision está construído **por cima do trabalho do João Silva**, e depende dele em dois
pontos que **não estão sob o nosso controlo**:

| dependência | onde vive | se desaparecer |
|---|---|---|
| **Código** — `padel_analytics` (os detetores) | `github.com/Joao-M-Silva/padel_analytics` | o `git clone` falha; ficamos sem detetor |
| **Pesos** — `yolov8m.pt` (o modelo treinado) | uma **pasta da Google Drive do João** | 🔴 **perdemos o modelo. Não se recupera.** |

**O risco pior são os pesos.** Um repo de código, se desaparecer, ainda se recria com trabalho.
Um modelo treinado, se desaparecer a Drive, **acabou** — não temos os dados de treino dele.

Hoje, se o João apagar a Drive, o projeto **para**.

---

## O OBJETIVO DESTA CONVERSA

Ficar independente das duas. Três passos, por ordem de importância.

### 1. 🔴 PESOS — copiar para a Drive do Vasco (o mais urgente)

A pasta do João:
`https://drive.google.com/drive/folders/1joO7w1Am7B418SIqGBq90YipQl81FMzh`

Ficheiros que nos interessam (pelo menos o primeiro):
- **`yolov8m.pt`** — deteção de jogadores ← **o crítico, é o que usamos**
- `TrackNet_best.pt`, `InpaintNet_best.pt` — deteção de bola (já não usamos; o BlurBall substituiu)
- `best.pt` (court keypoints, players keypoints) — não usamos

**Como:** abrir a pasta na Drive → selecionar → *Fazer uma cópia* / descarregar e voltar a carregar
numa pasta própria (ex.: `MyDrive/PadelPro/pesos/`).

**Já está meio-feito:** o notebook `colab/colab_jogadores_padel_analytics.ipynb` tem, no topo:
```python
GUARDAR_NA_DRIVE = True
DRIVE_PESOS = '/content/drive/MyDrive/PadelPro/pesos'
```
Na 1.ª corrida vai à Drive do João, traz o `yolov8m.pt` e **guarda uma cópia na Drive do Vasco**.
Nas seguintes usa a cópia. **Confirmar que isto correu** e que o ficheiro lá está.

Guardar também uma cópia **local**, na pasta do projeto ou num disco. Uma Drive também se perde.

### 2. CÓDIGO — fork do repo do João

No GitHub: abrir `github.com/Joao-M-Silva/padel_analytics` → botão **Fork** → fica em
`github.com/Vasco-Rocha/padel_analytics`.

Depois, no notebook, trocar:
```python
REPO_URL = 'https://github.com/Vasco-Rocha/padel_analytics.git'
```
(A linha já lá está, comentada.)

O repo dele tem `LICENSE` e `CONTRIBUTING.md` — o fork é legítimo e é para isso que serve.

### 3. VERSÕES — congelar as dependências

O `requirements.txt` do João **não fixa versões**. O Colab instala sempre as mais recentes, e o código
dele parte. Já aconteceu duas vezes hoje:
- `ModuleNotFoundError: No module named 'parse'` (faltava no pip install)
- `PolygonZone.__init__() got an unexpected keyword argument 'frame_resolution_wh'`
  (o `supervision` novo mudou a API)

**No fork, fixar as versões** que sabemos funcionar (`supervision==X`, `ultralytics==Y`, etc.).
Descobrir as versões atuais no Colab com `!pip freeze | grep -E "supervision|ultralytics"`.

---

## ETIQUETA

Vale a pena o Vasco dizer ao João Silva que ficou com uma cópia dos pesos e fez fork do repo.
Não por obrigação legal — por educação, já que o projeto está construído em cima do trabalho dele.

---

## CONTEXTO MÍNIMO DO PROJETO

- Análise de vídeo de padel. Repo nosso: `padelpro-vision` → `github.com/Vasco-Rocha/Modelo-Padel-VRO`.
- Consumimos os **detetores** do `padel_analytics` (João Silva); as **regras** são nossas.
- O Vasco **não é developer**: passo a passo, um de cada vez, confirmar com screenshots.
- **Push:** o Vasco usa o `PUSH.command` (duplo clique) ou o Claude Code. O sandbox do Cowork não tem
  credenciais do GitHub.

## QUANDO ACABAR

Voltar à conversa **Centro de Decisões** e dizer:
1. Os pesos estão na Drive do Vasco (e numa cópia local)?
2. O fork está feito e o `REPO_URL` trocado?
3. As versões estão fixadas?
