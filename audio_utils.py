"""audio_utils.py — Audio processing and storage utilities.

Handles volume scaling, peak normalization, audio format export (WAV/MP3),
and managing the outputs/ catalog.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import soundfile as sf

OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def process_and_save_audio(
    audio_data: np.ndarray,
    sample_rate: int = 24000,
    volume: float = 1.0,
    audio_format: str = "wav",
    prefix: str = "kokoro",
) -> tuple[Path, bytes]:
    """Process raw audio array (volume scale, clip) and write to file.

    Args:
        audio_data: Raw float audio array (usually normalized between -1.0 and 1.0).
        sample_rate: Audio sampling frequency in Hz (default 24000).
        volume: Volume multiplier (0.1 to 1.0).
        audio_format: 'wav' or 'mp3'.
        prefix: Prefix for saved file name.

    Returns:
        tuple of (saved_file_path, raw_bytes).
    """
    # Scale by volume
    scaled = audio_data.astype(np.float32) * float(volume)

    # Prevent hard digital clipping
    clipped = np.clip(scaled, -1.0, 1.0)

    # Format timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    ext = audio_format.lower().strip()
    if ext not in ("wav", "mp3"):
        ext = "wav"

    out_file = OUTPUT_DIR / f"{prefix}_{timestamp}.{ext}"

    # Write file using soundfile
    if ext == "wav":
        sf.write(str(out_file), clipped, sample_rate, format="WAV", subtype="PCM_16")
    elif ext == "mp3":
        # soundfile supports writing MP3 if libsndfile has MPEG support; fallback to WAV if unsupported
        try:
            sf.write(str(out_file), clipped, sample_rate, format="MP3")
        except Exception:
            # Fallback to WAV format
            out_file = out_file.with_suffix(".wav")
            sf.write(str(out_file), clipped, sample_rate, format="WAV", subtype="PCM_16")

    raw_bytes = out_file.read_bytes()
    return out_file, raw_bytes


def list_saved_audio_files() -> list[dict[str, str | int | float]]:
    """List all audio files stored in outputs/ with metadata."""
    if not OUTPUT_DIR.exists():
        return []

    audio_extensions = {".wav", ".mp3", ".ogg", ".flac"}
    files = [f for f in OUTPUT_DIR.glob("*.*") if f.suffix.lower() in audio_extensions]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    results = []
    for f in files:
        stat = f.stat()
        results.append({
            "path": str(f),
            "filename": f.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "format": f.suffix.replace(".", "").upper(),
        })
    return results
