import streamlit as st
import pandas as pd
from utils import page_setup, api_get

st.set_page_config(page_title="Observability — NeuraGuard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
page_setup("Observability", "📊")

st.markdown("## 📊 Observability Dashboard")
st.caption("Live request metrics, LLM latency histograms, agent trace timelines, and error monitoring.")

metrics = api_get("/observability/metrics")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Requests", metrics.get("total_requests", 0))
c2.metric("Avg LLM Latency", f"{metrics.get('avg_llm_latency_ms', 0):.0f} ms")
c3.metric("Total Errors", metrics.get("total_errors", 0))
c4.metric("Security Events", metrics.get("security_events", 0))

st.divider()

traces = api_get("/observability/traces")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Agent", "📦 Retrieval", "🧠 LLM", "🛠️ Tools", "⚠️ Errors"
])

def show_trace(data, label):
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True, height=380)
    else:
        st.info(f"No {label} traces recorded yet.")

with tab1: show_trace(traces.get("agents", []), "agent")
with tab2: show_trace(traces.get("retrieval", []), "retrieval")
with tab3: show_trace(traces.get("llm", []), "LLM")
with tab4: show_trace(traces.get("tools", []), "tool")
with tab5:
    errors = traces.get("errors", [])
    if errors:
        st.dataframe(pd.DataFrame(errors), use_container_width=True, height=380)
    else:
        st.success("✅ No errors recorded.")
