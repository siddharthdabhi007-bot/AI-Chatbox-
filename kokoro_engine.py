"""kokoro_engine.py — Open-source Neural Text-to-Speech Engine using Kokoro-82M.

Provides natural, studio-quality offline speech synthesis on Windows (RTX 3050 GPU or CPU fallback).
Includes resilient safety wrappers for Windows Application Control / Smart App Control policies.
"""

from __future__ import annotations

import os
from typing import Generator
import numpy as np

# Safe PyTorch import with Windows AppLocker / Smart App Control handling
try:
    import torch
    TORCH_AVAILABLE = True
    TORCH_ERROR = None
except Exception as _torch_err:
    torch = None
    TORCH_AVAILABLE = False
    TORCH_ERROR = str(_torch_err)

# Voice catalog organized by language, gender, and style
KOKORO_VOICES: dict[str, list[dict[str, str]]] = {
    "en_US": [  # American English (lang_code='a')
        {"id": "af_heart", "name": "Heart (Female - Grade A Studio)", "gender": "Female", "style": "Warm & Natural"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "Female", "style": "Expressive & Soft"},
        {"id": "af_nicole", "name": "Nicole (Female)", "gender": "Female", "style": "Professional & Crisp"},
        {"id": "af_aoede", "name": "Aoede (Female)", "gender": "Female", "style": "Melodic & Friendly"},
        {"id": "af_kore", "name": "Kore (Female)", "gender": "Female", "style": "Calm & Narration"},
        {"id": "af_sarah", "name": "Sarah (Female)", "gender": "Female", "style": "Engaging & Bright"},
        {"id": "af_sky", "name": "Sky (Female)", "gender": "Female", "style": "Youthful & Clear"},
        {"id": "af_alloy", "name": "Alloy (Female)", "gender": "Female", "style": "Versatile & Modern"},
        {"id": "af_jessica", "name": "Jessica (Female)", "gender": "Female", "style": "Confident & Authoritative"},
        {"id": "af_river", "name": "River (Female)", "gender": "Female", "style": "Gentle & Smooth"},
        {"id": "am_adam", "name": "Adam (Male)", "gender": "Male", "style": "Deep & Professional"},
        {"id": "am_echo", "name": "Echo (Male)", "gender": "Male", "style": "Warm & Radio Host"},
        {"id": "am_eric", "name": "Eric (Male)", "gender": "Male", "style": "Dynamic & Conversational"},
        {"id": "am_fenrir", "name": "Fenrir (Male)", "gender": "Male", "style": "Authoritative & Strong"},
        {"id": "am_liam", "name": "Liam (Male)", "gender": "Male", "style": "Friendly & Clear"},
        {"id": "am_michael", "name": "Michael (Male)", "gender": "Male", "style": "Storyteller & Rich"},
        {"id": "am_onyx", "name": "Onyx (Male)", "gender": "Male", "style": "Resonant & Deep"},
        {"id": "am_puck", "name": "Puck (Male)", "gender": "Male", "style": "Energetic & Character"},
        {"id": "am_santa", "name": "Santa (Male)", "gender": "Male", "style": "Jovial & Festive"},
    ],
    "en_GB": [  # British English (lang_code='b')
        {"id": "bf_alice", "name": "Alice (Female)", "gender": "Female", "style": "Refined British Accent"},
        {"id": "bf_emma", "name": "Emma (Female)", "gender": "Female", "style": "Polite & Documentary"},
        {"id": "bf_isabella", "name": "Isabella (Female)", "gender": "Female", "style": "Elegant & Narrative"},
        {"id": "bf_lily", "name": "Lily (Female)", "gender": "Female", "style": "Youthful & Expressive"},
        {"id": "bm_daniel", "name": "Daniel (Male)", "gender": "Male", "style": "Cultured & Professional"},
        {"id": "bm_fable", "name": "Fable (Male)", "gender": "Male", "style": "Storyteller & Dramatic"},
        {"id": "bm_george", "name": "George (Male)", "gender": "Male", "style": "Deep British Accent"},
        {"id": "bm_lewis", "name": "Lewis (Male)", "gender": "Male", "style": "Clear & Conversational"},
    ],
    "hi": [  # Hindi (lang_code='h')
        {"id": "hf_alpha", "name": "Alpha (Hindi Female)", "gender": "Female", "style": "Clear Hindi Narration"},
        {"id": "hf_beta", "name": "Beta (Hindi Female)", "gender": "Female", "style": "Soft & Melodic"},
        {"id": "hm_omega", "name": "Omega (Hindi Male)", "gender": "Male", "style": "Deep Hindi Broadcast"},
        {"id": "hm_psi", "name": "Psi (Hindi Male)", "gender": "Male", "style": "Natural & Conversational"},
    ],
    "es": [  # Spanish (lang_code='e')
        {"id": "ef_dora", "name": "Dora (Spanish Female)", "gender": "Female", "style": "Natural Spanish"},
        {"id": "em_alex", "name": "Alex (Spanish Male)", "gender": "Male", "style": "Clear Spanish"},
    ],
    "fr": [  # French (lang_code='f')
        {"id": "ff_siwis", "name": "Siwis (French Female)", "gender": "Female", "style": "Natural French"},
    ],
    "ja": [  # Japanese (lang_code='j')
        {"id": "jf_alpha", "name": "Alpha (Japanese Female)", "gender": "Female", "style": "Natural Japanese"},
        {"id": "jm_kumo", "name": "Kumo (Japanese Male)", "gender": "Male", "style": "Expressive Japanese"},
    ],
    "zh": [  # Mandarin (lang_code='z')
        {"id": "zf_xiaobei", "name": "Xiaobei (Mandarin Female)", "gender": "Female", "style": "Standard Mandarin"},
        {"id": "zm_yunjian", "name": "Yunjian (Mandarin Male)", "gender": "Male", "style": "Clear Mandarin"},
    ],
    "it": [  # Italian (lang_code='i')
        {"id": "if_sara", "name": "Sara (Italian Female)", "gender": "Female", "style": "Expressive Italian"},
        {"id": "im_nicola", "name": "Nicola (Italian Male)", "gender": "Male", "style": "Natural Italian"},
    ],
    "pt": [  # Portuguese (lang_code='p')
        {"id": "pf_dora", "name": "Dora (Portuguese Female)", "gender": "Female", "style": "Natural Brazilian"},
        {"id": "pm_alex", "name": "Alex (Portuguese Male)", "gender": "Male", "style": "Clear Portuguese"},
    ],
}

