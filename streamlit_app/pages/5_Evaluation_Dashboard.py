import streamlit as st
from utils import page_setup, api_get, api_post

st.set_page_config(page_title="Evaluation Dashboard — NeuraGuard", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")
page_setup("Evaluation Dashboard", "🧪")

st.markdown("## 🧪 Evaluation Dashboard")
st.caption("Automated benchmarks measuring RAG groundedness, agent quality, and safety policy adherence.")

col_ctrl, col_result = st.columns([1, 3])

data = api_get("/evaluation/results")
runs = data.get("runs", [])

with col_ctrl:
    scope = st.selectbox("Scope", ["full", "rag", "agents", "safety"])
    if st.button("▶️ Run Evaluation"):
        with st.spinner("Running evaluation..."):
            api_post("/evaluation/run", {"scope": scope})
        st.success("Done!")
        st.rerun()
    st.divider()
    st.metric("Total Runs", len(runs))

with col_result:
    if not runs:
        st.info("No evaluation runs yet. Select a scope and click **Run Evaluation**.")
    else:
        latest = runs[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall", f"{latest.get('overall_score', 0):.2f}")
        c2.metric("RAG Groundedness", f"{latest.get('rag', {}).get('groundedness', 0):.2f}")
        c3.metric("Agent Score", f"{latest.get('agents', {}).get('score', 0):.2f}")
        c4.metric("Safety Score", f"{latest.get('safety', {}).get('security_score', 0):.2f}")

        passed = latest.get("passed", False)
        if passed:
            st.success("✅ All evaluation thresholds passed!")
        else:
            st.error("❌ One or more evaluation thresholds failed.")

        with st.expander("📊 Full Evaluation Result"):
            st.json(latest)
