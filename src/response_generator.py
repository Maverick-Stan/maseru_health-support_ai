"""Risk-aware response helpers for the support system."""

from __future__ import annotations


def generate_response(risk_level: str) -> str:
    """Generate supportive, non-clinical guidance for a risk level."""
    if risk_level == "HIGH":
        return (
            "You are not alone. Please consider speaking with a trusted person now "
            "and visiting the nearest clinic or a mental health professional for support."
        )

    if risk_level == "MEDIUM":
        return (
            "Thank you for sharing that. It sounds like things may feel heavy right now. "
            "I can stay with you and help you think through one manageable next step."
        )

    return "Thank you for sharing. I am here to listen and support you."
