"""Interface de linha de comandos do PadelPro Vision."""
from __future__ import annotations
import argparse
import json
import sys

from .io.loader import load_game_data, load_shots, default_config
from .pipeline import run_pipeline


def _load_config(path: str | None) -> dict:
    cfg = default_config()
    if path:
        import yaml
        with open(path) as f:
            cfg.update(yaml.safe_load(f) or {})
    return cfg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="padelpro", description="Analise de padel")
    sub = parser.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="Corre os 3 modulos sobre um jogo")
    a.add_argument("--players", required=True, help="CSV de jogadores (padel_analytics)")
    a.add_argument("--ball", help="CSV/parquet da bola (opcional)")
    a.add_argument("--shots", help="CSV de pancadas detetadas (opcional)")
    a.add_argument("--fps", type=float, default=None)
    a.add_argument("--config", help="config.yaml (opcional)")
    a.add_argument("--out", help="Caminho do JSON de saida (senao imprime)")

    l = sub.add_parser("label", help="Auto-labeling das pancadas com o Gemini")
    l.add_argument("--players", required=True, help="CSV de jogadores (padel_analytics)")
    l.add_argument("--ball", help="CSV/parquet da bola (opcional)")
    l.add_argument("--shots", required=True, help="CSV de pancadas detetadas")
    l.add_argument("--video", help="Video original (para cortar clips, modo real)")
    l.add_argument("--fps", type=float, default=None)
    l.add_argument("--config", help="config.yaml (opcional)")
    l.add_argument("--out", default="labels.jsonl", help="JSONL de labels")
    l.add_argument("--clips-dir", default="clips", help="Pasta para os clips de video")
    l.add_argument("--api-key", help="Google API key (Gemini); sem isto corre em mock")
    l.add_argument("--mock", action="store_true", help="Forca modo offline (sem Gemini)")

    args = parser.parse_args(argv)
    if args.cmd == "label":
        from .labeling.gemini import GeminiLabeler
        from .labeling.run import run_labeling
        from .modules import analyze_active_time
        cfg = _load_config(args.config)
        fps = args.fps or cfg.get("fps", 30)
        game = load_game_data(args.players, ball_path=args.ball, fps=fps, config=cfg)
        shots = load_shots(args.shots, fps=fps, config=cfg)
        rallies = analyze_active_time(game, **cfg.get("active_time", {}))["rallies"]
        labeler = GeminiLabeler(api_key=args.api_key, mock=args.mock)
        store = run_labeling(game, shots, labeler, rallies=rallies,
                             video_path=args.video, clips_dir=args.clips_dir)
        store.save(args.out)
        mode = "mock" if labeler.mock else "Gemini"
        print(f"{len(store.records)} labels ({mode}) guardados em {args.out}")
        print("Confirma/corrige e depois usa build_training_table para treinar.")
        return 0

    if args.cmd == "analyze":
        cfg = _load_config(args.config)
        fps = args.fps or cfg.get("fps", 30)
        game = load_game_data(args.players, ball_path=args.ball, fps=fps, config=cfg)
        shots = load_shots(args.shots, fps=fps, config=cfg) if args.shots else None
        analysis = run_pipeline(game, shots=shots, config=cfg)
        payload = json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False)
        if args.out:
            with open(args.out, "w") as f:
                f.write(payload)
            print(f"Analise guardada em {args.out}")
        else:
            print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