# Mapping from app language code to Kokoro internal lang_code
LANG_CODE_MAP = {
    "en_US": "a",
    "en_GB": "b",
    "hi": "h",
    "es": "e",
    "fr": "f",
    "ja": "j",
    "zh": "z",
    "it": "i",
    "pt": "p",
}

# Global pipeline cache to avoid reloading weights repeatedly
_PIPELINE_CACHE: dict[str, object] = {}


def is_torch_available() -> bool:
    """Return True if PyTorch is loaded and operational."""
    return TORCH_AVAILABLE and torch is not None


def get_torch_error() -> str:
    """Return error message if PyTorch failed to load."""
    return TORCH_ERROR or ""


def get_device() -> str:
    """Detect NVIDIA GPU or fall back to CPU."""
    if is_torch_available():
        try:
            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
    return "cpu"


def get_device_info() -> dict[str, str]:
    """Return human-readable device and VRAM status."""
    if not is_torch_available():
        return {
            "device": "CPU (SAPI5 Active)",
            "name": "Host Processor (PyTorch restricted by Windows policy)",
            "vram": "System RAM",
            "is_gpu": False,
            "torch_available": False,
            "torch_error": TORCH_ERROR or "",
        }

    try:
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return {
                "device": "CUDA (GPU)",
                "name": name,
                "vram": f"{vram_gb:.1f} GB",
                "is_gpu": True,
                "torch_available": True,
                "torch_error": "",
            }
    except Exception:
        pass

    return {
        "device": "CPU",
        "name": "Standard Host Processor",
        "vram": "System RAM",
        "is_gpu": False,
        "torch_available": True,
        "torch_error": "",
    }


