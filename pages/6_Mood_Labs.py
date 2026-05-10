import streamlit as st
import numpy as np
import cv2
import pandas as pd
import joblib
import altair as alt
from tensorflow.keras.models import load_model, model_from_json
from tensorflow.keras.preprocessing.image import img_to_array
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration, WebRtcMode
from pathlib import Path
from PIL import Image

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Mitra – Mood Labs",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 Mood Labs (Experimental)")
st.write("Explore different AI models to analyze your mood through images, text, and real-time video.")

# Apply custom CSS
try:
    with open("assets/styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

tab1, tab2, tab3 = st.tabs(["🖼️ Image Emotion", "✍️ Text Emotion", "📷 Webcam Emotion"])

# ── Paths ──────────────────────────────────────────────────────────────────────
MODELS_DIR = Path("modified_face/MoodTracker")

# ── Tab 1: Image Emotion Analyzer ──────────────────────────────────────────────
with tab1:
    st.header("Image Emotion Analyzer")
    st.write("Upload an image containing faces to detect emotions.")
    
    img_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if img_file is not None:
        try:
            # Load models locally within the try block to avoid global errors if missing
            face_classifier = cv2.CascadeClassifier(str(MODELS_DIR / "Emotion_Dectector/haarcascade_frontalface_default.xml"))
            img_classifier = load_model(str(MODELS_DIR / "Emotion_Dectector/model.h5"), compile=False)
            img_emotion_labels = ['Angry','Disgust','Fear','Happy','Neutral', 'Sad', 'Surprise']
            
            # Read image
            image = Image.open(img_file)
            frame = np.array(image.convert("RGB"))
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            faces = face_classifier.detectMultiScale(gray, 1.3, 5)
            
            for (x,y,w,h) in faces:
                cv2.rectangle(frame_bgr, (x,y), (x+w,y+h), (0,255,255), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_gray = cv2.resize(roi_gray, (48,48), interpolation=cv2.INTER_AREA)
                
                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float')/255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)
                    
                    prediction = img_classifier.predict(roi, verbose=0)[0]
                    label = img_emotion_labels[prediction.argmax()]
                    label_position = (x, y-10)
                    cv2.putText(frame_bgr, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                else:
                    cv2.putText(frame_bgr, 'No Faces', (30,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            # Convert back to RGB for Streamlit display
            result_img = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            st.image(result_img, caption="Processed Image", use_container_width=True)
            
        except Exception as e:
            st.error(f"Error processing image: {e}")

# ── Tab 2: NLP Text Emotion ────────────────────────────────────────────────────
with tab2:
    st.header("Text Emotion Analyzer")
    st.write("Type a sentence to detect its emotional tone.")
    
    @st.cache_resource
    def load_nlp_model():
        model_path = MODELS_DIR / "NLP-Text-Emotion/models/emotion_classifier_pipe_lr_03_jan_2022.pkl"
        return joblib.load(model_path)
        
    try:
        pipe_lr = load_nlp_model()
        emotions_emoji_dict = {"anger":"😠", "disgust":"🤮", "fear":"😨", "happy":"🤗", "joy":"😂", "neutral":"😐", "sad":"😔", "sadness":"😔", "shame":"😳", "surprise":"😮"}
        
        with st.form(key='emotion_clf_form'):
            raw_text = st.text_area("Please enter your text here...")
            submit_text = st.form_submit_button(label="Analyze Emotion")
            
        if submit_text and raw_text:
            col1, col2 = st.columns(2)
            prediction = pipe_lr.predict([raw_text])[0]
            probability = pipe_lr.predict_proba([raw_text])
            
            with col1:
                st.success('Prediction')
                emoji_icon = emotions_emoji_dict.get(prediction, "🤔")
                st.write(f"**{prediction.capitalize()}** {emoji_icon}")
                st.write(f"Confidence: {np.max(probability):.2f}")
                
            with col2:
                st.success('Prediction Probabilities')
                proba_df = pd.DataFrame(probability, columns=pipe_lr.classes_)
                proba_df_clean = proba_df.transpose().reset_index()
                proba_df_clean.columns = ["emotion", "probability"]
                
                fig = alt.Chart(proba_df_clean).mark_bar().encode(
                    x='emotion',
                    y='probability',
                    color='emotion'
                )
                st.altair_chart(fig, use_container_width=True)
                
    except Exception as e:
        st.error(f"Error loading NLP model: {e}")

# ── Tab 3: Webcam Emotion ──────────────────────────────────────────────────────
with tab3:
    st.header("Live Webcam Emotion Detection")
    st.write("Allow camera access to analyze your facial expressions in real-time.")
    
    RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    
    @st.cache_resource
    def load_webcam_model():
        json_file_path = MODELS_DIR / "Webcam Opencv Project/emotion_model1.json"
        weights_path = MODELS_DIR / "Webcam Opencv Project/emotion_model1.h5"
        
        with open(json_file_path, 'r') as f:
            loaded_model_json = f.read()
            
        classifier = model_from_json(loaded_model_json)
        classifier.load_weights(str(weights_path))
        
        face_cascade = cv2.CascadeClassifier(str(MODELS_DIR / "Webcam Opencv Project/haarcascade_frontalface_default.xml"))
        return classifier, face_cascade
        
    class FaceEmotionTransformer(VideoTransformerBase):
        def __init__(self):
            try:
                self.classifier, self.face_cascade = load_webcam_model()
                self.emotion_dict = {0: 'angry', 1: 'happy', 2: 'neutral', 3: 'sad', 4: 'surprise'}
            except Exception as e:
                st.error(f"Failed to load webcam models: {e}")
                self.classifier = None
                
        def transform(self, frame):
            if not self.classifier:
                return frame.to_ndarray(format="bgr24")
                
            img = frame.to_ndarray(format="bgr24")
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(img_gray, scaleFactor=1.3, minNeighbors=5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_gray = img_gray[y:y + h, x:x + w]
                roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
                
                if np.sum([roi_gray]) != 0:
                    roi = roi_gray.astype('float') / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)
                    
                    prediction = self.classifier.predict(roi, verbose=0)[0]
                    maxindex = int(np.argmax(prediction))
                    output = str(self.emotion_dict[maxindex])
                    
                    cv2.putText(img, output, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
            return img

    webrtc_streamer(
        key="emotion-detection",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=FaceEmotionTransformer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True
    )
