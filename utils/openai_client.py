"""
Robust OpenAI client with multi-key rotation, quota pre-validation, and retry logic.
Handles: insufficient_quota, rate limits, auth errors, and network timeouts.
The singleton is stored in Streamlit session_state so Streamlit doesn't reset it.
"""
import os
import logging
import httpx
from openai import OpenAI, RateLimitError, AuthenticationError, APIStatusError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_QUOTA_ERROR_CODES = {"insufficient_quota", "rate_limit_exceeded"}
_KEY_NAMES = ["OPENAI_API_KEY", "OPENAI_API_KEY1", "OPENAI_API_KEY2", "OPENAI_API_KEY3", "OPENAI_API_KEY4"]


def _load_keys() -> list[str]:
    keys = []
    for name in _KEY_NAMES:
        val = os.environ.get(name, "").strip()
        if val and val not in keys:
            keys.append(val)
    return keys


def _is_retryable(e: Exception) -> bool:
    """Returns True if the error warrants switching to the next key."""
    if isinstance(e, (RateLimitError, AuthenticationError)):
        return True
    if isinstance(e, APIStatusError) and e.status_code in (429, 401, 403):
        return True
    # Check error body text
    err_str = str(e).lower()
    if any(code in err_str for code in _QUOTA_ERROR_CODES):
        return True
    return False


def validate_key(api_key: str) -> bool:
    """
    Fast lightweight check: tries a minimal API call to verify the key has quota.
    Uses the models list endpoint (cheap, token-free).
    """
    try:
        client = OpenAI(api_key=api_key, timeout=5.0)
        # List models is extremely cheap and confirms auth + quota status
        client.models.list()
        return True
    except Exception:
        return False


class RobustOpenAI:
    def __init__(self):
        all_keys = _load_keys()
        if not all_keys:
            raise EnvironmentError("No OPENAI_API_KEY found in environment variables.")

        # Pre-validate all keys at startup, only keep working ones
        self.keys = []
        for key in all_keys:
            if validate_key(key):
                self.keys.append(key)
                logger.info(f"[RobustOpenAI] Key ending ...{key[-6:]} is VALID")
            else:
                logger.warning(f"[RobustOpenAI] Key ending ...{key[-6:]} FAILED validation — skipping")

        if not self.keys:
            # Fall back to all keys if none pass validation (e.g., models endpoint blocked)
            logger.warning("[RobustOpenAI] All keys failed pre-validation. Using all keys with runtime fallback.")
            self.keys = all_keys

        self.current_key_idx = 0
        self._build_client()

    def _build_client(self):
        self.client = OpenAI(api_key=self.keys[self.current_key_idx], timeout=30.0)

    def _next_key(self) -> bool:
        """Advance to next available key. Returns True if switched, False if exhausted."""
        # Mark current as exhausted and try next
        start_idx = self.current_key_idx
        while self.current_key_idx < len(self.keys) - 1:
            self.current_key_idx += 1
            self._build_client()
            logger.warning(f"[RobustOpenAI] Switched to key #{self.current_key_idx + 1} (ending ...{self.keys[self.current_key_idx][-6:]})")
            return True
        return False

    def chat_completion(self, **kwargs) -> object:
        """Non-streaming completion with full key rotation on any quota/auth error."""
        last_exc = None
        for _ in range(len(self.keys)):
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as e:
                last_exc = e
                if _is_retryable(e):
                    logger.warning(f"[RobustOpenAI] chat_completion error: {type(e).__name__}. Trying next key...")
                    if self._next_key():
                        continue
                raise e
        raise EnvironmentError(f"All {len(self.keys)} API keys exhausted. Last error: {last_exc}")

    def chat_stream(self, **kwargs):
        """
        Streaming completion with full key rotation.
        Collects all chunks eagerly per key attempt to surface errors early.
        Yields text strings once a successful key is found.
        """
        kwargs.setdefault("stream", True)
        last_exc = None

        for attempt_key_idx in range(len(self.keys)):
            # Make sure we're on the right key
            if self.current_key_idx != attempt_key_idx:
                self.current_key_idx = attempt_key_idx
                self._build_client()
            try:
                response = self.client.chat.completions.create(**kwargs)
                chunks = []
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        chunks.append(delta.content)
                yield from chunks
                return  # Success — done
            except Exception as e:
                last_exc = e
                if _is_retryable(e):
                    logger.warning(f"[RobustOpenAI] chat_stream error on key #{attempt_key_idx + 1}: {type(e).__name__}. Trying next key...")
                    continue
                raise e

        raise EnvironmentError(f"All {len(self.keys)} API keys exhausted during streaming. Last error: {last_exc}")


def get_robust_client() -> RobustOpenAI:
    """
    Returns a singleton RobustOpenAI stored in Streamlit session_state
    so it survives re-runs but is re-created on fresh sessions.
    """
    import streamlit as st
    if "_robust_openai" not in st.session_state:
        st.session_state["_robust_openai"] = RobustOpenAI()
    return st.session_state["_robust_openai"]
