"""Create a small demonstration dataset for risk classification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DATASET_PATH = Path("data/mental_health_dataset.csv")


SAFE_EXAMPLES = [
    "I feel okay today",
    "I had a stressful day but I am managing",
    "I feel tired after work",
    "I am worried about school",
    "I slept badly last night",
    "I feel lonely sometimes",
    "I need someone to talk to",
    "I am feeling better than yesterday",
    "I am nervous about my appointment",
    "I feel sad but I am safe",
    "I argued with a friend and feel upset",
    "I am overwhelmed with responsibilities",
    "I feel anxious before exams",
    "I want advice on coping with stress",
    "I am having a hard week",
    "I miss my family",
    "I feel calm today",
    "I am frustrated but okay",
    "I need rest and support",
    "I feel hopeful after talking to someone",
]


AT_RISK_EXAMPLES = [
    "I feel hopeless",
    "I can't go on",
    "I want to end it",
    "I am tired of everything",
    "I want to die",
    "I want to kill myself",
    "I might hurt myself tonight",
    "There is no reason to live",
    "I feel like ending it all",
    "I do not want to be alive",
    "I am thinking about suicide",
    "I cannot keep living like this",
    "Everyone would be better without me",
    "I have a plan to hurt myself",
    "I feel trapped and want it to stop forever",
    "I am scared I will harm myself",
    "I keep thinking about ending my life",
    "I cannot see any way out",
    "I want the pain to end permanently",
    "I am close to giving up completely",
]


def create_dataset(output_path: Path = DATASET_PATH) -> pd.DataFrame:
    rows = [{"text": text, "label": "safe"} for text in SAFE_EXAMPLES]
    rows.extend({"text": text, "label": "at_risk"} for text in AT_RISK_EXAMPLES)

    dataset = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_path, index=False)
    return dataset


if __name__ == "__main__":
    created = create_dataset()
    print(f"Saved {len(created)} rows to {DATASET_PATH}")
