# ⛔ ESTE FICHEIRO ESTÁ MORTO. NÃO ESCREVAS AQUI.

# 👉 A FONTE É:  `padelpro-vision/data/ground_truth/ground_truth_parada4.md`

O ground-truth é **DADOS**, não documentação — é a **régua**, não um texto sobre a régua.
E o `docs/` já provou ser o sítio onde as coisas apodrecem sem ninguém ver.

## 🚨 O que estava aqui (13 jul 2026) — não repetir

**Tinha 12 rallies. O ground-truth tem 13.** Havia **três** cópias: **as duas erradas eram as
que iam para o GitHub**; a certa estava na raiz, que **não é versionada**.

> **A régua é de tudo. Se está errada, TUDO o que se mede está torto.**

## ⚠️ NÃO ESTÁ CURADO

A régua que **CORRE** é o `GT = [...]` **hard-coded** no `gerar_tempo_util.py` (linha 33).
Estes `.md` **não estão ligados a nada** — foi por isso que duas cópias puderam estar erradas
durante semanas sem nada gritar.

> **Um documento que ninguém lê não tem como estar certo. Só tem como estar desatualizado.**

**A cura:** o código passa a **LER** `data/ground_truth/<video>.md`. Mesma peça que a calibração
(`calibracao_<video>.json`). **Decisão do Vasco: fazer junto com o VÍDEO 2**, que obriga a isso de
qualquer maneira — não mexer no pipeline duas vezes.
