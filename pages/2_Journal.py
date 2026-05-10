"""
Page 2 — Daily Journal
Free-form journaling with AI reflection and session metrics.
"""

import streamlit as st
from datetime import date
import time

from database.db import save_journal, get_journals, get_today_checkin, get_user_profile
from components.ai_companion import analyze_journal
from utils.constants import EMOTION_EMOJI
from utils.helpers import format_date

st.set_page_config(
    page_title="Journal | Mitra",
    page_icon="📝",
    layout="centered",
)

from components.sidebar import render_sidebar
render_sidebar()

try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── Session Tracking ───────────────────────────────────────────────────────────
if "journal_start_time" not in st.session_state:
    st.session_state.journal_start_time = time.time()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 📝 Your Private Journal")
st.caption("Your journal is private and stored only on this device. 🔒")

# ── Context from today's check-in ─────────────────────────────────────────────
today_checkin = get_today_checkin()
today_mood = "neutral"
if today_checkin:
    today_mood = today_checkin.get("detected_mood", "neutral")
    emoji = EMOTION_EMOJI.get(today_mood, "😐")
    score = today_checkin.get("mood_score", "?")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#f0f4f8,#e8edf3);
                     border-radius:12px;padding:14px 18px;margin-bottom:16px;
                     border-left:4px solid #1B6CA8;">
            <strong>Today's mood context:</strong> {emoji} {today_mood.capitalize()} &nbsp;|&nbsp;
            Score: <strong>{score}/10</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Journal Entry ──────────────────────────────────────────────────────────────
st.markdown("### 📖 Write Your Entry")
journal_text = st.text_area(
    "Share whatever is on your mind...",
    placeholder="Start writing here... There's no right or wrong way to journal.",
    height=280,
)

# ── Session Metrics ────────────────────────────────────────────────────────────
word_count = len(journal_text.split()) if journal_text.strip() else 0
time_elapsed = int(time.time() - st.session_state.journal_start_time)
mins = time_elapsed // 60
secs = time_elapsed % 60

# Goal tracking
goal = int(get_user_profile("journal_goal") or 1)
past_entries = get_journals(days=0) # Get today's entries
entries_today = len(past_entries)

col1, col2, col3 = st.columns(3)
col1.caption(f"📝 Words: {word_count}")
col2.caption(f"⏱️ Session: {mins}m {secs}s")
col3.caption(f"🎯 Daily Goal: {entries_today} / {goal}")

submitted = st.button(
    "💙 Save & Reflect",
    type="primary",
    use_container_width=True,
    disabled=len(journal_text.strip()) < 10,
    key="journal_submit_btn",
)

if submitted and journal_text.strip():
    # Record time taken
    total_time_taken = f"{mins}m {secs}s"
    
    # Run crisis detection pipeline
    from ai.risk_scoring import calculate_risk
    from ai.emergency_mode import show_emergency_panel
    
    risk_info = calculate_risk(journal_text, detected_mood=today_mood)
    if risk_info["risk_level"] == "High Risk":
        show_emergency_panel()
        st.stop()

    with st.spinner("Mitra is reading your entry..."):
        try:
            analysis = analyze_journal(journal_text, today_mood)
        except Exception:
            analysis = {
                "sentiment": "neutral",
                "themes": [],
                "reflection": "I couldn't generate a reflection right now — all API keys are at their limit. Your entry has still been saved safely. 💙"
            }
            st.warning("⚠️ AI reflection unavailable — API quota reached. Your journal is still saved.")

    sentiment = analysis.get("sentiment", "neutral")
    themes = analysis.get("themes", [])
    reflection = analysis.get("reflection", "")

    # Sentiment badge
    sentiment_colors = {"positive": "#4CAF82", "neutral": "#F5A623", "negative": "#E05C5C"}
    sentiment_icons  = {"positive": "🟢",       "neutral": "🟡",       "negative": "🔴"}
    s_color = sentiment_colors.get(sentiment, "#95A5A6")
    s_icon  = sentiment_icons.get(sentiment, "⚪")

    st.markdown("---")
    st.markdown("### 💬 Mitra's Reflection")

    col_sent, col_themes = st.columns([1, 2])
    with col_sent:
        st.markdown(
            f"""
            <div style="background:{s_color}22;border:1px solid {s_color};
                         border-radius:20px;padding:6px 16px;
                         display:inline-block;font-size:0.9rem;">
                {s_icon} <strong>{sentiment.capitalize()}</strong> tone
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_themes:
        if themes:
            theme_tags = " ".join(
                f'<span style="background:#1B6CA822;border:1px solid #1B6CA8;'
                f'border-radius:20px;padding:4px 12px;font-size:0.8rem;'
                f'margin-right:4px;">#{t}</span>'
                for t in themes
            )
            st.markdown(theme_tags, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style="background:#fff;border-radius:14px;padding:18px 22px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.07);margin:12px 0;
                    font-size:1.05rem;line-height:1.75;color:#1A202C;
                    border-left:4px solid #4CAF82;">
            {reflection}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Save to DB
    save_journal({
        "date": date.today().isoformat(),
        "content": journal_text,
        "sentiment": sentiment,
        "themes": themes,
        "ai_reflection": reflection,
        "risk_score": risk_info["risk_score"],
        "risk_level": risk_info["risk_level"],
        "word_count": word_count,
        "time_taken": total_time_taken
    })
    
    # Reset tracking
    st.session_state.journal_start_time = time.time()
    st.success("✅ Journal entry saved privately on your device.")
    st.rerun()

# ── Past Entries ───────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📚 Past 7 Entries")

past_entries = get_journals(days=7)
if not past_entries:
    st.markdown(
        """
        <div style="text-align:center;padding:32px;color:#718096;">
            📖 No entries yet — today's a great day to start! 🌱
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    sentiment_colors = {"positive": "#4CAF82", "neutral": "#F5A623", "negative": "#E05C5C"}
    for entry in past_entries:
        s_color = sentiment_colors.get(entry.get("sentiment", "neutral"), "#95A5A6")
        themes_str = ", ".join(entry.get("themes") or []) or "—"
        preview = (entry.get("content", "")[:120] + "...") if len(entry.get("content", "")) > 120 else entry.get("content", "")
        date_label = format_date(entry.get("date", ""))
        
        words = entry.get("word_count", "N/A")
        duration = entry.get("time_taken", "N/A")

        with st.expander(
            f"📅 {date_label} · {entry.get('sentiment', 'neutral').capitalize()}"
        ):
            st.markdown(
                f"""
                <div style="border-left:3px solid {s_color};padding:8px 12px;
                             background:{s_color}11;border-radius:0 8px 8px 0;
                             margin-bottom:10px;font-size:0.9rem;color:#555;">
                    {preview}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(f"🏷️ Themes: {themes_str} | ⏱️ {duration} | 📝 {words} words")
            if entry.get("ai_reflection"):
                st.markdown(f"*💬 Mitra: {entry['ai_reflection']}*")
