"""
Journal sentiment and theme analyzer.
Thin wrapper over ai_companion.analyze_journal with caching.
"""

import streamlit as st
from components.ai_companion import analyze_journal


@st.cache_data(ttl=300, show_spinner=False)
def analyze_journal_cached(journal_text: str, mood: str) -> dict:
    """Cached journal analysis to avoid redundant API calls within a session."""
    return analyze_journal(journal_text, mood)
