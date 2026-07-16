# 🌙 FECHO — 13 JUL, À NOITE
### *O 2.º vídeo (BarbosaMeireles) ganhou ground-truth. E partiu quase tudo.*

> **Documento DATADO. É história, não é estado.**
> **O estado sai de `python3 teste_regressao.py`. Nada mais.**

---

# 📊 ONDE FICÁMOS

```
PARADA4   recall 96,8 · precisão 95,4 · 13/13 pontos · fim_dentro 0   ✅ VERDE
BARBOSA   recall 81,9 · precisão 65,7 · 22 pontos (GT: 21) · fim_dentro 3   🔴
          (esta manhã era 79,6 / 65,4 / fim_dentro 5)

🐕 verificar_fonte.py:  ✅ FONTE LIMPA
```

**O modelo é MUITO pior no vídeo novo.** Perde **18 %** do jogo e **34 %** do que marca é lixo.
**A razão está encontrada.** Não está resolvida.

---
---

# ⚖️ AS LEIS DO VASCO — nascidas hoje

*Todas nasceram da mesma coisa: **ele viu o vídeo** e disse **"está muito mau mesmo"**.
Nenhuma apareceu nos números primeiro. **Os números só confirmaram depois.***

---

## 🔴 B19 — OS 9 CANDIDATOS   ⭐ *a raiz. Tudo o resto espera por isto.*

> # **"Há 8 ténis num campo de padel."**
> # **8 pés + 1 bola = 9 hipóteses.**

**O BlurBall vê-as todas.** O `_detect_blob_nms` devolve **TODOS** os picos do mapa de calor
(`while True`, até acabarem). **Não há K. Nunca houve.**

**O `OnlineTracker._select_best` (`trackers/online.py:53`) fica com UMA e deita 8 fora.**
E escolhe **pelo SCORE** quando não tem previsão *(início de cada troço, depois de cada buraco)*:

```
um TÉNIS tem score 0,735   ·   a BOLA tem 0,758      →  É UMA MOEDA AO AR
```

**E depois o `_select_not_too_far` PRENDE-O ao sapato** — que está sempre perto de si próprio.
**O tracker senta-se lá e não larga.** *(Medido: mediana de movimento numa deteção-pé = **4,4 px**.
Está PARADA. Numa bola a sério são 10,0 px.)*

> ## ⇒ Nesses frames a bola A SÉRIO **NUNCA É DETETADA**.
> ## **A pancada não é "mal vista". É NUNCA VISTA.**
> ## **E apagar o ténis DEPOIS não devolve a bola.**

**⚠️ ESTADO:** patch escrito (`blurball/src/runners/inference.py`, procurar `🔴 PATCH`) — **aditivo**:
o `traj_frames` sai igual, sai um `candidatos.csv` ao lado. **Correr: `OS_9_CANDIDATOS.command`.**

**A RÉGUA:** mediana **≤ 2** ⇒ o limiar entupiu o cano a montante · **5–9** ⇒ vemos o campo todo.

---

## 🔴 B18 — A BOLA VAI SEMPRE A CAMINHO DE ALGUÉM   ⭐ *a mais forte. Espera pela B19.*

> ### *"O ponto decorre com a bola em movimento após o serviço. Tem de estar num **MOVIMENTO
> ### CONTÍNUO** que se ajuste ao **aproximar-se de pelo menos uma bounding box** — **até mudar
> ### de direção**."*

**Entre duas pancadas, a bola CONVERGE para um jogador. Sempre. É o que o jogo É.**

| mata | porquê |
|---|---|
| 👟 **os ténis** | estão **colados** a alguém. **Não se aproximam de ninguém** — já lá estão. |
| 👥 **o público** | um ponto branco na bancada **não vai a caminho de jogador nenhum** |
| 🔗 **e COSE a cadeia** | bola → jogador → bola → jogador. **Se a cadeia não fecha, não é jogo.** |

É a **P5** levada até ao fim: a P5 diz *"aproxima-se da box e depois muda de direção"* como um
**evento**. **A B18 diz que isso é o ESTADO NORMAL da bola em jogo. Tudo o resto é ruído.**

⚠️ **Precisa das boxes limpas (J1 — feito) E dos candidatos (B19 — a correr).**

