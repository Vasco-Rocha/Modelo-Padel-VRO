"""Demo end-to-end sem GPU: gera um jogo sintetico e corre os 3 modulos."""
import json
from padelpro.io import make_synthetic_game
from padelpro.pipeline import run_pipeline

game, shots = make_synthetic_game(fps=30, n_rallies=4, seed=1)
analysis = run_pipeline(game, shots=shots)

d = analysis.to_dict()
print("== Tempo util ==")
print({k: d["active_time"][k] for k in ("n_rallies", "active_time_s", "match_time_s", "active_ratio", "avg_rally_s")})
print("\n== Fases (tempo por fase, s) ==")
print(d["phases"]["time_by_phase_s"])
print("\n== Pancadas ==")
print(d["shots"]["outcomes"])
print("\n(JSON completo tem rallies, segmentos e stats por jogador)")
