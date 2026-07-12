# Próximos passos — v9 no Gemini (handoff)

Estado atual: o **v9 (PROMPT 1 / tempo útil) já funciona** no Colab (`colab_gemini_v9_test.ipynb`),
testado num clip de 90s do Parada 4. Deu 2 rallies com análise semântica rica (equipas por cor,
serviço vs rally, quem ganhou e com que pancada).

## Regras que descobrimos (importante, não esquecer)
- **SDK novo obrigatório:** a lib antiga `google-generativeai` NÃO aceita as chaves novas (começam por `AQ.`).
  Usa sempre `from google import genai` → `client = genai.Client(api_key=API_KEY)`.
- **Modelo:** `gemini-2.0-flash` dá erro de quota (limit 0 no grátis na UE). Usa **`gemini-2.5-flash`**.
- **Segurança:** a chave apareceu em screenshots. Vai a aistudio.google.com/apikey e **regenera-a** quando puderes.

---

## ⚠️ CORREÇÃO IMPORTANTE (feedback do Vasco): o clip que o v9 DETETOU está péssimo
Os timestamps de rally que o PROMPT_1 (v9) devolve são IMPRECISOS neste vídeo → NÃO usar o v9 para cortar.
Estratégia certa (arquitetura híbrida):
- **Cortar rallies com o MÉTODO DA BOLA** (preciso, já validado nos 132s) — os segmentos do `deteccao_rallies`.
- **Alimentar ESSES clips ao v9** (PROMPT 2 fases, PROMPT 3 pancadas) — o v9 só analisa, não corta.
Ou seja: PASSO 1 abaixo (cortar o rally2 pelos tempos do v9) serve só para VER que está mau.
Para o teste a sério do PROMPT 2, usar um rally cortado pela bola (dos segmentos do notebook da bola).

## PASSO 1 — Ver e cortar o rally (célula nova no fim)
```python
from IPython.display import Video
import subprocess
RALLY='/content/rally2.mp4'
subprocess.run(['ffmpeg','-y','-ss','69','-to','84','-i',VIDEO_PATH,
                '-c:v','libx264','-crf','23','-an',RALLY],capture_output=True)
print('rally cortado')
Video(RALLY, embed=True, width=480)
```
Confirma que começa no serviço e acaba no fim do ponto.

## PASSO 2 — Correr o PROMPT 2 (fases táticas) nesse rally  ← O PASSO MAIS IMPORTANTE
```python
f = client.files.upload(file=RALLY)
import time
while f.state.name == 'PROCESSING':
    time.sleep(3); f = client.files.get(name=f.name)
resp = client.models.generate_content(model=MODEL, contents=[PROMPT_2, f])
print(resp.text)
```
Se `PROMPT_2` não existir, corre primeiro a secção "4. Os teus prompts v9".
Avaliar: as fases DEFESA/TRANSIÇÃO/ATAQUE fazem sentido face ao que se vê no vídeo?
Se sim → a camada semântica é viável e o tempo útil passa a ser um detalhe.
Se não → é aqui que afinamos o prompt (o "câmara FRONTAL" pode precisar de mudar para "ângulo alto/elevado").

## PASSO 3 — Correr o PROMPT 3 (pancadas) no mesmo rally
```python
resp = client.models.generate_content(model=MODEL, contents=[PROMPT_3, f])
print(resp.text)
```
Isto é o módulo M3 (winner / erro forçado / não forçado). Guarda só tipo de pancada + resultado; a "emoção" é decoração.

## PASSO 4 — (opcional) Tempo útil no vídeo COMPLETO, para comparar com o ground-truth
Trocar o clip pelo vídeo inteiro e correr o PROMPT_1. Comparar:
- v9 (vídeo todo)  vs  **132s** (corte manual real)  vs  96–172s (método da bola).
Gasta mais quota; com 2.5-flash grátis deve dar 1 corrida.

---

## Fora do Gemini (quando quiseres fechar a via da bola)
- **Afinar margens do tempo útil pela bola:** já tens `padelpro-vision/colab/celula4_margens_afinadas.py`
  (margens pre=0.8/pos=1.1). Deve aterrar perto dos 132s. Gera `TempoUtil_bola_v2.mp4`.
- **Arrumar no repo:** levar o filtro de hotspots + `deteccao_rallies` para um módulo do `padelpro-vision`.
- **Commit/push:** destilação v9 (court.py, phases.py, gemini_v9.py) + notebooks novos, via Claude Code.

## Decisões já tomadas
- Fable NÃO vale a pena para este trabalho (raciocínio/debug) — manter modelo atual.
- Custo real está no Gemini (por uso); Colab é grátis. Free tier chega para testes.
- A bola é âncora; o v9 dá a noção do ponto + pancadas. Este é o rumo.
