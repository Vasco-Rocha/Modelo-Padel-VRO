# Afinar o tempo útil — guia completo (fazer sozinho, sem GPU)

Alvo: **~12 rallies, ~132s (45%)** — igual à referência (corte manual 132.2s).
Última corrida: 15 rallies, 171.3s (61%) → demasiado alto. Baixar com os botões abaixo.

## PASSO 0 — Guardar as deteções (uma vez, se ainda não fizeste)
As deteções (bola+jogadores) estão em memória. Guarda-as para nunca mais precisares de GPU:
```python
import pickle
pickle.dump({'ball_xy':ball_xy,'player_boxes':player_boxes,'fps':fps,'audio_hits':audio_hits,'N':N},
            open('/content/drive/MyDrive/PadelPro_Vision/parada4_deteccoes.pkl','wb')); print('ok')
```
Numa sessão nova sem GPU, em vez das células 1-4 corres:
```python
import pickle
d=pickle.load(open('/content/drive/MyDrive/PadelPro_Vision/parada4_deteccoes.pkl','rb'))
ball_xy,player_boxes,fps,audio_hits,N = d['ball_xy'],d['player_boxes'],d['fps'],d['audio_hits'],d['N']
SERVE_ZONE=[(335,421),(54,140)]   # os valores que calibraste na celula 4b
```

## PASSO 1 — Puxar o código novo (só na 1ª vez de cada sessão)
```python
!cd /content/Modelo-Padel-VRO && git pull -q
import importlib, padelpro.modules.rallies_bola as rb; importlib.reload(rb)
from padelpro.modules.rallies_bola import segmentar_rallies_bola
```

## PASSO 2 — Correr a segmentação (esta é a linha que afinas)
```python
res=segmentar_rallies_bola(ball_xy, player_boxes, fps, audio_hits_s=audio_hits, serve_zone_y=SERVE_ZONE,
                           gap_max_s=4.0, min_rally_s=1.5, margem_fim_s=2.0)
print(f"{res['n_rallies']} rallies | {res['tempo_util_s']}s ({round(100*res['tempo_util_s']/(N/fps))}%)")
```
Corre em ~1 segundo. Muda os 3 números, corre outra vez, repete.

## OS 3 BOTÕES — o que cada um faz e para onde mexer

### `gap_max_s` (o principal para o TEMPO)
Quantos segundos de bola ausente ainda contam como o MESMO ponto (se não se detetar serviço no meio).
- **Maior** (ex. 8) → junta mais → rallies mais longos, conta mais tempo morto, MENOS rallies, tempo SOBE.
- **Menor** (ex. 3) → separa mais → menos tempo morto, tempo DESCE, mais rallies.
- Agora o tempo está alto (171s) → **começa em 4.0, se ainda alto tenta 3.0**.

### `margem_fim_s` (afina o FIM de cada ponto)
Segundos que se adicionam depois da última pancada detetada (o detetor perde os últimos toques).
- **Maior** (3) → cada ponto fica mais longo, tempo SOBE.
- **Menor** (1.5) → fim mais apertado, tempo DESCE.
- Com muitos rallies, a margem multiplica-se → se o tempo estiver alto, usa **2.0 ou 1.5**.

### `min_rally_s` (limpa FRAGMENTOS)
Descarta rallies mais curtos que isto.
- **Maior** (1.5-2.0) → menos fragmentos falsos, MENOS rallies.
- Se vires rallies de 1-2s na lista → sobe para **2.0**.

## COMO AFINAR (receita)
1. **Tempo demasiado ALTO** (como agora, 171 > 132): baixa `gap_max_s` (4 → 3), depois `margem_fim_s` (2 → 1.5).
2. **Tempo demasiado BAIXO** (< 120): sobe `margem_fim_s` (2 → 3) ou `gap_max_s` (3 → 4).
3. **Rallies a MAIS** (> 13): sobe `min_rally_s` (1.5 → 2.0). Se continuar, é o detetor de serviço a disparar demais → aí a solução é treiná-lo (M3), não os botões.
4. **Rallies a MENOS** (< 11): baixa `gap_max_s` está a colar pontos — sobe um pouco, ou baixa `min_rally_s`.

Objetivo final: **11-13 rallies e 125-135s (43-46%)**, sem rallies de ~30s nem fragmentos de ~1s.

## Combinações para experimentar (por ordem)
```
gap_max_s=4.0, min_rally_s=1.5, margem_fim_s=2.0     <- começa aqui
gap_max_s=3.0, min_rally_s=1.5, margem_fim_s=2.0     <- se ainda alto
gap_max_s=3.0, min_rally_s=2.0, margem_fim_s=1.5     <- se ainda alto / muitos rallies
gap_max_s=4.0, min_rally_s=1.5, margem_fim_s=2.5     <- se ficar curto
```

## PASSO 3 — Gerar o vídeo (quando o número estiver bom)
Corre a célula 6 do notebook (mas primeiro atualiza a chamada da célula 5 para os valores que escolheste, para o vídeo usar a mesma segmentação). Gera `TempoUtil_pipeline.mp4` na Drive.

## Quando estiver bom
Fecha-se o M1. O passo seguinte é o M3 (detetor de serviço/pancadas treinado do PadelTracker100),
que resolve a raiz (serviço fiável) e melhora tudo isto sem afinação manual.