---

## 👟 B16 — O TÉNIS

> ### *"Se detetar uma bola no **limite inferior da bounding box**, e ela **É UMA CONSTANTE** —
> ### tenho de verificar essa bola."*

**É geometria pura** (D10) e é a tua **F3** *(a aresta inferior da box é o contacto com o solo)*.

**✅ MEDIDO:** **25,2 %** das "bolas" do Barbosa estão nos **18 % de baixo** de uma box.
*(No Parada4: **15,2 %**. **É um problema DESTA câmara** — como disseste.)*

**⚠️ E A PARTE QUE TU ACERTASTE E EU NÃO:** disseste **"se é uma CONSTANTE"**.
Eu fui testar a **B17** (o salto) e ela só apanha **4 %**. **O ténis não SALTA — SENTA-SE.**
**O sinal certo era o teu: a CONSTÂNCIA.**

**❌ MAS APAGAR O TÉNIS NÃO CHEGA.** Testado: matar TODOS os candidatos-pé deixa o `fim_dentro`
**exatamente onde estava (5)**. **O estrago acontece ANTES — no tracker (B19).**

---

## 🔁 B17 — O SALTO E O REGRESSO   *(medida: vale pouco)*

> *"Uma bola não pode estar num sítio, passar para outro **sem mudança de direção**, e **voltar à
> mesma direção** num terceiro frame."*

**Medido: só 4 % dos ténis têm esta assinatura.** A regra é boa, mas **não é este o sintoma**.

---

## ⏱️ S42 — A CONFIRMAÇÃO DO FIM   ⛔ *lei certa · código pronto · DESLIGADA*

> # **NÃO HÁ FIM DE PONTO SEM SERVIÇO A SEGUIR.**
> **Para um ponto acabar, a pancada SEGUINTE deve SEMPRE ser um SERVIÇO.**

### As TRÊS coisas que o `SILENCIO = 4` fazia sozinho, misturadas:

| | |
|---|---|
| **① AGRUPAR** | dois cruzamentos a menos de **4 s** são o **mesmo ponto** |
| **② VERIFICAR** | depois da última pancada, espera **4 s** para ver se vem outra. **É DECISÃO — não é o que se mostra.** |
| **③ APRESENTAR** | confirmado ⇒ o vídeo mostra **+2 s**. *(Chegaste aqui a VER: 1 s → "é pouco, põe 3" → os 3 s colaram dois pontos → **"2 segundos é o melhor"**.)* |

### A confirmação — **DUAS condições, ambas leis tuas, ZERO números novos:**

1. a pancada seguinte é um **SERVIÇO** *(S23: teve um **quique FUNDO** antes)*
2. **e está a ≥ 4 s** — **"UM PONTO NÃO PODE COMEÇAR 4 s DEPOIS DO OUTRO"**

> 🔑 **Sem a segunda, uma pancada a meio de um rally passa por serviço** — num rally a bola
> **também** quica fundo. *(O ponto 21 do Barbosa cortava aos 413,2 s e perdia **8,3 s** de jogo:
> a "pancada seguinte" estava a **2,8 s**.)*

**Não confirmado ⇒ O PONTO NÃO ACABOU ⇒ mais margem.**
⚠️ **"USA A REGRA COMO CONFIRMAÇÃO E NÃO COMO CORTE"** — só APERTA quando tem CERTEZA. **Nunca corta na dúvida** (D18).

**⛔ DESLIGADA:** a margem do ramo não-confirmado ainda serve de **cola** (fundia os pontos 13 e 14
do Barbosa). **Destrava com a S43 + o detetor de serviço a 100 % (⇒ B19).**

---

## 🔗 S43 — A COLA   ⛔ *lei certa · código pronto · DESLIGADA*

> # **Dois pedaços só são pontos DIFERENTES se houver um SERVIÇO entre eles.**
> *(Corolário direto do **"não há ponto sem serviço"**.)*

**O que resolve:** um ponto parte-se em dois quando a bola desaparece. Até hoje, o que os voltava a
juntar era **A SOBRA DA MARGEM DE APRESENTAÇÃO**. Isso não é uma regra — **é um acidente.**

> ## 🔑 **A MARGEM DE APRESENTAÇÃO NÃO PODE SER A COLA.**

