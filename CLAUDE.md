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
    c. **Rotate anchor frames across clips 2-N** — extract 5-7 different clean frames from clip 1 and assign a different one to each subsequent clip. Optionally pull 1-2 more from clip 2 once it lands for extra variety. **Never reuse a single anchor URL for every clip** — that produces visually identical clip starts and reads as templated/unnatural on UGC playback. Pattern in `scripts/chowchilla_a2_variations.py`: `get_anchor_url()` checks `clip{N}_anchor_url.txt` per-clip first, falls back to `clip1_anchor_url.txt`. See `feedback_clip_anchor_rotation.md` memory.
    d. **MUST — pick only EYES-OPEN, forward-gaze frames as anchors. This is the canonical method for ALL multi-clip ads (user-locked rule, 2026-05-20).** Do NOT grab anchor frames at blind fixed timestamps — a blink, half-closed, or averted-gaze seed makes Veo drift the **eye color and identity** across clips (this happened on the w05 white-woman ad: anchors caught mid-blink/averted → clips 2/5/8 drifted from blue-grey to brown). Use OpenCV eye-detection to filter: `select_clean_anchor_times()` in `scripts/chowchilla_b01_ads.py` samples the clip ~5Hz, keeps only frames with a frontal face + ≥2 eyes detected (= eyes open), and spreads N picks across the timeline. Reference end-to-end pipeline: `scripts/chowchilla_b01_ads.py` (clip-1 anchor + eyes-open rotation, KIE veo3_fast).
    e. **Always add an explicit EYE-COLOR LOCK to every i2v prompt** so Veo doesn't drift the iris color per generation — e.g. `"warm dark-brown eyes that stay the SAME color throughout (never lighter/changing), open and looking into the lens"`. Set the color to match the persona anchor (w05 = pale blue-grey, b01 = dark brown).
11. **Audit voice consistency — run BOTH detectors** (see "Audio QA" section): `scripts/audio_match.py` for loudness/noise/spectral outliers, and `scripts/voice_consistency.py` for speaker-identity drift (embedding cosine + F0). `audio_match` alone misses the "wrong person" cases; `voice_consistency` alone misses the "right person but mic blew up" cases. If voice loudness span > ~10dB OR speaker similarity < 0.85 OR |ΔF0| > 15Hz on several clips, **normalize via ElevenLabs voice changer** (see "Audio normalization" section). This is the single fix for Veo's biggest weakness — its TTS varies wildly between generations.
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
| **Veo 3.1 Fast** | **Poyo** | `poyo_client.generate_veo` | **$0.10/clip** flat | Default Veo. See "Poyo gotchas". Fallback: `openrouter_video.generate_veo(model="google/veo-3.1-fast")`. |
| **Veo 3.1 Lite** | **OpenRouter** | `openrouter_video.generate_veo` | **$0.40/8s** (audio) | Cheaper/lighter Veo tier. `OPENROUTER_ADCLI_KEY`. Not on Poyo. |
| **Seedance 2.0 Fast** | **useapi.net** | `useapi_client.generate_seedance` | **unlimited** (flat monthly) | Default for high volume. Set `USEAPI_EXPLORE=true`. |
| **Seedance 2.0 Fast (480p)** | **OpenRouter** | `openrouter_video.generate_seedance` | **~$0.053/clip** (10s 480p) | Pay-per-use fallback. `OPENROUTER_ADCLI_KEY`. Token-based pricing. |
| **Kling 3.0** | **useapi.net** | `useapi_client.generate_kling` | **unlimited** (flat monthly) | Replaces KIE. Models: `kling-3-0-standard` (default) or `kling-3-0-pro`. |
| **Runway Gen-4 Turbo** | **useapi.net** | `useapi_client.generate_runway` | **unlimited** (flat monthly) | New. Model: `gen4-turbo` (default) or `gen4`. Up to 10s. |
| **nano-banana-2** | KIE | `kie_client.generate_nano_banana` | varies | Unchanged. |
| **gpt-image-2** (t2i / i2i) | **KIE** | `kie_client.generate_gpt_image` | per-image (2K) | **Default image provider** (changed 2026-05-20). `resolution="2K"`, `aspect_ratio="9:16"`. OpenAI direct DROPPED — lower quality + caps at 1024×1536. |
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
- **KIE/Poyo tempfile URLs (both inputs and outputs) expire after ~24h.** This includes anchor frame URLs uploaded via `kie_client.upload_file()` for `IMAGE_2_VIDEO` / `frame`-mode generation — `clip{N}_anchor_url.txt` files from prior sessions WILL go dead. **Always keep the local source file** (e.g., `outputs/<source>/frames/scene_00_at_0.00s.jpg`, `outputs/<variation>/clip1_anchor.jpg`) and re-upload via `upload_file()` to get a fresh URL before re-running an old variation or porting a prompt to another platform. Don't trust the URLs in version-controlled txt files as a long-term reference.
- `veo3.1-fast` is the model id (not `veo3_fast`). Quality model `veo3.1-quality` exists too — costlier.
- **Poyo outages → KIE Veo fallback.** Poyo's `veo3.1-fast` endpoint can degrade — 10min+ timeouts on payloads that succeeded earlier, "Server exception" on benign prompts. When this happens, `kie_client.generate_veo` (model `veo3_fast`, mode `"IMAGE_2_VIDEO"`) is the backup at $0.30/clip vs $0.10 — same underlying Veo 3 Fast model, different infrastructure. Use the **same anchor URL** (works for both providers); output is codec-compatible for concat. **Diagnosis:** if a known-good payload (one that succeeded earlier in the session) times out too, it's a Poyo-wide outage, not prompt-specific moderation — switch providers immediately.

