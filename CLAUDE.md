# CLAUDE.md — aicreative

End-to-end UGC ad cloning. Four halves:

1. **Dissect** competitor videos beat-by-beat (`dissect.py`)
2. **Generate** clips/images via KIE (`kie_client.py`)
3. **Voice** TTS + cloning via ElevenLabs direct (`elevenlabs_client.py`)
4. **Caption** burn-in TikTok-style captions (`caption.py`)

---

## The Workflow

1. User drops a competitor video in chat (path or URL — yt-dlp first if URL).
2. Run `dissect.py <video>` → produces `outputs/<videoname>/` with frames, transcript, scenes.
3. Read frames + transcript → write `analysis.md` with **Setting / Character / Camera / Beats / Tone / Style**.
4. User picks the model (Seedance/Kling/Veo) and provides their product/character assets.
5. Generate **4–6 reference characters in parallel** with GPT Image 2 → user picks one anchor.
6. Adapt the analysis into a model-specific prompt. **Show the full prompt in chat. Wait for explicit go.**
7. **Test proper-noun pronunciation at the shortest viable duration** before committing to longer clips.
8. Generate clips. Clip count depends on model max-duration: **Veo 3 Fast = 8s/clip** (~8 clips per minute of ad), **Seedance = up to 15s/clip** (~3-4 clips per minute), **Kling = up to ~10s/clip**. Pick clip boundaries on natural speech breaks.
9. **Dissect every generated clip immediately** with `dissect.py --interval 1.0`. Review opening, midpoint, and end frames + Whisper transcript. Verify: identity match, visual age, emotional tone lock, camera lock (no drift), motion fidelity, lip-sync, proper-noun pronunciation, audio quality. **Do not proceed to the next clip or to stitching until the current clip passes this QA gate.**
10. **Trim silence; chain via clip-1 anchor.** Per-clip post-QA flow:
    a. `scripts/trim_silence.py <clip.mp4> <transcript.json>` (start/end-only by default — preserves internal pacing). Outputs `<clip>_trimmed.mp4`.
    b. **For clips 2-N: use a clean frame from CLIP 1 as the `IMAGE_2_VIDEO` first-frame**, NOT the last frame of the previous clip. Last-frame chaining compounds quality degradation across N generations; clip-1 anchor keeps quality consistent throughout the ad. Small visible "reset" between clips is acceptable for short-form UGC pacing. (Last-frame chain is an alternate technique — see "Stitching multi-clip ads" — for a "fake one-take" feel where you accept the drift.)
    c. **Rotate anchor frames across clips 2-N** — extract 5-7 different clean frames from clip 1 at varied timestamps (e.g., t=0.5s, 2.0s, 3.5s, 5.0s, 6.5s) and assign a different one to each subsequent clip. Optionally pull 1-2 more from clip 2 once it lands for extra variety. **Never reuse a single anchor URL for every clip** — that produces visually identical clip starts and reads as templated/unnatural on UGC playback. Pattern in `scripts/chowchilla_a2_variations.py`: `get_anchor_url()` checks `clip{N}_anchor_url.txt` per-clip first, falls back to `clip1_anchor_url.txt`. See `feedback_clip_anchor_rotation.md` memory.
11. **Audit voice consistency** with `scripts/audio_match.py <clip1_trimmed.mp4> <clip2_trimmed.mp4> ...`. If voice loudness span > ~10dB or several clips fail tolerance, **normalize via ElevenLabs voice changer** (see "Audio normalization" section). This single step fixes Veo's biggest weakness — its TTS varies wildly between generations.
12. Stitch with ffmpeg `concat` demuxer (lossless if codec params match).
13. Add b-rolls via `filter_complex` (replace video segments, audio passthrough).
14. Caption with `caption.py` (Whisper → PIL → ffmpeg overlay).
15. Optional variants: same script, different character anchor.

**Iteration cadence:** generate freely — no explicit "go" needed per clip. After each clip, dissect per step 9. If it passes QA, advance to the next clip. If it fails, you have up to **3 re-generation attempts on the same clip** to fix the issue (adjust the prompt, the seed, the reference image, or the model). After 3 failed attempts, stop and escalate to the user for guidance instead of burning budget.

