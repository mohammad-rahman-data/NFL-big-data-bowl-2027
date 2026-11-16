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
| Slant routes only | 69 | -0.05 (p=0.69) | -0.04 (p=0.75) | -0.02 (p=0.88) |
| All routes, 3+ targets | 73 | -0.02 (p=0.87) | 0.11 (p=0.34) | -0.01 (p=0.92) |
| All routes, 5+ targets | 66 | -0.04 (p=0.76) | 0.09 (p=0.45) | -0.02 (p=0.85) |
| Short routes, 3+ targets | 64 | -0.01 (p=0.93) | 0.14 (p=0.27) | -0.18 (p=0.16) |

**Conclusion so far:** no reliable link between slant-drill Combine measures and rookie-season separation. Negative result, consistent across thresholds and route sets.

## Known issues and limits
- Small samples per prospect; rookies have few targets on any single route.
- Combine drill vs in-game separation: different settings, and separation depends heavily on quarterback and play design.
- Only one drill and one outcome tested.
- An early version included preseason and postseason games; corrected to regular season only.

## Next options (not started)
- Write up the null result as a rigorous negative finding.
- Test three-cone or dagger route measures (smaller samples).
- Test defensive backs with the same framework.
