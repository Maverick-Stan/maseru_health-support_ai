"""Runtime configuration for the Maseru Health AI application."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs):
        return False

from src.paths import ROOT_DIR


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = "maseru_health_support"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None

    @property
    def llm_available(self) -> bool:
        """Return whether the configured LiteLLM/OpenAI model can be called."""
        return bool(self.openai_api_key)


def get_settings() -> Settings:
    """Load settings from `.env` and process environment variables."""
    load_dotenv(ROOT_DIR / ".env")
    return Settings(
        app_name=os.getenv("MASERU_APP_NAME", "maseru_health_support"),
        llm_model=os.getenv("MASERU_LLM_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
