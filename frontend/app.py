import os
import sys

# Ensure project root is on the path regardless of where streamlit is invoked from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from copilot.planner import EnergyCopilot
from scheduler.energy_data import load_or_generate

st.set_page_config(
    page_title="Energy Copilot",
    page_icon="⚡",
    layout="wide",
)

# --- Session state ---
if "copilot" not in st.session_state:
    st.session_state.copilot = EnergyCopilot()
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Sidebar: 24-hour energy forecast ---
def render_forecast_chart():
    df = load_or_generate()
    now = datetime.now()

    # Show the next 24 hours; fall back to first day of data if nothing matches
    window_df = df[
        (df["timestamp"] >= pd.Timestamp(now))
        & (df["timestamp"] <= pd.Timestamp(now + timedelta(hours=24)))
    ].copy()

    if window_df.empty:
        window_df = df[
            df["timestamp"].dt.normalize() == df["timestamp"].dt.normalize().iloc[0]
        ].copy()

    fig, ax1 = plt.subplots(figsize=(4, 3))
    ax1.plot(window_df["timestamp"], window_df["price_per_mwh"],
             color="#1f77b4", linewidth=2)
    ax1.set_ylabel("Price ($/MWh)", color="#1f77b4", fontsize=8)
    ax1.tick_params(axis="y", labelcolor="#1f77b4", labelsize=7)

    ax2 = ax1.twinx()
    ax2.plot(window_df["timestamp"], window_df["carbon_intensity"],
             color="#d62728", linestyle="--", linewidth=1.5, alpha=0.7)
    ax2.set_ylabel("Carbon (g CO₂/kWh)", color="#d62728", fontsize=8)
    ax2.tick_params(axis="y", labelcolor="#d62728", labelsize=7)

    if not window_df.empty and window_df["timestamp"].iloc[0] <= pd.Timestamp(now):
        ax1.axvline(pd.Timestamp(now), color="black", linestyle=":", linewidth=1.5,
                    label="Now")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha="right", fontsize=7)
    ax1.set_title("Next 24 hours", fontsize=9)
    fig.tight_layout()
    return fig


with st.sidebar:
    st.header("⚡ Energy Forecast")
    try:
        fig = render_forecast_chart()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.warning(f"Could not load forecast: {e}")

    st.caption("Blue = price  |  Red dashed = carbon intensity")
    st.divider()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.copilot.reset()
        st.session_state.messages = []
        st.rerun()


# --- Main chat area ---
st.title("⚡ Energy-Aware Workload Copilot")
st.caption("Describe a compute job and I'll find the cheapest, cleanest window to run it.")

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Placeholder shown before any messages
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "Hi! Tell me about a job you need to run — duration and deadline — "
            "and I'll find the optimal energy window for it.\n\n"
            "**Example:** *I need to run a 6-hour model training job before tomorrow at 9am.*"
        )

# Input
if prompt := st.chat_input("e.g. Run a 4-hour training job by tomorrow morning"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing energy forecast..."):
            try:
                response = st.session_state.copilot.chat(prompt)
            except Exception as e:
                response = f"Something went wrong: {e}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
