# Regras de bola do v9 → especificação para código

Objetivo: fazer o **timing** dos rallies (tempo útil) em código, a partir das deteções que já produzimos,
em vez de pedir timestamps ao Gemini (que são imprecisos). O Gemini fica só para o semântico (quem ganhou, que pancada).

## Sinais que já temos (ou conseguimos) por frame
- `bola_xy[f]` — posição da bola em píxeis (detetor treinado, best.pt). Pode faltar em frames (bola não detetada).
- `bola_visivel[f]` — bola detetada E em movimento (já filtrada dos hotspots estáticos).
- `jogadores_xy[f]` — bounding boxes dos 4 jogadores (do padel_analytics / detetor de jogadores).
- `homografia` — opcional, para converter píxeis→metros e saber "dentro/fora do campo". Sem ela, usar zonas em píxeis.
- `fps` — para converter frames↔segundos.

Derivados úteis (calcular uma vez):
- `vel_bola[f]` = distância entre `bola_xy[f-1]` e `bola_xy[f]` (píxeis/frame). Alta = a voar; ~0 = parada.
- `bola_perto_jogador[f]` = distância mínima da bola a uma box de jogador < limiar (ex. 60 px).

---

## Regras traduzidas (cada uma: origem v9 → sinal → pseudo-código → viabilidade)

### R1. Início do ponto = SERVIÇO (v9 P1 regra 1; versão Vasco: "bola perto da box até já não estar")
Sinal: a bola mantém-se **colada à box de um jogador** durante uns frames e depois **afasta-se** dela → esse
instante de afastamento é a bola posta em jogo (serviço). (Mais robusto que detetar o toss a subir.)
```
para cada f:
  se bola_perto_jogador[f] (dist bola↔box < limiar, ex. 60px) por >= K frames:
     bola_na_mao = True; jogador_servico = quem
  se bola_na_mao e bola_perto_jogador[f] == False:        # bola SAIU da box
     inicio_rally = f                                      # início real (não a margem adivinhada)
     bola_na_mao = False
```
Viabilidade: **alta**. Só precisa de bola + boxes dos jogadores, sem detetar o toss. Afinar `limiar` e `K` no teu vídeo.

### R2. Fim do ponto — bola fora do campo (v9 P1 regra 3; Vasco: "bola fora >4s")
Sinal: última posição fiável da bola sai da zona de jogo, OU bola desaparece do jogo por > N segundos.
```
se bola_visivel esteve ativa e desaparece por > gap_fora_s (ex. 2.0):
     fim_rally = último frame com bola_visivel                # regra que o deteccao_rallies JÁ faz
```
Viabilidade: **alta**. Já implementado (`deteccao_rallies.py`). O "fora do campo" exato pede homografia; sem ela, o gap temporal chega.

### R3. Fim do ponto — bola parada / na mão (v9 P1 regra 5; Vasco: "bola parada/na mão em 2 frames")
Sinal: bola perto de um jogador e velocidade ~0 durante K frames consecutivos (jogador segura a bola = ponto acabou).
```
se bola_perto_jogador[f] e vel_bola[f] ~ 0 por >= K frames (ex. K = 0.4*fps):
     fim_rally = f - K                                        # o ponto acabou quando parou
```
Viabilidade: **alta**. Dá o **fim real** e substitui a margem `pos` adivinhada.

### R3b. Fim imediato — bola na REDE ou DOIS toques no chão (v9 P1 regra 3; refinamento Vasco)
Sinal A (bola na rede): a bola para na zona da linha da rede e fica lá → fim imediato.
Sinal B (double bounce): a bola chega à zona do solo, sobe, e volta a descer ao solo (2 toques) → fim imediato.
```
# A: precisa de saber a linha da rede (dos keypoints do campo)
se bola perto da linha_rede e vel_bola ~ 0 por alguns frames: fim_rally = f
# B: inversões de velocidade vertical perto do solo
se bola atinge zona_solo, inverte (sobe), e volta a atingir zona_solo: fim_rally = 2º toque
```
Viabilidade: A **média** (precisa da rede); B **média-baixa** a 540p (falhas de deteção tornam o double bounce instável). Testar.

