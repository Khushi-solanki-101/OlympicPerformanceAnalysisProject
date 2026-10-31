"""
Global Olympic Sports Performance Analysis
------------------------------------------
Loads Olympic athlete-event records, cleans them, answers eight analytical
questions and saves charts + summary tables.

Usage:
    python olympic_analysis.py
Data lookup order:
    1. data/athlete_events.csv         (real Kaggle dataset, if you add it)
    2. data/athlete_events_sample.csv  (simulated sample shipped with this repo)
"""
from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent
SHOTS = BASE.parent / "Screenshots"
OUT = BASE / "outputs"
SHOTS.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
PALETTE = sns.color_palette("deep")


# ------------------------------------------------------------------ 1. LOAD
def load_data():
    real = BASE / "data" / "athlete_events.csv"
    sample = BASE / "data" / "athlete_events_sample.csv"
    path = real if real.exists() else sample
    df = pd.read_csv(path)
    print(f"Loaded {len(df):,} rows from {path.name}")
    return df, path.name


# ----------------------------------------------------------------- 2. CLEAN
def clean(df):
    df = df.drop_duplicates().copy()
    df["Medal"] = df["Medal"].fillna("None")
    df["Won_Medal"] = (df["Medal"] != "None").astype(int)
    df["Age"] = df.groupby("Sport")["Age"].transform(lambda s: s.fillna(s.median()))
    df["Sex"] = df["Sex"].str.upper()
    df["BMI"] = df["Weight"] / (df["Height"] / 100) ** 2
    return df


def save(fig, name):
    fig.tight_layout()
    fig.savefig(SHOTS / name, dpi=130)
    plt.close(fig)
    print("saved", name)


# -------------------------------------------------------------- 3. ANALYSIS
def top_countries(df):
    t = (df[df.Won_Medal == 1].groupby("Team")["Medal"].value_counts().unstack(fill_value=0)
         .reindex(columns=["Gold", "Silver", "Bronze"], fill_value=0))
    t["Total"] = t.sum(axis=1)
    t = t.sort_values("Total", ascending=False)
    t.to_csv(OUT / "medal_table.csv")
    top = t.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(12, 7))
    top[["Gold", "Silver", "Bronze"]].plot(kind="barh", stacked=True, ax=ax,
                                           color=["#D4AF37", "#A8A9AD", "#CD7F32"])
    ax.set_title("Top 10 Countries by Total Medals"); ax.set_xlabel("Medals"); ax.set_ylabel("")
    save(fig, "01_top10_medal_table.png")
    return t


def medal_trend(df, table):
    top5 = table.head(5).index
    d = (df[(df.Won_Medal == 1) & df.Team.isin(top5) & (df.Season == "Summer")]
         .groupby(["Year", "Team"]).size().unstack(fill_value=0))
    fig, ax = plt.subplots(figsize=(12, 7))
    for i, c in enumerate(d.columns):
        ax.plot(d.index, d[c], marker="o", lw=2.5, label=c, color=PALETTE[i])
    ax.set_title("Summer Games Medal Trend: Top 5 Countries")
    ax.set_xlabel("Year"); ax.set_ylabel("Medals"); ax.legend(frameon=False)
    save(fig, "02_medal_trend_top5.png")


