"""
Sentiment analysis using TextBlob for emotional negativity detection.
"""
from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes emotional negativity using TextBlob.
    Returns:
        dict: {
            "sentiment": "positive" | "neutral" | "negative",
            "score": float (-1.0 to 1.0)
        }
    """
    if not text.strip():
        return {"sentiment": "neutral", "score": 0.0}
        
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1.0 (negative) to 1.0 (positive)
    
    if polarity <= -0.3:
        sentiment_label = "negative"
    elif polarity >= 0.3:
        sentiment_label = "positive"
    else:
        sentiment_label = "neutral"
        
    return {
        "sentiment": sentiment_label,
        "score": float(polarity)
    }
