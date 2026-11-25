"""ollama_service.py — Local Ollama LLM integration service.

Connects to http://localhost:11434 for local LLM text generation,
grammar enhancement, tone rewriting, summarization, and translation.
"""

from __future__ import annotations

import json
from typing import Optional
import requests

DEFAULT_OLLAMA_HOST = "http://localhost:11434"


def check_ollama_status(host: str = DEFAULT_OLLAMA_HOST) -> dict[str, any]:
    """Test connection to local Ollama server and list available models.

    Returns:
        dict with keys: 'connected' (bool), 'models' (list[str]), 'error' (str|None).
    """
    host = host.rstrip("/")
    try:
        resp = requests.get(f"{host}/api/tags", timeout=2.5)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            return {
                "connected": True,
                "models": models,
                "error": None,
                "host": host,
            }
        return {
            "connected": False,
            "models": [],
            "error": f"Server returned status {resp.status_code}",
            "host": host,
        }
    except requests.exceptions.ConnectionError:
        return {
            "connected": False,
            "models": [],
            "error": "Ollama server is not running on this host/port.",
            "host": host,
        }
    except Exception as exc:
        return {
            "connected": False,
            "models": [],
            "error": str(exc),
            "host": host,
        }


def call_ollama(
    prompt: str,
    model: str,
    system_prompt: Optional[str] = None,
    host: str = DEFAULT_OLLAMA_HOST,
    temperature: float = 0.7,
) -> str:
    """Send a completion prompt to Ollama and return the generated text."""
    host = host.rstrip("/")
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": float(temperature),
        },
    }
    if system_prompt:
        payload["system"] = system_prompt

    resp = requests.post(f"{host}/api/generate", json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "").strip()


def generate_speech_script(
    topic: str,
    format_type: str = "Podcast Intro",
    tone: str = "Warm & Engaging",
    target_duration_seconds: int = 30,
    model: str = "llama3",
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """Generate a spoken speech script tailored for Text-to-Speech audio."""
    system = (
        "You are an expert scriptwriter specializing in spoken narration, podcasts, and video voiceovers. "
        "Write pure spoken text meant to be read aloud by an AI text-to-speech engine. "
        "Do not include stage directions, bracketed cues like [laughter] or [music], or speaker labels like 'Narrator:'. "
        "Write only the exact words that should be spoken."
    )
    approx_words = int(target_duration_seconds * 2.5)  # ~150 wpm = 2.5 words/sec
    prompt = (
        f"Write a {format_type} script about: '{topic}'.\n"
        f"Tone: {tone}.\n"
        f"Length: Approximately {approx_words} words (designed for ~{target_duration_seconds} seconds of speech).\n"
        f"Remember: Output only the spoken words, nothing else."
    )
    return call_ollama(prompt, model=model, system_prompt=system, host=host, temperature=0.7)


def improve_grammar(
    text: str,
    model: str = "llama3",
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """Enhance grammar, punctuation, and flow for natural text-to-speech pronunciation."""
    system = (
        "You are an editor for audio audiobooks and voiceovers. "
        "Correct all grammar and spelling errors, fix unnatural phrasing, and ensure smooth rhythm for voice narration. "
        "Return ONLY the corrected script without any explanations, headers, or quotes."
    )
    prompt = f"Improve and polish this text for spoken narration:\n\n{text}"
    return call_ollama(prompt, model=model, system_prompt=system, host=host, temperature=0.3)


def rewrite_tone(
    text: str,
    target_tone: str = "Professional",
    model: str = "llama3",
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """Rewrite text in a chosen conversational or dramatic tone."""
    system = (
        "You are a versatile voiceover writer. Rewrite the input text according to the requested tone. "
        "Maintain the core message, but make the phrasing perfectly fit the requested style. "
        "Return ONLY the rewritten spoken script without any intro or commentary."
    )
    prompt = f"Target Tone: {target_tone}\n\nOriginal Text:\n{text}"
    return call_ollama(prompt, model=model, system_prompt=system, host=host, temperature=0.7)


def summarize_for_speech(
    text: str,
    target_bullets: int = 3,
    model: str = "llama3",
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """Summarize long articles or documents into concise, flowing spoken sentences."""
    system = (
        "You are a news anchor and broadcast narrator. Summarize the key points of the input text into "
        "flowing, natural sentences that sound engaging when spoken aloud. Do not use bullet points or dashes. "
        "Return ONLY the summarized speech script."
    )
    prompt = f"Summarize this text into {target_bullets} key points spoken as natural sentences:\n\n{text}"
    return call_ollama(prompt, model=model, system_prompt=system, host=host, temperature=0.4)


def translate_for_speech(
    text: str,
    target_language: str = "Hindi",
    model: str = "llama3",
    host: str = DEFAULT_OLLAMA_HOST,
) -> str:
    """Translate text into target language formatted for speech synthesis."""
    system = (
        f"You are a professional multilingual translator. Translate the text into {target_language}. "
        "Ensure the translation sounds natural and colloquial when spoken out loud by native speakers. "
        "Output ONLY the translated text, no phonetic guides, notes, or romanization unless requested."
    )
    prompt = f"Translate the following text into natural {target_language} for speech synthesis:\n\n{text}"
    return call_ollama(prompt, model=model, system_prompt=system, host=host, temperature=0.3)
