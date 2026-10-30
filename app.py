import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ─────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Network Intelligence",
    page_icon="📡",
    layout="wide",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS — DARK THEME WITH TEAL ACCENTS
# ─────────────────────────────────────────────────────────

st.markdown("""
<style>
    :root {
        --bg-primary: #0B0F19;
        --bg-secondary: #111827;
        --bg-card: #1F2937;
        --accent: #14B8A6;
        --accent-glow: #0D9488;
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --border: #374151;
        --danger: #EF4444;
        --warning: #F59E0B;
        --success: #10B981;
    }
    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    .stSidebar {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px 20px;
        margin: 0 0 16px 0;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent);
        opacity: 0.7;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 4px;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border);
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-info { background: rgba(20,184,166,0.15); color: #5EEAD4; border: 1px solid rgba(20,184,166,0.3); }
    .badge-warn { background: rgba(245,158,11,0.15); color: #FCD34D; border: 1px solid rgba(245,158,11,0.3); }
    .badge-danger { background: rgba(239,68,68,0.15); color: #FCA5A5; border: 1px solid rgba(239,68,68,0.3); }
    .stDataFrame {
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    .footer-note {
        color: var(--text-secondary);
        font-size: 0.78rem;
        border-top: 1px solid var(--border);
        padding-top: 10px;
        margin-top: 30px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────
# PLOTLY DARK THEME HELPERS
# ─────────────────────────────────────────────────────────

PLOTLY_DARK = dict(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#F3F4F6"),
)

DARK_AXIS = dict(color="#9CA3AF", gridcolor="#374151", zerolinecolor="#374151")


def apply_dark(fig):
    fig.update_xaxes(**DARK_AXIS)
    fig.update_yaxes(**DARK_AXIS)
    fig.update_layout(**PLOTLY_DARK)
    return fig


def benchmark_line(fig, y=99.9, name="99.9% assumed benchmark"):
    fig.add_hline(y=y, line_dash="dash", line_color="#EF4444", line_width=1.4,
                  annotation_text=name, annotation_position="top right",
                  annotation_font=dict(size=9, color="#FCA5A5"))


# ─────────────────────────────────────────────────────────
# DATA LOADING
# Datasets are loaded from GitHub raw URLs (primary and only source).
# ─────────────────────────────────────────────────────────

NETWORK_URL = "https://raw.githubusercontent.com/amrit1426/Network-Performance-SLA/refs/heads/main/data/raw/network_perf_raw.csv"
MASTER_URL = "https://raw.githubusercontent.com/amrit1426/Network-Performance-SLA/refs/heads/main/data/raw/towers_site_master.csv"


@st.cache_data
def load_data():
    net = pd.read_csv(NETWORK_URL)
    tower = pd.read_csv(MASTER_URL)

    st.caption(f"Network data : {net.shape[0]:,} rows x {net.shape[1]} columns  <- remote: {NETWORK_URL}")
    st.caption(f"Tower master : {tower.shape[0]:,} rows x {tower.shape[1]} columns  <- remote: {MASTER_URL}")

    return net, tower


net, tower = load_data()

# Derived columns
UPTIME_BENCHMARK = 99.9
MIN_OBS_PER_SITE = 3
RNG_SEED = 42

net["below_benchmark"] = net["Uptime"] < UPTIME_BENCHMARK
net["Day"] = net["Date"].dt.normalize()

# ─────────────────────────────────────────────────────────
# AGGREGATIONS (reused across sections)
# ─────────────────────────────────────────────────────────

def summarize(frame, by):
    out = frame.groupby(by).agg(
        records=("SiteID", "size"),
        sites=("SiteID", "nunique"),
        days=("Day", "nunique"),
        avg_uptime=("Uptime", "mean"),
        median_uptime=("Uptime", "median"),
        pct_records_below_benchmark=("below_benchmark", "mean"),
        total_downtime=("Downtime", "sum"),
        avg_downtime=("Downtime", "mean"),
        total_faults=("Faults", "sum"),
        faults_per_record=("Faults", "mean"),
        avg_traffic=("Traffic", "mean"),
    )
    out["pct_records_below_benchmark"] *= 100
    out["uptime_gap_pp"] = UPTIME_BENCHMARK - out["avg_uptime"]
    out["records_share_pct"] = 100 * out["records"] / out["records"].sum()
    out["downtime_share_pct"] = 100 * out["total_downtime"] / out["total_downtime"].sum()
    out["faults_share_pct"] = 100 * out["total_faults"] / out["total_faults"].sum()
    return out


overall = summarize(net.assign(Scope="Whole network"), "Scope")
by_region = summarize(net, "Region")
by_tech = summarize(net, "NetworkType")

site_stats = net.groupby("SiteID").agg(
    n_obs=("Date", "size"),
    regions=("Region", lambda s: "/".join(sorted(s.unique()))),
    technologies=("NetworkType", lambda s: "/".join(sorted(s.unique()))),
    avg_uptime=("Uptime", "mean"),
    min_uptime=("Uptime", "min"),
    pct_obs_below_benchmark=("below_benchmark", "mean"),
    total_downtime=("Downtime", "sum"),
    avg_downtime=("Downtime", "mean"),
    total_faults=("Faults", "sum"),
    faults_per_obs=("Faults", "mean"),
)
site_stats["pct_obs_below_benchmark"] *= 100
site_stats["uptime_gap_pp"] = UPTIME_BENCHMARK - site_stats["avg_uptime"]
eligible = site_stats[site_stats["n_obs"] >= MIN_OBS_PER_SITE].copy()
eligible["meets_target_proxy"] = eligible["avg_uptime"] >= UPTIME_BENCHMARK
eligible["priority_score"] = pd.concat([
    (-eligible["avg_uptime"]).rank(pct=True),
    eligible["avg_downtime"].rank(pct=True),
    eligible["faults_per_obs"].rank(pct=True),
], axis=1).mean(axis=1)

daily = net.groupby("Day").agg(
    records=("SiteID", "size"),
    sites=("SiteID", "nunique"),
    avg_uptime=("Uptime", "mean"),
    pct_records_below_benchmark=("below_benchmark", "mean"),
    avg_downtime=("Downtime", "mean"),
    total_downtime=("Downtime", "sum"),
    total_faults=("Faults", "sum"),
    faults_per_record=("Faults", "mean"),
)
daily["pct_records_below_benchmark"] *= 100

# ─────────────────────────────────────────────────────────
# SIDEBAR — NAVIGATION + FILTERS
# ─────────────────────────────────────────────────────────

with st.sidebar.expander("Modules", expanded=True):
    page = st.radio(
        "Select Module",
        [
            "Executive Overview",
            "Regional Performance",
            "Technology Performance",
            "Daily Trends",
            "SiteID-Group Explorer",
            "Data Quality & Limitations",
        ],
        label_visibility="collapsed",
    )

with st.sidebar.expander("Filters", expanded=True):
    date_range = st.date_input(
        "Date range",
        value=(net["Date"].min().date(), net["Date"].max().date()),
        min_value=net["Date"].min().date(),
        max_value=net["Date"].max().date(),
    )
    region_filter = st.selectbox(
        "Region",
        options=["All Regions"] + sorted(net["Region"].unique().tolist()),
    )
    tech_filter = st.selectbox(
        "Network Technology",
        options=["All Technologies"] + sorted(net["NetworkType"].unique().tolist()),
    )
    clear_filters = st.button("Reset filters")
    if clear_filters:
        st.rerun()

# Apply filters
filtered = net.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["Date"] >= start) & (filtered["Date"] <= end)]

if region_filter != "All Regions":
    filtered = filtered[filtered["Region"] == region_filter]

if tech_filter != "All Technologies":
    filtered = filtered[filtered["NetworkType"] == tech_filter]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# Recompute aggregations on filtered data
f_overall = summarize(filtered.assign(Scope="Whole network"), "Scope")
f_by_region = summarize(filtered, "Region")
f_by_tech = summarize(filtered, "NetworkType")
f_site_stats = filtered.groupby("SiteID").agg(
    n_obs=("Date", "size"),
    regions=("Region", lambda s: "/".join(sorted(s.unique()))),
    technologies=("NetworkType", lambda s: "/".join(sorted(s.unique()))),
    avg_uptime=("Uptime", "mean"),
    min_uptime=("Uptime", "min"),
    pct_obs_below_benchmark=("below_benchmark", "mean"),
    total_downtime=("Downtime", "sum"),
    avg_downtime=("Downtime", "mean"),
    total_faults=("Faults", "sum"),
    faults_per_obs=("Faults", "mean"),
)
f_site_stats["pct_obs_below_benchmark"] *= 100
f_site_stats["uptime_gap_pp"] = UPTIME_BENCHMARK - f_site_stats["avg_uptime"]
f_eligible = f_site_stats[f_site_stats["n_obs"] >= MIN_OBS_PER_SITE].copy()
f_eligible["meets_target_proxy"] = f_eligible["avg_uptime"] >= UPTIME_BENCHMARK
if not f_eligible.empty:
    f_eligible["priority_score"] = pd.concat([
        (-f_eligible["avg_uptime"]).rank(pct=True),
        f_eligible["avg_downtime"].rank(pct=True),
        f_eligible["faults_per_obs"].rank(pct=True),
    ], axis=1).mean(axis=1)

f_daily = filtered.groupby("Day").agg(
    records=("SiteID", "size"),
    sites=("SiteID", "nunique"),
    avg_uptime=("Uptime", "mean"),
    pct_records_below_benchmark=("below_benchmark", "mean"),
    avg_downtime=("Downtime", "mean"),
    total_downtime=("Downtime", "sum"),
    total_faults=("Faults", "sum"),
    faults_per_record=("Faults", "mean"),
)
f_daily["pct_records_below_benchmark"] *= 100

ov = f_overall.iloc[0]
n_elig = len(f_eligible)
n_meet = int(f_eligible["meets_target_proxy"].sum()) if not f_eligible.empty else 0
reg_lo = f_by_region["avg_uptime"].idxmin() if not f_by_region.empty else "N/A"
reg_hi = f_by_region["avg_uptime"].idxmax() if not f_by_region.empty else "N/A"
reg_spread = f_by_region["avg_uptime"].max() - f_by_region["avg_uptime"].min() if not f_by_region.empty else 0
t_total = f_by_tech["total_downtime"].idxmax() if not f_by_tech.empty else "N/A"
t_avg = f_by_tech["avg_downtime"].idxmax() if not f_by_tech.empty else "N/A"
t_faults = f_by_tech["total_faults"].idxmax() if not f_by_tech.empty else "N/A"
t_fpr = f_by_tech["faults_per_record"].idxmax() if not f_by_tech.empty else "N/A"
t_lowup = f_by_tech["avg_uptime"].idxmin() if not f_by_tech.empty else "N/A"

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:4px;">
        <span style="font-size:1.6rem; font-weight:700; color:#F3F4F6;">Network Intelligence</span>
        <span class="badge badge-info">Illustrative Dataset</span>
    </div>
    <div style="font-size:0.95rem; color:#9CA3AF; margin-bottom:18px;">
        Network Performance &amp; SLA Analytics &nbsp;|&nbsp; Assumed {UPTIME_BENCHMARK}% uptime benchmark &nbsp;|&nbsp;
        {len(net):,} observations &nbsp;|&nbsp; {net['SiteID'].nunique()} SiteID identifiers
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ─────────────────────────────────────────────────────────
# HELPER — KPI CARD GRID
# ─────────────────────────────────────────────────────────

def kpi_row(values, cols=4):
    columns = st.columns(cols)
    for i, (label, value, unit) in enumerate(values):
        with columns[i]:
            st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{value} <span style="font-size:0.9rem; color:#9CA3AF;">{unit}</span></div>
                    <div class="kpi-label">{label}</div>
                </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PAGE: EXECUTIVE OVERVIEW
# ─────────────────────────────────────────────────────────

if page == "Executive Overview":
    st.markdown('<div class="section-title">Executive Overview</div>', unsafe_allow_html=True)

    kpi_row([
        ("Avg Uptime", f"{ov['avg_uptime']:.2f}", "%"),
        ("Total Downtime", f"{ov['total_downtime']:,.0f}", "min"),
        ("Total Faults", f"{int(ov['total_faults']):,}", "count"),
        ("Records Below Benchmark", f"{ov['pct_records_below_benchmark']:.1f}", "%"),
    ])

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Record Coverage by Technology</div>', unsafe_allow_html=True)
        tech_summary = f_by_tech[["records", "sites", "days", "records_share_pct"]].reset_index()
        fig = px.bar(
            tech_summary, x="NetworkType", y="records",
            color="NetworkType",
            color_discrete_sequence=["#14B8A6", "#0EA5E9", "#6366F1"],
            text="records",
            labels={"records": "Observation count", "NetworkType": "Technology"},
            height=320,
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    with col_b:
        st.markdown('<div class="section-title">Regional Uptime vs Benchmark</div>', unsafe_allow_html=True)
        reg = f_by_region[["avg_uptime", "pct_records_below_benchmark"]].reset_index()
        fig = px.bar(
            reg, x="Region", y="avg_uptime",
            color="avg_uptime",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            range_color=[97.5, 99.0],
            labels={"avg_uptime": "Avg Uptime (%)", "Region": "Region"},
            height=320,
        )
        benchmark_line(fig)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    st.markdown(
        f"""
        <div class="footer-note">
        Mean uptime is <strong>{ov['avg_uptime']:.2f}%</strong> ({ov['uptime_gap_pp']:.2f} pp below the {UPTIME_BENCHMARK}% assumed benchmark).
        {ov['pct_records_below_benchmark']:.1f}% of records are below benchmark. 
        {n_elig} of {len(f_site_stats)} SiteID groups are eligible for ranking (≥{MIN_OBS_PER_SITE} observations).
        These are analytical proxies, not contractual SLA compliance.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────
# PAGE: REGIONAL PERFORMANCE
# ─────────────────────────────────────────────────────────

elif page == "Regional Performance":
    st.markdown('<div class="section-title">Regional Performance Against Assumed Benchmark</div>', unsafe_allow_html=True)

    reg_table = f_by_region[
        ["records", "sites", "days", "avg_uptime", "uptime_gap_pp",
         "pct_records_below_benchmark", "total_downtime", "avg_downtime",
         "total_faults", "faults_per_record"]
    ].round(2).reset_index()

    st.dataframe(
        reg_table,
        column_config={
            "Region": st.column_config.TextColumn("Region"),
            "avg_uptime": st.column_config.NumberColumn("Avg Uptime (%)", format="%.2f"),
            "uptime_gap_pp": st.column_config.NumberColumn("Gap to Target (pp)", format="%.2f"),
            "pct_records_below_benchmark": st.column_config.NumberColumn("Records Below Benchmark (%)", format="%.1f"),
            "total_downtime": st.column_config.NumberColumn("Total Downtime (min)", format="%.1f"),
            "avg_downtime": st.column_config.NumberColumn("Avg Downtime/Record (min)", format="%.2f"),
            "total_faults": st.column_config.NumberColumn("Total Faults", format="%.0f"),
            "faults_per_record": st.column_config.NumberColumn("Faults/Record", format="%.2f"),
        },
        hide_index=True,
        width="stretch",
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            reg_table.sort_values("avg_uptime"),
            x="avg_uptime", y="Region", orientation="h",
            color="avg_uptime",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            range_color=[97.5, 99.0],
            text="avg_uptime",
            labels={"avg_uptime": "Average Uptime (%)", "Region": "Region"},
            height=340,
        )
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
        benchmark_line(fig)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            reg_table.sort_values("pct_records_below_benchmark", ascending=False),
            x="pct_records_below_benchmark", y="Region", orientation="h",
            color="pct_records_below_benchmark",
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
            text="pct_records_below_benchmark",
            labels={"pct_records_below_benchmark": "Records Below Benchmark (%)", "Region": "Region"},
            height=340,
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    st.markdown(
        f"""
        <div class="footer-note">
        Lowest average uptime: <strong>{reg_lo}</strong> ({f_by_region.loc[reg_lo, 'avg_uptime']:.2f}%).
        Highest: <strong>{reg_hi}</strong> ({f_by_region.loc[reg_hi, 'avg_uptime']:.2f}%).
        Spread: {reg_spread:.2f} pp. Regional comparisons are exploratory only; small effect sizes and non-significant Holm-adjusted p-values mean differences are not reliably detectable.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────
# PAGE: TECHNOLOGY PERFORMANCE
# ─────────────────────────────────────────────────────────

elif page == "Technology Performance":
    st.markdown('<div class="section-title">Technology Performance Comparison</div>', unsafe_allow_html=True)

    tech_table = f_by_tech[
        ["records", "sites", "days", "records_share_pct", "downtime_share_pct",
         "avg_uptime", "uptime_gap_pp", "pct_records_below_benchmark",
         "avg_downtime", "faults_per_record", "avg_traffic"]
    ].round(2).reset_index()

    st.dataframe(
        tech_table,
        column_config={
            "NetworkType": st.column_config.TextColumn("Technology"),
            "avg_uptime": st.column_config.NumberColumn("Avg Uptime (%)", format="%.2f"),
            "uptime_gap_pp": st.column_config.NumberColumn("Gap to Target (pp)", format="%.2f"),
            "pct_records_below_benchmark": st.column_config.NumberColumn("Records Below Benchmark (%)", format="%.1f"),
            "total_downtime": st.column_config.NumberColumn("Total Downtime (min)", format="%.1f"),
            "avg_downtime": st.column_config.NumberColumn("Avg Downtime/Record (min)", format="%.2f"),
            "total_faults": st.column_config.NumberColumn("Total Faults", format="%.0f"),
            "faults_per_record": st.column_config.NumberColumn("Faults/Record", format="%.2f"),
        },
        hide_index=True,
        width="stretch",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.bar(
            tech_table.sort_values("avg_uptime"),
            x="avg_uptime", y="NetworkType", orientation="h",
            color="NetworkType",
            color_discrete_sequence=["#14B8A6", "#0EA5E9", "#6366F1"],
            text="avg_uptime",
            labels={"avg_uptime": "Avg Uptime (%)", "NetworkType": "Technology"},
            height=280,
        )
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
        benchmark_line(fig)
        fig.update_layout(showlegend=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            tech_table.sort_values("avg_downtime"),
            x="avg_downtime", y="NetworkType", orientation="h",
            color="avg_downtime",
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
            text="avg_downtime",
            labels={"avg_downtime": "Avg Downtime/Record (min)", "NetworkType": "Technology"},
            height=280,
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    with col3:
        fig = px.bar(
            tech_table.sort_values("faults_per_record"),
            x="faults_per_record", y="NetworkType", orientation="h",
            color="faults_per_record",
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
            text="faults_per_record",
            labels={"faults_per_record": "Faults/Record", "NetworkType": "Technology"},
            height=280,
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

    st.markdown(
        f"""
        <div class="footer-note">
        Record coverage and totals by technology: {t_total} has the highest total downtime ({f_by_tech.loc[t_total, 'total_downtime']:,.0f} min) with 
        {f_by_tech.loc[t_total, 'records_share_pct']:.1f}% of records and {f_by_tech.loc[t_total, 'downtime_share_pct']:.1f}% of downtime.
        {t_avg} has the highest average downtime per record ({f_by_tech.loc[t_avg, 'avg_downtime']:.2f} min), and {t_lowup} the lowest average uptime ({f_by_tech.loc[t_lowup, 'avg_uptime']:.2f}%).
        Leaders differ by metric; differences are observational associations, not evidence of inherent technology superiority.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────
# PAGE: DAILY TRENDS
# ─────────────────────────────────────────────────────────

elif page == "Daily Trends":
    st.markdown('<div class="section-title">Daily Performance Trends</div>', unsafe_allow_html=True)

    if not f_daily.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=f_daily.index, y=f_daily["avg_uptime"],
            mode="lines+markers", name="Daily avg uptime",
            line=dict(color="#14B8A6", width=2),
            marker=dict(size=5),
        ))
        fig.add_hline(y=UPTIME_BENCHMARK, line_dash="dash", line_color="#EF4444",
                      annotation_text=f"{UPTIME_BENCHMARK}% benchmark",
                      annotation_font=dict(size=9, color="#FCA5A5"))
        if not f_daily.empty:
            fig.add_hline(y=f_daily["avg_uptime"].mean(), line_dash="dot", line_color="#9CA3AF",
                          annotation_text=f"Period avg {f_daily['avg_uptime'].mean():.2f}%",
                          annotation_font=dict(size=9, color="#9CA3AF"))
        fig.update_layout(
            title="Daily Average Uptime",
            xaxis_title="Date",
            yaxis_title="Average Uptime (%)",
            height=320,
            **PLOTLY_DARK,
        )
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=f_daily.index, y=f_daily["avg_downtime"],
            mode="lines+markers", name="Daily avg downtime",
            line=dict(color="#F59E0B", width=2),
            marker=dict(size=5),
        ))
        fig2.update_layout(
            title="Daily Average Downtime per Record",
            xaxis_title="Date",
            yaxis_title="Minutes per Record",
            height=280,
            **PLOTLY_DARK,
        )
        apply_dark(fig2)
        st.plotly_chart(fig2, width="stretch")

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=f_daily.index, y=f_daily["records"],
            marker_color="#0EA5E9",
            name="Records",
        ))
        fig3.update_layout(
            title="Record Coverage per Day",
            xaxis_title="Date",
            yaxis_title="Number of Records",
            height=240,
            **PLOTLY_DARK,
        )
        apply_dark(fig3)
        st.plotly_chart(fig3, width="stretch")

        worst_day = f_daily["avg_uptime"].idxmin()
        best_day = f_daily["avg_uptime"].idxmax()
        st.markdown(
            f"""
            <div class="footer-note">
            Daily average uptime ranges from <strong>{f_daily['avg_uptime'].min():.2f}%</strong> ({worst_day.strftime('%d %b')}, 
            n={int(f_daily.loc[worst_day, 'records'])}) to <strong>{f_daily['avg_uptime'].max():.2f}%</strong> ({best_day.strftime('%d %b')}, 
            n={int(f_daily.loc[best_day, 'records'])}). 
            Daily variation is descriptive only; differences in record counts, SiteID composition and unresolved observation dependencies 
            prevent reliable separation of operational changes from sampling variation.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No daily data available for selected filters.")

# ─────────────────────────────────────────────────────────
# PAGE: SITEID-GROUP EXPLORER
# ─────────────────────────────────────────────────────────

elif page == "SiteID-Group Explorer":
    st.markdown('<div class="section-title">SiteID-Group Explorer</div>', unsafe_allow_html=True)

    if f_eligible.empty:
        st.info("No SiteID groups meet the minimum observation threshold for the selected filters.")
    else:
        kpi_row([
            ("Eligible SiteID Groups", f"{n_elig}", ""),
            ("Above Benchmark", f"{n_meet}", ""),
            ("Below Benchmark", f"{n_elig - n_meet}", ""),
            ("Median Gap", f"{f_eligible['uptime_gap_pp'].median():.2f}", "pp"),
        ])

        top_n = st.slider("Number of SiteID groups to display", 5, min(50, len(f_eligible)), 15)
        top = f_eligible.sort_values("priority_score", ascending=False).head(top_n)

        show_cols = [
            "n_obs", "regions", "technologies", "avg_uptime", "uptime_gap_pp",
            "pct_obs_below_benchmark", "avg_downtime", "total_downtime",
            "total_faults", "faults_per_obs", "priority_score",
        ]
        display_df = top[show_cols].round(2).reset_index()
        display_df.columns = [
            "SiteID", "Observations", "Regions", "Technologies", "Avg Uptime (%)",
            "Gap (pp)", "Records Below Benchmark (%)", "Avg Downtime (min)",
            "Total Downtime (min)", "Total Faults", "Faults/Obs", "Priority Score",
        ]

        st.dataframe(
            display_df,
            column_config={
                "Priority Score": st.column_config.ProgressColumn(
                    "Priority Score (Exploratory)",
                    help="Analyst-defined heuristic score: mean percentile rank of low uptime, high downtime, and high faults per observation.",
                    format="%.2f",
                    min_value=0,
                    max_value=1.0,
                ),
            },
            hide_index=True,
            width="stretch",
        )

        fig = px.bar(
            display_df.sort_values("avg_uptime"),
            x="avg_uptime", y="SiteID", orientation="h",
            color="avg_uptime",
            color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            range_color=[f_eligible["avg_uptime"].min() - 0.1, UPTIME_BENCHMARK],
            text="avg_uptime",
            labels={"avg_uptime": "Average Uptime (%)", "SiteID": "SiteID Group"},
            height=420,
        )
        fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
        benchmark_line(fig)
        fig.update_layout(coloraxis_showscale=False, **PLOTLY_DARK)
        apply_dark(fig)
        st.plotly_chart(fig, width="stretch")

        st.markdown(
            """
            <div class="footer-note">
            Priority score is an analyst-defined exploratory heuristic. It does not establish that these SiteID groups are confirmed 
            problem towers. SiteID identifiers have not been verified as stable physical-tower keys. A useful next step is to 
            cross-check with alarm, ticket and maintenance history for the same period.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────
# PAGE: DATA QUALITY & LIMITATIONS
# ─────────────────────────────────────────────────────────

elif page == "Data Quality & Limitations":
    st.markdown('<div class="section-title">Data Quality & Limitations</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Dataset Overview")
        dq_rows = [
            ("Network observations", f"{len(net):,}"),
            ("Columns", f"{net.shape[1]}"),
            ("Distinct SiteID identifiers", f"{net['SiteID'].nunique()}"),
            ("Regions", f"{net['Region'].nunique()}"),
            ("Network technologies", f"{net['NetworkType'].nunique()}"),
            ("Distinct dates", f"{net['Date'].nunique()}"),
            ("Date range", f"{net['Date'].min().strftime('%d %b %Y')} – {net['Date'].max().strftime('%d %b %Y')}"),
            ("Missing values", f"{int(net[['SiteID','Region','NetworkType','Uptime','Downtime','Faults','Traffic','Date']].isna().sum().sum()):,}"),
            ("Exact duplicate rows", f"{int(net.duplicated().sum()):,}"),
        ]
        for label, value in dq_rows:
            st.markdown(f"- **{label}:** {value}")

    with col2:
        st.markdown("#### Key Data Quality Flags")
        flag_rows = [
            ("SiteID+Date duplicates", f"{int(net.duplicated(['SiteID','Date'], keep=False).sum()):,} rows share a SiteID+Date combination"),
            ("Cross-region SiteIDs", f"{int((net.groupby('SiteID')['Region'].nunique() > 1).sum())} of {net['SiteID'].nunique()} SiteID identifiers appear in >1 region"),
            ("Cross-technology SiteIDs", f"{int((net.groupby('SiteID')['NetworkType'].nunique() > 1).sum())} of {net['SiteID'].nunique()} SiteID identifiers appear in >1 technology"),
            ("Uptime–Downtime correlation", f"{net['Uptime'].corr(net['Downtime'], method='pearson'):.3f} (weak)"),
            ("Tower master overlap", "0% — zero matching identifiers between network data and tower master"),
        ]
        for label, value in flag_rows:
            if "0%" in value or "weak" in value:
                badge = '<span class="badge badge-warn">Review</span>'
            else:
                badge = '<span class="badge badge-info">Info</span>'
            st.markdown(f"- **{label}** {badge}  \n  {value}")

    st.markdown("#### Important Limitations")
    st.markdown(
        """
        - **No confirmed contractual SLA:** The 99.9% uptime figure is an assumed analytical benchmark, not a verified contractual SLA.
        - **SiteID identity unresolved:** SiteID identifiers appear across multiple regions and technologies; 146 rows share a SiteID+Date combination.
          These identifiers have not been established as unique physical tower identifiers.
        - **Undocumented measurement window:** The duration behind each record is undocumented; uptime and downtime are analysed separately.
        - **No causal fields:** No fault categories, maintenance records, power status, backhaul type, vendor or cost fields are available.
        - **Tower master excluded:** The tower master (`towers_site_master.csv`) cannot be joined because its identifiers (`EC-001`, `GP-001`, etc.) 
          do not match the network dataset's SiteID identifiers (`T001`–`T199`). No valid mapping exists.
        - **Short observation window:** Approximately one month of data cannot establish seasonality, trends or recurring weekly patterns.
        - **Sparse observations:** Most SiteID groups have few observations; site-level averages are noisy and rankings are unstable.
        """
    )

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="footer-note">
    Network Intelligence — Network Performance &amp; SLA Analytics &nbsp;|&nbsp; 
    Illustrative historical dataset &nbsp;|&nbsp; 
    Not connected to a live network &nbsp;|&nbsp; 
    <a href="https://github.com/amrit1426/Network-Performance-SLA" target="_blank" style="color:#14B8A6;">GitHub Repository</a>
    </div>
    """,
    unsafe_allow_html=True,
)
