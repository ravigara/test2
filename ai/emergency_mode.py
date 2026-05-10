"""
Emergency Support UI and logic.
"""
import streamlit as st

def get_high_risk_response() -> str:
    return (
        "I'm really sorry you're feeling this way right now. "
        "You deserve support and care. Please consider reaching out to someone you trust "
        "or a mental health professional."
    )

def show_emergency_panel():
    """
    Renders an emergency UI block in Streamlit.
    """
    st.markdown("---")
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #fff5f5, #ffe3e3); 
                    border: 2px solid #E05C5C; border-radius: 12px; padding: 24px; margin: 16px 0;">
            <h3 style="color: #E05C5C; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                🚨 Emergency Support Required
            </h3>
            <p style="color: #1A202C; font-size: 1.1rem; margin-bottom: 20px;">
                Mitra is an AI companion and cannot provide the professional help you may need right now. 
                Please know that you are not alone. There are people ready to support you.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <strong>🌍 National Crisis Line</strong><br/>
                    Dial <strong>988</strong> (US) or <strong>112</strong> (EU/Global)
                </div>
                <div style="background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <strong>💬 Crisis Text Line</strong><br/>
                    Text <strong>HOME to 741741</strong>
                </div>
            </div>
            <p style="color: #4A5568; font-size: 0.9rem; margin-top: 20px;">
                <em>Please reach out to a trusted loved one or healthcare professional.</em>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
