"""
Aggregates sentiment, keywords, mood, and history into a final Risk Score.
"""

from ai.sentiment_engine import analyze_sentiment
from ai.keyword_engine import scan_text

def classify_risk(score: int) -> str:
    """
    Classifies the numerical score into 4 distinct risk levels.
    """
    if score <= 30:
        return "Normal"
    elif score <= 60:
        return "Mild Concern"
    elif score <= 80:
        return "Moderate Concern"
    else:
        return "High Risk"

def calculate_risk(text: str, detected_mood: str = "neutral", consecutive_distress: int = 0) -> dict:
    """
    Calculates final risk score (0-100) combining textual, facial, and historical data.
    """
    # 1. Keyword Score
    scan_result = scan_text(text)
    score = scan_result["score"]
    
    # 2. Sentiment Score
    sentiment_result = analyze_sentiment(text)
    polarity = sentiment_result["score"]
    
    if polarity <= -0.6:
        score += 20
    elif polarity <= -0.3:
        score += 10
        
    # 3. Facial Emotion Score
    if detected_mood in ["sad", "fear", "angry"]:
        score += 10
        
    # 4. Repeated Distress (Pattern tracking)
    if consecutive_distress > 0:
        # Adds 20 max for repeated distress
        score += min(20, consecutive_distress * 10)
        
    # Cap score at 100
    final_score = min(100, score)
    level = classify_risk(final_score)
        
    return {
        "risk_score": final_score,
        "risk_level": level,
        "sentiment_label": sentiment_result["sentiment"],
        "sentiment_score": polarity,
        "has_high_risk_keywords": scan_result["detected_high_risk"],
        "has_medium_risk_keywords": scan_result["detected_medium_risk"]
    }
