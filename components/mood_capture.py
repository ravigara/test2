"""
Camera capture and mood detection integration.
Wraps mood_tracker/detector.py with Streamlit-friendly interface.
"""

import streamlit as st
from PIL import Image
import numpy as np
import io

from mood_tracker.detector import detect_emotion
from utils.constants import EMOTION_EMOJI, EMOTION_COLOR, EMOTIONS


def capture_and_detect(uploaded_image) -> dict:
    """
    Detect emotion from a Streamlit camera_input image.

    Args:
        uploaded_image: bytes-like object from st.camera_input()

    Returns:
        {
            "emotion": str,
            "confidence": float,
            "all_scores": dict
        }
    """
    try:
        img = Image.open(uploaded_image).convert("RGB")
        img_array = np.array(img)
        result = detect_emotion(img_array)
        return result
    except Exception as e:
        st.warning(f"⚠️ No face detected or detection failed: {e}. You can still complete your check-in manually.")
        return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}



def render_emotion_result(result: dict, allow_override: bool = True) -> str:
    """
    Render the detected emotion with confidence bar.
    Returns the final (possibly overridden) emotion label.
    """
    emotion = result.get("emotion", "neutral")
    confidence = result.get("confidence", 0.0)
    all_scores = result.get("all_scores", {})

    emoji = EMOTION_EMOJI.get(emotion, "😐")
    color = EMOTION_COLOR.get(emotion, "#95A5A6")

    if confidence > 0:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {color}22, {color}11);
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 16px 20px;
                margin: 8px 0;
            ">
                <span style="font-size:2rem">{emoji}</span>
                <span style="font-size:1.3rem; font-weight:700; color:{color}; margin-left:10px;">
                    {emotion.capitalize()}
                </span>
                <br/>
                <span style="font-size:0.85rem; color:#718096;">
                    Detection confidence: {confidence * 100:.1f}%
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(float(confidence), text=f"{confidence * 100:.1f}% confidence")

        if all_scores:
            with st.expander("📊 View all emotion scores"):
                for em in EMOTIONS:
                    score = float(all_scores.get(em, 0.0))
                    em_emoji = EMOTION_EMOJI.get(em, "")
                    st.markdown(f"{em_emoji} **{em.capitalize()}**")
                    st.progress(score)
    else:
        st.warning("🤔 No face detected. You can still complete your check-in manually.")

    if allow_override:
        st.markdown("**Does this match how you feel?**")
        override = st.selectbox(
            "Override detected mood (optional)",
            options=["— Keep detected —"] + [f"{EMOTION_EMOJI[e]} {e.capitalize()}" for e in EMOTIONS],
            key="mood_override_select",
        )
        if override != "— Keep detected —":
            return override.split(" ", 1)[1].lower()

    return emotion
