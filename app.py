import streamlit as st
from database.db import (
    init_db, get_today_checkin, get_total_checkins,
    get_avg_mood_score, get_user_profile, set_user_profile
)
from utils.helpers import get_greeting, load_user_name, get_time_of_day
from utils.constants import EMOTION_EMOJI, MOOD_SCORE_LABELS, PALETTE
from datetime import date
from utils.gemini_client import get_robust_client

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
.hero-banner.morning::before { content: '🌅'; }
.hero-banner.afternoon::before { content: '☀️'; }
.hero-banner.evening::before { content: '🌇'; }
.hero-banner.night::before { content: '🌙'; }

.hero-banner h1 {
    margin: 0 0 8px 0;
    font-size: 2.2rem;
    color: #1e293b !important;
}
.hero-banner p {
    margin: 0;
    color: #334155 !important;
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
    box-shadow: 0 16px 40px rgba(0,0,0,0.15);
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
    color: #1e293b;
    margin-bottom: 6px;
}
.feature-card .card-desc {
    font-size: 0.85rem;
    color: #475569;
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

/* Onboarding */
.onboarding-container {
    text-align: center;
    padding: 40px 20px;
    margin-top: 20px;
}
.onboarding-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #38BDF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}
.floating-orb {
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, #8B5CF6 0%, #E0E7FF 100%);
    border-radius: 50%;
    margin: 0 auto 30px auto;
    box-shadow: 0 0 40px rgba(139, 92, 246, 0.4);
    animation: float-orb 6s ease-in-out infinite;
}
@keyframes float-orb {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-15px) scale(1.05); box-shadow: 0 0 60px rgba(139, 92, 246, 0.6); }
}
.trust-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #F0FDF4;
    color: #166534;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid #BBF7D0;
    margin-bottom: 20px;
}
.form-box {
    background: white;
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
    text-align: left;
    max-width: 500px;
    margin: 0 auto;
}

/* Quote footer */
.quote-footer {
    text-align: center;
    font-style: italic;
    color: #475569;
    padding: 20px;
    font-size: 1.05rem;
    font-weight: 500;
    border-top: 1px solid rgba(0,0,0,0.05);
    margin-top: 20px;
    background: linear-gradient(to right, transparent, rgba(108,99,255,0.05), transparent);
}
</style>
""", unsafe_allow_html=True)

# ── Dynamic AI Quote Helper ────────────────────────────────────────────────────
@st.cache_data(ttl=3600) # Cache for 1 hour to prevent API spam but keep it fresh
def get_daily_quote():
    client = get_robust_client()
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents="Generate a short, inspiring, and comforting single-sentence quote about mental health, mindfulness, or taking things one step at a time. It should be totally unique. Do not use quotes by famous people. Just give the quote text.",
        )
        return response.text.strip().replace('"', '')
    except Exception:
        return "Every step forward is a step toward healing. Take your time."

# ── Onboarding / Login View ────────────────────────────────────────────────────
if not get_user_profile("consent_given"):
    st.markdown("""
    <div class="onboarding-container">
        <div class="trust-badge">🔒 100% Private & Device-Local Storage</div>
        <div class="floating-orb"></div>
        <h1 class="onboarding-title">Welcome to Mitra</h1>
        <p style="color: #475569; margin-bottom:30px;">Your safe, intelligent space for emotional check-ins.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-box">', unsafe_allow_html=True)
    st.markdown("### Let's personalize your experience")
    
    with st.form("onboarding_form"):
        name_input = st.text_input("What should I call you?", placeholder="Your name")
        dob_input = st.date_input("When is your birthday?", min_value=date(1900, 1, 1), max_value=date.today())
        journal_goal = st.number_input("How many journal entries do you want to aim for daily?", min_value=1, max_value=10, value=1)
        
        st.markdown("""
        <hr style="opacity:0.3">
        <p style="font-size:0.85rem; color:#64748b;">
        <strong>Privacy Promise:</strong> All data (facial images, journals, birth date) is processed entirely in memory or saved only on this device. 
        Mitra is an AI companion, not a medical therapist.
        </p>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Start My Journey ✨", type="primary", use_container_width=True)
        if submitted:
            if not name_input.strip():
                st.error("Please enter your name.")
            else:
                set_user_profile("name", name_input.strip())
                set_user_profile("dob", dob_input.isoformat())
                set_user_profile("journal_goal", str(journal_goal))
                set_user_profile("consent_given", "true")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Halt execution so the dashboard doesn't render


# ── Sidebar (Only visible after onboarding) ────────────────────────────────────
from components.sidebar import render_sidebar
render_sidebar()

# ── Dashboard View ─────────────────────────────────────────────────────────────
name = load_user_name() or "friend"
greeting = get_greeting(name)
tod = get_time_of_day()

st.markdown(f"""
<div class="hero-banner {tod}">
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
        "desc": "Voice-enabled journaling with AI reflection and personalization.",
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

# ── Dynamic AI Quote Footer ────────────────────────────────────────────────────
st.markdown("---")
daily_quote = get_daily_quote()
st.markdown(
    f'<div class="quote-footer">"{daily_quote}"</div>',
    unsafe_allow_html=True,
)
