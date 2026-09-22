"""
Real qualifying data, manually compiled from Formula1.com and Wikipedia
race reports (this sandbox's code-execution environment cannot reach
formula1.com directly — see src/scraping notes in the README). Every
number below is a REAL recorded qualifying result; nothing here is
synthetic.

Two parts:
1. DELTA_PAIRS — same-circuit 2025-vs-2026 comparisons, used to measure
   the 2026 regulation pace effect (src/features/delta_model.py).
2. REMAINING_CALENDAR — every round from Baku onward, each with its own
   real recent-history baseline, used to predict pole + Q1/Q2 cutoffs
   for the rest of the season (src/models/season_predictor.py).
"""
from __future__ import annotations

from dataclasses import dataclass


def t(mmss: str) -> float:
    """'1:32.064' -> 92.064 seconds."""
    m, s = mmss.split(":")
    return int(m) * 60 + float(s)


@dataclass
class QualiResult:
    year: int
    circuit: str
    pole_driver: str
    pole_time_s: float
    weather: str
    full_grid: list | None = None
    source: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# PART 1 — circuit pairs for the 2026 regulation pace delta
# (unchanged from the original Baku-only analysis; see notes for confounds)
# ---------------------------------------------------------------------------

RESULTS_2026 = [
    QualiResult(2026, "Australia (Albert Park)", "George Russell", t("1:18.518"), "dry",
        full_grid=[
            dict(driver="George Russell", q1=t("1:19.507"), q2=t("1:18.934"), q3=t("1:18.518")),
            dict(driver="Kimi Antonelli", q1=t("1:20.120"), q2=t("1:19.435"), q3=t("1:18.811")),
            dict(driver="Isack Hadjar", q1=t("1:20.023"), q2=t("1:19.653"), q3=t("1:19.303")),
            dict(driver="Charles Leclerc", q1=t("1:20.226"), q2=t("1:19.357"), q3=t("1:19.327")),
            dict(driver="Oscar Piastri", q1=t("1:19.664"), q2=t("1:19.525"), q3=t("1:19.380")),
            dict(driver="Lando Norris", q1=t("1:20.010"), q2=t("1:19.882"), q3=t("1:19.475")),
            dict(driver="Lewis Hamilton", q1=t("1:19.811"), q2=t("1:19.921"), q3=t("1:19.478")),
            dict(driver="Liam Lawson", q1=t("1:20.491"), q2=t("1:20.144"), q3=t("1:19.994")),
            dict(driver="Arvid Lindblad", q1=t("1:20.409"), q2=t("1:19.971"), q3=t("1:21.247")),
            dict(driver="Gabriel Bortoleto", q1=t("1:20.495"), q2=t("1:20.221"), q3=None),
            dict(driver="Nico Hulkenberg", q1=t("1:21.024"), q2=t("1:20.303"), q3=None),
            dict(driver="Oliver Bearman", q1=t("1:21.247"), q2=t("1:20.311"), q3=None),
            dict(driver="Esteban Ocon", q1=t("1:20.759"), q2=t("1:20.491"), q3=None),
            dict(driver="Pierre Gasly", q1=t("1:21.138"), q2=t("1:20.501"), q3=None),
            dict(driver="Alexander Albon", q1=t("1:21.051"), q2=t("1:20.941"), q3=None),
            dict(driver="Franco Colapinto", q1=t("1:21.200"), q2=t("1:21.270"), q3=None),
            dict(driver="Fernando Alonso", q1=t("1:21.969"), q2=None, q3=None),
        ],
        source="formula1.com/en/results/2026/races/1279/australia/qualifying",
        notes="22-car grid, bottom 6 eliminated in Q1 (new for 2026)."),
    QualiResult(2026, "China (Shanghai)", "Kimi Antonelli", t("1:32.064"), "dry",
        full_grid=[
            dict(driver="Kimi Antonelli", q1=t("1:33.305"), q2=t("1:32.443"), q3=t("1:32.064")),
            dict(driver="George Russell", q1=t("1:33.262"), q2=t("1:32.523"), q3=t("1:32.286")),
            dict(driver="Lewis Hamilton", q1=t("1:33.522"), q2=t("1:32.567"), q3=t("1:32.415")),
            dict(driver="Charles Leclerc", q1=t("1:33.175"), q2=t("1:32.486"), q3=t("1:32.428")),
            dict(driver="Oscar Piastri", q1=t("1:33.590"), q2=t("1:33.130"), q3=t("1:32.550")),
            dict(driver="Lando Norris", q1=t("1:33.535"), q2=t("1:32.910"), q3=t("1:32.608")),
            dict(driver="Pierre Gasly", q1=t("1:33.788"), q2=t("1:33.003"), q3=t("1:32.873")),
            dict(driver="Max Verstappen", q1=t("1:33.417"), q2=t("1:33.098"), q3=t("1:33.002")),
            dict(driver="Isack Hadjar", q1=t("1:33.632"), q2=t("1:33.352"), q3=t("1:33.121")),
            dict(driver="Oliver Bearman", q1=t("1:33.687"), q2=t("1:33.197"), q3=t("1:33.292")),
            dict(driver="Nico Hulkenberg", q1=t("1:34.116"), q2=t("1:33.354"), q3=None),
            dict(driver="Franco Colapinto", q1=t("1:33.634"), q2=t("1:33.357"), q3=None),
            dict(driver="Esteban Ocon", q1=t("1:33.974"), q2=t("1:33.538"), q3=None),
            dict(driver="Liam Lawson", q1=t("1:34.139"), q2=t("1:33.765"), q3=None),
            dict(driver="Arvid Lindblad", q1=t("1:33.906"), q2=t("1:33.784"), q3=None),
            dict(driver="Gabriel Bortoleto", q1=t("1:33.549"), q2=t("1:33.965"), q3=None),
            dict(driver="Carlos Sainz", q1=t("1:34.317"), q2=None, q3=None),
        ],
        source="formula1.com/en/results/2026/races/1280/china/qualifying"),
    QualiResult(2026, "Japan (Suzuka)", "Kimi Antonelli", t("1:28.778"), "cloudy",
        source="en.wikipedia.org/wiki/2026_Japanese_Grand_Prix"),
    QualiResult(2026, "Miami", "Kimi Antonelli", t("1:27.798"), "cloudy",
        source="en.wikipedia.org/wiki/2026_Miami_Grand_Prix"),
    QualiResult(2026, "Canada (Montreal)", "George Russell", t("1:12.578"), "cloudy",
        source="en.wikipedia.org/wiki/2026_Canadian_Grand_Prix"),
    QualiResult(2026, "Italy (Monza)", "Pierre Gasly", t("1:21.786"), "dry",
        source="planetf1.com/news/f1-results-italian-grand-prix-2026-qualifying",
        notes="Closest-in-time comparison to Baku (round 13, days before round 14)."),
]