def get_supported_languages() -> list[dict[str, str]]:
    """Return list of supported languages."""
    return [
        {"code": "en_US", "name": "English (United States)", "flag": "🇺🇸"},
        {"code": "en_GB", "name": "English (United Kingdom)", "flag": "🇬🇧"},
        {"code": "hi", "name": "Hindi (हिंदी)", "flag": "🇮🇳"},
        {"code": "es", "name": "Spanish (Español)", "flag": "🇪🇸"},
        {"code": "fr", "name": "French (Français)", "flag": "🇫🇷"},
        {"code": "ja", "name": "Japanese (日本語)", "flag": "🇯🇵"},
        {"code": "zh", "name": "Mandarin (中文)", "flag": "🇨🇳"},
        {"code": "it", "name": "Italian (Italiano)", "flag": "🇮🇹"},
        {"code": "pt", "name": "Portuguese (Português)", "flag": "🇧🇷"},
    ]


def get_voices_for_language(lang_code: str) -> list[dict[str, str]]:
    """Return all voices for a given language code."""
    return KOKORO_VOICES.get(lang_code, KOKORO_VOICES["en_US"])


def get_pipeline(lang_code: str = "en_US"):
    """Get or instantiate cached KPipeline for the requested language."""
    if not is_torch_available():
        raise RuntimeError(
            f"PyTorch is blocked or unavailable on this system: {TORCH_ERROR}. "
            "Please switch speech model to 'Windows SAPI5 (Local System)'."
        )

    internal_code = LANG_CODE_MAP.get(lang_code, "a")
    device = get_device()
    cache_key = f"{internal_code}_{device}"

    if cache_key not in _PIPELINE_CACHE:
        from kokoro import KPipeline
        _PIPELINE_CACHE[cache_key] = KPipeline(lang_code=internal_code, device=device)

    return _PIPELINE_CACHE[cache_key]


def synthesize_kokoro(
    text: str,
    voice: str = "af_heart",
    lang_code: str = "en_US",
    speed: float = 1.0,
) -> tuple[np.ndarray, int]:
    """Generate audio waveform from text using Kokoro-82M.

    Args:
        text: Input text string.
        voice: Kokoro voice ID (e.g. 'af_heart', 'am_adam', 'hf_alpha').
        lang_code: Language code ('en_US', 'hi', etc.).
        speed: Speech rate multiplier (0.5 to 2.0).

    Returns:
        tuple of (audio_numpy_array, sample_rate_hz).
    """
    if not is_torch_available():
        raise RuntimeError(
            f"Kokoro-82M requires PyTorch, but PyTorch was blocked by Windows Application Control:\n{TORCH_ERROR}\n\n"
            "Solution: Switch the Speech Engine dropdown to 'Windows SAPI5 (Local System)' which runs directly without PyTorch."
        )

    text = text.strip()
    if not text:
        raise ValueError("Text cannot be empty.")

    pipeline = get_pipeline(lang_code)
    generator = pipeline(text, voice=voice, speed=float(speed))

    chunks: list[np.ndarray] = []
    for _, _, audio in generator:
        if is_torch_available() and isinstance(audio, torch.Tensor):
            chunks.append(audio.detach().cpu().numpy())
        elif isinstance(audio, np.ndarray):
            chunks.append(audio)
        else:
            try:
                chunks.append(np.array(audio, dtype=np.float32))
            except Exception:
                pass

    if not chunks:
        raise RuntimeError("Kokoro model produced no audio chunks.")

    combined_audio = np.concatenate(chunks)
    sample_rate = 24000  # Kokoro outputs at high-fidelity 24 kHz
    return combined_audio, sample_rate
