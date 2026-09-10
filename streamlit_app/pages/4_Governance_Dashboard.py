import streamlit as st
import pandas as pd
from utils import page_setup, api_get

st.set_page_config(page_title="Governance Dashboard — NeuraGuard", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
page_setup("Governance Dashboard", "🛡️")

st.markdown("## 🛡️ Governance & Policy Audit")
st.caption("Real-time safety guardrails, PII detection, prompt injection alerts, and policy violation tracking.")

audit_data = api_get("/governance/audit").get("audit_log", [])

if not audit_data:
    st.info("No governance decisions recorded yet. Send some requests via AI Chat to see data here.")
else:
    df = pd.DataFrame(audit_data)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Approved", int((df["decision"] == "APPROVED").sum()) if "decision" in df else 0)
    c2.metric("🚫 Blocked", int((df["decision"] == "BLOCKED").sum()) if "decision" in df else 0)
    c3.metric("⏳ Review Required", int((df["decision"] == "REVIEW_REQUIRED").sum()) if "decision" in df else 0)
    c4.metric("⚠️ Policy Violations", int(df["policy_violation"].sum()) if "policy_violation" in df else 0)

    st.divider()

    col_chart, col_recent = st.columns([2, 3])

    with col_chart:
        st.markdown("#### 📈 Risk Score Distribution")
        if "risk_score" in df:
            st.bar_chart(df["risk_score"], use_container_width=True)

    with col_recent:
        st.markdown("#### 📋 Audit Log (last 50)")
        display_cols = [c for c in ["request_id", "risk_score", "decision", "pii_detected",
                                     "prompt_injection", "reason"] if c in df.columns]
        st.dataframe(df[display_cols].tail(50), use_container_width=True, height=320)
