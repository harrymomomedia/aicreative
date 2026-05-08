# CLAUDE.md — aicreative

End-to-end UGC ad cloning. Three halves:

1. **Dissect** competitor videos beat-by-beat (`dissect.py`)
2. **Generate** clips/images via KIE (`kie_client.py`)
3. **Voice** TTS + cloning via ElevenLabs direct (`elevenlabs_client.py`)

---

## The Workflow

1. User drops a competitor video in chat (path or URL — yt-dlp first if URL).
2. Run `dissect.py <video>` → produces `outputs/<videoname>/` with frames, transcript, scenes.
3. Read frames + transcript → write `analysis.md` with **Setting / Character / Camera / Beats / Tone / Style**.
4. User picks the model (Seedance/Kling/Veo) and provides their product/character assets.
5. Adapt the analysis into a model-specific prompt. **Show the full prompt in chat. Wait for explicit go.**
6. Call the matching `kie_client.generate_*` function. Save the result under `outputs/<videoname>/generations/`.

**Never run a generation without explicit user approval ("go", "run", "yes").**

---

## Available Models (KIE)

| Function | Model | Endpoint | Default settings |
|---|---|---|---|
| `generate_seedance` | `bytedance/seedance-2-fast` | `/jobs/createTask` | 480p, 9:16, audio on |
| `generate_kling` | `kling-3.0/video` | `/jobs/createTask` | mode `std` (720p), 9:16 |
| `generate_veo` | `veo3_fast` | `/veo/generate` (separate endpoint) | 720p, 9:16 |
| `generate_gpt_image` | `gpt-image-2-text-to-image` / `…-image-to-image` | `/jobs/createTask` | 1024x1024 |
| `generate_nano_banana` | `nano-banana-2` | `/jobs/createTask` | — |

All return `{"status": "success"|"failed", "urls": [...], "raw": {...}}`. Pipe `urls[0]` into `download(url, dest)`.

Veo polls a different endpoint (`/veo/record-info`) — handled internally.

---

## Voice (ElevenLabs direct)

| Function | Use |
|---|---|
| `tts(text, voice_id, out_path, ...)` | Synthesize speech → mp3 |
| `list_voices()` | Find voice_ids on the account |
| `clone_voice(name, sample_files)` | Instant voice clone from audio samples |

**Models** (pass via `model_id`):
- `eleven_turbo_v2_5` — cheapest, default. English/multilingual TTS.
- `eleven_multilingual_v2` — higher quality, 29 languages.
- `eleven_v3` — most expressive. Supports audio tags `[laughs] [whispers] [sighs] [excited] [sad]` inline in text. Use this for emotional UGC voiceovers.

ElevenLabs API is **synchronous** — no polling. The function blocks until audio is ready and writes the file.

---

## Picking the Right Video Model

- **Seedance Fast** — cheapest, best for vertical UGC clones. Default for talking-head, faceless, unboxing.
- **Kling 3.0** — better motion fidelity, multi-shot support, native audio. Use when Seedance fails moderation or motion looks wrong.
- **Veo 3 Fast** — best physics, longer reasoning. Reach for it when the scene has complex interaction (pouring, throwing, two characters).

---

## Dissect.py

```
.venv/bin/python dissect.py <video> [--model small] [--scene-threshold 0.3]
```

Whisper models: `tiny|base|small|medium|large`. Start with `small`. Bigger = more accurate, slower.

Outputs in `outputs/<videoname>/`:
- `metadata.json`, `scenes.json`, `transcript.json`
- `frames/` — one jpg per scene boundary
- `audio.wav`

You synthesize the analysis from those — don't invent details that aren't visible in the frames.

---

## Setup (one-time)

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

ffmpeg/ffprobe on PATH (`brew install ffmpeg`). KIE_API_KEY in `.env`.

---

## Prompt Rules (carry over from videogen)

- Word limit ~100-260 for Seedance prompts. Kling allows 0-2500.
- Reference images in Seedance prompts: `@(img1)`, `@(img2)` in order.
- Reference elements in Kling prompts: `@element_name` (defined under `kling_elements`).
- **Forbidden words:** cinematic, professional, stunning, 8k, studio, perfect.
- For faceless: avoid bare legs, bodycon, shorts — content moderation triggers. Use "light linen wide-leg trousers" etc.
- Always include "No on-screen text, no captions, no subtitles."
- End with a one-line emotional closing ("The feeling of...").

## If a Generation Fails or Returns 0KB

1. Check for bare-skin descriptions → swap for covered clothing.
2. Switch from v2v to i2v if moderation keeps tripping.
3. Try a different model (Seedance → Kling, etc.).

---

## Do Not

- Run generations without "go"/"run"/"yes".
- Combine `reference_image_urls` and `reference_video_urls` in one Seedance call.
- Commit `outputs/` or `.env` (both gitignored).
- Hardcode API keys — always from `.env`.
- Invent visual details. If the dissect frames don't show it, don't write it into the analysis.
