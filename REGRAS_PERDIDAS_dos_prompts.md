# 🕳️ As regras que se perderam entre os prompts e o código

**13 jul 2026.** Confronto: `REGRAS_CONSOLIDADAS_todos_prompts.md` (v1→v9) **vs** `MAPA_DAS_REGRAS.md`.

> **Porque é que isto era preciso:** o `MAPA_DAS_REGRAS.md` foi feito **a partir do código**.
> Por construção, **só vê o que sobreviveu**. Uma regra que foi formulada num prompt e nunca
> chegou ao código **não aparece em lado nenhum** — nem como "por implementar".
> Não estava esquecida. Estava **invisível**.

**9 regras encontradas.** Nenhuma delas está no mapa.

---

## 🔴 ACIONÁVEIS HOJE — tenho tudo o que é preciso

### ~~1. BOLA SAI DE CAMPO → fim imediato~~   ⛔ **VIA FECHADA PELO VASCO (13 jul)**
> *"Fim imediato (sem esperar os 6s): bola **sai de campo**."* (v1/v3/v9)

⛔ **A REGRA DO PROMPT ESTÁ ERRADA PARA PADEL.** O Vasco matou-a antes de eu gastar tempo:

1. **HÁ JOGO EXTERIOR.** A bola sai do campo, o jogador sai atrás dela e devolve-a.
   **"Sai do campo" NÃO é fim de ponto.**
2. **O POLÍGONO É DO CHÃO, NÃO DO VIDRO.** Uma bola contra o vidro — que é jogo **normal**, o
   padel vive disso — está **DENTRO do jogo** e **FORA do polígono**. Cortaria pontos em cima de
   bolas perfeitamente legais.

👉 **É a mesma cegueira do vidro do fundo:** *o que eu tenho é o **CHÃO**; o jogo acontece no
**VOLUME**.* **NÃO REIMPLEMENTAR.** *(Nem sequer com o vidro desenhado — ver
`project_ressalto_bloqueio_unico`: falta profundidade, não desenho.)*

⚠️ **E a lição maior: nem tudo o que está nos prompts está CERTO.** Os prompts são o inventário
das ideias, não a verdade. **As definições do jogo são do Vasco — sempre.**

### 2. JOGADOR TOCA NA REDE → fim imediato
> *"Fim imediato: jogador **toca na rede** (raquete ou corpo)."* (v1/v3/v9)

**Nunca implementada.** Tenho as boxes dos jogadores e a linha da rede calibrada.
É a **mesma estrutura** da S17 que hoje funcionou: box do jogador a intersectar a banda da rede.
**É codificável hoje.**

### 3. SERVIÇO POR BAIXO — a bola NÃO SOBE
> *"Padel = serviço **por baixo** → a bola **NÃO sobe**; o sinal é o **arranque HORIZONTAL**
>  após o ressalto."* (v1 §4)

**Nunca implementada — e é ouro.** É um teste sobre o `Theta` (que dá a direção a 2°) aplicado
logo a seguir ao **ressalto** — e o detetor de ressalto acerta **13/13** nos serviços (13 jul).
Distingue o serviço de qualquer outra pancada **sem precisar do quadrado cruzado**.
👉 **É o caminho mais curto para o detetor de serviço.** Ataca isto antes do quadrado.

---

## 🟡 REGRAS DE MEDIÇÃO — mudam os NÚMEROS, não o código

### 4. A MARGEM VISUAL NÃO CONTA NO TEMPO ÚTIL
> *"Ao cortar o clip, juntar **+2s** no fim — **só para ver bem**.
>  **NÃO conta** no tempo útil estatístico."* (v9 regra 6 / R8)

**Eu ando a MEDIR as minhas margens de visualização como se fossem LIXO.**
O `PAD_ANTES=1,6s` e o `M_COM_PAN=2s` entram na conta da precisão e penalizam-me.

MEDIDO (13 jul):
| | recall | precisão | tempo |
|---|---|---|---|
| como meço hoje (margens contam) | 96,3 | 93,9 | 123,0s |
| tempo útil "estatístico" (sem margem final) | **83,1** | **95,0** | 104,8s |

