"""02_analyze.py — has elite single sculling gotten faster?

Inputs:  data/olympic_singles_finals.csv (all Olympic Final A results, 1976–2024)
Outputs: results/games_summary.csv, charts/*.png

Scope decisions (see README for rationale):
  * Men: 1976–2024 (always 2000m).
  * Women: 1988–2024 only (1976–1984 were raced over 1000m — not comparable).
  * Focus on WINNING times + 6th-place times (field depth), not averages:
    finals fields are small and conditions vary, so the winner is the most
    stable signal of the frontier.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")
CHARTS = os.path.join(HERE, "charts")
os.makedirs(RESULTS, exist_ok=True)
os.makedirs(CHARTS, exist_ok=True)

df = pd.read_csv(os.path.join(DATA, "olympic_singles_finals.csv"))

# comparable sample: 2000m races only
c = df[df.distance_m == 2000].copy()

winners = c[c.final_rank == 1].copy()
sixth = c[c.final_rank == 6].copy()

summary = (
    winners[["year", "event", "rower", "nation", "time_str", "time_sec"]]
    .merge(sixth[["year", "event", "time_sec"]].rename(columns={"time_sec": "sixth_sec"}),
            on=["year", "event"])
)
summary["depth_gap_sec"] = summary["sixth_sec"] - summary["time_sec"]
summary.to_csv(os.path.join(RESULTS, "games_summary.csv"), index=False)

for event in ["Men's", "Women's"]:
    w = winners[winners.event == event].sort_values("year")
    slope, intercept, r, p, se = stats.linregress(w["year"], w["time_sec"])
    print(f"{event}: winning time trend {slope:+.2f} sec/year "
          f"(R²={r**2:.2f}, p={p:.3f})")
    first, last = w.iloc[0], w.iloc[-1]
    print(f"  {int(first.year)}: {first.time_str} ({first.rower}) -> "
          f"{int(last.year)}: {last.time_str} ({last.rower})")
    # early vs late era split at 2000
    for era, grp in [("1976-2000", w[w.year <= 2000]), ("2000-2024", w[w.year >= 2000])]:
        if len(grp) >= 3:
            s, *_ = stats.linregress(grp["year"], grp["time_sec"])
            print(f"  era {era}: {s:+.2f} sec/year")

# field depth: is 6th place catching the winner?
for event in ["Men's", "Women's"]:
    s = summary[summary.event == event].sort_values("year")
    slope, *_ = stats.linregress(s["year"], s["depth_gap_sec"])[:1]
    print(f"{event}: winner-to-6th gap trend {slope:+.2f} sec/year "
          f"(now ~{s.iloc[-1].depth_gap_sec:.1f}s)")

# gender gap among winners, 1988+
merged = (
    winners[winners.event == "Men's"][["year", "time_sec"]].rename(columns={"time_sec": "men"})
    .merge(winners[winners.event == "Women's"][["year", "time_sec"]].rename(columns={"time_sec": "women"}),
           on="year")
)
merged["gap_ratio"] = merged["women"] / merged["men"]
print("\nwomen's/men's winning time ratio:")
print(merged[["year", "gap_ratio"]].round({"gap_ratio": 3}).to_string(index=False))

# ---------- charts ----------
# 1. winning times over time
fig, ax = plt.subplots(figsize=(10, 5.5))
for event, color in [("Men's", "#4C78A8"), ("Women's", "#E45756")]:
    w = winners[winners.event == event].sort_values("year")
    ax.plot(w["year"], w["time_sec"] / 60, "o-", color=color, label=event, markersize=6)
    for _, r in w.iterrows():
        if r["year"] in (1976, 2024):
            ax.annotate(f"{r['rower'].split()[-1]} {r['time_str']}",
                        (r["year"], r["time_sec"] / 60),
                        textcoords="offset points", xytext=(6, 6), fontsize=8, color=color)
ax.axvspan(1976, 1984, color="gray", alpha=0.08)
ax.text(1980, 8.15, "women raced 1000m\nbefore 1988 (excluded)",
        ha="center", fontsize=8, color="gray")
ax.set_xlabel("Olympic Games")
ax.set_ylabel("Winning time (minutes)")
ax.set_title("Olympic single sculls winning times: faster, but the curve is flattening")
ax.set_xticks(sorted(c["year"].unique()))
ax.set_xticklabels([str(int(y)) for y in sorted(c["year"].unique())], rotation=45)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "winning_times.png"), dpi=150)
plt.close(fig)

# 2. field depth: winner vs 6th
fig, ax = plt.subplots(figsize=(10, 5))
for event, color in [("Men's", "#4C78A8"), ("Women's", "#E45756")]:
    s = summary[summary.event == event].sort_values("year")
    ax.plot(s["year"], s["depth_gap_sec"], "o-", color=color, label=f"{event} (6th − winner)")
ax.set_xlabel("Olympic Games")
ax.set_ylabel("Seconds behind the winner")
ax.set_title("The field is catching up: 6th place is closer to gold than it used to be")
ax.set_xticks(sorted(c["year"].unique()))
ax.set_xticklabels([str(int(y)) for y in sorted(c["year"].unique())], rotation=45)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "field_depth.png"), dpi=150)
plt.close(fig)

# 3. gender gap ratio
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(merged["year"], merged["gap_ratio"], "o-", color="#7A5195", markersize=7)
ax.axhline(1.0, color="black", linewidth=0.8)
ax.set_xlabel("Olympic Games")
ax.set_ylabel("Women's winning time / Men's winning time")
ax.set_title("The gender gap in winning times, 1988–2024")
ax.set_xticks(sorted(merged["year"].unique()))
ax.set_xticklabels([str(int(y)) for y in sorted(merged["year"].unique())], rotation=45)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "gender_gap.png"), dpi=150)
plt.close(fig)

print("\ncharts + games_summary.csv saved")
