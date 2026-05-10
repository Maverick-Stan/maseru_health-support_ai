"""Streamlit interface for Maseru Health AI."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import get_settings
from app.triage_service import TriageService


def _initialize_state() -> None:
    if "service" not in st.session_state:
        st.session_state.service = TriageService(user_id="patient_001")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "risk_assessments" not in st.session_state:
        st.session_state.risk_assessments = []


def main() -> None:
    """Render the user-facing Streamlit chat app."""
    st.set_page_config(
        page_title="Maseru Health AI",
        page_icon="🩺",
        layout="centered",
    )

    settings = get_settings()
    _initialize_state()

    st.markdown(
        """
        <style>
            .app-header {
                text-align: center;
                margin-bottom: 0.75rem;
            }
            .app-header h1 {
                font-size: 2.1rem;
                margin-bottom: 0.35rem;
            }
            .app-subtitle {
                color: #5f6368;
                font-size: 0.86rem;
                font-style: italic;
                line-height: 1.45;
                margin: 0.15rem auto;
                max-width: 46rem;
            }
        </style>
        <div class="app-header">
            <h1>🩺 Maseru Health AI</h1>
            <p class="app-subtitle">
                Operational healthcare support assistant for general, non-diagnostic guidance
                in low-resource contexts.
            </p>
            <p class="app-subtitle">
                This assistant provides general support only. It does not diagnose, treat,
                prescribe medication, replace a clinician, or provide emergency response.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Settings")
        language = st.radio("Language", ["English", "Sesotho"], index=0)
        st.divider()
        st.write("LLM status")
        if settings.llm_available:
            st.success(f"Configured: {settings.llm_model}")
        else:
            st.warning("OPENAI_API_KEY is not configured. Safe fallback responses are enabled.")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("How can I support you today?")

    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Listening and here for you."):
            result = st.session_state.service.handle_message(
                user_input,
                language=language,
                conversation_context=st.session_state.messages,
            )

        if result.safety.escalation_required:
            st.warning(
                "This message triggered a safety escalation. Please seek in-person "
                "support if there may be immediate danger."
            )

        if result.error:
            st.info("The LLM response failed, so a safe fallback response was used.")

        markdown_response = result.response.to_chat_markdown()
        st.markdown(markdown_response)

    st.session_state.risk_assessments.append(
        {
            "message": user_input,
            "intent": result.parsed_query.intent,
            "signals": ", ".join(result.parsed_query.signals) or "None",
            "risk_level": result.safety.risk_level,
            "confidence_score": result.safety.probability,
            "reason": result.safety.reason,
            "matched_keywords": ", ".join(result.safety.matched_keywords) or "None",
            "used_llm": result.used_llm,
            "model_available": result.safety.model_available,
        }
    )
    st.session_state.messages.append({"role": "assistant", "content": markdown_response})


if __name__ == "__main__":
    main()
