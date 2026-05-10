"""
Aggregates sentiment, keywords, and mood into a final risk score.
"""

from ai.sentiment_engine import analyze_sentiment
from ai.crisis_detector import scan_text

def calculate_risk(text: str, detected_mood: str = "neutral", consecutive_distress: int = 0) -> dict:
    """
    Calculates final risk score (0-100) and risk level.
    """
    # 1. Keyword Score
    scan_result = scan_text(text)
    score = scan_result["score"]
    
    # 2. Sentiment Score
    sentiment = analyze_sentiment(text)
    if sentiment < -0.6:
        score += 20
    elif sentiment < -0.3:
        score += 10
        
    # 3. Facial Emotion Score
    if detected_mood in ["sad", "fear", "angry"]:
        score += 10
        
    # 4. Repeated Distress
    if consecutive_distress > 0:
        score += min(20, consecutive_distress * 10)
        
    # Cap score at 100
    final_score = min(100, score)
    
    # Classify Risk Level
    if final_score <= 30:
        level = "Normal"
    elif final_score <= 60:
        level = "Mild Concern"
    elif final_score <= 80:
        level = "Moderate Concern"
    else:
        level = "High Risk"
        
    return {
        "risk_score": final_score,
        "risk_level": level,
        "sentiment": sentiment,
        "has_high_risk_keywords": scan_result["detected_high_risk"],
        "has_medium_risk_keywords": scan_result["detected_medium_risk"]
    }
