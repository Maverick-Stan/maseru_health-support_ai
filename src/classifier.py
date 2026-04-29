"""Train the risk classifier and persist model artifacts."""

from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.feature_engineering import fit_vectorizer
from src.preprocessing import clean_text


DATASET_PATH = Path("data/mental_health_dataset.csv")
MODEL_PATH = Path("models/model.pkl")


def train_classifier(dataset_path: Path = DATASET_PATH, model_path: Path = MODEL_PATH):
    """Train a recall-aware Logistic Regression classifier."""
    data = pd.read_csv(dataset_path)
    data["clean_text"] = data["text"].apply(clean_text)

    train_texts, test_texts, y_train, y_test = train_test_split(
        data["clean_text"],
        data["label"],
        test_size=0.25,
        random_state=42,
        stratify=data["label"],
    )

    vectorizer, x_train = fit_vectorizer(train_texts)
    x_test = vectorizer.transform(test_texts)

    model = LogisticRegression(
        class_weight="balanced",
        C=3.0,
        max_iter=1000,
        random_state=42,
    )
    model.fit(x_train, y_train)

    at_risk_index = list(model.classes_).index("at_risk")
    at_risk_probabilities = model.predict_proba(x_test)[:, at_risk_index]
    recall_threshold = 0.4
    predictions = [
        "at_risk" if probability >= recall_threshold else "safe"
        for probability in at_risk_probabilities
    ]

    precision = precision_score(y_test, predictions, pos_label="at_risk", zero_division=0)
    recall = recall_score(y_test, predictions, pos_label="at_risk", zero_division=0)
    f1 = f1_score(y_test, predictions, pos_label="at_risk", zero_division=0)

    print("Risk classifier metrics for at_risk class")
    print(f"decision threshold: {recall_threshold:.3f} (recall-oriented)")
    print(f"precision: {precision:.3f}")
    print(f"recall: {recall:.3f}")
    print(f"f1 score: {f1:.3f}")
    print()
    print(classification_report(y_test, predictions, zero_division=0))

    final_vectorizer, final_features = fit_vectorizer(data["clean_text"])
    final_model = LogisticRegression(
        class_weight="balanced",
        C=3.0,
        max_iter=1000,
        random_state=42,
    )
    final_model.fit(final_features, data["label"])

    model_path.parent.mkdir(parents=True, exist_ok=True)
    with model_path.open("wb") as file:
        pickle.dump(final_model, file)

    return final_model


if __name__ == "__main__":
    train_classifier()
