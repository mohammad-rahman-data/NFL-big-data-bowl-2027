# NFL Big Data Bowl 2027: Combine Break Measures and Rookie NFL Performance

Entry for the 2027 NFL Big Data Bowl, Open Track.
**Author:** Mohammad Rahman

## Summary

This project asks whether movement captured by 10 Hz sensors during NFL Scouting Combine drills predicts how prospects perform in their rookie regular season. It tests break-related measures (cut angle, speed kept through a break) for wide receivers and defensive backs against two outcomes: separation on targets for receivers, and completion rate allowed for defensive backs.

**Result:** no robust link found for either position. One receiver lead (dagger route, speed retained) did not survive a pre-specified check and is reported as withdrawn. The full account is in [WRITEUP.md](WRITEUP.md).

## Repository contents

- `WRITEUP.md`: the written submission, including the negative result and its limits.
- `FINDINGS.md`: a dated log of every test, including the ones that didn't hold up.
- `notebooks/combine_break_analysis.ipynb`: the reproducible notebook, with outputs saved.
- `analysis/`: the scripts behind each result (`slant_analysis.py`, `dagger_analysis.py`, `db_analysis.py`, `make_figures.py`, `build_notebook.py`) and `results.csv`.
- `figures/`: the four charts used in the writeup.

## Data

The data comes from the Kaggle competition: https://www.kaggle.com/competitions/nfl-big-data-bowl-2027

Raw files are not included in this repository. They are over 2 GB and are governed by the competition rules. Download them from the competition page and place them in a local `data/` folder, which is git-ignored.

## How to run

Install the dependencies:

```
pip install pandas numpy scipy matplotlib
```

Then, with the Kaggle files in `data/`:

```
python analysis/slant_analysis.py data
python analysis/dagger_analysis.py data
python analysis/db_analysis.py data
python analysis/make_figures.py data
```

Or open `notebooks/combine_break_analysis.ipynb` and run it top to bottom. Set `DATA` in the setup cell to the folder containing the CSVs.

**Public Kaggle notebook:** https://www.kaggle.com/code/mohammadrahma/combine-break-measures-reproducible-analysis

## Approach

1. Rebuild speed from positional tracking, since the acceleration field in the data is unsigned.
2. Detect the break as the frame of largest heading change while moving at 3 m/s or faster, and extract cut angle and speed retained.
3. Define outcomes from the rookie regular season: mean separation on targets (receivers) and completion rate allowed on covered attempts (defensive backs).
4. Test each measure with Spearman rank correlation, across minimum sample sizes and route sets.
5. Check the receiver outcome's reliability across seasons, then test an alternative break definition for the one lead found.

## Status

Analysis complete. The results are negative for both positions, and the writeup is final. The notebook is public on Kaggle and is the submission's reproducible analysis.

