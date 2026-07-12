# Benchmark de deteção e calibração de campo de padel
### (incluindo o caso "cantos cortados / fora do enquadramento")

Data: 2026-07-12 · Projeto: PadelPro Vision

---

## 0. TL;DR — a conclusão primeiro

1. **O problema está mal colocado.** "Detetar o campo" ≠ "detetar 4 cantos e fazer homografia". Os cantos são o *pior* alvo possível: são os primeiros a sair do enquadramento e os mais tapados por jogadores. Toda a literatura recente (SoccerNet 2023–2026) já abandonou a homografia por 4 pontos.

2. **A resposta certa para padel não é 2D — é 3D.** O campo de padel é uma **caixa rígida conhecida** (20×10 m, paredes de 3–4 m, rede a 0,88/0,92 m). Quando os cantos do chão estão cortados, as **paredes, os postes verticais e a rede continuam visíveis**. Passar de `findHomography` para `solvePnP` sobre um modelo 3D do campo resolve o caso "cantos cortados" por construção — nenhum outro desporto tem esta vantagem.

3. **A câmara é fixa.** Nas gravações MATCHi, a câmara não faz pan/tilt/zoom. Logo o problema real não é "registar cada frame" mas sim **calibrar uma vez por campo + detetar drift**. Isto muda completamente o benchmark: podes agregar centenas de frames (incluindo frames com o campo vazio entre pontos) e usar RANSAC temporal. Robustez sai de graça.

4. **Não existe benchmark público de calibração de padel.** Existe para futebol (SoccerNet-Calibration), ténis (TennisCourtDetector) e basket (KaliCalib). Para padel há datasets de bola/jogadores (PadelTracker100) e um dataset de keypoints no Roboflow (656 imgs), mas **zero benchmark de calibração com ground-truth de câmara**. Há aqui espaço para construir algo que ninguém tem — e que é diretamente monetizável.

5. **O erro que ninguém menciona: distorção de lente.** As câmaras de padel são grande-angular montadas atrás/acima do vidro de fundo para cobrir 20 m. Sob distorção barril, **uma homografia planar é matematicamente errada** — as linhas retas do campo não são retas na imagem. Se estás a ver erros de 30–60 cm perto das paredes laterais, é provavelmente isto, não o detetor.

---

## 1. Porque é que os cantos cortados matam os métodos padrão

O pipeline clássico (e o que o `padel_analytics` do João faz hoje, com **12 keypoints clicados à mão**):

```
imagem → detetar N keypoints → emparelhar com modelo 2D → cv2.findHomography → coordenadas de campo
```

Três falhas estruturais quando um canto está fora do frame ou tapado:

| Falha | Porquê |
|---|---|
| **Heatmaps não sabem prever fora da imagem** | Um modelo tipo TrackNet/HRNet produz um mapa de calor *dentro* do frame. Se o canto está a 200 px fora da borda, o heatmap fica plano e o keypoint é simplesmente perdido — não há forma de o modelo o "extrapolar". |
| **Pontos são frágeis, linhas não** | Um ponto ou está visível ou não está. Uma **linha parcialmente visível continua a ser uma restrição completa** (uma linha define 2 equações na homografia, via `l' = H⁻ᵀ l`). Cortar metade da linha não destrói a linha. |
| **Homografia planar assume pinhole** | Com lente grande-angular, `findHomography` faz um fit enviesado: tenta compensar a distorção radial deformando a projeção, e o erro concentra-se nas bordas — exatamente onde estão os cantos. |

**Consequência prática:** melhorar o detetor de cantos tem retorno decrescente. O ganho está em **mudar a representação**.

---

## 2. Estado da arte — o que já existe (e o que podes reutilizar)

### 2.1 Datasets e benchmarks

