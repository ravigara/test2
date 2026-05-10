"""
Robust Gemini client with multi-key round-robin rotation.

Key design decisions:
- Loads ALL available keys upfront from GEMINI_API_KEY1 ... GEMINI_API_KEY4.
- Rotates to the next key only when a live API call fails with a retryable
  error (quota exhaustion / rate limit / auth error).
- Singleton stored in st.session_state so it persists across Streamlit reruns.
"""

import os
import logging
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Names to scan in .env, in priority order
_KEY_ENV_NAMES = [
    "GEMINI_API_KEY1",
    "GEMINI_API_KEY2",
    "GEMINI_API_KEY3",
    "GEMINI_API_KEY4",
    "GEMINI_API_KEY5",
    "GEMINI_API_KEY6",
]


def _load_all_keys() -> list[str]:
    """Reads all keys from environment. Returns de-duplicated list."""
    keys = []
    for name in _KEY_ENV_NAMES:
        val = os.environ.get(name, "").strip()
        if val and val not in keys:
            keys.append(val)
    return keys


def _is_quota_error(e: Exception) -> bool:
    """Returns True for any error that should trigger a key switch."""
    if isinstance(e, APIError):
        # 429 Resource Exhausted, 403 Permission Denied, 401 Unauthorized
        if e.code in (429, 403, 401):
            return True
    
    err_lower = str(e).lower()
    return any(kw in err_lower for kw in (
        "quota", "rate limit", "exhausted", "invalid api key",
        "429", "403", "401"
    ))


class RobustGemini:
    """
    Multi-key Gemini client that automatically rotates through available keys
    when any key hits its quota or rate limit.
    """

    def __init__(self):
        all_keys = _load_all_keys()
        if not all_keys:
            raise EnvironmentError(
                "No Gemini API keys found. Set GEMINI_API_KEY1 ... GEMINI_API_KEY4 "
                "in your .env file."
            )

        self.keys: list[str] = all_keys
        self.exhausted: set[int] = set()
        self.current_key_idx: int = 0
        self._build_client()

        logger.info(f"[RobustGemini] Initialized with {len(self.keys)} key(s). "
                    f"Starting with key #1 (ending …{self.keys[0][-6:]})")

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _build_client(self):
        self.client = genai.Client(api_key=self.keys[self.current_key_idx])

    def _advance_to_next_key(self) -> bool:
        """
        Marks current key as exhausted and advances to the next non-exhausted key.
        Returns True if a usable key was found, False if all are exhausted.
        """
        self.exhausted.add(self.current_key_idx)
        for idx in range(len(self.keys)):
            if idx not in self.exhausted:
                self.current_key_idx = idx
                self._build_client()
                logger.warning(
                    f"[RobustGemini] Switched to key #{idx + 1} "
                    f"(ending …{self.keys[idx][-6:]})"
                )
                return True
        logger.error("[RobustGemini] All API keys are exhausted for this session.")
        return False

    # ── Public properties ──────────────────────────────────────────────────────

    @property
    def total_keys(self) -> int:
        return len(self.keys)

    @property
    def active_key_number(self) -> int:
        """1-indexed number of the currently active key."""
        return self.current_key_idx + 1

    @property
    def remaining_keys(self) -> int:
        return len(self.keys) - len(self.exhausted)

    # ── API call methods ───────────────────────────────────────────────────────

    def generate_content(self, model: str, contents: list, config: dict = None):
        """
        Non-streaming generation.
        Retries with successive keys on quota / rate-limit errors.
        """
        last_exc = None
        for _ in range(len(self.keys)):
            try:
                if config:
                    gen_config = genai.types.GenerateContentConfig(**config)
                    return self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=gen_config
                    )
                else:
                    return self.client.models.generate_content(
                        model=model,
                        contents=contents
                    )
            except Exception as e:
                last_exc = e
                if _is_quota_error(e):
                    logger.warning(
                        f"[RobustGemini] generate_content: {type(e).__name__} on "
                        f"key #{self.current_key_idx + 1}. Trying next key…"
                    )
                    if self._advance_to_next_key():
                        continue
                    else:
                        break
                raise

        raise EnvironmentError(
            f"All {len(self.keys)} Gemini API keys are exhausted for this session. "
            f"Last error: {last_exc}"
        )

    def generate_content_stream(self, model: str, contents: list, config: dict = None):
        """
        Streaming generation.
        Eagerly collects chunks per key attempt so quota errors are caught
        before any text is yielded to the caller.
        """
        last_exc = None

        for attempt in range(len(self.keys)):
            try:
                if config:
                    gen_config = genai.types.GenerateContentConfig(**config)
                    response_stream = self.client.models.generate_content_stream(
                        model=model,
                        contents=contents,
                        config=gen_config
                    )
                else:
                    response_stream = self.client.models.generate_content_stream(
                        model=model,
                        contents=contents
                    )
                
                # Collect chunks
                chunks = []
                for chunk in response_stream:
                    if chunk.text:
                        chunks.append(chunk.text)
                
                yield from chunks
                return

            except Exception as e:
                last_exc = e
                if _is_quota_error(e):
                    logger.warning(
                        f"[RobustGemini] generate_content_stream: {type(e).__name__} on "
                        f"key #{self.current_key_idx + 1}. Trying next key…"
                    )
                    if self._advance_to_next_key():
                        continue
                    else:
                        break
                raise

        raise EnvironmentError(
            f"All {len(self.keys)} Gemini API keys are exhausted during streaming. "
            f"Last error: {last_exc}"
        )


# ── Singleton accessor ─────────────────────────────────────────────────────────

def get_robust_client() -> RobustGemini:
    """
    Returns the session-scoped RobustGemini singleton from st.session_state.
    """
    import streamlit as st
    if "_robust_gemini" not in st.session_state:
        st.session_state["_robust_gemini"] = RobustGemini()
    return st.session_state["_robust_gemini"]