### R4. Bola fora do ENQUADRAMENTO ≠ fim (v9 P1 regra 4)
Sinal: a bola some do frame (lob alto/fundo) mas volta a aparecer dentro de gap_fora_s → NÃO cortar.
```
NÃO fechar o rally só por bola ausente < gap_fora_s.
Só R2 (ausência > gap_fora_s) fecha.
```
Viabilidade: **alta**. É o comportamento do gap atual — só garantir que gap_fora_s é generoso (2s).

### R5. Confirmação ao contrário — janela de 5s (v9 P1 regra 2; Vasco reduziu 6→5s)
Sinal: depois de um "fim" candidato, esperar 5s; se aparecer nova PANCADA que NÃO é serviço, o rally continua.
```
fim_candidato = f
olhar frames [f, f + 5*fps]:
  se houver nova PANCADA (ver R-pancada) que NÃO seja serviço:
     rally continua; recomeça a contar a partir dessa pancada
  senão:
     fim_confirmado = fim_candidato
```
Viabilidade: **média**. Depende de detetar "pancada" (ver regra abaixo).

### R-pancada. Noção de PANCADA (base para R5) — proximidade + afastamento de boxes (ideia do Vasco)
Sinal: a bola **aproxima-se** da box de um jogador e depois a trajetória **muda** (afasta-se / pico de velocidade);
reforçar com o **movimento do jogador** (deslocamento da box).
```
pancada em f se:
  dist(bola, box_jogador) atinge mínimo local (aproximação)  E
  logo a seguir a bola afasta-se (dist aumenta) OU vel_bola dá pico  E
  (opcional) a box do jogador teve deslocamento nesse instante
```
Viabilidade: **média-alta**. É o evento central: serve→R1, pancada→R5, sem pancada 5s→fim.

### R6. Inatividade dos jogadores (v9 P1 regra 5, confirmação rápida)
Sinal: todos os 4 jogadores visíveis e ~parados por ~3s → confirma fim sem esperar os 6s.
```
se 4 jogadores visíveis e deslocamento de todos < limiar por ~3s:
     fim_confirmado = início dessa paragem
```
Viabilidade: **média**. Precisa das boxes dos 4 jogadores fiáveis. Opcional (acelera o fecho).

### R7. Descartar rallies curtos (v9 implícito; deteccao_rallies minr)
```
se duração_rally < min_rally_s (ex. 1.0): descartar.
```
Viabilidade: **alta**. Já existe.

### R8. Margem visual de +2s (v9 P1 regra 6)
Sinal: NÃO é deteção — só ao **cortar o vídeo** juntar +2s no fim para se ver bem. (No cálculo do tempo útil, não contar.)
```
clip = [inicio_rally, fim_rally + 2*fps]   # só para o vídeo condensado, não para a estatística
```
Viabilidade: **alta**. Separar "tempo útil real" (sem margem) de "clip para ver" (com margem).

### R9. Trocas de campo (v9 P1 regra 7)
Sinal: pausa > 45s entre pontos → marcar troca de campo (e reavaliar cores, mas isso é do Gemini).
```
se intervalo entre fim de um rally e início do seguinte > 45s: registar troca_de_campo.
```
Viabilidade: **alta** (a deteção da pausa; a cor das camisolas fica para o v9).

---

## Máquina de estados (junta tudo)
```
estado = FORA
para cada frame f:
  se estado == FORA:
     se R1 (serviço detetado): estado = EM_JOGO; inicio = f
  se estado == EM_JOGO:
     se R3 (bola na mão parada) ou R2 (bola sumiu > gap): 
        fim_cand = f
        se R5 confirma (6s sem nova pancada não-serviço): 
           fechar rally [inicio, fim_cand]; estado = FORA
# no fim: aplicar R7 (descartar curtos), R8 (margem só no vídeo), R9 (trocas)
```

