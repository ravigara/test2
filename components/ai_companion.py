"""
OpenAI API wrapper for all Mitra AI interactions.
Uses the robust multi-key client with automatic fallback on quota/rate limit errors.
Compatible with openai SDK v2.x
"""

import os
import json
import logging
from dotenv import load_dotenv
from utils.gemini_client import get_robust_client

from utils.constants import (
    CHECKIN_SYSTEM_PROMPT, CHECKIN_USER_PROMPT,
    JOURNAL_SYSTEM_PROMPT, JOURNAL_USER_PROMPT,
    WELLNESS_SYSTEM_PROMPT, WELLNESS_USER_PROMPT,
    JOURNAL_WRITING_PROMPT_SYSTEM,
)

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def get_checkin_response(context: dict) -> str:
    """Call OpenAI for a personalized check-in message."""
    user_msg = CHECKIN_USER_PROMPT.format(**context)
    try:
        client = get_robust_client()
        response = client.generate_content(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": CHECKIN_SYSTEM_PROMPT,
                "temperature": 0.85,
                "max_output_tokens": 300,
            }
        )
        return response.text.strip()
    except EnvironmentError:
        raise
    except Exception as e:
        logger.error(f"Gemini check-in call failed: {e}")
        return (
            "I'm here with you. 💙 It sounds like today has been a journey. "
            "Whatever you're feeling right now is completely valid. "
            "How would you like to spend a few minutes taking care of yourself today?"
        )


def get_checkin_response_stream(context: dict):
    """Generator: yields text chunks for Streamlit's st.write_stream()."""
    user_msg = CHECKIN_USER_PROMPT.format(**context)
    try:
        client = get_robust_client()
        yield from client.generate_content_stream(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": CHECKIN_SYSTEM_PROMPT,
                "temperature": 0.85,
                "max_output_tokens": 300,
            }
        )
    except EnvironmentError as e:
        raise
    except Exception as e:
        logger.error(f"Gemini stream failed: {e}")
        yield (
            "I'm here with you. 💙 Whatever you're feeling right now is valid. "
            "What would help you most right now?"
        )


def analyze_journal(journal_text: str, mood: str) -> dict:
    """Call OpenAI to analyze a journal entry. Returns: {sentiment, themes[], reflection}"""
    user_msg = JOURNAL_USER_PROMPT.format(journal_text=journal_text, mood_label=mood)
    try:
        client = get_robust_client()
        response = client.generate_content(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": JOURNAL_SYSTEM_PROMPT,
                "temperature": 0.7,
                "max_output_tokens": 400,
                "response_mime_type": "application/json"
            }
        )
        raw = response.text.strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in journal analysis: {e}")
        return {
            "sentiment": "neutral",
            "themes": ["personal"],
            "reflection": "Thank you for sharing. Every word you write is a step toward understanding yourself better. 💙",
        }
    except EnvironmentError:
        raise
    except Exception as e:
        logger.error(f"Gemini journal analysis failed: {e}")
        return {
            "sentiment": "neutral",
            "themes": [],
            "reflection": "Thank you for sharing. I'm here with you. 💙",
        }


def get_wellness_suggestions(context: dict) -> list[dict]:
    """Call OpenAI to generate 3 personalized wellness suggestions."""
    user_msg = WELLNESS_USER_PROMPT.format(**context)
    try:
        client = get_robust_client()
        response = client.generate_content(
            model=MODEL,
            contents=user_msg,
            config={
                "system_instruction": WELLNESS_SYSTEM_PROMPT,
                "temperature": 0.8,
                "max_output_tokens": 600,
            }
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:]) if lines[-1].strip() == "```" else "\n".join(lines[1:-1])
        result = json.loads(raw)
        if isinstance(result, list):
            return result
        return result.get("suggestions", [])
    except Exception as e:
        logger.error(f"Gemini wellness suggestions failed: {e}")
        return [
            {
                "category": "breathing",
                "title": "4-7-8 Breathing",
                "description": "Inhale for 4 counts, hold for 7, exhale for 8. Activates your parasympathetic nervous system.",
                "why_now": "Great for releasing tension and resetting your nervous system.",
            },
            {
                "category": "movement",
                "title": "5-Minute Walk",
                "description": "Step outside for a brief walk. Fresh air and movement boost mood-lifting endorphins.",
                "why_now": "Movement is one of the most effective natural mood elevators.",
            },
            {
                "category": "cognitive",
                "title": "Gratitude Snapshot",
                "description": "Write down 3 small things you noticed today — a warm drink, a smile, a moment of quiet.",
                "why_now": "Shifting focus to positives rewires how we perceive our day.",
            },
        ]


def get_journal_prompt(emotion: str) -> str:
    """Call OpenAI for a personalized journaling prompt based on emotion."""
    system = JOURNAL_WRITING_PROMPT_SYSTEM.format(detected_mood=emotion)
    try:
        client = get_robust_client()
        response = client.generate_content(
            model=MODEL,
            contents="Generate the journaling prompt.",
            config={
                "system_instruction": system,
                "temperature": 0.9,
                "max_output_tokens": 60,
            }
        )
        return response.text.strip()
    except EnvironmentError:
        raise
    except Exception as e:
        logger.error(f"Gemini journal prompt failed: {e}")
        from utils.constants import JOURNAL_PROMPTS
        return JOURNAL_PROMPTS.get(emotion, JOURNAL_PROMPTS["neutral"])
