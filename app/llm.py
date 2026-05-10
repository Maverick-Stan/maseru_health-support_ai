"""LLM orchestration layer using the existing Google ADK + LiteLLM provider."""

from __future__ import annotations

import asyncio

from app.config import Settings, get_settings
from app.parser import ParsedQuery
from app.rules import SafetyAssessment


class LLMUnavailableError(RuntimeError):
    """Raised when the configured LLM cannot be called."""


class MaseruLLMClient:
    """Small wrapper around Google ADK runner/session setup."""

    def __init__(self, user_id: str, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.user_id = user_id
        self.session_id = f"session_{user_id}"
        self.agent = None
        self.runner = None
        self.session_service = None
        self._types = None
        self.unavailable_reason = ""

        if not self.settings.llm_available:
            self.unavailable_reason = "OPENAI_API_KEY is not configured."
            return

        try:
            from google.adk.agents import LlmAgent
            from google.adk.models.lite_llm import LiteLlm
            from google.adk.runners import Runner
            from google.adk.sessions import InMemorySessionService
            from google.genai import types

            self._types = types
            model = LiteLlm(model=self.settings.llm_model)
            self.agent = LlmAgent(
                name="MaseruHealthSupportCoordinator",
                description="Coordinates safe, non-diagnostic health support responses.",
                instruction=(
                    "You are Maseru Health AI, a non-diagnostic healthcare support assistant "
                    "for low-resource health support workflows in Maseru, Lesotho. "
                    "Provide supportive, general wellbeing guidance only. Do not diagnose, "
                    "prescribe medication, provide treatment plans, claim clinical validation, "
                    "or present yourself as an emergency service. Keep responses concise, calm, "
                    "and practical. Encourage in-person professional care when symptoms are severe, "
                    "persistent, worsening, or safety-related."
                ),
                model=model,
            )
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                agent=self.agent,
                app_name=self.settings.app_name,
                session_service=self.session_service,
            )
            asyncio.run(
                self.session_service.create_session(
                    app_name=self.settings.app_name,
                    user_id=self.user_id,
                    session_id=self.session_id,
                )
            )
        except Exception as exc:
            self.runner = None
            self.unavailable_reason = str(exc)

    def generate(
        self,
        parsed_query: ParsedQuery,
        safety: SafetyAssessment,
        conversation_context: list[dict[str, str]] | None = None,
    ) -> str:
        """Generate a safe, non-diagnostic response for a parsed message."""
        if not self.runner:
            raise LLMUnavailableError(self.unavailable_reason or "The LLM is unavailable.")

        prompt = self._build_prompt(parsed_query, safety, conversation_context or [])
        return asyncio.run(self._run_async(prompt))

    async def _run_async(self, prompt: str) -> str:
        if not self._types:
            raise LLMUnavailableError("The Google ADK message types are unavailable.")

        content = self._types.Content(role="user", parts=[self._types.Part(text=prompt)])
        async for event in self.runner.run_async(
            user_id=self.user_id,
            session_id=self.session_id,
            new_message=content,
        ):
            if event.is_final_response():
                return event.content.parts[0].text

        raise LLMUnavailableError("The LLM did not return a final response.")

    @staticmethod
    def _build_prompt(
        parsed_query: ParsedQuery,
        safety: SafetyAssessment,
        conversation_context: list[dict[str, str]],
    ) -> str:
        recent_context = conversation_context[-6:]
        context_lines = [
            f"{item.get('role', 'unknown')}: {item.get('content', '')}"
            for item in recent_context
        ]
        context = "\n".join(context_lines) or "No prior context."

        return (
            f"Requested response language: {parsed_query.language}\n"
            f"Parsed intent: {parsed_query.intent}\n"
            f"Detected signals: {', '.join(parsed_query.signals) or 'none'}\n"
            f"Safety risk level: {safety.risk_level}\n"
            f"Safety reason: {safety.reason}\n"
            f"Matched safety terms: {', '.join(safety.matched_keywords) or 'none'}\n\n"
            "Recent conversation:\n"
            f"{context}\n\n"
            "User message:\n"
            f"{parsed_query.original_text}\n\n"
            "Respond with supportive general guidance only. Do not include section headings; "
            "the application will add the final response structure."
        )