| Nome | Desporto | O que tem | Utilidade para ti |
|---|---|---|---|
| **[SoccerNet-Calibration](https://arxiv.org/abs/2404.08401)** | Futebol | ~20k imagens, anotação de **segmentos de linha** (não pontos), GT de parâmetros de câmara, métricas oficiais (JaC@t, Completeness Rate, Final Score) | **O protocolo a copiar.** Anotar segmentos em vez de pontos é a decisão-chave que permite lidar com oclusão. |
| **[WorldCup 2014 / TS-WorldCup](https://arxiv.org/abs/2404.08401)** | Futebol | GT de homografia | Benchmark secundário standard |
| **[TennisCourtDetector](https://github.com/yastrebksv/TennisCourtDetector)** | Ténis | 8841 imgs, 14 keypoints, rede tipo TrackNet (input 640×360, 15 canais de saída), + pós-processamento clássico (extração de pixels brancos → Hough → interseções) | **Arquitetura de arranque mais próxima.** Código aberto, pesos disponíveis. |
| **[PadelTracker100](https://www.sciencedirect.com/science/article/pii/S2352340926000995)** (Data in Brief, 2026) | **Padel** | ~100k frames, WPT Finals 2022, bola, pose (ViTPose-L), **posições reais dos jogadores no campo**, 6 classes de pancada | Tem posições em coordenadas de campo → **implica uma calibração**. Vale a pena pedir/derivar o GT de câmara. [Zenodo](https://zenodo.org/records/14653706) |
| **[Padel Court Detection (Roboflow)](https://universe.roboflow.com/joshs-workspace-p1aa0/padel-court-detection)** | **Padel** | 656 imgs, keypoints | Pequeno, mas serve de *seed* e de baseline honesto |
| **[padel_analytics](https://github.com/Joao-M-Silva/padel_analytics)** (João) | **Padel** | Pipeline YOLO; **12 keypoints selecionados manualmente numa UI** | O baseline a bater. O custo humano por vídeo é o problema. |
| **[KaliCalib](https://arxiv.org/pdf/2209.07795)** | Basquete | Registo de campo por dicionário de keypoints | Boas ideias para campos pequenos e fechados |
| **[Tese "Padel court detection system"](https://www.diva-portal.org/smash/get/diva2:1770685/FULLTEXT01.pdf)** (DiVA) | **Padel** | OpenCV clássico: pré-processamento + contornos + homografia | Leitura obrigatória: mostra os limites da via clássica pura |

### 2.2 Métodos (por ordem de relevância para padel)

| Método | Ideia central | Porque interessa |
|---|---|---|
| **[TVCalib](https://arxiv.org/abs/2207.11709)** (WACV'23) | Não estima homografia; **calibra a câmara** (pose + focal) minimizando o **erro de reprojeção de segmentos** com uma função objetivo diferenciável. Não precisa de treino na parte de calibração. | **O método mais adequado ao teu caso.** Funciona com o que estiver visível. Não precisa de cantos. Podes agregar máscaras de linhas de N frames. |
| **[PnLCalib](https://arxiv.org/abs/2404.08401)** (2024/25) | Modelo 3D do campo + grelha de keypoints **derivada geometricamente** (interseções linha-linha, incluindo pontos *fora* do campo) + refinamento não-linear conjunto com pontos **e** linhas | Introduz explicitamente os **keypoints virtuais** — a resposta direta ao teu "cantos cortados". Código aberto. |
| **[No Bells, Just Whistles](https://www.researchgate.net/publication/384420344)** / **[Enhancing Soccer Camera Calibration Through Keypoint Exploitation](https://arxiv.org/html/2410.07401v1)** | Multiplica os pontos utilizáveis explorando interseções linha-linha e linha-cónica | Mesma família. Padel não tem círculos, mas tem **muitas linhas + arestas de parede** |
| **[Nie et al., WACV'21](https://openaccess.thecvf.com/content/WACV2021/papers/Nie_A_Robust_and_Efficient_Framework_for_Sports-Field_Registration_WACV_2021_paper.pdf)** (Amazon) | **Grelha uniforme de keypoints** por todo o campo (não só cantos) + **mapas densos de distância às linhas**, alinhados por *warp* diferenciável. Multi-task, tempo real. | **A ideia mais subestimada.** Se cada pixel de chão visível dá uma correspondência, os cantos tornam-se irrelevantes. |
| **[TacticalCalib](https://openaccess.thecvf.com/content/WACV2026/papers/Fan_TacticalCalib_End-to-End_6-DoF_Camera_Pose_Regression_for_Tactical_Camera_Calibration_WACV_2026_paper.pdf)** (WACV'26) | **Regressão direta da pose 6-DoF** a partir de uma vista tática (câmara fixa e ampla). Localização sub-pixel por offsets para robustez a oclusão. | A "tactical camera" **é** a câmara de padel. SOTA em JaC@5. |
| **[Can Geometry Save Central Views?](https://arxiv.org/abs/2504.20052)** (2025) | Método *bottom-up* geométrico para vistas onde faltam interseções | Exatamente a filosofia "quando não há cantos, usa a geometria" |
| **VP / Manhattan** ([ICCV'25 workshop](https://openaccess.thecvf.com/content/ICCV2025W/CALIPOSE/papers/Kosaka_Direct_Camera_Calibration_from_Vanishing_Points_via_Polynomial_Solvers_ICCVW_2025_paper.pdf)) | Focal + rotação a partir de 2–3 pontos de fuga ortogonais | O campo de padel é um mundo de Manhattan perfeito (comprimento ⟂ largura ⟂ postes verticais) |

---

## 3. As sete vias, avaliadas para padel

| # | Via | Sobrevive a cantos cortados? | Custo | Veredicto |
|---|---|---|---|---|
| A | 4 keypoints + `findHomography` (atual) | ❌ Não | Baixo | Baseline. Descartar. |
| B | ~16 keypoints + RANSAC sobre o subconjunto visível (filtrar por confiança) | ⚠️ Parcial (precisa de ≥4 visíveis) | Baixo | **Quick win.** Faz isto esta semana. |
| C | Heatmap em **canvas expandido** (prever keypoints fora do frame) | ✅ Sim | Médio | Truque barato e eficaz: treina o heatmap num canvas 2× e permite âncoras negativas |
| D | **Homografia a partir de linhas** (DLT com linhas, ≥4 linhas) | ✅ Sim | Baixo-médio | Robusto, clássico, subestimado |
| E | **Segmentação de linhas/paredes + otimização tipo TVCalib** | ✅ Sim | Médio | **A via principal.** Sem keypoints, sem cantos. |
| F | **Modelo 3D + solvePnP** (paredes, postes, rede) | ✅✅ Sim, por construção | Médio | **A jogada específica de padel.** Ninguém está a fazer isto. |
| G | Regressão densa de **coordenadas de campo por pixel** (cada pixel de chão → (x,y) em metros) | ✅✅ Sim | Alto (dados) | O teto de qualidade. Faz sentido a médio prazo. |

**Recomendação: B (agora) → E+F combinados (o objetivo) → G (se justificar).**

---

## 4. Fora da caixa — as ideias específicas do padel

### 4.1 Usar a caixa (literalmente)
O padel é o único desporto de raquete com uma **estrutura 3D rígida e normalizada** à volta do campo:

- Chão: 20,00 × 10,00 m (tolerância 0,5 %)
- Linha de serviço: 6,95 m da rede (⇒ 3,05 m da parede de fundo)
- Rede: 0,88 m ao centro, 0,92 m nos postes laterais
- Paredes de fundo: 3 m de vidro; laterais degradam 3 m → 2 m em direção à rede; malha metálica até 4 m nos cantos

Isto dá-te, para além dos ~16 pontos de chão, mais **~12–16 pontos 3D fora do plano**: topos de vidro, cantos superiores da estrutura, bases e topos dos postes de canto, topos dos postes da rede. **Estes pontos estão altos — são os últimos a sair do enquadramento e nunca são tapados por jogadores.** Quando os cantos do chão desaparecem, os cantos *superiores* das paredes ainda lá estão.

> **Regra de ouro do padel: quando o chão falha, sobe.**

### 4.2 A câmara é fixa → calibra uma vez, valida sempre
- Deteta em **N=300 frames** espalhados pelo vídeo, agrega por mediana + RANSAC temporal.
- Escolhe preferencialmente **frames sem jogadores em campo** (entre pontos): oclusão zero. Podes identificá-los com o detetor de jogadores que já tens.
- Guarda a calibração por `(court_id, camera_id)`. Nos vídeos seguintes do mesmo campo, **começa da calibração guardada** e só refina.
- Métrica nova e barata: **drift detection** — se o erro de reprojeção do modelo salta, alguém mexeu na câmara.

### 4.3 A rede como régua vertical
A rede tem uma **curva catenária conhecida** (0,88 centro → 0,92 pontas) e é sempre visível. Dá-te escala vertical e um forte constraint de pose mesmo em close-ups.

### 4.4 Pontos de fuga a partir das paredes
As arestas horizontais do vidro (topo e base) são paralelas às linhas do chão → **reforçam o mesmo VP** com linhas muito mais longas e muito mais limpas que as linhas pintadas. E os postes verticais dão o **VP vertical** → focal + rotação a partir de um único frame, sem qualquer canto.

### 4.5 Distorção não é opcional
Modela pelo menos `k1, k2`. Teste diagnóstico de 2 minutos: **pega numa linha longa do campo (a linha lateral), ajusta uma reta aos seus pixels e mede o resíduo máximo.** Se for > 2–3 px, tens distorção significativa e nenhuma homografia planar te vai salvar.

### 4.6 O vidro trai-te (e ajuda-te)
- **Contra:** reflexos no vidro criam linhas falsas e "jogadores fantasma" que envenenam o Hough e os heatmaps.
- **A favor:** o vidro é uma **superfície plana conhecida** — reflexos de linhas do campo no vidro são geometricamente previsíveis, e um modelo treinado com estas imagens aprende a ignorá-los. Inclui isto como uma condição explícita no benchmark.

### 4.7 Auto-supervisão quase de graça
A câmara é fixa e o campo é rígido. Podes gerar **dados sintéticos ilimitados**: renderiza o modelo 3D do campo com poses/focais/distorções amostradas + fundos reais + oclusões sintéticas (recortes de jogadores) + **crops agressivos que cortam cantos de propósito**. É a forma mais barata de ensinar o modelo a viver sem cantos.

### 4.8 Anotar de forma esperta
Não anotes pontos. **Anota polilinhas** (linhas do chão + arestas de vidro). Depois:
- os pontos (incluindo os que estão fora do frame) saem de **interseções analíticas** — de graça;
- e ficas com o GT no formato certo para TVCalib/PnLCalib.

Isto é exatamente o que o SoccerNet faz, e é a razão pela qual eles conseguem "encontrar pontos ocultos ou fora dos limites".

---

## 5. Proposta de benchmark: **PadelCal**

### 5.1 Dados

| Eixo | Cobertura mínima |
|---|---|
| Campos | ≥ 12 campos distintos (cores diferentes: azul, verde, cinza) |
| Câmaras | ≥ 2 posições por campo (fundo alto, canto) |
| Ambiente | indoor / outdoor, dia / noite / luz artificial |
| Split | **Held-out por campo** — treinar em campos A–H, avaliar em I–L. É o único split honesto. Um split aleatório por frame dá números lindos e inúteis. |

**Frames:** ~2 000 anotados chega, se forem bem escolhidos (estratificados pelas condições abaixo).

### 5.2 Condições etiquetadas (o coração do benchmark)

Cada frame recebe *tags*, e os resultados são reportados **por tag**, não só em média:

- `corners_out`: 0 / 1 / 2 / 3 / 4 cantos do chão fora do enquadramento
- `occlusion`: nº de keypoints tapados por jogadores
- `glare`: reflexo/sol no vidro
- `wet`: chão molhado (reflexos especulares)
- `low_light`
- `distortion`: fisheye forte / moderado / baixo
- `empty_court`: sem jogadores (caso fácil de controlo)

> Um método que ganha em `corners_out=0` e colapsa em `corners_out=2` **não serve**. É por isso que a média global é uma métrica traiçoeira.

### 5.3 Ground truth (receita prática)

1. Anotar **polilinhas** de todas as linhas de chão visíveis **e** das arestas de vidro/postes.
2. Ajustar `(K, k1, k2, R, t)` minimizando o erro de reprojeção segmento-a-segmento contra o **modelo 3D do padel**.
3. Validação humana: sobrepor o wireframe 3D renderizado; rejeitar se desalinhar visivelmente.
4. Congelar como GT. Os keypoints (incluindo os fora do frame) derivam analiticamente.

### 5.4 Métricas

| Métrica | O que mede | Porquê |
|---|---|---|
| **JaC@t (t=5 px)** | Jaccard entre máscara do campo reprojetada e GT | Comparável com SoccerNet |
| **Completeness Rate (CR)** | % de frames com calibração produzida | Um método que desiste em 40 % dos frames não é bom, é só seletivo |
| **Final Score = CR × JaC@5** | — | Impede o *cherry-picking* |
| **🎯 Erro no chão (cm)** — *a métrica que importa* | Erro médio e p95 em **metros** numa grelha 1×1 m no chão do campo | É isto que estraga a tua analítica. 5 px na parede de fundo ≈ 40 cm. |
| **Erro de posição do jogador** | Erro dos pés em 4 posições canónicas (2 fundo, 2 rede) | Métrica de produto |
| **Jitter temporal** | Desvio-padrão da reprojeção de um ponto fixo ao longo de frames (câmara fixa!) | Deteta calibrações instáveis que a média esconde |
| **Runtime** | ms/frame + s/vídeo (com calibração amortizada) | — |
| **Custo humano** | cliques necessários por vídeo | O baseline atual custa 12 cliques. Zero é o objetivo. |

### 5.5 Baselines a correr (por ordem)

0. **Manual 12 pontos** (`padel_analytics`) — o teto humano
1. Hough + VP clássico (a tese DiVA)
2. TennisCourtDetector re-treinado para padel (heatmap, 16 kpts)
3. YOLOv11-pose 16 kpts + filtro de confiança + RANSAC no subconjunto visível
4. + canvas expandido (keypoints fora do frame)
5. PnLCalib adaptado (modelo 3D de padel + keypoints virtuais)
6. TVCalib adaptado (segmentos, sem keypoints)
7. **Híbrido proposto:** segmentação de linhas+paredes → VP → solvePnP no modelo 3D → refinamento por segmentos → agregação temporal

---

## 6. Plano de execução (o que fazer na prática)

**Semana 1 — diagnóstico (barato, decide tudo)**
- [ ] Correr o teste de distorção (§4.5) num frame de cada câmara MATCHi que tens.
- [ ] Contar, em 50 frames aleatórios, quantos dos 4 cantos do chão estão fora do frame ou tapados. **Se a resposta for "quase sempre ≥1", a via F é obrigatória.**
- [ ] Medir o erro em cm da calibração manual atual: coloca um ponto conhecido (linha de serviço) e mede a reprojeção.

**Semana 2 — quick win (via B)**
- [ ] Definir os **16 keypoints de chão + 12 keypoints 3D** do modelo de padel num ficheiro `padel_court_model.json`.
- [ ] Anotar ~300 frames com polilinhas (não pontos).
- [ ] Treinar YOLO-pose / heatmap; na inferência usar **todos** os keypoints com conf > 0,5 + RANSAC. Já não precisas exatamente dos cantos.

**Semana 3–4 — a via principal (E + F)**
- [ ] Segmentar linhas + arestas de vidro (modelo leve de segmentação).
- [ ] `solvePnP` sobre o modelo 3D + refinamento por erro de segmento (TVCalib-style), com `k1,k2`.
- [ ] Agregação temporal sobre frames de campo vazio.

**Sempre**
- [ ] Reportar **sempre** por tag `corners_out`. É esse o teste.

---

## 7. O que ninguém tem (a oportunidade)

Não existe um **PadelCal** público. Se construíres o dataset com anotação de segmentos + GT de câmara 3D + tags de dificuldade, tens:
- o primeiro benchmark de calibração de padel,
- um artigo submetível (CVsports / MMSports workshop),
- e, mais prosaicamente, o ativo que torna todo o resto do pipeline (bola, fases de jogo, deteção de serviço) fiável — porque **tudo o que fazes a jusante está construído em cima da calibração**.

---

## Fontes

- [PnLCalib: Sports Field Registration via Points and Lines Optimization (arXiv 2404.08401)](https://arxiv.org/abs/2404.08401)
- [TVCalib: Camera Calibration for Sports Field Registration in Soccer (arXiv 2207.11709, WACV'23)](https://arxiv.org/abs/2207.11709)
- [TacticalCalib: End-to-End 6-DoF Camera Pose Regression for Tactical Camera Calibration (WACV 2026)](https://openaccess.thecvf.com/content/WACV2026/papers/Fan_TacticalCalib_End-to-End_6-DoF_Camera_Pose_Regression_for_Tactical_Camera_Calibration_WACV_2026_paper.pdf)
- [A Robust and Efficient Framework for Sports-Field Registration (Nie et al., WACV 2021)](https://openaccess.thecvf.com/content/WACV2021/papers/Nie_A_Robust_and_Efficient_Framework_for_Sports-Field_Registration_WACV_2021_paper.pdf)
- [Can Geometry Save Central Views for Sports Field Registration? (arXiv 2504.20052)](https://arxiv.org/abs/2504.20052)
- [Enhancing Soccer Camera Calibration Through Keypoint Exploitation (arXiv 2410.07401)](https://arxiv.org/html/2410.07401v1)
- [KaliCalib: A Framework for Basketball Court Registration (arXiv 2209.07795)](https://arxiv.org/pdf/2209.07795)
- [Direct Camera Calibration from Vanishing Points via Polynomial Solvers (ICCVW 2025)](https://openaccess.thecvf.com/content/ICCV2025W/CALIPOSE/papers/Kosaka_Direct_Camera_Calibration_from_Vanishing_Points_via_Polynomial_Solvers_ICCVW_2025_paper.pdf)
- [PadelTracker100: A dataset for intelligent player and ball tracking in padel sports (Data in Brief, 2026)](https://www.sciencedirect.com/science/article/pii/S2352340926000995) · [Zenodo](https://zenodo.org/records/14653706)
- [TennisCourtDetector (GitHub)](https://github.com/yastrebksv/TennisCourtDetector) · [TennisProject](https://github.com/yastrebksv/TennisProject)
- [padel_analytics (João M. Silva, GitHub)](https://github.com/Joao-M-Silva/padel_analytics)
- [Padel Court Detection — Roboflow Universe (656 imgs, keypoints)](https://universe.roboflow.com/joshs-workspace-p1aa0/padel-court-detection)
- [Padel court detection system (tese, DiVA)](https://www.diva-portal.org/smash/get/diva2:1770685/FULLTEXT01.pdf)
- [Real time tracking of Padel game movements (FEUP)](https://repositorio-aberto.up.pt/bitstream/10216/156035/2/653052.pdf)
- [Official Padel Court Dimensions (FIP)](https://www.padel.build/en/regulations/court-dimensions) · [LTA Padel Court Data Sheet](https://www.lta.org.uk/4ad2a4/siteassets/play/padel/file/lta-padel-court-guidance.pdf)
- [Camera Calibration in Sports with Keypoints (Roboflow)](https://blog.roboflow.com/camera-calibration-sports-computer-vision/)
