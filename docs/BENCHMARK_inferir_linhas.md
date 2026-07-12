# Benchmark — "adivinhar" linhas a partir de linhas reais de referência

**Pergunta do Vasco (12 jul 2026):** já existem sistemas que inferem linhas imaginárias a partir de
duas ou mais linhas reais? (o fora-de-jogo do VAR, por exemplo)

**Resposta curta:** sim. O campo chama-se **sports field registration**. O princípio que usámos no
`calibrar_campo.html` — poucas referências + dimensões regulamentares → tudo o resto sai por conta —
**é o princípio-base de toda a área.** Não inventámos nada, e isso é bom sinal. O que o estado da arte
acrescenta é **automatizar a deteção das referências**, não a inferência em si.

---

## 1. O achado que interessa: o VAR NÃO adivinha linhas

Era a hipótese natural, e está errada. O **Semi-Automated Offside Technology** (SAOT) da FIFA:

- **12 a 16 câmaras dedicadas**, fixas, em altura para minimizar oclusões (16 no Mundial 2026).
- **Pré-calibração do campo, offline**: píxeis → coordenadas físicas (X, Y, Z), com erro declarado de
  **poucos centímetros** na linha de fora-de-jogo.
- **Recalibra antes do jogo e ao intervalo** — para compensar a *dilatação térmica dos suportes das câmaras*.
- Segue **29 pontos anatómicos** por jogador, em **3D**, a 50 Hz. Não em 2D: um pé pode *parecer* fora
  de jogo numa vista e estar em jogo depois de triangulado.
- A linha de fora-de-jogo é **traçada a partir do modelo pré-calibrado** — não é detetada na imagem.

**A conclusão que interessa:** mesmo a FIFA, com orçamento ilimitado, **calibra previamente com câmaras
fixas** em vez de detetar o campo em cada frame. É exatamente a nossa abordagem. A calibração manual não
é um atalho de pobre — é o que faz quem tem tudo a perder com um erro de 3 cm.

O detalhe da *dilatação térmica* diz-nos outra coisa: "câmara fixa = calibrar uma vez para sempre" pode
ser otimista demais a longo prazo. Vale a pena, um dia, verificar se a calibração do Parada4 ainda
assenta noutro vídeo do mesmo campo, gravado noutra altura.

---

## 2. Estado da arte académico (para quando quisermos automatizar)

| Método | Ano | O que faz | Aproveitável? |
|---|---|---|---|
| **TVCalib** | 2023 | Trata o registo como **calibração de câmara** (pose + focal), não como homografia. Aprende de correspondências de **segmentos**, sem depender de keypoints. | Conceito |
| **PnLCalib** | 2024 | Otimização por **pontos E linhas**. Bate o TVCalib em calibração 3D mono e multi-vista. **Código aberto.** | **Sim — é por aqui** |

**A lição transversal das duas:** *linhas e segmentos são mais adequados do que keypoints isolados*.
Os **cantos desaparecem** (saem do enquadramento, são tapados por jogadores); as **linhas não**.
É exatamente o problema que apanhámos hoje no Parada4 — o fundo perto está cortado pelo frame.

Isto valida, por caminhos independentes, duas decisões de hoje:

1. O calibrador desenha **linhas**, não cantos. ✔
2. Não extrapolar o fundo perto (deu y=4748 px, absurdo) — e não precisar dele. ✔

E dá razão **parcial** à sugestão externa do `solvePnP`: a direção (calibração 3D em vez de homografia
planar) é a do estado da arte. **Mas não é preciso escrevê-la — o PnLCalib já existe, com código.**

---

## 3. Padel — terra rasa

Muito pouco publicado:

- Tese sueca (DiVA) sobre deteção de campo de padel.
- **CourtVision** (Thinkst, 2023) — projeto pessoal de tracking de padel.
- Comerciais (**PlaySight**, **Hawk-Eye**) exigem **instalação permanente de várias câmaras**; o
  Hawk-Eye usa 6+ câmaras ligadas para reconstruir a bola em 3D.
- Referência útil: em padel a estimativa de posição por imagem usa tipicamente uma câmara alta a **~7,6 m**.

**Implicação:** não há solução pronta a copiar para padel de câmara única. O que estamos a fazer é
razoavelmente original — e a câmara **fixa** + calibração **uma vez** é uma vantagem real, não um
compromisso.

---

## 4. Decisão

**Agora (Parada4, câmara fixa):** fica a calibração manual. É o que a FIFA faz, é exata, custa 5 minutos
por campo. Não há nada a ganhar em automatizar o que se faz uma vez.

**Depois (produção, N clubes, câmaras variáveis):** avaliar o **PnLCalib** — tem código, e ataca
exatamente o problema (referências que desaparecem). Teste: correr num vídeo de outro clube e comparar
com uma calibração manual desse clube.

**Não fazer:** escrever de raiz um `solvePnP` sobre modelo 3D. Chegaríamos, com mais trabalho, a uma
versão pior de algo já publicado e aberto.

---

## Fontes

- [PnLCalib: Sports Field Registration via Points and Lines Optimization (arXiv)](https://arxiv.org/html/2404.08401v4) — [código](https://github.com/mguti97/PnLCalib)
- [TVCalib: Camera Calibration for Sports Field Registration in Soccer (arXiv)](https://arxiv.org/abs/2207.11709)
- [FIFA — inovação no Mundial 2026 (fora-de-jogo semiautomático)](https://inside.fifa.com/news/offside-decisions-referee-body-cams-innovation-world-cup-2026)
- [LearnOpenCV — World Cup 2026 Offside Technology](https://learnopencv.com/world-cup-2026-offside-technology/)
- [FC Barcelona Innovation Hub — Semi-Automated Offside Technology](https://barcainnovationhub.fcbarcelona.com/blog/semi-automated-offside-technology-var/)
- [Automated Tennis Player and Ball Tracking with Court Keypoints Detection (arXiv)](https://arxiv.org/pdf/2511.04126)
- [Padel court detection system (DiVA)](https://www.diva-portal.org/smash/get/diva2:1770685/FULLTEXT01.pdf)
- [CourtVision — Where's my padel at? (Thinkst)](https://blog.thinkst.com/2023/09/courtvision-wheres-my-padel-at.html)
- [Paradigma — Computer Vision for Racket Sports (Tennis & Padel)](https://paradigma.dev/cases/computer-vision-subsystems-for-racket-sports-products-tennis-padel/)
