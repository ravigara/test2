import streamlit as st
from database.db import get_streak, get_user_profile, set_user_profile, get_today_checkin, clear_all_data
from utils.helpers import load_user_name, format_streak
from utils.constants import EMOTION_EMOJI


def render_sidebar():
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div style="text-align:center;padding:24px 0 16px 0;">
            <div style="font-size:3.5rem;animation:float 3s ease-in-out infinite;display:inline-block;">🌱</div>
            <div style="font-size:1.7rem;font-weight:800;
                        background:linear-gradient(135deg,#60a5fa,#34d399);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text;letter-spacing:-0.5px;margin-top:4px;">
                Mitra
            </div>
            <div style="font-size:0.78rem;color:#475569;margin-top:2px;letter-spacing:0.05em;">
                YOUR PRIVATE WELLNESS SPACE
            </div>
        </div>
        <style>
        @keyframes float {
            0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)}
        }
        </style>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Name Input ─────────────────────────────────────────────────────────
        saved_name = load_user_name()
        name = st.text_input(
            "Your name",
            value=saved_name,
            placeholder="Enter your name...",
            key="sidebar_name_input_global",
            help="Stored only on this device",
        )
        if name and name != saved_name:
            set_user_profile("name", name)

        st.divider()

        # ── Streak & Status ────────────────────────────────────────────────────
        streak = get_streak()
        st.metric("🔥 Current Streak", f"{streak} day{'s' if streak != 1 else ''}")
        st.caption(format_streak(streak))

        today_ci = get_today_checkin()
        if today_ci:
            mood_emoji = EMOTION_EMOJI.get(today_ci.get("detected_mood", "neutral"), "😐")
            st.success(f"✅ Checked in! {mood_emoji} Score: {today_ci.get('mood_score','?')}/10")
        else:
            st.warning("📋 No check-in yet today")

        st.divider()

        # ── Navigation ─────────────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.75rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">📍 Navigate</div>', unsafe_allow_html=True)

        pages = [
            ("app.py",                   "🏠", "Home"),
            ("pages/1_Daily_Checkin.py", "📸", "Daily Check-In"),
            ("pages/2_Journal.py",       "📝", "Journal"),
            ("pages/5_Chatbot.py",       "💬", "AI Chatbot"),
            ("pages/3_Mood_Trends.py",   "📊", "Mood Trends"),
            ("pages/4_Wellness_Tips.py", "💡", "Wellness Tips"),
        ]
        for path, icon, label in pages:
            st.page_link(path, label=f"{icon}  {label}")

        st.divider()

        # ── Privacy ────────────────────────────────────────────────────────────
        st.markdown('<div style="font-size:0.75rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">🔒 Privacy</div>', unsafe_allow_html=True)
        st.caption("All data stays on your device. No cloud sync.")

        with st.expander("⚠️ Danger Zone"):
            st.warning("This will permanently delete all your data.")
            confirm = st.checkbox("I understand this cannot be undone", key="delete_confirm_global")
            if confirm:
                if st.button("🗑️ Clear All My Data", key="clear_data_btn_global", type="primary"):
                    clear_all_data()
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.success("✅ All data cleared.")
                    st.rerun()


        # ── API Key Status ─────────────────────────────────────────────────────
        st.divider()
        try:
            from utils.openai_client import get_robust_client
            c = get_robust_client()
            total     = c.total_keys
            current   = c.active_key_number
            remaining = c.remaining_keys
            color = "#22c55e" if remaining > 1 else "#f59e0b" if remaining == 1 else "#ef4444"
            st.markdown(
                f'<div style="font-size:0.78rem;color:#475569;margin-bottom:4px;">🔑 API Key Pool</div>'
                f'<div style="font-size:0.82rem;color:{color};font-weight:700;">'
                f'Key {current}/{total} active &nbsp;·&nbsp; {remaining} key(s) remaining</div>',
                unsafe_allow_html=True
            )
        except Exception:
            pass