---

## Available Models

### Provider routing (per-model)

User-set rule: **route each model to its cheapest reliable host**, not all through KIE.

| Model | Provider | Module | Cost | Notes |
|---|---|---|---|---|
| **Veo 3 / 3.1 Fast** | **Poyo** | `poyo_client.generate_veo` | **$0.10/clip** flat | Cheapest verified Veo. See "Poyo gotchas" below. |
| **Seedance 2.0 Fast** | OpenRouter | (no client built — user pref) | $0.45-0.97/clip (token-based) | KIE Seedance is actually 20% cheaper ($0.36-0.80) but user prefers OpenRouter for consolidation. |
| **Kling 3.0** | KIE | `kie_client.generate_kling` | varies | Unchanged. |
| **nano-banana-2** | KIE | `kie_client.generate_nano_banana` | varies | Unchanged. |
| **gpt-image-2** (t2i / i2i) | OpenAI direct | `openai_image.generate_image` | bundled in OpenAI subscription | **NEVER use `kie_client.generate_gpt_image`** — proxy adds cost. |
| **ElevenLabs** (TTS / clone / voice_changer) | ElevenLabs direct | `elevenlabs_client` | per-character | 5 concurrent max — throttle when batching. |

Memory: `project_video_provider_routing.md` — confirm before bulk-running new models since pricing tiers shift.

### KIE (for Kling / nano-banana)

| Function | Model | Endpoint | Defaults |
|---|---|---|---|
| `generate_kling` | `kling-3.0/video` | `/jobs/createTask` | mode `std` (720p), 9:16 |
| `generate_nano_banana` | `nano-banana-2` | `/jobs/createTask` | — |
| `generate_seedance` | `bytedance/seedance-2-fast` | `/jobs/createTask` | 480p (496×864), 9:16, audio on, **min 4s, max 15s**. **NOT preferred — route to OpenRouter per user rule.** |
| `generate_veo` | `veo3_fast` | `/veo/generate` | 720p (720×1280), 9:16. **NOT preferred — route to Poyo for $0.10/clip vs $0.30.** |

All return `{"status": "success"|"failed", "urls": [...], "raw": {...}}`. KIE Veo polls a different endpoint (`/veo/record-info`) — handled internally.

**KIE upload endpoint stays useful** for hosting reference images:
```
POST https://kieai.redpandaai.co/api/file-stream-upload  → returns {data.downloadUrl}
```
Use this even when Veo runs via Poyo — image hosting is a separate concern from generation.

### Poyo gotchas (Veo 3.1 Fast at $0.10/clip)

- **`generation_type: "frame"` requires EXACTLY 2 `image_urls`.** For clip-1 anchor pattern, pass the anchor twice (start = end). API rejects 1-image with 400. Client at `poyo_client.py`.
- **Submit rate limit: 20 requests per 10 seconds (account-wide).** Batches >20 in parallel will 429. Use `max_workers=10` in ThreadPoolExecutor — generation takes 90-180s so sustained submit rate stays under limit.
- **Status polling rate limit: 1 request per 2 seconds PER TASK.** The built-in `_poll(interval=5)` is safe. Don't manually curl the status endpoint while a script is polling — you'll trip the limit and confuse the script.
- Async model: POST `/api/generate/submit` returns `task_id`, then poll `/api/generate/status/{task_id}` until `status: finished`. Files in `data.files[].file_url`, valid 24h.
- `veo3.1-fast` is the model id (not `veo3_fast`). Quality model `veo3.1-quality` exists too — costlier.

**Resolution mismatch warning:** Seedance 480p (496×864) won't concat cleanly with Veo/Kling 720p (720×1280). Pick one model per ad, or rescale.

### GPT Image — OpenAI direct (NOT KIE)

| Function | Module | Auth | Notes |
|---|---|---|---|
| `generate_image` | `openai_image.py` | `OPENAI_API_KEY` | Text-to-image and image-to-image via OpenAI's `gpt-image-1` (or successor). **Do not use `kie_client.generate_gpt_image`.** |

