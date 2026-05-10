"""
Landing Page (Home)
Premium onboarding experience with animations and clear value proposition.
"""
import streamlit as st

st.set_page_config(
    page_title="Mitra | Your AI Mental Wellness Companion",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.markdown("""
<style>
/* Landing Page Specific Styles */
.hero-container {
    text-align: center;
    padding: 60px 20px;
    margin-top: 40px;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #38BDF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #475569;
    max-width: 600px;
    margin: 0 auto 40px auto;
    line-height: 1.6;
}
.floating-orb {
    width: 120px;
    height: 120px;
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

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 60px;
}
.feature-card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    text-align: center;
    transition: transform 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.05);
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
</style>

<div class="hero-container">
    <div class="trust-badge">🔒 100% Private & Device-Local Storage</div>
    <div class="floating-orb"></div>
    <h1 class="hero-title">Your AI companion for healthier daily emotional check-ins.</h1>
    <p class="hero-subtitle">
        Mitra is a safe, intelligent space to track your mood, journal your thoughts, 
        and talk through your feelings with an empathetic AI guide.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✨ Start Your First Check-In", type="primary", use_container_width=True):
        st.switch_page("pages/1_Daily_Checkin.py")

st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <h3 style="font-size:2rem; margin:0;">📸</h3>
        <h4 style="margin:10px 0; color:#1e293b;">Facial Mood Detection</h4>
        <p style="font-size:0.9rem; color:#64748b;">Instantly analyzes your expression to adapt the conversation tone securely.</p>
    </div>
    <div class="feature-card">
        <h3 style="font-size:2rem; margin:0;">💬</h3>
        <h4 style="margin:10px 0; color:#1e293b;">Adaptive AI Chat</h4>
        <p style="font-size:0.9rem; color:#64748b;">A companion that listens, remembers, and responds with clinical safety boundaries.</p>
    </div>
    <div class="feature-card">
        <h3 style="font-size:2rem; margin:0;">📊</h3>
        <h4 style="margin:10px 0; color:#1e293b;">Emotional Analytics</h4>
        <p style="font-size:0.9rem; color:#64748b;">Track your emotional trends, sleep correlations, and stress patterns over time.</p>
    </div>
</div>

<div style="margin-top: 80px; text-align: center; color: #94a3b8; font-size: 0.8rem; border-top: 1px solid #e2e8f0; padding-top: 20px;">
    <strong>Disclaimer:</strong> Mitra is an AI wellness tool, not a licensed therapist or medical provider. 
    If you are in crisis, please use our built-in emergency resources or call your local emergency number.
    <br/><br/>
    Data is stored locally on your device or session and is never sold or shared.
</div>
""", unsafe_allow_html=True)