**Resolution mismatch warning:** Seedance 480p (496×864) won't concat cleanly with Veo/Kling 720p (720×1280). Pick one model per ad, or rescale.

### useapi.net (Seedance / Kling / Runway — unlimited)

All models route through: `POST https://api.useapi.net/v1/runwayml/videos/create`
Client: `useapi_client.py`. Auth: `USEAPI_TOKEN` in `.env`.

| Function | Default model | Duration | Notes |
|---|---|---|---|
| `generate_seedance` | `seedance-2` | 4–15s | Up to 11 image refs. Use `start_frame_path` for i2v clip-1 anchor. |
| `generate_kling` | `kling-3.0-standard` | **5/10/15 only** | Also: `kling-3.0-pro`, `kling-o3-pro`, `kling-o3-4k`, `kling-2.6-pro`. |
| `generate_runway` | `gen4-turbo` | 2–10s | Also: `gen4`, `gen4.5`. Supports `seed` param. |

**All model IDs use dots:** `kling-3.0-pro` not `kling-3-0-pro`.

**Image references** — upload local files first via `upload_asset(path)` → returns `assetId`. All generate functions accept `start_frame_path` / `end_frame_path` / `image_paths` as local-file shortcuts that auto-upload. Or pass pre-uploaded `*_asset_id` strings directly.

**Asset upload endpoint:** `POST https://api.useapi.net/v1/runwayml/assets/?name={name}` — raw binary body, Content-Type = file mime type. Returns `assetId`.

**`exploreMode=True`** (default) — Unlimited plan, no credits consumed, lower priority. ~10 min for Seedance/Gen-4.5. Gen-4 Turbo ~1-2 min even in explore. **NOT supported by `veo-3.1`.** Set `USEAPI_EXPLORE=false` in `.env` for credit mode / higher priority.

**Status flow:** `PENDING → PROCESSING → SUCCEEDED / FAILED`. Response wrapped in `task: { taskId, status, progressRatio, estimatedTimeToStartSeconds, artifacts[] }`.

**Output resolution:** Seedance on useapi defaults to 720p (supports 480p/720p/1080p). **HARD RULE — always use 480p for Seedance.** The user has set this as a project default: 720p costs 2× per second and 1080p ~3× per second for marginal quality gain at social-feed playback size. Pass `resolution="480p"` explicitly even on useapi.net (where price doesn't bite since it's flat-rate, but the rule is consistent so output specs match across providers and Veo/Kling 720p clips can be downscaled to 480p for clean concat — NOT the other way around).

**Seedance is per-second pricing, not per-clip.** Poyo Seedance 2-Fast: 480p i2v $0.04/s, 480p t2v $0.07/s, 720p i2v $0.08/s, 720p t2v $0.14/s. So a 10s 480p t2v clip = $0.70, not $0.07. Veo 3.1 Fast IS flat-rate ($0.10/clip flat, always 8s). Don't confuse the two.

### Veo content-moderation triggers (Poyo + KIE)

Veo's NSFW/safety classifier runs ~10% into the job. Rejected prompts return opaque `"Server exception"` — the real reason is hidden. After 2 consecutive 10%-mark failures, treat it as deterministic moderation, not transient — re-rolling won't help, the prompt needs to change.

Visual-prompt language that triggers rejection, especially when combined with sensitive dialogue ("sexual abuse", "juvenile center", "lawsuit"):
- **Racial descriptors** — "Black man" gets flagged on sensitive-topic dialogue. Use a skin-tone descriptor instead: `"man, medium-dark skin tone"` passes where `"Black man, medium-dark skin tone"` doesn't.
- **Specific commercial settings** — `"Chicago corner store / bodega"`, `"liquor store exterior"` get flagged. Soften to `"residential street, brick wall slightly out of focus, faded awning edge"`.
- **"durag"** — slightly higher rejection rate; **`"wave cap tied at the back"`** reads visually identical in the output and passes reliably.
- **In-car / parked-vehicle settings + young Black male persona** — frequently blocked even with benign dialogue. (Persona E "block_serious" in the IL JDC campaign was entirely unusable until the car setting was swapped.) **`"older sedan"`** is worse than **`"car"`**.
- **Neck tattoo + sensitive dialogue** — compounds risk. Remove the neck-tattoo line from the visual prompt for clips that carry abuse/lawsuit language. Carry the neck tattoo on clip 1 only (where dialogue is the hook, not the claim).

### GPT Image — KIE (default, changed 2026-05-20)

| Function | Module | Auth | Notes |
|---|---|---|---|
| `generate_gpt_image` | `kie_client.py` | `KIE_API_KEY` | **Default.** Text-to-image (no `image_urls`) and image-to-image (with `image_urls`) via KIE's **`gpt-image-2`**. `aspect_ratio`: auto\|1:1\|9:16\|16:9\|4:3\|3:4. `resolution`: 1K\|2K\|4K (1:1 can't be 4K). Use `resolution="2K"`. |
| `generate_image` | `openai_image.py` | `OPENAI_API_KEY` | **No longer default** — OpenAI's gpt-image-2 produces lower-quality output and caps at 1024×1536. Only use if the user explicitly asks for the OpenAI path. |

