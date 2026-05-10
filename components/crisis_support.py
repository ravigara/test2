"""
Crisis support component — shows a non-blocking, dismissible safety banner
when the user's stress level is critically high.
"""

import streamlit as st
from utils.constants import CRISIS_RESOURCES


def show_crisis_banner():
    """
    Render a warm, non-blocking crisis support banner.
    Uses st.session_state to track user dismissal.
    Never blocks the user from continuing their check-in.
    """
    key = "crisis_banner_dismissed"
    if st.session_state.get(key, False):
        return

    with st.container():
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #fff5f5, #ffe8e8);
                border: 1px solid #E05C5C;
                border-radius: 16px;
                padding: 20px 24px;
                margin: 16px 0;
                box-shadow: 0 2px 12px rgba(224,92,92,0.12);
            ">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    <span style="font-size:1.5rem">💙</span>
                    <strong style="font-size:1.1rem; color:#c0392b;">You're not alone</strong>
                </div>
                <p style="color:#555; margin:0 0 12px 0; font-size:0.95rem;">
                    It looks like you're going through a tough time right now.
                    It's okay to reach out — trained listeners are available 24/7.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(len(CRISIS_RESOURCES))
        for col, resource in zip(cols, CRISIS_RESOURCES):
            with col:
                st.markdown(
                    f"""
                    <div style="
                        background:#fff;
                        border-radius:10px;
                        padding:12px;
                        text-align:center;
                        border:1px solid #eee;
                        box-shadow:0 1px 4px rgba(0,0,0,0.06);
                    ">
                        <div style="font-weight:700;font-size:0.85rem;color:#1B6CA8;">{resource['name']}</div>
                        <div style="font-size:1.1rem;font-weight:800;color:#E05C5C;margin:4px 0;">📞 {resource['number']}</div>
                        <div style="font-size:0.75rem;color:#718096;">{resource['hours']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("")
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("✕ Dismiss", key="dismiss_crisis_banner", help="Hide this banner"):
                st.session_state[key] = True
                st.rerun()
