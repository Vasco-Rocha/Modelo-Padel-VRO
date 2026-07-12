# M3 — Deteção de serviço · estado em 12 jul 2026

## Porque é o M3 e não o threshold da bola
Medido contra o ground-truth (12 rallies / 117 s), com a bola a `thr=0.7`:

- **0** rallies partidos · **0** arranques tardios (2,4 s no total) · maior buraco 0,9 s
- **mas 45 % das deteções de bola (1799 de 4039) caem FORA dos rallies**, em **26 blocos > 2 s**

Essa bola **não é falso positivo — é bola a sério**, do intervalo (apanhar, passar, preparar).
Exemplo: `186,5 s → 196,8 s` (10,2 s, 127 deteções) é exactamente o intervalo entre o rally 7 e o 8.

> **Nenhum detetor de bola distingue bola-em-jogo de bola-no-intervalo. Só a estrutura o faz.**

---

## A regra do Vasco (a chave)

**O serviço é a única jogada em que a bola ressalta obrigatoriamente dos DOIS lados da rede.**

```
RESSALTO (lado A)  →  a bola CRUZA A REDE  →  RESSALTO (lado B, quadrado cruzado)
```

- **Antes** — o servidor deixa-a cair; o serviço é por baixo, tem de ressaltar.
- **Depois** — tem de ressaltar no quadrado antes de o recetor lhe poder bater. É regra do jogo.

Em jogo aberto nada disto é obrigatório (pode-se voleiar). No intervalo a bola pode ressaltar,
mas **do mesmo lado**, e não cruza a rede entre dois ressaltos.

### Corolário (resolve a oclusão)
O ressalto do lado de baixo **pode estar tapado pelo jogador** (observação do Vasco — confirmada:
nos 2,5 s do serviço a trajetória é intermitente, `..XX.XX...X....`, e só fica contínua **depois**).
Mas os dois ressaltos estão **em lados opostos por definição** ⇒ **um deles está SEMPRE em cima**,
o lado que a câmara vê bem.
**Ancorar no ressalto de cima. O de baixo é confirmação opcional — se faltar, não invalida.**

### A formação (Vasco)
Do lado que serve: **um na rede** (o parceiro) e **um atrás da linha** (o servidor, que pode nem
ser visível) — e **depois de servir, o servidor sobe à rede**.
Do lado que recebe: **os dois atrás**.

---

## O que está MEDIDO

Profundidade normalizada: `0` = na rede · `1` = na linha de serviço · `>1` = atrás dela.

**O mais recuado dos 2 de CIMA** (quartis 25/50/75):

| | valor |
|---|---|
| **no serviço** | **1,05 / 1,06 / 1,07** ← ambos atrás, e notavelmente constante |
| em jogo aberto | 0,61 / 0,69 / 0,86 ← subiram à rede |
| no intervalo | 0,76 / 0,93 / 1,06 |

**`cima_max > 1,00` é a assinatura do serviço.** Separa bem de *jogo aberto*; sobrepõe-se
parcialmente ao *intervalo* (é por isso que a formação sozinha não chega).

### Resultado da formação SOZINHA
`cima_max > 1,00 ∧ cima_min > 0,50`, suavizado a 1 s → **6/12 serviços, 27 falsos.**
Insuficiente. **Falta cruzar com a bola.**

### Limitação a resolver
Só **28 %** dos frames de serviço têm as 2 boxes de cima válidas (contra 58 % em jogo).
⇒ aplicar primeiro a cascata de limpeza + **continuidade** (que preenche buracos) antes de ler a formação.

---

## Próximo passo (por fazer)
Combinar os três sinais, que são independentes:

1. **Formação** — `cima_max > 1,0` (os recetores atrás)
2. **Ressalto de cima** — inversão do `Y` da bola no lado de cima *(detetor a reescrever: não pode
   exigir frames seguidos — no serviço não os há)*
3. **A bola cruza a rede** entre os dois ressaltos
4. **(confirmação)** o servidor **sobe à rede** nos 2 s seguintes

Dados prontos: `dados_parada4/traj_frames_Parada4.csv` (bola) ·
`dados_parada4/player_boxes_parada4.pkl` (4 boxes em 52,6 % dos frames) ·
`padelpro-vision/calibracao_campo.json` (campo).
Corre tudo em CPU, em segundos. Não precisa de Colab nem de Kaggle.

## Vídeos de referência (pasta do projeto)
- `OS_12_SERVICOS.mp4` — os 12 serviços com bola + boxes + profundidade. **Validado pelo Vasco.**
- `O_PROBLEMA_intervalo.mp4` — a bola do intervalo, que engana o sistema.
- `BOLA_thr07_rally2.mp4` — a bola a 0.7 num rally.
