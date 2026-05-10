"""
Helper utilities: date/time, greeting, streak formatting, user name.
"""

from datetime import datetime, date
from database.db import get_user_profile, get_streak


def get_time_of_day() -> str:
    """Return a time-of-day label."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def get_greeting(name: str = "") -> str:
    """Return a warm, time-aware greeting."""
    tod = get_time_of_day()
    icons = {
        "morning":   "☀️",
        "afternoon": "🌤️",
        "evening":   "🌙",
        "night":     "✨",
    }
    icon = icons.get(tod, "🌱")
    greetings = {
        "morning":   f"Good morning{', ' + name if name else ''}! {icon}",
        "afternoon": f"Good afternoon{', ' + name if name else ''}! {icon}",
        "evening":   f"Good evening{', ' + name if name else ''}! {icon}",
        "night":     f"Hey there{', ' + name if name else ''}! {icon}",
    }
    return greetings.get(tod, f"Welcome{', ' + name if name else ''}! 🌱")


def load_user_name() -> str:
    """Load the user's name from the profile DB."""
    return get_user_profile("name") or ""


def format_streak(streak: int) -> str:
    """Return a formatted streak badge string."""
    if streak == 0:
        return "Start your streak today! 🌱"
    elif streak == 1:
        return "🔥 1-day streak!"
    elif streak < 7:
        return f"🔥 {streak}-day streak! Keep going!"
    elif streak < 30:
        return f"🔥 {streak}-day streak! Amazing consistency!"
    else:
        return f"🔥 {streak}-day streak! You're a wellness champion! 💙"


def format_date(d: str | date) -> str:
    """Return a human-readable date string."""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except Exception:
            return d
    today = date.today()
    if d == today:
        return "Today"
    elif d == today.replace(day=today.day - 1):
        return "Yesterday"
    return d.strftime("%B %d, %Y")


def derive_stress_level(mood_score: int, detected_mood: str) -> str:
    """Derive stress level from mood score and detected emotion."""
    if detected_mood in ["angry", "fear", "disgust"] or mood_score <= 3:
        return "high"
    elif detected_mood in ["sad", "neutral"] or mood_score <= 6:
        return "medium"
    else:
        return "low"


def mood_score_to_label(score: int) -> str:
    """Map numeric mood score to an emotion label."""
    if score >= 8:
        return "happy"
    elif score >= 6:
        return "neutral"
    elif score >= 4:
        return "sad"
    else:
        return "fear"


def get_yesterday_mood() -> str:
    """Fetch yesterday's detected mood from the DB."""
    from database.db import get_checkins
    from datetime import timedelta

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    records = get_checkins(days=2)
    for r in records:
        if r.get("date") == yesterday:
            return r.get("detected_mood", "unknown")
    return "unknown"
