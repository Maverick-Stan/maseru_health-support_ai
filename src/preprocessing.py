"""Text preprocessing utilities for the risk detection pipeline."""

from __future__ import annotations

import re
import string


def clean_text(text: str) -> str:
    """Normalize text before keyword checks and vectorization."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    """Tokenize cleaned text into simple word tokens."""
    return clean_text(text).split()