def gender_participation(df):
    d = df.groupby(["Year", "Season", "Sex"]).ID.nunique().reset_index()
    p = d.pivot_table(index=["Year", "Season"], columns="Sex", values="ID", fill_value=0).reset_index()
    p["Female_Share"] = p["F"] / (p["F"] + p["M"]) * 100
    p.to_csv(OUT / "gender_participation.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 7))
    for i, s in enumerate(["Summer", "Winter"]):
        q = p[p.Season == s].sort_values("Year")
        ax.plot(q.Year, q.Female_Share, marker="o", lw=2.5, label=s, color=PALETTE[i])
    ax.axhline(50, ls="--", color="grey", lw=1)
    ax.set_title("Female Share of Athletes Over Time"); ax.set_ylabel("Female athletes (%)")
    ax.set_xlabel("Year"); ax.legend(frameon=False)
    save(fig, "03_gender_participation.png")
    return p


def host_advantage(df):
    host = df.groupby(["Year", "Season"]).City.first().reset_index()
    # Host NOC is the team that sends most athletes relative to its own average
    medals = df[df.Won_Medal == 1].groupby(["NOC", "Year", "Season"]).size().rename("Medals").reset_index()
    host_map = {"Barcelona": "ESP", "Atlanta": "USA", "Sydney": "AUS", "Beijing": "CHN", "London": "GBR",
                "Rio de Janeiro": "BRA", "Tokyo": "JPN", "Albertville": "FRA", "Lillehammer": "NOR",
                "Nagano": "JPN", "Salt Lake City": "USA", "Turin": "ITA", "Vancouver": "CAN",
                "Sochi": "RUS", "Pyeongchang": "KOR"}
    rows = []
    for _, r in host.iterrows():
        noc = host_map.get(r.City)
        if noc is None:
            continue
        m = medals[(medals.NOC == noc) & (medals.Season == r.Season)]
        at_host = m.loc[m.Year == r.Year, "Medals"].sum()
        other = m.loc[m.Year != r.Year, "Medals"]
        avg_other = other.mean() if len(other) else float("nan")
        rows.append({"City": r.City, "Year": r.Year, "Season": r.Season, "Host_NOC": noc,
                     "Medals_As_Host": at_host, "Avg_Medals_Other_Games": round(avg_other, 1)})
    h = pd.DataFrame(rows).dropna()
    h["Uplift_%"] = ((h.Medals_As_Host / h.Avg_Medals_Other_Games - 1) * 100).round(1)
    h.to_csv(OUT / "host_advantage.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 7))
    hh = h.sort_values("Uplift_%")
    ax.barh(hh.City + " " + hh.Year.astype(str), hh["Uplift_%"],
            color=["#2a9d8f" if v >= 0 else "#e76f51" for v in hh["Uplift_%"]])
    ax.axvline(0, color="black", lw=1)
    ax.set_title("Host-Nation Effect: Medal Uplift vs the Same Country at Other Games")
    ax.set_xlabel("Uplift (%)")
    save(fig, "04_host_advantage.png")
    return h


def age_by_sport(df):
    order = df.groupby("Sport").Age.median().sort_values().index
    fig, ax = plt.subplots(figsize=(12, 9))
    sns.boxplot(data=df, y="Sport", x="Age", order=order, ax=ax, palette="viridis", fliersize=1)
    ax.set_title("Athlete Age Distribution by Sport"); ax.set_ylabel("")
    save(fig, "05_age_by_sport.png")
    return df.groupby("Sport").Age.median().sort_values()


def medal_efficiency(df):
    g = df.groupby("Team").agg(Athletes=("ID", "count"), Medals=("Won_Medal", "sum"))
    g = g[g.Athletes >= 500]
    g["Medal_Rate_%"] = (g.Medals / g.Athletes * 100).round(2)
    g = g.sort_values("Medal_Rate_%", ascending=False)
    g.to_csv(OUT / "medal_efficiency.csv")
    top = g.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(top.index, top["Medal_Rate_%"], color=PALETTE[2])
    ax.set_title("Medal Conversion Rate: Medals per 100 Athlete Entries (Top 10)")
    ax.set_xlabel("Medals per 100 entries")
    save(fig, "06_medal_efficiency.png")
    return g


def season_split(df):
    d = df[df.Won_Medal == 1].groupby(["Team", "Season"]).size().unstack(fill_value=0)
    d["Total"] = d.sum(axis=1)
    d = d.sort_values("Total", ascending=False).head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(12, 7))
    d[["Summer", "Winter"]].plot(kind="barh", stacked=True, ax=ax, color=["#f4a261", "#4ea8de"])
    ax.set_title("Summer vs Winter Medals: Top 10 Countries"); ax.set_ylabel("")
    ax.set_xlabel("Medals")
    save(fig, "07_summer_vs_winter.png")
    return d


def country_sport_heatmap(df):
    top = df[df.Won_Medal == 1].groupby("Team").size().sort_values(ascending=False).head(10).index
    d = (df[(df.Won_Medal == 1) & df.Team.isin(top)].groupby(["Team", "Sport"]).size().unstack(fill_value=0))
    d = d.loc[top, d.sum().sort_values(ascending=False).head(12).index]
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.heatmap(d, annot=True, fmt="d", cmap="YlOrRd", cbar_kws={"label": "Medals"}, ax=ax)
    ax.set_title("Where Medals Come From: Top Countries x Top Sports"); ax.set_xlabel(""); ax.set_ylabel("")
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    save(fig, "08_country_sport_heatmap.png")


# ------------------------------------------------------------------- 4. MAIN
def main():
    df, source = load_data()
    df = clean(df)
    table = top_countries(df)
    medal_trend(df, table)
    gender = gender_participation(df)
    host = host_advantage(df)
    ages = age_by_sport(df)
    eff = medal_efficiency(df)
    season_split(df)
    country_sport_heatmap(df)

    summary = {
        "data_source": source,
        "rows": int(len(df)),
        "years": [int(df.Year.min()), int(df.Year.max())],
        "countries": int(df.Team.nunique()),
        "sports": int(df.Sport.nunique()),
        "total_medals": int(df.Won_Medal.sum()),
        "top_country": table.index[0],
        "top_country_medals": int(table.iloc[0].Total),
        "top3": table.head(3)["Total"].astype(int).to_dict(),
        "female_share_first_games": round(float(gender.sort_values("Year").iloc[0].Female_Share), 1),
        "female_share_last_games": round(float(gender.sort_values("Year").iloc[-1].Female_Share), 1),
        "avg_host_uplift_pct": round(float(host["Uplift_%"].mean()), 1),
        "youngest_median_sport": ages.index[0], "youngest_median_age": float(ages.iloc[0]),
        "oldest_median_sport": ages.index[-1], "oldest_median_age": float(ages.iloc[-1]),
        "best_conversion_country": eff.index[0], "best_conversion_rate": float(eff.iloc[0]["Medal_Rate_%"]),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
