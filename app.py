import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# Import Custom Modules
from modules.fetch_data import fetch_thingspeak_data, get_latest_reading
from modules.analytics import calculate_moving_average, detect_anomalies_zscore, summarize_analytics
from modules.risk_model import classify_health_risk, get_risk_score
from modules.alerts import trigger_logic

# Premium Medical Indigo UI (Non-White Design)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Professional Layered Gradient Background (No more White) */
    .stApp {
        background: radial-gradient(circle at top right, #1e3a8a 0%, #1e40af 35%, #0f172a 100%) !important;
    }
    
    /* Global Text: High Contrast White/Grey on Dark */
    h1, h2, h3, h4, h5, p, span, label, .stMarkdown {
        color: #F8FAFC !important;
    }

    /* Metric Cards: Glassmorphism Design */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
    }
    
    div[data-testid="stMetricLabel"] > div {
        color: #94A3B8 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 11px !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 40px !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }

    /* Status Banners: Vivid & Glossy */
    .status-card {
        padding: 28px;
        border-radius: 16px;
        text-align: center;
        font-weight: 800;
        font-size: 34px;
        margin: 25px 0;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5);
    }
    .status-normal { background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important; }
    .status-warning { background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%) !important; }
    .status-critical { background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%) !important; animation: glow 2s infinite alternate; }

    @keyframes glow {
        from { box-shadow: 0 0 10px #EF4444; }
        to { box-shadow: 0 0 30px #EF4444; }
    }

    /* Sidebar: Extra Dark Contrast */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] * {
        color: #CBD5E1 !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Configuration & Secrets
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
st.sidebar.title("⚕️ VoceHealth Admin")

# Use secrets for credentials (Production way)
try:
    CHANNEL_ID = st.secrets["THINGSPEAK_CHANNEL_ID"]
    READ_KEY = st.secrets["THINGSPEAK_READ_KEY"]
    TWILIO_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_FROM = st.secrets["TWILIO_FROM_NUMBER"]
    TO_NUMBER = st.secrets["TWILIO_TO_NUMBER"]
    
    # Check if we are using placeholders
    if "YOUR_ID" in str(CHANNEL_ID):
        raise ValueError("Placeholders detected")

except Exception:
    st.sidebar.warning("⚠️ Local secrets not found. Please check .streamlit/secrets.toml.")
    CHANNEL_ID = "" 
    READ_KEY = ""
    TWILIO_SID = ""
    TWILIO_TOKEN = ""
    TWILIO_FROM = ""
    TO_NUMBER = ""

refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 30)

# Main Branding Header
st.markdown("<div style='text-align: center; padding: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    st.markdown(f"<h1 style='color: #FFFFFF; font-weight: 800; font-size: 52px; text-align: center; margin-bottom: 0; text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);'>VocePulse Medical</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #94A3B8; font-size: 20px; text-align: center; font-weight: 600; letter-spacing: 2px;'>ADVANCED BIOMETRIC TELEMETRY • {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Data Acquisition
df = fetch_thingspeak_data(CHANNEL_ID, READ_KEY, results=100)

if not df.empty:
    latest_data = get_latest_reading(df)
    
    # AI Risk Calculation
    status, color_class, reasons, current_gesture = classify_health_risk(latest_data)
    risk_score = get_risk_score(latest_data)
    
    # Alert Execution Logic
    if status == "Critical":
        alert_success, alert_info = trigger_logic(status, reasons, TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TO_NUMBER)
        if alert_success:
            st.success(f"✅ CRITICAL ALERT DISPATCHED: WhatsApp ID {alert_info[:10]}...")
        else:
            st.error(f"⚠️ ALERT DELIVERY FAILED: {alert_info}")
            if "join" in str(alert_info).lower():
                st.warning("👉 **Action Required**: Please send 'join [your-sandbox-keyword]' to your Twilio WhatsApp number from your phone.")

    # Status Banner
    st.markdown(f'<div class="status-card status-{color_class.lower()}">{status.upper()} CLINICAL STATUS</div>', unsafe_allow_html=True)

    # Sidebar Diagnostics
    with st.sidebar:
        st.divider()
        st.subheader("📡 System Diagnostics")
        if st.button("🔄 Test WhatsApp Connection"):
            t_success, t_info = trigger_logic("Critical", ["MANUAL SYSTEM DIAGNOSTIC TEST"], TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TO_NUMBER)
            if t_success:
                st.sidebar.success("Test Dispatched!")
            else:
                st.sidebar.error(f"Test Failed: {t_info}")

    # Vital Metrics Grid
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    mcol1.metric("HEART RATE", f"{latest_data['BPM']} BPM")
    mcol2.metric("ROOM TEMP", f"{latest_data['Room_Temperature']}°C")
    mcol3.metric("GESTURE CMD", f"{current_gesture}")
    mcol4.metric("RISK INDEX", f"{risk_score}/100")
    
    if status != "Normal":
        with st.expander("� Clinical Case Observations", expanded=True):
            st.markdown(f"<h3 style='color:white'>Patient Command: {current_gesture}</h3>", unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f"<p style='color:#CBD5E1'>• {r}</p>", unsafe_allow_html=True)

    # Visualizations
    st.subheader("📊 Physiological Activity Streams")
    
    # Motion and Pulse Chart
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.15,
                        subplot_titles=("Cardiovascular Pulse (BPM)", "Kinetic Activity (Three-Axis)"))

    # Heart Rate
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['BPM'], name="Pulse", line=dict(color='#60A5FA', width=3)), row=1, col=1)
    
    # Motion Data
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Accel_X'], name="X-Axis", line=dict(color='#F87171', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Accel_Y'], name="Y-Axis", line=dict(color='#818CF8', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Timestamp'], y=df['Accel_Z'], name="Z-Axis", line=dict(color='#34D399', width=2)), row=2, col=1)

    fig.update_layout(
        height=600, 
        showlegend=True, 
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(color="#F8FAFC")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Anomaly Detection Table
    st.subheader("⚠️ Detected Anomalies (Last 100 Readings)")
    anomalies = detect_anomalies_zscore(df, 'BPM')
    if anomalies:
        st.dataframe(df.loc[anomalies, ['Timestamp', 'BPM', 'Room_Temperature']].style.highlight_max(axis=0, color='red'))
    else:
        st.success("No statistical anomalies detected in current stream.")

    # Data Table
    with st.expander("📋 Raw Data Feed"):
        st.dataframe(df.sort_values(by='Timestamp', ascending=False), use_container_width=True)

else:
    st.error("Waiting for IoT Data Stream... Please check if Hardware is transmitting.")
    st.info("Ensure ThingSpeak Channel ID and API Keys are correct.")

# Auto-refresh logic
time.sleep(refresh_rate)
st.rerun()
