"""piper_engine.py — Alternative Speech Model (Piper TTS).

Provides fast local VITS-based neural speech synthesis with multi-language
support including English, Hindi (hi_IN), and Gujarati (gu_IN).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import numpy as np

PIPER_MODELS_DIR = Path(__file__).resolve().parent / "models" / "piper"
PIPER_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Catalog of known Piper voice models
PIPER_VOICES: dict[str, list[dict[str, str]]] = {
    "en_US": [
        {"id": "en_US-lessac-medium", "name": "Lessac (Female - Clean)", "gender": "Female", "quality": "medium"},
        {"id": "en_US-amy-medium", "name": "Amy (Female - Friendly)", "gender": "Female", "quality": "medium"},
        {"id": "en_US-ryan-medium", "name": "Ryan (Male - Authoritative)", "gender": "Male", "quality": "medium"},
        {"id": "en_US-danny-low", "name": "Danny (Male - Fast)", "gender": "Male", "quality": "low"},
    ],
    "hi": [
        {"id": "hi_IN-rohan-medium", "name": "Rohan (Hindi Male)", "gender": "Male", "quality": "medium"},
        {"id": "hi_IN-priyam-medium", "name": "Priyam (Hindi Female)", "gender": "Female", "quality": "medium"},
    ],
    "gu": [
        {"id": "gu_IN-gujarati-medium", "name": "Gujarati Voice (gu_IN)", "gender": "Unspecified", "quality": "medium"},
    ],
}


def is_piper_installed() -> bool:
    """Check if piper CLI or python package is installed."""
    if shutil.which("piper"):
        return True
    try:
        import piper  # noqa
        return True
    except ImportError:
        return False


def get_installed_piper_models() -> list[str]:
    """Check which piper .onnx models are currently downloaded."""
    if not PIPER_MODELS_DIR.exists():
        return []
    return [f.stem for f in PIPER_MODELS_DIR.glob("*.onnx")]


def get_piper_voices_for_language(lang_code: str) -> list[dict[str, str]]:
    """Return available Piper voices, annotated with downloaded/available status."""
    installed = set(get_installed_piper_models())
    voices = PIPER_VOICES.get(lang_code, [])

    enriched = []
    for v in voices:
        is_ready = v["id"] in installed
        enriched.append({
            **v,
            "is_installed": is_ready,
            "display_name": f"{v['name']} " + ("✅ Ready" if is_ready else "📥 Requires ONNX download"),
        })
    return enriched


def has_gujarati_model() -> bool:
    """Check whether a compatible Gujarati model is downloaded."""
    installed = get_installed_piper_models()
    return any("gu" in m.lower() for m in installed)


def has_hindi_model() -> bool:
    """Check whether a compatible Hindi model is downloaded."""
    installed = get_installed_piper_models()
    return any("hi" in m.lower() for m in installed)
