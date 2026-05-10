"""Repository-root-aware filesystem paths shared across app and ML modules."""

from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "model.pkl"
VECTORIZER_PATH = ROOT_DIR / "models" / "vectorizer.pkl"
DATASET_PATH = ROOT_DIR / "data" / "mental_health_dataset.csv"
