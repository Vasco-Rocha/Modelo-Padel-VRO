# 🗓️ FECHO — 14 JUL 2026 · **INFRAESTRUTURA**

> *(ficheiro separado do `FECHO_14JUL.md`, que é sobre a GEOMETRIA. Este é sobre
> o dia em que o Mac crashou — e porque foi a melhor coisa que podia ter acontecido.)*

---

## 🩸 O QUE ACONTECEU

Kernel panic no MacBook Air (**16 GB**). O BlurBall a pedir **18 GB**.
O paniclog apontava para o driver wireless (`AppleCentauriManager`), mas mesmo ao lado:
`compressor 100% of segments limit (BAD), 44 swapfiles`. **Memória esgotada.**

**Não era um bug. Eram DOIS. E nenhum se resolvia com mais RAM.**

---

## 🔴 DOENÇA 1 — a RAM (o heatmap)

`blurball/src/runners/inference.py` guardava o **mapa de calor 288×512 de CADA frame**
(~590 KB) num dicionário que **nunca era limpo**.

E guardava-o **para depois o reduzir a UM FLOAT** (o pico — o patch do `score`).

Pior: guardava-o mesmo com a visualização **desligada** (`vis_hm=False`) ⇒
**pagavam-se 9,5 GB de RAM por imagens que nunca chegavam a ser desenhadas.**

**⇒ CORRIGIDO:** guarda-se o **pico** à medida (**8 bytes**). O heatmap completo só
se `vis_result` ou `vis_hm` estiverem ligados.

## 🔴 DOENÇA 2 — o DISCO (os PNGs)

O BlurBall **descomprimia o vídeo inteiro para PNGs no disco** (1,7 MB/frame) e só
depois os voltava a ler, um a um.

*(O detetor de **jogadores já lia o vídeo em streaming**. Só a bola é que não.)*

**⇒ CORRIGIDO:** `utils/preprocess.py::iter_frames()` — lê o vídeo frame a frame.
**Zero PNGs** (só se a visualização os pedir, porque o `vis` faz `imread`).

## 🟠 DOENÇA 3 — a mesma, nos JOGADORES

`padel_analytics/correr_jogadores_mac.py` acumulava **todas** as deteções (`todos`),
fazia uma **segunda cópia** (`serial`), e só então escrevia o JSON.
**13,95 deteções/frame ⇒ 2,3 MILHÕES num jogo de 1h30.**

**⇒ CORRIGIDO:** o JSON escreve-se **à medida**. Memória constante.
🔜 **por VERIFICAR no Mac** — `VERIFICAR_JOGADORES.command`

---

## 📊 O ANTES E O DEPOIS — **um jogo de 1h30**

| | antes | depois |
|---|---|---|
| 🧠 **RAM (bola)** | **18 GB → kernel panic** | **513 MB** |
| 💾 **disco** | **~270 GB** ⛔ | **0** |
| ⏱️ **bola** | 4,8 h | **4,3 h** |
| ⏱️ **jogadores** | 4,4 h | 4,4 h |
| | **IMPOSSÍVEL** | **≈ 8,6 h — uma noite** |

## 🔒 E O MODELO NÃO MUDOU

```
md5 do traj ANTES:  dfa4d9262f3c9d57499d1fdb107e7239
md5 do traj DEPOIS: dfa4d9262f3c9d57499d1fdb107e7239

teste_regressao:  recall 96.8 · precisao 95.4 · 13/13 · fim_dentro 0   ✅ VERDE
```

**Byte a byte. Foi essa a única prova aceite.**

---

## ⚖️ A DECISÃO DE INFRAESTRUTURA — **medida, não opinada**

> ## ❌ **NÃO se justificam GPUs online. NÃO se justifica um Mac de 32 GB.**

- **32 GB** teriam **escondido** os bugs, não resolvido: os 18 GB caberiam, e o
  problema só apareceria no primeiro jogo a sério — a pedir **~95 GB**.
- **GPU online** resolve o **tempo** — e o tempo (**8,6 h**) **cabe numa noite**.
  Pagar para ver o resultado umas horas mais cedo, uma vez por jogo, **não vale**.
- **O que impedia o 1h30 não era RAM nem GPU. Era o DISCO — e era um bug.**

---

# 📏 A LEI NOVA — **D19**

> ## 📏 **MEDIR O CUSTO ANTES DE ESCALAR.**
> **Nenhum componente entra num vídeo longo sem três números medidos num curto:**
> **`frames/s` · `pico de RAM` · `disco por frame` — e a extrapolação escrita ao lado.**
>
> *Todo o pipeline foi construído e afinado em vídeos de 3 e 9 minutos.*
> *Ninguém fez a conta para o alvo real — e o alvo real **nunca teria corrido**.*
> *Um componente que corre bem em 3 minutos e nunca foi extrapolado é uma bomba*
> *com um temporizador de **18×**.*

