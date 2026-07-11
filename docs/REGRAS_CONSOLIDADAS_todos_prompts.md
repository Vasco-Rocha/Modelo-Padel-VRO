# Regras consolidadas — todos os prompts (v1 → v9) + código

Fonte única. Reúne TODAS as regras dos prompts de análise de padel, por tema, marcando a evolução entre versões e o que já está traduzido para código. Câmara fixa Court-Master, 540p, vista do vidro de fundo.

Versões: v1 (`prompt_gemini_analise_padel.md`), v3 (`..._v3.md`), v7.1, v7.7, v8.0, v9 MASTER (`prompt_padel_v9_MASTER.md`), híbrido (`prompt_modelo_hibrido_v9.md`), código (`REGRAS_BOLA_PARA_CODIGO.md`).

---

## 0. GEOMETRIA DO CAMPO (evolução das zonas)

- **v1 (6 zonas finas):** ML1, ML2 (rede), ML3 (até linha serviço), VL1, VL2, VF1–VF5 (fundo). Fronteira ATA/TRA/DEF = linha de serviço + malhas.
- **v3 (3 zonas simples):** REDE (2 primeiras malhas), MEIO (3ª malha→linha serviço), FUNDO (linha serviço→vidro fundo).
- **v7.1 (percentagens):** REDE ~15% topo · MEIO ~15–60% · FUNDO ~60–100% da altura visível. Ancorar em marcas físicas, não em pixels absolutos.
- **v7.7/v8 (marcas físicas):** DEFESA=atrás da linha de serviço · TRANSIÇÃO=entre linha serviço e junção Parede/VL1 · ATAQUE=à frente da junção Parede/VL1.
- **v9 (duas boxes):** posição = **aresta inferior da box** (contacto com solo). DEFESA=ambas atrás da linha serviço; ATAQUE=ambas à frente da interceção malha 3/2; TRANSIÇÃO=tudo o resto (estado-resíduo). Anti-jitter: só conta se cruza CLARAMENTE a marca.

**Regra transversal:** posição de um jogador = base do bounding box (pés), nunca cabeça/tronco/raquete. Em dúvida de fase → TRANSIÇÃO. DEFESA→ATAQUE sem passar por TRANSIÇÃO é proibido (exceção: transição rápida demais para captar).

---

## 1. MÓDULO 1 — TEMPO ÚTIL ("O Batedor") ⭐ [prioridade atual]

Objetivo: isolar rallies (cortar pausas), vídeo COMPLETO. Ignorar tática/pancadas.

### Início do ponto (SERVIÇO / "Set")
- Todo o rally começa num **serviço**. Margem do clip: 1–2s antes do impacto.
- Gatilho visual (v7.1): os 4 jogadores em posição estática inicial; o servidor **atira a bola ao chão e levanta a raquete**.
- Versão-código (R1): a bola fica **colada à box do servidor** uns frames e depois **afasta-se** — esse afastamento = bola em jogo (mais robusto que detetar o toss).

### Fim do ponto (várias condições — QUALQUER uma fecha)
- **Regra dos 6s (v1/v3/v9, principal):** a última pancada só é fim depois de **6s sem nova pancada**. Nos 6s: se houver pancada que **não** é serviço → o ponto continuava (mesmo rally, recomeça daí); se passam 6s sem pancada OU a próxima é serviço → acabou na última pancada. **Aplica-se sempre, independentemente de a bola ser detetável.** [v9 usou 6s; Vasco testou 5s]
- **Fim imediato (sem esperar 6s):** bola **sai de campo**; ou jogador **toca na rede** (raquete/corpo).
- **Bola na mão / parada (v1, R3):** bola perto de um jogador e velocidade ~0 por K frames = ponto acabou (fim limpo).
- **Dois toques no chão (v1/v3, R3b/R14):** bola solo→sobe→solo = fim (double bounce).
- **Mesma equipa 2x seguidas (v1/v3, R13):** duas pancadas consecutivas do mesmo lado = ponto acaba.
- **Cumprimento entre jogadores (v1/v3):** fim de ponto claro. [semântico → Gemini]
- **Linguagem corporal (v7.1):** ombros relaxados, raquetes caídas, virar de costas → confirma fim; esperar 2–3s antes de cortar. [semântico → Gemini]
- **Inatividade dos jogadores (v9 regra 5, opcional):** 4 jogadores visíveis e ~3s parados → confirma fim sem esperar os 6s. Se não vires todos, NÃO adivinhes.