## Prioridade de implementação (o que dá mais retorno já)
1. **R3 (fim = bola na mão parada)** + **R1 (início = serviço)** → substituem as margens pre/pos adivinhadas.
   Isto sozinho deve levar o tempo útil dos 96–172s para perto dos **132s** reais.
2. R5 (janela 6s) para robustez contra pancadas não detetadas.
3. R6/R9 (jogadores parados, trocas de campo) — refinamentos.

---

## REGRAS RECUPERADAS dos prompts v2/v3/v7/v8 (tinham-se perdido na v9)

### R10. Serviço bate no chão antes de ser batido (v2/v3) — reforça o R1
Sinal: entre a bola sair da mão e a raquetada (pico de vel.), a bola **toca a zona do solo** uma vez.
Isto distingue um serviço de qualquer outra bola que sai da mão.
```
servico confirmado se: bola sai da box + toca zona_solo (1 ressalto) + pico_vel (raquetada)
```
Viabilidade: **média** (precisa da zona do solo). É a base codificável da validade de serviço.

### R11. Posição de serviço (v2/v3)
Servidor atrás da linha de serviço (FUNDO); parceiro na rede (REDE); adversários na linha ou atrás.
Viabilidade: **média** (precisa de homografia/zonas). Valida um candidato a serviço.

### R12. Validade de serviço — let / falta (v2/v3)
- válido = bola cai no quadrado de serviço CRUZADO sem tocar na malha.
- let    = toca na tela da rede mas cai dentro → serviço REPETE.
- falta  = toca na malha e não entra; OU recetor não jogou; OU muda o servidor.
Viabilidade: **baixa-média** (maioria semântica/homografia). Implementado como stub em `servico_valido()`.

### R13. Fim — mesma equipa toca 2x seguidas (dupla) (v2/v3)
Sinal: duas pancadas consecutivas atribuídas a jogadores do MESMO lado → ponto acaba.
```
se pancada[i] e pancada[i+1] são do mesmo lado (sem pancada adversária entre elas): fim_rally = pancada[i+1]
```
Viabilidade: **média-alta** (precisa de saber o lado de cada jogador; já temos boxes). Nova condição de fim.

### R14. Fim — dois toques no chão (v2/v3) [= R3b, implementar no código]
Já descrito em R3b; recuperado também aqui como condição explícita de fim.

### R15. Confirmação por ÁUDIO (v7.1/v7.7) — sinal novo e forte
Usar o **som do impacto da raquete / ressalto da bola** para detetar pancadas e confirmar rally ativo.
Ignorar conversas (ocorrem entre pontos). Se o vídeo Court-Master tiver áudio, picos de áudio = pancadas —
detetor de pancadas mais robusto que só a posição da bola. Combinar com R-pancada (visão) para redundância.
Viabilidade: **alta SE houver áudio** (o MATCHi TV não tinha; o Court-Master pode ter — verificar).

### R16. Fim semântico (v2/v3/v7/v8) — fica para o Gemini
Cumprimento entre jogadores; linguagem corporal (ombros relaxados, raquetes baixas, virar costas). NÃO codificar.

### Confirmações de parâmetros já usados
- "Stitching proibido com gap > 2s" (v7/v8) → confirma `gap_fora_s = 2.0`.
- Pausa média entre pontos: 5-15s. Troca de campo: > 45s (R9). Fim por inatividade de pancadas: 5-6s (R5).
- Tag "2ª bola" (v2): 1ª pancada do recetor após o serviço — marca analítica opcional (não afeta timing).

## O que NÃO fazer em código (fica para o Gemini/v9)
- Quem ganhou o ponto, tipo de pancada (winner/erro forçado/não forçado), fases táticas.
  Isso é semântico → PROMPT 2 e 3, alimentados com os clips que estas regras cortam.
