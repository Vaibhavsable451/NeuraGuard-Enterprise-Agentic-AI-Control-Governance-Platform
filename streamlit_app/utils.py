import os
import requests
import streamlit as st

API_BASE = os.getenv("AEGIS_API_BASE", "http://127.0.0.1:8000")


def check_backend_status() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.05rem !important;
    }

    /* Main app background */
    .stApp {
        background: #0a0f1a !important;
    }

    /* Main content area — generous padding to prevent left/right text clipping */
    .main .block-container {
        background: #0a0f1a !important;
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        padding-left: 3.5rem !important;
        padding-right: 3.5rem !important;
        max-width: 1450px !important;
        margin: 0 auto !important;
        color: #f1f5f9 !important;
    }

    /* Header bar */
    header[data-testid="stHeader"] {
        background: rgba(10, 15, 26, 0.8) !important;
        backdrop-filter: blur(8px) !important;
    }

    /* Sidebar collapse / expand toggle button — fixed floating top-left */
    [data-testid="collapsedControl"] {
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        background: #0f172a !important;
        border: 1.5px solid #10b981 !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4) !important;
    }
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarExpandButton"] button,
    button[aria-label="Expand sidebar"],
    button[aria-label="Collapse sidebar"] {
        color: #10b981 !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarExpandButton"] button svg,
    button[aria-label="Expand sidebar"] svg,
    button[aria-label="Collapse sidebar"] svg {
        fill: #10b981 !important;
        color: #10b981 !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #070c16 !important;
        border-right: 1px solid rgba(16, 185, 129, 0.2) !important;
        width: 310px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #070c16 !important;
    }

    /* Sidebar nav links */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem !important;
    }
    [data-testid="stSidebarNav"] a {
        color: #cbd5e1 !important;
        font-size: 0.98rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 0.6rem 0.85rem !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(16, 185, 129, 0.1) !important;
        color: #10b981 !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(16, 185, 129, 0.18) !important;
        color: #10b981 !important;
        font-weight: 700 !important;
        border-left: 3px solid #10b981 !important;
    }

    /* Custom page link buttons in sidebar */
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
        background: rgba(15, 22, 35, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 9px !important;
        padding: 8px 14px !important;
        margin-bottom: 5px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
        background: rgba(16, 185, 129, 0.18) !important;
        border-color: rgba(16, 185, 129, 0.45) !important;
        transform: translateX(3px) !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover p {
        color: #10b981 !important;
    }

    /* Text colors & sizes */
    p { color: #e2e8f0; font-size: 1.02rem; line-height: 1.6; }
    li { color: #e2e8f0; font-size: 1.02rem; }

    h1 { color: #ffffff !important; font-weight: 800 !important; font-size: 2.2rem !important; letter-spacing: -0.02em !important; }
    h2 { color: #f1f5f9 !important; font-weight: 700 !important; font-size: 1.7rem !important; }
    h3 { color: #e2e8f0 !important; font-weight: 600 !important; font-size: 1.35rem !important; }

    /* Metric widget */
    [data-testid="stMetric"] {
        background: rgba(16,185,129,0.06) !important;
        border: 1px solid rgba(16,185,129,0.22) !important;
        border-radius: 12px !important;
        padding: 18px !important;
    }
    [data-testid="stMetricValue"] {
        color: #10b981 !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 700 !important;
    }

    /* Buttons — primary style */
    .stButton > button {
        background: linear-gradient(135deg, #10b981, #059669) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.3rem !important;
        font-size: 0.96rem !important;
        box-shadow: 0 4px 14px rgba(16,185,129,0.25) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(16,185,129,0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea textarea {
        background: #0f1623 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important;
        color: #f1f5f9 !important;
        font-size: 1.02rem !important;
        padding: 0.55rem 0.85rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(16,185,129,0.5) !important;
        box-shadow: 0 0 0 2px rgba(16,185,129,0.15) !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: #0f1623 !important;
        border: 1px solid rgba(16,185,129,0.35) !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #f1f5f9 !important;
        font-size: 1.02rem !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(15, 22, 35, 0.85) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        font-size: 1.02rem !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: #0f1623 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 9px !important;
        color: #f1f5f9 !important;
        font-size: 1.02rem !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        font-size: 0.98rem !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(15, 22, 35, 0.65) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] summary {
        color: #f1f5f9 !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: rgba(15, 22, 35, 0.5) !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.98rem !important;
        border-radius: 7px !important;
    }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: rgba(16,185,129,0.18) !important;
        color: #10b981 !important;
    }

    /* Alerts / info / success / error */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        font-size: 1.02rem !important;
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.09) !important;
    }

    /* Spinner text */
    [data-testid="stSpinner"] {
        color: #10b981 !important;
        font-size: 1.02rem !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0a0f1a; }
    ::-webkit-scrollbar-thumb { background: rgba(16,185,129,0.35); border-radius: 3px; }

    /* Glass card helper class */
    .glass {
        background: rgba(15, 22, 35, 0.75);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 12px;
        padding: 18px 22px;
        margin-bottom: 12px;
        font-size: 1.02rem;
    }
    .glass-green { border-left: 3px solid #10b981; }
    .glass-red   { border-left: 3px solid #ef4444; }
    .glass-amber { border-left: 3px solid #f59e0b; }
    .glass-blue  { border-left: 3px solid #3b82f6; }

    /* Badge pills */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    .badge-green  { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
    .badge-red    { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.35); }
    .badge-amber  { background: rgba(245,158,11,0.15); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }
    </style>
    """, unsafe_allow_html=True)


def backend_banner():
    if not check_backend_status():
        st.error(
            "⚠️ FastAPI backend is offline. Run: `uv run uvicorn app.api.main:app --reload`",
            icon="🔴"
        )


def page_setup(title: str, icon: str):
    """Call at the top of every page after set_page_config."""
    inject_css()
    with st.sidebar:
        st.markdown("""
        <div style="padding: 4px 0 14px 0; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 14px;">
            <div style="font-size:1.4rem; font-weight:800; color:#ffffff; display:flex; align-items:center; gap:8px;">
                <span>🛡️</span> <span style="background: linear-gradient(135deg, #ffffff, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">NeuraGuard</span>
            </div>
            <div style="font-size:0.82rem; color:#94a3b8; font-weight:600; margin-top:2px;">Enterprise AI Control Plane</div>
        </div>
        """, unsafe_allow_html=True)

        if check_backend_status():
            st.markdown('<div style="margin-bottom:14px;"><span class="badge badge-green">🟢 Backend Online</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="margin-bottom:14px;"><span class="badge badge-red">🔴 Backend Offline</span></div>', unsafe_allow_html=True)

        st.markdown("<div style='font-size:0.8rem; color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; margin:14px 0 8px 4px;'>Navigation</div>", unsafe_allow_html=True)

        st.page_link("app.py", label="Control Plane", icon="🛡️")
        st.page_link("pages/1_AI_Chat.py", label="AI Chat", icon="💬")
        st.page_link("pages/2_RAG_Playground.py", label="RAG Playground", icon="🔍")
        st.page_link("pages/3_Agent_Control_Center.py", label="Agent Control Center", icon="🤖")
        st.page_link("pages/4_Governance_Dashboard.py", label="Governance Dashboard", icon="🛡️")
        st.page_link("pages/5_Evaluation_Dashboard.py", label="Evaluation Dashboard", icon="🧪")
        st.page_link("pages/6_Observability_Dashboard.py", label="Observability Dashboard", icon="📊")
        st.page_link("pages/7_FinOps_Dashboard.py", label="FinOps Dashboard", icon="💰")
        st.page_link("pages/8_Incident_Center.py", label="Incident Center", icon="🚨")
        st.page_link("pages/9_Human_Approval_Queue.py", label="Human Approval Queue", icon="👤")

        st.divider()
        st.caption("NeuraGuard v2.4 · 2026 Dark Edition")

    backend_banner()


def api_get(path: str, **kwargs):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if check_backend_status():
            st.error(f"API GET {path} failed: {e}")
        return {}


def api_post(path: str, json_body: dict, **kwargs):
    try:
        r = requests.post(f"{API_BASE}{path}", json=json_body, timeout=60, **kwargs)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        if check_backend_status():
            st.error(f"API POST {path} failed: {e}")
        return {}
