# Mapa das regras — onde vive cada uma, e se está LIGADA

12 jul 2026. **Uma regra pode estar implementada e à mesma não correr.** É assim que se perdem.

---

## 🟢 LIGADAS — correm no `gerar_tempo_util.py` (produzem os 93,2% / 89,4%)

| regra | onde |
|---|---|
| **B8 vai-e-vem** — A→B longe, A→C perto ⇒ B é erro | `gerar_tempo_util.vai_e_vem()` |
| **B6 Theta** — direção a 2°, costura os buracos | `gerar_tempo_util.tracklets()` |
| **coerência / tracklets** — a bola do intervalo não faz trajetórias longas | `gerar_tempo_util.tracklets()` |
| **cruzamento profundo** — de fundo a fundo; roçar a fita não conta | `gerar_tempo_util.cruzamentos()` |
| **S15 mão vs raquete** — `L`: serviço 17,4 · mão 2,7 | `gerar_tempo_util.cruzamentos()` |
| **pancadas** — mudança brusca de direção com a bola a voar | `gerar_tempo_util.pancadas()` |
| **S12 fim = última pancada + margem** | `gerar_tempo_util.rallies()` |
| **S16 dúvida = mais margem; certeza = corte rente** | `gerar_tempo_util.rallies()` |
| **S13 timeline nunca recua** | `gerar_tempo_util.rallies()` |
| **C1–C5 calibração do campo** | `calibracao_campo.json` |

> ⚠️ **O pipeline que dá os 93,2% usa SÓ A BOLA.** Nem uma regra de jogadores.

---

## 🟡 IMPLEMENTADAS mas DESLIGADAS — existem, estão testadas, NÃO correm

**Risco: apodrecem. Se um dia forem precisas, ninguém se lembra que estão aqui.**

### Jogadores — `padelpro/modules/servico.py`
| regra | função |
|---|---|
| **J1 fora do campo** — os pés nunca passam do vidro | `Campo.dentro_do_campo()` |
| **J2 + J3 imóveis com salvaguarda** — dentro do campo = IMUNE | `filtrar_espectadores()` |
| **J4 2 por lado** | `dois_por_lado()` |
| **J5 continuidade** — preenche buracos (a única que ACRESCENTA informação) | `continuidade_jogadores()` |
| **J6 cor da roupa** | `filtrar_espectadores()` |
| **J7 permissão para os de baixo** — box a tocar a borda ⇒ aceita | `Campo.dentro_do_campo()` |
| **J8 pés cortados ⇒ fundo perto ⇒ DEFESA** | `Campo.zona_minima()` |
| **S3 formação lida só nos 2 de cima** | `formacao_de_cima()` |
| **ausência dos de baixo = sinal** (retiraram-se ⇒ recebem) | `estado_de_baixo()` |
| **quem serve** — 2 leituras independentes; contradição ⇒ não inventa | `quem_serve()` |
| **a régua local** — todas as tolerâncias em frações disto | `Campo.meio_campo_px()` |

### Serviço — `padelpro/modules/m3_servico.py`
| | |
|---|---|
| **S4 quadrado de serviço cruzado** — construído da calibração, **zero números à mão** | `CampoM3.prof()` + `quadrado` |
| **S5 confiança pela formação** — pontua, **não corta** | `confianca_formacao()` |

### Bola — `padelpro/modules/servico.py`
| | |
|---|---|
| **B1 objetos imóveis** | `filtrar_objetos_imoveis()` |
| **B2 continuidade da bola** | `filtrar_continuidade()` |

---

## 🔴 POR IMPLEMENTAR — regras do Vasco já dadas, ainda sem código

| | porquê importa |
|---|---|
| **S10 duplo ressalto** | o serviço é a **única** jogada com ressalto obrigatório dos **dois** lados |
| **S14 fim = 2 ressaltos sem raquete** | o fim **verdadeiro** do ponto |
| **S9 a sequência** — mão → chão → raquete → quadrado cruzado | **sem ressalto no quadrado NÃO HÁ SERVIÇO** |
| **S17 bola na rede → fim certo**, corte a 0,5 s | não há dúvida a gerir |
| **S18 mão/corpo na bola → fim** (postura corporal) | as boxes mudam de forma quando alguém se baixa |
| **S6 alternância** — pontua, não corta | ponto de ouro e tie-break são exceções legítimas |
| **B3 velocidade por 2 frames** · **B4 estados da bola** · **B5 cima vs baixo** | por formalizar |
| **B9 não inventar perto dos cegos** | ausência é ausência (ao contrário dos jogadores) |
| **J9 cor reiniciada por ponto** | ⛔ bloqueada: precisa de saber onde começa o ponto — que é o que o M1 procura |

**S10 + S14 são o bloqueio único.** Desbloqueiam o início E o fim do ponto.

---

## ⛔ VIAS FECHADAS — não repetir

| | |
|---|---|
| **fine-tune do YOLO da bola** | `best_v2` ficou **pior** que o `best.pt` (57/39 vs 67/73) |
| **cross-ratio / inferência métrica de linhas** | inválida nesta lente (distorção de barril, −7% a +12%) |
| **thr=0.4 "para o tempo útil"** | não faz falta (a 0.7 não se parte nenhum rally). **Mas FAZ falta às pancadas e ao serviço** — 57 → 135 pancadas |
| **formação como FILTRO do serviço** | corta recall de 11/12 para 7/12. **Pontua, não corta** |
| **`L` máximo do tracklet** para salvar o balão | não resolveu (recall igual, precisão pior) |

---

## Módulos antigos, não auditados hoje
`active_time.py` · `audio_pancadas.py` · `phases.py` · `rallies_bola.py` · `shots.py` ·
`blurball_io.py` · `players_io.py`
**Ver o que ainda vale antes de reescrever seja o que for.**
