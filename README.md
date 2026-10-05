# Has Elite Rowing Gotten Faster? 48 Years of Olympic Single Sculls

**Question:** Are Olympic champions actually faster than they used to be — or does
it just feel that way because the boats look sleeker?

**Stack:** Python (pandas, scipy, matplotlib) · dataset: every Olympic single
sculls Final A, 1976–2024 (150 results, scraped from Wikipedia's compilation of
official results — see `scripts/01_scrape.py`)

---

## The data (and the traps in it)

Single sculls is the purest event to study: one athlete, no crew changes or
seat-racing politics confounding the times. But three traps had to be handled
before any trend meant anything:

| Trap | Handling |
|---|---|
| **Women raced 1000m, not 2000m, from 1976–1984** | Women's analysis covers the 2000m era only (1988–2024). The 1000m times are kept in the CSV with `distance_m` marked, not silently mixed in. This is the kind of domain gotcha that ruins a naive analysis. |
| **Wikipedia table layouts changed across 50 years** ("Rower" → "Athletes Names", "Final A" → "Finals A") | The scraper finds the Final A *heading* and parses the table after it, instead of assuming page structure. An earlier "last table" heuristic grabbed Final E for 2004 women's — caught by validating winners against known champions. |
| **One race ≠ one data point about human progress** | Olympic finals are single observations under wildly varying conditions (2012 London was rowed into a headwind; 2024 Paris was fast). Trends are reported with R² and p-values, not vibes. |

## What I found

**1. Yes — the men are ~51 seconds faster than 1976.**
Winning time fell from 7:29.03 (Karppinen, Montreal) to 6:37.57 (Zeidler, Paris):
**−0.67 sec/year**, R²=0.56, p=0.003. A real, significant trend.

**2. But the improvement is slowing down.**
1976–2000: **−1.60 sec/year**. 2000–2024: **−0.63 sec/year**. The easy gains —
carbon-fiber hulls, hatchet/cleaver blades (early 90s), professionalized
training — are banked. We're approaching the flat part of the curve, where
progress comes in fractions.

**3. For the women, the honest answer is "can't tell from winning times."**
Trend is −0.49 sec/year but **not significant** (p=0.196, R²=0.20, n=10 Games).
With one race per Olympiad, weather noise swamps the signal — 2012's winning
time (7:54, headwind) is 36 seconds slower than 2020's (7:14, fast water), and
no training effect is 36 seconds. A portfolio that reports a non-result instead
of torturing the data is more trustworthy than one that doesn't.

**4. The field is getting deeper, even where the frontier stalls.**
The gap from winner to 6th place is shrinking (~−0.1 sec/year for both events).
Gold isn't pulling away; the chasing pack is catching up — consistent with
professionalization spreading beyond the traditional powers.

**5. The gender gap isn't closing (in winning times).**
Women's/men's winning-time ratio has hovered around **1.05–1.14 since 1988**
with no trend — it bounces with conditions rather than narrowing. (Physiology
suggests a stable gap; the data doesn't contradict that.)

## Caveats

- **Olympic winning times understate the sport's speed.** Finals are tactical —
  rowers race the field, not the clock — and world bests (set at World Cups in
  fast conditions) run several seconds quicker.
- **Boycotts (1980, 1984)** thinned the fields; those points are kept but
  flagged, not dropped.
- n=13 (men) / n=10 (women) Olympiads: this is a small sample wearing a big
  story. The men's trend survives it; the women's doesn't — and that's the point.

## Reproduce it

```bash
pip install -r requirements.txt
python scripts/01_scrape.py    # ~1 min, polite 1s delay between pages
python scripts/02_analyze.py   # trends, stats, charts
```

Outputs: `data/olympic_singles_finals.csv`, `results/games_summary.csv`,
`charts/*.png`. Re-scraping hits Wikipedia live; the committed CSV is the
frozen dataset the analysis ran on.
