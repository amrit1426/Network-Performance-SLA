# 📡 Telecom Network Performance & SLA Analytics

**Network Performance SLA | Telecom Data Analytics**

---

## Business Problem

As a Network Operations Analyst at a telecom operator, you are responsible for monitoring network health, ensuring SLA compliance, and driving operational improvements across a multi-vendor, multi-technology infrastructure. This project analyzes network performance data from 199 sites across 5 regions over 30 days, evaluating KPIs like uptime, downtime, faults, and traffic against SLA benchmarks.

## Intended Stakeholder

- **Primary:** Network Operations Manager / NOC Lead
- **Secondary:** Field Engineering teams, Vendor management, Regulatory compliance team

## Business Questions

1. Which regions and technologies are missing SLA compliance?
2. What are the root causes of downtime?
3. Are there daily patterns affecting network performance?
4. Which sites represent the highest operational risk?
5. What concrete actions can improve overall network availability?

## Key Performance Indicators (KPIs)

- Average Uptime % (target: ≥99.9%)
- Total Downtime (minutes)
- Total Faults
- Average Traffic Load
- Max Downtime events
- Regional performance variance
- Technology-wise performance

## Dataset Source

- **Source:** Telecom Network Performance Dataset
- **URL:** https://github.com/olufemi-builds/Telecom-Network-Performance-Dashboard
- **License:** Public / Educational use
- **Size:** 1,000 rows × 8 columns
- **Time Period:** January 1-30, 2026
- **Coverage:** 199 sites, 5 regions, 3 technologies (3G/4G/5G)
- **Raw file:** `data/raw/network_perf_raw.csv`
- **Tower master:** `data/raw/towers_site_master.csv`

## Tools and Skills Demonstrated

- Python (pandas, numpy, matplotlib, seaborn, scipy)
- Data visualization and KPI dashboarding
- Statistical analysis (ANOVA, correlation)
- Business-oriented network analytics
- Streamlit app deployment
- Jupyter notebook development

## Project Structure

```
TelecomNetworkPerformance_SLA/
├── data/
│   ├── raw/
│   │   ├── network_perf_raw.csv
│   │   └── towers_site_master.csv
│   └── processed/
├── notebooks/
│   └── network_performance_analysis.ipynb
├── reports/
│   └── figures/
│       ├── network_performance.png
│       └── daily_trends.png
├── src/
│   └── utilities.py
├── scripts/
│   └── run_analysis.py
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/config.toml
└── README.md
```

## Setup and Execution

### Local Setup
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Run Analysis Script
```bash
python scripts/run_analysis.py
```

### Launch Streamlit App
```bash
streamlit run app.py
```

### Open Jupyter Notebook
```bash
jupyter notebook notebooks/network_performance_analysis.ipynb
```

## Key Findings

| Metric | Value |
|--------|-------|
| Total Records | 1,000 |
| Sites | 199 |
| Average Uptime | 98.48% |
| Total Faults | 1,985 |
| Average Traffic | 201.53 |

### Critical Insights
- West region shows lowest average uptime
- 3G technology contributes highest downtime
- Total 1,985 faults recorded across 30 days
- Daily uptime varies with some days below 97%
- Statistical analysis confirms significant regional variance

## Business Recommendations

### Immediate (0-30 days)
- Focus on West region for immediate intervention
- Address 3G technology - highest downtime contribution
- Review sites with Downtime > 60 mins for emergency maintenance

### Short-term (30-90 days)
- Implement predictive maintenance for high-downtime technologies
- Review traffic engineering for overloaded sites
- Seasonal preparedness for monsoon months

### Medium-term (90-180 days)
- Technology refresh plan for legacy 3G towers
- Deploy redundant backhaul for critical towers
- Real-time KPI monitoring dashboard

### Expected Impact
- Uptime improvement: +0.5% → saves ~432 mins downtime/month
- SLA compliance: from current levels to >95% compliant sites
- OPEX savings: ₹1-2Cr/year from reduced truck rolls

## Limitations

- Dataset covers only 30 days; longer history would reveal seasonal patterns
- 199 sites is a small subset; full operator portfolio may have thousands
- Missing vendor-level granularity in network performance data
- No customer impact data (e.g., affected subscribers per fault)

## Next Steps

- Integrate with tower master data for vendor analysis
- Add more recent/public telecom datasets (TRAI, Ookla, etc.)
- Build predictive model for fault forecasting
- Deploy on Streamlit Community Cloud
- Create Power BI dashboard version
