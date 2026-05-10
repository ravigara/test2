"""
Wellness recommendation engine based on mood/risk.
"""

def get_recommendations(mood: str, risk_level: str) -> list:
    """
    Returns a list of actionable wellness tips.
    """
    tips = []
    
    if risk_level in ["Moderate Concern", "High Risk"]:
        tips.append("Try the 4-7-8 breathing method: Inhale for 4s, hold for 7s, exhale for 8s.")
        tips.append("Reach out to someone you trust just to hear their voice.")
        tips.append("Drink a glass of cold water to help ground your physical senses.")
        return tips
        
    mood = mood.lower()
    
    if mood == "sad":
        tips.append("Listen to a comforting, nostalgic playlist.")
        tips.append("Wrap yourself in a warm blanket and have a warm drink.")
        tips.append("Journal your thoughts—getting them out can lighten the load.")
    elif mood == "angry":
        tips.append("Do a quick physical activity, like a brisk walk or 10 jumping jacks.")
        tips.append("Try writing down what made you angry, then tear up the paper.")
        tips.append("Splash cold water on your face.")
    elif mood in ["anxious", "fear", "stressed"]:
        tips.append("Use the 5-4-3-2-1 grounding technique to focus on your surroundings.")
        tips.append("Step outside for just 2 minutes of fresh air.")
        tips.append("Do a gentle neck and shoulder stretch.")
    else:
        tips.append("Take a moment to appreciate one good thing that happened today.")
        tips.append("Stay hydrated and take a short walk.")
        
    return tips
