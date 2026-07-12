# Ground-truth — rallies reais do Parada 4 (anotados pelo Vasco, jul 2026)

Anotado com o anotador_rallies (serviço → fim do ponto). Esta é a VERDADE para avaliar o pipeline.
⚠️ **13 jul 2026 — ACRESCENTADO O 13.º RALLY.** O Vasco confirmou: *"é serviço, começa onde está
destacado e acaba pelo fim do vídeo"*. **FALTAVA.** O pipeline encontrou-o sozinho e eu chamei-lhe
"segmento falso" durante um dia inteiro. A precisão estava a castigar-me por **acertar**.
👉 **O ground-truth é a régua de tudo. Se está incompleto, TUDO o que se mede está torto.**

Jogo real = **119,6s** em **13 rallies** (o corte manual WhatsApp tinha 132.2s = +15s de margens do editor).

| # | início | fim | dur |
|---|--------|-----|-----|
| 1 | 00:38.0 | 00:41.5 | 3.5s |
| 2 | 00:46.8 | 01:07.5 | 20.7s |
| 3 | 01:17.6 | 01:25.5 | 7.9s |
| 4 | 01:35.9 | 01:51.1 | 15.2s |
| 5 | 02:02.4 | 02:15.9 | 13.5s |
| 6 | 02:37.9 | 02:49.4 | 11.5s |
| 7 | 02:58.1 | 03:06.5 | 8.4s |
| 8 | 03:17.0 | 03:22.1 | 5.1s |
| 9 | 03:30.5 | 03:36.3 | 5.8s |
| 10 | 03:49.9 | 03:57.3 | 7.4s |
| 11 | 04:09.6 | 04:15.0 | 5.4s |
| 12 | 04:23.8 | 04:36.4 | 12.6s |
| **13** | **04:49.1** | **04:51.7** | **2.6s** |

## Avaliação do pipeline (versão 16 rallies) contra esta verdade
- Recall 72% (84 de 117s de jogo real apanhados), Precisão 63% (dos 133s, só 84 são jogo).
- Erros: V2 partido em 3 + começa 4s tarde; V4 partido em 2 + acaba 7.1s cedo; V6/V8/V9 começam 2-3s tarde
  (serviço perdido); V10/V12 acabam ~2s cedo; V11 partido em 2; P16 (284.5-291.6) = rally FALSO.
- Raiz: recall da bola/serviço (~15% a 540p). Heurística apara bordas mas nao inventa deteções. Via A (re-treinar
  bola em frames Court-Master) + M3 (detetor de serviço) sobem o recall.

## Como usar (avaliação automática de futuras corridas)
GT em segundos:
```python
GT=[(38.0,41.5),(46.8,67.5),(77.6,85.5),(95.9,111.1),(122.4,135.9),(157.9,169.4),
    (178.1,186.5),(197.0,202.1),(210.5,216.3),(229.9,237.3),(249.6,255.0),(263.8,276.4),
    (289.1,291.7)]   # 13.o — acrescentado 13 jul. Fica CORTADO pelo fim do video.
```
Comparar os rallies do pipeline com GT por sobreposição → recall (jogo apanhado/117s), precisão (jogo/total do pipeline),
e por rally: partido? começa tarde? acaba cedo? falso?
