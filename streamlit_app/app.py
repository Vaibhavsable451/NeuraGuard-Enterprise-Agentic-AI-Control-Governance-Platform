import streamlit as st
from utils import page_setup, check_backend_status, API_BASE

st.set_page_config(
    page_title="NeuraGuard — Control Plane",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)
page_setup("NeuraGuard", "🛡️")

# Hero
st.markdown("""
<div style="padding: 8px 0 24px 0;">
    <div style="font-size:0.9rem; color:#10b981; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:6px;">Enterprise AI Control Platform</div>
    <h1 style="font-size:2.7rem; margin:0; background:linear-gradient(135deg,#fff 30%,#10b981 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🛡️ NeuraGuard Control Plane</h1>
    <p style="color:#94a3b8; font-size:1.05rem; margin:8px 0 0 0;">Real-time Governance · Multi-Agent Routing · RAG Evaluation · FinOps · Incident Management</p>
</div>
""", unsafe_allow_html=True)

# Status pill
is_online = check_backend_status()
col_l, col_r = st.columns([1, 5])
with col_l:
    if is_online:
        st.markdown('<span class="badge badge-green">🟢 Backend Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-red">🔴 Backend Offline</span>', unsafe_allow_html=True)
with col_r:
    st.caption(f"API: `{API_BASE}` — Docs: [`{API_BASE}/docs`]({API_BASE}/docs)")

st.divider()

# Module cards
MODULES = [
    ("💬", "1. AI Chat", "Governed multi-agent chat with PII & guardrail protection.", "AI_Chat"),
    ("🔍", "2. RAG Playground", "Compare 11 RAG strategies — naive, graph, self-RAG, corrective…", "RAG_Playground"),
    ("🤖", "3. Agent Control Center", "Inspect LangGraph agent routing, paths, latency & health.", "Agent_Control_Center"),
    ("🛡️", "4. Governance Dashboard", "Risk scores, PII alerts, policy audit logs & violation tracking.", "Governance_Dashboard"),
    ("🧪", "5. Evaluation Dashboard", "Automated groundedness, safety & agent quality benchmarks.", "Evaluation_Dashboard"),
    ("📊", "6. Observability Dashboard", "Request metrics, LLM latency traces & error monitoring.", "Observability_Dashboard"),
    ("💰", "7. FinOps Dashboard", "Per-agent token cost, budget anomalies & optimization tips.", "FinOps_Dashboard"),
    ("🚨", "8. Incident Center", "Auto-detected incidents, self-healing triggers & timelines.", "Incident_Center"),
    ("👤", "9. Human Approval Queue", "Review & action high-risk requests requiring human oversight.", "Human_Approval_Queue"),
]

cols = st.columns(3)
for i, (icon, name, desc, page) in enumerate(MODULES):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="glass glass-green" style="min-height:140px; cursor:pointer;">
            <div style="font-size:1.75rem; margin-bottom:8px;">{icon}</div>
            <strong style="color:#f1f5f9; font-size:1.1rem;">{name}</strong>
            <p style="color:#94a3b8; font-size:0.92rem; margin:6px 0 0 0; line-height:1.5;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