`kie_client.generate_gpt_image` exists but is **deprecated for this project** — it routes through KIE's GPT Image proxy and adds cost/latency. Always import from `openai_image` instead.

---

## Voice (ElevenLabs direct)

| Function | Use |
|---|---|
| `tts(text, voice_id, out_path, ...)` | Synthesize speech → mp3 (text → audio, fresh timing) |
| `voice_changer(audio_path, voice_id, out_path, ...)` | Speech-to-speech: convert input audio to target voice **preserving timing/prosody** (audio → audio, lip-sync intact) |
| `list_voices()` | Find voice_ids on the account |
| `clone_voice(name, sample_files)` | Instant voice clone from audio samples (~6s minimum, more is better) |

**TTS models** (pass via `model_id` to `tts()`):
- `eleven_turbo_v2_5` — cheapest, default. English/multilingual TTS.
- `eleven_multilingual_v2` — higher quality, 29 languages.
- `eleven_v3` — most expressive. Supports audio tags `[laughs] [whispers] [sighs] [excited] [sad]` inline. **TTS-only, NOT available for voice_changer.**

**Voice changer (STS) models** — use with `voice_changer()`:
- `eleven_multilingual_sts_v2` — default, 29 languages, latest STS model.
- `eleven_english_sts_v2` — English only.

ElevenLabs API is **synchronous** — no polling. Function blocks until audio is ready and writes the file.

**When to use which:**
- **All KIE video models (Veo/Kling/Seedance) have non-deterministic voice/audio quality** — voice loudness can span 40dB across clips, mic character shifts, noise floor varies. The canonical fix is ElevenLabs.
- `voice_changer()` is the default normalization: keeps the source's pacing/prosody (so lip-sync stays intact) but unifies voice timbre/loudness. See "Audio normalization" section.
- `tts()` is for cases where you want to fully replace the audio script (different words than what was generated) and you're willing to redo lip-sync via Sync.so.

---

## Captions — two scripts, two skills

**Default rule: DO NOT burn captions onto deliverables** (memory `feedback_skip_burned_captions`). The user adds captions themselves in their post-production tool. Only run the caption pipeline when explicitly asked ("caption this", "add subtitles", "Submagic style", "with the disclaimer").

### `scripts/caption_styled.py` — Submagic / TikTok yellow-text style (canonical)

The skill `yellow-text-sub` documents this. Per-word yellow text highlight (or yellow box), all-caps Arial Black, optional legal disclaimer overlay at bottom.

```bash
.venv/bin/python scripts/caption_styled.py <in.mp4> --out <out.mp4> --highlight-style yellow_text
```

| Setting | Default | Notes |
|---|---|---|
| `--highlight-style` | `box` | Pass `yellow_text` for yellow fill instead of yellow rect behind white. **User preference: `yellow_text`.** |
| `--font-ratio` | `0.0336` | ~3.4% of frame height. Campaign-approved. |
| `--vertical-pos` | **auto by aspect** | `0.72` for 9:16, `0.82` for 4:5. Caption always lands just below the chin regardless of aspect. |
| `--disclaimer-start / --disclaimer-end` | `7.0 / 12.0` | Hard-cut window for disclaimer overlay. |
| `--disclaimer-text` | Pulaski/Jones campaign | Skill `pulaski-jones-disclaimer` has the verbatim text. |
| `--no-disclaimer` | — | Skip the disclaimer pass entirely. |

**Whisper proper-noun substitutions** live in `caption_styled.py:SUBSTITUTIONS`. Add new mistranscriptions there. Already covers `MIHA→MIJA` and the `CHOWCHILLA` variants.

### `scripts/caption.py` — legacy classic captions

Older style — white text + black outline, no per-word highlight. Kept for ad-hoc previews. Don't use for deliverables.

### Yellow-rect-positioning gotcha (lesson from this session)

When rendering the yellow highlight rect behind a word, **use `draw.textbbox()` to measure where the text will actually land**, NOT `cur_y + line_h`. The latter includes line-leading and makes the rect hang below the text. Already fixed in `caption_styled.py` — preserve when refactoring.

---

## Picking the Right Video Model

