# NFL Big Data Bowl 2027: Combine Tracking to NFL Performance

Entry for the 2027 NFL Big Data Bowl (Open Track).

## Summary

This project asks whether movement captured by 10 Hz sensors during NFL Scouting Combine drills says anything useful about how prospects perform in regular-season games. The current focus is wide receivers and deceleration into breaks, compared with on-field separation.

## Data

The data comes from the Kaggle competition: https://www.kaggle.com/competitions/nfl-big-data-bowl-2027

Raw files are not included in this repository because they are over 2 GB. Download them from the competition page and place them in a local `data/` folder (this folder is git-ignored).

## Approach (planned)

1. Extract break-related movement features per prospect from the Combine drill tracking.
2. Check that the features are stable across repeated attempts.
3. Define a rookie-season outcome from regular-season tracking and play-level data (for example, separation at target).
4. Test the relationship with simple statistical methods and bootstrapped confidence intervals.
5. Turn the findings into a usable screen or profile for evaluators.

## Status

Setup stage. No results yet.

## How to run

Instructions will be added once the analysis code is in place.
