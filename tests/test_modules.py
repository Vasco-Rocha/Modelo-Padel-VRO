"""Testes dos 3 modulos com dados sinteticos."""
from padelpro.io import make_synthetic_game
from padelpro.pipeline import run_pipeline
from padelpro.modules import analyze_active_time, analyze_phases


def test_active_time_detects_rallies():
    game, _ = make_synthetic_game(fps=30, n_rallies=4, seed=2)
    out = analyze_active_time(game)
    assert out["n_rallies"] >= 3            # ~4 rallies gerados
    assert 0 < out["active_ratio"] < 1      # ha jogo e pausas
    assert out["active_time_s"] <= out["match_time_s"]
    assert out["signal_source"] == "ball"


def test_phases_assign_two_teams():
    game, _ = make_synthetic_game(seed=3)
    out = analyze_phases(game)
    assert len(out["teams"]["near"]) == 2
    assert len(out["teams"]["far"]) == 2
    assert out["n_segments"] >= 1
    assert sum(out["time_by_phase_s"].values()) > 0


def test_shots_outcomes_sum_to_total():
    game, shots = make_synthetic_game(seed=4)
    analysis = run_pipeline(game, shots=shots).to_dict()
    s = analysis["shots"]
    assert s["n_shots"] == sum(s["outcomes"].values())
    # cada rally fechado deve produzir pelo menos um erro
    assert s["outcomes"]["forced_error"] + s["outcomes"]["unforced_error"] >= 1


def test_pipeline_end_to_end():
    game, shots = make_synthetic_game(seed=5)
    analysis = run_pipeline(game, shots=shots).to_dict()
    assert analysis["duration_s"] > 0
    assert "active_time" in analysis and "phases" in analysis and "shots" in analysis


def test_centered_origin_shift():
    # CSV com coords centradas (rede em y=0) deve ser deslocado para canto.
    import tempfile, os
    from padelpro.io.loader import load_game_data, default_config
    game, _ = make_synthetic_game(seed=8)
    df = game.frames.copy()
    for pid in (1, 2, 3, 4):
        df[f"player{pid}_x"] = df[f"p{pid}_x"] - 5.0   # centrar
        df[f"player{pid}_y"] = df[f"p{pid}_y"] - 10.0
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "c.csv"); df.to_csv(p, index=False)
        cfg = default_config(); cfg["court"]["origin"] = "centered"
        g = load_game_data(p, fps=30, config=cfg)
    # depois do shift, posicoes voltam ao intervalo de canto (0..20 em y)
    assert g.frames["p1_y"].min() >= -1
    assert g.frames["p1_y"].max() <= 21


def test_works_without_ball():
    game, shots = make_synthetic_game(seed=6)
    game.has_ball = False
    game.frames = game.frames.drop(columns=["ball_x", "ball_y", "ball_speed", "ball_hit"])
    out = analyze_active_time(game)
    assert out["signal_source"] == "players"
    assert out["n_rallies"] >= 1
