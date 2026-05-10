"""
Orchestrates the AI Chatbot interaction, utilizing Google Gemini with automatic key fallback.
"""

from dotenv import load_dotenv
from ai.mood_adapter import get_mood_adaptation
from utils.gemini_client import get_robust_client
from ai.safety_prompt_manager import get_safety_instruction

load_dotenv()


def generate_chat_response_stream(messages: list, current_mood: str, risk_level: str = "Normal"):
    """
    Generator that streams the chatbot response.
    Automatically falls back to the next API key if quota is exhausted.
    """
    robust_client = get_robust_client()

    base_mood_prompt = get_mood_adaptation(current_mood)
    safety_prompt = get_safety_instruction(risk_level)
    
    system_prompt = f"{safety_prompt}\n\n[MOOD CONTEXT]\n{base_mood_prompt}"
    
    # Convert messages from {"role": "user"/"assistant", "content": "..."}
    # to Gemini format {"role": "user"/"model", "parts": [{"text": "..."}]}
    gemini_messages = []
    # Keep last 10 messages for context
    for msg in messages[-10:]:
        role = "model" if msg["role"] == "assistant" else "user"
        gemini_messages.append(
            {"role": role, "parts": [{"text": msg["content"]}]}
        )

    config = {
        "temperature": 0.75,
        "max_output_tokens": 1500,
        "system_instruction": system_prompt
    }

    try:
        yield from robust_client.generate_content_stream(
            model="gemini-2.5-flash",
            contents=gemini_messages,
            config=config,
        )
    except EnvironmentError as e:
        yield f"⚠️ All API keys are exhausted. Please check your quota. ({e})"
    except Exception as e:
        yield f"⚠️ AI service unavailable. Error: {e}"
