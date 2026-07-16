#!/usr/bin/env python3
"""🦶 J1 — OS PÉS NO POLÍGONO.  Tira o PÚBLICO das boxes dos jogadores.

    "DETETAR GENEROSAMENTE, LIMPAR PELA ESTRUTURA." (J14)
    "O critério é a GEOMETRIA: os PÉS no polígono." (D10 — a lição do max_det=4)

Os PÉS = o ponto médio da ARESTA INFERIOR da box (F3: o contacto com o SOLO).

⚠️ A ARMADILHA (J5 + C4): quando o jogador é cortado pela BORDA INFERIOR do frame,
   a aresta de baixo da box DEIXA DE SER OS PÉS — passa a ser a borda do vídeo.
   Julgá-lo pelos "pés" atirava-o fora. E são os de baixo, os que jogam à rede.
   ⇒ Uma box que TOCA a borda inferior julga-se pelo X (a coluna), não pelo Y.

NÃO altera o gerar_tempo_util.py. Escreve um ficheiro NOVO.
    python3 limpar_boxes_J1.py
"""
import json, pickle, sys
from matplotlib.path import Path

B = ".."
POLI = f"{B}/dados_barbosa/poligono_barbosa.json"
DENTRO = f"{B}/dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl"
FORA = f"{B}/dados_BarbosaMeireles/player_boxes_BarbosaMeireles_J1.pkl"
H_FRAME = 720          # BarbosaMeireles: 1280x720
BORDA = 6              # px: "toca a borda de baixo"

pol = json.load(open(POLI))["poligono"]
path = Path(pol)
xs = [p[0] for p in pol]
XMIN, XMAX = min(xs), max(xs)

d = pickle.load(open(DENTRO, "rb"))
boxes = d["player_boxes"]

novo, antes, depois, cortados = [], 0, 0, 0
for bs in boxes:
    if not bs:
        novo.append([])
        continue
    antes += len(bs)
    keep = []
    for (x1, y1, x2, y2) in bs:
        pe_x, pe_y = (x1 + x2) / 2.0, y2
        if y2 >= H_FRAME - BORDA:
            # 🦶 CORTADO PELA BORDA (J5/C4): os pés não se veem.
            # Julga-se pela COLUNA: o corpo está dentro da largura do campo?
            ok = XMIN <= pe_x <= XMAX
            cortados += ok
        else:
            ok = path.contains_point((pe_x, pe_y))
        if ok:
            keep.append((x1, y1, x2, y2))
    depois += len(keep)
    novo.append(keep)

d["player_boxes"] = novo
d["_J1"] = "pes no poligono (dados_barbosa/poligono_barbosa.json). Box na borda inferior: julgada pelo X."
pickle.dump(d, open(FORA, "wb"))

n = len(boxes)
import collections
c = collections.Counter(len(b) for b in novo)
print("🦶 J1 — OS PÉS NO POLÍGONO")
print(f"   boxes ANTES : {antes:6d}  =  {antes/n:.2f} por frame")
print(f"   boxes DEPOIS: {depois:6d}  =  {depois/n:.2f} por frame   ({100*(antes-depois)/antes:.0f}% eram PÚBLICO)")
print(f"   (salvas pela regra da borda inferior: {cortados})")
print("\n   quantos jogadores por frame, agora:")
for k in sorted(c):
    print(f"      {k}: {c[k]:6d} frames ({100*c[k]/n:5.1f}%)")
q4 = sum(v for k, v in c.items() if k >= 4)
mais = sum(v for k, v in c.items() if k > 4)
print(f"\n   >>> com os 4 jogadores: {100*q4/n:.1f}%   ·   com MAIS de 4 (=ainda ha lixo): {100*mais/n:.1f}%")
print(f"\n-> {FORA}")
