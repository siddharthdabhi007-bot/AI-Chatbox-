"""
tts_engine.py — High-compatibility Text to Speech engine.
Supports:
- pyttsx3 (SAPI5 on Windows, NSSpeechSynthesizer on macOS, espeak on Linux)
- Windows PowerShell System.Speech fallback
- gTTS (Google Text to Speech) optional fallback
- In-browser Web Speech API support
"""

from __future__ import annotations

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timezone


def get_available_voices() -> list[dict[str, str]]:
    """Return available TTS voices on the system."""
    voices: list[dict[str, str]] = []

    # 1. Try pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        py_voices = engine.getProperty("voices")
        if py_voices:
            for idx, v in enumerate(py_voices):
                name = getattr(v, "name", f"Voice {idx}")
                vid = str(getattr(v, "id", idx))
                voices.append({
                    "id": vid,
                    "name": name,
                    "engine": "pyttsx3",
                })
            engine.stop()
            if voices:
                return voices
    except Exception:
        pass

    # 2. Windows PowerShell fallback voice detection
    if os.name == "nt":
        try:
            ps_cmd = (
                "Add-Type -AssemblyName System.Speech; "
                "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "foreach ($v in $s.GetInstalledVoices()) { "
                "  $info = $v.VoiceInfo; "
                "  Write-Output ($info.Name + '::' + $info.Gender); "
                "}; $s.Dispose();"
            )
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.strip().splitlines():
                    if "::" in line:
                        vname, vgender = line.split("::", 1)
                        voices.append({
                            "id": vname.strip(),
                            "name": f"{vname.strip()} ({vgender.strip()})",
                            "engine": "sapi",
                        })
                if voices:
                    return voices
        except Exception:
            pass

    # Default fallback options if hardware/services are constrained
    return [
        {"id": "default", "name": "System Default Voice", "engine": "default"},
        {"id": "female", "name": "Microsoft Zira (Female)", "engine": "sapi"},
        {"id": "male", "name": "Microsoft David (Male)", "engine": "sapi"},
    ]


def synthesize_speech(
    text: str,
    output_path: str | Path,
    voice_id: str | None = None,
    rate: int = 150,
    volume: float = 1.0,
) -> Path:
    """Synthesize text to an audio file (WAV).

    Args:
        text: Text to speak.
        output_path: Target path to save the .wav file.
        voice_id: Specific voice identifier or None for default.
        rate: Speaking speed in words per minute (e.g. 50-300, default 150).
        volume: Volume level from 0.0 to 1.0 (default 1.0).

    Returns:
        Path to the saved audio file.
    """
    out_path = Path(output_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = text.strip()

    if not text:
        raise ValueError("Text cannot be empty.")

    errors: list[str] = []

    # 1. Primary: pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", int(rate))
        engine.setProperty("volume", float(volume))

        if voice_id and voice_id not in ("default", "male", "female"):
            try:
                engine.setProperty("voice", voice_id)
            except Exception:
                pass

        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        engine.stop()

        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path
    except Exception as exc:
        errors.append(f"pyttsx3: {exc}")

    # 2. Windows PowerShell SAPI fallback
    if os.name == "nt":
        try:
            # Map rate 50..300 to PowerShell range -10..10
            ps_rate = max(-10, min(10, int((rate - 150) / 15)))
            ps_volume = max(0, min(100, int(volume * 100)))

            escaped_text = text.replace("'", "''").replace("`", "``")
            escaped_path = str(out_path).replace("'", "''")

            voice_filter = ""
            if voice_id and voice_id not in ("default",):
                first_name = voice_id.split()[0].replace("'", "''")
                voice_filter = f"try {{ $s.SelectVoice('{first_name}') }} catch {{}};"

            ps_code = (
                f"Add-Type -AssemblyName System.Speech; "
                f"$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"$s.Rate = {ps_rate}; $s.Volume = {ps_volume}; "
                f"{voice_filter} "
                f"$s.SetOutputToWaveFile('{escaped_path}'); "
                f"$s.Speak('{escaped_text}'); "
                f"$s.Dispose();"
            )
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_code],
                capture_output=True,
                text=True,
                timeout=25,
            )
            if out_path.exists() and out_path.stat().st_size > 0:
                return out_path
            errors.append(f"PowerShell SAPI: {res.stderr.strip() or 'No audio written'}")
        except Exception as exc:
            errors.append(f"PowerShell SAPI: {exc}")

    # 3. Optional: gTTS (Google Text to Speech)
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en")
        tts.save(str(out_path))
        if out_path.exists() and out_path.stat().st_size > 0:
            return out_path
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"gTTS: {exc}")

    raise RuntimeError(
        "Could not generate speech audio. Details:\n" + "\n".join(errors)
    )
