import streamlit as st
import pandas as pd

from simulation import find_optimal
from data import get_current_state

st.set_page_config(layout="wide")

st.title("VPN Capacity Optimization")

state = get_current_state()

# Sidebar
st.sidebar.header("Scenario Controls")

sla = st.sidebar.slider("SLA Target", 0.95, 0.9999, 0.10)

load_multiplier = st.sidebar.slider(
    "Traffic Scenario Multiplier",
    0.8, 2.0, 1.0
)

cost_per_server = st.sidebar.number_input(
    "Cost per server €/day",
    1.0, 30.0, 5.0
)

st.subheader("Live System State")
st.json(state)

if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        optimal, results = find_optimal(state, sla, load_multiplier)

    df = pd.DataFrame(results)

    st.subheader("Results")

    current = state["current_servers"]

    if optimal:
        optimal_servers = optimal["servers"]
        reduction = current - optimal_servers
        savings = reduction * cost_per_server

        st.success(f"Optimal servers: {optimal_servers}")

        st.write(f"SLA target: {sla*100:.2f}%")
        st.write(f"Violation rate: {optimal['violation']:.2%}")

        st.write(
            f"Confidence interval: "
            f"{optimal['ci_low']:.2%} – {optimal['ci_high']:.2%}"
        )

        st.metric("Current servers", current)
        st.metric("Optimal servers", optimal_servers)
        st.metric("Reduction", reduction)
        st.metric("Daily savings (€)", int(savings))

    else:
        st.error("No configuration meets SLA")

    st.subheader("Risk vs Servers")

    chart_df = df.set_index("servers")[["violation"]]

    st.line_chart(chart_df)
