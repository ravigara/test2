"""
UI Components for Emergency / High Risk scenarios.
"""
import streamlit as st

def show_emergency_panel():
    """
    Renders a dedicated Emergency Support Panel with grounding techniques and resources.
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff5f5, #ffe4e6); border-left: 5px solid #ef4444; border-radius: 12px; padding: 24px; margin: 20px 0; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);">
        <h3 style="color: #991b1b; margin-top: 0; font-family: 'Inter', sans-serif;">🛡️ Safety Mode Activated</h3>
        <p style="color: #7f1d1d; font-size: 1.05rem;">
            It sounds like you are going through an incredibly difficult time right now. 
            Please know that <strong>you are not alone, and your life has value</strong>.
        </p>
        <hr style="border-color: #fca5a5; opacity: 0.5;">
        """
    )
    
    from components.breathing_ui import render_breathing_exercise
    render_breathing_exercise()
    
    st.markdown("""
        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #fecaca;">
                <h4 style="color: #b91c1c; margin:0 0 8px 0;">📞 Emergency Resources</h4>
                <p style="margin:0; font-size: 0.95rem; color: #4b5563;">
                    If you are in immediate danger or feeling overwhelmed, please reach out to professional help:<br/>
                    • <strong>National Emergency Number:</strong> 911 / 112 (or your local equivalent)<br/>
                    • <strong>Crisis Text Line:</strong> Text HOME to 741741<br/>
                    • <strong>Suicide & Crisis Lifeline:</strong> Call or text 988 (US/Canada)
                </p>
            </div>
            
            <div style="background: white; padding: 16px; border-radius: 8px; border: 1px solid #fecaca;">
                <h4 style="color: #0369a1; margin:0 0 8px 0;">🌬️ Grounding Exercise (5-4-3-2-1)</h4>
                <p style="margin:0; font-size: 0.95rem; color: #4b5563;">
                    Let's take a deep breath together. Try to look around you and name out loud:<br/>
                    <strong>5</strong> things you can see<br/>
                    <strong>4</strong> things you can touch<br/>
                    <strong>3</strong> things you can hear<br/>
                    <strong>2</strong> things you can smell<br/>
                    <strong>1</strong> thing you can taste
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_high_risk_response() -> str:
    return (
        "I'm really sorry you're feeling this way. You deserve support and care. "
        "Please consider contacting someone you trust or a mental health professional right now. "
        "I have locked the chat temporarily to focus on your immediate safety."
    )