**Rule change (2026-05-20):** the prior "OpenAI direct, never KIE" rule (which existed to avoid KIE's proxy cost markup) is **reversed**. The user prioritizes image quality + larger 2K/4K output over the markup. Route GPT Image through `kie_client.generate_gpt_image` at 2K. Memory: `feedback_image_gen_provider.md`.

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

## Captions — three scripts, three skills

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
| `--vertical-pos` | **auto by aspect** | `0.72` for 9:16, `0.82` for 4:5. Caption always lands just below the chin regardless of aspect — **but only for STANDARD centered talking-head layouts.** For PIP composites (persona overlay in a corner), the auto value lands on the persona's face. See PIP override rule below. |
| `--disclaimer-start / --disclaimer-end` | `7.0 / 12.0` | Hard-cut window for disclaimer overlay. |
| `--disclaimer-text` | Pulaski/Jones campaign | Skill `pulaski-jones-disclaimer` has the verbatim text. |
| `--no-disclaimer` | — | Skip the disclaimer pass entirely. |

**Whisper proper-noun substitutions** live in `caption_styled.py:SUBSTITUTIONS`. Add new mistranscriptions there. Already covers `MIHA→MIJA` and the `CHOWCHILLA` variants.

### `scripts/caption_hormozi3.py` — Submagic "Hormozi 3" style (reverse-engineered 2026-05-21)

The skill `hormozi3` documents this. Alex-Hormozi creator-caption look: Montserrat Black all-caps, white text with the active LINE in a rotating yellow/green/red accent (per card), small text pop, and **animated emojis that slide across the subtitle**. Reverse-engineered + tuned frame-by-frame against a real Submagic export and user-approved.

```bash
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4>
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4> --biased ""   # generic text
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4> --disclaimer  # + legal disclaimer
```

**`--disclaimer`** overlays the verbatim Pulaski/Jones legal text (skill `pulaski-jones-disclaimer`) at the bottom (white + black stroke, ~0.013 font, vertical 0.99), UNDER the captions, for 6s (`--disclaimer-secs`). It **auto-places at the calmest "most boring" window** via motion analysis (`find_boring_window()` — lowest frame-to-frame difference, avoiding the first/last 4s hook/CTA). Override with `--disclaimer-start <sec>`.

**GLOBAL parametric rule (no word-specific hacks — any new video looks like Submagic):**
- **Font: Montserrat Black (`assets/fonts/Montserrat-Black.ttf`), FIXED `font_ratio 0.0336`** — a ~2-word line fills ~42% of frame width; white-cap height is uniform ~2.2% of frame. **NOT fit-to-width/area growth** — that makes short cards too big. Font only shrinks if a line/card overflows.
- **Wrapping: ~2 words per line** (`words_per_line = 2`), max 3 lines; width fallback drops long single words to their own line. Tight stacking = the Submagic look ("I WAS / WRONG", "SIGNIFICANT / POTENTIAL / COMPENSATION").
- **Color:** white default; active LINE = card accent, rotating per card 🟡`#FCFB14`→🟢`#2AF82B`→🔴`#EE1916`. Stroke `0.06×fontsize`, subtle shadow, **no glow** (glow = newer Impact template).
- **Animation:** captions stay ON continuously (no per-word flash); text pop 96%→105%→100% over 0.12s; **emoji slide-across `0.42×width` (one side→center) over 0.40s**, presets rotate `slide_left/slide_right/slide_up/pop`; emoji uses **Noto animated GIFs** (internal wiggle/draw) — Submagic uses Apple's set, Noto is the closest *animated* one.
- **Render = single-pass:** pre-composite the WHOLE caption track (text + animated-emoji frames + motion) to a PNG sequence in PIL, then **ONE ffmpeg `overlay`**. ~20s for a 60s clip. **Do NOT chain one `overlay` filter per card** — that's O(cards) and takes minutes.

**Measurement lesson:** match RELATIVE proportions (% of frame width/height), not absolute px. Pixel masks are noisy — emoji color contaminates text measurements; measure a clean no-emoji card's widest-line WIDTH as % of frame.

### `scripts/caption.py` — legacy classic captions

Older style — white text + black outline, no per-word highlight. Kept for ad-hoc previews. Don't use for deliverables.

### Yellow-rect-positioning gotcha (lesson from this session)

When rendering the yellow highlight rect behind a word, **use `draw.textbbox()` to measure where the text will actually land**, NOT `cur_y + line_h`. The latter includes line-leading and makes the rect hang below the text. Already fixed in `caption_styled.py` — preserve when refactoring.

### PIP-composite caption override

When the persona is in a PIP corner overlay (e.g., scaled to height ~720 in bottom-right of a 720×1280 canvas — see "Composite V3" pattern), the auto `--vertical-pos 0.72` lands on the persona's mouth/nose because the persona's chin sits much lower than in a standard centered talking-head shot.

**For PIP composites, use `--vertical-pos 0.85` explicitly.** This lands the caption baseline at ~y=1088 on a 1280-tall canvas:
- **Below** the PIP persona's chin (which is around y≈900 in a 720-tall PIP placed at y=540)
- **Above** the Facebook mobile safe-cut area (FB's share/comment UI covers the bottom ~10% = ~y>1152 — caption baseline must stay ≤y≈1100)

Calibrated specifically: chin clears at ≥0.82, FB safe area starts at 0.90. **0.85 is the sweet spot.** Do not use 0.92+ on PIP composites — it pushes the caption into FB's UI cut area and gets clipped on mobile playback.

Same rule applies to 4:5 PIP composites — pass `--vertical-pos 0.85` explicitly, do not rely on the 0.82 default which assumes standard layout.

For standard (non-PIP) talking-head deliverables, the existing aspect-aware defaults (0.72 / 0.82) remain correct.

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

### dissect.py output-dir collisions

`dissect.py` writes to `outputs/<video_stem>/`. When you have multiple files named `clip1.mp4`, `clip2.mp4` across persona directories (e.g. `outputs/illinois_jdc_blue_collar/clip1.mp4` and `outputs/illinois_jdc_stoop_calm/clip1.mp4`), they all collide on `outputs/clip1/` and overwrite each other — the last dissect wins, prior transcripts are lost.

**Fix:** copy each clip to a unique stem before dissecting:

```bash
for slug in blue_collar stoop_calm; do
  for idx in 1 2 3; do
    cp outputs/illinois_jdc_${slug}/clip${idx}.mp4 outputs/illinois_jdc_${slug}_clip${idx}.mp4
  done
done
# Each dissect output now lands in outputs/illinois_jdc_<slug>_clip<idx>/
```

Then point `trim_silence.py` / `voice_consistency.py` at the unique-stem transcript path.

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
- **Veo (Poyo / KIE)** accepts ~3,000+ characters comfortably — our standard Chowchilla per-clip prompts run ~3,100 chars / ~520 words with all locks (CHARACTER, SETTING, CAMERA, register, EYES_LOCK, MOUTH_LOCK_NEUTRAL, NO_TEXT_LOCK, PRONUNCIATION_LOCK, DIALOGUE_LOCK, SPOKEN DIALOGUE).
- **Image-to-video prompts should be SHORT** — when an anchor is passed (FIRST_AND_LAST_FRAMES_2_VIDEO / frame / IMAGE_2_VIDEO modes), the scene/character/setting is already in the image. Don't re-describe them. Target **<100 words / <600 chars** per i2v prompt. REQUIRED fields (each <1 sentence): **GAZE** (where they're looking and how it changes), **BODY LANGUAGE** (head tilt, lean, blinks, micro-expressions), **VOICE STYLE** (pitch / age / register), **TONE** (emotional register — specific, not just "honest"), **SPEED** (target words-per-second). Plus boilerplate locks: AUDIO CRITICAL clause, PRONUNCIATION LOCK, DIALOGUE LOCK, NO-TEXT. DROP: character description, wardrobe, setting, framing, photo-realism boilerplate. Long prompts that re-describe in-image content sometimes confuse the model (it tries to reconcile prompt vs anchor and drifts). Long prompts are only needed for text-to-video (no anchor). Memory: `feedback_i2v_short_prompts.md`.
- **Runway (Gen-4 / Aleph) hard-caps prompts at 2,500 characters.** When porting a Veo prompt over, compress in this order without losing fidelity: (1) consolidate EYES + MOUTH locks into one sentence, (2) trim adjectival redundancy in CHARACTER ("late 40s to early 50s" → "late 40s", "Throughout the entire clip" → drop), (3) shorten SETTING photo descriptions ("framed family photographs — a graduation portrait at left…" → "framed family photos — graduation at left…"), (4) drop the "no beauty mode, no retouching, no filter, no skin smoothing" tail if still over. **Never cut**: CHARACTER core identity, register, NO_TEXT_LOCK, PRONUNCIATION_LOCK, DIALOGUE_LOCK, SPOKEN DIALOGUE. Target ~2,300 chars to leave headroom. V2 clip 1 reference: 3,171 → 2,287 chars with all critical locks intact.
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

## PIP composite — persona overlay over animated backdrop

When you want the BACKDROP to read as the primary subject (B-roll / news photos / facility shots) and the persona to read as a documentary cut-in / commentary, use the PIP layout instead of full-frame persona.

```bash
ffmpeg -y \
  -i <backdrop_24s.mp4> \
  -i <persona_greenscreen.mp4> \
  -i <ugc_audio_source.mp4> \
  -filter_complex "
    [1:v]chromakey=color=0x78FF9A:similarity=0.12:blend=0.04,scale=-1:720,setsar=1[fg];
    [0:v][fg]overlay=x=W-w-20:y=H-h-20:shortest=1,format=yuv420p[out]
  " \
  -map "[out]" -map 2:a -t 24.0 \
  -c:v libx264 -preset fast -crf 19 -c:a aac -b:a 192k out.mp4
```

- **Persona height**: 720 (vs 1050 for full-frame layout) — about 56% of canvas height
- **Position**: bottom-right (`x=W-w-20:y=H-h-20`); swap to `x=20` for bottom-left
- **RVM green is 0x78FF9A** (not pure green) — sampled from actual Replicate RVM output. Use `chromakey=color=0x78FF9A:similarity=0.12:blend=0.04` — milder values prevent eating grey clothing
- **Audio source**: use the ORIGINAL mp4 (RVM strips audio from greenscreen output)
- **Caption MUST use `--vertical-pos 0.85`** — see "PIP-composite caption override" earlier
- Reference: `outputs/illinois_jdc_urban_peer/composite_v5*.mp4`

### Backdrop aspect-preservation — letterbox-with-blur (don't crop sides)

gpt-image-2 outputs at 1024×1536 (2:3 portrait). Target 9:16 canvas (720×1280). 2:3 is "more square" than 9:16 — fitting requires either cropping sides (~16% width loss, kills wider composition) or letterboxing.

**Letterbox-with-blur preserves full source composition.** Background = scaled+blurred source filling 720×1280 (context-aware filler, matches source colors). Foreground = source scaled preserving aspect to 720×1080 (fits width). Overlay fg centered vertically over bg:

```bash
ffmpeg -loop 1 -t 4 -i <source_1024x1536.png> -filter_complex "
  [0:v]scale=2560:3840,boxblur=40:8,scale=720:1280,setsar=1[bg];
  [0:v]scale=720:1080,setsar=1[fg];
  [bg][fg]overlay=x=0:y=(H-h)/2,setsar=1[v]
" -map "[v]" ...
```

Top + bottom 100px each are blurred zoomed source — reads as depth-of-field, not flat black bars. Most of canvas (720×1080, ~84%) shows source at native proportions.

For docu-zoom on backdrops with this pattern, apply zoompan to the FOREGROUND layer only (scale source up first to 2160×3240 for headroom, then zoompan output to 720×1080). Reference: `scripts/jdc_a_docu_zoom.py`.

### Varied docu-zoom — don't templated-zoom every backdrop

Stitching multiple still-image backdrops with identical zoom (e.g., always slow push-in center 1.00→1.16) reads as templated/lazy. Vary per beat:

| Beat type | zoompan recipe |
|---|---|
| Establishing wide | Slow push-in center, z=1.00→1.16 |
| Subject emphasis | Push-in offset toward subject — `x='iw/3-(iw/zoom/3)'` for left bias, `x='(2*iw/3)-(iw/zoom/2)'` for right |
| Emotional intensity | Tight push-in, z=1.00→1.20+ |
| Reveal / scale | Slow tilt-down — z held at 1.10, `y='ih*0.15 + (ih*0.45 - ih*0.15) * on/<frames>'` |
| Open up / breath | Slow pull-back — `z='if(eq(on,0),1.18,max(zoom-0.0019,1.00))'` |
| Intimate / detail | Push-in offset toward a specific element |

Mix 4–6 different recipes across a 24s ad. Patterns in `scripts/jdc_a_docu_zoom.py` for IL JDC campaign.

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
9. **Em-dash list-completion trap** — Veo invents a noun to "complete" a grammatically-open list. Example from IL JDC: `"...Cook County, St. Charles, or Harrisburg — I need you to hear this"` produced gibberish `"Coast Center"` between "Harrisburg" and "I need" — Veo grammatically completed the list as if the user had said `"Cook County [center], St. Charles [center], or Harrisburg [Center]"`. The em-dash gave Veo permission to keep going.
   **Fix:** restructure so the noun list is grammatically closed before the next clause. Use a preposition + comma:
   - ✗ `"a kid in Cook County, St. Charles, or Harrisburg — I need you to hear this"`
   - ✓ `"a kid LOCKED UP IN Cook County, St. Charles, or Harrisburg, I need you to hear this"`
   The `"locked up in [list],"` structure makes the noun phrase grammatically complete. Veo no longer feels compelled to add a list-completing noun. Same rule applies to em-dashes, "or", "and" — any conjunction without a closing preposition invites improv.

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

**Important learnings:**
- Voice_changer normalizes TIMBRE successfully (centroid drift drops from ±15% to ±3%, speaker-embedding sim jumps from ~0.83 to ~0.90+).
- But voice_changer can MAKE LOUDNESS VARIANCE WORSE — the cloned voice's output cleanliness varies per clip, so output loudness diverges. Always run `loudnorm` AFTER voice_changer if you use it.
- **ElevenLabs has a 5-concurrent-request limit.** Use `max_workers=4` in ThreadPoolExecutor.
- Don't bother voice-changing if `audio_match.py` only flags a few clips on LOUDNESS — `loudnorm` alone is enough. Only invoke voice_changer when CENTROID or NOISE differs significantly (>10%/4dB), OR when `voice_consistency.py` flags speaker similarity <0.85.

### STS pitch-delta zones — when voice_changer works vs fails

Voice_changer is Speech-to-Speech: it preserves the source's **pitch contour** (so lip-sync stays intact) and only swaps **timbre**. **It cannot fix pitch drift.** A clip whose mean F0 is +50Hz higher than your reference clip will STILL be +50Hz higher after voice_changer — just now sounding like the cloned voice at an unnatural elevated pitch.

| Source F0 delta from ref clip | STS outcome |
|---|---|
| ≤10Hz | Clean — timbre unified, post-VC sim ≥0.90 |
| 10–25Hz | Usually clean, reads as natural intonation |
| 25–40Hz | Hit-or-miss — depends on input quality, post-VC sim 0.80–0.90 |
| **>40Hz** | **STS fails** — output sounds like different person, sim drops to 0.70s |

When source clip's F0 delta is in the failure zone (>40Hz from reference clip 1), **re-roll the source clip via Veo** before running STS — don't keep adjusting stability values. Empirical: bumping `stability` from 0.5 → 0.7 on a +45Hz-off clip only moved sim from 0.724 → 0.752 (still under threshold).

**Right order of operations:**
1. Generate all clips → audit with `voice_consistency.py`
2. If any clip's F0 delta from clip 1 >40Hz → **re-roll that clip** (Poyo first; KIE if Poyo's down) — don't proceed to STS yet
3. Once all clips have F0 deltas <40Hz → clone clip 1's voice → voice_changer each clip (stability=0.5, similarity_boost=0.85, model `eleven_multilingual_sts_v2`)
4. Re-loudnorm post-VC
5. Re-audit with `voice_consistency.py` to confirm sim ≥0.85 across all clips before stitching

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

