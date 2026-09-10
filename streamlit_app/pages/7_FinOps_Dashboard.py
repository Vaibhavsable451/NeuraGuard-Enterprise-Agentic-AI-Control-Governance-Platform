import streamlit as st
from utils import page_setup, api_get

st.set_page_config(page_title="FinOps Dashboard — NeuraGuard", page_icon="💰", layout="wide", initial_sidebar_state="expanded")
page_setup("FinOps Dashboard", "💰")

st.markdown("## 💰 FinOps Dashboard")
st.caption("AI token cost tracking, per-agent spend analysis, budget optimization, and anomaly detection.")

cost = api_get("/finops/cost")

c1, c2, c3 = st.columns(3)
c1.metric("Daily Cost", f"${cost.get('daily_cost', 0):.4f}")
c2.metric("Monthly Cost", f"${cost.get('monthly_cost', 0):.4f}")
c3.metric("Cost / Request", f"${cost.get('cost_per_request', 0):.6f}")

st.divider()

col_agent, col_wf = st.columns(2)

with col_agent:
    st.markdown("#### 🤖 Cost by Agent")
    by_agent = cost.get("cost_per_agent", {})
    if by_agent:
        st.bar_chart(by_agent, use_container_width=True)
        for agent, val in sorted(by_agent.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                <span style="color:#cbd5e1;">🤖 {agent}</span>
                <span class="badge badge-amber">${val:.6f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No per-agent cost data yet.")

with col_wf:
    st.markdown("#### 🔄 Cost by Workflow")
    by_wf = cost.get("cost_per_workflow", {})
    if by_wf:
        st.bar_chart(by_wf, use_container_width=True)
        most_exp = max(by_wf, key=by_wf.get)
        st.markdown(f"""
        <div class="glass glass-amber">
            <div style="color:#94a3b8;font-size:0.8rem;">Most Expensive Workflow</div>
            <strong style="color:#fbbf24;">{most_exp}</strong>
            <span style="color:#64748b;margin-left:8px;">${by_wf[most_exp]:.6f}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No workflow cost data yet.")

st.divider()

col_anom, col_rec = st.columns(2)

with col_anom:
    st.markdown("#### ⚠️ Cost Anomalies")
    for a in cost.get("anomalies", []):
        st.markdown(f'<div class="glass glass-red" style="padding:10px 14px;">{a}</div>', unsafe_allow_html=True)
    if not cost.get("anomalies"):
        st.success("No anomalies detected.")

with col_rec:
    st.markdown("#### 💡 Optimization Tips")
    for r in cost.get("recommendations", []):
        st.markdown(f'<div class="glass glass-green" style="padding:10px 14px;">{r}</div>', unsafe_allow_html=True)
    if not cost.get("recommendations"):
        st.info("No recommendations at this time.")
