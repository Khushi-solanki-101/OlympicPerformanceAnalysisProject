"""
Generates a SAMPLE dataset that follows the schema of the public Kaggle dataset
"120 years of Olympic history: athletes and results" (athlete_events.csv).

IMPORTANT: The values produced here are SIMULATED for demonstration and testing.
They are not real athlete records. To run the analysis on real data, download the
Kaggle file and save it as data/athlete_events.csv (see README.md).
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# (NOC, team name, strength 0-1, summer sport affinities, winter strength)
COUNTRIES = [
    ("USA", "United States", 1.00, 0.55), ("CHN", "China", 0.90, 0.35),
    ("GBR", "Great Britain", 0.70, 0.20), ("RUS", "Russia", 0.80, 0.70),
    ("GER", "Germany", 0.75, 0.85), ("JPN", "Japan", 0.60, 0.30),
    ("AUS", "Australia", 0.60, 0.15), ("FRA", "France", 0.60, 0.40),
    ("ITA", "Italy", 0.55, 0.50), ("NED", "Netherlands", 0.45, 0.55),
    ("CAN", "Canada", 0.45, 0.90), ("KOR", "South Korea", 0.45, 0.45),
    ("BRA", "Brazil", 0.40, 0.02), ("ESP", "Spain", 0.35, 0.05),
    ("KEN", "Kenya", 0.25, 0.00), ("JAM", "Jamaica", 0.25, 0.01),
    ("NOR", "Norway", 0.25, 1.00), ("SWE", "Sweden", 0.30, 0.60),
    ("IND", "India", 0.15, 0.01), ("NZL", "New Zealand", 0.25, 0.10),
    ("CUB", "Cuba", 0.30, 0.00), ("HUN", "Hungary", 0.30, 0.05),
    ("SUI", "Switzerland", 0.25, 0.75), ("POL", "Poland", 0.25, 0.20),
    ("ETH", "Ethiopia", 0.15, 0.00), ("RSA", "South Africa", 0.20, 0.00),
    ("MEX", "Mexico", 0.15, 0.01), ("TUR", "Turkey", 0.15, 0.02),
]

SUMMER_SPORTS = {
    "Athletics": (24, 175, 68, 0.22), "Swimming": (22, 180, 72, 0.14),
    "Gymnastics": (21, 160, 55, 0.07), "Cycling": (26, 178, 70, 0.07),
    "Rowing": (26, 188, 85, 0.06), "Judo": (25, 172, 75, 0.05),
    "Football": (25, 178, 73, 0.07), "Basketball": (26, 195, 92, 0.04),
    "Weightlifting": (25, 170, 80, 0.04), "Boxing": (24, 174, 70, 0.04),
    "Tennis": (25, 180, 72, 0.03), "Shooting": (33, 172, 74, 0.03),
    "Diving": (21, 165, 60, 0.03), "Fencing": (27, 178, 70, 0.03),
    "Hockey": (26, 178, 73, 0.04),
}
WINTER_SPORTS = {
    "Alpine Skiing": (25, 176, 74, 0.20), "Cross Country Skiing": (26, 177, 70, 0.18),
    "Speed Skating": (24, 175, 72, 0.12), "Ice Hockey": (26, 182, 87, 0.12),
    "Biathlon": (27, 176, 70, 0.10), "Figure Skating": (22, 165, 58, 0.08),
    "Snowboarding": (24, 175, 70, 0.08), "Bobsleigh": (28, 180, 90, 0.06),
    "Freestyle Skiing": (24, 173, 68, 0.06),
}
# Games: (year, season, host NOC, city)
GAMES = [
    (1992, "Summer", "ESP", "Barcelona"), (1992, "Winter", "FRA", "Albertville"),
    (1996, "Summer", "USA", "Atlanta"), (1994, "Winter", "NOR", "Lillehammer"),
    (1998, "Winter", "JPN", "Nagano"), (2000, "Summer", "AUS", "Sydney"),
    (2002, "Winter", "USA", "Salt Lake City"), (2004, "Summer", "GRE", "Athens"),
    (2006, "Winter", "ITA", "Turin"), (2008, "Summer", "CHN", "Beijing"),
    (2010, "Winter", "CAN", "Vancouver"), (2012, "Summer", "GBR", "London"),
    (2014, "Winter", "RUS", "Sochi"), (2016, "Summer", "BRA", "Rio de Janeiro"),
    (2018, "Winter", "KOR", "Pyeongchang"), (2020, "Summer", "JPN", "Tokyo"),
]

rows, pid = [], 1
for year, season, host, city in GAMES:
    sports = SUMMER_SPORTS if season == "Summer" else WINTER_SPORTS
    names = list(sports); weights = np.array([v[3] for v in sports.values()]); weights /= weights.sum()
    for noc, team, s_str, w_str in COUNTRIES:
        strength = s_str if season == "Summer" else w_str
        if strength <= 0.005:
            continue
        base = 260 if season == "Summer" else 70
        n_ath = int(base * (0.25 + 0.75 * strength) * rng.uniform(0.85, 1.15))
        if noc == host:
            n_ath = int(n_ath * 1.25)
        n_ath = max(n_ath, 3)
        for _ in range(n_ath):
            sport = rng.choice(names, p=weights)
            age_m, h_m, w_m, _p = sports[sport]
            sex = rng.choice(["M", "F"], p=[0.55, 0.45] if year < 2004 else [0.5, 0.5] if year < 2012 else [0.48, 0.52])
            sx = 0.93 if sex == "F" else 1.0
            medal_p = 0.02 + 0.22 * strength ** 1.6
            if noc == host:
                medal_p *= 1.35
            r = rng.random()
            medal = None
            if r < medal_p:
                medal = rng.choice(["Gold", "Silver", "Bronze"], p=[0.36, 0.32, 0.32])
            rows.append({
                "ID": pid, "Name": f"Athlete {pid:06d}", "Sex": sex,
                "Age": int(np.clip(rng.normal(age_m, 3.2), 15, 45)),
                "Height": round(float(rng.normal(h_m * sx, 6)), 0),
                "Weight": round(float(rng.normal(w_m * (0.85 if sex == "F" else 1), 7)), 0),
                "Team": team, "NOC": noc, "Games": f"{year} {season}", "Year": year,
                "Season": season, "City": city, "Sport": sport,
                "Event": f"{sport} Event {rng.integers(1, 9)}", "Medal": medal,
            })
            pid += 1

df = pd.DataFrame(rows)
df.to_csv("data/athlete_events_sample.csv", index=False)
print(f"Wrote data/athlete_events_sample.csv with {len(df):,} rows")
