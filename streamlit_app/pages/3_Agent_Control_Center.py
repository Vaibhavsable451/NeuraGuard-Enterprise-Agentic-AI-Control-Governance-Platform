import streamlit as st
from utils import page_setup, api_get, api_post

st.set_page_config(page_title="Agent Control Center — NeuraGuard", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
page_setup("Agent Control Center", "🤖")

st.markdown("## 🤖 Agent Control Center")
st.caption("Execute LangGraph multi-agent workflows and inspect routing decisions, latency, and health.")

# Run workflow
col_q, col_btn = st.columns([4, 1])
with col_q:
    query = st.text_input("Agent Query", "Research our latest compliance policy and summarize the risk.")
with col_btn:
    st.markdown("<div style='margin-top:28px;'>", unsafe_allow_html=True)
    run = st.button("🚀 Run Workflow")
    st.markdown("</div>", unsafe_allow_html=True)

if run:
    with st.spinner("Routing through agent graph..."):
        result = api_post("/agents/run", {"query": query})

    if result:
        st.divider()
        # Agent path
        path = result.get("agent_path", [])
        st.markdown("#### 🌐 Execution Path")
        if path:
            badges = " &nbsp;➔&nbsp; ".join(
                f'<span class="badge badge-green">🤖 {a}</span>' for a in path
            )
            st.markdown(f'<div style="margin:8px 0 16px 0;">{badges}</div>', unsafe_allow_html=True)
        else:
            st.info("No agent path recorded.")

        # Response + verification side by side
        col_resp, col_verif = st.columns([3, 2])
        with col_resp:
            raw_resp = result.get("final_response") or "No response."
            if raw_resp.startswith("Answer: "):
                raw_resp = raw_resp[8:].strip()
            st.markdown(f"""
            <div class="glass glass-blue" style="line-height:1.7;">
                {raw_resp}
            </div>
            """, unsafe_allow_html=True)
            if result.get("errors"):
                st.error(f"Errors: {result['errors']}")

        with col_verif:
            st.markdown("#### 🔬 Verification")
            verif = result.get("verification") or {}
            if verif:
                for k, v in verif.items():
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:5px 0;
                        border-bottom:1px solid rgba(255,255,255,0.06);">
                        <span style="color:#64748b;font-size:0.85rem;">{k}</span>
                        <span style="color:#10b981;font-weight:600;font-size:0.85rem;">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No verification data.")

st.divider()

# Agent health
st.markdown("#### 📊 Agent Health (All-Time)")
status = api_get("/agents/status")
agents = status.get("agents", {})

if not agents:
    st.info("No agent run history recorded yet.")
else:
    header_col = st.columns([2, 1, 1, 1, 1])
    header_col[0].markdown('<span style="color:#64748b;font-size:0.78rem;font-weight:700;text-transform:uppercase;">Agent</span>', unsafe_allow_html=True)
    header_col[1].markdown('<span style="color:#64748b;font-size:0.78rem;font-weight:700;text-transform:uppercase;">Runs</span>', unsafe_allow_html=True)
    header_col[2].markdown('<span style="color:#64748b;font-size:0.78rem;font-weight:700;text-transform:uppercase;">Failures</span>', unsafe_allow_html=True)
    header_col[3].markdown('<span style="color:#64748b;font-size:0.78rem;font-weight:700;text-transform:uppercase;">Avg Latency</span>', unsafe_allow_html=True)
    header_col[4].markdown('<span style="color:#64748b;font-size:0.78rem;font-weight:700;text-transform:uppercase;">Status</span>', unsafe_allow_html=True)

    for name, s in agents.items():
        cols = st.columns([2, 1, 1, 1, 1])
        failure_rate = s.get("failures", 0) / max(s.get("runs", 1), 1)
        status_badge = '<span class="badge badge-green">Healthy</span>' if failure_rate < 0.1 else '<span class="badge badge-amber">Degraded</span>'
        cols[0].markdown(f"**{name}**")
        cols[1].markdown(f"`{s.get('runs', 0)}`")
        cols[2].markdown(f"`{s.get('failures', 0)}`")
        cols[3].markdown(f"`{s.get('avg_duration_ms', 0):.1f} ms`")
        cols[4].markdown(status_badge, unsafe_allow_html=True)
