import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from copilot.planner import EnergyCopilot
from scheduler.energy_data import load_or_generate

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Energy Copilot",
    page_icon="⚡",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide Streamlit chrome */
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Push content below the Streamlit top bar */
.block-container { padding-top: 3.5rem !important; }

/* Prompt chip buttons */
[data-testid="stHorizontalBlock"] button {
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #aab !important;
    font-size: 0.78rem !important;
    padding: 0.25rem 0.75rem !important;
    transition: all 0.15s ease;
}
[data-testid="stHorizontalBlock"] button:hover {
    border-color: #00d4aa !important;
    color: #00d4aa !important;
    background: rgba(0, 212, 170, 0.06) !important;
}

/* Metric card styling */
[data-testid="metric-container"] {
    background: #1a1d2e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.6rem 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "copilot" not in st.session_state:
    st.session_state.copilot = EnergyCopilot()
if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Energy data (cached 5 min) ────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_df():
    return load_or_generate()


def get_window(df: pd.DataFrame, hours: int = 24):
    """Return the next `hours` rows; fall back to the first day if data is stale."""
    now = pd.Timestamp(datetime.now())
    window = df[df["timestamp"] >= now].head(hours)
    if window.empty:
        first_day = df["timestamp"].dt.normalize().iloc[0]
        window = df[df["timestamp"].dt.normalize() == first_day]
    return window


def make_forecast_chart(df: pd.DataFrame) -> go.Figure:
    window = get_window(df)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=window["timestamp"], y=window["price_per_mwh"],
        name="Price ($/MWh)", yaxis="y1",
        line=dict(color="#00d4aa", width=2),
        hovertemplate="%{x|%H:%M}  $%{y:.0f}/MWh<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=window["timestamp"], y=window["carbon_intensity"],
        name="Carbon (g CO₂/kWh)", yaxis="y2",
        line=dict(color="#ff6b6b", width=1.5, dash="dot"),
        hovertemplate="%{x|%H:%M}  %{y:.0f} g CO₂/kWh<extra></extra>",
    ))

    # Mark current time if it falls inside the window
    now_ts = pd.Timestamp(datetime.now())
    if window["timestamp"].iloc[0] <= now_ts <= window["timestamp"].iloc[-1]:
        fig.add_vline(x=now_ts, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                      line_width=1.5, annotation_text="now",
                      annotation_font_color="rgba(255,255,255,0.4)",
                      annotation_position="top left")

    fig.update_layout(
        yaxis=dict(title=dict(text="$/MWh", font=dict(color="#00d4aa")),
                   tickfont=dict(color="#00d4aa"), gridcolor="rgba(255,255,255,0.05)"),
        yaxis2=dict(title=dict(text="g CO₂/kWh", font=dict(color="#ff6b6b")),
                    tickfont=dict(color="#ff6b6b"), overlaying="y", side="right",
                    gridcolor="rgba(255,255,255,0)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)",
                   tickformat="%H:%M", tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        margin=dict(l=0, r=0, t=28, b=0),
        height=200,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0"),
        hovermode="x unified",
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Energy Copilot")
    st.divider()

    df = get_df()
    window = get_window(df)

    # Stat cards
    current_price = window["price_per_mwh"].iloc[0]
    cheapest_row = window.loc[window["price_per_mwh"].idxmin()]
    avg_carbon = window["carbon_intensity"].mean()

    c1, c2 = st.columns(2)
    c1.metric("Current price", f"${current_price:.0f}/MWh")
    c2.metric("Cheapest hour", f"${cheapest_row['price_per_mwh']:.0f}/MWh",
              delta=f"{cheapest_row['timestamp'].strftime('%H:%M')}",
              delta_color="off")
    st.metric("Avg carbon (24 hr)", f"{avg_carbon:.0f} g CO₂/kWh")

    st.divider()
    st.caption("Next 24 hours")
    st.plotly_chart(make_forecast_chart(df), width="stretch",
                    config={"displayModeBar": False})

    # Job queue
    jobs = st.session_state.copilot.scheduled_jobs
    if jobs:
        st.divider()
        st.caption(f"Scheduled this session ({len(jobs)} job{'s' if len(jobs) != 1 else ''})")
        st.dataframe(
            [
                {
                    "Job": j["job_name"],
                    "Start": j["recommended_start"][11:16],
                    "End": j["recommended_end"][11:16],
                    "Savings": f"{j['cost_savings_vs_now_pct']:.0f}%",
                }
                for j in jobs
            ],
            width="stretch",
            hide_index=True,
        )

    st.divider()
    if st.button("Clear conversation", width="stretch"):
        st.session_state.copilot.reset()
        st.session_state.messages = []
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex; align-items:center; justify-content:space-between;
            padding-bottom:14px; border-bottom:1px solid rgba(255,255,255,0.08);
            margin-bottom:18px;">
  <div>
    <span style="font-size:1.25rem; font-weight:700; color:#e8eaf0;">
      Energy-Aware Workload Scheduler
    </span><br>
    <span style="font-size:0.78rem; color:#6b7280;">
      Describe a job — get the cheapest, cleanest window to run it
    </span>
  </div>
  <div style="text-align:right; font-size:0.78rem; color:#6b7280;">
    <span style="color:#00d4aa;">●</span>&nbsp;Live&nbsp;&nbsp;
    <span style="color:#e8eaf0;">${current_price:.0f}/MWh</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "Hi! Tell me about a job you need to run and I'll find the optimal energy window.\n\n"
            "**Try one of the examples below, or describe your own job.**"
        )

# ── Prompt chips ──────────────────────────────────────────────────────────────
chip_used = None
if not st.session_state.messages:
    cols = st.columns(3)
    chips = [
        ("2hr ETL by 5pm today",         "I need to run a 2-hour ETL pipeline that has to finish by 5pm today."),
        ("6hr training by 9am tomorrow", "Schedule a 6-hour model training job before 9am tomorrow."),
        ("Cheapest 1hr window tonight",  "What's the cheapest 1-hour window to run a job tonight?"),
    ]
    for col, (label, prompt) in zip(cols, chips):
        if col.button(label, width="stretch"):
            chip_used = prompt


# ── Chat input + response ─────────────────────────────────────────────────────
typed = st.chat_input("e.g. Run a 4-hour training job before tomorrow morning…")
prompt = chip_used or typed

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing energy forecast…"):
            # Collect the generator first so the spinner covers the tool call phase
            chunks = list(st.session_state.copilot.stream_chat(prompt))

        # Then display as a stream for the typing effect
        def _gen():
            yield from chunks

        response = st.write_stream(_gen())

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
