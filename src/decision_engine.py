"""Hybrid ML + rules decision engine for risk detection."""

from __future__ import annotations

import pickle
from pathlib import Path

from src.preprocessing import clean_text
from src.rules import check_critical_keywords


MODEL_PATH = Path("models/model.pkl")
VECTORIZER_PATH = Path("models/vectorizer.pkl")


def _load_pickle(path: Path):
    with path.open("rb") as file:
        return pickle.load(file)


def _model_probability(text: str) -> float:
    """Return probability of the at_risk class from the trained model."""
    model = _load_pickle(MODEL_PATH)
    vectorizer = _load_pickle(VECTORIZER_PATH)
    features = vectorizer.transform([text])

    if hasattr(model, "classes_"):
        at_risk_index = list(model.classes_).index("at_risk")
        return float(model.predict_proba(features)[0][at_risk_index])

    return float(model.predict_proba(features)[0][1])


def evaluate_risk(text: str) -> dict:
    """
    Evaluate risk using explicit crisis rules first, then model probability.

    Rules have priority because false negatives are more harmful than false
    positives in crisis detection.
    """
    cleaned_text = clean_text(text)
    keyword_detected, matched_keywords = check_critical_keywords(text)

    try:
        probability = _model_probability(cleaned_text)
    except FileNotFoundError:
        probability = 0.0

    if keyword_detected:
        risk_level = "HIGH"
        reason = "keyword_trigger"
    elif probability > 0.7:
        risk_level = "HIGH"
        reason = "model_high_confidence"
    elif 0.4 <= probability <= 0.7:
        risk_level = "MEDIUM"
        reason = "model_moderate"
    else:
        risk_level = "LOW"
        reason = "model_low_confidence"

    return {
        "risk_level": risk_level,
        "probability": probability,
        "reason": reason,
        "matched_keywords": matched_keywords,
    }
