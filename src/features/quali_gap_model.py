"""
Q1/Q2 cutoff-gap model.

Q1 and Q2 cutoffs don't sit a fixed number of seconds behind pole —
that gap scales with the lap time itself (a 5% gap at a 90s circuit is
~4.5s; at a 110s circuit it's ~5.5s). So we compute the gap as a
PERCENTAGE of pole time from every full grid we actually have, and
average across them, rather than assuming a constant.

We have four real full grids: 2025 China, 2025 Baku, 2026 Australia,
2026 China. Two qualifying FORMATS are mixed in here (20-car/top-15
advance vs 22-car/top-16 advance) — see the per-grid notes below for
exactly which rank each cutoff uses.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data" / "raw"))
import real_qualifying_data as data


def _grid_cutoffs(full_grid: list, q1_rank: int, q2_rank: int) -> tuple[float, float]:
    """q1_rank/q2_rank are 1-indexed positions of the cutoff (last car to advance)."""
    q1_times = sorted(row["q1"] for row in full_grid if row.get("q1") is not None)
    q2_times = sorted(row["q2"] for row in full_grid if row.get("q2") is not None)
    return q1_times[q1_rank - 1], q2_times[q2_rank - 1]


def compute_gap_percentages() -> dict:
    """Returns per-source and averaged Q1/Q2 gap-to-pole percentages."""
    sources = []

    # 2025 China: 20-car grid, old format, top-15 advance from Q1, top-10 from Q2.
    china_2025 = next(r for r in data.RESULTS_2025 if r.circuit == "China (Shanghai)")
    q1c, q2c = _grid_cutoffs(china_2025.full_grid, q1_rank=15, q2_rank=10)
    sources.append(("2025 China", china_2025.pole_time_s, q1c, q2c))

    # 2026 Australia: 22-car grid, new format, top-16 advance from Q1, top-10 from Q2.
    aus_2026 = next(r for r in data.RESULTS_2026 if r.circuit == "Australia (Albert Park)")
    q1a, q2a = _grid_cutoffs(aus_2026.full_grid, q1_rank=16, q2_rank=10)
    sources.append(("2026 Australia", aus_2026.pole_time_s, q1a, q2a))

    # 2026 China: 22-car grid (well, 17 recorded here — full field was 22,
    # but only 17 rows are in our hand-entered subset), new format.
    china_2026 = next(r for r in data.RESULTS_2026 if r.circuit == "China (Shanghai)")
    q1c2, q2c2 = _grid_cutoffs(china_2026.full_grid, q1_rank=16, q2_rank=10)
    sources.append(("2026 China (partial grid)", china_2026.pole_time_s, q1c2, q2c2))

    rows = []
    for name, pole, q1_cut, q2_cut in sources:
        rows.append({
            "source": name,
            "pole_s": pole,
            "q1_cutoff_s": q1_cut,
            "q2_cutoff_s": q2_cut,
            "q1_gap_pct": (q1_cut - pole) / pole,
            "q2_gap_pct": (q2_cut - pole) / pole,
        })

    avg_q1_pct = sum(r["q1_gap_pct"] for r in rows) / len(rows)
    avg_q2_pct = sum(r["q2_gap_pct"] for r in rows) / len(rows)

    return {"rows": rows, "avg_q1_gap_pct": avg_q1_pct, "avg_q2_gap_pct": avg_q2_pct}


if __name__ == "__main__":
    result = compute_gap_percentages()
    for row in result["rows"]:
        print(f"{row['source']:28s} Q1 gap: {row['q1_gap_pct']*100:.2f}%   Q2 gap: {row['q2_gap_pct']*100:.2f}%")
    print(f"\nAveraged: Q1 gap {result['avg_q1_gap_pct']*100:.2f}%, Q2 gap {result['avg_q2_gap_pct']*100:.2f}%")