## Audio QA — two detectors, run both

### Tier 1: `scripts/audio_match.py` (spectral statistics)

Audits voice loudness, noise floor, and spectral character across clips against a reference. Use after every Veo batch to detect outliers before stitching.

```bash
.venv/bin/python scripts/audio_match.py <reference.mp4> <clip2.mp4> <clip3.mp4> ...
```

**Output:** per-clip PASS/FAIL with deltas in dB and %. Default tolerances:
- voice loudness ±2 dB
- noise floor ±4 dB
- spectral centroid ±20%
- spectral rolloff ±20%

**Catches:** loudness mismatches, mic/noise-floor differences, gross timbre drift.
**Misses:** speaker-character changes that humans clearly hear. Centroid at ±20% is too loose for "is this the same person."

### Tier 2: `scripts/voice_consistency.py` (speaker-identity QA)

Use this whenever the user (or you on close listening) reports "the voice changes" between clips — `audio_match.py` will pass clips that clearly sound like different speakers.

```bash
.venv/bin/python scripts/voice_consistency.py <ref.mp4> <clip2.mp4> <clip3.mp4>
```

Two metrics that match human perception:
1. **Speaker embedding** (Resemblyzer / GE2E) — 256-dim unit vector per clip, cosine similarity to reference.
   - `≥0.85` reliably same speaker
   - `0.75–0.85` borderline, audible character shift
   - `<0.75` reads as different speaker
