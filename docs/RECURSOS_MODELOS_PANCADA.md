# Recursos: deteção de serviço / pancadas (para M1 e M3)

Nota central: detetar SERVIÇO e PANCADAS a partir da trajetória da bola serve os **dois** módulos:
- **M1 (tempo útil):** melhores cortes — o serviço âncora o início; "há pancada?" resolve o fim/continuação.
- **M3 (pancadas):** classificação completa (tipo + winner/erro).
Ou seja, investir num detetor de pancada/serviço melhora já o tempo útil, não é só trabalho futuro.

## Diretamente padel
- **PadelTracker100** (o dataset que já usamos para a bola) — CC-BY-4.0. Tem anotações de **bola + pose + eventos de pancada (6 classes, inclui `serve`)**.
  - Dataset + notebook: https://zenodo.org/records/14653706
  - Notebook oficial (39 kB, mostra como ler labels de pancada/pose): `explore-padeltracker100-annotations.ipynb`
    - download: https://zenodo.org/records/14653706/files/explore-padeltracker100-annotations.ipynb?download=1
  - Paper: https://www.sciencedirect.com/science/article/pii/S2352340926000995
  - → É daqui que se treina o detetor de serviço/pancadas próprio (M3). Já temos `colab_padeltracker100_explore.ipynb` nosso; o oficial mostra o formato das labels de pancada.
- **guillecartes/Padel-Shot-Classification-and-Dataset** — https://github.com/guillecartes/Padel-Shot-Classification-and-Dataset
  - Público/clonável (arquivado 2021). 13 pancadas, 2000+ shots. Scripts: SVM, CNN 1D, árvore, KNN, rede densa.
  - ⚠️ Parece dataset de **sensores/wearable** (séries temporais), não vídeo. O dataset não encaixa direto; os **métodos** (CNN 1D em série temporal) transferem-se para a trajetória de bola.

## Metodologia mais próxima do nosso sinal (pancada a partir da BOLA) — útil para M1
- **Table Tennis Stroke Detection and Recognition Using Ball Trajectory Data** — https://arxiv.org/pdf/2302.09657
  - Deteta e classifica pancadas SÓ com a trajetória da bola. É o método a imitar para o serviço/hits do tempo útil.

## Via pose (o "gesto do serviço")
- **BST: Badminton Stroke-type Transformer (skeleton-based)** — https://arxiv.org/html/2502.21085v2
  - Reconhecimento de pancada por esqueleto/pose. Referência se formos por RTMPose.

## Ténis (mais maduro; serviço incluído)
- **chow-vincent/tennis_action_recognition** — https://github.com/chow-vincent/tennis_action_recognition
  - Inception V3 + LSTM para classificar pancadas de ténis (inclui serviço). Arquitetura reutilizável.
- **Classification of Tennis Actions Using Deep Learning** — https://arxiv.org/pdf/2402.02545
  - Insight útil: serviço e smash confundem-se (movimento parecido); distinguem-se pelo **estado do jogo e posição do jogador** — confirma usar a posição (servidor atrás da linha) como sinal-chave.

## Benchmarks (para comparar métodos)
- **P2ANet** (deteção densa de ações, ténis de mesa) — https://dl.acm.org/doi/full/10.1145/3633516
- **TTStroke-21 / MediaEval Sports Task** — https://multimediaeval.github.io/editions/2022/tasks/sportsvideo/

## Ordem sugerida
1. M1 primeiro: fechar o tempo útil com as regras da bola (heurística atual).
2. Quando entrar no M3: começar pelos notebooks do PadelTracker100 (labels de pancada) + método do paper de ténis de mesa (trajetória de bola). Pose (BST) e treino dedicado como reforço.
