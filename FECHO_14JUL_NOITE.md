# 🌙 FECHO — 14 JUL, À NOITE
### *O detetor de serviço pelos JOGADORES. E a parede onde tudo bate: a B19.*

> **Documento DATADO. É história, não é estado.**
> **O estado sai de `python3 teste_regressao.py` + `python3 auditar_mentiras.py`. Nada mais.**

---

# ▶️ PARA A PRÓXIMA CONVERSA — LÊ ISTO PRIMEIRO

```
⛔ NÃO TOCAR no gerar_tempo_util.py — outra caneta pode estar lá.
   Livre: servico.py · ficheiros NOVOS · os .md.
⛔ NADA PESADO no Mac (extração de PNGs).

▶️ O ÚNICO PASSO QUE IMPORTA A SEGUIR:  correr  OS_9_CANDIDATOS.command
   (o patch da BOLA — a B19 — escrito e NUNCA corrido. Destrava TUDO o que está abaixo.)
```

---

# 🎾 O QUE SE FEZ HOJE — o detetor de serviço, SÓ com jogadores

A pergunta do Vasco que inverteu tudo: *"e se for ao contrário — partires da S2 (a formação) e
confirmares com as outras regras?"*

**Resultado:** `detetor_servico.py` — 4 regras dele, ZERO bola:
```
S2   a formação diz quem serve   (só um jogador adiantado — SAIR DA DEFESA, não "a rede")
F5   o adiantado tem de ser ESTÁVEL (~1,2 s)   ← a tolerância vive no TEMPO (D19)
S2b  depois do serviço, o servidor CORRE para transição/rede
S30  a formação está PARADA (medido DENTRO da formação, não antes)
```

## ⚖️ O NÚMERO HONESTO — **corrigido na re-auditoria (5 releituras contra o código)**
> ## 🩸 **NUNCA TIVEMOS 23 SERVIÇOS CERTOS. O "21/21" QUE EU CITEI ERA UMA JANELA LARGA
> ## (±3,5 s) A DISFARÇAR-SE DE SUCESSO.** *(a mesma doença de manhã, quando disse "13/13" e
> ## eram espectadores. MEDIR ANTES DE CITAR — falhei-a DUAS vezes.)*

**A decomposição REAL das deteções:**
```
BARBOSA — 23 deteções:   11 no INÍCIO de um ponto (certas) · 1 a MEIO · 11 em INTERVALO (falsas)
PARADA4 — 16 deteções:   10 no INÍCIO de um ponto (certas) · 1 a MEIO ·  5 em INTERVALO (falsas)
```
*(O FECHO dizia antes "Parada4: 13 deteções" — ERRADO, são 16.)*

## ✅ O QUE ESTÁ SÓLIDO (verificado)
- **O detetor de base é SELETIVO:** 23/16 deteções em vídeos de 9/5 min. Não são centenas.
- **~11/~10 delas caem MESMO no início de um ponto.** A parte grossa funciona.
- **A cascata dos jogadores está CERTA** (o Vasco confirmou a olhar: "está sempre bem").
- **13 interruptores · 0 vazios · `teste_regressao.py` intacto.** *(re-auditado)*

## 🔴 O QUE NÃO ESTÁ — e o Vasco confirmou a OLHAR
**~11 (Barbosa) / 5 (Parada4) deteções caem em INTERVALO — e são FALSAS.**
> **O Vasco viu os clips e confirmou: "os últimos serviços que tinhas dúvida se eram falsos,
> eram MESMO falsos".** ⇒ **o detetor TEM falsos positivos a sério.** (NÃO é o GT incompleto.)

## ⚠️ E O GUARDA — tem um erro NOVO (re-auditoria)
`auditar_mentiras.py` marca **B13 e B15 como "mentiras" — e NÃO são** (correm via `cruzamentos()`).
Os meus edits ao `.md` partiram o parser dele. **Um guarda que se engana é pior que nenhum.**
👉 **A CORRIGIR: o parser do guarda, antes de confiar na lista de mentiras.**

---

# 🔑 A DISTINÇÃO QUE ESCLARECE TUDO — **INVARIANTE ≠ DETETOR**
### *(o Vasco apontou a um "21/21" que eu tinha citado e desmontou-o — 14 jul, à noite)*

