#!/usr/bin/env python3
"""
🎾 S23 — A SEQUÊNCIA DO SERVIÇO   (Vasco, 14 jul)   — v2, com as correções dele

    "Depois do ③, quica na RAQUETE — inversão HORIZONTAL em direção ao campo adversário."
    "O ténis NÃO está sempre parado. A única coisa que podemos dizer é que os ténis estão
     sempre no LIMITE DAS BOUNDING BOXES."

⇒ UMA REGRA, UMA CADEIA. E é a CADEIA que nenhum sapato consegue imitar:

    ⓪  NÃO é um TÉNIS  — a deteção não está no limite inferior de uma box   (B16, dele)
    ①  FUNDA           — lá atrás, na linha de serviço      (é onde o servidor está)
    ②  QUICA NO CHÃO   — inversão VERTICAL   (desce → sobe)  (ele larga a bola)
    ③  BATE NA RAQUETE — inversão HORIZONTAL, EM DIREÇÃO AO CAMPO ADVERSÁRIO
    ④  🔑 só conta o ÚLTIMO **ANTES DE A BOLA MUDAR DE CAMPO**   (o kick, os saltinhos)
    ⑤  e a travessia só vale se vier da RAQUETE (L alto)          (S15 — a da mão vai lenta)

🩸 O ERRO DA v1 (14 jul, apanhado a MEDIR):
   ❌ pus "② a bola está PARADA (L≈0)" como filtro do ténis.  **UM TÉNIS TAMBÉM ESTÁ PARADO.**
      Essa condição separa a bola-na-MÃO da bola-em-VOO — não separa a bola do SAPATO.
      Quem separa o sapato é a GEOMETRIA (B16) e a inversão HORIZONTAL (③).
   ❌ escrevi o "só o ÚLTIMO" como "o último de uma fila de quiques". O ténis gera quiques
      EM CATADUPA (DY_MIN=1px — um sapato a tremer "quica"), a fila nunca acaba, e o "último"
      vai parar a qualquer lado. **O ÚLTIMO É O ÚLTIMO ANTES DA MUDANÇA DE CAMPO.**
      Ele tinha dito a âncora; eu apaguei-a.

⚠️ FICHEIRO NOVO. Não toca no gerar_tempo_util.py.
"""
import csv, json, pickle, sys
import numpy as np

VID = sys.argv[1] if len(sys.argv) > 1 else "barbosa"
CFG = {
    "barbosa": dict(bola="../dados_BarbosaMeireles/traj_frames_BarbosaMeireles_thr04.csv",
                    boxes="../dados_BarbosaMeireles/player_boxes_BarbosaMeireles.pkl",
                    cal="calibracao_BarbosaMeireles.json", fps=29.97002997002997),
    "parada4": dict(bola="data/parada4/traj_frames_Parada4_thr04.csv"   # ⚠️ o MESMO do pipeline (thr=0.4),
                    boxes="../dados_parada4/player_boxes_parada4_mac_nocap.pkl",
                    cal="calibracao_parada4_v2.json", fps=29.97),
}[VID]
FPS = CFG["fps"]
cal = json.load(open(CFG["cal"]))
ev = lambda k, x: float(np.polyval(cal[k], x))

# ---------- os ATALHOS, todos declarados ----------
FUNDA    = 0.70   # ⚠️ ATALHO (= QUIQUE_PROF do pipeline). ① "lá atrás, na linha de serviço"
DY_MIN   = 1.0    # ⚠️ AJUSTE (do pipeline). ② píxeis da inversão VERTICAL
DX_MIN   = 2.0    # ⚠️ ATALHO. ③ píxeis da inversão HORIZONTAL (a raquetada)
JAN_RAQ  = 25     # ⚠️ ATALHO. ③ quantos frames depois do quique procurar a raquetada (0,8 s)
TENIS_BX = 0.18   # ⚠️ ATALHO (a B16 dele). ⓪ os 18% de baixo de uma box = onde vivem os ténis


def carregar():
    R = {}
    for r in csv.DictReader(open(CFG["bola"])):
        if int(r["Visibility"]) and float(r["X"]):
            R[int(r["Frame"])] = (float(r["X"]), float(r["Y"]),
                                  float(r["L"]), float(r["Theta"]))
    boxes = pickle.load(open(CFG["boxes"], "rb"))["player_boxes"]
    return R, boxes


y_rede = lambda x: ev("rede_base_coef", x)
lado = lambda x, y: "baixo" if y > y_rede(x) else "cima"


def prof(x, y):
    """0 = na rede · 1 = na linha de serviço · >1 = atrás dela (o fundo)"""
    yb = y_rede(x)
    ys = ev("servico_perto_coef" if y > yb else "servico_longe_coef", x)
    return abs(y - yb) / max(1e-6, abs(ys - yb))


