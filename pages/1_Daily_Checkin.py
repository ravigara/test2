"""
Page 1 — Daily Check-In
Full check-in flow: facial capture → self-report → AI companion response.
"""

import streamlit as st
from datetime import date

from database.db import (
    save_checkin, get_today_checkin, get_streak, get_user_profile,
    set_user_profile,
)
from components.mood_capture import capture_and_detect, render_emotion_result
from components.ai_companion import get_checkin_response_stream
from components.crisis_support import show_crisis_banner
from utils.helpers import (
    get_greeting, get_time_of_day, derive_stress_level,
    format_streak, get_yesterday_mood, load_user_name,
)
from utils.constants import EMOTION_EMOJI, MOOD_SCORE_LABELS, ENERGY_OPTIONS

st.set_page_config(
    page_title="Daily Check-In | Mitra",
    page_icon="🌱",
    layout="centered",
)

from components.sidebar import render_sidebar
render_sidebar()

# ── Load custom CSS ────────────────────────────────────────────────────────────
try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── Page-specific styles ───────────────────────────────────────────────────────
st.markdown("""
<style>
.page-header {
    background: linear-gradient(135deg, rgba(27,108,168,0.25), rgba(76,175,130,0.12));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '📸';
    position: absolute; right: 24px; top: 50%;
    transform: translateY(-50%);
    font-size: 7rem;
    opacity: 0.06;
}
.page-header h2 { margin: 0 0 6px 0; color: #f0f4ff !important; font-size: 1.9rem; }
.page-header p  { margin: 0; color: #64748b !important; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
name = load_user_name()
greeting = get_greeting(name)
streak = get_streak()

st.markdown(f"""
<div class="page-header">
    <h2>{greeting}</h2>
    <p>📸 Daily Check-In &nbsp;·&nbsp; {format_streak(streak)}</p>
</div>
""", unsafe_allow_html=True)

# Check if already checked in today
today_checkin = get_today_checkin()
if today_checkin:
    st.success(
        f"✅ You've already checked in today! Come back tomorrow to keep your streak going. "
        f"Your mood today: {EMOTION_EMOJI.get(today_checkin.get('detected_mood','neutral'), '😐')} "
        f"**{today_checkin.get('detected_mood','').capitalize()}** — Score: **{today_checkin.get('mood_score','?')}/10**"
    )
    if today_checkin.get("ai_response"):
        with st.expander("💬 Mitra's message to you"):
            st.markdown(today_checkin["ai_response"])
    st.page_link("pages/2_Journal.py", label="📝 Go to Journal →", icon="📖")
    st.stop()

# ── Step 1: Facial Mood Capture ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📸 Step 1 — Capture Your Mood")
st.caption("Take a selfie and let Mitra detect your expression. Your image is never stored.")

camera_col, tip_col = st.columns([2, 1])
with camera_col:
    st.markdown("**Use your default camera for live expression detection.**")
    from components.mood_capture import live_camera_streamlit
    live_res = live_camera_streamlit()
    if live_res.get("confidence", 0) > 0:
        st.session_state.live_result = live_res

with tip_col:
    st.markdown("""
    <div style="background:#f0f8ff;border-radius:12px;padding:16px;margin-top:10px;">
        <strong>💡 Tips for best results</strong>
        <ul style="font-size:0.85rem;color:#555;margin-top:8px;">
            <li>Look directly at the camera</li>
            <li>Click <strong>Stop & Capture Emotion</strong> when ready</li>
            <li>Relax your expression naturally</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

detected_emotion = "neutral"
detection_result = {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}

if "live_result" in st.session_state and st.session_state.live_result.get("confidence", 0) > 0:
    detection_result = st.session_state.live_result
    detected_emotion = render_emotion_result(detection_result, allow_override=True)
else:
    st.info("📷 Live camera not started or no face detected — you can still complete check-in manually below.")
    override_sel = st.selectbox(
        "How are you feeling?",
        options=[f"{EMOTION_EMOJI[e]} {e.capitalize()}" for e in EMOTION_EMOJI],
        key="manual_mood_select",
    )
    detected_emotion = override_sel.split(" ", 1)[1].lower()

# ── Step 2: Self-Report Sliders ────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🎚️ Step 2 — Tell Me More")

mood_score = st.slider(
    "How would you rate your overall mood today?",
    min_value=1, max_value=10, value=5, step=1,
    help="1 = Very low, 10 = Amazing",
    key="mood_score_slider",
)
st.caption(f"_{MOOD_SCORE_LABELS.get(mood_score, '')}_")

energy_level = st.radio(
    "Energy level right now:",
    options=ENERGY_OPTIONS,
    horizontal=True,
    index=1,
    key="energy_radio",
)

notes = st.text_input(
    "Anything on your mind? _(optional)_",
    placeholder="e.g. Feeling a bit overwhelmed with deadlines...",
    key="checkin_notes",
)

# ── Step 3: AI Companion Response ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💬 Step 3 — Hear from Mitra")

if "checkin_done" not in st.session_state:
    st.session_state.checkin_done = False

# Calculate real-time stress level before submission
from utils.helpers import derive_stress_level
current_stress = derive_stress_level(mood_score, detected_emotion)
stress_colors = {"low": "#4CAF82", "medium": "#F5A623", "high": "#E05C5C"}
stress_icons  = {"low": "🟢", "medium": "🟡", "high": "🔴"}

st.markdown(
    f"""
    <div style="background:{stress_colors[current_stress]}15;
                border: 2px solid {stress_colors[current_stress]};
                border-radius: 12px; padding: 16px; margin: 24px 0;">
        <div style="font-size: 0.9rem; color: #718096; font-weight: 600; text-transform: uppercase;">
            🚦 AI Stress Detection
        </div>
        <div style="font-size: 1.2rem; color: #1A202C; margin-top: 4px;">
            Derived Stress Level: {stress_icons[current_stress]} <strong>{current_stress.capitalize()}</strong>
        </div>
        <div style="font-size: 0.85rem; color: #718096; margin-top: 4px;">
            Based on your detected expression ({detected_emotion}) and reported mood score.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

submit = st.button(
    "✨ Complete Check-In",
    type="primary",
    use_container_width=True,
    key="submit_checkin_btn",
)

if submit or st.session_state.checkin_done:
    confidence = detection_result.get("confidence", 0.0)
    stress_level = derive_stress_level(mood_score, detected_emotion)
    yesterday_mood = get_yesterday_mood()
    tod = get_time_of_day()

    # Crisis check
    if stress_level == "high" and mood_score <= 2:
        show_crisis_banner()

    # Energy indicator only (stress is now prominently shown above)
    st.markdown(
        f"""
        <div style="display:flex;gap:16px;flex-wrap:wrap;margin:12px 0;">
            <span style="background:#1B6CA822;border:1px solid #1B6CA8;
                         border-radius:20px;padding:4px 14px;font-size:0.9rem;">
                ⚡ Energy: <strong>{energy_level}</strong>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    context = {
        "name": name or "friend",
        "detected_mood": detected_emotion,
        "confidence": f"{confidence * 100:.0f}",
        "mood_score": mood_score,
        "energy_level": energy_level,
        "stress_level": stress_level,
        "notes": notes or "Nothing specific",
        "yesterday_mood": yesterday_mood,
        "time_of_day": tod,
    }

    # Stream Mitra's response
    if not st.session_state.checkin_done:
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#e8f5e9,#f1f8e9);
                         border-radius:16px;border-left:4px solid #4CAF82;
                         padding:16px 20px;margin:12px 0;">
                <strong>🌱 Mitra says...</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            with st.spinner("Mitra is thinking..."):
                response_text = "".join(get_checkin_response_stream(context))
        except EnvironmentError as e:
            st.error(f"⚠️ API key missing: {e}")
            st.stop()

        st.markdown(
            f"""
            <div style="background:#fff;border-radius:12px;padding:16px 20px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);margin:8px 0;
                        font-size:1.05rem;line-height:1.7;color:#1A202C;">
                {response_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Save to DB
        save_checkin({
            "date": date.today().isoformat(),
            "detected_mood": detected_emotion,
            "self_mood": detected_emotion,
            "mood_score": mood_score,
            "stress_level": stress_level,
            "energy_level": energy_level,
            "notes": notes,
            "ai_response": response_text,
        })
        st.session_state.checkin_done = True
        st.session_state.last_ai_response = response_text
        st.session_state.today_mood = detected_emotion

    else:
        st.markdown(
            f"""
            <div style="background:#fff;border-radius:12px;padding:16px 20px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);margin:8px 0;
                        font-size:1.05rem;line-height:1.7;color:#1A202C;">
                {st.session_state.get('last_ai_response', '')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.success("✅ Check-in saved! Your data is stored privately on this device.")
    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_Journal.py", label="📝 Go to Journal →")
    with col2:
        st.page_link("pages/4_Wellness_Tips.py", label="💡 View Wellness Tips →")
