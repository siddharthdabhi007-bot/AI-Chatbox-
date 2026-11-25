"""Speech.py — Standalone CLI script for Speech Synthesis.

Supports:
1. Local SAPI5 via pyttsx3 (when interactive audio device is available)
2. Studio-quality Neural TTS via Kokoro-82M (fallback or high-fidelity mode)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

def run_cli():
    print("=" * 55)
    print("🎙️  AI SPEECH GENERATOR CLI")
    print("=" * 55)

    sapi_working = False
    engine = None
    voices = []

    # Attempt pyttsx3 initialization
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        voices = engine.getProperty("voices")
        if voices:
            sapi_working = True
    except Exception as e:
        sapi_working = False

    if sapi_working and engine:
        print("\nUsing Engine: Windows SAPI5 (pyttsx3)")
        print("Available voices:")
        for index, v in enumerate(voices):
            print(f"  [{index}] {v.name}")

        choice = input(f"\nSelect voice index (0 to {len(voices)-1}, press Enter for 0): ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(voices):
            engine.setProperty("voice", voices[int(choice)].id)
            print(f"Selected voice: {voices[int(choice)].name}")
        else:
            engine.setProperty("voice", voices[0].id)
            print(f"Using default voice: {voices[0].name}")

        text = input("\nEnter text to convert into speech: ").strip()
        if text:
            print("Speaking...")
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

            output_filename = "output.wav"
            engine.save_to_file(text, output_filename)
            engine.runAndWait()
            engine.stop()
            print(f"✅ Audio saved successfully as '{output_filename}'.")
        else:
            print("Please enter some text.")

    else:
        # Seamless fallback to Kokoro-82M Neural Model
        print("\nNote: Windows SAPI5 audio service is restricted or unavailable.")
        print("Switching to: 🌟 Kokoro-82M Studio Neural Model (Local)\n")

        try:
            import kokoro_engine
            import audio_utils

            if not kokoro_engine.is_torch_available():
                print(f"⚠️ PyTorch is blocked by Windows Application Control: {kokoro_engine.get_torch_error()}\n")
                print("💡 To unblock PyTorch DLLs on your system, run this command in PowerShell:")
                print("   Get-ChildItem -Path \"$env:LOCALAPPDATA\\Programs\\Python\\Python312\\Lib\\site-packages\\torch\" -Recurse | Unblock-File\n")
                return

            voices = kokoro_engine.get_voices_for_language("en_US")
            print("Available Kokoro voices:")
            for index, v in enumerate(voices[:8]):
                print(f"  [{index}] {v['name']} ({v['gender']} - {v['style']})")

            choice = input(f"\nSelect voice index (0 to {min(7, len(voices)-1)}, press Enter for 0): ").strip()
            if choice.isdigit() and 0 <= int(choice) < len(voices):
                selected_voice = voices[int(choice)]["id"]
            else:
                selected_voice = voices[0]["id"]

            print(f"Selected voice: {selected_voice}")
            text = input("\nEnter text to convert into speech: ").strip()

            if not text:
                text = "Hello! This is Kokoro, your open-source neural text to speech generator."
                print(f"Using default text: '{text}'")

            print("Synthesizing neural audio...")
            audio_arr, sr = kokoro_engine.synthesize_kokoro(text, voice=selected_voice, speed=1.0)
            out_file, _ = audio_utils.process_and_save_audio(
                audio_data=audio_arr,
                sample_rate=sr,
                volume=1.0,
                audio_format="wav",
                prefix="cli_speech",
            )
            print(f"✅ Neural audio synthesized successfully!")
            print(f"📁 Saved to: {out_file.resolve()}")

        except Exception as exc:
            print(f"❌ Error during speech synthesis: {exc}")

if __name__ == "__main__":
    run_cli()