- **Seedance Fast** — cheapest, best for vertical UGC clones. Default for talking-head, faceless, unboxing.
- **Kling 3.0** — better motion fidelity, multi-shot support, native audio. Use when Seedance fails moderation or motion looks wrong.
- **Veo 3 Fast** — best physics, longer reasoning. Reach for it when the scene has complex interaction (pouring, throwing, two characters). **Different endpoint, different output dims.**

---

## Dissect.py — QA gate for generated clips

```
.venv/bin/python dissect.py <video> [--model small] [--interval 1.5] [--no-ocr]
```

Whisper models: `tiny|base|small|medium|large`. Start with `small`. Bigger = more accurate, slower.

Auto-falls back to interval-sampling (every `--interval` seconds) when scene-detection finds zero cuts. Important for single-shot UGC (talking heads).

Outputs in `outputs/<videoname>/`:
- `metadata.json`, `scenes.json`, `transcript.json`
- `frames/` — one jpg per scene boundary AND every `--interval` seconds
- `audio.wav`
- **`burned_text.json`** — per-frame OCR results + `{flagged: bool, reason}` summary. Flags clips where Veo hallucinated burned-in subtitle text (~10% of generations even with the NO-TEXT lock).

### Burned-text OCR (step 6/6)

Requires `brew install tesseract`. Skip with `--no-ocr` if not installed.

A clip is flagged when:
- A single frame has **2+ words at confidence ≥60** outside the corner watermark, OR
- The **same word repeats across 2+ frames** (stable text = real burn-in, not noise)

`scripts/scan_burned_text.py` exists for batch scanning multiple clips at once (predates the dissect integration). Either tool works.

### dissect.py concurrency limit — MAX 2 PARALLEL

Memory: `feedback_dissect_concurrency`. Each dissect loads the Whisper model (~1GB), extracts frames, writes many small files. Running ~10 in parallel CRASHES the host.

```bash
# RIGHT — cap at 2:
seq 1 10 | xargs -P 2 -I {} .venv/bin/python dissect.py clips/clip{}.mp4 --interval 1.0 --model small

# WRONG — for/wait spawns all 10 simultaneously:
for n in {1..10}; do .venv/bin/python dissect.py clip${n}.mp4 & ; done; wait
```

### Tesseract on macOS — invoke via stdin

The homebrew tesseract install can't read files directly from `/tmp/` due to sandbox. Always pipe via stdin:

```python
ocr = subprocess.run(["tesseract", "stdin", "-", "--psm", "11", "-l", "eng", "tsv"],
                     input=img_bytes, capture_output=True)
```

Also: **TSV `conf` column is a FLOAT, not int**. Parse `float(parts[10])`. Filtering by `int(conf)` silently drops everything (ValueError).

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

## Pronunciation (proper nouns and non-English words)

KIE video models' native TTS frequently mangles proper nouns and non-English words. **Test pronunciation at the shortest viable duration** before committing to longer clips.

### General rule

When TTS mispronounces a word, **rewrite it phonetically using English-syllable approximations** until the closed-loop test passes:

> Generate the clip → dissect → check Whisper transcript. If Whisper renders the **intended target word** (or an audibly equivalent rendering), the TTS got close enough.

**Don't revert phonetic spellings just because Whisper transcribed them differently than the original word.** A respell that produces "Miha" or "me, huh?" for `Mee-hah` is correct — it's saying *Mija* in Spanish (/ˈmi.xa/), which is the goal.

### Heuristics

- **Hyphenate by syllable** to force separation: `Chowchilla → Chow-chilluh`, `Represa → Re-press-uh`
- **Spanish `j` → English `h`**: `Mija → Mee-hah`, `jefe → heh-feh`, `mojo → moh-hoh`
- **Spanish trailing `a` → English `uh` or `ah`**: open-syllable Spanish endings sound flat in English TTS; the `uh` cue closes them naturally
- **Spanish `i` → English `ee`**: `Mija → Mee-hah`, `Chino → Chee-no`
- **Spanish `ll` → English `y`**: `tortilla → tor-tee-yuh`, `pollo → poh-yoh`
- **Stress with capitals when needed**: `Chow-CHILL-uh` (forces emphasis on second syllable)

### When to give up and dub

