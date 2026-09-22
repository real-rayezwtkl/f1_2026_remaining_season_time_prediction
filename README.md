# 2026 Remaining Season — Lap Time & Qualifying Cutoff Prediction

**Pole time and Q1/Q2 qualifying cutoffs for every round from Baku (round 14) through the
Abu Dhabi finale (round 23)** — under F1's 2026 regulation reset — using only real, sourced
qualifying data. No synthetic data anywhere in this repo.

## Why this exists

2026 introduced new 50/50 hybrid power units, active aero (X-mode/Z-mode replacing DRS), and
smaller/lighter cars — the biggest single-year regulation change since the 2022 ground-effect
reset. There's no historical telemetry for a six-month-old rule set, and none of the nine
remaining circuits has run under these rules before. So instead of a telemetry-feature
regression, this project measures the **real, verified 2025-to-2026 slowdown** at circuits that
have raced under both rule sets, and applies it to each remaining circuit's **own real recent
qualifying history** — a smaller, more defensible model than the alternative, given what data
genuinely exists right now.

## The regulation delta (shared across every prediction)

Four weather-matched circuits that ran under both 2025 and 2026 rules:

| Circuit | 2025 pole | 2026 pole | Delta |
|---|---|---|---|
| China (Shanghai) | 1:30.641 | 1:32.064 | +1.423s |
| Miami | 1:26.204 | 1:27.798 | +1.594s |
| Canada (Montreal) | 1:10.899 | 1:12.578 | +1.679s |
| Japan (Suzuka) | 1:26.983 | 1:28.778 | +1.795s |
| **Mean** | | | **+1.623s (σ = 0.157s)** |

Australia (wet 2025 vs dry 2026) and Monza (2025's pole was an all-time F1 qualifying speed
record) are excluded from this headline number as confounded comparisons — see
`src/features/delta_model.py` for the full reasoning, kept transparent rather than hidden.

## The predictions

| Rd | Circuit | Date | Pole | Q2 cutoff | Q1 cutoff | Confidence |
|---|---|---|---|---|---|---|
| 14 | Azerbaijan (Baku) | Sep 26 | **1:42.298** | 1:43.874 | 1:44.734 | High |
| 16 | Bahrain-in-Malaysia (Sepang) | Oct 4 | **1:31.699** | 1:33.111 | 1:33.882 | **Low** |
| 17 | Singapore (Marina Bay) | Oct 11 | **1:30.781** | 1:32.179 | 1:32.943 | Medium |
| 18 | United States (COTA) | Oct 18 | **1:34.810** | 1:36.271 | 1:37.068 | High |
| 19 | Mexico City | Oct 25 | **1:17.309** | 1:18.499 | 1:19.150 | Medium |
| 20 | Brazil (Interlagos) | Nov 8 | **1:11.134** | 1:12.229 | 1:12.828 | Medium |
| 21 | Las Vegas | Nov 21 | **1:33.735** | 1:35.178 | 1:35.967 | Medium |
| 22 | Qatar (Lusail) | Nov 29 | **1:22.869** | 1:24.146 | 1:24.843 | Medium |
| 23 | Abu Dhabi (Yas Marina) | Dec 6 | **1:24.372** | 1:25.671 | 1:26.381 | High |

Run it yourself:
```bash
python src/models/season_predictor.py
```

## Method, in full

For each circuit:

1. **Baseline** = mean of that circuit's own real recent *dry* pole times (which years count as
   "clean" is a per-circuit judgment — documented for every circuit in
   `data/raw/real_qualifying_data.py`, e.g. Brazil's 2023/2024 poles are excluded because both
   were rain-affected).
2. **+ 1.623s** — the clean 4-circuit 2026 regulation delta, the strongest available evidence for
   the rules' effect independent of any single circuit's quirks.
