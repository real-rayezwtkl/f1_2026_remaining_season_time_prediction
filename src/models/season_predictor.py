"""
2026 remaining-season predictor: pole time and Q1/Q2 cutoffs for every
round from Baku (round 14) to Abu Dhabi (round 23, season finale).

Method per circuit:
1. Baseline = mean of the circuit's own recent DRY pole times (years
   chosen per-circuit to exclude weather-affected sessions — see notes
   in data/raw/real_qualifying_data.py for exactly which years and why).
2. Add the clean-circuit 2026 regulation delta (+1.623s, from
   delta_model.py), the strongest available evidence for the
   regulation's effect independent of any one circuit's quirks.
3. Add each circuit's own qualitative layout adjustment (0 for most;
   negative for long-straight circuits like Baku/Vegas where 2026's
   low-drag active aero should claw back some of the deficit; positive
   for Mexico City's altitude, where the effect is genuinely unclear).
4. Derive Q1/Q2 cutoffs from the predicted pole using the averaged
   real gap-to-pole percentages (quali_gap_model.py) — NOT a fixed
   per-circuit grid, since we don't have full 2026 grids for most of
   these circuits yet.
5. Confidence label carries through from the baseline data quality
   (see CircuitBaseline.confidence) — this is not a fitted uncertainty,
   it's an honest editorial judgment about how much to trust each row.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data" / "raw"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import real_qualifying_data as data
from features.delta_model import clean_delta_stats
from features.quali_gap_model import compute_gap_percentages


def format_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:06.3f}"


def predict_circuit(circuit: "data.CircuitBaseline", clean_delta: dict, gaps: dict) -> dict:
    baseline_pole = sum(circuit.baseline_pole_times_s) / len(circuit.baseline_pole_times_s)
    predicted_pole = baseline_pole + clean_delta["mean"] + circuit.layout_adjustment_s

    low = predicted_pole - clean_delta["stdev"]
    high = predicted_pole + clean_delta["stdev"] + max(0.0, -circuit.layout_adjustment_s) * 0  # symmetry; widened below for low confidence
    if circuit.confidence == "low":
        # Sepang: two regulation eras of extrapolation — widen the band substantially
        # rather than pretend to a precision the data doesn't support.
        low -= 2.0
        high += 3.0
    elif circuit.confidence == "medium":
        low -= 0.3
        high += 0.5

    q1_cutoff = predicted_pole * (1 + gaps["avg_q1_gap_pct"])
    q2_cutoff = predicted_pole * (1 + gaps["avg_q2_gap_pct"])

    return {
        "round": circuit.round_no,
        "circuit": circuit.circuit,
        "date": circuit.race_date_2026,
        "baseline_pole_s": round(baseline_pole, 3),
        "baseline_years": circuit.baseline_years,
        "predicted_pole_s": round(predicted_pole, 3),
        "predicted_pole_range_s": (round(low, 3), round(high, 3)),
        "predicted_q2_cutoff_s": round(q2_cutoff, 3),
        "predicted_q1_cutoff_s": round(q1_cutoff, 3),
        "confidence": circuit.confidence,
        "layout_adjustment_s": circuit.layout_adjustment_s,
        "notes": circuit.notes,
    }


def predict_remaining_season() -> list[dict]:
    clean_delta = clean_delta_stats()
    gaps = compute_gap_percentages()
    return [predict_circuit(c, clean_delta, gaps) for c in data.REMAINING_CALENDAR]


def print_report(predictions: list[dict]):
    print(f"{'Rd':<4}{'Circuit':<32}{'Date':<12}{'Pole':<12}{'Q2 cutoff':<12}{'Q1 cutoff':<12}{'Conf.'}")
    print("-" * 100)
    for p in predictions:
        print(
            f"{p['round']:<4}{p['circuit']:<32}{p['date']:<12}"
            f"{format_time(p['predicted_pole_s']):<12}"
            f"{format_time(p['predicted_q2_cutoff_s']):<12}"
            f"{format_time(p['predicted_q1_cutoff_s']):<12}"
            f"{p['confidence']}"
        )


if __name__ == "__main__":
    predictions = predict_remaining_season()
    print_report(predictions)

    print("\n" + "=" * 100)
    print("Detail for each round:")
    for p in predictions:
        print(f"\n--- Round {p['round']}: {p['circuit']} ({p['date']}) ---")
        print(f"  Baseline: {format_time(p['baseline_pole_s'])} (years: {p['baseline_years']})")
        print(f"  Predicted pole: {format_time(p['predicted_pole_s'])}  "
              f"range: {format_time(p['predicted_pole_range_s'][0])}-{format_time(p['predicted_pole_range_s'][1])}")
        print(f"  Q2 cutoff: {format_time(p['predicted_q2_cutoff_s'])}   Q1 cutoff: {format_time(p['predicted_q1_cutoff_s'])}")
        print(f"  Confidence: {p['confidence']}")
        print(f"  Notes: {p['notes']}")
