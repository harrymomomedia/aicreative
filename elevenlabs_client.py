"""
ElevenLabs direct API client for TTS + voice cloning.

Functions:
  tts(text, voice_id, ...)     → synthesize speech, write to file
  list_voices()                → list all voices on the account (find voice_ids)
  clone_voice(name, files)     → instant voice clone from sample audio files

Models:
  eleven_turbo_v2_5             — cheapest, fastest, English+multilingual
  eleven_multilingual_v2        — higher quality, 29 languages
  eleven_v3                     — most expressive, supports audio tags like [laughs], [whispers]

Audio tags (v3 only): [laughs], [whispers], [sighs], [excited], [angry], [sad], [chuckles]
Use them inline in text:  "She's like, [exhales] you need to look at this."
"""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY not set in .env")

BASE = "https://api.elevenlabs.io"
HEADERS = {"xi-api-key": API_KEY}


def list_voices():
    """Return all voices on the account: [{voice_id, name, category, ...}, ...]."""
    r = requests.get(f"{BASE}/v1/voices", headers=HEADERS)
    r.raise_for_status()
    return r.json().get("voices", [])


def tts(
    text,
    voice_id,
    out_path,
    model_id="eleven_turbo_v2_5",
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    speed=1.0,
    output_format="mp3_44100_128",
):
    """Synthesize `text` with the given voice → write to out_path. Returns out_path.

    model_id: 'eleven_turbo_v2_5' | 'eleven_multilingual_v2' | 'eleven_v3'
    output_format: 'mp3_44100_128' (default), 'mp3_44100_192', 'pcm_44100', 'pcm_16000', etc.
    """
    url = f"{BASE}/v1/text-to-speech/{voice_id}"
    params = {"output_format": output_format}
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "speed": speed,
        },
    }
    r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, params=params)
    if not r.ok:
        raise RuntimeError(f"TTS failed ({r.status_code}): {r.text}")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)
    print(f"  Saved: {out_path} ({len(r.content) // 1024}KB)", flush=True)
    return out_path


def voice_changer(
    audio_path,
    voice_id,
    out_path,
    model_id="eleven_multilingual_sts_v2",
    stability=0.5,
    similarity_boost=0.75,
    style=0.0,
    output_format="mp3_44100_128",
    remove_background_noise=False,
    use_speaker_boost=True,
):
    """Speech-to-speech: convert input audio to target voice while preserving timing/cadence.

    Use this to normalize audio across multiple clips (each clip's voice → one consistent voice)
    WITHOUT losing the original mouth-movement timing (so lip-sync stays intact).

    model_id: 'eleven_multilingual_sts_v2' (default) | 'eleven_english_sts_v2'
    use_speaker_boost: ON (default) adds presence/energy (louder, more pushed); OFF = less aggressive.
    NOTE: STS has NO output-loudness param — it always normalizes hot (~-0.5 dBFS). Match the source
    level in POST (gain the VC output to the source clip's measured loudness).
    """
    url = f"{BASE}/v1/speech-to-speech/{voice_id}"
    params = {"output_format": output_format}
    voice_settings = {
        "stability": stability,
        "similarity_boost": similarity_boost,
        "style": style,
        "use_speaker_boost": use_speaker_boost,
    }
    import json as _json
    files = {"audio": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/mpeg")}
    data = {
        "model_id": model_id,
        "voice_settings": _json.dumps(voice_settings),
        "remove_background_noise": "true" if remove_background_noise else "false",
    }
    r = requests.post(url, headers=HEADERS, params=params, files=files, data=data)
    if not r.ok:
        raise RuntimeError(f"Voice changer failed ({r.status_code}): {r.text}")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)
    print(f"  Saved: {out_path} ({len(r.content) // 1024}KB)", flush=True)
    return out_path


