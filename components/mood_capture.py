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


def live_camera_streamlit() -> dict:
    """
    Renders Start and Stop buttons and displays the live OpenCV default camera feed directly in Streamlit.
    Returns the last captured emotion state.
    """
    import cv2
    import numpy as np
    from mood_tracker import detector
    
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False
        
    if "live_result" not in st.session_state:
        st.session_state.live_result = {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}

    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🔴 Start Live Camera", type="primary", disabled=st.session_state.camera_running, use_container_width=True)
        if start_btn:
            st.session_state.camera_running = True
            st.rerun()
            
    with col2:
        stop_btn = st.button("⏹️ Stop & Capture Emotion", type="secondary", disabled=not st.session_state.camera_running, use_container_width=True)
        if stop_btn:
            st.session_state.camera_running = False
            st.rerun()

    if st.session_state.camera_running:
        try:
            detector._load_model_and_cascade()
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("Could not open default system camera.")
                st.session_state.camera_running = False
                return st.session_state.live_result
                
            stframe = st.empty()
            
            while st.session_state.camera_running:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                
                if len(faces) > 0:
                    faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                    (x, y, w, h) = faces[0]
                    roi_gray = gray[y:y+h, x:x+w]
                    roi = cv2.resize(roi_gray, (64, 64))
                    roi = roi.astype("float32") / 255.0
                    roi = np.expand_dims(roi, axis=-1)
                    roi = np.expand_dims(roi, axis=0)

                    preds = detector._model.predict(roi, verbose=0)[0]
                    dominant_idx = np.argmax(preds)
                    detected_emotion = detector.MODEL_LABELS[dominant_idx].lower()
                    confidence = float(preds[dominant_idx])
                    
                    total = float(sum(preds)) or 1.0
                    all_scores = {detector.MODEL_LABELS[i].lower(): float(float(preds[i]) / total) for i in range(len(preds))}
                    
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
                    cv2.putText(frame, f"{detector.MODEL_LABELS[dominant_idx]} ({confidence*100:.0f}%)", (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                                
                    st.session_state.live_result = {
                        "emotion": detected_emotion,
                        "confidence": confidence,
                        "all_scores": all_scores
                    }
                
                # Convert BGR to RGB for Streamlit rendering
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                stframe.image(frame_rgb, channels="RGB", use_container_width=True)
                
            cap.release()
            
        except Exception as e:
            st.error(f"Failed to process live camera: {e}")
            st.session_state.camera_running = False

    return st.session_state.live_result


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