RESULTS_2025 = [
    QualiResult(2025, "Australia (Albert Park)", "Lando Norris", t("1:15.096"), "light rain",
        source="en.wikipedia.org/wiki/2025_Australian_Grand_Prix",
        notes="WEATHER CONFOUND vs 2026's dry session — excluded from clean delta."),
    QualiResult(2025, "China (Shanghai)", "Oscar Piastri", t("1:30.641"), "dry",
        full_grid=[
            dict(driver="Oscar Piastri", q1=t("1:31.591"), q2=t("1:31.200"), q3=t("1:30.641")),
            dict(driver="George Russell", q1=t("1:31.295"), q2=t("1:31.307"), q3=t("1:30.723")),
            dict(driver="Lando Norris", q1=t("1:30.983"), q2=t("1:30.787"), q3=t("1:30.793")),
            dict(driver="Max Verstappen", q1=t("1:31.424"), q2=t("1:31.142"), q3=t("1:30.817")),
            dict(driver="Lewis Hamilton", q1=t("1:31.690"), q2=t("1:31.501"), q3=t("1:30.927")),
            dict(driver="Charles Leclerc", q1=t("1:31.579"), q2=t("1:31.450"), q3=t("1:31.021")),
            dict(driver="Isack Hadjar", q1=t("1:31.162"), q2=t("1:31.253"), q3=t("1:31.079")),
            dict(driver="Kimi Antonelli", q1=t("1:31.676"), q2=t("1:31.590"), q3=t("1:31.103")),
            dict(driver="Yuki Tsunoda", q1=t("1:31.238"), q2=t("1:31.260"), q3=t("1:31.638")),
            dict(driver="Alexander Albon", q1=t("1:31.503"), q2=t("1:31.595"), q3=t("1:31.706")),
            dict(driver="Esteban Ocon", q1=t("1:31.876"), q2=t("1:31.625"), q3=None),
            dict(driver="Nico Hulkenberg", q1=t("1:31.921"), q2=t("1:31.632"), q3=None),
            dict(driver="Fernando Alonso", q1=t("1:31.719"), q2=t("1:31.688"), q3=None),
            dict(driver="Lance Stroll", q1=t("1:31.923"), q2=t("1:31.773"), q3=None),
            dict(driver="Carlos Sainz", q1=t("1:31.628"), q2=t("1:31.840"), q3=None),
            dict(driver="Pierre Gasly", q1=t("1:31.992"), q2=None, q3=None),
        ],
        source="formula1.com/en/results/2025/races/1255/china/qualifying"),
    QualiResult(2025, "Japan (Suzuka)", "Max Verstappen", t("1:26.983"), "dry (track record)",
        source="en.wikipedia.org/wiki/2025_Japanese_Grand_Prix"),
    QualiResult(2025, "Miami", "Max Verstappen", t("1:26.204"), "cloudy",
        source="en.wikipedia.org/wiki/2025_Miami_Grand_Prix"),
    QualiResult(2025, "Canada (Montreal)", "George Russell", t("1:10.899"), "sunny",
        source="en.wikipedia.org/wiki/2025_Canadian_Grand_Prix"),
    QualiResult(2025, "Italy (Monza)", "Max Verstappen", t("1:18.792"), "sunny",
        source="en.wikipedia.org/wiki/2025_Italian_Grand_Prix",
        notes="All-time qualifying speed record (264.7 km/h) — unusually fast baseline, "
              "inflates the apparent 2026 delta at this circuit."),
]