After ~2 respell attempts that still fail, **stop and plan an ElevenLabs voice-changer or TTS dub** for that clip. Don't burn budget on more retries — a dub fixes pronunciation deterministically.

### Long-form drift

Pronunciation that's clean at 4s can drift in 8s+ clips. If a clip-1 test passes but clip-7 mangles the same word, fall back to: (a) rewrite the script to avoid the word, or (b) dub via ElevenLabs.

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

### Chain technique: clip-1 anchor (default) vs last-frame (alternate)

**Default — clip-1 anchor:** for clips 2-N, use a clean frame from CLIP 1 as the `IMAGE_2_VIDEO` first-frame. Quality stays consistent across all clips because every clip has the same reference baseline. Small visible "reset" between clips is acceptable for short-form UGC. **Use this in 90% of cases.**

**Alternate — last-frame chain:** for a "fake one-take" feel where you want true scene-to-scene continuity (no resets), chain each clip's first-frame to the previous clip's last-frame. Caveat: quality compounds-degrades across N generations because each clip's input is the previous clip's already-degraded output.

```bash
# Extract last clean frame from previous clip (avoid mid-blink/mid-syllable)
ffmpeg -y -sseof -0.05 -i clipN.mp4 -frames:v 1 -q:v 2 /tmp/clipN_last.jpg

# Upload to KIE for the next clip's first-frame reference
curl -sS -X POST https://kieai.redpandaai.co/api/file-stream-upload \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -F "file=@/tmp/clipN_last.jpg" -F "uploadPath=aicreative" | jq -r '.data.downloadUrl'
```

Then use that URL as `imageUrls[0]` with `generationType: "IMAGE_2_VIDEO"` for clip N+1. If the last frame is mid-syllable / mid-blink / glance off-camera, **pick an earlier clean frame** (e.g., extract at -0.5s instead of the very end) — Veo will start the next clip in whatever state the input frame is in.

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

## Veo 3 gotchas (learned the hard way)

### Audio is non-deterministic
Veo's TTS varies dramatically between generations on the SAME prompt:
- Voice loudness can span ~40dB across an ad's clips
- Background noise floor varies ±10dB
- Spectral character ("mic feel") shifts between clips

**No prompt fix exists.** The canonical normalization is ElevenLabs voice changer — see "Audio normalization" section.

### Watermark is random
Veo sometimes (~30-50% of generations) burns a "Veo" watermark in the bottom-right corner. Same payload can produce a clean clip or a watermarked one. **No flag exposed via KIE.** Mitigations:
- Re-roll until clean
- OR crop bottom ~50px in post (changes aspect slightly)

### Improvisation patterns
Veo will frequently:
1. **Insert filler words** between sentences (often Spanish-sounding gibberish like "Hoeya", "Bacchiazade")
2. **Double proper nouns** ("Miha, Miha")
3. **Add a trailing word** at the end as if starting a new sentence ("And…", "I…", "So…")
4. **Drop the first word** ("I'm" missing at clip start)
5. **Burn hallucinated subtitle text into the frame** — even WITH the "ABSOLUTELY NO ON-SCREEN TEXT" lock, ~10% of clips have garbled text at the bottom (e.g., "sopussol maret beong neolia?", "Juist ex shm sister", "Ex't ife the wbout"). **Cannot be fixed in post — must re-roll the clip.** Use the OCR step in `dissect.py` to flag these automatically.
6. **News-headline phrasing triggers newscaster TTS delivery** — if the dialogue reads like an article intro ("Women from the California women's prisons are finding out they may qualify…"), Veo's TTS shifts to a formal/energetic announcer voice that doesn't match the intimate UGC tone of the rest of the ad. **Fix: rewrite the line to be conversational** ("Women in California prisons may qualify for compensation. For what the guards did.") AND add a tone hint like "SAME intimate quiet tone as the rest, NOT news-anchor, NOT informational, NOT energetic — she's repeating what she just read in her own quiet voice."
7. **Quote-framing ("And it said…", "She's like…") sometimes triggers a second, off-screen narrator voice** for the framing phrase. The framing is rendered by a DIFFERENT speaker than the main character. Fix: drop the framing entirely. Just have her say the line directly.
8. **Doubled lines** — Veo occasionally repeats the last sentence ("Tap the button. See if you qualify. See if you qualify."). Must re-roll. Detect via Whisper transcript word-count.

