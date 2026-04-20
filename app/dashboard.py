"""Streamlit dashboard for CANInsight."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.analysis import run_analysis
from src.decoder import SIGNAL_COLUMNS, decode_dataframe
from src.insights import generate_insight_report, generate_insights

st.set_page_config(page_title="CANInsight Dashboard", page_icon="🚗", layout="wide")

st.markdown(
    """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 176, 102, 0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(56, 138, 255, 0.12), transparent 22%),
            linear-gradient(180deg, #08111f 0%, #0d1728 55%, #111827 100%);
        color: #e5eefc;
    }
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.6rem;
    }
    h1, h2, h3, h4, p, span, label {
        color: #e5eefc !important;
    }
    [data-testid="stSidebar"] {
        background: #0b1322;
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }
    .hero-card {
        padding: 1.5rem 1.6rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.86));
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 18px 60px rgba(0, 0, 0, 0.22);
    }
    .hero-kicker {
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #8fb7ff;
        font-size: 0.74rem;
        margin-bottom: 0.3rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.05;
        margin-bottom: 0.35rem;
        color: #f8fbff;
    }
    .hero-subtitle {
        color: #b6c4da;
        font-size: 0.98rem;
        max-width: 54rem;
    }
    .metric-card {
        padding: 1.1rem 1rem 1rem 1rem;
        border-radius: 1rem;
        background: rgba(15, 23, 42, 0.86);
        border: 1px solid rgba(148, 163, 184, 0.18);
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);
        height: 100%;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }
    .metric-value {
        color: #f8fbff;
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 0.15rem;
    }
    .metric-note {
        color: #b6c4da;
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
    .section-shell {
        padding: 1.1rem 1.15rem 1rem 1.15rem;
        margin-top: 0.9rem;
        margin-bottom: 0.9rem;
        border-radius: 1rem;
        background: rgba(15, 23, 42, 0.74);
        border: 1px solid rgba(148, 163, 184, 0.16);
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.14);
    }
    .risk-banner {
        padding: 1rem 1.1rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.88);
        border-left: 8px solid #f59e0b;
        border-top: 1px solid rgba(148, 163, 184, 0.16);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
        border-bottom: 1px solid rgba(148, 163, 184, 0.16);
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
    }
    .insight-list li {
        margin-bottom: 0.7rem;
        line-height: 1.6;
    }
    .section-gap {
        height: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class='hero-card'>
  <div class='hero-kicker'>Automotive Diagnostics Intelligence</div>
  <div class='hero-title'>CANInsight</div>
  <div class='hero-subtitle'>
    Simulated CAN telemetry, decoded into engineering signals, analyzed for trip risk,
    and translated into actionable diagnostics insights.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

csv_path = st.sidebar.text_input("CAN CSV path", "data/can_simulated_day1.csv")
decode_from_raw = st.sidebar.checkbox("Decode from raw CAN payload", value=True)
show_raw_preview = st.sidebar.checkbox("Show decoded sample rows", value=False)

st.sidebar.caption("Load raw CAN logs or pre-decoded telemetry.")

try:
    df_input = pd.read_csv(csv_path)
except Exception as exc:
    st.error(f"Failed to load CSV: {exc}")
    st.stop()

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

alerts, metrics = run_analysis(df)
insights = generate_insights(alerts, metrics)
report = generate_insight_report(alerts, metrics)

st.markdown(
    f"""
<div class='risk-banner'>
  <div style='text-transform:uppercase;letter-spacing:0.14em;color:#fbbf24;font-size:0.72rem;'>Trip Risk</div>
  <div style='font-size:1.2rem;font-weight:700;color:#f8fbff;margin-top:0.2rem;'>{report.risk_level}</div>
  <div style='color:#cbd5e1;margin-top:0.25rem;'>{report.headline}</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

metric_cols = st.columns(4, gap="large")
metric_data = [
    ("Driving Score", f"{metrics.driving_score}/100", "Lower is more severe."),
    ("Max Speed", f"{metrics.max_speed_kph:.1f} kph", "Peak vehicle velocity."),
    ("Max RPM", f"{metrics.max_rpm:.0f}", "Maximum engine speed observed."),
    ("Max Temp", f"{metrics.max_engine_temp_c:.1f} C", "Highest thermal load."),
]

for col, (label, value, note) in zip(metric_cols, metric_data):
    with col:
        st.markdown(
            f"""
<div class='metric-card'>
  <div class='metric-label'>{label}</div>
  <div class='metric-value'>{value}</div>
  <div class='metric-note'>{note}</div>
</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

overview = make_subplots(specs=[[{"secondary_y": True}]])
overview.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["speed_kph"],
        name="Speed (kph)",
        line=dict(color="#38bdf8", width=3),
    ),
    secondary_y=False,
)
overview.add_trace(
    go.Scatter(
        x=df["timestamp"],
        y=df["rpm"],
        name="RPM",
        line=dict(color="#f97316", width=3),
    ),
    secondary_y=True,
)
overview.update_layout(
    height=430,
    margin=dict(l=70, r=85, t=70, b=55),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15, 23, 42, 0.75)",
    legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
    font=dict(color="#e5eefc"),
    title=dict(text="Speed / RPM Overview", x=0.02, y=0.96),
)
overview.update_xaxes(title_text="Time (s)", title_standoff=18, nticks=7, gridcolor="rgba(148, 163, 184, 0.15)")
overview.update_yaxes(
    title_text="Speed (kph)",
    title_standoff=20,
    secondary_y=False,
    automargin=True,
    gridcolor="rgba(148, 163, 184, 0.15)",
)
overview.update_yaxes(
    title_text="RPM",
    title_standoff=18,
    secondary_y=True,
    automargin=True,
)

