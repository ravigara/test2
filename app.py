"""
Mitra — Your Private Mental Wellness Companion
Main Streamlit entrypoint: premium home dashboard.
"""

import streamlit as st
from database.db import (
    init_db, get_today_checkin, get_total_checkins,
    get_avg_mood_score,
)
from utils.helpers import get_greeting, load_user_name, get_time_of_day
from utils.constants import EMOTION_EMOJI, MOOD_SCORE_LABELS, PALETTE
from datetime import date

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mitra – Your Wellness Companion",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Initialize DB ──────────────────────────────────────────────────────────────
init_db()

# ── Custom CSS ─────────────────────────────────────────────────────────────────
try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── Sidebar ────────────────────────────────────────────────────────────────────
from components.sidebar import render_sidebar
render_sidebar()

# ── Extra inline page styles ───────────────────────────────────────────────────
st.markdown("""
<style>
/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg,
        rgba(27,108,168,0.35) 0%,
        rgba(76,175,130,0.20) 50%,
        rgba(155,89,182,0.15) 100%);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 40px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '🌱';
    position: absolute;
    right: 24px; top: 50%;
    transform: translateY(-50%);
    font-size: 9rem;
    opacity: 0.07;
    animation: float 4s ease-in-out infinite;
}
.hero-banner h1 {
    margin: 0 0 8px 0;
    font-size: 2.2rem;
    color: #f0f4ff !important;
}
.hero-banner p {
    margin: 0;
    color: #93c5fd !important;
    font-size: 1rem;
    opacity: 0.9;
}

/* Feature cards */
.feature-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 12px;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.3s ease,
                border-color 0.3s ease;
    cursor: pointer;
    min-height: 165px;
    position: relative;
    overflow: hidden;
}
.feature-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 16px 40px rgba(0,0,0,0.35);
}
.feature-card .card-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
    display: block;
    animation: float 3s ease-in-out infinite;
}
.feature-card .card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0f4ff;
    margin-bottom: 6px;
}
.feature-card .card-desc {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.5;
}
.feature-card .card-glow {
    position: absolute;
    bottom: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%;
    filter: blur(30px);
    opacity: 0.15;
    pointer-events: none;
}

/* Consent modal */
.consent-card {
    background: rgba(27,108,168,0.08);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.consent-card h3 { color: #93c5fd !important; margin-top: 0; }
.consent-card ul { color: #94a3b8 !important; }
.consent-card strong { color: #cbd5e0 !important; }

/* Quote footer */
.quote-footer {
    text-align: center;
    font-style: italic;
    color: #475569;
    padding: 20px;
    font-size: 0.95rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── First-Run Consent ──────────────────────────────────────────────────────────
from database.db import get_user_profile, set_user_profile

if not get_user_profile("consent_given"):
    st.markdown("""
    <div class="consent-card">
        <h3>👋 Welcome to Mitra!</h3>
        <p style="color:#94a3b8;"><strong style="color:#cbd5e0;">Before you begin, here's what you should know:</strong></p>
        <ul>
            <li>📷 <strong>Facial images</strong> are processed in memory only — never stored or transmitted</li>
            <li>📝 <strong>Journal entries</strong> are saved on this device only</li>
            <li>🤖 <strong>Mood labels and journal text</strong> are sent to OpenAI's API for AI responses</li>
            <li>🔒 <strong>No personal identifiers</strong> are attached to API calls</li>
            <li>💙 Mitra is a <strong>companion, not a therapist</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✅ I understand — Let's begin!", type="primary", key="consent_btn"):
        set_user_profile("consent_given", "true")
        st.rerun()

# ── Hero Banner ────────────────────────────────────────────────────────────────
name = load_user_name() or "friend"
greeting = get_greeting(name)

st.markdown(f"""
<div class="hero-banner">
    <h1>{greeting}</h1>
    <p>Your private mental wellness space. No judgment, no tracking, just you.</p>
</div>
""", unsafe_allow_html=True)

# ── Stats Row ──────────────────────────────────────────────────────────────────
today_ci      = get_today_checkin()
total_checkins = get_total_checkins()
avg_mood      = get_avg_mood_score()

col1, col2, col3, col4 = st.columns(4)
with col1:
    mood_val = EMOTION_EMOJI.get(today_ci.get("detected_mood", "—") if today_ci else "—", "—")
    mood_label = today_ci.get("detected_mood", "—").capitalize() if today_ci else "—"
    st.metric("Today's Mood", f"{mood_val} {mood_label}", delta=f"{today_ci.get('mood_score','?')}/10" if today_ci else None)
with col2:
    stress     = today_ci.get("stress_level", "—").capitalize() if today_ci else "—"
    stress_icon = "🔴" if stress == "High" else "🟡" if stress == "Medium" else "🟢" if stress == "Low" else ""
    st.metric("Stress Level", f"{stress_icon} {stress}")
with col3:
    st.metric("Total Check-ins", total_checkins)
with col4:
    st.metric("Avg Mood Score", f"{avg_mood}/10" if avg_mood else "—")

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Cards ──────────────────────────────────────────────────────────────
st.markdown("### 🧭 What would you like to do?")

nav_cards = [
    {
        "icon": "📸", "title": "Daily Check-In",
        "desc": "Capture your mood with your camera and get a personalized Mitra response.",
        "cta": "Start Check-In →", "page": "pages/1_Daily_Checkin.py",
        "color": "#1B6CA8", "glow": "#3b82f6", "done": bool(today_ci),
    },
    {
        "icon": "📝", "title": "Journal",
        "desc": "Free-form journaling with AI-powered reflection and theme analysis.",
        "cta": "Open Journal →", "page": "pages/2_Journal.py",
        "color": "#4CAF82", "glow": "#22c55e", "done": False,
    },
    {
        "icon": "💬", "title": "AI Companion",
        "desc": "Have a real conversation with Mitra. Your mood context is actively used.",
        "cta": "Open Chat →", "page": "pages/5_Chatbot.py",
        "color": "#E05C5C", "glow": "#ef4444", "done": False,
    },
    {
        "icon": "📊", "title": "Mood Trends",
        "desc": "Visualize your mood patterns, stress levels, and journal sentiment over time.",
        "cta": "View Trends →", "page": "pages/3_Mood_Trends.py",
        "color": "#F5A623", "glow": "#f59e0b", "done": False,
    },
    {
        "icon": "💡", "title": "Wellness Tips",
        "desc": "Get personalized wellness suggestions and guided breathing exercises.",
        "cta": "Get Tips →", "page": "pages/4_Wellness_Tips.py",
        "color": "#9B59B6", "glow": "#a855f7", "done": False,
    },
]

cols = st.columns(2)
for i, card in enumerate(nav_cards):
    with cols[i % 2]:
        done_badge = " ✅" if card["done"] else ""
        st.markdown(
            f"""
            <div class="feature-card" style="border-top: 4px solid {card['color']};">
                <div class="card-glow" style="background: {card['glow']};"></div>
                <span class="card-icon">{card['icon']}{done_badge}</span>
                <div class="card-title">{card['title']}</div>
                <div class="card-desc">{card['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(card["cta"], key=f"nav_{i}", use_container_width=True):
            st.switch_page(card["page"])
        st.write("")

# ── Motivational Footer ────────────────────────────────────────────────────────
st.markdown("---")
tod = get_time_of_day()
quotes = {
    "morning":   "Every morning is a fresh start. 🌅 Take it one breath at a time.",
    "afternoon": "You're doing better than you think. Keep going. 💙",
    "evening":   "Rest is productive too. You deserve to wind down. 🌙",
    "night":     "Taking care of your mind is the bravest thing you can do. ✨",
}
st.markdown(
    f'<div class="quote-footer">"{quotes.get(tod, "You matter. 💙")}"</div>',
    unsafe_allow_html=True,
)
