"""
Keyword-based crisis detector with weighted categorization.
"""
import re

LOW_RISK_KEYWORDS = [
    "stressed", "anxious", "lonely", "tired", "overwhelmed", "exhausted",
    "sad", "nervous", "uneasy"
]

MEDIUM_RISK_KEYWORDS = [
    "hopeless", "worthless", "empty", "giving up", "numb", "nobody cares",
    "can't do this", "what's the point", "failure", "trapped"
]

HIGH_RISK_KEYWORDS = [
    "suicide", "kill myself", "hurt myself", "self harm", "end my life",
    "want to disappear", "want to die", "better off dead", "end it all"
]

def scan_text(text: str) -> dict:
    """
    Scans text for severity keywords case-insensitively.
    Returns categorized hits and a base keyword score.
    """
    text_lower = text.lower()
    score = 0
    has_high = False
    has_medium = False
    
    # 60 points for high risk
    for kw in HIGH_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 60
            has_high = True
            
    # 30 points for medium risk
    for kw in MEDIUM_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 30
            has_medium = True
            
    # 10 points for low risk
    for kw in LOW_RISK_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            score += 10
            
    return {
        "score": score,
        "detected_high_risk": has_high,
        "detected_medium_risk": has_medium
    }