3. **+ a per-circuit layout adjustment** (0 for most circuits; −0.3s for Baku and −0.2s for Las
   Vegas, both very long-straight circuits where 2026's low-drag active aero should claw back
   some of the deficit; +0.1s for Mexico City, where high-altitude aero/cooling effects under the
   new rules are genuinely unclear). **These are qualitative judgments, not fitted
   coefficients** — there's no 2026 data yet at a comparable long-straight or high-altitude
   circuit to calibrate them against, and the repo says so rather than dressing up a guess as a
   parameter.
4. **Q1/Q2 cutoffs** are derived from the predicted pole using **gap-to-pole percentages**
   (`src/features/quali_gap_model.py`) averaged across the three real full grids available
   (2025 China, 2026 Australia, 2026 China: Q1 gap ≈ 2.4%, Q2 gap ≈ 1.5%) — not a fixed-second
   gap, since that gap scales with the lap time itself.

## Confidence is not decoration

Every row carries an honest confidence label, and it isn't cosmetic:

- **High** (Baku, USA, Abu Dhabi): 2–3 consecutive clean dry baseline years, no unusual
  circuit-specific caveats.
- **Medium** (Singapore, Mexico, Brazil, Las Vegas, Qatar): only one or two clean years
  available, or a real but bounded circuit quirk (Mexico's altitude, Qatar's multi-year track
  evolution trend).
- **Low** (Sepang): Formula 1 hasn't raced there since **2017** — nine years, and *two* full
  regulation eras (2017→2022 ground-effect, 2022→2026 this reset) separate the only available
  baseline from the 2026 cars. This prediction is a genuine best-effort extrapolation, not a
  defensible forecast, and the test suite (`tests/test_season_predictions.py`) explicitly checks
  that its uncertainty band is wide enough to reflect that rather than presenting false precision.

## What isn't accounted for

- **In-season development.** If 2026 cars close the regulation gap as the year progresses (the
  usual pattern after a big reset), later rounds could run faster than predicted. The one
  late-season data point available (Monza, round 13) is inconclusive on this — see
  `src/features/delta_model.py` — so no seasonal-convergence adjustment is applied anywhere.
- **Weather on the day.** Every baseline was deliberately chosen to exclude rain-affected
  sessions, which means every prediction implicitly assumes dry qualifying. Baku's actual 2025
  session (six red flags, rain in Q3) is the standing reminder of how wrong that assumption can
  turn out to be in practice.
- **Car development order.** No attempt is made to predict which *team* will be fastest — this
  predicts the grid-wide pole/cutoff times, not who sets them.

## Repo layout

```
├── data/raw/real_qualifying_data.py      # every real result used, with source URLs
├── src/
│   ├── features/
│   │   ├── delta_model.py                # 2026 regulation pace delta
│   │   └── quali_gap_model.py            # Q1/Q2 gap-to-pole percentage model
│   └── models/season_predictor.py        # generalized predictor, all 9 circuits
├── notebooks/season_predictions.ipynb    # full walkthrough with charts, executed with real output
├── tests/test_season_predictions.py      # validates against hand-checked real numbers
└── requirements.txt
```

## Data provenance and this project's known limitation

Every number in `data/raw/real_qualifying_data.py` was manually verified via web search and
reading the actual formula1.com/Wikipedia pages, with the source recorded next to each result.
This was necessary because the sandbox this project was built in has network access locked to
package registries (PyPI, npm, etc.) and cannot reach formula1.com or Wikipedia directly — there
is no live scraper in this repo attempting to hide that constraint. If you extend this project
with more circuits or more historical years, the same manual-verification-with-cited-source
approach is what keeps the "no synthetic data" claim actually true.

## 2026 context (background)

- **Regulation reset**: 50/50 hybrid power split (up from ~80/20), active aero replacing DRS,
  smaller and lighter cars.
- **Season disruption**: the 2026 Iran war (Feb 28, 2026) forced cancellation of the Saudi
  Arabian GP entirely, and relocation of the Bahrain GP to Sepang, Malaysia — its first F1 race
  since 2017 — under an unprecedented cross-government arrangement between Bahrain and Malaysia.
- **Calendar**: 23 rounds total in 2026 (Saudi Arabia's slot was not backfilled).

## Requirements

```
pip install -r requirements.txt
```
