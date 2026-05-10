"""
Facial Expression Mood Detector
Uses the pre-built Keras emotion model provided by the user.
Exposes: detect_emotion(image_array) -> dict
"""

import numpy as np
import logging
import cv2
import os
from pathlib import Path

logger = logging.getLogger(__name__)

EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
MODEL_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# Set paths to the model and cascade xml relative to this file
BASE_DIR = Path(__file__).parent / "Real-Time-Smile-Detection-and-Mood-Tracker"
MODEL_PATH = BASE_DIR / "emotion_model.hdf5"
CASCADE_PATH = BASE_DIR / "haarcascade_frontalface_default .xml"

# Lazy load model
_model = None
_face_cascade = None

def _load_model_and_cascade():
    global _model, _face_cascade
    if _model is None:
        try:
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" # Suppress TF warnings
            from tensorflow.keras.models import load_model
            _model = load_model(str(MODEL_PATH), compile=False)
        except Exception as e:
            logger.error(f"Failed to load Keras emotion model: {e}")
            raise e

    if _face_cascade is None:
        _face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
        if _face_cascade.empty():
            # Try to load default cv2 cascade if the provided one fails
            logger.warning(f"Failed to load cascade from {CASCADE_PATH}. Falling back to default.")
            _face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def detect_emotion(image_array: np.ndarray) -> dict:
    """
    Detect facial emotion from an RGB numpy array.

    Args:
        image_array: numpy array of shape (H, W, 3) in RGB format

    Returns:
        {
            "emotion": str,        # dominant emotion
            "confidence": float,   # 0.0 to 1.0
            "all_scores": dict     # {emotion: score} for all classes
        }
    """
    try:
        _load_model_and_cascade()
        
        # Convert RGB to BGR for cv2 processing (though Haar doesn't strictly care as we convert to gray anyway)
        # But grayscale conversion needs to know the format
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        if len(faces) == 0:
            return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}

        # For simplicity, just take the first detected face (or largest)
        # Let's take the largest face
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        (x, y, w, h) = faces[0]
        
        roi_gray = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi_gray, (64, 64))
        roi = roi.astype("float32") / 255.0
        roi = np.expand_dims(roi, axis=-1)
        roi = np.expand_dims(roi, axis=0)

        preds = _model.predict(roi, verbose=0)[0]
        
        # Normalize just in case, though softmax output should sum to 1
        total = sum(preds) or 1.0
        normalized = {MODEL_LABELS[i].lower(): float(preds[i]) / total for i in range(len(preds))}
        
        dominant = MODEL_LABELS[np.argmax(preds)].lower()
        confidence = normalized.get(dominant, 0.0)

        return {
            "emotion": dominant,
            "confidence": round(confidence, 3),
            "all_scores": {k: round(v, 3) for k, v in normalized.items()},
        }

    except Exception as e:
        logger.error(f"Detector failed: {e}")
        return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}
