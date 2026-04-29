"""Rule-based safety checks for critical mental health language."""

from __future__ import annotations

from src.preprocessing import clean_text


CRITICAL_KEYWORDS = [
    "kill myself",
    "cant go on",
    "can't go on",
    "end it all",
    "want to die",
]


def check_critical_keywords(text: str) -> tuple[bool, list[str]]:
    """Return whether critical phrases appear and which phrases matched."""
    normalized = clean_text(text)
    matched = []

    for keyword in CRITICAL_KEYWORDS:
        normalized_keyword = clean_text(keyword)
        if normalized_keyword in normalized:
            matched.append(keyword)

    return bool(matched), matched
