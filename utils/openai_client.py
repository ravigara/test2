"""
Robust OpenAI client with multi-key round-robin rotation.

Key design decisions:
- Loads ALL available keys upfront (NO pre-validation — quota-exhausted keys
  also fail the models.list() call, which incorrectly removes them).
- Rotates to the next key only when a live API call fails with a retryable
  error (quota exhaustion / rate limit / auth error).
- Singleton stored in st.session_state so it persists across Streamlit reruns
  but resets on new sessions (when the server restarts).
- Marks exhausted keys per-session so we don't retry them again in the same session.
"""

import os
import logging
from openai import OpenAI, RateLimitError, AuthenticationError, APIStatusError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Names to scan in .env, in priority order
_KEY_ENV_NAMES = [
    "OPENAI_API_KEY",
    "OPENAI_API_KEY1",
    "OPENAI_API_KEY2",
    "OPENAI_API_KEY3",
    "OPENAI_API_KEY4",
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
    if isinstance(e, (RateLimitError, AuthenticationError)):
        return True
    if isinstance(e, APIStatusError) and e.status_code in (429, 401, 403):
        return True
    err_lower = str(e).lower()
    return any(kw in err_lower for kw in (
        "insufficient_quota", "rate_limit_exceeded",
        "exceeded your current quota", "invalid_api_key",
    ))


class RobustOpenAI:
    """
    Multi-key OpenAI client that automatically rotates through available keys
    when any key hits its quota or rate limit.
    """

    def __init__(self):
        all_keys = _load_all_keys()
        if not all_keys:
            raise EnvironmentError(
                "No OpenAI API keys found. Set OPENAI_API_KEY (and optionally "
                "OPENAI_API_KEY1 … OPENAI_API_KEY4) in your .env file."
            )

        # All keys available — no pre-validation
        self.keys: list[str] = all_keys
        self.exhausted: set[int] = set()   # indices of keys that have failed this session
        self.current_key_idx: int = 0
        self._build_client()

        logger.info(f"[RobustOpenAI] Initialized with {len(self.keys)} key(s). "
                    f"Starting with key #1 (ending …{self.keys[0][-6:]})")

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _build_client(self):
        self.client = OpenAI(api_key=self.keys[self.current_key_idx], timeout=30.0)

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
                    f"[RobustOpenAI] Switched to key #{idx + 1} "
                    f"(ending …{self.keys[idx][-6:]})"
                )
                return True
        logger.error("[RobustOpenAI] All API keys are exhausted for this session.")
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

    def chat_completion(self, **kwargs):
        """
        Non-streaming chat completion.
        Retries with successive keys on quota / rate-limit errors.
        """
        last_exc = None
        for _ in range(len(self.keys)):
            try:
                return self.client.chat.completions.create(**kwargs)
            except Exception as e:
                last_exc = e
                if _is_quota_error(e):
                    logger.warning(
                        f"[RobustOpenAI] chat_completion: {type(e).__name__} on "
                        f"key #{self.current_key_idx + 1}. Trying next key…"
                    )
                    if self._advance_to_next_key():
                        continue          # retry with new key
                    else:
                        break             # all keys exhausted
                raise                     # non-quota error → propagate immediately

        raise EnvironmentError(
            f"All {len(self.keys)} OpenAI API keys are exhausted for this session. "
            f"Last error: {last_exc}"
        )

    def chat_stream(self, **kwargs):
        """
        Streaming chat completion.
        Eagerly collects chunks per key attempt so quota errors are caught
        before any text is yielded to the caller.
        """
        kwargs["stream"] = True
        last_exc = None

        for attempt in range(len(self.keys)):
            try:
                response = self.client.chat.completions.create(**kwargs)
                # Collect all chunks for this key; raises if key is quota-exhausted
                chunks: list[str] = []
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        chunks.append(delta.content)
                # Success — yield collected text
                yield from chunks
                return

            except Exception as e:
                last_exc = e
                if _is_quota_error(e):
                    logger.warning(
                        f"[RobustOpenAI] chat_stream: {type(e).__name__} on "
                        f"key #{self.current_key_idx + 1}. Trying next key…"
                    )
                    if self._advance_to_next_key():
                        continue          # retry with new key
                    else:
                        break             # all keys exhausted
                raise                     # non-quota error → propagate

        raise EnvironmentError(
            f"All {len(self.keys)} OpenAI API keys are exhausted during streaming. "
            f"Last error: {last_exc}"
        )


# ── Singleton accessor ─────────────────────────────────────────────────────────

def get_robust_client() -> RobustOpenAI:
    """
    Returns the session-scoped RobustOpenAI singleton from st.session_state.
    This ensures the key rotation state persists across Streamlit reruns
    but resets when the browser session ends.
    """
    import streamlit as st
    if "_robust_openai" not in st.session_state:
        st.session_state["_robust_openai"] = RobustOpenAI()
    return st.session_state["_robust_openai"]
