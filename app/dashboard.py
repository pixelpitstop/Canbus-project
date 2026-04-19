"""Streamlit dashboard for CANInsight."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import run_analysis
from src.decoder import SIGNAL_COLUMNS, decode_dataframe
from src.insights import generate_insights

st.set_page_config(page_title="CANInsight Dashboard", layout="wide")
st.title("CANInsight: Vehicle Telemetry & Diagnostics Intelligence System")

csv_path = st.sidebar.text_input("CAN CSV path", "data/can_simulated_day1.csv")

try:
    df_input = pd.read_csv(csv_path)
except Exception as exc:
    st.error(f"Failed to load CSV: {exc}")
    st.stop()

decode_from_raw = st.sidebar.checkbox("Decode from raw CAN payload", value=True)

if decode_from_raw and {"timestamp", "can_id", "data_hex"}.issubset(df_input.columns):
    try:
        df = decode_dataframe(df_input)
    except Exception as exc:
        st.error(f"Failed to decode raw CAN payload: {exc}")
        st.stop()
else:
    missing_cols = [col for col in SIGNAL_COLUMNS if col not in df_input.columns]
    if missing_cols:
        st.error(
            "CSV does not include required signal columns. "
            f"Missing: {', '.join(missing_cols)}"
        )
        st.stop()
    df = df_input[SIGNAL_COLUMNS].copy()

st.subheader("Telemetry Overview")
col1, col2 = st.columns(2)
with col1:
    st.line_chart(df.set_index("timestamp")["speed_kph"])
with col2:
    st.line_chart(df.set_index("timestamp")["rpm"])

alerts, metrics = run_analysis(df)
insights = generate_insights(alerts, metrics)

st.subheader("Trip Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Driving Score", f"{metrics.driving_score}/100")
m2.metric("Max Speed", f"{metrics.max_speed_kph:.1f} kph")
m3.metric("Max RPM", f"{metrics.max_rpm:.0f}")
m4.metric("Max Temp", f"{metrics.max_engine_temp_c:.1f} C")

st.subheader("Alerts")
if alerts:
    for alert in alerts[:30]:
        st.warning(f"t={alert.timestamp:.1f}s | {alert.category} | {alert.message}")
else:
    st.success("No alerts in this run.")

st.subheader("Insights")
for line in insights:
    st.markdown(f"- {line}")
