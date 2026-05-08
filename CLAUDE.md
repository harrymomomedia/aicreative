# CLAUDE.md — aicreative

End-to-end UGC ad cloning. Four halves:

1. **Dissect** competitor videos beat-by-beat (`dissect.py`)
2. **Generate** clips/images via KIE (`kie_client.py`)
3. **Voice** TTS + cloning via ElevenLabs direct (`elevenlabs_client.py`)
4. **Caption** burn-in TikTok-style captions (`caption.py`)

> See **`LEARNINGS.md`** for accumulated gotchas. Read it before starting a new project.

---

## The Workflow

1. User drops a competitor video in chat (path or URL — yt-dlp first if URL).
2. Run `dissect.py <video>` → produces `outputs/<videoname>/` with frames, transcript, scenes.
3. Read frames + transcript → write `analysis.md` with **Setting / Character / Camera / Beats / Tone / Style**.
4. User picks the model (Seedance/Kling/Veo) and provides their product/character assets.
5. Generate **4–6 reference characters in parallel** with GPT Image 2 → user picks one anchor.
6. Adapt the analysis into a model-specific prompt. **Show the full prompt in chat. Wait for explicit go.**
7. **Test proper-noun pronunciation at 4s** before committing to longer clips.
8. Generate clips (typically 3 for a 35s ad: 14 + 11 + 10s).
9. Stitch with ffmpeg `concat` demuxer (lossless if codec params match).
10. Add b-rolls via `filter_complex` (replace video segments, audio passthrough).
11. Caption with `caption.py` (Whisper → PIL → ffmpeg overlay).
12. Optional variants: same script, different character anchor.

**Never run a generation without explicit user approval ("go", "run", "yes").**

---

## Available Models (KIE)

| Function | Model | Endpoint | Defaults |
|---|---|---|---|
| `generate_seedance` | `bytedance/seedance-2-fast` | `/jobs/createTask` | 480p (496×864), 9:16, audio on, **min 4s, max 15s** |
| `generate_kling` | `kling-3.0/video` | `/jobs/createTask` | mode `std` (720p), 9:16 |
| `generate_veo` | `veo3_fast` | `/veo/generate` (separate endpoint) | 720p (720×1280), 9:16 |
| `generate_gpt_image` | `gpt-image-2-text-to-image` / `…-image-to-image` | `/jobs/createTask` | `aspect_ratio="9:16"`, `resolution="2K"` |
| `generate_nano_banana` | `nano-banana-2` | `/jobs/createTask` | — |

All return `{"status": "success"|"failed", "urls": [...], "raw": {...}}`. Pipe `urls[0]` into `download(url, dest)`.

Veo polls a different endpoint (`/veo/record-info`) — handled internally.

**Resolution mismatch warning:** Seedance 480p (496×864) won't concat cleanly with Veo/Kling 720p (720×1280). Pick one model per ad, or rescale.

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
- `eleven_v3` — most expressive. Supports audio tags `[laughs] [whispers] [sighs] [excited] [sad]` inline. Use for emotional UGC.

ElevenLabs API is **synchronous** — no polling. Function blocks until audio is ready and writes the file.

**When to use:** Seedance has no voice ID — voice can drift across multi-clip ads. ElevenLabs is the answer for true voice consistency. Workflow: generate Seedance with audio (guide track) → replace audio with ElevenLabs (fixed `voice_id`) → optionally lip-sync with Sync.so via KIE.

---

## Captions (`caption.py`)

```
.venv/bin/python caption.py <input.mp4> --out <output.mp4>
```

Pipeline: extract audio → Whisper word-level transcribe → chunk into 3–4 word phrases (split on >0.35s pauses or word count) → render each as PIL PNG (Arial Black, white fill, black stroke, max 2 lines, **adaptive font shrink**) → ffmpeg `overlay` filter with `enable=between(t,...)`.

**Why PIL+overlay instead of `subtitles=` filter:** Homebrew ffmpeg lacks libass.

**Style defaults** (TikTok/Submagic look):
- Font size: ~3.5% of frame height
- Outline: ~8% of font size, scales with adaptive shrink
- Position: 16% from bottom (lower-third)
- Max 2 lines per chunk; auto-shrinks 8% per attempt up to 10× until it fits

**Whisper proper-noun substitutions** live in `caption.py` `SUBSTITUTIONS` dict at top. When Whisper mistranscribes a proper noun (e.g., "Chow-chilluh" → "Chow Chiller"), add to dict — applies before render.

---

## Picking the Right Video Model

- **Seedance Fast** — cheapest, best for vertical UGC clones. Default for talking-head, faceless, unboxing.
- **Kling 3.0** — better motion fidelity, multi-shot support, native audio. Use when Seedance fails moderation or motion looks wrong.
- **Veo 3 Fast** — best physics, longer reasoning. Reach for it when the scene has complex interaction (pouring, throwing, two characters). **Different endpoint, different output dims.**

---

## Dissect.py

```
.venv/bin/python dissect.py <video> [--model small] [--scene-threshold 0.3] [--interval 1.5]
```

Whisper models: `tiny|base|small|medium|large`. Start with `small`. Bigger = more accurate, slower.

Auto-falls back to interval-sampling (every `--interval` seconds) when scene-detection finds zero cuts. Important for single-shot UGC (talking heads).

