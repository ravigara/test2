"""
Page 5 — AI Wellness Companion Chatbot
Premium UI with mood-adaptive OpenAI responses and crisis detection.
"""

import streamlit as st
from ai.chatbot_engine import generate_chat_response_stream
from ai.risk_scoring import calculate_risk
from ai.emergency_mode import show_emergency_panel, get_high_risk_response
from utils.constants import EMOTION_EMOJI

st.set_page_config(
    page_title="AI Companion | Mitra",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

from components.sidebar import render_sidebar
render_sidebar()

try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── Extra inline chat styles ───────────────────────────────────────────────────
st.markdown("""
<style>
.chat-header {
    background: linear-gradient(135deg, rgba(27,108,168,0.2), rgba(76,175,130,0.1));
    border: 1px solid rgba(59,130,246,0.3);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.chat-header::before {
    content: '💬';
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.08;
}
.chat-header h2 {
    margin: 0 0 4px 0;
    font-size: 1.8rem;
    color: #f0f4ff !important;
}
.chat-header p {
    margin: 0;
    color: #8892a4 !important;
    font-size: 0.9rem;
}
.mood-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.25);
    border-radius: 30px;
    padding: 8px 18px;
    font-size: 0.88rem;
    color: #93c5fd;
    margin-bottom: 20px;
    font-weight: 500;
    animation: float 3s ease-in-out infinite;
}
.disclaimer {
    background: rgba(245,166,35,0.08);
    border: 1px solid rgba(245,166,35,0.2);
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 0.82rem;
    color: #fde68a;
    margin-bottom: 20px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-header">
    <h2>💬 Mitra Companion</h2>
    <p>I'm here to listen, support, and walk alongside you — no judgment, just care.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="disclaimer">⚠️ Mitra is an AI wellness companion — not a therapist. For clinical help, please reach out to a professional.</div>', unsafe_allow_html=True)

# ── Mood Context Badge ─────────────────────────────────────────────────────────
current_mood = st.session_state.get("today_mood", "neutral")
mood_emoji = EMOTION_EMOJI.get(current_mood, "😐")

st.markdown(
    f'<div class="mood-badge">✨ Adapting to your detected mood: <strong>{current_mood.capitalize()} {mood_emoji}</strong></div>',
    unsafe_allow_html=True
)

# ── Session Init ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_initialized" not in st.session_state:
    # Greet based on mood
    greet_map = {
        "sad":     "Hey, I can tell it's been a tough day. I'm here for you. 💙 What's on your mind?",
        "angry":   "I see things might be feeling intense right now. I'm here, and we can take this slowly. 🌊",
        "fear":    "You're safe here. Whatever is worrying you, let's talk through it together. 🤍",
        "happy":   "You're radiating great energy today! 🌟 What's been making you smile?",
        "neutral": "Hello! I'm Mitra. How are you feeling right now? I'm all ears. 💬",
    }
    greeting = greet_map.get(current_mood, greet_map["neutral"])
    st.session_state.messages = [{"role": "assistant", "content": greeting}]
    st.session_state.chat_initialized = True

# ── Key Status Indicator ───────────────────────────────────────────────────────
try:
    from utils.openai_client import get_robust_client
    client = get_robust_client()
    total     = client.total_keys
    current   = client.active_key_number
    remaining = client.remaining_keys
    color = "#22c55e" if remaining > 1 else "#f59e0b" if remaining == 1 else "#ef4444"
    st.markdown(
        f'<div style="text-align:right;font-size:0.75rem;color:{color};margin-bottom:12px;">'
        f'🔑 API Key {current}/{total} active &nbsp;&middot;&nbsp; {remaining} remaining</div>',
        unsafe_allow_html=True
    )
except Exception:
    pass

# ── Display Chat History ───────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Emergency Lock ─────────────────────────────────────────────────────────────
if st.session_state.get("emergency_lock", False):
    show_emergency_panel()
    if st.button("✅ I am safe now — Reset Chat", type="primary", key="emergency_reset"):
        st.session_state.emergency_lock = False
        st.session_state.messages = [
            {"role": "assistant", "content": "I'm really glad you're safe. I'm still here whenever you want to talk. 💙"}
        ]
        st.rerun()
    st.stop()

# ── Chat Input ─────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Talk to Mitra..."):
    # Store & show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Crisis pipeline check
    risk_info = calculate_risk(prompt, detected_mood=current_mood)

    if risk_info["risk_level"] == "High Risk":
        st.session_state.emergency_lock = True
        emergency_response = get_high_risk_response()
        st.session_state.messages.append({"role": "assistant", "content": emergency_response})
        with st.chat_message("assistant"):
            st.markdown(emergency_response)
        st.rerun()

    # ── Generate AI Response ───────────────────────────────────────────────────
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            for chunk in generate_chat_response_stream(st.session_state.messages, current_mood):
                full_response += chunk
                response_placeholder.markdown(full_response + " ▌")

            response_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = "I'm having trouble connecting right now. All available API keys seem to be at their limit. Please try again shortly. 💙"
            response_placeholder.markdown(error_msg)
            full_response = error_msg

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ── Footer Controls ────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
        st.session_state.messages = []
        st.session_state.chat_initialized = False
        st.rerun()
