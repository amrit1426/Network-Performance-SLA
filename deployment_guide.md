# Deployment Guide - Telecom Network Performance & SLA

## Local Setup
1. Clone repo
2. `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install deps: `pip install -r requirements.txt`
5. Launch: `streamlit run app.py`
6. Open browser at `http://localhost:8501`

## Streamlit Community Cloud
1. Push repo to GitHub
2. Go to https://streamlit.io/community-cloud
3. Click "New app" → select repo/branch
4. Set main file: `app.py`
5. Click "Deploy"

## Power BI Integration
- Import `data/raw/network_perf_raw.csv`
- Create visuals: uptime trends, downtime by technology, regional comparison
- Add slicers for Region and NetworkType

## Notebook Execution
```bash
jupyter notebook notebooks/network_performance_analysis.ipynb
```
Run all cells sequentially. Requires Python 3.8+.
