import numpy as np
import pandas as pd
from scipy import stats

def calculate_moving_average(series, window=5):
    """
    Smooths sensor data using a simple moving average.
    """
    return series.rolling(window=window).mean()

def detect_anomalies_zscore(df, column, threshold=3):
    """
    Detects anomalies in a specific column using Z-score methodology.
    Returns indices of anomalies.
    """
    if df.empty or column not in df.columns:
        return []
    
    data = df[column].dropna()
    if len(data) < 2:
        return []
        
    z_scores = np.abs(stats.zscore(data))
    anomalies = data[z_scores > threshold]
    return anomalies.index.tolist()

def analyze_trend_slope(series):
    """
    Calculates the slope of a trend using linear regression.
    A positive slope indicates an increasing trend, negative indicates decreasing.
    """
    if len(series) < 2:
        return 0
    
    y = series.values
    x = np.arange(len(y))
    
    # Filter nan values
    mask = ~np.isnan(y)
    if np.sum(mask) < 2:
        return 0
        
    slope, _, _, _, _ = stats.linregress(x[mask], y[mask])
    return slope

def summarize_analytics(df):
    """
    Calculates summary statistics for the dashboard.
    """
    if df.empty:
        return {}
        
    summary = {
        'avg_bpm': df['BPM'].mean(),
        'max_bpm': df['BPM'].max(),
        'min_bpm': df['BPM'].min(),
        'avg_temp': df['Temperature'].mean(),
        'bpm_trend': analyze_trend_slope(df['BPM'].tail(10))
    }
    return summary
