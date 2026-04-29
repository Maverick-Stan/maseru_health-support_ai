"""TF-IDF feature engineering for mental health risk classification."""

from __future__ import annotations

import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer


DEFAULT_VECTORIZER_PATH = Path("models/vectorizer.pkl")


def fit_vectorizer(texts, output_path: Path = DEFAULT_VECTORIZER_PATH):
    """Fit and persist a TF-IDF vectorizer."""
    vectorizer = TfidfVectorizer(
        lowercase=False,
        ngram_range=(1, 2),
        min_df=1,
        max_features=1500,
    )
    features = vectorizer.fit_transform(texts)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as file:
        pickle.dump(vectorizer, file)

    return vectorizer, features


def load_vectorizer(path: Path = DEFAULT_VECTORIZER_PATH):
    """Load a saved TF-IDF vectorizer."""
    with path.open("rb") as file:
        return pickle.load(file)
