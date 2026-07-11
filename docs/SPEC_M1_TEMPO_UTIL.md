# SPEC — M1 Tempo Útil (desenho final, jul 2026)

Desenho fechado com o Vasco depois de o BlurBall resolver a deteção de bola. Substitui a
segmentação por "gaps de bola" (que era uma muleta para o detetor fraco).

**Objetivo:** cortar o vídeo em rallies e medir o tempo útil, contra o ground-truth de
**117s / 12 rallies** (`ground_truth_parada4.md`, anotado à mão — conjunto de avaliação permanente).

---

## Diretriz de produto (manda em tudo)

> **Nunca deixar um ponto de fora. Mais lixo é preferível a menos tempo útil.**

O custo é assimétrico: um ponto que falta é informação perdida para sempre; lixo a mais é só um
incómodo a saltar. **Otimizar RECALL, não precisão.** Não perseguir os 117s exatos — perseguir
"nenhum ponto perdido", mesmo que o total fique acima.

---

## O pipeline (a SEQUÊNCIA é a regra)

```
1. SERVIÇO detetado            -> ABRE o rally
                                  início = raquetada − 1s (margem do clip)

2. Corpo do rally: PANCADAS     -> travessias alternadas da rede
   • bola fora do enquadramento != fim
   • ressalto no chão = normal, o ponto continua

3. FIM: a ÚLTIMA PANCADA só é confirmada como fim se:
   (a) o próximo evento for um SERVIÇO           <- REGRA ÂNCORA
   (b) OU fim imediato:  bola direta à REDE
                       · duplo toque no chão + bola parada
                       · mesma equipa bate 2x seguidas (toque duplo)
                       · bola fora do campo
   (c) OU rede de segurança: 6s sem NENHUMA pancada

4. Volta ao 1.
```

**Porquê a regra âncora:** o fim do ponto N é definido pelo **início do ponto N+1**. Sem isso o
fim é um palpite (margem inventada) — e foi isso que fez um rally arrastar 7.4s para lá do fim.

---

## Regra do SERVIÇO (define o ponto)

Todas as condições:

- **A.** bola dentro/perto da box de um jogador e ~parada → **na mão**
- **B.** a bola **desce e RESSALTA aos pés do servidor** (inversão da velocidade vertical)
  ← **sinal-chave: nenhuma outra bola do jogo faz isto**
- **C.** **raquetada** — pico de velocidade, a bola afasta-se
- **D.** servidor **atrás da linha** (base da box dentro da `serve_zone`)
- **E.** restantes jogadores **na linha de serviço ou atrás** (formação)
- **F.** o **servidor arranca a seguir** (corre na direção da bola / sobe à rede)

No padel o serviço é **por baixo** — a bola **não sobe**. O sinal é o arranque horizontal
**depois** do ressalto.

> É o ressalto (B) que distingue um serviço de qualquer outra bola que sai de uma mão
> (ex.: um jogador a devolver a bola ao adversário entre pontos — isso é lançamento, não serviço,
> e não tem ressalto-seguido-de-raquetada nem formação nem arranque do servidor).

---

## Regra da ALTERNÂNCIA (corpo do rally)

- As pancadas **alternam** entre campo de baixo e campo de cima. Uma equipa **não bate 2x seguidas**.
- Logo **cada TRAVESSIA DA REDE implica uma pancada** no campo de origem — não é preciso *ver* a
  pancada; a física garante-a. **Robusto a oclusão e a bola fora do frame.**
- Bola muda de direção sem pancada detetada → **INFERIR a pancada**.
- Duas pancadas seguidas no mesmo campo = impossível → uma é espúria **OU o ponto acabou** (toque duplo).
- **Travessias alternadas e sustentadas = rally em curso.** Entre pontos a bola cruza a rede no
  máximo uma vez (devolvida ao servidor), não faz vaivém.
  → **É o melhor sinal de jogo/não-jogo que temos** — melhor que presença ou velocidade da bola.
  Dá precisão **sem** sacrificar recall.

---

## Regra do LADO DO SERVIÇO (invariante estrutural — distingue ACE de FALTA)

- Depois de um **ponto concluído** (ace incluído) → o serviço seguinte vai para o **lado OPOSTO**.
- Depois de uma **FALTA** → o serviço repete-se para o **MESMO lado**. **É a única vez que isso acontece.**
- Logo: **falta + 2º serviço = UM ponto, não dois** → corrige a sobre-contagem de rallies.
- **Distingue ace de falta sem homografia**: não olhamos se a bola entrou no quadrado — olhamos
  para o **lado do serviço seguinte**.
- **Auto-verificação de graça:** a sequência de lados tem de alternar (exceto após falta). Se não
  alternar e não houver falta → detetámos um serviço a mais **ou perdemos um**. Sinal de erro sem
  precisar do ground-truth.
- Lado = `x` do centro da box do servidor vs `x` do meio do campo. **Sem calibração nova.**

---

## Distinguir eventos SEM plano do solo

Não é preciso calibrar o chão (seria um pesadelo — a perspetiva faz a bola ressaltar a um `y`
completamente diferente ao fundo e à frente):

| Evento | Sinal |
|---|---|
| **Ressalto no chão** | inversão da velocidade vertical **SEM jogador perto** |
| **Pancada** | mudança brusca de direção **COM jogador perto** |
| **Ressalto do serviço** | inversão vertical **com** jogador perto, a **baixa velocidade**, seguida de pico (a raquetada) |

Referência do chão **para o serviço** = a **base da box do servidor** (`y2`) — a bola ressalta aos
pés dele. Poupa uma calibração e é mais robusto.

---

## Calibrações necessárias (câmara fixa, uma vez)

| O quê | Estado | Desbloqueia |
|---|---|---|
| `serve_zone_y` = `[(335,421),(54,140)]` (960×540) | ✅ feito | posição do servidor |
| **`y` da linha da rede** | ⬜ **falta** | travessias (pancadas inferidas) · bola-direta-à-rede · alternância |

Calibrar a rede como se calibrou a `serve_zone`: mostrar um frame com uma régua de `y` e ler onde
está a fita da rede. **Um número desbloqueia três regras.**

---

## Salvaguarda (obedece à diretriz)

Se um serviço **não** for detetado mas houver jogo evidente, o segmento **entra na mesma**, marcado
`confianca: baixa`. **Colar dois pontos é mau; perder um ponto é pior.**

A âncora do serviço **afina**; a atividade da bola **garante que nada se perde**.

---

## Estado atual (o que já funciona)

Ponto de operação em `padelpro/modules/blurball_io.py` (`PONTO_OPERACAO`):
`vmin=6, gap_fora_s=1.0, serve_zone_y=None` → **13 rallies, recall 99%**, precisão 56%, 205s.
(baseline YOLO `best.pt`: 10 rallies, recall 67%, precisão 73%, 106s.)

O que falta é implementar este spec — o serviço, a alternância e os fins — que vão **limpar o lixo
sem perder pontos**.
