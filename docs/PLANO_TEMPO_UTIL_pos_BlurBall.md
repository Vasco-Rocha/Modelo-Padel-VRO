# Plano — Tempo Útil com o BlurBall (pós-validação)

**Objetivo final:** detetar o **tempo útil** — cortar o vídeo em rallies e medir quanto é jogo a decorrer, contra o ground-truth de **117s / 12 rallies** (`ground_truth_parada4.md`). Alvo: recall ≥67%, precisão ≥73%, tempo útil ~117s.

## Onde estamos (resumo)
- **Detetor de bola: RESOLVIDO.** O BlurBall (temporal) bate o YOLO out-of-box (recall dentro dos rallies 85.6% @thr0.4 vs 67%), sem pontos cegos. Via A (fine-tune YOLO) morta.
- **Novo gargalo: SEGMENTAÇÃO / DETEÇÃO DE SERVIÇO.** No A/B do tempo útil (thr0.4), o recall subiu (73%) mas a precisão desabou (41%) e o segmentador colou tudo em **3 mega-rallies** (205.8s). Porquê: as regras v9 separam pontos pelo **serviço** e fundem gaps de bola. Com o BlurBall a bola está detetada quase sempre (bola real, também entre pontos) → não há gaps → e a deteção de serviço não corta → mega-rallies.
- Conclusão: as regras de gap eram muleta do detetor fraco. Com detetor forte, o que separa os pontos tem de ser a **deteção de serviço** (fiável), não a ausência de bola.

## Passos

### Passo 1 — Varrimento de limiar (barato, EM CURSO)
Correr o A/B do tempo útil a **thr 0.7 e 0.5** (reusando os `player_boxes`). Ver se há ponto de operação onde a precisão recupera (~73%) com recall ≥67%.
- **Se sim** → ganho interino: BlurBall + esse limiar já bate o baseline. Fixa-se como detetor de operação.
- **Se não** → confirma que o problema é a segmentação (não o limiar) → Passo 2.
- *Entregável:* tabela recall/precisão/falsos/tempo útil por limiar.

### Passo 2 — Deteção de SERVIÇO baseada na BOLA (o desbloqueio real — "M3")
Re-fazer a heurística de serviço **mais na trajetória da bola (BlurBall), menos no jogador** (que é frágil). Assinatura do serviço na bola:
- bola emerge de perto do servidor na zona de serviço (`serve_zone_y=[(335,421),(54,140)]`, 960×540);
- **ressalto no solo** antes da raquetada (sinal-chave; já é TODO em `servico_valido()`);
- arranque de movimento/rasto (o L/Theta do BlurBall);
- no padel a bola NÃO sobe — o sinal é o arranque horizontal.
- **[Vasco tem ideias concretas para esta heurística — a detalhar.]**
- *Medir:* serviços detetados vs os 12 serviços reais (início de cada rally no GT).

### Passo 3 — Re-segmentar o tempo útil com serviço fiável
Com serviços a separar os pontos corretamente, re-correr `rallies_bola` (BlurBall + serviço novo) e medir vs 117s.
- *Alvo:* ~12 rallies, recall ≥67%, precisão ≥73%, tempo útil ~117s, sem mega-rallies.

### Passo 4 — (Só se preciso) Fine-tune do BlurBall (Passo 2 do plano BlurBall)
Em espera. Só se, depois da segmentação estar boa, o recall do detetor for o fator limitante. Provavelmente não urgente.

### Passo 5 — Módulos seguintes
M3 completo (pancadas/serviço treinado), fases de jogo, etc. — depois do tempo útil fechado.

## Divisão de trabalho (conversas)
- **Decisões (esta):** rumo, interpretação de números, spec dos passos.
- **BlurBall (Opus build):** executar inferência, integração, segmentação, medir. Traz números.
- **Sonnet (mecânica):** edições repetitivas, manifests, listas.

## Ficheiros-chave
`rallies_bola.py` (regras v9 + `servico_valido()` TODO), `ground_truth_parada4.md` (117s/12 rallies + serviços), `traj.csv` (bola BlurBall 960×540), `colab_validar_best_v2.ipynb` (pipeline A/B reutilizável).
