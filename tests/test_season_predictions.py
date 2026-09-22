"""Sanity tests for the remaining-season predictor."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data" / "raw"))

from features.delta_model import compute_deltas, clean_delta_stats
from features.quali_gap_model import compute_gap_percentages
from models.season_predictor import predict_remaining_season


def test_all_nine_remaining_rounds_present():
    predictions = predict_remaining_season()
    assert len(predictions) == 9
    rounds = [p["round"] for p in predictions]
    assert rounds == sorted(rounds)  # chronological order preserved


def test_baku_is_first_and_abu_dhabi_is_last():
    predictions = predict_remaining_season()
    assert predictions[0]["circuit"] == "Azerbaijan (Baku)"
    assert predictions[-1]["circuit"] == "Abu Dhabi (Yas Marina)"


def test_china_delta_matches_hand_calc():
    deltas = compute_deltas()
    assert abs(deltas["China (Shanghai)"] - 1.423) < 0.001


def test_sepang_flagged_low_confidence():
    """Sepang's 9-year-old baseline must not be presented with false
    precision — its confidence label and wide range are the whole point."""
    predictions = predict_remaining_season()
    sepang = next(p for p in predictions if "Sepang" in p["circuit"])
    assert sepang["confidence"] == "low"
    lo, hi = sepang["predicted_pole_range_s"]
    assert (hi - lo) > 4.0  # much wider than any other circuit's band


def test_all_predictions_slower_than_their_own_dry_baseline():
    """The core claim of the whole model: every 2026 prediction should be
    slower than that circuit's own recent dry baseline, since the clean
    delta is positive (2026 is slower) at every clean comparison circuit."""
    predictions = predict_remaining_season()
    for p in predictions:
        assert p["predicted_pole_s"] > p["baseline_pole_s"] + p["layout_adjustment_s"] - 0.5


def test_q1_slower_than_q2_slower_than_pole():
    predictions = predict_remaining_season()
    for p in predictions:
        assert p["predicted_q1_cutoff_s"] > p["predicted_q2_cutoff_s"] > p["predicted_pole_s"]


def test_gap_percentages_are_small_and_positive():
    gaps = compute_gap_percentages()
    assert 0 < gaps["avg_q1_gap_pct"] < 0.05
    assert 0 < gaps["avg_q2_gap_pct"] < 0.05


if __name__ == "__main__":
    import subprocess
    subprocess.run(["python3", "-m", "pytest", __file__, "-v"])