### Bola fora do ENQUADRAMENTO ≠ fim (v9 regra 4 / R4)
A bola pode sair da imagem (lob alto, bola ao fundo) sem o ponto acabar. "Inatividade" refere-se a **pancadas e jogadores**, não à bola estar fora do frame. Só ausência real seguida de serviço separa.

### Separação de rallies / "Stitching" (v7.1/v7.7/v8)
- Proibido unir dois momentos com > **2s** de inatividade entre eles → são rallies diferentes.
- Dois períodos só são rallies distintos se houver fim real (ausência > 2s **seguida de SERVIÇO**).
- Pausa média entre pontos: **5–15s**.

### Confirmação por ÁUDIO (v7.1/v7.7, R15)
Som de impacto de raquete / ressalto da bola confirma rally ativo e deteta pancadas. Ignorar conversas (ocorrem entre pontos). Forte SE houver áudio (verificar Court-Master).

### Trocas de campo (todas as versões, R9)
Pausa > **45s** → reavaliar camisolas (cor) e registar se a Equipa A mudou de lado. v1 distingue: `troca_de_campo` (jogadores no lado oposto) · `discussao`/timeout (mesmo lado, reagrupados) · `lesao` (dispersos, câmara foca um) · `indefinido`.

### Margem visual (v9 regra 6 / R8)
Ao cortar o clip, juntar **+2s** no fim (só para ver bem). **Não conta** no tempo útil estatístico.

### Sem invenção
Não criar rallies que não se ancoram a um serviço visível. Segmento ambíguo → `confianca: baixa`, nunca omitir/duplicar.

---

## 2. DETEÇÃO E VALIDADE DO SERVIÇO (v1 §4, v3 Passo 6 — detalhado; encolhido na v9)

### Condições do serviço
- Servidor **atrás da linha de serviço** (FUNDO).
- Parceiro do servidor **junto à rede** (REDE).
- Adversários perto da linha de serviço ou atrás.
- **A bola cai da mão → bate no chão → o servidor bate-a com a raquete** (ressalto-antes-da-pancada = assinatura do serviço, R10).
- A bola vai **cruzada** para o quadrado de serviço diagonal do adversário.
- Padel = serviço **por baixo** → a bola NÃO sobe; o sinal é o arranque horizontal após o ressalto.

### Validade (R12)
- ✅ **Válido:** bola cai no quadrado de serviço **cruzado** sem tocar na malha; confirmado se o recetor jogou de volta E o próximo serviço vai para o lado oposto (ou muda o servidor).
- 🔄 **Let (repete):** bola toca na tela da rede mas cai dentro do quadrado cruzado → serviço repete.
- ❌ **Falta:** bola toca na malha e não entra; OU o recetor não jogou (deixou passar / devolveu sem força / bateu à rede); OU muda o servidor.

*(Quadrado/let/falta precisam de homografia; o ressalto-no-solo é codificável só com a trajetória.)*

### 2ª bola (marca analítica opcional)
1ª pancada do recetor após o serviço → tag `segunda_bola: true`. Não afeta o timing.

---

## 3. PANCADAS — tipos e resultados (evolução da taxonomia)

### Tipos (`tipo` — como se bate)
- **v1:** volley, forehand, backhand, smash, overhead (inclui víbora/bandeja/kick), saida_vidro, serve, indefinido.
- **v3/v7/v8:** serve, volley, forehand, backhand, overhead (agrupa smash/bandeja/víbora/kick), saida_vidro, indefinido.
- **v9 (dois eixos):** `tipo` = serve, volley, forehand, backhand, overhead, **bandeja**, **vibora**, indeterminado · `contexto` = normal, saida_parede_fundo, saida_parede_lateral, contra_parede, indeterminado (o antigo `saida_vidro` passou a contexto).

Definições-chave: **volley** = sem a bola tocar o chão · **forehand/backhand** = após tocar chão/vidro · **smash** = força máxima acima da cabeça pós-balão · **overhead** = ao lado da cabeça, efeito lateral, a recuar · **saida_vidro** = deixa a bola bater alto no vidro de fundo e bate no ressalto.

