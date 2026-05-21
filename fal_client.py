"""Thin fal.ai gateway for ElevenLabs models (this project's own client, NOT fal's SDK).

fal.ai hosts ElevenLabs models behind its own API + auth. Use this when we have a
FAL_KEY but no direct ELEVENLABS_API_KEY.

Auth:      Authorization: Key <FAL_KEY>
Sync run:  POST https://fal.run/<model-id>            → returns result directly (blocks)
Audio in:  `audio_url` accepts a public URL OR a base64 data URI (we use data URI for
           local files, so no separate storage upload step is needed for short clips).

Implemented:
  scribe / scribe_whisper_compat  — fal-ai/elevenlabs/speech-to-text (Scribe STT)

See module-level MODELS for the other ElevenLabs endpoints fal exposes.
"""
import base64
import mimetypes
import os

import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("FAL_KEY")
if not KEY:
    raise RuntimeError("FAL_KEY not set in .env")

BASE = "https://fal.run"
HEADERS = {"Authorization": f"Key {KEY}", "Content-Type": "application/json"}

MODELS = {
    "scribe": "fal-ai/elevenlabs/speech-to-text",
}


def _data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def scribe(audio_path, language_code="en", diarize=False, tag_audio_events=False,
           keyterms=None, timeout=300):
    """ElevenLabs Speech-to-Text via fal. Returns the raw fal/ElevenLabs JSON:
      {text, language_code, language_probability, words:[{text,start,end,type,speaker_id}]}

    keyterms: list of words/phrases to bias toward (Scribe V2 only — passed through;
              omit on V1). diarize / tag_audio_events default OFF for clean QA transcripts.
    """
    payload = {
        "audio_url": _data_uri(audio_path),
        "diarize": diarize,
        "tag_audio_events": tag_audio_events,
    }
    if language_code:
        payload["language_code"] = language_code
    if keyterms:
        payload["keyterms"] = list(keyterms)
    r = requests.post(f"{BASE}/{MODELS['scribe']}", headers=HEADERS, json=payload, timeout=timeout)
    if not r.ok:
        raise RuntimeError(f"fal Scribe failed ({r.status_code}): {r.text[:500]}")
    return r.json()


def scribe_whisper_compat(audio_path, biased_keywords=None, language_code="en"):
    """Whisper-compatible shape: {text, segments:[{words:[{start,end,word}]}], language}.

    Drop-in match for elevenlabs_client.scribe_whisper_compat so dissect / caption /
    trim consumers don't care which backend produced the transcript.
    """
    raw = scribe(audio_path, language_code=language_code, keyterms=biased_keywords)
    words = []
    for w in raw.get("words", []):
        if w.get("type") not in (None, "word"):
            continue
        words.append({"start": w.get("start"), "end": w.get("end"),
                      "word": w.get("text", "")})
    return {
        "text": raw.get("text", ""),
        "segments": [{"words": words}] if words else [],
        "language": raw.get("language_code", language_code),
    }