⚠️ **MAS NÃO É SÓ DISPLAY.** O recall cai 13 pontos ⇒ os 2s **estão a fazer trabalho real**:
tapam o buraco entre a **última pancada detetada** e o **fim verdadeiro** do ponto.
👉 **É uma DEFINIÇÃO, e é do Vasco:** o "tempo útil" que ele quer no produto é o **clip** (com
margem, para ver) ou o **número** (sem margem, para a estatística)? **PERGUNTAR. Não decidir.**

### 5. A REGRA DOS 6 SEGUNDOS (e não 4)
> *"A última pancada só é fim depois de **6s** sem nova pancada. E: se nesses 6s houver uma
>  pancada que **NÃO é serviço**, o ponto continuava."* (v1/v3/v9 — a regra principal)

O código usa `SILENCIO = 4.0`. **O 6 vinha dos prompts; o 4 inventei-o eu.**
E a segunda metade — *"a menos que a próxima seja serviço"* — é a **S8**, testada e rejeitada
hoje (47% de precisão) por falta de detetor de serviço. **A regra dos 6s está INCOMPLETA no
código, e o número está trocado.** Re-testar o 6 assim que houver serviço.

### 6. PAUSA ENTRE PONTOS = 5–15s
> *"Pausa média entre pontos: **5–15s**."* (v7.1/v7.7/v8)

**Nunca usada.** É um *prior* grátis: um "intervalo" de 2s é suspeito; um de 40s também.
Serve para **pontuar** candidatos (lei de desenho do Vasco: pontuar, não cortar).

---

## ⛔ BLOQUEADAS (mas registadas, para não se perderem outra vez)

### 7. R-PANCADA: o MÍNIMO LOCAL de distância à box
> *"Bola **aproxima-se** da box de um jogador (**mínimo local**) e depois a trajetória **muda**."*

O meu `pancadas()` só olha à **mudança de direção** (`Theta`) e à velocidade (`L`). Hoje juntei-lhe
o `PAN_TEM_JOGADOR` (distância ≤ 3 meios-campos) — que é uma **versão fraca** disto.
A versão do prompt é mais forte: **aproxima-se e depois afasta-se**. Vale a pena testar.

### 8. INATIVIDADE DOS JOGADORES → confirma o fim
> *"4 jogadores visíveis e ~3s parados → confirma fim sem esperar os 6s.
>  **Se não vires todos, NÃO adivinhes.**"* (v9 regra 5)

⛔ **Bloqueada pela CÂMARA:** só **21,8%** dos frames têm os 4 jogadores. A própria regra manda
não adivinhar. **Reabrir com a câmara nova.**

### 9. CONFIRMAÇÃO POR ÁUDIO
> *"Som de impacto de raquete / ressalto da bola confirma rally ativo e deteta pancadas.
>  Ignorar conversas (ocorrem entre pontos)."* (v7.1/v7.7, R15)

⛔ **Bloqueada:** os vídeos MATCHi não têm áudio utilizável.
👉 **Mas isto resolvia o RESSALTO e a PAREDE de uma vez** — o som do quique e o da parede são
diferentes. **É um REQUISITO DE CAPTURA para a câmara nova.** Pedir áudio.

---

## Regras dos prompts que ficam para o Gemini (semânticas — não codificar)
Quem ganhou o ponto · winner/erro · cumprimento entre jogadores · linguagem corporal ·
reavaliação das cores nas trocas de campo.

---

## 📌 A LIÇÃO, para o próximo mapa
> **Um mapa feito a partir do CÓDIGO só vê o que sobreviveu.**
> As regras morrem **em silêncio**, entre a formulação e a implementação.
> ⇒ O inventário tem de sair da **FONTE** (prompts, conversas, o que o Vasco disse), e o código
> é que se confronta com ele — **nunca ao contrário**.

E: **correr o `ablacao.py` sempre que entra uma regra.** Uma regra nova pode tornar outra
redundante — e continuar a defendê-la é mentir a nós próprios. *(Foi assim que se descobriu que
o `min_det` está morto e que o `vai-e-vem` ficou redundante quando o Theta e o thr=0.4 entraram.)*