**Custa 15 minutos por componente.** Hoje teria poupado um kernel panic.

## 🩹 E uma lição pequena que mordeu na mesma

> **Um backup DENTRO da pasta que se vai apagar NÃO É UM BACKUP.**
> O macOS **não distingue maiúsculas**: `run_Parada4` e `run_parada4` **são a mesma pasta**.
> O `rm -rf` do meu próprio script de verificação apagou o meu próprio backup.
>
> *Salvou-nos a **lição 2 de 13 jul**: **os dados do estado travado vivem DENTRO do repo.***
> *O `data/parada4/traj_frames_Parada4_thr04.csv` era a cópia que não podia morrer — e não morreu.*

---

---

# ⛔ VIA FECHADA — **`step=3`**   *(medida, 14 jul. NÃO REPETIR.)*

O BlurBall vê cada frame em **3 janelas** (`step=1`). Com `step=3` vê-o **uma vez**
⇒ **3× mais rápido: 13m48 → 4m29** *(um jogo de 1h30: 4,3 h → **1,3 h**)*.

**E destrói o modelo:**

```
                travado    step=3
recall            96,8      77,5     <<<  −19,3
precisao          95,4      91,4     <<<   −4,0
servicos            13        11     <<<  PERDEU 2 SERVIÇOS
n_pontos            13        12     <<<  PERDEU UM PONTO
fim_dentro           0         3     <<<  ⛔⛔ O PIOR ERRO POSSÍVEL (D15)
```

**O `fim_dentro = 3` fecha a discussão sozinho** — três "fins certos" a cair **a meio
de um ponto**. Mesmo com o recall intacto, bastava.

## 🔑 E porquê — o número que explica tudo

```
step=1:  19 805 candidatos em 8741 frames  =  2,27 / frame
step=3:   7 109 candidatos em 8739 frames  =  0,81 / frame   ← MENOS DE UM
```

> **O `step=1` não é desperdício. É o que faz o modelo VER.**
> Cada frame passa por 3 janelas e fica-se com o **máximo** das três (é o `score`).
> Com `step=3`, em quase metade dos frames **não se vê NADA**.
>
> **As 3 horas por jogo não são um custo. São o preço do SINAL.**
> *(Lição 8: "não se afina o detetor — muda-se a pergunta.")*

---

## 🔜 O QUE FICA ABERTO
| 🧐 **2,27 candidatos/frame** | o próprio aviso no código diz: *"se for 1-2, o LIMIAR está a matar os candidatos antes do tracker"*. **2,27 está perto disso.** Fio por puxar. |
| 👥 **13,95 deteções/frame** | o detetor vê ~14 pessoas (4 jogadores + ~10 de público). É o esperado (**D9**) — **mas a estrutura que devia limpar, a cascata J1→J5, ainda não corre.** |
| ⛔ **o que NÃO se fez** | usar os jogadores (mais baratos) para **cortar** onde a bola corre. **Viola a D18** (*nenhuma regra veta um candidato*) e a diretriz (*nunca perder um ponto*). **Só depois da cascata J estar validada.** |

---

## 🛠️ OS SCRIPTS QUE FICARAM

| | |
|---|---|
| `VERIFICAR_STREAMING.command` | ✅ **corrido** — md5 igual, 0 PNGs, 13m48 |
| `VERIFICAR_HMFIX.command` | ✅ corrido *(e depois corrigido: o `rm -rf`)* |
| `CRONOMETRAR_JOGADORES.command` | ✅ corrido — 10,25 fps, 923 MB |
| `VERIFICAR_JOGADORES.command` | 🔜 **por correr** — prova o patch da memória dos jogadores |
| `MEDIR_STEP3.command` | 🔜 **por correr** — vale as 3 h que poupa? |
| `LIMPAR_PNGS.command` | 🔜 apaga os ~27 GB de PNGs velhos do Barbosa |

---

> # 🚪 **E O GARGALO DO MODELO NÃO MEXEU.**
> **RAQUETE / PAREDE / CHÃO** — quatro regras dele param na mesma porta.
> **🔊 O ÁUDIO resolve as três de uma vez. GRAVAR COM ÁUDIO.**
>
> **Nada do que se fez hoje lhe toca.** Hoje tirou-se **uma pedra do caminho** —
> uma pedra que ninguém sabia que lá estava, e que teria parado tudo no primeiro
> jogo a sério.
