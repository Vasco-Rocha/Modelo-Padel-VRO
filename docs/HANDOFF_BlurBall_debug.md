# Handoff — BlurBall out-of-box (Kaggle): desbloquear o número

**Para:** conversa Opus da build do BlurBall.
**De:** conversa de decisões (centro do projeto).
**Objetivo único:** obter **UM número** — a % de deteção da bola DENTRO dos 12 rallies reais (proxy de recall), para comparar com os 67% do YOLO (`best.pt`). Esse número decide se treinamos o BlurBall.

---

## Contexto (porque isto importa)
- Problema-raiz do projeto: recall da bola ~67-72% (perde bola rápida/borrada em serviços e remates).
- **Via A (fine-tune YOLO) está FECHADA — falhou.** `best_v2` ficou pior que `best.pt` (recall 57% vs 67%, precisão 39% vs 73%, 104s de falsos). Um detetor de-um-frame não resolve o borrão.
- **BlurBall (detetor temporal, WASB + tratamento do borrão) é a aposta a sério.** Repo: github.com/cogsys-tuebingen/blurball (MIT). Está a correr out-of-box (pré-treinado, sem treinar) no `Parada4.mp4` no Kaggle.
- Estamos no **Passo 1**: só validar o out-of-box. NÃO treinar ainda — o número decide.

## Estado atual (onde encalhou)
Notebook `BlurBall_Passo1_Teste.ipynb` no Kaggle. Célula 6 correu:
```
!python main.py --config-name=inference_blurball \
   detector.model_path="{BLURBALL_W}" +input_vid="{VIDEO_PATH}" \
   detector.step=1 detector.postprocessor.score_threshold=0.7
```
Log: `Finished preprocess_video` → `Starting********` (arrancou a inferência).

**Dois bloqueios:**

### Bloqueio 1 — o output não aparece onde o notebook procura
```
traj.csv: /kaggle/working/frames_Parada4/traj.csv -> False
overlay : /kaggle/working/frames.mp4          -> False
```
Hipóteses: (a) a inferência ainda não tinha acabado quando se correu a célula de verificação; (b) o BlurBall escreveu noutra pasta/nome; (c) a inferência morreu a meio (ver fim do log da célula 6).

**Diagnóstico a correr:**
```python
!find /kaggle/working -name "*.csv" 2>/dev/null
!find /kaggle/working -iname "*traj*" -o -iname "*.mp4" 2>/dev/null
!ls -R /kaggle/working/frames_Parada4 2>/dev/null | head -40
# ver as ultimas linhas do log da inferencia (erro silencioso?)
```
Ajustar `TRAJ`/`OVERLAY` para o caminho real que o BlurBall usou (o config do `inference_blurball` define o output dir — confirmar no `conf/` do repo).

### Bloqueio 2 — `import pandas` rebenta com `ValueError`
A instalação do BlurBall provavelmente fixou uma versão de numpy incompatível com o pandas do Kaggle (mismatch de binário). Duas saídas:
1. **Restart kernel** (Run → Restart) depois dos installs, para o ambiente recarregar coerente.
2. Melhor ainda: **desacoplar o scoring do ambiente do BlurBall.** O `traj.csv` é só um CSV — não precisa do ambiente do BlurBall para ser lido. Depois de gerar o `traj.csv`, calcular o recall num **notebook/kernel limpo** (só `pandas`), ou fixar `!pip install -q "numpy==1.26.4" pandas` e restart.

## O cálculo do número (quando o traj.csv existir)
Ground-truth (12 rallies reais, `ground_truth_parada4.md`, jogo real = 117s):
```python
import pandas as pd, numpy as np, cv2
df = pd.read_csv(TRAJ); vis = df['Visibility'].values; N = len(df)
fps = cv2.VideoCapture(VIDEO_PATH).get(cv2.CAP_PROP_FPS) or 29.97
GT = [(1,38.0,41.5),(2,46.8,67.5),(3,77.6,85.5),(4,95.9,111.1),(5,122.4,135.9),
      (6,157.9,169.4),(7,178.1,186.5),(8,197.0,202.1),(9,210.5,216.3),
      (10,229.9,237.3),(11,249.6,255.0),(12,263.8,276.4)]
inplay = np.zeros(N, bool)
for k,a,b in GT:
    f0,f1 = int(a*fps), int(b*fps)
    if f0 >= N: continue
    inplay[f0:min(N-1,f1)+1] = True
print("deteção global: %.1f%%" % (vis.mean()*100))
print(">>> Deteção DENTRO dos rallies: %.1f%%   (YOLO best.pt = 67%%)" % (vis[inplay].mean()*100))
```
**Cuidado com o vídeo usado:** se correu o **clip de 120s** (e não o Parada4 completo, 292s), só os rallies 1-4 do GT ficam dentro do alcance — filtra o GT em conformidade, senão o número vem artificialmente baixo. Confirmar a duração de `VIDEO_PATH` (N/fps).

## Como ler o resultado (a decisão)
- **`score_threshold=0.7` é alto para um domínio novo.** Se o recall vier baixo, NÃO concluir que falhou — repetir a inferência com `score_threshold=0.4` e `0.5` (lição do `best_v2`: baixar limiar mudou tudo). Comparar.
- Se a deteção dentro dos rallies **subir claramente acima de 67-72%** (e o `frames.mp4` mostrar a bola apanhada nos serviços/remates) → **salto temporal validado** → avançar para Passo 2 (fine-tune do BlurBall com os frames Court-Master) e depois ligar `traj.csv` → `rallies_bola.py` (regras v9 intactas) e medir contra os 117s.
- Se ficar igual/pior mesmo com limiar baixo → reportar de volta; repensa-se.

## O que trazer de volta à conversa de decisões
Só isto:
1. Deteção dentro dos rallies (a 0.7, e a 0.4/0.5 se preciso).
2. Uma impressão do `frames.mp4`: apanha a bola nos serviços/remates que o YOLO perdia?

Nada mais. A decisão (treinar BlurBall ou não) fica para a conversa de decisões.
