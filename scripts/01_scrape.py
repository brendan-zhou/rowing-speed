"""01_scrape.py — Olympic single sculls finals results, 1976–2024.

Source: Wikipedia "Rowing at the {year} Summer Olympics – {Men's/Women's}
single sculls" pages (compiling official results). For each page we locate the
"Final A" heading and parse the table immediately after it — the medal final.
(An earlier "last table on page" heuristic grabbed Final E for 2004 women's;
heading-aware parsing fixed it. Lesson documented in README.)

Output: data/olympic_singles_finals.csv
Columns: year, city, event, distance_m, final_rank, rower, nation,
         time_str, time_sec

Notes / judgment calls:
  * Times parsed from strings like "6:37.57". Rows without a parseable time
    (DNF/DNS/walkover) are dropped.
  * Medalists' Rank cells are often blank/icons on Wikipedia; final_rank is
    assigned by table order (1–6).
  * Women's Olympic singles were raced over 1000m in 1976–1984, then 2000m
    from 1988. distance_m records this — the two eras are NOT comparable.
  * 1980 Moscow had a boycott-depleted field — flagged in analysis, not dropped.
"""
import os
import re
import time
import urllib.request

import bs4
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

GAMES = [
    (1976, "Montreal"), (1980, "Moscow"), (1984, "Los Angeles"),
    (1988, "Seoul"), (1992, "Barcelona"), (1996, "Atlanta"),
    (2000, "Sydney"), (2004, "Athens"), (2008, "Beijing"),
    (2012, "London"), (2016, "Rio de Janeiro"), (2020, "Tokyo"),
    (2024, "Paris"),
]
UA = {"User-Agent": "Mozilla/5.0 (data-portfolio research project)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read()


def parse_time(s):
    """'6:37.57' -> 397.57 seconds. Returns None if unparseable."""
    s = str(s).strip()
    m = re.match(r"^(\d+):(\d{1,2})(?:\.(\d+))?$", s)
    if not m:
        return None
    frac = float("0." + m.group(3)) if m.group(3) else 0.0
    return int(m.group(1)) * 60 + int(m.group(2)) + frac


def final_a_table(html):
    """Find the 'Final A' heading, return the table right after it."""
    soup = bs4.BeautifulSoup(html, "lxml")
    for h in soup.find_all(["h2", "h3", "h4"]):
        t = h.get_text().strip().lower()
        # matches "Final A", "Finals A" (1980 uses the plural)
        if t.startswith("final") and re.search(r"\ba\b", t):
            tbl = h.find_next("table")
            if tbl is not None:
                return pd.read_html(str(tbl))[0]
    return None


def scrape_event(year, event_slug, event_label):
    html = fetch(
        f"https://en.wikipedia.org/wiki/Rowing_at_the_{year}"
        f"_Summer_Olympics_%E2%80%93_{event_slug}_single_sculls"
    )
    ft = final_a_table(html)
    if ft is None:
        print(f"  !! no Final A table for {year} {event_label}")
        return []
    ft.columns = [str(c).strip().lower() for c in ft.columns]
    rower_col = next(c for c in ft.columns
                     if "rower" in c or "athlete" in c or "competitor" in c)
    time_col = next(c for c in ft.columns if c == "time")
    nation_col = next(
        (c for c in ft.columns if "nation" in c or "country" in c or "team" in c),
        None,
    )
    rows = []
    for i, (_, r) in enumerate(ft.iterrows(), start=1):
        t = parse_time(r[time_col])
        if t is None:
            continue
        rows.append({
            "year": year,
            "event": event_label,
            "distance_m": 1000 if (event_label == "Women's" and year <= 1984) else 2000,
            "final_rank": i,
            "rower": str(r[rower_col]).strip(),
            "nation": str(r[nation_col]).strip() if nation_col else "",
            "time_str": str(r[time_col]).strip(),
            "time_sec": round(t, 2),
        })
    return rows


all_rows = []
for year, city in GAMES:
    for event_slug, event_label in [("Men%27s", "Men's"), ("Women%27s", "Women's")]:
        print(f"scraping {year} {event_label}...", flush=True)
        try:
            rows = scrape_event(year, event_slug, event_label)
            for r in rows:
                r["city"] = city
            print(f"  got {len(rows)} finalists")
            all_rows.extend(rows)
        except Exception as e:  # noqa: BLE001 — log and continue; verified below
            print(f"  !! FAILED: {e}")
        time.sleep(1.0)  # be polite to Wikipedia

df = pd.DataFrame(all_rows)
out = os.path.join(DATA, "olympic_singles_finals.csv")
df.to_csv(out, index=False)
print(f"\nwrote {out}: {df.shape}")
print(df.groupby(["year", "event"]).size())
