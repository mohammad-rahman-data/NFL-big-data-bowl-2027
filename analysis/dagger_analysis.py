"""
Reproduces the slant-route analysis from raw competition files.

Usage:
    python analysis/slant_analysis.py path/to/data_folder

Expects the Kaggle CSVs in data_folder: combine_tracking.csv, player_play.csv,
games.csv, players.csv.
"""
import sys, os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

DATA = sys.argv[1] if len(sys.argv) > 1 else "data"
SLANT_DRILL = "DAGGER_ROUTE_LEFT"
SHORT_ROUTES = ["SLANT", "IN", "CROSS", "OUT", "HITCH", "FLAT"]


def combine_features():
    ct = pd.read_csv(os.path.join(DATA, "combine_tracking.csv"))
    s = ct[(ct.drill_name == SLANT_DRILL) & (ct.entity_type == "PLAYER")].copy()
    s["t"] = pd.to_datetime(s.time)
    s = s.sort_values(["nfl_id", "attempt", "t"]).reset_index(drop=True)

    rows = []
    for (pid, att), p in s.groupby(["nfl_id", "attempt"]):
        p = p.reset_index(drop=True)
        if len(p) < 20:
            continue
        n = len(p)
        idx = np.arange(n)

        # speed from positions (smoothed over 3 frames)
        dt = p.t.diff().dt.total_seconds().fillna(0.1).values.copy()
        dt[dt <= 0] = 0.1
        v = np.r_[0, np.hypot(np.diff(p.x), np.diff(p.y))] / dt
        v = pd.Series(v).rolling(3, center=True, min_periods=1).mean().values

        # break = sharpest heading change while moving at >= 3 m/s
        d = np.diff(p.dir.values)
        d = (d + 180) % 360 - 180
        dd = np.r_[0, np.abs(d)]
        ok = np.where((v >= 3) & (idx >= 5) & (idx < n - 5))[0]
        if len(ok) == 0:
            continue
        b = ok[np.argmax(dd[ok])]

        rows.append(dict(
            nfl_id=pid,
            attempt=att,
            duration=(n - 1) / 10,
            pre_speed=v[max(b - 10, 0):b + 1].max(),
            speed_after_1s=v[min(b + 10, n - 1)],
            cut_angle_deg=np.abs(d[max(b - 3, 0):b + 3]).sum(),
        ))

    f = pd.DataFrame(rows)
    # prospects with two attempts: keep the faster (shorter) one
    f = f.sort_values("duration").drop_duplicates("nfl_id", keep="first")
    f["speed_retained"] = f.speed_after_1s / f.pre_speed
    return f[["nfl_id", "cut_angle_deg", "pre_speed", "speed_retained"]]


def rookie_outcomes():
    pp = pd.read_csv(os.path.join(DATA, "player_play.csv"),
                     usecols=["game_id", "nfl_id", "route_ran", "target",
                              "separation_at_pass_forward"])
    gm = pd.read_csv(os.path.join(DATA, "games.csv"),
                     usecols=["game_id", "season", "season_type"])
    pl = pd.read_csv(os.path.join(DATA, "players.csv"))

    t = (pp[(pp.target == 1) & pp.separation_at_pass_forward.notna()]
         .merge(gm, on="game_id")
         .merge(pl[["nfl_id", "draft_year"]], on="nfl_id"))
    # rookie season = draft year, regular season only
    t = t[(t.season == t.draft_year) & (t.season_type == "REG")]
    return t


def summarise(features, targets, label, min_targets):
    g = (targets.groupby("nfl_id")
         .agg(n=("separation_at_pass_forward", "size"),
              sep=("separation_at_pass_forward", "mean"))
         .reset_index())
    g = g[g.n >= min_targets]
    d = features.merge(g, on="nfl_id")
    out = {"test": label, "min_targets": min_targets, "prospects": len(d)}
    for c in ["cut_angle_deg", "speed_retained", "pre_speed"]:
        r, p = spearmanr(d[c], d.sep)
        out[c] = f"rho={r:.2f} (p={p:.2f})"
    return out


if __name__ == "__main__":
    feats = combine_features()
    tgt = rookie_outcomes()
    rows = []
    slant_targets = tgt[tgt.route_ran == "SLANT"]
    rows.append(summarise(feats, slant_targets, "Slant routes only", 5))
    rows.append(summarise(feats, tgt, "All routes", 3))
    rows.append(summarise(feats, tgt, "All routes", 5))
    rows.append(summarise(feats, tgt[tgt.route_ran.isin(SHORT_ROUTES)],
                          "Short routes", 3))
    res = pd.DataFrame(rows)
    print(res.to_string(index=False))
    res.to_csv("analysis/results.csv", index=False)