Eu citei **"21/21"** de DUAS maneiras, como se fosse a mesma coisa. **São duas medições diferentes,
e as DUAS são verdade — mas dizem coisas OPOSTAS.** Medido contra o código:

```
MEDIÇÃO A — NOS 21 momentos de serviço REAIS:
   "exatamente um jogador dos 4 não está em defesa"  →  21/21   ✅  É VERDADE.
   ⇒ o INVARIANTE do serviço (um adiantado, cruzado, servidor corre) está CORRETO.
     Quando SEI que ali há um serviço, a formação prova-o SEMPRE.

MEDIÇÃO B — a MESMA condição, no VÍDEO INTEIRO:
   'um adiantado' aparece em 32% dos frames (5086 de 16138) — NÃO só nos serviços.
   ⇒ o invariante é NECESSÁRIO (todo serviço o tem) mas NÃO SUFICIENTE (o intervalo também).
```

> ## 🩸 **O MEU ERRO:** peguei num invariante VERDADEIRO (medição A) e usei-o como DETETOR
> ## (medição B). **Provar que algo é verdade NOS serviços ≠ conseguir ENCONTRAR os serviços com isso.**

> ## 🔑 **A LEI QUE FICA (nova):** UM INVARIANTE VERDADEIRO NÃO É UM DETETOR.
> ## Uma condição pode valer 21/21 nos eventos e mesmo assim disparar 32% do tempo. Antes de
> ## chamar "detetor" a uma regra, MEDE-A NO VÍDEO INTEIRO, não só nos eventos conhecidos.

### E o que isto NÃO destrói — **o modelo do serviço do Vasco está CERTO**
A medição A é **OURO**: prova que *"um adiantado + cruzado + servidor corre"* descreve **mesmo** o
serviço. **O que falta não é a regra — é o SINAL que a torna ÚNICA.** E esse é a BOLA:
```
NOS serviços:  a formação tem 1 adiantado, é cruzada, o servidor corre — E a bola faz 3 quiques.
NO intervalo:  a formação TAMBÉM tem tudo isso...                       — mas a bola NÃO os faz.
```
> ## **A única diferença FÍSICA entre um serviço e o intervalo está na BOLA. E a bola está partida (B19).**
> # 🚪 **Tudo volta à mesma porta. OS_9_CANDIDATOS.command.**

---

# 🩸 A PAREDE — medida de SETE maneiras esta noite

**Nenhum sinal dos JOGADORES separa o serviço a sério da formação no intervalo.** Testado e medido:

| tentativa | resultado |
|---|---|
| **DIAGONAL** (servidor/recetor lados opostos da central) | 🔴 FALSOS 12/12 passam — quase sempre verdadeiro |
| **CRUZADO** ("existe recetor do lado oposto") | 🔴 12/12 falsos passam *(e tinha um BUG: escolhia o recetor "mais atrás" por 5 px — o Vasco apanhou-o a olhar)* |
| **FORMAÇÃO PARADA** | 🔴 ✅ em TODOS os 23 — não distingue |
| **SERVIDOR CORRE p/ rede** | 🔴 ✅ em TODOS os 23 |
| **RALLY a seguir** (travessias/pancadas em 8s) | 🔴 reais 2,5 · falsos 2,5 — iguais |
| **os 3 QUIQUES da bola** (mão→chão→raquete→quadrado cruzado) | 🔴 4/11 reais — a bola vê metade dos frames |
| **quique FUNDO → RASO** (na caixa de serviço) | 🔴 4/11 reais |

> ## 🔑 **PORQUÊ:** os falsos caem no INTERVALO — e o intervalo NÃO é silêncio, é jogo informal:
> **os jogadores formam-se, param, um arranca, cruzam-se, batem à bola, atravessam a rede.**
> **Aos JOGADORES, o intervalo PARECE um serviço.**

---

# 🎯 A ÚNICA COISA QUE SEPARA — e porque não a temos ainda

> ## **O que distingue um serviço a sério de uma formação no intervalo é UMA coisa:**
> ## **no SERVIÇO, a BOLA faz os 3 QUIQUES. No intervalo, NÃO faz.**

