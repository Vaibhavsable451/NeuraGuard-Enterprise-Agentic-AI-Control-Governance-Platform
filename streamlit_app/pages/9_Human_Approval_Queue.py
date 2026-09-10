import streamlit as st
from utils import page_setup, api_get, api_post

st.set_page_config(page_title="Approval Queue — NeuraGuard", page_icon="👤", layout="wide", initial_sidebar_state="expanded")
page_setup("Human Approval Queue", "👤")

st.markdown("## 👤 Human Approval Queue")
st.caption("Review and action high-risk AI requests flagged for mandatory human oversight.")

data = api_get("/approvals")
pending = data.get("pending", [])
all_approvals = data.get("all", [])

tab_pending, tab_history = st.tabs([
    f"⏳ Pending ({len(pending)})",
    f"📋 All Decisions ({len(all_approvals)})",
])

with tab_pending:
    if not pending:
        st.success("✅ Queue clear — No pending approvals.")
    else:
        for a in pending:
            risk = a.get("risk_score", 0)
            risk_color = "red" if risk >= 7 else "amber" if risk >= 4 else "green"
            badge_cls = f"badge-{'red' if risk >= 7 else 'amber' if risk >= 4 else 'green'}"

            with st.expander(f"📋 {a['approval_id']} — Risk Score: {risk}/10", expanded=True):
                col_info, col_form = st.columns([3, 2])

                with col_info:
                    st.markdown(f"""
                    <div class="glass glass-{risk_color}">
                        <p><span style="color:#64748b;">Request:</span><br>{a.get('original_request', '–')}</p>
                        <p><span style="color:#64748b;">Reason flagged:</span> {a.get('reason', '–')}</p>
                        <p><span style="color:#64748b;">Risk score:</span>
                            <span class="{badge_cls} badge">{risk} / 10</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_form:
                    reviewer = st.text_input("Your Name", placeholder="Reviewer name", key=f"rev_{a['approval_id']}")
                    reason = st.text_input("Decision Reason", placeholder="Brief justification", key=f"rsn_{a['approval_id']}")
                    c_approve, c_reject = st.columns(2)
                    if c_approve.button("✅ Approve", key=f"appr_{a['approval_id']}", type="primary"):
                        r = api_post(f"/approvals/{a['approval_id']}/approve",
                                     {"reviewer": reviewer or "unknown", "reason": reason or "Approved"})
                        if r:
                            st.success("Approved!")
                            st.rerun()
                    if c_reject.button("❌ Reject", key=f"rej_{a['approval_id']}"):
                        r = api_post(f"/approvals/{a['approval_id']}/reject",
                                     {"reviewer": reviewer or "unknown", "reason": reason or "Rejected"})
                        if r:
                            st.warning("Rejected.")
                            st.rerun()

with tab_history:
    if not all_approvals:
        st.info("No approval decisions recorded yet.")
    else:
        for a in reversed(all_approvals):
            decision = a.get("decision", "pending")
            d_cls = "badge-green" if decision == "approved" else "badge-red" if decision == "rejected" else "badge-amber"
            st.markdown(f"""
            <div class="glass" style="display:flex;justify-content:space-between;align-items:center;padding:12px 16px;margin-bottom:6px;">
                <div>
                    <span style="color:#64748b;font-size:0.78rem;">{a.get('approval_id','')}</span><br>
                    <span style="font-size:0.9rem;">{str(a.get('original_request',''))[:100]}…</span>
                </div>
                <div style="text-align:right;min-width:120px;">
                    <span class="badge {d_cls}">{decision.upper()}</span><br>
                    <span style="color:#64748b;font-size:0.78rem;margin-top:4px;display:block;">by {a.get('reviewer','unknown')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
