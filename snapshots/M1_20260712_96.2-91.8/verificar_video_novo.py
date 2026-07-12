#!/usr/bin/env python3
"""
✅ VERIFICAR os dados de um VÍDEO NOVO — antes de o pipeline lhes tocar.

    python3 verificar_video_novo.py ../dados_<video>/  [calibracao_<video>.json]

PORQUE ISTO EXISTE
------------------
Um ficheiro no feitio errado não dá um erro claro: dá NÚMEROS ERRADOS, em silêncio. E depois
passam-se horas a debater regras quando o problema era uma coluna trocada.
(13 jul: a lista de ficheiros dizia que o snapshot estava bom. Só CORRÊ-LO mostrou que não estava.)

Isto não corrige nada. Só VERIFICA, e falha alto.
"""
import sys, os, csv, json, glob, pickle
import numpy as np

ok_tudo = True


def diz(ok, msg, detalhe=""):
    global ok_tudo
    print(f"  {'✅' if ok else '❌'} {msg}" + (f"   {detalhe}" if detalhe else ""))
    if not ok:
        ok_tudo = False
    return ok


def aviso(msg):
    print(f"  ⚠️  {msg}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pasta = sys.argv[1]
    cal_p = sys.argv[2] if len(sys.argv) > 2 else "calibracao_campo.json"

    print("=" * 78)
    print(f"VERIFICAR: {pasta}")
    print("=" * 78)

    # ---------------------------------------------------------------- A BOLA
    print("\n[1] A BOLA (BlurBall)")
    csvs = glob.glob(os.path.join(pasta, "*.csv"))
    if not diz(bool(csvs), "existe um .csv", pasta):
        sys.exit(1)
    bola_p = csvs[0]
    print(f"      {os.path.basename(bola_p)}")

    linhas = list(csv.DictReader(open(bola_p)))
    cols = set(linhas[0]) if linhas else set()
    precisas = {"Frame", "X", "Y", "Visibility", "L", "Theta"}
    diz(precisas <= cols, "tem as colunas necessárias",
        f"faltam: {precisas - cols}" if not precisas <= cols else "")
    diz("score" in cols, "tem a coluna `score` (contínua)",
        "" if "score" in cols else "⇒ SEM ISTO tens de correr o modelo outra vez para mudar de threshold!")

    n_frames = len(linhas)
    vis = [r for r in linhas if int(float(r["Visibility"]))]
    pct = 100 * len(vis) / max(n_frames, 1)
    diz(n_frames > 0, f"frames: {n_frames}")
    diz(pct > 50, f"bola visível em {pct:.1f}% dos frames",
        "(no Parada4 a thr=0.4 eram 76,1%)")
    if pct < 60:
        aviso("Recall da bola BAIXO. Confirma que o threshold ficou em 0.4 (não 0.7).")

    if "score" in cols:
        sc = [float(r["score"]) for r in vis]
        thr = min(sc)
        diz(abs(thr - 0.4) < 0.02, f"threshold usado: {thr:.2f}",
            "⇒ TEM de ser 0.4" if abs(thr - 0.4) >= 0.02 else "")

    Ls = [float(r["L"]) for r in vis if float(r["L"]) > -1e9]
    if Ls:
        print(f"      L: mediana {np.median(Ls):.1f} · p90 {np.percentile(Ls,90):.1f}"
              f"   (Parada4: mediana 2,5 · p90 12,4)")
        print("      ⚠️ O `L` é a base da S15 (mão vs raquete), a regra MAIS VALIOSA do sistema.")
        print("         Se a escala do L mudar muito, o L_RAQUETE=11 vai partir. É ESPERADO.")

    # ------------------------------------------------------------ JOGADORES
    print("\n[2] OS JOGADORES")
    pkls = glob.glob(os.path.join(pasta, "*.pkl"))
    if diz(bool(pkls), "existe um .pkl"):
        d = pickle.load(open(pkls[0], "rb"))
        print(f"      {os.path.basename(pkls[0])}")
        diz(isinstance(d, dict) and "player_boxes" in d, "tem a chave `player_boxes`")
        if isinstance(d, dict) and "player_boxes" in d:
            B = d["player_boxes"]
            diz(len(B) == n_frames, f"nº de frames bate com o da bola",
                f"bola {n_frames} vs jogadores {len(B)}" if len(B) != n_frames else "")
            q = sum(1 for f in B if len(f) >= 4)
            p4 = 100 * q / max(len(B), 1)
            print(f"      frames com >=4 boxes CRUAS: {p4:.1f}%   (Parada4: 52,6%)")
            print("      ⚠️ ATENÇÃO — ISTO NÃO É 'vê os 4 jogadores'.")
            print("         São boxes CRUAS: podem incluir ESPECTADORES (no Parada4, o espectador")
            print("         era a deteção MAIS FREQUENTE do vídeo — 32% dos frames).")
            print("         Os 4 jogadores REAIS só se contam DEPOIS dos filtros do Vasco")
            print("         (J1 fora-do-campo · J2/J3 imóveis · J4 dois-por-lado), que estão em")
            print("         `padelpro/modules/servico.py` e NÃO CORREM no pipeline do tempo útil.")
            print("         👉 O '21,8% tem os 4' que anda nos documentos refere-se aos jogadores")
            print("            FILTRADOS, não a isto. NÃO CONFUNDIR. (E o 21,8% nunca foi")
            print("            re-verificado — desconfiar dele antes de o citar.)")
            diz("fps" in d, "tem o `fps`", f"fps={d.get('fps')}" if "fps" in d else "")

    # ----------------------------------------------------------- CALIBRAÇÃO
    print("\n[3] A CALIBRAÇÃO DO CAMPO")
    if diz(os.path.exists(cal_p), f"existe {cal_p}"):
        cal = json.load(open(cal_p))
        precisas = ["rede_topo_coef", "rede_base_coef", "rede_tape_coef",
                    "servico_perto_coef", "servico_longe_coef", "fundo_longe_coef"]
        falta = [k for k in precisas if k not in cal]
        diz(not falta, "tem todas as curvas necessárias", f"faltam: {falta}" if falta else "")

        if not falta:
            ev = lambda c, x: float(np.polyval(cal[c], x))
            W = cal.get("resolucao", [960, 540])[0]
            xs = range(0, W, max(W // 8, 1))
            # a RÉGUA: o meio-campo local (rede -> linha de serviço)
            longe = [abs(ev("rede_base_coef", x) - ev("servico_longe_coef", x)) for x in xs]
            perto = [abs(ev("servico_perto_coef", x) - ev("rede_base_coef", x)) for x in xs]
            print(f"      meio-campo (6,95 m):  LONGE {np.mean(longe):.0f} px  ·  "
                  f"PERTO {np.mean(perto):.0f} px   (Parada4: 95 / 275)")
            diz(min(longe) > 20 and min(perto) > 20,
                "a régua é coerente (nenhuma linha colapsou)")
            razao = np.mean(perto) / max(np.mean(longe), 1)
            print(f"      razão perto/longe: {razao:.1f}×   (Parada4: 2,9×)")
            if razao > 4:
                aviso("Perspetiva MUITO agressiva — a câmara está muito baixa.")
            # a banda da rede vs o meio-campo do fundo (a lição do vidro)
            banda = np.mean([abs(ev("rede_base_coef", x) - ev("rede_topo_coef", x)) for x in xs])
            print(f"      banda da rede: {banda:.0f} px  =  {100*banda/np.mean(longe):.0f}% "
                  f"do meio-campo do fundo   (Parada4: 35%)")

    # ---------------------------------------------------------------- FECHO
    print("\n" + "=" * 78)
    if ok_tudo:
        print("✅ PODE CORRER.")
        print()
        print("   NO gerar_tempo_util.py, MUDA SÓ ISTO:")
        print(f'     BOLA  = "{bola_p}"')
        print(f'     BOXES = "{pkls[0] if pkls else "?"}"')
        print(f'     CAL   = "{cal_p}"')
        print(f"     N_FRAMES = {n_frames}")
        print("     FPS, VIDEO, GT")
        print()
        print("   🛑 E MAIS NADA. NEM UM LIMIAR.")
        print("      Afinar os números ao vídeo novo torna o teste INÚTIL.")
        print("      O que sair, sai — é ESSE o objetivo.")
    else:
        print("❌ NÃO CORRER. Arruma o que está acima primeiro.")
        print("   Um ficheiro no feitio errado não dá erro: dá NÚMEROS ERRADOS, em silêncio.")
    print("=" * 78)
    sys.exit(0 if ok_tudo else 1)


if __name__ == "__main__":
    main()