### Required prompt clauses to lock dialogue

Every Veo clip's prompt should include these clauses verbatim (they cut improvisation from ~50% to ~10%):

```
CRITICAL — DIALOGUE LOCK: She speaks in ENGLISH ONLY (except where a phonetic respell is explicitly listed below). Do NOT add any Spanish words, fillers like "uh", "um", "like", "you know", "so", or any extra words beyond what is listed. Do NOT add any trailing words at the end. Speak ONLY the words listed in SPOKEN DIALOGUE below, in order, with no insertions and no improvisation, and STOP speaking after the final word.

SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "..."
```

Plus, for visual consistency:

```
CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip her eyes stay OPEN and looking DIRECTLY at the camera lens. She does NOT close her eyes during dialogue.

CRITICAL — NO SMILE EVER: Throughout the entire clip her mouth stays in a SOFT NEUTRAL LINE. ZERO upturned corners. ZERO smile.
```

### Trailing-word workaround
Even with the lock, Veo sometimes adds a trailing word. Detect via Whisper word-timing in dissect output:

```python
# In transcript.json: find the intended last word's `end` time
# Then trim the mp4 with ffmpeg
ffmpeg -y -i clip.mp4 -t <end_time + 0.2> -c:v libx264 -preset fast -crf 19 -c:a aac out.mp4
```

`scripts/trim_silence.py` handles leading/trailing silence automatically; manual `-t` trim is for cases where Veo added an unwanted full word past the script.

---

## Audio normalization

When voice/audio quality varies across clips (always — Veo TTS is non-deterministic), normalize. **Two tools, two use cases:**

### Tier 1: `ffmpeg loudnorm` (default — simpler, safer)

```bash
ffmpeg -y -i clipN_trimmed.mp4 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:v copy -c:a aac -b:a 192k \
  clipN_norm.mp4
```

EBU R128 loudness normalization. Brings voice loudness within ~2.5dB across clips. Lip-sync intact. **No API cost.** Use this as the default normalization step in the production pipeline (between trim and crop).

### Tier 2: ElevenLabs voice_changer (when timbre/mic-character drifts)

`loudnorm` only fixes LOUDNESS. If one clip sounds "from a different mic" (different spectral centroid, different noise floor) compared to the others — that's a timbre problem, not a loudness problem. Use voice_changer.

**Important learnings from this session:**
- Voice_changer normalizes TIMBRE successfully (centroid drift drops from ±15% to ±3%).
- But voice_changer can MAKE LOUDNESS VARIANCE WORSE — the cloned voice's output cleanliness varies per clip, so output loudness diverges. Always run `loudnorm` AFTER voice_changer if you use it.
- **ElevenLabs has a 5-concurrent-request limit.** Use `max_workers=4` in ThreadPoolExecutor.
- Don't bother voice-changing if `audio_match.py` only flags a few clips on LOUDNESS — `loudnorm` alone is enough. Only invoke voice_changer when CENTROID or NOISE differs significantly (>10%/4dB).

### Recipe (for timbre normalization)

When voice quality varies across clips (always — Veo TTS is non-deterministic), normalize them all through one consistent voice using ElevenLabs **voice changer** (speech-to-speech). This preserves each clip's prosody/timing/lip-sync and only swaps the voice timbre/loudness.

### Recipe

```bash
# 1. Extract clip 1's audio as the voice clone source (~6s minimum is enough)
ffmpeg -y -i clip1_trimmed.mp4 -vn -ar 44100 -ac 1 /tmp/voice_source.mp3

# 2. Clone the voice via ElevenLabs (returns voice_id)
.venv/bin/python -c "
from elevenlabs_client import clone_voice
print(clone_voice('character_name', ['/tmp/voice_source.mp3']))
"
# → outputs voice_id like 'k4dxI3hVwttg9flzt8Bm'

# 3. Run each clip's audio through voice_changer with that voice_id
.venv/bin/python -c "
from elevenlabs_client import voice_changer
for n in range(1, 11):
    voice_changer(
        f'/tmp/clip{n}_orig.mp3',
        'VOICE_ID_FROM_STEP_2',
        f'/tmp/clip{n}_voice.mp3',
        model_id='eleven_multilingual_sts_v2',
        stability=0.5,
        similarity_boost=0.85,
    )
"

# 4. Replace each clip's audio (keeps video, swaps audio track)
for n in 1 2 ... N; do
  ffmpeg -y -i clip${n}.mp4 -i clip${n}_voice.mp3 \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
    out${n}.mp4
done
```

