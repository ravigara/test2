"""
Sentiment analysis using TextBlob.
"""

from textblob import TextBlob

def analyze_sentiment(text: str) -> float:
    """
    Returns a sentiment polarity score between -1.0 (very negative) and 1.0 (very positive).
    """
    if not text or not text.strip():
        return 0.0
    blob = TextBlob(text)
    return blob.sentiment.polarity
