"""
UI component for guided breathing and relaxation exercises.
"""
import streamlit as st

def render_breathing_exercise():
    """
    Renders an animated breathing circle using CSS and HTML.
    """
    st.markdown("""
    <style>
    .breathing-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, rgba(230,242,255,0.5), rgba(240,248,255,0.8));
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
        margin: 20px 0;
    }
    
    .breathe-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: radial-gradient(circle, #6C63FF 0%, #A5B4FC 100%);
        box-shadow: 0 0 40px rgba(108, 99, 255, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 1.2rem;
        animation: breathe 8s ease-in-out infinite;
    }
    
    @keyframes breathe {
        0% {
            transform: scale(1);
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.3);
        }
        50% {
            transform: scale(1.4);
            box-shadow: 0 0 60px rgba(108, 99, 255, 0.6);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.3);
        }
    }
    
    .breathe-text {
        margin-top: 40px;
        color: #4b5563;
        font-size: 1.1rem;
        text-align: center;
        font-weight: 500;
        animation: text-breathe 8s ease-in-out infinite;
    }
    
    @keyframes text-breathe {
        0%, 100% { content: "Breathe In..."; opacity: 0.8; }
        50% { content: "Breathe Out..."; opacity: 0.8; }
    }
    </style>
    
    <div class="breathing-container">
        <h3 style="margin-top:0; color:#374151; font-family:'Inter', sans-serif;">Guided Breathing</h3>
        <p style="color:#6b7280; font-size:0.9rem; margin-bottom:30px;">Sync your breathing with the circle to reduce stress.</p>
        
        <div class="breathe-circle"></div>
        
        <div class="breathe-text">Follow the rhythm</div>
    </div>
    """, unsafe_allow_html=True)
