"""
Constants: mood labels, emoji maps, color maps, and prompt templates for Mitra.
"""

# ── Mood & Emotion Definitions ─────────────────────────────────────────────────

EMOTIONS = ["happy", "sad", "angry", "fear", "disgust", "surprise", "neutral"]

EMOTION_EMOJI = {
    "happy":    "😊",
    "sad":      "😢",
    "angry":    "😠",
    "fear":     "😨",
    "disgust":  "🤢",
    "surprise": "😲",
    "neutral":  "😐",
}

EMOTION_COLOR = {
    "happy":    "#4CAF82",   # calm green
    "sad":      "#5C85D6",   # soft blue
    "angry":    "#E05C5C",   # soft red
    "fear":     "#9B59B6",   # purple
    "disgust":  "#E67E22",   # amber-orange
    "surprise": "#F5A623",   # warm amber
    "neutral":  "#95A5A6",   # grey
}

MOOD_SCORE_LABELS = {
    1:  "Very Low 💔",
    2:  "Low 😞",
    3:  "Below Average 😕",
    4:  "Fair 😐",
    5:  "Okay 🙂",
    6:  "Good 😊",
    7:  "Pretty Good 😄",
    8:  "Great 🌟",
    9:  "Excellent 🎉",
    10: "Amazing 🌈",
}

STRESS_COLORS = {
    "low":    "#4CAF82",
    "medium": "#F5A623",
    "high":   "#E05C5C",
}

ENERGY_OPTIONS = ["Low", "Medium", "High"]

# ── Journal Writing Prompts ────────────────────────────────────────────────────

JOURNAL_PROMPTS = {
    "happy":   "You seem to be in a good space today! What's been bringing you joy lately?",
    "sad":     "It's okay to not be okay. What's been weighing on your heart?",
    "angry":   "Anger often points to something that matters. What's been frustrating you?",
    "fear":    "What's been making you feel unsettled? Let's explore it together.",
    "neutral": "How has your day been unfolding? Walk me through it.",
    "surprise":"Something unexpected happened? Tell me all about it.",
    "disgust": "Something feels off. What's been bothering you?",
}

# ── Wellness Categories ────────────────────────────────────────────────────────

WELLNESS_CATEGORIES = {
    "breathing": {"icon": "🌬️", "label": "Breathing Exercise"},
    "movement":  {"icon": "🚶", "label": "Movement & Body"},
    "cognitive": {"icon": "🧠", "label": "Cognitive Reframing"},
    "sleep":     {"icon": "😴", "label": "Sleep Hygiene"},
    "social":    {"icon": "🤝", "label": "Social Connection"},
    "creative":  {"icon": "🎨", "label": "Creative Expression"},
}

# ── AI Prompt Templates ────────────────────────────────────────────────────────

CHECKIN_SYSTEM_PROMPT = """You are Mitra, a warm, emotionally intelligent mental wellness companion.
You are NOT a therapist. You are a supportive friend who listens without judgment.
Keep responses to 3–4 sentences. Be genuine, not clinical.
Always end with one open-ended question to encourage reflection.
Never use toxic positivity. Acknowledge difficult emotions first."""

CHECKIN_USER_PROMPT = """User name: {name}
Detected facial mood: {detected_mood} (confidence: {confidence}%)
Self-reported mood score: {mood_score}/10
Energy level: {energy_level}
Stress level derived: {stress_level}
Short note: "{notes}"
Previous check-in mood (yesterday): {yesterday_mood}
Current time: {time_of_day}

Please respond as Mitra with a personalized check-in message."""

JOURNAL_SYSTEM_PROMPT = """You are Mitra, a compassionate journal companion.
Analyze the journal entry and return a JSON object with:
{{
  "sentiment": "positive|neutral|negative",
  "themes": ["theme1", "theme2"],
  "reflection": "2-3 sentence empathetic response acknowledging what was shared and gently offering one reframe or encouragement"
}}
Return ONLY valid JSON. No preamble. No markdown fences."""

JOURNAL_USER_PROMPT = """Journal entry: "{journal_text}"
User's mood today: {mood_label}"""

WELLNESS_SYSTEM_PROMPT = """You are Mitra's wellness engine. Generate exactly 3 personalized wellness suggestions.
Return a JSON array:
[
  {{
    "category": "breathing|movement|cognitive|sleep|social|creative",
    "title": "Short title",
    "description": "2 sentences explaining the activity",
    "why_now": "1 sentence connecting it to their current mood"
  }}
]
Return ONLY valid JSON. No preamble. No markdown fences."""

WELLNESS_USER_PROMPT = """Mood score: {mood_score}/10
Detected emotion: {detected_mood}
Stress level: {stress_level}
Journal themes today: {themes}
Time of day: {time_of_day}"""

JOURNAL_WRITING_PROMPT_SYSTEM = """Generate one warm, open-ended journaling prompt for a user feeling {detected_mood}.
Max 20 words. Start with an empathetic acknowledgment. Return only the prompt text, no extra formatting."""

# ── Crisis Resources ────────────────────────────────────────────────────────────

CRISIS_RESOURCES = [
    {"name": "iCall India",              "number": "9152987821",    "hours": "Mon–Sat, 8am–10pm"},
    {"name": "Vandrevala Foundation",    "number": "1860-2662-345", "hours": "24/7"},
    {"name": "NIMHANS Helpline",         "number": "080-46110007",  "hours": "24/7"},
    {"name": "Snehi",                    "number": "044-24640050",  "hours": "Mon–Sat, 8am–10pm"},
]

# ── Color Palette ──────────────────────────────────────────────────────────────

PALETTE = {
    "primary":     "#1B6CA8",
    "calm_green":  "#4CAF82",
    "warm_amber":  "#F5A623",
    "soft_red":    "#E05C5C",
    "background":  "#F0F4F8",
    "card":        "#FFFFFF",
    "dark_bg":     "#0F1C2E",
    "text_primary":"#1A202C",
    "text_muted":  "#718096",
}
