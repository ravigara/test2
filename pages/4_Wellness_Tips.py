"""
Page 4 — Wellness Tips
AI-generated personalized wellness suggestions + inline guided breathing exercise.
"""

import streamlit as st
import time
from datetime import date

from database.db import (
    get_today_checkin, get_journals, save_suggestions,
    get_wellness_suggestions_for_date,
)
from components.ai_companion import get_wellness_suggestions
from utils.constants import WELLNESS_CATEGORIES, EMOTION_EMOJI
from utils.helpers import get_time_of_day

st.set_page_config(
    page_title="Wellness Tips | Mitra",
    page_icon="💡",
    layout="centered",
)

from components.sidebar import render_sidebar
render_sidebar()

try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 💡 Personalized Wellness Tips")
st.caption("Fresh suggestions tailored to your current mood and energy.")

# ── Load Today's Context ───────────────────────────────────────────────────────
today_checkin = get_today_checkin()
today_journals = get_journals(days=1)

mood_score   = today_checkin.get("mood_score", 5) if today_checkin else 5
detected_mood = today_checkin.get("detected_mood", "neutral") if today_checkin else "neutral"
stress_level  = today_checkin.get("stress_level", "medium") if today_checkin else "medium"
tod           = get_time_of_day()

# Collect journal themes
all_themes = []
for j in today_journals:
    themes = j.get("themes", [])
    if isinstance(themes, list):
        all_themes.extend(themes)
themes_str = ", ".join(set(all_themes)) if all_themes else "general wellbeing"

# Context card
emoji = EMOTION_EMOJI.get(detected_mood, "😐")
if today_checkin:
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#e8f5e9,#f1f8e9);
                     border-radius:14px;padding:16px 20px;margin-bottom:20px;
                     border-left:4px solid #4CAF82;">
            <strong>Based on your mood:</strong> {emoji} {detected_mood.capitalize()} &nbsp;|&nbsp;
            Score: <strong>{mood_score}/10</strong> &nbsp;|&nbsp;
            Stress: <strong>{stress_level.capitalize()}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("💡 No check-in today. Showing general wellness tips.")

# ── Load or Generate Suggestions ──────────────────────────────────────────────
today_str = date.today().isoformat()

if "wellness_suggestions" not in st.session_state:
    # Try DB cache first
    cached = get_wellness_suggestions_for_date(today_str)
    if cached:
        st.session_state.wellness_suggestions = cached
    else:
        with st.spinner("✨ Mitra is crafting your personalized suggestions..."):
            context = {
                "mood_score": mood_score,
                "detected_mood": detected_mood,
                "stress_level": stress_level,
                "themes": themes_str,
                "time_of_day": tod,
            }
            suggestions = get_wellness_suggestions(context)
            st.session_state.wellness_suggestions = suggestions
            save_suggestions({
                "date": today_str,
                "trigger_mood": detected_mood,
                "suggestions": suggestions,
                "category": suggestions[0].get("category", "general") if suggestions else "general",
            })

suggestions = st.session_state.wellness_suggestions

# Regenerate button
if st.button("🔄 Regenerate Tips", key="regen_tips_btn"):
    with st.spinner("Generating new tips..."):
        context = {
            "mood_score": mood_score,
            "detected_mood": detected_mood,
            "stress_level": stress_level,
            "themes": themes_str,
            "time_of_day": tod,
        }
        st.session_state.wellness_suggestions = get_wellness_suggestions(context)
    st.rerun()

# ── Suggestion Cards ───────────────────────────────────────────────────────────
st.markdown("### 🌟 Your Suggestions")