CLEAN_DELTA_CIRCUITS = ["China (Shanghai)", "Japan (Suzuka)", "Miami", "Canada (Montreal)"]
ALL_DELTA_CIRCUITS = CLEAN_DELTA_CIRCUITS + ["Australia (Albert Park)", "Italy (Monza)"]


# ---------------------------------------------------------------------------
# PART 2 — every remaining round of the 2026 season, Baku onward, each with
# its own real recent-history baseline.
# ---------------------------------------------------------------------------

@dataclass
class CircuitBaseline:
    round_no: int
    circuit: str
    race_date_2026: str
    baseline_years: list      # years used for the "recent dry pace" baseline
    baseline_pole_times_s: list
    confidence: str           # "high" / "medium" / "low"
    layout_adjustment_s: float
    notes: str
    source: str


REMAINING_CALENDAR = [
    CircuitBaseline(
        round_no=14, circuit="Azerbaijan (Baku)", race_date_2026="2026-09-26",
        baseline_years=[2022, 2023, 2024], baseline_pole_times_s=[t("1:41.359"), t("1:40.203"), t("1:41.365")],
        confidence="high", layout_adjustment_s=-0.3,
        notes="2025 pole (1:41.117) excluded from baseline: rain-affected Q3, six red flags. "
              "2.2km pit straight — longest full-throttle stretch of any circuit bar Jeddah/Spa/Vegas, "
              "favoring 2026's low-drag active aero X-mode, hence the negative layout adjustment.",
        source="en.wikipedia.org/wiki/{2022,2023,2024}_Azerbaijan_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=16, circuit="Bahrain-in-Malaysia (Sepang)", race_date_2026="2026-10-04",
        baseline_years=[2017], baseline_pole_times_s=[t("1:30.076")],
        confidence="low", layout_adjustment_s=0.0,
        notes="Sepang has not hosted F1 since 2017 — a 9-year-old baseline from an entirely different "
              "car generation (2017's wide, high-downforce cars were among the fastest-cornering in "
              "history; 2022 ground-effect and now 2026 rules have both intervened since). The "
              "clean-circuit delta is being extrapolated across TWO regulation eras here, not one — "
              "treat this prediction as substantially less reliable than every other circuit in this "
              "repo, a genuine best-effort estimate rather than a defensible forecast.",
        source="en.wikipedia.org/wiki/2017_Malaysian_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=17, circuit="Singapore (Marina Bay)", race_date_2026="2026-10-11",
        baseline_years=[2025], baseline_pole_times_s=[t("1:29.158")],
        confidence="medium", layout_adjustment_s=0.0,
        notes="Only one clean dry baseline year used (2025) — 2023/2024 pole times were on a "
              "since-shortened track layout (4.940km vs earlier 5.063km), not directly comparable.",
        source="en.wikipedia.org/wiki/2025_Singapore_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=18, circuit="United States (Austin, COTA)", race_date_2026="2026-10-18",
        baseline_years=[2023, 2024, 2025], baseline_pole_times_s=[t("1:34.723"), t("1:32.330"), t("1:32.510")],
        confidence="high", layout_adjustment_s=0.0,
        notes="Three consecutive dry-pole years averaged.",
        source="en.wikipedia.org/wiki/{2023,2024,2025}_United_States_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=19, circuit="Mexico City", race_date_2026="2026-10-25",
        baseline_years=[2025], baseline_pole_times_s=[t("1:15.586")],
        confidence="medium", layout_adjustment_s=0.1,
        notes="Single clean year used (2025, sunny, pole by Norris) — 2023 excluded for weather. "
              "High-altitude circuit (2,240m) — thin air changes aero and cooling efficiency "
              "differently than at sea level; 2026's active aero and higher-electrical-deployment "
              "power unit could behave slightly differently here than the clean-circuit average "
              "suggests. Small positive adjustment reflects genuine uncertainty, not a strong prior.",
        source="en.wikipedia.org/wiki/2025_Mexico_City_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=20, circuit="Brazil (Interlagos)", race_date_2026="2026-11-08",
        baseline_years=[2025], baseline_pole_times_s=[t("1:09.511")],
        confidence="medium", layout_adjustment_s=0.0,
        notes="2023/2024 poles excluded: 2024 was rain-affected (1:23.405, far off pace), 2023 was "
              "also a weather-affected session. 2025 (cloudy, representative pace) used alone.",
        source="en.wikipedia.org/wiki/2025_S%C3%A3o_Paulo_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=21, circuit="Las Vegas", race_date_2026="2026-11-21",
        baseline_years=[2024], baseline_pole_times_s=[t("1:32.312")],
        confidence="medium", layout_adjustment_s=-0.2,
        notes="2025's pole (1:47.934) was rain-affected — NOT used as baseline (would overstate "
              "2026 deficit by ~15s if included). 2024's dry pole used instead. Long straights "
              "(the Strip itself) again favor low-drag active aero, hence a negative adjustment "
              "similar to Baku's, though smaller since Vegas has more medium-speed corners too.",
        source="en.wikipedia.org/wiki/2024_Las_Vegas_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=22, circuit="Qatar (Lusail)", race_date_2026="2026-11-29",
        baseline_years=[2023, 2024, 2025], baseline_pole_times_s=[t("1:23.778"), t("1:20.575"), t("1:19.387")],
        confidence="medium", layout_adjustment_s=0.0,
        notes="Baseline years show a clear downward trend even under stable 2023-2025 rules "
              "(track evolution / tyre allocation changes), so the 3-year average may overstate "
              "true 'normal' pace — using 2025 alone would be an alternative, faster baseline.",
        source="en.wikipedia.org/wiki/{2023,2024,2025}_Qatar_Grand_Prix",
    ),
    CircuitBaseline(
        round_no=23, circuit="Abu Dhabi (Yas Marina)", race_date_2026="2026-12-06",
        baseline_years=[2023, 2024, 2025], baseline_pole_times_s=[t("1:23.445"), t("1:22.595"), t("1:22.207")],
        confidence="high", layout_adjustment_s=0.0,
        notes="Season finale — by this point 2026 cars will have had a full season of development; "
              "if the regulation gap narrows over the year (unconfirmed — see Monza discussion), "
              "this is the round where that would show up most, and the clean early-season delta "
              "may overstate the true Abu Dhabi deficit.",
        source="en.wikipedia.org/wiki/{2023,2024,2025}_Abu_Dhabi_Grand_Prix",
    ),
]

