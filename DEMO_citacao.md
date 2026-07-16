# DEMO — o guarda de citação a funcionar
*(ficheiro de teste. Corre: `python3 guarda_citacao.py --demo`)*

## 1) A LEI do Vasco, à letra (deve dar ✅ LEI)
<<CITA D20>>
Quem tem o pé **NA** linha **ainda não a passou**.
<<FIM>>

## 2) As MESMAS palavras da lei, sem formatação (deve dar ✅ LEI)
<<CITA D20>>
Quem tem o pé NA linha ainda não a passou.
<<FIM>>

## 3) Citação ERODIDA — falta uma palavra, muda a caixa (deve dar 🟥 EROSÃO)
<<CITA D20>>
Quem tem o pé na linha ainda não passou.
<<FIM>>

## 4) Texto certo, atribuído à REGRA ERRADA (deve dar 🟥 REGRA ERRADA)
<<CITA S17>>
Quem tem o pé **NA** linha **ainda não a passou**.
<<FIM>>

## 5) Texto REAL da fonte, mas é a MINHA prosa, não a lei marcada (deve dar ⚠️ PROSA)
<<CITA D19>>
A LINHA É A LINHA. NÃO SE PÕE UM LIMIAR EM CIMA DELA.
<<FIM>>
