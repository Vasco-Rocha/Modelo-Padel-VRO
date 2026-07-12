#!/usr/bin/env python3
"""
Artefacto: JOGADORES sem cap + a CASCATA COMPLETA do Vasco, na ordem certa.

    python3 gerar_pkl_jogadores_J.py \
        <players_detections_SEM_CAP.json>  <saida.pkl>  [calibracao.json]  [fps]

Ordem (a que o Vasco pediu):
    J1  pes no poligono        -> filtrar_espectadores (fora-do-campo + imoveis)
    J7  os de baixo cortados   -> preservados (pes fora do frame => aceites; ja dentro de J1/J4)
    J4  2 por lado             -> dois_por_lado (fica com os 2 melhores de cada lado da rede)
    J5  continuidade           -> continuidade_jogadores (rejeita saltos + PREENCHE buracos)

So GRAVA o .pkl { "player_boxes": [...], "fps": float }. NAO liga nada ao pipeline.

Cuidado tecnico: J1 e J4 trabalham em listas de boxes; J5 precisa dos IDs do
ByteTrack (para saber quem preencher). Por isso os IDs (e as confiancas) sao
arrastados atraves de J1/J4 por identidade do objecto, e so no fim se achatam.
"""
import sys, os, json, pickle, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from padelpro.modules.servico import (
    Campo, filtrar_espectadores, dois_por_lado,
)


def continuidade_fix(frames_id, campo, fps=29.97, v_max_ms=9.0, max_buraco_frames=15):
    """J5 -- mesma regra/parametros que servico.continuidade_jogadores, MAS com a
    iteracao corrigida.

    O original (servico.py) tem um bug: ao rejeitar um salto faz `del out[b][pid]`
    enquanto itera sobre a lista `vistos` ja obsoleta -> KeyError na iteracao
    seguinte (aparece com saltos consecutivos). Aqui recomputa-se `vistos` apos
    cada remocao. NAO se altera o ficheiro partilhado (a outra sessao mexe nele).
    """
    n = len(frames_id)
    out = [dict(d) for d in frames_id]

    def px_por_m(box):
        xc, y2 = (box[0] + box[2]) / 2.0, box[3]
        lado = "baixo" if y2 > campo.y_rede_base(xc) else "cima"
        return max(campo.meio_campo_px(xc, lado) / 6.95, 1.0)

    def pes(b):
        return ((b[0] + b[2]) / 2.0, b[3])

    ids = set()
    for d in frames_id:
        ids |= set(d)

    saltos = preenchidos = 0
    for pid in ids:
        # 1. saltos impossiveis -- recomputa vistos apos cada remocao (o fix)
        while True:
            vistos = [f for f in range(n) if pid in out[f]]
            removeu = False
            for a, b in zip(vistos, vistos[1:]):
                pa, pb = pes(out[a][pid]), pes(out[b][pid])
                dt = (b - a) / fps
                limite = v_max_ms * px_por_m(out[a][pid]) * dt * 1.5
                if math.hypot(pb[0] - pa[0], pb[1] - pa[1]) > limite:
                    del out[b][pid]; saltos += 1; removeu = True
                    break
            if not removeu:
                break

        # 2. preencher buracos curtos
        vistos = [f for f in range(n) if pid in out[f]]
        for a, b in zip(vistos, vistos[1:]):
            gap = b - a - 1
            if not (0 < gap <= max_buraco_frames):
                continue
            ba, bb = out[a][pid], out[b][pid]
            for k in range(1, gap + 1):
                t = k / (gap + 1)
                out[a + k][pid] = tuple(ba[i] + t * (bb[i] - ba[i]) for i in range(4))
                preenchidos += 1

    return out, {"ids": len(ids), "saltos_rejeitados": saltos,
                 "frames_preenchidos": preenchidos}


def dist(boxes):
    n = len(boxes)
    p4 = 100 * sum(1 for f in boxes if len(f) >= 4) / max(n, 1)
    p3 = 100 * sum(1 for f in boxes if len(f) >= 3) / max(n, 1)
    med = sum(len(f) for f in boxes) / max(n, 1)
    return med, p3, p4


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    jpath, out = sys.argv[1], sys.argv[2]
    cal_p = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "calibracao_campo.json")
    fps = float(sys.argv[4]) if len(sys.argv) > 4 else 29.97

    bruto = json.load(open(jpath))
    campo = Campo(json.load(open(cal_p)))

    # box tuples distintos por deteccao; mapa identidade -> (tracker_id, conf)
    box_lists, meta = [], []
    for fr in bruto:
        bl, m = [], {}
        for p in fr:
            b = tuple(map(float, p["xyxy"]))
            bl.append(b)
            m[id(b)] = (p.get("id"), float(p.get("confidence", 1.0)))
        box_lists.append(bl); meta.append(m)
    bruto_med = dist(box_lists)[0]

    # --- J1 (pes no poligono) + J7 (os de baixo cortados, aceites dentro de dentro_do_campo)
    j1, rel = filtrar_espectadores(box_lists, campo)

    # --- J4 (2 por lado) -- com as confiancas arrastadas, para ficar com os 2 de MAIOR conf
    confs = [[meta[f].get(id(b), (None, 1.0))[1] for b in fr] for f, fr in enumerate(j1)]
    j4 = dois_por_lado(j1, campo, confs=confs)

    # --- J5 (continuidade) -- precisa dos IDs: reconstroi {id: box} por identidade do objecto
    frames_id = []
    for f, fr in enumerate(j4):
        d = {}
        for b in fr:
            tid = meta[f].get(id(b), (None, None))[0]
            if tid is not None:
                d[int(tid)] = b
        frames_id.append(d)
    frames_id, rel5 = continuidade_fix(frames_id, campo, fps=fps)

    player_boxes = [[tuple(map(float, b)) for b in d.values()] for d in frames_id]

    pickle.dump({"player_boxes": player_boxes, "fps": fps}, open(out, "wb"))

    m0 = bruto_med
    m1 = dist(j1)[0]; m4 = dist(j4)[0]; mf = dist(player_boxes)
    print(f"✅ {out}")
    print(f"   frames: {len(player_boxes)} · fps: {fps}")
    print(f"   media/frame:  bruto {m0:.2f} -> J1 {m1:.2f} -> J4 {m4:.2f} -> J5 {mf[0]:.2f}")
    print(f"   J1: fora-do-campo {rel['descartadas_fora_do_campo']} · imoveis {rel['descartadas_imoveis']}")
    print(f"   J5: saltos rejeitados {rel5['saltos_rejeitados']} · frames preenchidos {rel5['frames_preenchidos']}")
    print(f"   FINAL: com os 4 jogadores {mf[2]:.1f}%  ·  com >=3 {mf[1]:.1f}%")


if __name__ == "__main__":
    main()
