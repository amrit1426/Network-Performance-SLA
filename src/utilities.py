"""Utility functions for Telecom Network Performance analysis."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

plt.style.use('seaborn-v0_8-whitegrid')

def load_data(network_path='data/raw/network_perf_raw.csv', tower_path='data/raw/towers_site_master.csv'):
    df_network = pd.read_csv(network_path)
    df_towers = pd.read_csv(tower_path)
    return df_network, df_towers

def kpi_summary(df):
    return {
        'avg_uptime': df['Uptime'].mean(),
        'avg_downtime': df['Downtime'].mean(),
        'total_faults': df['Faults'].sum(),
        'avg_traffic': df['Traffic'].mean(),
        'max_downtime': df['Downtime'].max()
    }

def regional_performance(df):
    return df.groupby('Region').agg({
        'Uptime': 'mean',
        'Downtime': 'sum',
        'Faults': 'sum',
        'Traffic': 'mean'
    }).round(2)

def technology_performance(df):
    return df.groupby('NetworkType').agg({
        'Uptime': 'mean',
        'Downtime': 'sum',
        'Faults': 'sum',
        'Traffic': 'mean'
    }).round(2)

def statistical_tests(df):
    # ANOVA: uptime across regions
    region_groups = [group['Uptime'].values for name, group in df.groupby('Region')]
    f_stat, p_value = stats.f_oneway(*region_groups)
    
    # ANOVA: downtime across technologies
    tech_groups = [group['Downtime'].values for name, group in df.groupby('NetworkType')]
    f_stat2, p_value2 = stats.f_oneway(*tech_groups)
    
    return {
        'uptime_region_f': f_stat,
        'uptime_region_p': p_value,
        'downtime_tech_f': f_stat2,
        'downtime_tech_p': p_value2
    }
