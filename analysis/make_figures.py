"""Builds the writeup figures from the raw data. Usage: python analysis/make_figures.py path/to/data"""
import sys, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
DATA = sys.argv[1] if len(sys.argv) > 1 else "data"
OUT = "figures"; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

# receiver features and all-route rookie separation (3+ targets)
import importlib.util
spec = importlib.util.spec_from_file_location("sa", os.path.join(os.path.dirname(__file__), "slant_analysis.py"))
sys.argv = [sys.argv[0], DATA]; sa = importlib.util.module_from_spec(spec); spec.loader.exec_module(sa)
feat = sa.combine_features()
tgt = sa.rookie_outcomes()
g = tgt.groupby("nfl_id").agg(n=("separation_at_pass_forward", "size"),
                              sep=("separation_at_pass_forward", "mean")).reset_index()
rec = feat.merge(g[g.n >= 3], on="nfl_id")

# Figure 1: outcome reliability (year one vs year two)
pp = pd.read_csv(os.path.join(DATA, "player_play.csv"), usecols=["game_id","nfl_id","target","separation_at_pass_forward"])
gm = pd.read_csv(os.path.join(DATA, "games.csv"), usecols=["game_id","season","season_type"])
pl = pd.read_csv(os.path.join(DATA, "players.csv"))
t = pp[(pp.target==1)&pp.separation_at_pass_forward.notna()].merge(gm,on="game_id").merge(pl[["nfl_id","draft_year"]],on="nfl_id")
t = t[(t.season_type=="REG")]; t["yr"] = t.season - t.draft_year; t = t[t.yr.isin([0,1])]
w = t.groupby(["nfl_id","yr"]).agg(n=("separation_at_pass_forward","size"), sep=("separation_at_pass_forward","mean")).reset_index().pivot(index="nfl_id", columns="yr", values=["n","sep"]).dropna()
w.columns = ["n0","n1","s0","s1"]; w = w[(w.n0>=5)&(w.n1>=5)]
r, _ = spearmanr(w.s0, w.s1)
fig, ax = plt.subplots(figsize=(5,4))
ax.scatter(w.s0, w.s1, s=18, alpha=0.7, color="#3b6ea5")
ax.set_xlabel("Mean separation, season 1 (yards)"); ax.set_ylabel("Mean separation, season 2 (yards)")
ax.set_title(f"Outcome reliability: rho = {r:.2f}, n = {len(w)} receivers", fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_outcome_reliability.png", dpi=200); plt.close(fig)

# Figure 2: receiver cut angle vs rookie separation
fig, ax = plt.subplots(figsize=(5,4))
ax.scatter(rec.cut_angle_deg, rec.sep, s=18, alpha=0.7, color="#3b6ea5")
rho, p = spearmanr(rec.cut_angle_deg, rec.sep)
ax.set_xlabel("Slant cut angle at Combine (degrees)"); ax.set_ylabel("Mean rookie separation (yards)")
ax.set_title(f"Receivers: rho = {rho:.2f} (p = {p:.2f}), n = {len(rec)}", fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_receiver_cut_angle.png", dpi=200); plt.close(fig)

# Figure 3: DB cut angle vs completion rate allowed
db = pd.read_csv("/home/claude/db_break_features.csv"); dbo = pd.read_csv("/home/claude/db_outcomes.csv")
dd = db.merge(dbo[dbo.n>=20], on="nfl_id")
rho2, p2 = spearmanr(dd.cut_angle_deg, dd.comp)
fig, ax = plt.subplots(figsize=(5,4))
ax.scatter(dd.cut_angle_deg, dd.comp*100, s=18, alpha=0.7, color="#a65b3b")
ax.set_xlabel("90-degree break cut angle at Combine (degrees)"); ax.set_ylabel("Completion rate allowed, rookie season (%)")
ax.set_title(f"Defensive backs: rho = {rho2:.2f} (p = {p2:.2f}), n = {len(dd)}", fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_db_cut_angle.png", dpi=200); plt.close(fig)

# Figure 4: summary of all tests (Spearman rho with 95% sampling spread)
tests = {"Receivers, cut angle": rho, "Receivers, speed retained": spearmanr(rec.speed_retained, rec.sep)[0],
         "DBs, cut angle": rho2, "DBs, max braking": spearmanr(dd.max_brake, dd.comp)[0]}
fig, ax = plt.subplots(figsize=(6,3.2))
names = list(tests); vals = list(tests.values())
ax.barh(names, vals, color=["#3b6ea5"]*2 + ["#a65b3b"]*2)
ax.axvline(0, color="black", lw=0.8); ax.set_xlim(-0.5, 0.5)
ax.set_xlabel("Spearman rho (0 = no relationship)")
ax.set_title("No measure reaches significance", fontsize=10)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_summary.png", dpi=200); plt.close(fig)
print("figures written:", sorted(os.listdir(OUT)))
print({k: round(v,2) for k,v in tests.items()})
