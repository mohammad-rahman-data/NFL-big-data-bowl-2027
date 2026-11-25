# Findings log

A running record of what has been tested, including results that did not hold up.
Keep entries dated and factual. Update the README only when the project scope changes.

## Setup
- Data: NFL Big Data Bowl 2027 (Kaggle). Raw files kept locally in `data/`, not in this repo.
- Focus so far: wide receivers, slant route (`SLANT_ROUTE_LEFT`) on the Combine tracking data.

## Data checks
- Combine tracking: 10 Hz, about 4 s per slant attempt (roughly 40 frames). 107 receivers, 110 attempts; 3 receivers have two attempts, and the faster one is kept.
- Raw `a` (acceleration) field is unsigned, so it cannot show braking. Signed acceleration is derived from x/y positions instead.

## Features (slant drill)
- Cut angle: total heading change around the break. Median about 24 degrees (range 18 to 33).
- Pre-break speed: median about 5.3 m/s.
- Speed retained: speed 1 s after the break divided by pre-break peak. Median about 1.36, so receivers accelerate through the cut.
- Braking: almost no receivers slow down in the slant. Only about 2% lose more than 1 m/s in any half-second window.

## Outcome
- Rookie season (season = draft year), regular season only.
- Mean `separation_at_pass_forward` on targets.

## Results (Spearman rank correlation, features vs rookie separation)

| Test | Prospects | Cut angle | Speed retained | Pre-break speed |
|---|---|---|---|---|
| Slant routes only, 5+ targets (regular season) | 22 | 0.04 (p=0.85) | -0.03 (p=0.89) | -0.14 (p=0.53) |
| All routes, 3+ targets | 73 | -0.02 (p=0.87) | 0.12 (p=0.33) | -0.01 (p=0.92) |
| All routes, 5+ targets | 66 | -0.04 (p=0.77) | 0.10 (p=0.43) | -0.02 (p=0.85) |
| Short routes, 3+ targets | 64 | -0.01 (p=0.93) | 0.14 (p=0.27) | -0.18 (p=0.16) |

**Conclusion so far:** no reliable link between slant-drill Combine measures and rookie-season separation. Negative result, consistent across thresholds and route sets.

## Outcome reliability check
- Receivers with 5+ regular-season targets in both their first and second seasons: 54.
- Year-one vs year-two mean separation: Spearman rho = 0.56 (p < 0.001), Pearson r = 0.53.
- Interpretation: the outcome carries real signal, so the null result is not just noise in the outcome. But reliability is moderate, which attenuates any true link. With these sample sizes, a strong link is unlikely, while a weak or moderate link cannot be ruled out.

## Defensive backs (drill: BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL)
- Sample: 122 DBs with tracking on this drill. Break features: median cut angle about 47 degrees; median braking about 0.3 m/s^2, so braking is measurable here, unlike the slant.
- Outcome: completion rate allowed on covered pass attempts (C, I, IN; excluding no-assignment plays), rookie regular season. Limitation: this is the play result while the DB was on the field, not a record of the exact ball he defended.
- Results (Spearman, features vs completion rate allowed):

| Min plays | DBs | Cut angle | Max braking | Speed retained | Pre-break speed |
|---|---|---|---|---|---|
| 20 | 77 | 0.19 (p=0.10) | 0.14 (p=0.21) | 0.07 (p=0.54) | -0.10 (p=0.39) |
| 40 | 65 | 0.18 (p=0.15) | 0.15 (p=0.22) | 0.04 (p=0.74) | -0.07 (p=0.57) |

- Conclusion: no significant link. The cut-angle sign is opposite to what a coach would expect (sharper cuts, more completions allowed), which is more likely noise than a real effect.
- Reproduce with `python analysis/db_analysis.py path/to/data`.

## Receivers, dagger route (DAGGER_ROUTE_LEFT) - first positive lead
- Run after the slant and defensive back nulls, so treat as exploratory until confirmed.
- Sample: 107 receivers with tracking; 73 with 3+ rookie-season targets.
- Measure: speed retained through the break (speed one second after the break / pre-break peak). Median 0.94, so most receivers slow slightly through the break.
- Results (Spearman, speed retained vs rookie separation):

| Test | Prospects | rho | p |
|---|---|---|---|
| All routes, 3+ targets | 73 | 0.30 | 0.010 |
| All routes, 5+ targets | 66 | 0.32 | 0.010 |
| Short routes, 3+ targets | 64 | 0.19 | 0.141 |
| Deep and intermediate routes, 3+ targets | 67 | 0.35 | 0.003 |
| Split half of rookie targets, first | 66 | 0.32 | 0.009 |
| Split half of rookie targets, second | 66 | 0.27 | 0.030 |
| Draft class 2023 only | 28 | 0.34 | 0.073 |
| Draft class 2024 only | 24 | 0.38 | 0.067 |
| Draft class 2025 only | 21 | 0.14 | 0.540 |

- Interpretation: direction is consistent across routes, splits and classes, and strongest on deep routes, which fits the football logic. But several tests were run, so the headline p-value overstates confidence. Per-class results are too small to be significant on their own.
- Status: see the break-definition check below. The result does not survive it.
- Reproduce with `python analysis/dagger_analysis.py path/to/data`.

## Dagger lead: break-definition check (fixed in advance)
- Alternative break rule, fixed before running: frame of sharpest braking (most negative signed acceleration) at 3 m/s or faster. The original rule used the largest heading change.
- Results (speed retained vs rookie separation, all routes):

| Min targets | Prospects | rho | p |
|---|---|---|---|
| 3 | 73 | 0.06 | 0.61 |
| 5 | 66 | 0.14 | 0.27 |

- Result: the dagger lead does not survive the alternative break definition. It depends on how the break is detected, which is a warning sign for an artefact.
- Caveat: the braking rule sometimes picks a near-stop (speed retained as low as 0.05), so it is a weaker detector. This check shows the lead is not robust, but it does not fully prove it is false.
- Status: dagger result withdrawn as a lead. Do not build a screen or writeup claim on it.

## Known issues and limits
- Small samples per prospect; rookies have few targets on any single route.
- Combine drill vs in-game separation: different settings, and separation depends heavily on quarterback and play design.
- Only one drill and one outcome tested.
- An early version included preseason and postseason games; corrected to regular season only.
- The first slant-only row (69 prospects) was run without the regular-season filter, due to a silent dtype check. Corrected: with the filter, only 22 prospects qualify, so that row is too small to say anything.
- Reproduce everything with `python analysis/slant_analysis.py path/to/data`. The script writes `analysis/results.csv`.

## Next options (not started)
- Write up the null result as a rigorous negative finding.
- Test three-cone or dagger route measures (smaller samples).
- Test defensive backs with the same framework.
