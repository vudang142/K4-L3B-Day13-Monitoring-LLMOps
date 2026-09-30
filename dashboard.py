"""Simple dashboard to visualize logs from data/logs.jsonl"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

LOG_PATH = Path("data/logs.jsonl")


@st.cache_data
def load_logs():
    records = []
    if LOG_PATH.exists():
        with LOG_PATH.open() as f:
            for line in f:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return pd.DataFrame(records)


st.title("K4-L3B Day 13 Dashboard")

df = load_logs()

if df.empty:
    st.warning("No logs found. Run the API and load_test.py first.")
else:
    # Filter response_sent events
    response_df = df[df["event"] == "response_sent"]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_requests = len(df[df["event"] == "request_received"])
        st.metric("Total Requests", total_requests)

    with col2:
        if "latency_ms" in response_df.columns and len(response_df) > 0:
            p95 = response_df["latency_ms"].quantile(0.95)
            st.metric("Latency P95 (ms)", f"{p95:.0f}")

    with col3:
        errors = len(df[df["event"] == "request_failed"])
        error_rate = (errors / total_requests * 100) if total_requests > 0 else 0
        st.metric("Error Rate (%)", f"{error_rate:.1f}")

    with col4:
        if "cost_usd" in response_df.columns and len(response_df) > 0:
            total_cost = response_df["cost_usd"].sum()
            st.metric("Total Cost (USD)", f"${total_cost:.4f}")

    # Latency chart
    st.subheader("Latency Distribution")
    if "latency_ms" in response_df.columns and len(response_df) > 0:
        p50 = response_df["latency_ms"].quantile(0.50)
        p95 = response_df["latency_ms"].quantile(0.95)
        p99 = response_df["latency_ms"].quantile(0.99)

        latency_data = pd.DataFrame({
            "Percentile": ["P50", "P95", "P99"],
            "Latency (ms)": [p50, p95, p99]
        })
        st.bar_chart(latency_data.set_index("Percentile"))

    # Quality score
    st.subheader("Quality Proxy")
    if "quality_score" in response_df.columns and len(response_df) > 0:
        avg_quality = response_df["quality_score"].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.2f}")

    # Recent logs
    st.subheader("Recent Logs")
    st.dataframe(df.tail(10)[["ts", "event", "correlation_id", "latency_ms"]])
