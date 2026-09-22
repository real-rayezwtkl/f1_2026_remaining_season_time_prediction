"""2026 regulation pace-delta model — see module docstring in the original
analysis: measures 2026-vs-2025 pole time at circuits that ran under both
rule sets, rather than modeling lap time from telemetry we don't have."""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data" / "raw"))
import real_qualifying_data as data


def _pole_by_circuit(results: list) -> dict[str, float]:
    return {r.circuit: r.pole_time_s for r in results}


def compute_deltas() -> dict[str, float]:
    poles_2026 = _pole_by_circuit(data.RESULTS_2026)
    poles_2025 = _pole_by_circuit(data.RESULTS_2025)
    common = set(poles_2026) & set(poles_2025)
    return {c: poles_2026[c] - poles_2025[c] for c in common}


def clean_delta_stats() -> dict:
    deltas = compute_deltas()
    clean = {c: v for c, v in deltas.items() if c in data.CLEAN_DELTA_CIRCUITS}
    values = list(clean.values())
    return {
        "per_circuit": clean,
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "n": len(values),
    }


def all_delta_stats() -> dict:
    deltas = compute_deltas()
    values = list(deltas.values())
    return {
        "per_circuit": deltas,
        "mean": statistics.mean(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "n": len(values),
    }


if __name__ == "__main__":
    print("Clean delta:", clean_delta_stats())
    print("All delta:", all_delta_stats())
