# Network Intelligence — Network Performance & SLA Analytics

A dark-themed Streamlit portfolio dashboard that presents the findings of a complete telecom network performance analysis. The dashboard translates an analytical notebook into an interactive business intelligence experience, covering regional and technology comparisons, daily trends, SiteID-group prioritisation, and transparent data-quality documentation.

> **Note:** This project uses an illustrative historical dataset. It is not connected to a live telecom operator network. All uptime figures are analytical proxies, not contractual SLA compliance.

---

## Business Context

Telecom network operations teams need to monitor service availability, identify under-performing segments, and prioritise field investigations with limited time and budget. This project demonstrates a disciplined analytics workflow applied to a synthetic but realistic network performance dataset.

The analysis evaluates uptime, downtime, fault counts and traffic volume across five regions and three network technologies (3G, 4G, 5G), using an assumed 99.9% uptime benchmark as an analytical reference point.

---

## Project Objectives

1. Assess how observed uptime compares to the assumed 99.9% benchmark at record, regional, technology and SiteID-group levels.
2. Compare regional and technology performance while documenting observation coverage.
3. Describe daily temporal patterns without over-interpreting short-window variation.
4. Identify candidate SiteID groups for further operational investigation using a transparent heuristic.
5. Communicate data limitations honestly so that conclusions are proportionate to the evidence.

---

## Dataset Description

| Item | Detail |
|------|--------|
|| Network file | `network_perf_raw.csv` — one row per observation |
| Tower master | `towers_site_master.csv` — supplementary site attributes (excluded from joins) |
| Data source | [Network-Performance-SLA GitHub repository](https://github.com/amrit1426/Network-Performance-SLA) |
| Loaded from | Raw GitHub URLs — `network_perf_raw.csv` and `towers_site_master.csv` are loaded directly from the repository's `data/raw/` folder. No local copies are required. |
| Rows | 1,000 |
| Columns | 8 (`SiteID`, `Region`, `NetworkType`, `Uptime`, `Downtime`, `Faults`, `Traffic`, `Date`) |
| SiteID identifiers | 199 distinct |
| Regions | 5 (Central, East, North, South, West) |
| Technologies | 3 (3G, 4G, 5G) |
| Period | 01 Jan 2026 – 30 Jan 2026 |
| Missing values | 0 in network dataset |

**Key data-quality findings:**
- 189 of 199 SiteID identifiers appear across multiple regions.
- 187 of 199 SiteID identifiers appear across multiple network technologies.
- 146 rows (14.6%) share a SiteID+Date combination with another observation.
- Zero identifier overlap between the network dataset and the tower master dataset.
- The measurement window behind each record is undocumented.

---

## Tools and Technologies

| Component | Technology |
|-----------|-----------|
| Analytics notebook | Python, pandas, NumPy, SciPy, Matplotlib, Seaborn |
| Dashboard | Streamlit, Plotly |
| Version control | Git / GitHub |

---

## Analytics Notebook

`network_performance_analysis.ipynb` contains the full reproducible analysis:

- Data loading and configuration with remote GitHub fallback
- Data-quality assessment (missing values, duplicates, cross-region/cross-technology SiteIDs, identifier overlap with tower master)
- KPI definitions and aggregation logic
- Executive summary (dynamically generated from computed results)
- Regional and technology performance comparisons
- Daily trends and day-of-week descriptive summaries
- SiteID-group exploratory analysis and prioritisation
- Bootstrap confidence intervals (95%, cluster bootstrap by SiteID)
- Statistical diagnostics: ANOVA, Kruskal-Wallis, Levene's test, Holm-Bonferroni adjustment, eta-squared effect size, ICC
- Spearman rank correlations
- Evidence-based recommendations with findings, hypotheses and quantified-impact sections kept separate
- Limitations and future enhancements

The notebook is the analytical source of truth. The Streamlit dashboard presents these findings interactively without re-running or expanding the analysis.

---

## Streamlit Dashboard Features

The **Network Intelligence** dashboard provides six modules accessible from the sidebar:

1. **Executive Overview** — network-wide KPIs, record coverage by technology, regional uptime vs benchmark.
2. **Regional Performance** — regional comparison tables, uptime bars, share of records below benchmark.
3. **Technology Performance** — technology-level KPIs, uptime, downtime and fault comparisons.
4. **Daily Trends** — interactive date-filtered daily uptime, downtime and record-coverage charts.
5. **SiteID-Group Explorer** — eligible SiteID-group table with exploratory priority scores and uptime ranking.
6. **Data Quality & Limitations** — dataset overview, key quality flags and honest limitation statements.

### Design

- Dark navy/charcoal interface with teal and cyan accents.
- High-contrast KPI cards with accent borders.
- Interactive Plotly charts with consistent dark styling.
- Sidebar filters for date range, region and technology.
- Responsive layout optimised for desktop use.

---

## Project Structure

```
Network-Performance-SLA/
├── app.py
├── network_performance_analysis.ipynb
├── network_perf_raw.csv
├── towers_site_master.csv
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/amrit1426/Network-Performance-SLA.git
cd Network-Performance-SLA
pip install -r requirements.txt
```

---

## How to Run the Dashboard

```bash
streamlit run app.py
```

The application opens in your default browser at `http://localhost:8501`.

---

## Important Assumptions and Limitations

- **Assumed benchmark, not contractual SLA:** The 99.9% uptime figure is an analytical benchmark. No SLA contract, measurement period, exclusions or penalty rules are available.
- **SiteID identity:** SiteID identifiers have not been established as stable physical tower identifiers. They appear across multiple regions and technologies, and 14.6% of rows share a SiteID+Date combination with another observation.
- **Undocumented measurement windows:** The duration behind each record is undocumented. Uptime and downtime are analysed separately and never converted into one another.
- **No causal information:** No fault categories, maintenance records, power status, backhaul type, vendor or cost fields exist. Root causes cannot be identified.
- **Tower master excluded:** The tower master dataset has zero matching identifiers with the network data. It is not joined.
- **Short observation window:** One month of data cannot establish seasonality, trends or recurring weekly patterns.
- **Sparse sampling:** Most SiteID groups have few observations; site-level averages and rankings are noisy.

---

## Future Deployment

The dashboard is ready for deployment on Streamlit Community Cloud.

Placeholder deployment URL (replace after deployment):

```
https://YOUR-STREAMLIT-APP-NAME.streamlit.app
```

---

## GitHub Repository

[https://github.com/amrit1426/Network-Performance-SLA](https://github.com/amrit1426/Network-Performance-SLA)

---

## License

This project is shared as a portfolio piece. The dataset is illustrative.
