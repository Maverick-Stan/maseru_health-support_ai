"""Input parsing utilities for lightweight intent extraction."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.preprocessing import clean_text


GREETING_TERMS = {"hello", "hi", "hey", "morning", "afternoon", "evening"}
EMOTIONAL_TERMS = {
    "anxious",
    "anxiety",
    "sad",
    "stress",
    "stressed",
    "depressed",
    "lonely",
    "overwhelmed",
    "hopeless",
    "scared",
}
PHYSICAL_TERMS = {
    "pain",
    "fever",
    "cough",
    "headache",
    "chest",
    "breathing",
    "dizzy",
    "bleeding",
    "vomiting",
    "faint",
}


@dataclass(frozen=True)
class ParsedQuery:
    """Small structured representation of a user message."""

    original_text: str
    normalized_text: str
    language: str
    intent: str
    signals: list[str] = field(default_factory=list)


def parse_user_input(message: str, language: str = "English") -> ParsedQuery:
    """Extract a coarse intent and simple signals from a user message."""
    normalized = clean_text(message)
    tokens = set(normalized.split())
    signals: list[str] = []

    if tokens & EMOTIONAL_TERMS:
        signals.append("emotional_wellbeing")

    if tokens & PHYSICAL_TERMS:
        signals.append("physical_symptoms")

    if normalized in GREETING_TERMS or tokens & GREETING_TERMS:
        intent = "greeting"
    elif "physical_symptoms" in signals:
        intent = "health_support"
    elif "emotional_wellbeing" in signals:
        intent = "emotional_support"
    elif normalized:
        intent = "general_support"
    else:
        intent = "empty"

    return ParsedQuery(
        original_text=message.strip(),
        normalized_text=normalized,
        language=language,
        intent=intent,
        signals=signals,
    )