2. **F0 (pitch)** via librosa pyin — `mean ± std` per clip in Hz.
   - `Δmean ≤8Hz` below human perception threshold
   - `>15Hz` audibly different pitch
   - `>40Hz` essentially a different vocal register

Stack is free, local, no API calls. Resemblyzer is Apache 2.0; weights bundled (~17MB cached). `pip install resemblyzer` once.

**Run both.** Tier 1 catches volume/mic-floor issues. Tier 2 catches speaker-identity drift. Each misses what the other catches.

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

## Presenting videos in chat — backticked paths only

The user's chat client renders a video path as a **clickable inline preview ONLY when the path is wrapped in `` `backticks` ``** (markdown inline code). Any other format — plain text, table cell, markdown link syntax `[label](path)`, `file:///` URL, `http://localhost:<port>/` URL — does NOT trigger the preview.

```
✅ Source ad: `/Users/harry/Desktop/ad.mp4`
✅ Clip 1 v2: `outputs/illinois_jdc_news_eltracks/clip1.mp4`

❌ Source ad: /Users/harry/Desktop/ad.mp4               (no preview)
❌ [clip](outputs/foo/clip.mp4)                         (no preview)
❌ file:///Users/harry/.../clip.mp4                     (no preview)
```

Rule: every time you present a video file (generated clip, source upload, b-roll, composite, stitched final, aspect variant), wrap the path in backticks. Bulleted lists, tables, paragraphs — all fine, as long as the path itself is backticked. Same applies to absolute and relative paths.