### Why voice_changer not pure TTS

| Method | Pros | Cons |
|---|---|---|
| `voice_changer()` (STS) | Lip-sync intact, prosody preserved, normalizes voice timbre + loudness | Doesn't fully normalize spectral character; constrained by source |
| `tts()` (text → fresh audio) | Maximum control, can use `eleven_v3` for expressive delivery | **Breaks lip-sync** — TTS generates fresh timing; would need Sync.so to re-sync |

**Default to voice_changer** unless you're rewriting the script wholesale.

### Settings that work

- `stability=0.5` — moderate; lets emotional variation through (heavier/lighter beats survive)
- `similarity_boost=0.85` — high; anchors tightly to the cloned voice character
- `model_id="eleven_multilingual_sts_v2"` — latest STS model, 29-language support, handles Spanish-inflected English natively

### Result (verified empirically)

Voice loudness span shrinks from ~40dB (Veo native) to ~5dB across all clips. Use `scripts/audio_match.py` to verify before/after.

---

## Audio QA (`scripts/audio_match.py`)

Audits voice loudness, noise floor, and spectral character across clips against a reference. Use after every Veo batch to detect outliers before stitching.

```bash
.venv/bin/python scripts/audio_match.py <reference.mp4> <clip2.mp4> <clip3.mp4> ...
```

**Output:** per-clip PASS/FAIL with deltas in dB and %. Default tolerances:
- voice loudness ±2 dB
- noise floor ±4 dB
- spectral centroid ±20%
- spectral rolloff ±20%

**Use cases:**
1. **Before stitching** — detect Veo outliers; decide whether to re-roll worst offenders or normalize via voice_changer
2. **After voice_changer** — verify normalization actually reduced the spread
3. **Tuning thresholds** — relax `--tol-voice-db 5` etc. if the strict defaults flag every clip; the goal is to spot true outliers, not theoretical drift

---

## Aspect-ratio deliverables

Each campaign typically needs both:
- **9:16 / 3:5** (Reels, TikTok, Stories) — the native Veo output aspect after watermark crop
- **4:5** (Instagram feed / Facebook feed) — tallest aspect feed supports

### `scripts/crop_4x5.py` — 4:5 conversion with letterbox detection

```bash
.venv/bin/python scripts/crop_4x5.py <portrait.mp4> --out <4x5.mp4>
```

**Veo bakes in ~100px black letterbox at top + ~20px at bottom** of its 720×1280 output. Naive `crop=720:900:0:0` keeps those bars. `crop_4x5.py` runs `ffmpeg cropdetect` first to find the actual non-black content region, then computes the largest 4:5 window inside it. Bias `top` (default) keeps face / drops floor.

Workflow chain:
```bash
# 1. Stitched 9:16 ad at 720x1200
# 2. Convert to 4:5 (auto-removes letterbox) → 720x900
.venv/bin/python scripts/crop_4x5.py outputs/.../final_lr01.mp4 \
  --out outputs/.../final_lr01_4x5.mp4
# 3. Caption the 4:5 — caption_styled.py auto-adjusts position by aspect
.venv/bin/python scripts/caption_styled.py outputs/.../final_lr01_4x5.mp4 \
  --out outputs/.../final_lr01_4x5_styled.mp4 --highlight-style yellow_text
```

---

## User skills (`~/.claude/skills/`)

These auto-surface on relevant user phrases. Don't need to invoke manually — Claude does it.

