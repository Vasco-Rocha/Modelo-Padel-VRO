# ✅ CONCLUÍDO — A CURA DA DOENÇA   *(13 jul 2026)*

> # 🛑 **NÃO VOLTES A ESCREVER O GUARDA. ELE JÁ EXISTE.**
> **`padelpro-vision/verificar_fonte.py`** — feito, testado, e a dar **`✅ FONTE LIMPA`**.
>
> *(Este ficheiro **era** um prompt a mandar construí-lo. Se o leres como tarefa, vais escrever um
> guarda **novo, diferente, por cima do que já corre** — que é **exactamente a doença que ele cura**.
> Por isso deixou de ser prompt e passou a **REGISTO**.)*

---

# 🐕 O GUARDA — como se usa

```bash
cd padelpro-vision
python3 verificar_fonte.py                 # completo (inclui a ablação, ~1 min)
python3 verificar_fonte.py --so-estrutura  # só a estrutura (segundos)
```
**Tem de dar `✅ FONTE LIMPA` (exit 0).** Se der vermelho: **PÁRA e diz ao Vasco.**

**Corre-o SEMPRE, junto com o `teste_regressao.py`.** Ele faz **automaticamente** a 3.ª releitura —
bater as regras contra o código — que é a que ninguém se lembra de fazer à mão.

## As 6 verificações
```
① duplicados      → qualquer nome repetido FALHA (exceto se um for PONTEIRO)
                     ⚠️ "idêntico hoje NÃO é um estado — é uma contagem decrescente"
② ✅ que não corre → a função existe? é CHAMADA com TODOS os argumentos?
                     o interruptor existe, está True, e é LIDO?
③ ablação         → regra que vale +0,0 → AVISA (redundante OU não corre)
④ colisão de nomes → o mesmo ID de regra usado duas vezes
⑤ sinónimos       → RESSALTO = QUIQUE = BOLA NO CHÃO
⑥ 🐕 a COLEIRA    → o GT do código vs o GT do .md. Se divergirem, FALHA.
```

---

# 🦠 A DOENÇA — o que era, e o que custou

> **Uma regra pode estar no mapa, com o nome certo, e fazer outra coisa.**
> **Um ficheiro pode chamar-se "a fonte", e ser uma cópia morta.**

**Mordeu TRÊS vezes em 13 jul:**
1. a **S12** marcada ✅, com o nome certo, **a fazer outra coisa** *(e a S8 marcada ✅ e a não correr)*
2. **duas regras diferentes chamadas `S23`** — a que corre (**+3,5 precisão**) e a que nunca correu
3. **DEZ documentos duplicados**, 4 já divergidos — incluindo o **ground-truth** (o de `docs/` tinha
   **12 rallies**; o certo tem **13**) e a `RECEITA`, que ainda mandava pôr `MIN_PROF=0,35`

**E mordeu quem a estava a curar:** o Claude arrumou 10 duplicados **e criou 4 novos a seguir**.

---

# ✅ O QUE FICOU FEITO — **33 → 0 falhas**

| | |
|---|---|
| **A FONTE ÚNICA** | `padelpro-vision/REGRAS_DO_VASCO.md` — **117 regras**, zero nomes duplicados |
| **O GROUND-TRUTH** | `data/ground_truth/` (13 rallies) — **com COLEIRA** (verificação ⑥) |
| **`m1_tempo_util.py`** | era um **ENGODO VIVO** (a S12 velha lá dentro; 4 regras apontavam para lá). Virou **lápide**. |
| **`B8_VAI_E_VEM` → `B14_VAI_E_VEM`** | o interruptor tinha o nome de **OUTRA** regra (a B8 = coerência temporal, por implementar) |
| **`S18_MAO_PASSE` · `S19_2_TOQUES`** | **interruptores VAZIOS** (sem código atrás) — fora do `REGRAS`. *"Uma regra desligada é uma escolha. **Um interruptor vazio é uma armadilha.**"* |
| **16 duplicados** | a cópia do repo fica; a da raiz vira **ponteiro** |
| **Todos os interruptores** | nomeados no mapa — **SEM números de linha** *(apodrecem: o ficheiro cresceu por baixo e provou-o na hora)* |

## E o guarda **disparou contra quem o escreveu** — 3 bugs a sério
- procurava o ficheiro **só na raiz** ⇒ disse *"o `m1_tempo_util.py` não existe"* — **existia**
- a regex exigia `| **B6** |` e a **B6** está escrita `| B6 |` ⇒ **nunca a leu** ⇒ declarou *"não existe
  regra B6"*. **A B6 é uma regra do Vasco** *("dois cliques dão a direção")* e vale **+10,2 de RECALL.**
  A contagem passou de "83" para as **117** regras reais.
- os ponteiros que ele escreveu **passaram das 30 linhas** ⇒ **`[PONTEIRO QUE CRESCEU]`** contra ele próprio

> **Um guarda que nunca dispara é indistinguível de um guarda que não existe.**
> Este foi **testado contra as 4 doenças REAIS**, injetadas numa cópia em `/tmp`. **Apanhou as quatro.**

---

# 🔴 O QUE FICOU POR CURAR — *de propósito*

## O `GT` continua **hard-coded** no `gerar_tempo_util.py`
A verificação ⑥ (a coleira) **obriga o `.md` a estar certo** — mas o código continua a **NÃO o ler**.

**A cura verdadeira:** o código **lê o ground-truth de um ficheiro**. Aí passa a haver **UMA régua**, e
estragá-la faz o `teste_regressao` **gritar**.

⏳ **Fica para o VÍDEO 2** — que precisa da **MESMA peça** (um GT **e** uma calibração **por vídeo**).
**Não se mexe no pipeline duas vezes para fazer a mesma coisa.**

---

# 🚨 A REGRA QUE NASCEU DISTO: **UMA CANETA DE CADA VEZ**

Hoje **duas conversas escreveram no `gerar_tempo_util.py` ao mesmo tempo.** Deu certo **por SORTE**
(mexeram em sítios diferentes). Da próxima, **uma apaga o trabalho da outra e o `teste_regressao`
continua VERDE** — porque as duas alterações eram, isoladamente, válidas.

> **Só UMA conversa toca no `gerar_tempo_util.py` de cada vez.**
> As outras **leem, medem, criam ficheiros novos.** **Nunca editam.**
>
> **O git não protege disto: a última a gravar ganha, em silêncio.**