def clone_voice(name, sample_files, description=None):
    """Instant voice clone from one or more audio samples (mp3/wav). Returns voice_id."""
    files = []
    for fp in sample_files:
        files.append(("files", (os.path.basename(fp), open(fp, "rb"), "audio/mpeg")))
    data = {"name": name}
    if description:
        data["description"] = description
    r = requests.post(f"{BASE}/v1/voices/add", headers=HEADERS, files=files, data=data)
    r.raise_for_status()
    voice_id = r.json().get("voice_id")
    print(f"  Cloned voice '{name}' → {voice_id}", flush=True)
    return voice_id


def scribe(audio_path, model_id="scribe_v1", biased_keywords=None,
           language_code=None, diarize=False, timestamps_granularity="word",
           tag_audio_events=False, num_speakers=None):
    """ElevenLabs Speech-to-Text (Scribe). Returns dict with 'text' + per-word timing.

    audio_path:        path to audio/video file (mp3/wav/m4a/mp4 etc.)
    model_id:          'scribe_v1' (default) | 'scribe_v1_experimental'
    biased_keywords:   list of words/phrases to bias toward, e.g. ['Chowchilla', 'Miha']
                       — KILLER for proper-noun-heavy QA. Each can include a bias
                       weight via 'word:N.N' (1.0 default, max ~5.0).
    language_code:     ISO-639-1 (e.g. 'en'); None = auto-detect.
    diarize:           identify speakers.
    timestamps_granularity: 'word' | 'character' | 'none'.
    tag_audio_events:  include [laughter], [music], etc.

    Returns: {
      "text": "full transcript",
      "language_code": "en",
      "language_probability": 0.99,
      "words": [{"text": "...", "start": 0.12, "end": 0.34, "type": "word"}, ...]
    }
    """
    url = f"{BASE}/v1/speech-to-text"
    import mimetypes
    mime = mimetypes.guess_type(audio_path)[0] or "application/octet-stream"
    files = {"file": (os.path.basename(audio_path), open(audio_path, "rb"), mime)}
    data = {"model_id": model_id}
    if biased_keywords:
        # ElevenLabs expects a JSON array string for the multipart 'biased_keywords' field
        import json as _json
        # If user passed plain strings, default to weight 1.5 (helpful but not overpowering)
        normalized = []
        for k in biased_keywords:
            if ":" in str(k):
                normalized.append(str(k))
            else:
                normalized.append(f"{k}:1.5")
        data["biased_keywords"] = _json.dumps(normalized)
    if language_code:
        data["language_code"] = language_code
    if diarize:
        data["diarize"] = "true"
        if num_speakers:
            data["num_speakers"] = str(num_speakers)
    if timestamps_granularity:
        data["timestamps_granularity"] = timestamps_granularity
    if tag_audio_events:
        data["tag_audio_events"] = "true"

    try:
        r = requests.post(url, headers=HEADERS, files=files, data=data, timeout=120)
    finally:
        files["file"][1].close()
    if not r.ok:
        raise RuntimeError(f"Scribe failed ({r.status_code}): {r.text[:500]}")
    return r.json()


def scribe_whisper_compat(audio_path, biased_keywords=None, language_code="en"):
    """Wrapper that returns Whisper-compatible JSON shape.

    Returns {
      "text": "...",
      "segments": [{"words": [{"start", "end", "word"}, ...]}],
      "language": "en",
    }

    Lets us drop-in replace whisper.transcribe() everywhere in this project
    (trim_silence.py reads segments[].words[], so this stays compatible).
    """
    raw = scribe(audio_path, biased_keywords=biased_keywords,
                 language_code=language_code, timestamps_granularity="word")
    words = []
    for w in raw.get("words", []):
        # Scribe yields type="word" entries plus separator "spacing" entries; keep only words
        if w.get("type") not in (None, "word"):
            continue
        words.append({"start": w.get("start"), "end": w.get("end"),
                      "word": w.get("text", "")})
    return {
        "text": raw.get("text", ""),
        "segments": [{"words": words}] if words else [],
        "language": raw.get("language_code", language_code),
    }
