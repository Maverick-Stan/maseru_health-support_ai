"""Minimal admin page for explainable safety assessment."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.parser import parse_user_input
from app.rules import assess_safety


def main() -> None:
    """Render the admin safety-inspection page."""
    st.set_page_config(
        page_title="Risk Admin",
        layout="centered",
    )

    st.title("Risk Admin")
    st.caption("Explainable parser, classifier, and rule-based safety review")

    sample_text = st.text_area(
        "Message",
        placeholder="Paste a user message to evaluate...",
        height=120,
    )

    if sample_text:
        parsed = parse_user_input(sample_text)
        result = assess_safety(parsed)

        if result.risk_level == "HIGH":
            st.warning(
                "You are not alone. Please consider visiting a nearby clinic or "
                "speaking to a professional."
            )

        col1, col2 = st.columns(2)
        col1.metric("Risk Level", result.risk_level)
        col2.metric("Confidence Score", f"{result.probability:.2%}")

        col3, col4 = st.columns(2)
        col3.metric("Intent", parsed.intent)
        col4.metric("Escalation", "Yes" if result.escalation_required else "No")

        if not result.model_available:
            st.info(
                "The classifier model was unavailable, so rule-based safety output was used."
            )

        st.divider()
        st.write("**Signals**")
        st.write(", ".join(parsed.signals) or "None")

        st.write("**Reason**")
        st.write(result.reason)

        st.write("**Matched Safety Terms**")
        st.write(", ".join(result.matched_keywords) or "None")
    else:
        st.info("Enter a message to view risk metadata.")


if __name__ == "__main__":
    main()
