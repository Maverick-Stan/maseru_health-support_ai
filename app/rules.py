"""Rule-based safety layer for non-diagnostic health support."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.parser import ParsedQuery
from src.decision_engine import evaluate_risk
from src.preprocessing import clean_text


PHYSICAL_RED_FLAGS = [
    "chest pain",
    "difficulty breathing",
    "trouble breathing",
    "shortness of breath",
    "severe bleeding",
    "fainting",
    "seizure",
    "stroke",
    "unconscious",
    "overdose",
]


@dataclass(frozen=True)
class SafetyAssessment:
    """Explainable safety decision used before any LLM response."""

    risk_level: str
    probability: float
    reason: str
    matched_keywords: list[str] = field(default_factory=list)
    escalation_required: bool = False
    professional_help_recommended: bool = False
    model_available: bool = True


def _match_physical_red_flags(text: str) -> list[str]:
    normalized = clean_text(text)
    return [phrase for phrase in PHYSICAL_RED_FLAGS if clean_text(phrase) in normalized]


def assess_safety(parsed_query: ParsedQuery) -> SafetyAssessment:
    """Run deterministic safety rules and the existing risk classifier."""
    risk = evaluate_risk(parsed_query.original_text)
    matched_keywords = list(risk.get("matched_keywords", []))
    physical_matches = _match_physical_red_flags(parsed_query.original_text)

    if physical_matches:
        matched_keywords.extend(physical_matches)
        return SafetyAssessment(
            risk_level="HIGH",
            probability=float(risk.get("probability", 0.0)),
            reason="physical_red_flag_rule",
            matched_keywords=matched_keywords,
            escalation_required=True,
            professional_help_recommended=True,
            model_available=bool(risk.get("model_available", True)),
        )

    risk_level = str(risk.get("risk_level", "LOW"))
    return SafetyAssessment(
        risk_level=risk_level,
        probability=float(risk.get("probability", 0.0)),
        reason=str(risk.get("reason", "unknown")),
        matched_keywords=matched_keywords,
        escalation_required=risk_level == "HIGH",
        professional_help_recommended=risk_level in {"HIGH", "MEDIUM"},
        model_available=bool(risk.get("model_available", True)),
    )
