# Global Olympic Sports Performance Analysis

**Link for the Project Demo video:**

https://drive.google.com/file/d/REPLACE_WITH_YOUR_DRIVE_FILE_ID/view?usp=drive_link

---

## Overview
This project analyses Olympic athlete and medal records to understand how countries, sports,
athletes and host cities shape performance at the Summer and Winter Games. It cleans the raw
data, answers eight analytical questions with Python, and exports charts and summary tables
that can be used in a report or dashboard.

## Objectives
- Identify which countries lead the medal table and how their performance changed over time.
- Measure how efficiently countries convert athlete entries into medals.
- Track female participation across Games.
- Quantify the host-nation effect.
- Compare athlete age profiles across sports.
- Show which sports drive each country's medal count, and the Summer vs Winter split.

## Repository Structure
```
.
├── Readme.md
├── Global Olympic Sports Performance Analysis - Project Documentation.pdf
├── Screenshots/                 # 8 analysis charts (PNG)
└── source code/
    ├── olympic_analysis.py      # cleaning + analysis + charts
    ├── generate_sample_data.py  # builds the sample dataset
    ├── requirements.txt
    ├── data/
    │   └── athlete_events_sample.csv
    └── outputs/                 # medal_table.csv, host_advantage.csv, summary.json, ...
```

## Dataset
The code is written for the schema of the public Kaggle dataset **"120 years of Olympic history:
athletes and results"** (`athlete_events.csv`) with columns `ID, Name, Sex, Age, Height, Weight,
Team, NOC, Games, Year, Season, City, Sport, Event, Medal`.

> **Data note:** the file included in this repository (`athlete_events_sample.csv`) is a
> **simulated sample** that follows the same schema so the project runs end to end without
> downloads. Its numbers are illustrative and are **not** official Olympic results.
> To analyse real data, download `athlete_events.csv` from Kaggle, place it in
> `source code/data/`, and run the script again. It will use the real file automatically.

## Methodology
1. **Load:** read the real dataset if present, otherwise the sample.
2. **Clean:** drop duplicates, label non-medalists, fill missing ages with the sport median, compute BMI.
3. **Analyse:** medal table, trends, participation, host effect, age profile, conversion rate, season split, country x sport matrix.
4. **Export:** charts to `Screenshots/`, tables and `summary.json` to `source code/outputs/`.

## Analyses and Charts
| # | Question | Chart |
|---|----------|-------|
| 1 | Which countries win the most medals? | `01_top10_medal_table.png` |
| 2 | How did the top 5 evolve at the Summer Games? | `02_medal_trend_top5.png` |
| 3 | How has female participation changed? | `03_gender_participation.png` |
| 4 | Is there a host-nation advantage? | `04_host_advantage.png` |
| 5 | How does athlete age differ by sport? | `05_age_by_sport.png` |
| 6 | Who converts entries into medals best? | `06_medal_efficiency.png` |
| 7 | How do Summer and Winter medals split? | `07_summer_vs_winter.png` |
| 8 | Which sports drive each country's medals? | `08_country_sport_heatmap.png` |

## How to Run
```bash
cd "source code"
pip install -r requirements.txt
python generate_sample_data.py     # optional: rebuilds the sample dataset
python olympic_analysis.py
```

## Tech Stack
Python 3, pandas, NumPy, Matplotlib, Seaborn.

## Skills Demonstrated
Data cleaning, exploratory data analysis, data visualisation, statistical summarisation,
analytical storytelling, reproducible project structure, Git and GitHub.

## Future Improvements
- Run on the full 120-year Kaggle dataset and add per-capita and GDP-adjusted comparisons.
- Build an interactive Power BI or Tableau dashboard from the exported tables.
- Add a predictive model for medal probability.