**⛔ DESLIGADA:** o detetor de serviço acerta **12/13 (92 %)**. O falhado é o **ponto 2 do Parada4**.
A cola pergunta *"abres com um serviço?"*, ouve **NÃO** — e **ENGOLE UM PONTO REAL** (13 → 12).

> ⚠️ **A D18 diz que nenhuma regra pode VETAR. Esta não veta — ENGOLE, que é pior.**

---

## 🤝 O PASSE À MÃO ENTRE COLEGAS   🔴 *registada, por implementar*

> *"Quando um jogador passa a bola ao outro à mão, **da mesma equipa**, não pode disparar."*

A S23 assume que o passe à mão **não quica**. **Às vezes quica — e dispara à mesma.**
**A guarda que falta é GEOMETRIA:** se quem larga e quem apanha estão **do MESMO lado da rede**,
**não houve mudança de campo ⇒ não é serviço.**

---
---

# ⚖️ AS LEIS QUE SAÍRAM DA MEDIÇÃO   *(minhas, mas ancoradas no jogo)*

## 🎾 A BOX É O CORPO. A RAQUETE CHEGA A MAIS DE UM METRO.   ✅ *APLICADA*

A S17 (a rede) só dispara se a bola virar **"longe de qualquer box"**. **"Longe" eram 70 cm.**
Mas uma bola batida **à VOLEIA** sai da raquete e fica a **70 cm–1,2 m do CORPO**: *"longe"* pela
regra — **e no entanto FOI BATIDA**. A S17 lia isso como *"bateu na rede"* e **MATAVA O PONTO A MEIO**.

**Medido no Barbosa: 4 dos 5 fins-a-meio-de-ponto eram VOLEIAS** — a bola virava **70°, 75°, 77°,
86°** ao pé da rede, com um jogador a **~1 m**.

```
RED_DIST 0,10 (70 cm)  →  Barbosa recall 79,6 · fim_dentro 5
RED_DIST 0,17 (1,2 m)  →  Barbosa recall 81,9 · fim_dentro 3      ✅ APLICADO
Parada4: NÃO MEXE UMA DÉCIMA. A ablação diz que a S17 continua a valer −5,0.
```

⚠️ **0,17 não é mágico:** é **(braço + raquete ≈ 1,2 m) / (meio-campo = 6,95 m)**. É o **ALCANCE DE
UMA RAQUETADA**. Sobrevive a outra câmara.
⚠️ **NÃO cura o fundo:** a box dos **PÉS** continua a não ver a **RAQUETE**. **É um penso.**

## 🔢 UM NÚMERO, UM TRABALHO.

**O `SILENCIO = 4` fazia três coisas. O `M_COM_PAN = 2` fazia duas** *(apresentar **e colar**)*.
**Cada sobreposição destas é uma bomba com temporizador.** Só aparece quando alguém lhe mexe.

---
---

# ⛔ VIAS FECHADAS — **MEDIDAS HOJE. NÃO REPETIR.**

| hipótese | veredito | o número |
|---|---|---|
| *"a resolução (960→1280) parte os limiares em píxeis"* | ❌ **FALSO** | o `L` mediano é **0,95×**, não 1,33×. **O BlurBall redimensiona por dentro.** |
| *"o PÚBLICO nas boxes mata a regra da rede"* | ❌ **FALSO** | limpei **52 %** das boxes (6,80 → 3,25/frame). **Os 22 segmentos ficaram IDÊNTICOS ao décimo.** O público está nas **bancadas**; a bola está no **campo**. |
| *"a COR separa a bola do ténis"* | ❌ **FALSO** | saturação **61** (ténis) vs **76** (bola). Matiz **igual**. A bola tem 4 px e o quadradinho é dominado pelo **azul do campo** (D13). |
| *"subir o THRESHOLD mata os ténis"* | ❌ **FALSO** | score **0,735** (ténis) vs **0,758** (bola). `thr=0,9` mata **4 em cada 5 BOLAS**. ⇒ **D9: o detetor não salva isto. Só a ESTRUTURA.** |
| *"os ténis causam os cortes a meio"* | ❌ **FALSO** | matar **TODOS**: o `fim_dentro` fica em **5**. Nos 5 cortes, a bola **não está nos pés**. |
| *"exigir que o 'a bola PAROU' DURE cura o fim_dentro"* | ❌ **FALSO** | 0,5 s de duração: `fim_dentro` **não mexe** nos dois vídeos. |
| *"trocar de detetor de bola"* | ❌ **não resolve** | o modelo está bem. **É o TRACKER que escolhe mal.** |
| *"mudar as definições de cor do BlurBall"* | ❌ **não existe** | é uma rede neuronal. **Não tem botão de cor.** |
| **passar tudo para o Antigravity** | ❌ **ganho ≈ 0** | muda o **editor**, não o **sinal**. E os **agentes em paralelo** colidem de frente com a *uma caneta de cada vez*. |

