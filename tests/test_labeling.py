"""Testes do pipeline de labeling (offline, modo mock)."""
import tempfile, os
from padelpro.io import make_synthetic_game
from padelpro.modules import analyze_active_time
from padelpro.labeling import (
    extract_clips, build_label_prompt, GeminiLabeler, LabelStore, build_training_table,
    OUTCOME_LABELS,
)
from padelpro.labeling.run import run_labeling


def _game():
    return make_synthetic_game(seed=7)


def test_extract_clips_has_features():
    game, shots = _game()
    rallies = analyze_active_time(game)["rallies"]
    clips = extract_clips(game, shots, rallies=rallies)
    assert len(clips) == len(shots)
    c = clips[0]
    assert c.start_frame <= c.shot.frame <= c.end_frame
    assert "player_zone" in c.features


def test_prompt_mentions_enums():
    game, shots = _game()
    clips = extract_clips(game, shots)
    p = build_label_prompt(clips[0])
    assert "forced_error" in p and "unforced_error" in p
    assert "JSON" in p


def test_mock_labeler_outcomes_valid():
    game, shots = _game()
    rallies = analyze_active_time(game)["rallies"]
    store = run_labeling(game, shots, GeminiLabeler(mock=True), rallies=rallies)
    assert len(store.records) == len(shots)
    for r in store.records.values():
        assert r.outcome_pred in OUTCOME_LABELS
        assert r.status == "pending"


def test_store_roundtrip_and_training_table():
    game, shots = _game()
    rallies = analyze_active_time(game)["rallies"]
    store = run_labeling(game, shots, GeminiLabeler(mock=True), rallies=rallies)
    # confirma tudo (na vida real e' o humano)
    for cid in list(store.records):
        store.confirm(cid)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "labels.jsonl")
        store.save(path)
        store2 = LabelStore.load(path)
    assert len(store2.confirmed()) == len(shots)
    table = build_training_table(store2, target="outcome")
    assert "label" in table.columns and len(table) >= 1
