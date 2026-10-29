"""Telecom Network Performance & SLA - Streamlit Portfolio App"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Network Performance & SLA", layout="wide")

@st.cache_data
def load_data():
    df_network = pd.read_csv('data/raw/network_perf_raw.csv')
    df_towers = pd.read_csv('data/raw/towers_site_master.csv')
    return df_network, df_towers

df_network, df_towers = load_data()

st.title("📡 Telecom Network Performance & SLA Analytics")
st.markdown("### Network Performance SLA | Data Analyst Transition")
st.markdown("Real network performance data | 1,000 records | 5 regions | 3G/4G/5G technologies")

# Sidebar filters
st.sidebar.header("Filters")
region_filter = st.sidebar.multiselect("Region", df_network['Region'].unique(), default=df_network['Region'].unique())
tech_filter = st.sidebar.multiselect("Technology", df_network['NetworkType'].unique(), default=df_network['NetworkType'].unique())

filtered = df_network[df_network['Region'].isin(region_filter) & df_network['NetworkType'].isin(tech_filter)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Uptime", f"{filtered['Uptime'].mean():.2f}%")
with col2:
    st.metric("Total Faults", f"{filtered['Faults'].sum():,}")
with col3:
    st.metric("Avg Downtime", f"{filtered['Downtime'].mean():.1f} mins")
with col4:
    st.metric("Avg Traffic", f"{filtered['Traffic'].mean():.1f}")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Uptime by Region")
    region_uptime = filtered.groupby('Region')['Uptime'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    region_uptime.plot(kind='barh', ax=ax, color='steelblue')
    ax.axvline(x=99.9, color='red', linestyle='--')
    ax.set_title('Average Uptime % by Region')
    ax.set_xlabel('Uptime %')
    st.pyplot(fig)
    plt.close()

with col2:
    st.subheader("Downtime by Technology")
    tech_downtime = filtered.groupby('NetworkType')['Downtime'].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    tech_downtime.plot(kind='bar', ax=ax, color='coral')
    ax.set_title('Total Downtime by Technology')
    ax.set_ylabel('Downtime mins')
    st.pyplot(fig)
    plt.close()

# Recommendations
st.subheader("💡 Business Recommendations")
st.markdown("""
1. **Immediate:** Focus on worst-performing regions and technologies
2. **Short-term:** Implement predictive maintenance for high-downtime sites
3. **Medium-term:** Technology refresh and redundant backhaul planning
4. **Expected Impact:** Uptime +0.5%, OPEX savings ₹1-2Cr/year
""")