Does NOT apply to images (use the Read tool to show those inline). Audio paths don't render previews regardless, so plain text is fine for `.mp3` / `.wav`.

---

## User skills (`~/.claude/skills/`)

These auto-surface on relevant user phrases. Don't need to invoke manually — Claude does it.

| Skill | Triggers | What it knows |
|---|---|---|
| `yellow-text-sub` | "caption this", "add subtitles", "Submagic style", "yellow highlight subs" | Full settings for `caption_styled.py` — font 0.0336, aspect-aware vertical_pos, yellow_text default, disclaimer integration. |
| `hormozi3` | "Hormozi captions", "Hormozi 3", "Submagic Hormozi", "yellow green red captions" | `caption_hormozi3.py` — Montserrat Black, rotating yellow/green/red per-line accent, text pop, animated emojis sliding across the subtitle. Font fixed 0.0336, 2-words/line, single-pass render. Global parametric rule. |
| `pulaski-jones-disclaimer` | "the disclaimer", "Pulaski/Jones disclaimer", "Chowchilla disclaimer", "CCWF disclaimer" | Verbatim legal text + on-screen styling for the women's-prison campaign. **DO NOT paraphrase** — regulated. |
| `feed-4x5` | "make it 4:5", "feed version", "Instagram feed crop", "Reels to feed" | `crop_4x5.py` invocation + the letterbox-detection rationale. |

---

## If a Generation Fails or Returns 0KB

1. Check for bare-skin descriptions → swap for covered clothing.
2. Switch from v2v to i2v if moderation keeps tripping.
3. Try a different model (Seedance → Kling, etc.).
4. For sensitive contexts: encode visually (institutional pants, weary look) instead of naming ("victim", "abuse", "prison").
5. **Veo "Internal Error" responses** are random; just re-roll the same prompt. **Exception:** if you get 2+ consecutive failures at the ~10% progress mark, treat it as deterministic content-moderation, not transient — see "Veo content-moderation triggers" in the Poyo section. Soften the prompt or anchor before more retries.
6. **Veo improvisation** (extra words, doubled proper nouns, trailing word, burned text, off-screen narrator, em-dash list-completion) — see "Veo 3 gotchas" section. Most issues require **re-roll**, not post-fix.
7. **Burned subtitle hallucinations** — flagged automatically by `dissect.py`'s OCR step. Check `burned_text.json`. Re-roll any flagged clip.
8. **Poyo rate-limited (429)** — drop `max_workers` from 40 to 10. Submit limit is 20/10s account-wide.
9. **Poyo wider outage** — known-good payloads (a prompt+anchor combo that succeeded earlier in the session) time out after 10min, or every submission returns "Server exception" regardless of prompt content. Switch to `kie_client.generate_veo` (model `veo3_fast`, mode `"IMAGE_2_VIDEO"`) — same Veo model, different infra, $0.30/clip. See Poyo gotchas section.
10. **Voice character drifts across clips post-stitch** — run `voice_consistency.py`. If a clip's F0 delta from ref is >40Hz, voice_changer won't fix it (STS preserves source pitch). Re-roll that clip via Veo first, then run STS. See "STS pitch-delta zones".

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

