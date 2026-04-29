"""User-facing Streamlit chat app."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

exec((ROOT_DIR / "application.py").read_text(encoding="utf-8"))