if suggestions:
    cols = st.columns(min(3, len(suggestions)))
    for i, suggestion in enumerate(suggestions[:3]):
        col = cols[i % len(cols)]
        with col:
            category = suggestion.get("category", "breathing")
            cat_info = WELLNESS_CATEGORIES.get(category, {"icon": "💡", "label": category.title()})
            icon = cat_info["icon"]
            label = cat_info["label"]
            title = suggestion.get("title", "Wellness Activity")
            description = suggestion.get("description", "")
            why_now = suggestion.get("why_now", "")

            st.markdown(
                f"""
                <div style="
                    background:white;
                    border-radius:16px;
                    padding:20px;
                    box-shadow:0 4px 16px rgba(0,0,0,0.08);
                    border-top:4px solid #1B6CA8;
                    height:100%;
                    margin-bottom:16px;
                ">
                    <div style="font-size:2rem;margin-bottom:8px;">{icon}</div>
                    <div style="font-size:0.75rem;color:#1B6CA8;font-weight:600;
                                text-transform:uppercase;letter-spacing:0.5px;
                                margin-bottom:6px;">{label}</div>
                    <div style="font-size:1.05rem;font-weight:700;color:#1A202C;
                                margin-bottom:10px;">{title}</div>
                    <div style="font-size:0.9rem;color:#4A5568;line-height:1.6;
                                margin-bottom:12px;">{description}</div>
                    <div style="font-size:0.82rem;color:#718096;font-style:italic;
                                border-top:1px solid #f0f0f0;padding-top:10px;">
                        💡 {why_now}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.warning("No suggestions generated. Please try regenerating.")

# ── Guided Breathing Exercise ──────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🌬️ Guided Breathing Exercise")
st.caption("4-7-8 breathing technique — one of the most effective ways to reduce stress quickly.")

with st.expander("▶️ Start Guided Breathing Session", expanded=False):
    st.markdown("""
    **The 4-7-8 Technique:**
    - Inhale quietly through your nose for **4 seconds**
    - Hold your breath for **7 seconds**
    - Exhale completely through your mouth for **8 seconds**
    - Repeat 3–4 times
    """)

    cycles = st.slider("Number of cycles:", 2, 6, 3, key="breathing_cycles")

    if st.button("🫁 Begin Breathing Session", key="start_breathing_btn", type="primary"):
        progress_bar = st.progress(0)
        status_text  = st.empty()
        cycle_info   = st.empty()

        total_cycle_time = 4 + 7 + 8  # 19 seconds per cycle

        for cycle in range(1, cycles + 1):
            cycle_info.markdown(f"**Cycle {cycle} of {cycles}**")

            # INHALE — 4 seconds
            for t in range(40):
                fraction = t / 40
                global_progress = ((cycle - 1) * total_cycle_time + fraction * 4) / (cycles * total_cycle_time)
                progress_bar.progress(min(global_progress, 1.0))
                status_text.markdown(
                    f"<div style='text-align:center;font-size:1.5rem;color:#1B6CA8;'>🌬️ Inhale... ({int(4 - fraction * 4) + 1}s)</div>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.1)

            # HOLD — 7 seconds
            for t in range(70):
                fraction = t / 70
                global_progress = ((cycle - 1) * total_cycle_time + 4 + fraction * 7) / (cycles * total_cycle_time)
                progress_bar.progress(min(global_progress, 1.0))
                status_text.markdown(
                    f"<div style='text-align:center;font-size:1.5rem;color:#F5A623;'>⏸️ Hold... ({int(7 - fraction * 7) + 1}s)</div>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.1)

            # EXHALE — 8 seconds
            for t in range(80):
                fraction = t / 80
                global_progress = ((cycle - 1) * total_cycle_time + 11 + fraction * 8) / (cycles * total_cycle_time)
                progress_bar.progress(min(global_progress, 1.0))
                status_text.markdown(
                    f"<div style='text-align:center;font-size:1.5rem;color:#4CAF82;'>💨 Exhale... ({int(8 - fraction * 8) + 1}s)</div>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.1)

        progress_bar.progress(1.0)
        status_text.markdown(
            "<div style='text-align:center;font-size:1.5rem;'>✅ Session complete! You did great! 💙</div>",
            unsafe_allow_html=True,
        )
        cycle_info.empty()

# ── Additional Wellness Resources ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎨 Quick Wellness Menu")

qcols = st.columns(3)
quick_tips = [
    ("🚶 5-Minute Walk", "Step outside for 5 minutes. Fresh air resets your perspective."),
    ("💧 Hydrate", "Drink a glass of water right now. Dehydration amplifies stress."),
    ("🙏 Gratitude", "Name 3 small things you're grateful for today."),
    ("📵 Screen Break", "Look at something 20 feet away for 20 seconds (20-20-20 rule)."),
    ("🎵 Music Therapy", "Play one song that reliably lifts your mood."),
    ("✍️ Brain Dump", "Write everything on your mind for 5 minutes without stopping."),
]

for i, (tip_title, tip_desc) in enumerate(quick_tips):
    with qcols[i % 3]:
        st.markdown(
            f"""
            <div style="background:#f8faff;border-radius:12px;padding:14px 16px;
                        margin-bottom:12px;border:1px solid #e8edf5;">
                <div style="font-weight:700;margin-bottom:4px;">{tip_title}</div>
                <div style="font-size:0.85rem;color:#718096;">{tip_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
