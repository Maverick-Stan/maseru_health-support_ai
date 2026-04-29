"""Minimal admin page for explainable risk assessment."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.decision_engine import evaluate_risk


st.set_page_config(
    page_title="Risk Admin",
    page_icon="📊",
    layout="centered",
)

st.title("Risk Admin")
st.caption("Explainable ML + rule-based risk review")

sample_text = st.text_area(
    "Message",
    placeholder="Paste a user message to evaluate...",
    height=120,
)

if sample_text:
    result = evaluate_risk(sample_text)

    if result["risk_level"] == "HIGH":
        st.warning(
            "You are not alone. Please consider visiting a nearby clinic or "
            "speaking to a professional."
        )

    col1, col2 = st.columns(2)
    col1.metric("Risk Level", result["risk_level"])
    col2.metric("Confidence Score", f"{result['probability']:.2%}")

    st.divider()
    st.write("**Reason**")
    st.write(result["reason"])

    st.write("**Matched Keywords**")
    st.write(", ".join(result["matched_keywords"]) or "None")
else:
    st.info("Enter a message to view risk metadata.")