## News-realistic backdrop generation (legal/prison campaigns)

For lawsuit / juvenile-justice / institutional campaigns where backdrops should read as actual NEWS B-ROLL (not AI-stylized), use **nano-banana via KIE** ($0.05/image, ~30s render):

Style anchors that work:
- `"Photoreal news b-roll cinematography, shot like a 20/20 / Frontline / PBS Newshour documentary segment"`
- `"Natural color grading, real-world lighting (no dramatic Hollywood key-light), slight handheld feel, slight grain"`
- `"NOT cinematic, NOT stylized — looks like genuine news investigative footage shot on a news ENG camera or DSLR"`
- For scenes with people: specify "documentary middle/wide framing keeps identities partially obscured by angle or distance" — passes moderation, matches doc style

For scenes inside an institution (inmates + guards), nano-banana renders multi-figure scenes reliably — line walks, intake booking, cafeteria, yard, dayroom, procedural pat-down. See `scripts/jdc_a_inmate_backdrops.py` for the 6-prompt set we used on IL JDC.

Use **gpt-image-2 medium quality** at 1024×1536 portrait when you need fine text rendering (signs, headlines) or higher-quality character consistency. Slightly pricier (~$0.05) but more reliable for text.

### Real facility / location photos — sources that work

When the user wants ACTUAL photos of real facilities (vs AI-generated), these web sources have produced usable shots in past campaigns:

| Source pattern | What works |
|---|---|
| Construction-company project pages (e.g., `pathcc.com/projects/<facility>`) | Often have entrance monuments + building exteriors mid-renovation |
| Local news outlets (`propublica.org`, `injusticewatch.org`) | Photojournalist exteriors w/ razor-wire / signage |
| Advocacy non-profits (Chapin Hall, John Howard Association) | Building shots from inspection reports |
| Tor Hoerman Law / Helping Survivors / Levy Law | Placeholder SVGs only — skip |
| Wikipedia / Wikimedia Commons | Almost never have detention-facility photos |
| Local news affiliates (WTTW, CBS local) | Often 403-block direct WebFetch — try Google search → click through |
| Official state agency sites (idjj.illinois.gov) | Logos only, no facility photos |
| AsylumProjects.org | 403-blocks scrapers |
| The Final 5 Campaign timeline | Year-graphic images, NOT facility photos — easy to confuse since filenames reference facility opening years |

**Copyright caveat:** all of these are copyrighted (advocacy non-profits, news orgs, construction companies). User-explicit "fair use / ignore copyright" only — for cleared commercial campaigns, license images or use AI-generated alternatives.

### Video matting via Replicate RVM — specifics

Replicate `arielreplicate/robust_video_matting` is the proven path for matting persona out of existing UGC. Pricing ~$0.05–0.15 per clip.

Specifics from production use:
- **RVM green color is `0x78FF9A`** (light-leaf green), not pure `0x00FF00`. Sampled from actual Replicate output.
- **chromakey settings**: `similarity=0.12, blend=0.04` — milder than defaults. Grey clothing has similar luminance to green; aggressive chromakey eats hoodies.
- **RVM strips audio** — pass the ORIGINAL mp4 as a 3rd input to ffmpeg for the audio map (`-map 2:a`).
- **Watermark on free-tier output**: small green "DLY"/text on the persona's clothing. Not visible after composite if persona scale + position covers it.
- Reusable: ONE matte file (`<persona>_greenscreen.mp4`) works across UNLIMITED background swaps. Generate once, composite many.
- Reference: `replicate_client.py` + `outputs/illinois_jdc_urban_peer/ugc_greenscreen.mp4`.

### gpt-image-2 60s timeout fix

High-quality (`quality="high"`) 1024×1536 or 1536×1024 renders take 60–120s. OpenAI's default httpx timeout is 60s — renders fail with "Connection error." **Already fixed in `openai_image.py`**: client initialized with `timeout=600.0, max_retries=2`. Preserve this when refactoring.

---

## Do Not