---
---

# 🔊 A DESCOBERTA QUE NINGUÉM ESPERAVA

A constituição dizia, sobre o bloqueio único: ***"E o ÁUDIO resolvia as três de uma vez — GRAVAR COM ÁUDIO."***

# **OS VÍDEOS JÁ TÊM ÁUDIO.**

```
Parada4.mp4          aac · 48 kHz · estéreo · 100 kbps   ✅  max −16,8 dB
BarbosaMeireles.mp4  aac · 48 kHz · estéreo ·  99 kbps   ✅  max −13,4 dB
```

**Não é silêncio. É som a sério. E NUNCA FOI TOCADO** — o pipeline só lê píxeis.
**O quique, a parede e a raquete são TRÊS SONS DIFERENTES.**

> **A doença outra vez: uma frase escrita ("gravar com áudio") que APODRECEU e passou a mentir na
> linha que toda a gente lê.  — SÓ O QUE SE CORRE É QUE CONTA.**

**⚠️ Não está testado.** Falta ver se a pancada tem um **pico** alinhado, ou se o público a tapa.
**É um teste de 15 minutos e ninguém o fez.**

---

# 🕳️ E AS OUTRAS COISAS QUE APARECERAM

| | |
|---|---|
| 🔴 **A B1 NÃO CORRE** | *"objetos imóveis não são a bola. A bola nunca pousa duas vezes no mesmo sítio."* **É lei tua. Nunca foi implementada.** E é o que mataria a "bola" dos **380,7 s** — parada meio segundo, **a 42 metros** de qualquer jogador. |
| ✅ **`calibracao_campo.json`** | era **ANÓNIMO** (sem `_video`). O pipeline carregava-o; o **etiquetado** era o que **ninguém lia**. Geometria idêntica **hoje**. *"Idêntico hoje não é um estado — é uma contagem decrescente."* **TROCADO.** |
| ✅ **J1 — pés no polígono** | aplicado. **52 % eram público.** Correto — **mas não muda um número.** |
| ✅ **Ground-truth do Barbosa** | **21 pontos, 138,0 s.** Anotado por ti. **Sem isto, tudo o que fizermos ao Barbosa é adivinhar.** |

---
---

# 🚨 A ORDEM PARA A PRÓXIMA VEZ

```
1. 🔴 B19 — os 9 candidatos        ← DESTRAVA a B18, a S42 e a S43 de uma vez
2. 🔗 B18 — a bola vai a caminho de alguém
3. ⚪ B1  — objetos imóveis não são a bola   (mata o corte dos 380,7 s)
4. ⏱️ S42 + S43 — ligar, quando o detetor de serviço chegar a 100%
5. 🔊 O ÁUDIO — o teste dos 15 minutos que ninguém fez
```

---

# 🩸 E A LIÇÃO DE HOJE

## **Cinco hipóteses. Quatro eram minhas. TODAS erradas.**

**A que estava certa era do Vasco, e ele viu-a com os olhos:**
> *"eu acredito que os ténis estão a tirar a deteção da pancada da bola"*

**Ele não tinha um número. Tinha razão.**

> # 🎬 **VÍDEO ANTES DE MÉTRICAS. Ele encontrou TODOS os bugs a olhar.**
> # 🧪 **TESTAR, NÃO RACIOCINAR. Eu perdi a noite a raciocinar bonito.**
> # 🧐 **CONFIRMAR A PREMISSA ANTES DE ACEITAR A CONCLUSÃO.**
