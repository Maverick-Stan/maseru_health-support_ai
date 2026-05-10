"""Structured response generation for the health support assistant."""

from __future__ import annotations

from dataclasses import dataclass

from app.parser import ParsedQuery
from app.rules import SafetyAssessment


@dataclass(frozen=True)
class AssistantResponse:
    """Structured response returned to Streamlit."""

    summary: str
    guidance: str
    when_to_seek_help: str
    limitations: str

    def to_markdown(self) -> str:
        """Render the full structured response for logs or admin-style views."""
        return (
            f"**Summary**\n\n{self.summary}\n\n"
            f"**Guidance**\n\n{self.guidance}\n\n"
            f"**When to seek professional help**\n\n{self.when_to_seek_help}\n\n"
            f"**Limitations**\n\n{self.limitations}"
        )

    def to_chat_markdown(self) -> str:
        """Render only the user-facing support message for chat."""
        return (
            f"{self.guidance}\n\n"
            f"**When to seek professional help**\n\n{self.when_to_seek_help}"
        )


def build_summary(parsed_query: ParsedQuery, safety: SafetyAssessment) -> str:
    """Create a short, non-diagnostic summary from parser and rule outputs."""
    if parsed_query.intent == "empty":
        return "I did not receive enough detail to understand what support you need."

    if safety.risk_level == "HIGH":
        return "Your message includes language that may indicate an immediate safety concern."

    if parsed_query.intent == "greeting":
        return "You started the conversation and may be looking for support."

    if parsed_query.signals:
        return f"I noticed signals related to {', '.join(parsed_query.signals)}."

    return "You shared a health or wellbeing concern that can be discussed in general terms."


def _help_guidance(safety: SafetyAssessment) -> str:
    if safety.risk_level == "HIGH":
        return (
            "Please contact a trusted person now and seek in-person help from the nearest "
            "clinic, hospital, or local emergency service if you may be in immediate danger."
        )

    if safety.risk_level == "MEDIUM":
        return (
            "Consider speaking with a healthcare professional, counselor, or trusted person, "
            "especially if the feeling continues, worsens, or affects daily life."
        )

    return (
        "Seek professional help if symptoms persist, become severe, or make it difficult "
        "to sleep, work, study, care for yourself, or stay safe."
    )


def format_llm_response(
    llm_text: str,
    parsed_query: ParsedQuery,
    safety: SafetyAssessment,
) -> AssistantResponse:
    """Wrap an LLM response with fixed safety and limitation sections."""
    guidance = (
        llm_text.strip()
        or "I am here to listen and help you think through a safe next step."
    )
    return AssistantResponse(
        summary=build_summary(parsed_query, safety),
        guidance=guidance,
        when_to_seek_help=_help_guidance(safety),
        limitations=(
            "This assistant provides general, non-diagnostic support. It does not diagnose, "
            "treat, prescribe medication, replace a clinician, or provide emergency response."
        ),
    )


def escalation_response(
    parsed_query: ParsedQuery, safety: SafetyAssessment
) -> AssistantResponse:
    """Return deterministic escalation messaging without relying on the LLM."""
    if parsed_query.language == "Sesotho":
        guidance = (
            "Ha o mong. Ka kopo bua le motho eo o mo tshepang hona jwale, mme o batle "
            "thuso ya sefahleho le sefahleho tleliniking e haufi, sepetlele, kapa tshebeletso "
            "ya tshohanyetso haeba o ka ba kotsing hona jwale."
        )
    else:
        guidance = (
            "You are not alone. Please speak with someone you trust now and seek in-person "
            "support from the nearest clinic, hospital, or local emergency service if you may "
            "be in immediate danger."
        )

    return AssistantResponse(
        summary=build_summary(parsed_query, safety),
        guidance=guidance,
        when_to_seek_help=_help_guidance(safety),
        limitations=(
            "This system cannot assess emergencies, diagnose conditions, provide treatment, "
            "or replace professional medical care."
        ),
    )


def fallback_response(
    parsed_query: ParsedQuery, safety: SafetyAssessment
) -> AssistantResponse:
    """Return a safe response when the LLM layer is unavailable or fails."""
    return AssistantResponse(
        summary=build_summary(parsed_query, safety),
        guidance=(
            "I am having trouble generating a full response right now. A safer next step is "
            "to pause, stay near someone you trust if possible, and contact a local clinic "
            "or healthcare professional if the concern continues."
        ),
        when_to_seek_help=_help_guidance(safety),
        limitations=(
            "This fallback message is general support only. It is not diagnosis, treatment, "
            "clinical advice, or emergency response."
        ),
    )
