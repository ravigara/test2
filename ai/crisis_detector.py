"""
Keyword-based crisis detector.
"""
import re

LOW_RISK_KEYWORDS = [
    "stressed", "tired", "lonely", "anxious", "overwhelmed", "exhausted"
]

MEDIUM_RISK_KEYWORDS = [
    "hopeless", "worthless", "numb", "giving up", "empty", "nobody cares"
]

HIGH_RISK_KEYWORDS = [
    "suicide", "kill myself", "end my life", "hurt myself", "self harm", "want to disappear"
]

def scan_text(text: str) -> dict:
    """
    Scans the text for risk keywords and returns a severity score.
    Returns:
        dict with keys: 'score' (int), 'detected_high_risk' (bool), 'detected_medium_risk' (bool)
    """
    text_lower = text.lower()
    score = 0
    has_high = False
    has_medium = False
    
    for kw in HIGH_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 60
            has_high = True
            
    for kw in MEDIUM_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 30
            has_medium = True
            
    for kw in LOW_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 10
            
    return {
        "score": score,
        "detected_high_risk": has_high,
        "detected_medium_risk": has_medium
    }