A regra do Vasco (14 jul), na íntegra:
```
① mão → chão → raquete   (quique VERTICAL com mudança de direção após o chão)
② raquete → rede         (quique HORIZONTAL + travessia p/ o quadrado do lado contrário, se válido)
③ quique no CHÃO do lado contrário, no QUADRADO CRUZADO, antes de o recetor bater
+ o servidor entra na zona de transição / aproxima-se da rede
+ servidor à ESQ da central ⇒ recetor à DIR   ·   servidor à DIR ⇒ recetor à ESQ
```
**Esta regra É a solução. E precisa da BOLA — que está partida (B19).**

⇒ **NÃO É PREGUIÇA dizer "vamos à B19".** É o que os dados dizem, medidos sete vezes. **Cada porta
dá ao mesmo sítio:** os jogadores geram o candidato; **só a bola confirma que é serviço a sério.**

---

# ⏱️🔗 A S42 ⊕ S43 — O SERVIÇO É A FRONTEIRA DO PONTO   *(estado: desligada, e porquê)*

**A LEI (fundida hoje):** um ponto começa num serviço e acaba quando vem o seguinte.
- 🔗 **COLA:** dois pedaços sem serviço entre eles = o MESMO ponto.
- ✂️ **CORTA:** um serviço a meio ⇒ o anterior já acabou ⇒ **corta na ÚLTIMA PANCADA COM RAQUETE
  antes do serviço, + 2 s de margem** *(a régua do Vasco, "2 segundos é o melhor")*. **NÃO no serviço.**

**A trava do SILÊNCIO (14 jul, à noite):** só se corta se a pancada foi seguida de silêncio (S12).
**Isto matou o falso dos 64,7 s sem subir o fim_dentro** — o corte ficou CERTO.

**Porque está DESLIGADA:** o detetor de serviço tem 1 falso a meio de um ponto ⇒ o corte parte
esse ponto ⇒ **fim_dentro sobe (D15 proíbe).** ⇒ **destrava quando o detetor não tiver falsos
dentro de pontos — o que só a bola (os 3 quiques) resolve. Volta à B19.**

---

# 🩸 OS MEUS ERROS DE HOJE — para não voltarem

1. **"21/21" mal medido** — contei "há um serviço perto de cada ponto", não "NO serviço". Cada
   deteção cai ~1-2 s ao lado. ⚖️ **MEDIR ANTES DE CITAR.** (Falhei-a nos dois sentidos.)
2. **Boxes erradas ao pipeline** (nocap em vez das limpas) → baseline falso (93 em vez de 96,7).
3. **Polígono aceite sem o bater contra a calibração** — o Vasco apontou-o **3 vezes**.
4. **Bug do recetor "mais atrás"** — escolhia o errado por 5 px. O Vasco apanhou-o a OLHAR.
5. **ATALHEI as regras dele** — o Vasco: *"sempre que atualizo, tu atalhas".* ⇒ nasceu a **D21**.

---

# 📁 FICHEIROS NOVOS (todos correm em segundos, zero Mac)
```
detetor_servico.py     o detetor de serviço (4 regras, zero bola) — 21/21 e 13/13 no nº, falsos por matar
s23_sequencia.py       a cadeia da bola (3 quiques) — lei certa, sinal partido
ligar_s42_s43.py       a fronteira do ponto (cola/corta) — medida, desligada
cascata_jogadores.py   J1→J5 + J16 · fases_m2.py · lei_da_formacao.py · auditar_mentiras.py
poligono_derivado.py   (a tentativa recuada) · calibracao_parada4_v2.json (as costuras, à mão)
```
🖼️ **vídeos:** `DIAGNOSTICO_servicos.mp4` (corrompido — usar) `ERROS_intervalos_h264.mp4` (bom)

---

# 🏁 A LIÇÃO DA NOITE
> ## **Todas as regras do serviço do Vasco estão CERTAS.**
> ## **Todas batem na mesma parede: precisam da BOLA (os 3 quiques) ou do INSTANTE EXATO — e os
> ## dois vêm da bola, que está partida (B19).**
> # 🚪 **A B19 não se resolve com uma regra. Resolve-se a limpar o SINAL. (D12.)**
> # **OS_9_CANDIDATOS.command — é o próximo passo, e é o único.**