def e_tenis(f, x, y, boxes):
    """⓪ B16 (Vasco) — «os ténis estão SEMPRE no limite das bounding boxes».
       ⚠️ E NÃO «o ténis está parado» — um ténis mexe-se. A verdade dele é GEOMÉTRICA."""
    if f >= len(boxes):
        return False
    for x1, y1, x2, y2 in boxes[f]:
        if x1 <= x <= x2 and (y2 - TENIS_BX * (y2 - y1)) <= y <= y2 + 4:
            return True
    return False


def sequencia(R, boxes):
    """A CADEIA INTEIRA. Devolve os frames do quique-do-serviço (o do CHÃO)."""
    fs = sorted(R)
    cand = []

    for i in range(1, len(fs) - 1):
        a, b, c = fs[i-1], fs[i], fs[i+1]
        if c - a > 8:
            continue
        xb, yb, _, _ = R[b]

        # ⓪ não é um TÉNIS  (B16 — geometria, não velocidade)
        if e_tenis(b, xb, yb, boxes):
            continue

        # ② QUICA NO CHÃO — inversão VERTICAL (desce → sobe)
        if not (R[b][1] - R[a][1] > DY_MIN and R[c][1] - R[b][1] < -DY_MIN):
            continue

        # ① FUNDA — lá atrás, onde o servidor está
        p = prof(xb, yb)
        if p < FUNDA:
            continue

        # ③ BATE NA RAQUETE — inversão HORIZONTAL, EM DIREÇÃO AO CAMPO ADVERSÁRIO
        #    (a rede está do lado do campo do adversário ⇒ a bola passa a APROXIMAR-SE dela)
        l0 = lado(xb, yb)
        dep = [f for f in fs[i+1:] if f - b <= JAN_RAQ and not e_tenis(f, R[f][0], R[f][1], boxes)]
        if len(dep) < 3:
            continue
        raq = False
        for j in range(1, len(dep) - 1):
            u, v, w = dep[j-1], dep[j], dep[j+1]
            dx1 = R[v][0] - R[u][0]
            dx2 = R[w][0] - R[v][0]
            # inversão HORIZONTAL: o x muda de sentido, com força
            inv_h = (abs(dx1) > DX_MIN and abs(dx2) > DX_MIN and dx1 * dx2 < 0)
            # ...e a seguir aproxima-se da REDE (vai para o campo adversário)
            vai = prof(R[w][0], R[w][1]) < prof(R[v][0], R[v][1]) or \
                  lado(R[w][0], R[w][1]) != l0
            if inv_h and vai:
                raq = True
                break
        if not raq:
            continue

        cand.append((b, l0))

    # ④ 🔑 SÓ O ÚLTIMO **ANTES DE A BOLA MUDAR DE CAMPO** (a âncora que eu tinha perdido)
    fs_set = sorted(R)
    out = []
    for k, (f, l0) in enumerate(cand):
        # a bola muda de campo depois deste quique?
        mud = next((g for g in fs_set if g > f and not e_tenis(g, R[g][0], R[g][1], boxes)
                    and lado(R[g][0], R[g][1]) != l0), None)
        if mud is None:
            continue
        # há outro quique DEPOIS deste e ANTES da mudança de campo? então este não é o último
        if any(f2 > f and f2 < mud for f2, _ in cand):
            continue
        out.append(f)
    return sorted(set(out))


def main():
    R, boxes = carregar()
    S = sequencia(R, boxes)
    GT = {"barbosa": [13.6,33.9,40.3,54.5,69.8,83.3,135.0,155.0,162.9,188.3,196.0,227.2,
                      242.3,257.1,298.3,326.1,352.1,367.9,377.9,406.8,526.0],
          "parada4": [38.0,46.8,77.6,95.9,122.4,157.9,178.1,197.0,210.5,229.9,249.6,263.8,
                      289.1]}[VID]
    print("=" * 78)
    print(f"🎾 A SEQUÊNCIA DO SERVIÇO — {VID.upper()}   (v2: com a RAQUETE e a B16)")
    print("=" * 78)
    print("   ⓪ não-ténis  ① funda  ② quica no CHÃO (vertical)")
    print("   ③ bate na RAQUETE (horizontal, p/ o outro campo)  ④ só o ÚLTIMO antes de mudar\n")
    print(f"   candidatos: {len(S)}   ·   serviços reais: {len(GT)}\n")
    ok = 0
    for i, t in enumerate(GT, 1):
        hit = [f/FPS for f in S if -1.5 <= f/FPS - t <= 2.5]
        ok += bool(hit)
        print(f"   {i:2}  t={t:6.1f}s   " +
              (f"✅  {hit[0]:.1f}s" if hit else "🔴  sem sequência"))
    fal = [f/FPS for f in S if not any(-1.5 <= f/FPS - t <= 2.5 for t in GT)]
    print(f"\n   📈 RECALL:   {ok}/{len(GT)}  ({ok/len(GT)*100:.0f}%)")
    print(f"   🎯 PRECISÃO: {ok}/{len(S)}  ({ok/max(1,len(S))*100:.0f}%)  ·  {len(fal)} fora")


if __name__ == "__main__":
    main()