- Combine `reference_image_urls` and `reference_video_urls` in one Seedance call.
- Commit `outputs/` or `.env` (both gitignored).
- Hardcode API keys — always from `.env`.
- Invent visual details. If the dissect frames don't show it, don't write it into the analysis.
- For legal services lead-gen (prison-abuse compensation campaigns): use the phrase **"significant potential compensation"** when referring to the recovery. Don't say "compensation" alone, "damages", "settlement", "money owed", or "payout" — unify on "significant potential compensation" across all variations of the same campaign.
- Mix output resolutions across clips of the same ad (Seedance 480p + Veo 720p won't concat clean).
- **Use 720p or 1080p for Seedance** — HARD RULE: always 480p. Seedance is per-second pricing ($0.07/s t2v at 480p vs $0.14/s at 720p), so 720p doubles cost for marginal-at-best gain on social-feed-sized playback. Pass `resolution="480p"` on every Seedance call regardless of provider (Poyo / useapi / OpenRouter).
- **Quote Seedance pricing as "per clip"** — it's per-SECOND. A 10s 480p t2v clip on Poyo costs $0.70 ($0.07/s × 10s), not $0.07. Only Veo 3.1 Fast on Poyo is true flat-rate ($0.10/clip flat, fixed 8s).
- **Use default `--vertical-pos` (0.72) for PIP composites** — the persona's chin sits lower in a PIP corner overlay than in a standard centered talking head, so the default caption lands on the face. Pass `--vertical-pos 0.85` for any PIP composite (lands below chin, above FB mobile safe-cut area). Do NOT push it to 0.92+ — that clips under Facebook's mobile UI.
- **Chain last-frame for >5 clips** — quality compounds-degrades. Use clip-1 anchor instead.
- **Extract anchor frames at fixed/blind timestamps** — MUST select only EYES-OPEN, forward-gaze frames (OpenCV filter `select_clean_anchor_times()` in `scripts/chowchilla_b01_ads.py`). A blink/averted seed drifts Veo's eye-color + identity across clips (w05 lesson). Also add an eye-color lock to every i2v prompt. This is the user-locked canonical clip-1-anchor method — `feedback_clip_anchor_rotation.md`.
- **Skip the per-clip dissect QA gate** — Veo improvisation/audio-drift/watermark go undetected and compound through the rest of the ad.
- **Use `tts()` to "fix" voice quality on existing Veo clips** — it breaks lip-sync. Use `voice_changer()` instead.
- **Use `openai_image.generate_image()` for GPT Image work** — as of 2026-05-20 GPT Image routes through `kie_client.generate_gpt_image` at 2K (OpenAI dropped — lower quality, caps at 1024×1536). Only use the OpenAI path if the user explicitly asks for it.
- **Use `kie_client.generate_veo` for Veo3 Fast** — route to Poyo (`poyo_client.generate_veo`) at $0.10/clip. KIE is $0.30/clip.
- **Run >2 `dissect.py` instances in parallel** — Whisper + I/O crashes the host. Cap at 2 with `xargs -P 2`.
- **Burn captions onto deliverables by default** — user does captioning in post. Only burn when explicitly asked ("caption this", "with the disclaimer", "Submagic style").
- **Submit >20 Poyo generations in parallel** — submit rate limit is 20/10s account-wide. Use `max_workers=10`.
- **Pass 1 image to Poyo `generation_type: "frame"`** — requires exactly 2. For clip-1 anchor pattern, pass the anchor URL twice (start=end).
- **Naive `crop=720:900:0:0` to make 4:5** — keeps Veo's baked-in letterbox bars. Use `scripts/crop_4x5.py` which runs `cropdetect` first.
- **Paraphrase the Pulaski/Jones disclaimer** — it's REGULATED legal copy. Every comma is intentional. Skill `pulaski-jones-disclaimer` has the verbatim text.
- **Frame Veo dialogue as a news-headline** (e.g., "Women from the X are finding out…") — triggers newscaster TTS that doesn't match intimate UGC tone. Rewrite conversationally.
- **Use quote-framing in dialogue** ("And it said…", "She's like…") — Veo sometimes renders the framing as a separate off-screen narrator voice. Drop the framing.
- **End a noun list with an em-dash before the next clause** (e.g., "…Cook County, St. Charles, or Harrisburg — I need…") — Veo invents a noun to complete the list ("Coast Center"). Use a preposition + closing comma: `"locked up in [list], I need…"`.
- **Include "Black man" in Veo prompts paired with sensitive-topic dialogue** (sexual abuse, juvenile center, lawsuit) — deterministic moderation block. Use a skin-tone descriptor only: `"man, medium-dark skin tone"`. Same applies to specific commercial settings ("Chicago corner store"), in-car settings + young Black male persona, and neck-tattoo descriptors. See "Veo content-moderation triggers".
- **Retry voice_changer with higher stability to fix big pitch drift** — STS preserves source pitch by design. If F0 delta from ref clip is >40Hz, re-roll the source via Veo instead. Bumping `stability=0.5 → 0.7` only moves sim ~0.03 (0.724 → 0.752 — still under 0.85 threshold).
- **Skip `voice_consistency.py` when user reports voice changes** — `audio_match.py`'s ±20% centroid tolerance is too loose to catch what humans hear. Always run both detectors.
- **Dissect multiple `clip1.mp4` files in one run** — they all overwrite `outputs/clip1/`. Copy to unique stems first: `outputs/illinois_jdc_<slug>_clip${idx}.mp4`.
- **Keep submitting Poyo after 10min timeouts on known-good payloads** — that's a Poyo-wide outage. Switch to `kie_client.generate_veo` at $0.30/clip instead of burning budget on retries.
- **Present video file paths as plain text** — the user's chat client only renders a clickable inline preview when the path is wrapped in `` `backticks` ``. Plain text paths, paths inside markdown table cells, paths in markdown link syntax `[label](path)`, `file:///` URLs, and `http://localhost:<port>/` URLs all FAIL to trigger the preview. Every video file (generated clip, source upload, b-roll, composite, stitched final, aspect variant) must be backticked. See the "Presenting videos in chat" section above.
- **Use Veo 3.1 Quality (`veo3`) on KIE** — HARD RULE: NEVER. Always start with Veo 3.1 Lite (`veo3_lite`). Only fall back to Veo 3.1 Fast (`veo3_fast`) after 2-3 Lite failures on the same prompt for the same failure mode. If Fast also fails, stop and escalate to the user — do NOT use Quality. Memory: `feedback_veo_tier_routing.md`.