Outputs in `outputs/<videoname>/`:
- `metadata.json`, `scenes.json`, `transcript.json`
- `frames/` — one jpg per scene boundary AND every `--interval` seconds
- `audio.wav`

Synthesize the analysis from those — don't invent details that aren't visible in the frames.

---

## Setup (one-time)

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

ffmpeg/ffprobe on PATH (`brew install ffmpeg`). `KIE_API_KEY` and `ELEVENLABS_API_KEY` in `.env`.

---

## Prompt Rules

- Word limit ~100–260 for Seedance prompts. Kling allows 0–2500.
- Reference images in Seedance prompts: `@(img1)`, `@(img2)` in order.
- Reference elements in Kling prompts: `@element_name` (defined under `kling_elements`).
- **Forbidden words:** cinematic, professional, stunning, 8k, studio, perfect.
- **Photorealism imperfections** are required: "visible pores, fine lines, faint under-eye darkness, dry lips, slight asymmetry, no makeup, no beauty mode, no retouching, no filter".
- For faceless: avoid bare legs, bodycon, shorts — content moderation triggers. Use "light linen wide-leg trousers" etc.
- Always include "No on-screen text, no captions, no subtitles."
- End with a one-line emotional closing ("The feeling of...").
- **i2v needs explicit motion direction** — "STEPS INTO" not "moves toward."

---

## Pronunciation (proper nouns)

Seedance native audio mangles proper nouns. **Always test at 4s** before committing to longer clips.

Phonetic respells that work:
- `Chowchilla` → `Chow-chilluh` (hyphen + "uh" ending)
- `Chino` → `Chee-no`
- `Folsom` → usually fine
- `Represa` → `Re-press-uh`

Pronunciation can drift at longer durations even when 4s test was clean. If a respell fails at 14s, try a more phonetically explicit form, or plan to dub via ElevenLabs at the end.

---

## Stitching multi-clip ads

For 3-clip ads (e.g., 14 + 11 + 10s split):

```bash
# Lossless concat when codec params match
printf "file '/abs/part1.mp4'\nfile '/abs/part2.mp4'\nfile '/abs/part3.mp4'\n" > /tmp/concat.txt
ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy final.mp4
```

**Trim trailing content** by silence detection:
```bash
ffmpeg -i partN.mp4 -af silencedetect=noise=-30dB:d=0.4 -f null - 2>&1 | grep silence
# pick midpoint of a >0.4s pause as cut point
ffmpeg -y -i partN.mp4 -t 8.5 -c copy partN_trimmed.mp4
```

**Use absolute paths in the concat list** — relative paths resolve relative to the list file, not the cwd.

---

## B-roll insertion (filter_complex)

Replace video segments while keeping the source's audio continuous:

```bash
ffmpeg -y \
  -i source.mp4 -i broll1.mp4 -i broll2.mp4 \
  -filter_complex "\
[0:v]trim=0:4,setpts=PTS-STARTPTS[s1];\
[1:v]trim=0:2,setpts=PTS-STARTPTS[b1];\
[0:v]trim=6:17,setpts=PTS-STARTPTS[s2];\
[2:v]trim=0:3,setpts=PTS-STARTPTS[b2];\
[0:v]trim=20,setpts=PTS-STARTPTS[s3];\
[s1][b1][s2][b2][s3]concat=n=5:v=1:a=0[vout]" \
  -map "[vout]" -map 0:a -c:v libx264 -preset fast -crf 19 -c:a copy \
  out.mp4
```

Math must add up: each segment's length × count = source duration. Audio passes through `-map 0:a -c:a copy`.

**Always show the character's face first** (no b-roll at 0–4s) to establish identity. Aim for **20% b-roll, 80% face** ratio.

**Multi-reference Seedance blends, doesn't storyboard.** Don't pass 3 images expecting 3 hard cuts — generate separate clips and concat.

---

## If a Generation Fails or Returns 0KB

1. Check for bare-skin descriptions → swap for covered clothing.
2. Switch from v2v to i2v if moderation keeps tripping.
3. Try a different model (Seedance → Kling, etc.).
4. For sensitive contexts: encode visually (institutional pants, weary look) instead of naming ("victim", "abuse", "prison").

---

## Reference character generation pattern

For each new ad, generate **4–6 candidates in parallel** via GPT Image 2, varying:
- Setting (kitchen/bedroom/car/porch/hallway/garage)
- Time of day / lighting
- Hair / clothing / age
- Emotional register

Save as `outputs/<videoname>/reference/character_<letter>_<setting>.png`.

User picks one anchor → use the same image across all clips of that ad for character consistency.

For variants (A/B test same script with different character), pick a different anchor and re-run the clip generation phase.

---

## Do Not

- Run generations without "go"/"run"/"yes".
- Combine `reference_image_urls` and `reference_video_urls` in one Seedance call.
- Commit `outputs/` or `.env` (both gitignored).
- Hardcode API keys — always from `.env`.
- Invent visual details. If the dissect frames don't show it, don't write it into the analysis.
- For legal services copy: omit "potential" before "compensation" — it's regulated.
- Mix output resolutions across clips of the same ad (Seedance 480p + Veo 720p won't concat clean).
