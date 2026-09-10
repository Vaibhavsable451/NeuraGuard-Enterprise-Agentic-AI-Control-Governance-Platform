import streamlit as st
from utils import page_setup, api_get, api_post

st.set_page_config(page_title="Incident Center — NeuraGuard", page_icon="🚨", layout="wide", initial_sidebar_state="expanded")
page_setup("Incident Center", "🚨")

st.markdown("## 🚨 Incident Center")
st.caption("Automated AI security incident detection, self-healing triggers, and full incident timelines.")

data = api_get("/incidents")
incidents = data.get("incidents", [])

SEV_COLOR = {"critical": "red", "high": "red", "medium": "amber", "low": "green"}

if not incidents:
    st.success("✅ All Systems Operational — No active incidents detected.")
else:
    st.markdown(f'<span class="badge badge-red">{len(incidents)} active incident(s)</span>', unsafe_allow_html=True)
    st.markdown("")

    for inc in reversed(incidents):
        sev = inc.get("severity", "medium").lower()
        color_class = f"glass-{SEV_COLOR.get(sev, 'amber')}"
        badge_class = f"badge-{'red' if sev in ('critical','high') else 'amber' if sev=='medium' else 'green'}"

        with st.expander(
            f"[{inc.get('severity','?').upper()}] {inc.get('kind','Incident')} — {inc.get('status','open')}",
            expanded=(sev in ("critical","high"))
        ):
            col_info, col_action = st.columns([3, 1])

            with col_info:
                st.markdown(f"""
                <div class="glass {color_class}">
                    <p><span style="color:#64748b;">Root Cause:</span> {inc.get('root_cause', '–')}</p>
                    <p><span style="color:#64748b;">Impact:</span> {inc.get('impact', '–')}</p>
                    <p><span style="color:#64748b;">Description:</span> {inc.get('description', '–')}</p>
                </div>
                """, unsafe_allow_html=True)

                actions = inc.get("self_healing_actions", [])
                if actions:
                    st.markdown("**🔧 Self-Healing Actions:**")
                    for a in actions:
                        st.markdown(f"""
                        <div style="padding:6px 12px; margin:3px 0; background:rgba(16,185,129,0.08);
                            border-radius:6px; border-left:3px solid #10b981; font-size:0.88rem;">
                            <strong>{a.get('action','')}</strong>:
                            <span style="color:#94a3b8;">{a.get('outcome','')}</span>
                        </div>
                        """, unsafe_allow_html=True)

            with col_action:
                st.markdown(f'<span class="{badge_class} badge">{sev.upper()}</span>', unsafe_allow_html=True)
                st.markdown("")
                if inc.get("status") != "resolved":
                    if st.button("🔧 Self-Heal", key=f"heal_{inc['incident_id']}"):
                        with st.spinner("Applying self-healing..."):
                            result = api_post(f"/incidents/{inc['incident_id']}/self-heal", {})
                        if result:
                            st.success("Applied!")
                            st.rerun()
                else:
                    st.success("Resolved ✅")

            with st.expander("📅 Timeline"):
                st.json(inc.get("timeline", []))