st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
st.subheader("Telemetry Overview")
st.plotly_chart(overview, use_container_width=True, theme=None)

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

detail_cols = st.columns(2, gap="large")
with detail_cols[0]:
    throttle_temp = go.Figure()
    throttle_temp.add_trace(go.Scatter(x=df["timestamp"], y=df["throttle_pct"], name="Throttle %", line=dict(color="#22c55e", width=2.5)))
    throttle_temp.add_trace(go.Scatter(x=df["timestamp"], y=df["brake_pct"], name="Brake %", line=dict(color="#ef4444", width=2.5)))
    throttle_temp.add_trace(go.Scatter(x=df["timestamp"], y=df["engine_temp_c"], name="Temp C", line=dict(color="#eab308", width=2.5)))
    throttle_temp.update_layout(
        height=330,
        margin=dict(l=68, r=30, t=70, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.75)",
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
        font=dict(color="#e5eefc"),
        title=dict(text="Throttle / Brake / Temperature", x=0.02, y=0.96),
    )
    throttle_temp.update_xaxes(title_text="Time (s)", title_standoff=18, nticks=6, gridcolor="rgba(148, 163, 184, 0.15)")
    throttle_temp.update_yaxes(title_text="Value", title_standoff=20, automargin=True, gridcolor="rgba(148, 163, 184, 0.15)")
    st.plotly_chart(throttle_temp, use_container_width=True, theme=None)

with detail_cols[1]:
    temp_speed = go.Figure()
    temp_speed.add_trace(go.Bar(x=df["timestamp"], y=df["speed_kph"], name="Speed", marker_color="#38bdf8", opacity=0.75))
    temp_speed.add_trace(go.Scatter(x=df["timestamp"], y=df["engine_temp_c"], name="Temp", line=dict(color="#f59e0b", width=2.5)))
    temp_speed.update_layout(
        height=330,
        margin=dict(l=68, r=30, t=70, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.75)",
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
        font=dict(color="#e5eefc"),
        title=dict(text="Speed / Temperature Relationship", x=0.02, y=0.96),
    )
    temp_speed.update_xaxes(title_text="Time (s)", title_standoff=18, nticks=6, gridcolor="rgba(148, 163, 184, 0.15)")
    temp_speed.update_yaxes(title_text="Value", title_standoff=20, automargin=True, gridcolor="rgba(148, 163, 184, 0.15)")
    st.plotly_chart(temp_speed, use_container_width=True, theme=None)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

st.subheader("Alerts")
if alerts:
    alert_rows = []
    for alert in alerts[:30]:
        alert_rows.append(
            {
                "Time (s)": f"{alert.timestamp:.1f}",
                "Severity": alert.severity.title(),
                "Category": alert.category.replace("_", " ").title(),
                "Message": alert.message,
            }
        )
    st.dataframe(pd.DataFrame(alert_rows), use_container_width=True, hide_index=True)
else:
    st.success("No alerts in this run.")

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

st.subheader("Insights")
st.markdown("<ul class='insight-list'>", unsafe_allow_html=True)
for line in insights:
    st.markdown(f"<li>{line}</li>", unsafe_allow_html=True)
st.markdown("</ul>", unsafe_allow_html=True)

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

st.subheader("Priority Findings")
for finding in report.priority_findings:
    st.markdown(f"- {finding}")

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

st.subheader("Recommended Actions")
for rec in report.recommendations:
    st.markdown(f"- {rec}")

if show_raw_preview:
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    st.subheader("Decoded Sample Rows")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
