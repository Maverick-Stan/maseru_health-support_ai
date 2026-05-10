"""Application service that connects parsing, safety, LLM, and formatting."""

from __future__ import annotations

from dataclasses import dataclass

from app.llm import MaseruLLMClient
from app.parser import ParsedQuery, parse_user_input
from app.response_formatter import (
    AssistantResponse,
    escalation_response,
    fallback_response,
    format_llm_response,
)
from app.rules import SafetyAssessment, assess_safety


@dataclass(frozen=True)
class TriageResult:
    """Full result returned by the triage service."""

    parsed_query: ParsedQuery
    safety: SafetyAssessment
    response: AssistantResponse
    used_llm: bool
    error: str | None = None


class TriageService:
    """Coordinates the health support workflow for the UI layer."""

    def __init__(
        self, user_id: str = "patient_001", llm_client: MaseruLLMClient | None = None
    ):
        self.llm_client = llm_client or MaseruLLMClient(user_id=user_id)

    def handle_message(
        self,
        message: str,
        language: str = "English",
        conversation_context: list[dict[str, str]] | None = None,
    ) -> TriageResult:
        """Process a user message through parser, safety layer, and LLM."""
        parsed_query = parse_user_input(message, language=language)
        safety = assess_safety(parsed_query)

        if safety.escalation_required:
            return TriageResult(
                parsed_query=parsed_query,
                safety=safety,
                response=escalation_response(parsed_query, safety),
                used_llm=False,
            )

        try:
            llm_text = self.llm_client.generate(
                parsed_query=parsed_query,
                safety=safety,
                conversation_context=conversation_context or [],
            )
            response = format_llm_response(llm_text, parsed_query, safety)
            return TriageResult(
                parsed_query=parsed_query,
                safety=safety,
                response=response,
                used_llm=True,
            )
        except Exception as exc:
            return TriageResult(
                parsed_query=parsed_query,
                safety=safety,
                response=fallback_response(parsed_query, safety),
                used_llm=False,
                error=str(exc),
            )
