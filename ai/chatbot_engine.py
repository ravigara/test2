"""
Orchestrates the AI Chatbot interaction, utilizing OpenAI's API with automatic key fallback.
"""

from dotenv import load_dotenv
from ai.mood_adapter import get_mood_adaptation
from utils.openai_client import get_robust_client

load_dotenv()


def generate_chat_response_stream(messages: list, current_mood: str):
    """
    Generator that streams the chatbot response.
    Automatically falls back to the next API key if quota is exhausted.
    """
    robust_client = get_robust_client()

    system_prompt = get_mood_adaptation(current_mood)
    api_messages = [{"role": "system", "content": system_prompt}]

    # Keep last 10 messages for context
    for msg in messages[-10:]:
        api_messages.append(msg)

    try:
        yield from robust_client.chat_stream(
            model="gpt-4o-mini",
            messages=api_messages,
            temperature=0.75,
            max_tokens=300,
        )
    except EnvironmentError as e:
        yield f"⚠️ All API keys are exhausted. Please check your quota. ({e})"
    except Exception as e:
        yield f"⚠️ AI service unavailable. Error: {e}"