| Skill | Triggers | What it knows |
|---|---|---|
| `yellow-text-sub` | "caption this", "add subtitles", "Submagic style", "yellow highlight subs" | Full settings for `caption_styled.py` — font 0.0336, aspect-aware vertical_pos, yellow_text default, disclaimer integration. |
| `pulaski-jones-disclaimer` | "the disclaimer", "Pulaski/Jones disclaimer", "Chowchilla disclaimer", "CCWF disclaimer" | Verbatim legal text + on-screen styling for the women's-prison campaign. **DO NOT paraphrase** — regulated. |
| `feed-4x5` | "make it 4:5", "feed version", "Instagram feed crop", "Reels to feed" | `crop_4x5.py` invocation + the letterbox-detection rationale. |

---

## If a Generation Fails or Returns 0KB

1. Check for bare-skin descriptions → swap for covered clothing.
2. Switch from v2v to i2v if moderation keeps tripping.
3. Try a different model (Seedance → Kling, etc.).
4. For sensitive contexts: encode visually (institutional pants, weary look) instead of naming ("victim", "abuse", "prison").
5. **Veo "Internal Error" responses** are random; just re-roll the same prompt.
6. **Veo improvisation** (extra words, doubled proper nouns, trailing word, burned text, off-screen narrator) — see "Veo 3 gotchas" section. Most issues require **re-roll**, not post-fix.
7. **Burned subtitle hallucinations** — flagged automatically by `dissect.py`'s OCR step. Check `burned_text.json`. Re-roll any flagged clip.
8. **Poyo rate-limited (429)** — drop `max_workers` from 40 to 10. Submit limit is 20/10s account-wide.

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

- Combine `reference_image_urls` and `reference_video_urls` in one Seedance call.
- Commit `outputs/` or `.env` (both gitignored).
- Hardcode API keys — always from `.env`.
- Invent visual details. If the dissect frames don't show it, don't write it into the analysis.
- For legal services lead-gen (prison-abuse compensation campaigns): use the phrase **"significant potential compensation"** when referring to the recovery. Don't say "compensation" alone, "damages", "settlement", "money owed", or "payout" — unify on "significant potential compensation" across all variations of the same campaign.
- Mix output resolutions across clips of the same ad (Seedance 480p + Veo 720p won't concat clean).
- **Chain last-frame for >5 clips** — quality compounds-degrades. Use clip-1 anchor instead.
- **Skip the per-clip dissect QA gate** — Veo improvisation/audio-drift/watermark go undetected and compound through the rest of the ad.
- **Use `tts()` to "fix" voice quality on existing Veo clips** — it breaks lip-sync. Use `voice_changer()` instead.
- **Use `kie_client.generate_gpt_image` for GPT Image work** — always go through `openai_image.generate_image()` (OpenAI direct, `OPENAI_API_KEY`). KIE's GPT Image proxy adds cost markup and latency.
- **Use `kie_client.generate_veo` for Veo3 Fast** — route to Poyo (`poyo_client.generate_veo`) at $0.10/clip. KIE is $0.30/clip.
- **Run >2 `dissect.py` instances in parallel** — Whisper + I/O crashes the host. Cap at 2 with `xargs -P 2`.
- **Burn captions onto deliverables by default** — user does captioning in post. Only burn when explicitly asked ("caption this", "with the disclaimer", "Submagic style").
- **Submit >20 Poyo generations in parallel** — submit rate limit is 20/10s account-wide. Use `max_workers=10`.
- **Pass 1 image to Poyo `generation_type: "frame"`** — requires exactly 2. For clip-1 anchor pattern, pass the anchor URL twice (start=end).
- **Naive `crop=720:900:0:0` to make 4:5** — keeps Veo's baked-in letterbox bars. Use `scripts/crop_4x5.py` which runs `cropdetect` first.
- **Paraphrase the Pulaski/Jones disclaimer** — it's REGULATED legal copy. Every comma is intentional. Skill `pulaski-jones-disclaimer` has the verbatim text.
- **Frame Veo dialogue as a news-headline** (e.g., "Women from the X are finding out…") — triggers newscaster TTS that doesn't match intimate UGC tone. Rewrite conversationally.
- **Use quote-framing in dialogue** ("And it said…", "She's like…") — Veo sometimes renders the framing as a separate off-screen narrator voice. Drop the framing.