### Resultado (ancorado ao fim do rally)
Só a **última** pancada pode ser winner/erro; as restantes são `neutro`.
- `winner` = adversário não devolve, ponto a favor.
- `erro_nao_forcado` = falha sem pressão (bola fácil).
- `erro_forcado` = falha sob pressão clara do adversário.
- `neutro` = mantém a bola em jogo sem vantagem.

### Noção de PANCADA em código (R-pancada)
Bola **aproxima-se** da box de um jogador (mínimo local) e depois a trajetória **muda** (afasta-se / pico de velocidade); reforçar com deslocamento da box do jogador. É o evento central: serve→início, pancada→confirmação, 6s sem pancada→fim.

### Ancoragem do timestamp (v7.1/v7.7)
No **movimento biomecânico** (preparação/extensão do braço), NÃO no impacto (rápido demais). Arredondar; nunca inventar por estimativa — se não ancora, omite.

---

## 4. MÓDULO 2 — FASES / CONFRONTOS TÁTICOS ("O Estratega")

Vídeo CURTO (1 rally). Fase pela posição **coletiva** (2 boxes), pelos pés.
- Novo clip **sempre que QUALQUER equipa muda de fase**. Conta-se por **transições** (nº entradas = nº transições + 1).
- A mesma combinação pode repetir-se; cada ocorrência é entrada independente. Sem buracos/sobreposições: `fim[i]` = `inicio[i+1]`.
- Anti-jitter (v9): só conta se a box cruza CLARAMENTE a marca. Análise frame-a-frame interna, apresentação por clip.
- Serviço = momento dentro do ATAQUE (não fase separada).

---

## 5. MÓDULO 3 — TÉCNICO (pancadas de UMA equipa)

Vídeo CURTO (1 rally). Identifica `tipo` + `contexto` + `resultado` da `equipa_alvo`. Bloco de raciocínio obrigatório (preparação → execução → resultado). Confiança alta/baixa (baixa se ocluído/fora de frame/ambíguo).

---

## 6. ARQUITETURA HÍBRIDA (o que é prompt / modelo / geometria)

Pipeline alvo: `Vídeo → deteção por frame (MODELO: boxes jogadores + bola) → calibração campo (GEOMETRIA) → regras (fases, rallies, cortes) → classificação pancadas (MODELO) → JSON v9`.
- **Módulo 1 (rallies):** bola = MODELO; início/fim = REGRA. [é onde estamos — bola resolvida pelo BlurBall; falta a segmentação por serviço/pancada]
- **Módulo 2 (fases):** MODELO (jogadores) + GEOMETRIA pura (comparar boxes vs linhas). Maior retorno, primeira a migrar.
- **Módulo 3 (pancadas):** Prompt (auto-labeler) → confirmação humana → treino gradual de modelo de ação.

---

## 7. MÁQUINA DE ESTADOS (código, junta o Módulo 1)

```
estado = FORA
por frame f:
  FORA:     se R1 (serviço) → EM_JOGO; inicio=f
  EM_JOGO:  se R3 (bola na mão parada) ou R2 (bola sumiu > gap):
               fim_cand=f
               se R5 confirma (6s sem nova pancada não-serviço) → fecha [inicio, fim_cand]; FORA
no fim: R7 (descartar curtos) · R8 (margem +2s só no vídeo) · R9 (trocas)
```

Prioridade de código (retorno imediato): **R1 (início=serviço) + R3 (fim=bola na mão)** substituem margens adivinhadas; depois R5 (janela 6s), R6/R9 (refinamentos).

**⚠ Nota crítica pós-BlurBall (jul 2026):** o `rallies_bola` mede inatividade por **ausência de BOLA** — muleta do detetor esparso. Com o BlurBall (bola detetada quase sempre) isto funde tudo. As regras antigas medem inatividade por **ausência de PANCADAS** (regra dos 6s) e usam o **ressalto do serviço** como âncora — é para AÍ que a segmentação tem de migrar. Ver `PLANO_TEMPO_UTIL_pos_BlurBall.md`.

---

## 8. O QUE FICA PARA O GEMINI (semântico, não codificar)
Quem ganhou o ponto; tipo de pancada winner/erro; fases táticas de nomeação; cumprimento/linguagem corporal como fim; reavaliação de cor das camisolas nas trocas.
