# CLAUDE.md — aicreative

End-to-end UGC ad cloning. Four halves:

1. **Dissect** competitor videos beat-by-beat (`dissect.py`)
2. **Generate** clips/images via KIE (`kie_client.py`)
3. **Voice** TTS + cloning via ElevenLabs direct (`elevenlabs_client.py`)
4. **Caption** burn-in TikTok-style captions (`caption.py`)

**API-first — no local LLM/CPU heavy lifting.** Speech-to-text runs on **ElevenLabs Scribe**
(`elevenlabs_client.scribe` / `scribe_whisper_compat`), NOT local Whisper. Whisper has been
removed entirely (changed 2026-05-20). Transcription, generation, voice, and image work all
go through provider APIs; the local machine only runs ffmpeg + tesseract. This keeps the
pipeline portable (runs on a small cloud box with no GPU) and consistent. `ELEVENLABS_API_KEY`
is therefore required for any step that needs a transcript (dissect QA gate, captions, trims).

---

## The Workflow

1. User drops a competitor video in chat (path or URL — yt-dlp first if URL).
2. Run `dissect.py <video>` → produces `outputs/<videoname>/` with frames, transcript, scenes.
3. Read frames + transcript → write `analysis.md` with **Setting / Character / Camera / Beats / Tone / Style**.
4. User picks the model (Seedance/Kling/Veo) and provides their product/character assets.
5. Generate **4–6 reference characters in parallel** with GPT Image 2 → user picks one anchor. **Whenever generating any image or video, show the exact model/provider and the full prompt in chat so the prompt is reusable in later sessions.**
6. Adapt the analysis into a model-specific prompt. **Show the full prompt in chat. Wait for explicit go.**
7. **Test proper-noun pronunciation at the shortest viable duration** before committing to longer clips.
8. Generate clips. Clip count depends on model max-duration: **Veo 3 Fast = 8s/clip** (~8 clips per minute of ad), **Seedance = up to 15s/clip** (~3-4 clips per minute), **Kling = up to ~10s/clip**. Pick clip boundaries on natural speech breaks.
9. **Dissect every generated clip immediately** with `dissect.py --interval 1.0`. Review opening, midpoint, and end frames + ElevenLabs Scribe transcript. Verify: identity match, visual age, emotional tone lock, camera lock (no drift), motion fidelity, lip-sync, proper-noun pronunciation, audio quality. **Do not proceed to the next clip or to stitching until the current clip passes this QA gate.**
10. **Trim silence; chain via clip-1 anchor.** Per-clip post-QA flow:
    a. `scripts/trim_silence.py <clip.mp4> <transcript.json>` (start/end-only by default — preserves internal pacing). Outputs `<clip>_trimmed.mp4`.
    b. **For clips 2-N: use a clean frame from CLIP 1 as the `IMAGE_2_VIDEO` first-frame**, NOT the last frame of the previous clip. Last-frame chaining compounds quality degradation across N generations; clip-1 anchor keeps quality consistent throughout the ad. Small visible "reset" between clips is acceptable for short-form UGC pacing. (Last-frame chain is an alternate technique — see "Stitching multi-clip ads" — for a "fake one-take" feel where you accept the drift.)
    c. **Rotate anchor frames across clips 2-N** — extract 5-7 different clean frames from clip 1 and assign a different one to each subsequent clip. Optionally pull 1-2 more from clip 2 once it lands for extra variety. **Never reuse a single anchor URL for every clip** — that produces visually identical clip starts and reads as templated/unnatural on UGC playback. Pattern in `scripts/chowchilla_a2_variations.py`: `get_anchor_url()` checks `clip{N}_anchor_url.txt` per-clip first, falls back to `clip1_anchor_url.txt`. See `feedback_clip_anchor_rotation.md` memory.
    d. **MUST — pick only EYES-OPEN, forward-gaze frames as anchors. This is the canonical method for ALL multi-clip ads (user-locked rule, 2026-05-20).** Do NOT grab anchor frames at blind fixed timestamps — a blink, half-closed, or averted-gaze seed makes Veo drift the **eye color and identity** across clips (this happened on the w05 white-woman ad: anchors caught mid-blink/averted → clips 2/5/8 drifted from blue-grey to brown). Use OpenCV eye-detection to filter: `select_clean_anchor_times()` in `scripts/chowchilla_b01_ads.py` samples the clip ~5Hz, keeps only frames with a frontal face + ≥2 eyes detected (= eyes open), and spreads N picks across the timeline. Reference end-to-end pipeline: `scripts/chowchilla_b01_ads.py` (clip-1 anchor + eyes-open rotation, KIE veo3_fast).
       **Reusable standalone picker (use this for any new persona): `scripts/pick_clean_anchors.py <clip1.mp4> --out-dir <dir> --n 6 --prefix _anchor`** — Haar frontal-face + eye cascade, samples every 0.15s, keeps only eyes-open frames, writes N well-spaced `_anchor_*.jpg`. Built + verified on w05 (2026-05): the blind-timestamp anchors had caught a mid-blink frame that seeded clips 2/8 to brown eyes; re-picking eyes-open frames + the eye-color lock fixed it.
    e. **Always add an explicit EYE-COLOR LOCK to every i2v prompt** so Veo doesn't drift the iris color per generation — e.g. `"warm dark-brown eyes that stay the SAME color throughout (never lighter/changing), open and looking into the lens"`. Set the color to match the persona anchor (w05 = pale blue-grey, b01 = dark brown).
11. **Audit voice consistency — run BOTH detectors** (see "Audio QA" section): `scripts/audio_match.py` for loudness/noise/spectral outliers, and `scripts/voice_consistency.py` for speaker-identity drift (embedding cosine + F0). `audio_match` alone misses the "wrong person" cases; `voice_consistency` alone misses the "right person but mic blew up" cases. If voice loudness span > ~10dB OR speaker similarity < 0.85 OR |ΔF0| > 15Hz on several clips, **normalize via ElevenLabs voice changer** (see "Audio normalization" section). This is the single fix for Veo's biggest weakness — its TTS varies wildly between generations.
12. Stitch with ffmpeg `concat` demuxer (lossless if codec params match).
13. Add b-rolls via `filter_complex` (replace video segments, audio passthrough).
14. Caption with `caption.py` (ElevenLabs Scribe → PIL → ffmpeg overlay).
15. Optional variants: same script, different character anchor.

**Iteration cadence:** generate freely — no explicit "go" needed per clip. After each clip, dissect per step 9. If it passes QA, advance to the next clip. If it fails, you have up to **3 re-generation attempts on the same clip** to fix the issue (adjust the prompt, the seed, the reference image, or the model). After 3 failed attempts, stop and escalate to the user for guidance instead of burning budget.

---

## Available Models

### Provider routing (per-model)

User-set rule: **route each model to its cheapest reliable host**, not all through KIE.

| Model | Provider | Module | Cost | Notes |
|---|---|---|---|---|
| **Veo 3.1 Fast** | **Poyo** | `poyo_client.generate_veo` | **$0.10/clip** flat | Default Veo. See "Poyo gotchas". Fallback: `openrouter_video.generate_veo(model="google/veo-3.1-fast")`. |
| **Veo 3.1 Lite (FREE)** | **useapi google-flow** | `googleflow_client.generate_veo` | **$0 — free, no credit** | **DEFAULT for Veo Lite.** Model `veo-3.1-lite-low-priority`, ultra-low-priority queue (SLOW but free). `startImage` i2v persona lock. `USEAPI_TOKEN`, EMAIL `flowmomomedia@gmail.com`. See `feedback_veo_lite_free_path` memory + `scripts/podcast_omni_produce.py`. |
| **Veo 3.1 Lite** | **OpenRouter** | `openrouter_video.generate_veo` | **$0.40/8s** (audio) | Paid fallback when the free queue is too slow. `OPENROUTER_ADCLI_KEY`. Not on Poyo. (KIE `veo3_lite` also paid — spends points, hourly cap.) |
| **Seedance 2.0 Fast** | **useapi.net** | `useapi_client.generate_seedance` | **unlimited** (flat monthly) | Default for high volume. Set `USEAPI_EXPLORE=true`. |
| **Seedance 2.0 Fast (480p)** | **OpenRouter** | `openrouter_video.generate_seedance` | **~$0.05/sec** (480p, token-based) | Pay-per-use fallback when useapi is down or the unlimited queue is too slow. `OPENROUTER_ADCLI_KEY`. Seedance is per-second, not per-clip. Do not confuse this with Runway; OpenRouter video API has Seedance/Kling/Veo/Sora/Wan, not Runway Gen-4. |
| **Kling 3.0** | **useapi.net** | `useapi_client.generate_kling` | **unlimited** (flat monthly) | Replaces KIE. Models: `kling-3.0-standard` (default) or `kling-3.0-pro`. |
| **Runway Gen-4 Turbo** | **useapi.net** | `useapi_client.generate_runway` | **unlimited** (flat monthly) | New. Model: `gen4-turbo` (default) or `gen4`. Up to 10s. |
| **prunaai/p-video** | **Replicate** | `replicate.Client(...).predictions.create(model=("prunaai","p-video"))` | token-based | Image-to-video fallback for policy-heavy talking-head/reporter clips. Use native audio, 10s chunks, short prompts, and post links before QA. |
| **nano-banana-2** | KIE | `kie_client.generate_nano_banana` | varies | Unchanged. |
| **gpt-image-2** (t2i / i2i) | **KIE** | `kie_client.generate_gpt_image` | per-image (2K) | **Default image provider** (changed 2026-05-20). `resolution="2K"`, `aspect_ratio="9:16"`. OpenAI direct DROPPED — lower quality + caps at 1024×1536. |
| **ElevenLabs** (TTS / clone / voice_changer) | ElevenLabs direct | `elevenlabs_client` | per-character | 5 concurrent max — throttle when batching. |

Memory: `project_video_provider_routing.md` — confirm before bulk-running new models since pricing tiers shift.

### KIE (for Kling / nano-banana)

| Function | Model | Endpoint | Defaults |
|---|---|---|---|
| `generate_kling` | `kling-3.0/video` | `/jobs/createTask` | mode `std` (720p), 9:16 |
| `generate_nano_banana` | `nano-banana-2` | `/jobs/createTask` | — |
| `generate_seedance` | `bytedance/seedance-2-fast` | `/jobs/createTask` | 480p (496×864), 9:16, audio on, **min 4s, max 15s**. **NOT preferred — route high-volume jobs to useapi.net, or OpenRouter for cheap 480p pay-per-use fallback.** |
| `generate_veo` | `veo3_fast` | `/veo/generate` | 720p (720×1280), 9:16. **NOT preferred — route to Poyo for $0.10/clip vs $0.30.** |

All return `{"status": "success"|"failed", "urls": [...], "raw": {...}}`. KIE Veo polls a different endpoint (`/veo/record-info`) — handled internally.

**KIE jobs run server-side once submitted — killing the local process does NOT cancel them (image AND video).** As soon as `createTask` / `/veo/generate` returns a task id, KIE produces (and bills) the job on its own infrastructure, independent of your local script. Ctrl-C / `pkill` / killing a background task only stops local **polling + download** — the output is still generated server-side and the points are still spent. So there is no point killing a batch mid-flight to "save points" or "stop generation"; it does neither. Just let it finish, or stop polling and rely on **skip-if-exists** to pick the finished files up on a re-run (re-running re-polls the same in-flight task and downloads it). Applies to every KIE model: `generate_gpt_image`, `generate_nano_banana`, `generate_veo`, `generate_kling`, `generate_seedance`. (Poyo is the same — submit returns a `task_id` that completes regardless of the local poller.)

**KIE upload endpoint stays useful** for hosting reference images:
```
POST https://kieai.redpandaai.co/api/file-stream-upload  → returns {data.downloadUrl}
```
Use this even when Veo runs via Poyo — image hosting is a separate concern from generation.

### KIE Veo 3.1 model ids + anchor mode (verified 2026-05)

KIE's confusingly-named Veo models (docs: `docs.kie.ai/veo3-api/generate-veo-3-video`):
- `veo3_lite` = **Veo 3.1 Lite** (cheapest; use first per `feedback_veo_tier_routing`)
- `veo3_fast` = **Veo 3.1 Fast** (NOT "Veo 3" — better identity hold than Lite)
- `veo3` = **Veo 3.1 Quality** (NEVER use — hard rule)

`generationType` for Veo 3.1 (the old `IMAGE_2_VIDEO` is gone): `TEXT_2_VIDEO` | `FIRST_AND_LAST_FRAMES_2_VIDEO` | `REFERENCE_2_VIDEO`. **For the clip-1 anchor pattern, use `FIRST_AND_LAST_FRAMES_2_VIDEO` and pass the anchor twice** (`image_urls=[anchor, anchor]`, start=end) — locks framing the same way Poyo's `frame` mode does. `kie_client.generate_veo(..., model="veo3_lite")` takes a `model` kwarg.

**Lite drifts identity mid-clip on multi-character scenes** (the reporter+interviewee two-shot drifted both faces between 0.5s and 5.5s on Lite; Veo 3.1 Fast held them). For 2-person framing, expect to escalate Lite→Fast.

### Kling 3.0 on KIE — element references + gotchas (verified 2026-05)

`kie_client.generate_kling` → model `kling-3.0/video`, polls `/jobs/recordInfo`. Native audio via `sound=True`. `mode="std"` (720p, cheaper) | `"pro"` (better). Output is **higher-res than Veo** (~1176×1764 at 9:16 → scale to 720×1280 before concat with Veo clips). Docs: `docs.kie.ai/market/kling/kling-3-0`.

**Element-reference system** (the "Omni" multi-subject path — best for locking 2+ distinct characters in one scene): define `kling_elements`, reference each by `@element_name` token in the prompt.
```python
kling_elements=[
  {"name": "element_reporter", "description": "...", "element_input_urls": [url1, url2]},
  {"name": "element_interviewee", "description": "...", "element_input_urls": [url1, url2]},
]
# prompt: "@element_reporter asks the question while @element_interviewee listens..."
```
Plus an optional `image_urls=[scene_baseline]` for the establishing composite/first-frame.

Hard gotchas (all hit this session):
- **Each element requires 2-4 images** (`element_input_urls`) — 1 image 422s with "must contain between 2 and 4 images". Generate a 2nd angle of the persona via gpt-image-2 i2i if you only have one.
- **Max 3 elements per task.**
- **Prompt hard-caps at 2500 chars** (same as Runway). Compress: consolidate locks, trim adjectives, drop photo-realism boilerplate. 422s with "length of 'prompt' must not exceed 2500 characters" if over.
- **`multi_shots` is REQUIRED in the payload** (boolean) — omitting it 422s "multi_shots cannot be empty". Set `multi_shots=False` for a single shot, or `True` + a `multi_prompt=[{"prompt","duration"},...]` array for multi-shot.
- **Kling auto-cuts shots mid-clip EVEN WITH `multi_shots=False`.** On a 10s reporter-question clip it held the two-shot 0-7s then hard-cut to a reporter-only close-up at 7.04s. Its auto-cinematography decides to insert reaction-shot cuts. To enforce one continuous take: keep the clip short (≤7s) and/or trim at the detected cut (`dissect.py` scene-detection reports the cut timestamp). Strong "NO CUTS, single continuous take" prompt language helps but does not guarantee.

### Poyo gotchas (Veo 3.1 Fast at $0.10/clip)

- **`generation_type: "frame"` requires EXACTLY 2 `image_urls`.** For clip-1 anchor pattern, pass the anchor twice (start = end). API rejects 1-image with 400. Client at `poyo_client.py`.
- **Submit rate limit: 20 requests per 10 seconds (account-wide).** Batches >20 in parallel will 429. Use `max_workers=10` in ThreadPoolExecutor — generation takes 90-180s so sustained submit rate stays under limit.
- **Status polling rate limit: 1 request per 2 seconds PER TASK.** The built-in `_poll(interval=5)` is safe. Don't manually curl the status endpoint while a script is polling — you'll trip the limit and confuse the script.
- Async model: POST `/api/generate/submit` returns `task_id`, then poll `/api/generate/status/{task_id}` until `status: finished`. Files in `data.files[].file_url`, valid 24h.
- **KIE/Poyo tempfile URLs (both inputs and outputs) expire after ~24h.** This includes anchor frame URLs uploaded via `kie_client.upload_file()` for `IMAGE_2_VIDEO` / `frame`-mode generation — `clip{N}_anchor_url.txt` files from prior sessions WILL go dead. **Always keep the local source file** (e.g., `outputs/<source>/frames/scene_00_at_0.00s.jpg`, `outputs/<variation>/clip1_anchor.jpg`) and re-upload via `upload_file()` to get a fresh URL before re-running an old variation or porting a prompt to another platform. Don't trust the URLs in version-controlled txt files as a long-term reference.
- `veo3.1-fast` is the model id (not `veo3_fast`). Quality model `veo3.1-quality` exists too — costlier.
- **Poyo outages → KIE Veo fallback.** Poyo's `veo3.1-fast` endpoint can degrade — 10min+ timeouts on payloads that succeeded earlier, "Server exception" on benign prompts. When this happens, `kie_client.generate_veo` (model `veo3_fast`, mode `"IMAGE_2_VIDEO"`) is the backup at $0.30/clip vs $0.10 — same underlying Veo 3 Fast model, different infrastructure. Use the **same anchor URL** (works for both providers); output is codec-compatible for concat. **Diagnosis:** if a known-good payload (one that succeeded earlier in the session) times out too, it's a Poyo-wide outage, not prompt-specific moderation — switch providers immediately.
- **Poyo flaky-error signatures (all transient — re-roll or fall back to KIE):** besides "Server exception" and 600s timeouts, Poyo also returns **`"Please enter a prompt and try again"`** on perfectly valid non-empty payloads (the SAME prompt succeeds on retry). Don't treat it as a real "empty prompt" error. If it recurs across a batch alongside timeouts, it's the outage signal → switch to KIE `veo3_fast`. **KIE `veo3_fast` has its own transient `"Internal Error, Please try again later"`** — also just a re-roll (hit ~3/30 clips this session). Build skip-if-exists into batch scripts so re-running only regenerates the failures.

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

**Account setup gotcha (hit 2026-06-12):** A valid `USEAPI_TOKEN` is not enough for RunwayML-backed models. First register at least one Runway account:
```
POST https://api.useapi.net/v1/runwayml/accounts/{email}
Authorization: Bearer $USEAPI_TOKEN
Content-Type: application/json

{"email":"same@email.com","password":"...","maxJobs":3}
```
Do not URL-encode the `@` in the path for this API; include the same `email` in the JSON body. Omitting the account gives `Please configure at least one account`; omitting `maxJobs` gives `Required param maxJobs is missing or empty`.

**Verified smoke test (2026-06-12):** `useapi_client.generate_seedance(..., duration=5, aspect_ratio="9:16")` submitted, polled, and downloaded successfully to `outputs/test_seedance.mp4` in ~2 minutes with explore mode enabled.

**Explore-mode queue is intentionally slow and shallow.** For bulk Seedance jobs, assume tasks can sit `THROTTLED` for hours, not minutes. Do not use 15-minute poll ceilings. Use multi-hour polling (3h+) and 429 submit backoff; a 429 usually means the useapi account queue is full, not that the prompt failed. For long runs, persist task IDs as soon as they submit so completed outputs can be recovered if local polling dies.

**Seedance juvenile/JDC moderation pattern (verified 2026-05 JDC b-roll batch).** `seedance-2` on useapi rejects prompts that combine juvenile/youth detention with body-search, shower/towel, bunk/bedroom proximity, or adult-guard-over-minor framing, returning `SAFETY.INPUT.TEXT` / `CHILDREN`. Do not keep rerolling these; rewrite more indirectly, remove child-age descriptors, move the implication into props/CCTV/logbooks/corridors/documents, or route to another model. Shots that passed: doorway silhouettes, corridor escort, peephole observation, closed office door, empty cell clothing, laundry evidence, CCTV wall shadows, yard corner whisper, stairwell escort, logbook, personnel file, untouched tray, solitary aftermath, exterior night, empty corridor, redacted court docs.

### OpenRouter video (Seedance/Kling/Veo/Sora/Wan — pay-per-use)

Client: `openrouter_video.py`. Auth: prefer `OPENROUTER_ADCLI_KEY`, fallback `OPENROUTER_API_KEY`. Endpoint: `POST https://openrouter.ai/api/v1/videos`; model discovery: `GET /videos/models`.

**Do not repeat:** OpenRouter does **not** provide Runway Gen-4 models here. It does provide `bytedance/seedance-2.0-fast`, `kwaivgi/kling-v3.0-std`, `google/veo-3.1-lite`, `google/veo-3.1-fast`, `openai/sora-2-pro`, and Wan models. Keep Runway Gen-4 on useapi.net's RunwayML wrapper.

**Seedance 2.0 Fast 480p:** use `openrouter_video.generate_seedance(resolution="480p", model="bytedance/seedance-2.0-fast")` as cheap pay-per-use fallback. User correction: the memorable figure is about **$0.053 per 10s 480p clip**, token-based, not "Runway at $0.05" and not per-second pricing.

**Veo:** OpenRouter Veo 3.1 Lite is paid fallback (`google/veo-3.1-lite`, ~$0.40/8s audio at 720p). Poyo remains default for Veo Fast at $0.10/clip flat.

**Status flow:** `PENDING → PROCESSING → SUCCEEDED / FAILED`. Response wrapped in `task: { taskId, status, progressRatio, estimatedTimeToStartSeconds, artifacts[] }`.

**Output resolution:** Seedance on useapi defaults to 720p (supports 480p/720p/1080p). **HARD RULE — always use 480p for Seedance.** The user has set this as a project default: 720p costs 2× per second and 1080p ~3× per second for marginal quality gain at social-feed playback size. Pass `resolution="480p"` explicitly even on useapi.net (where price doesn't bite since it's flat-rate, but the rule is consistent so output specs match across providers and Veo/Kling 720p clips can be downscaled to 480p for clean concat — NOT the other way around).

**Seedance pricing differs by provider.** useapi is flat monthly/unlimited, OpenRouter Seedance 2.0 Fast 480p is token-based and remembered here as about **$0.053 per 10s clip**, while KIE-style Seedance endpoints may be per-second. Do not carry a per-second warning from one provider into OpenRouter decisions.

### Veo content-moderation triggers (Poyo + KIE)

Veo's NSFW/safety classifier runs ~10% into the job. Rejected prompts return opaque `"Server exception"` — the real reason is hidden. After 2 consecutive 10%-mark failures, treat it as deterministic moderation, not transient — re-rolling won't help, the prompt needs to change.

Visual-prompt language that triggers rejection, especially when combined with sensitive dialogue ("sexual abuse", "juvenile center", "lawsuit"):
- **Racial descriptors** — "Black man" gets flagged on sensitive-topic dialogue. Use a skin-tone descriptor instead: `"man, medium-dark skin tone"` passes where `"Black man, medium-dark skin tone"` doesn't.
- **Specific commercial settings** — `"Chicago corner store / bodega"`, `"liquor store exterior"` get flagged. Soften to `"residential street, brick wall slightly out of focus, faded awning edge"`.
- **"durag"** — slightly higher rejection rate; **`"wave cap tied at the back"`** reads visually identical in the output and passes reliably.
- **In-car / parked-vehicle settings + young Black male persona** — frequently blocked even with benign dialogue. (Persona E "block_serious" in the IL JDC campaign was entirely unusable until the car setting was swapped.) **`"older sedan"`** is worse than **`"car"`**.
- **Neck tattoo + sensitive dialogue** — compounds risk. Remove the neck-tattoo line from the visual prompt for clips that carry abuse/lawsuit language. Carry the neck tattoo on clip 1 only (where dialogue is the hook, not the claim).

**THE big one — child + sexual-abuse in the SAME generation = hard child-safety block (2026-05-25).** A clip whose dialogue pairs a minor reference ("kid", "juvenile", "juvie", "I was twelve") with "sexual abuse"/"sexually abused" gets deterministically blocked (child-safety classifier, not generic NSFW). **Fix: split the two across separate clips** — clip A carries the age/"kid" beat, clip B carries the "a staff member sexually abused you" beat; never both in one clip. Verified across the IL JDC podcast set. Note: "sexual abuse" + "locked up" + facility names in one clip passes FINE as long as no kid/juvenile word is present (the announcer videos do exactly this). Also: a persona image that simply *reads young* can block every generation regardless of dialogue (real_02 was unusable on benign lines) — swap the persona, don't fight the prompt.

**Unwanted recurring element (e.g. headphones)? Check the PROMPT first, not the anchor.** When every clip kept showing headphones, the cause was a prompt line ("headphones on"), NOT the host image (which was clean). Negate it explicitly (`"NOT wearing headphones — none on head or neck"`) or delete the line. Don't re-roll the anchor chasing a prompt-driven artifact.

### Replicate p-video gotchas (PrunaAI, verified 2026-06)

Use `prunaai/p-video` only when the user explicitly asks for it or Veo policy blocks a simple talking-head/reporter ad. For talking heads, use **image-to-video with native model audio**. Do NOT pass an external audio file by default; lip-sync degraded and long audio-conditioned runs capped badly.

- **Chunk at 10 seconds** for speech control. The public duration allows up to 20s, but 10s chunks had better mouth timing, cleaner pacing, and fewer weird sounds.
- **Keep prompts short**: fixed camera, fixed frame, no zooming, no panning, no screen text, no graphics, natural mouth movement, clean native audio. Long negative prompt lists confused the model.
- **No subtitles/on-screen text in the generation**. If text appears, re-prompt shorter with "No screen text, no graphics, no labels, no captions, no subtitles."
- **Camera still breathes slightly** even with fixed-camera wording. The user accepted this as a model limit; do not add stabilization, deshake, frozen frames, or speed changes unless explicitly approved.
- **Post every generated chunk/final link in chat before QA or post-production** so the user can review the raw model output first.

### GPT Image — KIE (default, changed 2026-05-20)

| Function | Module | Auth | Notes |
|---|---|---|---|
| `generate_gpt_image` | `kie_client.py` | `KIE_API_KEY` | **Default.** Text-to-image (no `image_urls`) and image-to-image (with `image_urls`) via KIE's **`gpt-image-2`**. `aspect_ratio`: auto\|1:1\|9:16\|16:9\|4:3\|3:4. `resolution`: 1K\|2K\|4K (1:1 can't be 4K). Use `resolution="2K"`. |
| `generate_image` | `openai_image.py` | `OPENAI_API_KEY` | **No longer default** — OpenAI's gpt-image-2 produces lower-quality output and caps at 1024×1536. Only use if the user explicitly asks for the OpenAI path. |

**Rule change (2026-05-20):** the prior "OpenAI direct, never KIE" rule (which existed to avoid KIE's proxy cost markup) is **reversed**. The user prioritizes image quality + larger 2K/4K output over the markup. Route GPT Image through `kie_client.generate_gpt_image` at 2K. Memory: `feedback_image_gen_provider.md`.

#### Upscaling a PICKED image to 4K — Real-ESRGAN, NOT gpt-image-2 i2i (2026-05-25)

**`gpt-image-2` image-to-image REGENERATES the subject — it does NOT upscale.** Feeding a picked persona back in with a "same man, render at 4K" prompt produced a **completely different person** (a Black man with braids came back as a light-skinned Mediterranean man). i2i is conditioned loosely; it re-imagines. Never use it to "make this exact image higher-res."

**For identity-preserving 4K, use Real-ESRGAN** (true pixel super-resolution — adds pixels, keeps the exact face): `replicate_client.upscale_image(path, scale=2, face_enhance=True)` → `nightmareai/real-esrgan`. Gotchas:
- **GPU input cap ~2.09M px.** A 1152×2048 source (2.36M) is rejected → downscale input to **1080×1920** first, then `scale=2` → exactly **2160×3840** (true 4K 9:16). Pipeline: `scripts/jdc_pod_upscale_4k.py`.
- `face_enhance=True` (GFPGAN) sharpens the face but **smooths skin slightly** (loses a little "documentary" texture) — fine for most, use `False` to keep more imperfection.
- **Replicate throttles to 6 req/min (burst 1) while account < $5 credit** — run upscales one at a time, not in parallel, or you 429.
- **4K does NOT improve the Veo video** (Veo outputs 720p; a 1152×2048 anchor is already 1.6× that). Upscale only for crisp source assets / when the user asks — say so.

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

#### voice_changer (STS) — when NOT to use it, and its hard limits (2026-05-25)

- **Skip the voice_changer for SINGLE-PERSONA videos.** STS *re-synthesizes* — it always sounds slightly hotter/more processed than the Veo source (the user A/B'd it and preferred **raw Veo**). VC's only real job is fixing voice drift **across clips that aren't the same person/seed**, or unifying a host who recurs **across multiple videos**. When all clips of one video are seeded from the **same persona anchor**, Veo's voice is already consistent → VC is pure quality loss. Instead: keep raw Veo audio, **per-clip static-gain to even Veo's clip-to-clip loudness**, concat, one true-peak limiter (Veo source often peaks **over 0 dBFS** — see Veo gotchas). Reference: `scripts/jdc_pod_winner_gen.py` (no-VC path).
- **STS has NO output-loudness/volume parameter.** It always normalizes hot (~-0.5 dBFS peak) regardless of input level — *this* is why VC always comes back louder than Veo. To match the source loudness, do it in **post** (gain the VC output to the source clip's measured LUFS). No `stability`/`similarity_boost` value changes loudness.
- **Settable params** (`elevenlabs_client.voice_changer`): `model_id` (we use **`eleven_english_sts_v2`** — crisper on English than multilingual), `stability` (0.5 — consistency vs expressiveness), `similarity_boost` (0.70 — adherence to clone timbre; high values amplify a dull clone → muffled), `style` (0.0), `use_speaker_boost` (**defaults ON** = more presence/louder/pushed; OFF = less aggressive — the only loudness-ish lever), `remove_background_noise` (default OFF). None set loudness.
- **For a more NATURAL conversion (alternative to STS):** Replicate RVC (`zsxkib/realistic-voice-cloning`) is a different algorithm that preserves more source character. fal.ai hosts the same ElevenLabs STS with lossless PCM but only fal-account voices (not our clones).

**ElevenLabs voice-slot limit = 30 (Creator tier).** Clones hit the cap fast across campaigns. When `/v1/voices/add` 400s, it's the slot limit — free slots by **deleting voices from completed campaigns** (`DELETE /v1/voices/{id}`); the source clips still exist locally to re-clone if ever needed. Check usage: `GET /v1/user/subscription` → `voice_slots_used`/`voice_limit`.

---

## Captions — four scripts, four skills

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

**STT proper-noun substitutions** live in `caption_styled.py:SUBSTITUTIONS`. Add new mistranscriptions there. Already covers `MIHA→MIJA` and the `CHOWCHILLA` variants. **Prefer reducing them at the source** by passing `--biased-keywords Chowchilla Mija ...` to Scribe (sharply improves proper-noun accuracy); the SUBSTITUTIONS dict is the post-fix for whatever still slips through.

### `scripts/caption_hormozi3.py` — Submagic "Hormozi 3" style (reverse-engineered 2026-05-21)

The skill `hormozi3` documents this. Alex-Hormozi creator-caption look: Montserrat Black all-caps, white text with the active LINE in a rotating yellow/green/red accent (per card), small text pop, and **animated emojis that slide across the subtitle**. Reverse-engineered + tuned frame-by-frame against a real Submagic export and user-approved.

```bash
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4>
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4> --biased ""   # generic text
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4> --disclaimer  # + legal disclaimer
```

**`--disclaimer`** overlays the verbatim Pulaski/Jones legal text (skill `pulaski-jones-disclaimer`) at the bottom (white + black stroke, ~0.013 font, vertical 0.99), UNDER the captions, for 6s (`--disclaimer-secs`). It **auto-places at the calmest "most boring" window** via motion analysis (`find_boring_window()` — lowest frame-to-frame difference, avoiding the first/last 4s hook/CTA). Override with `--disclaimer-start <sec>`.

**GLOBAL parametric rule (no word-specific hacks — any new video looks like Submagic):**
- **Font: Montserrat Black (`assets/fonts/Montserrat-Black.ttf`), FIXED `font_ratio 0.0336`, sized relative to WIDTH (not height)** — a ~2-word line fills ~42% of frame width. **WIDTH-anchored so the caption is the SAME physical size across aspects** (`_font_px(width, ratio)` + `REF_ASPECT = 16/9`): a phone shows the same horizontal width whether 9:16 / 4:5 / 1:1, so sizing to height was wrong — it made 4:5 captions ~70% the size of 9:16's despite identical 720px width (fixed 2026-05-22). `font_ratio` keeps its historical 9:16 value, so 9:16 is unchanged and 4:5/1:1 now match it. **NOT fit-to-width/area growth** — that makes short cards too big. Font only shrinks if a line/card overflows.
- **Wrapping: ~2 words per line** (`words_per_line = 2`), max 3 lines; width fallback drops long single words to their own line. Tight stacking = the Submagic look ("I WAS / WRONG", "SIGNIFICANT / POTENTIAL / COMPENSATION").
- **Position: text-block center ~0.70 of frame height** (lower third, well clear below the chin even when she leans/tilts). `vertical_pos` defaults to 0.70 (user-approved 2026-05-21; 0.60/0.64 still caught the jaw on some clips). Stays above the bottom disclaimer band (~0.88–1.0).
- **Color:** white default; active LINE = card accent, rotating per card 🟡`#FCFB14`→🟢`#2AF82B`→🔴`#EE1916`. Stroke `0.06×fontsize`, subtle shadow, **no glow** (glow = newer Impact template).
- **Animation:** captions stay ON continuously (no per-word flash); text pop 96%→105%→100% over 0.12s.
- **Emoji motion = LOCKED-IN system (user-approved GO-TO, 2026-05-21):**
  - **Bound to its text card** — appears with the card, disappears the instant the caption advances (no cross-card linger).
  - **Directional set** (`EMOJI_PRESETS`, rotates): 4 cardinals + 4 diagonals + one **static** — `right, up_right, up, up_left, left, down, static, down_right, down_left`.
  - **Fixed distance, same speed for ALL:** horizontal travel = width of the word **"INSIDE"** (centered ±half, `slide_half`) — a single fixed distance, NOT relative to subtitle/word length. Motion is **EASE-IN-OUT** (`_smooth`, accel→decel like a car) over a **FIXED** `SLIDE_ENTER_DUR 0.30s` (constant speed, NOT card-relative), then **HOLDS at the destination** the rest of the card.
  - **Stays close to text:** vertical travel capped **< 1 line** (`slide_v ≈ 0.85×fontsize`), `sdy/rdy ≥ 0` so it never rises INTO the text (no blocking) and never drifts more than ~1 line away. "up" rests just below text; "down" ~1 line below. Diagonals shallow.
  - **High rate (~60% of cards):** `KEYWORD_EMOJI` broadly expanded + `EMOJI_MIN_GAP 0.4s` low throttle.
  - **No back-to-back repeats:** `pick_emoji(words, exclude=last_placed)` never shows the same glyph on two consecutive placements (prefers a different keyword's emoji in the card, else nothing).
- **Emoji art = PREFER the animated Noto GIF** when one exists for the glyph (flags work here), else **Apple Color Emoji static** (PIL `embedded_color` 160px sbix strike, single-codepoint only — Apple fallback can't shape ZWJ families), else Twemoji PNG. `.nogif` marker caches 404s. All get the transform motion regardless of art source.
- **Render = single-pass:** pre-composite the WHOLE caption track (text + animated-emoji frames + motion) to a PNG sequence in PIL, then **ONE ffmpeg `overlay`**. ~20s for a 60s clip. **Do NOT chain one `overlay` filter per card** — that's O(cards) and takes minutes.

**Measurement lesson:** match RELATIVE proportions (% of frame width/height), not absolute px. Pixel masks are noisy — emoji color contaminates text measurements; measure a clean no-emoji card's widest-line WIDTH as % of frame.

### Submagic emoji-match — the in-house emoji track (built 2026-06)

`caption_hormozi3.py --submagic-emojis <inventory.json>` reproduces Submagic's animated emoji track. Full model + tooling in **`inventory/EMOJI_MODEL.md`**. The hard-won rules (each cost real time this session — do NOT relearn):

- **MEASURE by dissecting EVERY 24fps frame** — DIFF the captioned video vs the clean master to isolate the emoji (compact blob below the text). **Template matching FAILS during the scale-in entrance** (it mis-locks while the glyph grows); the diff works at any scale. Tools: `scripts/emoji_diff_track.py`, `emoji_match_report.py`, `rederive_emoji.py`, `capture_clean_traj.py`.
- **The emoji SET must be VISUALLY verified — never trust blob counts.** Auto-detection is noisy BOTH ways: it OVER-counts (brief caption-text fragments register as phantom emoji "events") AND MISSES real ones whose glyph the wrapped text covers in the crop. Submagic's true rate on the 2-min e_b14 ad was **~10/min (21 emojis)** — not the 14 or 29 the auto-scan claimed at different settings. Eyeball each candidate's lower-caption region at its appear frame.
- **Placement (user-locked):** statics → CENTERED; **subtle sliders (<~80px travel) → rest CENTERED** (they still slide IN, just settle centered); only **big horizontal sliders (>~200px, a clear fly-in) rest OFF-CENTER** under their keyword. A subtle slide parked far off-center reads as a broken "off-center static" (user flagged 🔢/🏆 for exactly this).
- **Vertical: emoji sits ~16px BELOW OUR text block** (`ey = y0 + text_h + 16`). **NEVER pin Submagic's absolute cy** — our caption sits lower than theirs, so an absolute-cy pin lands the emoji ON our words and blocks the subtitle (this caused the "emoji covering the text" bug).
- **Multi-part glyphs** (💰 money-bag, 📊 bar-chart, 💸) render as several colored blobs; the position capture can lock onto one part and read off-center — verify the TRUE center (they're centered in Submagic, not off-center). `rederive_emoji.py` guards: a big-slide needs **≥3 captured frames** (a spurious 1-frame capture is NOT a slide).
- **Rate control:** `--emoji-gap <sec>` thins the AUTO-placed (non-Submagic) emoji rate toward Submagic's ~10/min (≈4.5s gives ~10/min). Default stays emoji-heavy. Glyph fixes verified: the "JUST A KID" emoji is 😔 (sad), not 😴; the courtroom emoji is 🏛️, not 🔒.
- `rederive_emoji.py` is the ONE-SHOT builder: dissect → capture rest/appear/trajectory → apply the placement rules → ready-to-render inventory.

### `scripts/caption_nick.py` — Submagic "Nick" style (reverse-engineered 2026-06-04, internal)

In-house clone of Submagic's **"Nick"** caption template — **white sentence-case Helvetica Neue Bold on a semi-transparent dark rounded box, no color accent, no emoji**. Reverse-engineered frame-by-frame (diff captioned-vs-master) from a real Submagic Nick export and matched 1:1. **Use this instead of the Submagic API for the Nick look** — it's free and uses OUR verbatim Scribe text (Submagic auto-transcribes and can reformat the regulated "significant potential compensation" line or split cards oddly).

```bash
.venv/bin/python scripts/caption_nick.py <in.mp4> --out <out.mp4>
#   --font helvetica|arial   --biased "Chowchilla:3.0,Chino:2.0"   --max-words 2   --vertical-pos 0.754
.venv/bin/python scripts/burn_disclaimer.py <out.mp4> <out_disclaimer.mp4>   # combo (disclaimer is a separate layer)
```

Locked spec (do NOT re-derive): text white `#F8F8F8` **sentence-case** (preserve case — NOT all-caps); box fill `rgb(45,45,42)` @ **0.58** opacity, corner radius ~0.20×box_h, pad_x 0.32 / pad_y 0.14 ×font_px; **font px ≈ 0.044×H** (cap-height ~0.031×H); box center **vpos 0.754**; ~2 words/card single centered line; trailing punctuation stripped (keeps apostrophes); subtle scale-pop 0.94→1.0 over 0.12s. Same single-pass PNG-sequence + one-overlay render as `caption_hormozi3.py` (reuses its `scribe_transcribe`/`probe_*`). Skill: `caption-disclaimer` (Nick subsection).

**Default use case:** sensitive legal ads where the user references **Submagic Nick** but needs verbatim control. For the women's-prison campaign, pair it with `burn_disclaimer.py` or the `pulaski-jones-disclaimer` skill for the final combo file.

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
.venv/bin/python dissect.py <video> [--biased-keywords Chowchilla Mija] [--interval 1.0] [--language en] [--no-ocr]
```

Transcription is **ElevenLabs Scribe** (`scribe_v1`), not local Whisper — needs `ELEVENLABS_API_KEY`.
Pass `--biased-keywords` with the ad's proper nouns (place names, Spanish words, brand names) to
sharply improve their transcription accuracy. `--language` defaults to `en`. (probe / frame
extraction / OCR all still run without a key — only the transcript step calls the API.)

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

### dissect.py concurrency limit — cap at ~4 (ElevenLabs limit, not host memory)

Memory: `feedback_dissect_concurrency`. **Updated 2026-05-20:** the old "MAX 2 PARALLEL" rule
existed because each dissect loaded a ~1GB local Whisper model and running ~10 in parallel
crashed the host. With transcription now on **ElevenLabs Scribe** (remote API), that local-memory
bottleneck is gone — dissect only runs ffmpeg frame extraction locally, which is light. The new
limit is **ElevenLabs' 5-concurrent-request cap** (shared across Scribe + TTS + voice_changer).
**Cap at ~4 parallel** so you leave headroom and don't 429 other ElevenLabs jobs running at the
same time.

```bash
# RIGHT — cap at 4 (respects ElevenLabs 5-concurrent limit):
seq 1 10 | xargs -P 4 -I {} .venv/bin/python dissect.py clips/clip{}.mp4 --interval 1.0

# WRONG — for/wait spawns all 10 simultaneously → 429s from ElevenLabs:
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

`requirements.txt` is now light (requests, python-dotenv, Pillow) — no Whisper/torch, since
transcription is API-based (ElevenLabs Scribe). The voice-QA scripts (`voice_consistency.py`)
pull `resemblyzer` + `librosa` separately if you run them.

System tools — ffmpeg/ffprobe + tesseract on PATH:
- macOS: `brew install ffmpeg tesseract`
- Linux / cloud box: `apt-get install -y ffmpeg tesseract-ocr`

API keys in `.env` (or as real env vars — `load_dotenv()` defers to those): `KIE_API_KEY`,
`ELEVENLABS_API_KEY` (required — transcription + voice), plus `POYO_API_KEY` (Veo) and any
others per the provider-routing table.

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

> Generate the clip → dissect → check the Scribe transcript. If Scribe renders the **intended target word** (or an audibly equivalent rendering), the TTS got close enough.

**Don't revert phonetic spellings just because Scribe transcribed them differently than the original word.** A respell that produces "Miha" or "me, huh?" for `Mee-hah` is correct — it's saying *Mija* in Spanish (/ˈmi.xa/), which is the goal.

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

### Two-character dialogue in ONE clip → both speakers collapse to the same voice
When a single clip has TWO people exchanging dialogue (e.g. a news-interview two-shot: reporter asks, interviewee answers), Veo renders **both voices at nearly identical pitch** even when the prompt explicitly asks for a mature-deep reporter vs a younger-higher interviewee. Measured on the IL JDC news clip: reporter F0 = 130.2 Hz, interviewee F0 = 128.8 Hz → **ΔF0 = 1.4 Hz, below human perception threshold** → it sounds like ONE person doing both parts. The *visual* lip-sync attribution can still be correct (right mouth moves at the right time — verify by frame-extracting at speech boundaries and checking which mouth is open), but the AUDIO reads as a single speaker. No prompt phrasing fixes this.

**Fixes (in order of preference):**
1. **One speaker per clip.** Restructure so each clip carries a single voice — e.g. clip 1 = reporter asks the question (interviewee in frame but SILENT, mouth sealed the entire clip), clip 2 = interviewee answers + next line. Add an explicit "ONLY <X> speaks this entire clip; <Y>'s mouth STAYS CLOSED, makes NO sound" lock. This was the chosen fix and it works cleanly.
2. **ElevenLabs voice_changer dub per speaker segment.** Keep Veo's visual lip-sync, split the audio at the speaker boundary, run each segment through `voice_changer` to a distinct cloned voice (mature vs young), splice back. Guarantees ΔF0 separation; lip-sync stays intact (STS preserves timing).

**Verify with the per-segment F0 probe**: extract each speaker's audio span (`ffmpeg -ss <start> -t <dur>`) and run `librosa.pyin(fmin=70,fmax=400)`; if two on-camera speakers land within ~10 Hz of each other, they will read as the same person.

### Fast 1080p over-sharpens UGC — use Lite 720p for "real phone" look
Veo 3.1 **Fast at 1080p applies aggressive sharpening/upscaling** — edges (hair, beard, jacket seams) come out razor-crisp and read as AI-generated, which kills the UGC "shot on a phone" aesthetic. **Veo 3.1 Lite at 720p looks natural** — softer, like a real front-camera capture — AND comes out louder (avg -17 LUFS vs Fast's -25), smaller files (3× smaller), and cheaper. For UGC selfie/testimonial ads, default to **Lite 720p**; the extra resolution of 1080p is thrown away anyway since social feeds re-encode to ~720p. (Fast/1080p is still right for polished broadcast-style work where crispness is wanted.) Verified on the IL JDC persona-08 UGC ad, 2026-05.

### Veo TTS volume is quiet by default — add an AUDIO CRITICAL clause
Veo's TTS lands quiet (~-25 LUFS) and varies wildly per generation. Adding this clause to the prompt raises it to ~-17 LUFS (near broadcast) reliably:
```
AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational
projection, like he's speaking right into the phone's microphone. NOT
whispered, NOT muttered, NOT soft. Clean clear broadcast-quality audio
that fills the foreground.
```
Then `loudnorm=I=-16` in the stitch pass unifies all clips to -16 LUFS broadcast standard. Belt-and-suspenders: prompt clause gets you close, loudnorm finishes the job.

### "Full projection" + announcer register overshoots 0 dBFS — limiter is mandatory (2026-05-25)
The `AUDIO CRITICAL: FULL projection` clause makes Veo's TTS **overshoot full-scale** — measured source peaks of **+1 to +2.4 dBFS** (over 0) on most clips. A **direct-to-camera announcer** register is louder/more "in your face" than an intimate confession at the same LUFS, so the user perceives it as "red / talking too close" even when the final measures clean. Fixes: (1) **always run a true-peak limiter** on the master (`alimiter=limit=0.71:level=disabled:asc=1`) — it tames the over-0 source; (2) if it still feels hot, **master quieter** (-18 LUFS reads far less aggressive than -16 for the announcer register — but confirm with the user, they may prefer -16); (3) for less shouty delivery, soften the prompt to `clear relaxed conversational, NOT shouting` instead of "full projection." Note: a clip can have a peak >0 dBFS yet `flat factor 0` (mp3 float decode) — the over-0 still distorts on fixed-point playback, so don't trust flat-factor alone.

### Veo TTS mangles slang interjections ("Ayo") and stacked short bursts (2026-05-25)
Veo 3 renders **"Ayo" / "Aye yo" badly** — it came out as "Uh, yo" and blended into the next word. Stacking three short bursts ("Ayo, Illinois, real quick" = greeting + place + aside) makes it worse; Veo runs them together. **Lead with ONE clean opening clause.** "Yo" alone renders fine; a plain imperative ("Listen up, Illinois.") or a question hook ("You from Illinois? Listen.") is cleanest. Same proper-noun rule as always: Veo mangled "**Pere Marquette**" → "Pere Martel" — for legal ads naming a wrong/non-existent facility is a real problem, so prefer well-known facilities (Cook County, St. Charles) or phonetically respell.

### Podcast format — keep "mm-hmm/yeah" reactions, just don't caption them (2026-05-25)
In a podcast/interview register, Veo's interjected "mm-hmm"/"yeah" between sentences read as **natural reactions from others in the room** — the user wants them KEPT (audible), not re-rolled out. Just filter them from the burned captions (filler-word filter in `caption_hormozi3.py`). A "mm-hmm" filling what was dead silence (e.g. "...not you. Mm-hmm. Period.") actually improves pacing. This is the opposite of the confession/UGC rule where fillers are defects — register-dependent.

### Pace consistency across clips — match word count, split long lines with overlap
Veo fits whatever dialogue you give it into the clip duration, so a 28-word clip rushes (~3.5 wps) while a 12-word clip drags (~1.5 wps) — stitched together they feel jerky. **Target a consistent ~2.4 words/sec across all clips** (add `PACE LOCK: ~2.4 words per second. Slow, deliberate, each word given weight.` to the prompt). If a sentence is too long to fit at that pace, **split it across two clips with an overlapping bridge phrase**: clip A ends with "…Just found out." and clip B starts with "Just found out Illinois is paying…". At stitch time, keep clip A whole and trim clip B's duplicate opening phrase (Scribe auto-detects the overlap words and moves the trim-in point — see `scripts/jdc_ugc_p08_stitch.py` `overlap_trim_start`). Net result: full sentence delivered at consistent pace, seamless splice.

### Per-beat emotional tone control + anti-commercial CTA
Once dialogue/pace/audio locks are in place, the next failure mode is **emotional mismatch between clips** — e.g. a quiet vulnerable disclosure clip followed by a CTA clip that suddenly sounds like a TV ad. Two fixes:
- **Reference the surrounding clips' energy explicitly.** For a bridge clip: "START quiet matching the prior disclosure, GRADUAL very-slight lift, END slightly more informational but still subdued — energy goes from -3 to -1, NOT 0 to +3."
- **Kill commercial inflection on CTA words by name.** "Free", "quiz", "qualify" trigger Veo's salesy TTS. Generic "calm tone" doesn't fix it — you must call out the specific words: "NO emphasis on 'Free', NO enthusiasm on 'two-minute quiz', NO rising/upbeat inflection, NO TV-ad voice, NO smile in the voice. Deliver it like a sad afterthought, same subdued register as the disclosure." For richer facial life, generate 2-3 variants with different micro-expression direction (vulnerable-drift / contemplative-build / micro-expressive) and pick the best — prompt-only "be more expressive" is too vague.

### Per-prompt voice variety is weak on Veo — use voice_changer for distinct speakers
Asking for different voices per persona via prompt (pitch/age/register descriptions) barely moves Veo's TTS — across 5 personas with explicit distinct voice profiles, F0 still clustered at 84-109 Hz (only ~25 Hz max spread). If you genuinely need distinct-sounding speakers (e.g. multiple personas in one stitched piece), the prompt won't do it — clone + ElevenLabs voice_changer per speaker is the only reliable path. (For single-persona ads where every clip is the same person, this is moot.)

### Provider degradation can hit Veo across ALL hosts at once
Veo 3.1 routes through Google's backend regardless of reseller, so a Google-side capacity crunch fails KIE, Poyo, AND EvoLink simultaneously. Symptoms seen in one session: KIE returned `500 Internal Error` after full 4-min renders; Poyo got stuck at "running 5%" indefinitely then timed out; EvoLink returned `"Service busy. Allocating resources, please retry later."` at ~50%. When a benign prompt fails on 2+ different hosts, it's a Google-wide crunch, not your prompt — wait 30-60 min rather than burning re-rolls. **EvoLink** (`evolink_client.py`, `veo-3.1-fast-generate-preview`, `EVOLINK_API_KEY`) is a third Veo host to add to the KIE/Poyo fallback rotation. Separately, **KIE's own file host (`tempfile.redpandaai.co`) Cloudflare-429s per-account** if its URLs are fetched too often — don't curl-probe the upload URL yourself (your probes feed the rate-limit counter); free public hosts (catbox/imgur/0x0) also get 429'd by Veo fetchers, so prefer the generator's own storage.

### Underfilled clips → dangerous improv (R10, 2026-06-11)
Veo fills whatever duration you request — a SHORT line in a LONG clip leaves a void it fills with invented monologue. A 10-word hook in an 8s clip produced a full defamatory ramble ("...it is a prison that houses women who have committed serious crimes... housed with male inmates"). **Match dialogue length to duration at ~2.4wps: ≤10 words → duration=4; 15-19 words → 8s.** Never leave >2s of unscripted room. Per-clip Scribe QA catches it when it slips through — and also catches clip↔line MAPPING bugs after any re-segmentation (an off-by-one in R10's loop silently dropped a beat and shifted every line; the transcript check caught it on clip 2). Verify the first persona's transcripts line-by-line before letting a big multi-persona batch run.

### Background stillness — prompt lock + dense QA + frozen-plate rescue (2026-06-11)
Veo renders background motion non-deterministically per clip (washer drums spin, doors swing open, cars pass), breaking stitched-ad continuity. Three-part rule:
1. **Prompt:** audit each persona setting for motion sources BEFORE generating; add a global BACKGROUND LOCK clause ("completely STATIC — no moving people, vehicles, screens, flickering lights; nothing in motion except her") plus setting-specific locks (machines IDLE + doors CLOSED, street empty, car PARKED engine off).
2. **QA (user-locked):** background-motion checks need DENSE sampling — `fps=6` tile grid over the WHOLE clip, NOT a single spot frame. A door swing is an event in time; a single-frame check passed a still-moving door twice.
3. **Deterministic rescue:** when re-rolls keep drawing motion and a VEED alpha matte exists, composite the persona cutout over a FROZEN (blurred) background plate for the offending segment — motion becomes impossible. Used on the l7 laundromat CTA. Reference: `scripts/cawp_r10_blur_finish.py` + memory `feedback_static_backgrounds`.

### google-flow free queue ops (403/429)
The free `veo-3.1-lite-low-priority` queue throws transient 403s under sustained load — `googleflow_client` retries internally and usually recovers, but a run can die when retries exhaust, and hard 429s leave a `[FAIL]` hole. **Just relaunch the same gen script**: skip-if-exists resumes at the first missing clip; a final sweep re-run fills the holes. Server-side jobs survive local process death (same as KIE/Poyo). Don't run parallel one-off gens during a big batch — the extra submit pressure feeds the throttle.

### Improvisation patterns
Veo will frequently:
1. **Insert filler words** between sentences (often Spanish-sounding gibberish like "Hoeya", "Bacchiazade")
2. **Double proper nouns** ("Miha, Miha")
3. **Add a trailing word** at the end as if starting a new sentence ("And…", "I…", "So…")
4. **Drop the first word** ("I'm" missing at clip start)
5. **Burn hallucinated subtitle text into the frame** — even WITH the "ABSOLUTELY NO ON-SCREEN TEXT" lock, ~10% of clips have garbled text at the bottom (e.g., "sopussol maret beong neolia?", "Juist ex shm sister", "Ex't ife the wbout"). **Cannot be fixed in post — must re-roll the clip.** Use the OCR step in `dissect.py` to flag these automatically.
6. **News-headline phrasing triggers newscaster TTS delivery** — if the dialogue reads like an article intro ("Women from the California women's prisons are finding out they may qualify…"), Veo's TTS shifts to a formal/energetic announcer voice that doesn't match the intimate UGC tone of the rest of the ad. **Fix: rewrite the line to be conversational** ("Women in California prisons may qualify for compensation. For what the guards did.") AND add a tone hint like "SAME intimate quiet tone as the rest, NOT news-anchor, NOT informational, NOT energetic — she's repeating what she just read in her own quiet voice."
7. **Quote-framing ("And it said…", "She's like…") sometimes triggers a second, off-screen narrator voice** for the framing phrase. The framing is rendered by a DIFFERENT speaker than the main character. Fix: drop the framing entirely. Just have her say the line directly.
8. **Doubled lines** — Veo occasionally repeats the last sentence ("Tap the button. See if you qualify. See if you qualify."). Must re-roll. Detect via Scribe transcript word-count.
9. **Em-dash list-completion trap** — Veo invents a noun to "complete" a grammatically-open list. Example from IL JDC: `"...Cook County, St. Charles, or Harrisburg — I need you to hear this"` produced gibberish `"Coast Center"` between "Harrisburg" and "I need" — Veo grammatically completed the list as if the user had said `"Cook County [center], St. Charles [center], or Harrisburg [Center]"`. The em-dash gave Veo permission to keep going.
   **Fix:** restructure so the noun list is grammatically closed before the next clause. Use a preposition + comma:
   - ✗ `"a kid in Cook County, St. Charles, or Harrisburg — I need you to hear this"`
   - ✓ `"a kid LOCKED UP IN Cook County, St. Charles, or Harrisburg, I need you to hear this"`
   The `"locked up in [list],"` structure makes the noun phrase grammatically complete. Veo no longer feels compelled to add a list-completing noun. Same rule applies to em-dashes, "or", "and" — any conjunction without a closing preposition invites improv.
   **BROADER RULE (Chowchilla w05 session, 2026-05): NEVER put an em-dash or a trailing colon in a SPOKEN-DIALOGUE line.** Em-dashes don't just complete lists — they make Veo insert ANY word, most often an invented NAME at a vocative-shaped gap. Real failures this session, all from em-dashes/open colons in the i2v dialogue: `"on a Tuesday — didn't even"`→inserted **"Helen"**; `"completely — figured"`→**"Sam"**; `"my rule — don't"`→**"with Khayyed"**; `"confidential — between"`→**"ping"**; `"in plain words:"`→**"Has a cover"**/**"The bottom line"**. **Write every clip line as closed sentences with periods/commas only.** A trailing colon or em-dash at the END of a clip (a lead-in to the next clip) is the worst — Veo "finishes the thought" with improv. Replace `"my rule — don't look back"` with `"my rule. Don't look back"`.

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
Even with the lock, Veo sometimes adds a trailing word. Detect via Scribe word-timing in dissect output:

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

#### ⚠️ loudnorm PUMPS — use STATIC gain for the final pass (IL JDC, 2026-05-22)

**Single-pass `loudnorm` runs in DYNAMIC mode** — it rides the gain over time (boosts quiet gaps, ducks loud words). On short UGC speech this is audible as **"the volume cuts off / pumps,"** and it can read as clipping. **`linear=true` does NOT fix it**: two-pass linear loudnorm silently **falls back to dynamic** whenever the content's loudness range exceeds the target LRA (a multi-clip ad almost always does). Confirmed on this campaign — the user flagged the pump immediately.

**Fix — measure integrated loudness, apply ONE constant `volume` gain + a true-peak limiter** (transparent, no gain-riding, preserves natural dynamics). Do it ONCE on the **whole concatenated ad**, not per-clip:
```python
# measure integrated loudness of the concatenated ad
input_i = json.loads(ffmpeg loudnorm=...:print_format=json on the concat)["input_i"]
gain = -16.0 - input_i
ffmpeg -i concat.mp4 -af f"volume={gain:.2f}dB,alimiter=limit=0.794:asc=1" ...  # 0.794 ≈ -2.0 dBFS
```
Verify: `astats` Flat factor must be `0.000000` (no clipping) and peak ≤ ~-1 dB. Reference: `scripts/jdc_finalize_v2.py` (step 4b) + standalone `scripts/jdc_refinish.py` (re-applies audio from saved STS without new API calls). **Also: ElevenLabs STS output is HOT (~-0.6 dBFS peak)** — never stack another normalization on top without a limiter.

### Tier 2: ElevenLabs voice_changer (when timbre/mic-character drifts)

`loudnorm` only fixes LOUDNESS. If one clip sounds "from a different mic" (different spectral centroid, different noise floor) compared to the others — that's a timbre problem, not a loudness problem. Use voice_changer.

**Important learnings:**
- Voice_changer normalizes TIMBRE successfully (centroid drift drops from ±15% to ±3%, speaker-embedding sim jumps from ~0.83 to ~0.90+).
- But voice_changer can MAKE LOUDNESS VARIANCE WORSE — the cloned voice's output cleanliness varies per clip, so output loudness diverges. Always run `loudnorm` AFTER voice_changer if you use it.
- **ElevenLabs has a 5-concurrent-request limit.** Use `max_workers=4` in ThreadPoolExecutor.
- Don't bother voice-changing if `audio_match.py` only flags a few clips on LOUDNESS — `loudnorm` alone is enough. Only invoke voice_changer when CENTROID or NOISE differs significantly (>10%/4dB), OR when `voice_consistency.py` flags speaker similarity <0.85.
- **voice_changer also STRIPS background music / room bleed (Chowchilla w05 session).** STS re-synthesizes ONLY the voice, so a clip with hallucinated instrumental music or "(paper rustling)" comes out clean after the VC pass. So the voice-change pass doubles as music removal — no separate de-noise step needed.
- **Clone the persona's voice ONCE and reuse the `voice_id` across ALL variation ads** (e.g., w05 E/D/A/C all used one cloned voice → every ad sounds like the same woman). Cache the id (`outputs/<persona>/<persona>_voice_id.txt`). Clone from a ~12s concat of a few clean clips, not one 4s clip.
- **Clone from the CLEANEST clips, ranked — the #1 fix for a muffled clone (IL JDC, 2026-05-22).** Veo audio quality varies clip-to-clip; an instant clone built from dull/compressed clips comes out muffled/boxy. **Rank ALL of a persona's clips across ALL their ads by spectral centroid (brightness) and clone from the crispest 2-3.** Then **audio-isolate** that clone source first (`POST /v1/audio-isolation` — available on Creator tier; strips Veo's room-tone/compression hiss → brighter clone; note it 400s on very short <~4s clips, fall back to raw). Use **`eleven_english_sts_v2` + `similarity_boost=0.70`** (crisper than `multilingual_sts_v2` + 0.85; high similarity_boost makes a dull clone dominate). Verify with spectral centroid: the clean-clone output should track or exceed the original's centroid. Pipeline: `scripts/jdc_persona_clone.py` (one clone per persona) → `scripts/jdc_finalize_v2.py --voice-id <persona clone>`.
- **ElevenLabs output-format ceiling is tier-gated:** `pcm_*` (lossless) needs **Pro tier**; Creator caps at **`mp3_44100_192`** (still a big step up from the `mp3_44100_128` default — always pass 192 explicitly). **fal.ai hosts the ElevenLabs voice-changer** (`fal-ai/elevenlabs/voice-changer`, `FAL_KEY`) and exposes **lossless `pcm_44100`/`pcm_48000` regardless of our tier** (billed via fal's account) — BUT its `voice` param only accepts voices on **fal's** account (presets like "Adam"/"Brian" + public library by name), NOT our private clones (`422 Voice not found`). So fal = lossless + generic/library voice; our direct API = persona's own clone @ 192k. We chose the persona clone (voice match > the marginal 192k→lossless gain for social-feed playback).

### Multi-clip finalize pipeline (Chowchilla w05, canonical)

Per-ad finalize order that produced clean stitched ads: **Scribe-QA → word-aware trim → voice_changer → loudnorm → concat**. Reference: `scripts/chowchilla_w05_finalize.py`. Two techniques worth reusing:

- **Word-aware trailing trim (not silence trim).** Veo adds trailing words/sounds AFTER the scripted line ("They got-", "The bottom line", "(wave crash sound)") that silence-trim keeps (they're speech). Instead, subsequence-match the intended line against the Scribe word list and cut to the **last INTENDED word's end-time** (+ small pad). Removes trailing improv deterministically. Leading junk (a stray "But"/"um" before the first scripted word) is cut the same way. NOTE: this only removes leading/trailing improv — MID-line insertions ("ping", "Sam") still need a re-roll.
- **Lead-in pad before voice_changer for first-word clarity.** Clips that start speaking immediately (first word at <0.1s, e.g. clip4's "women" at 0.079s) come out with a weak/dropped first word after STS — the voice_changer needs lead-in. Fix: after trimming, prepend ~0.15s of **frozen first-frame + silence** (`tpad=start_duration=0.15:start_mode=clone` on video, `adelay` on audio) so STS renders the first word at full energy. Lip-sync stays intact because the video is held during the silence.
- **Shell gotchas (the Bash tool runs zsh, not bash — bit us twice this session):**
  1. **Unmatched glob aborts the whole command.** `rm clipA* clipB*` where one pattern matches nothing → zsh errors `no matches found` and runs NOTHING, so you silently reuse stale intermediates (the "tighter trim + VC" looked applied but wasn't — duration was byte-identical). Use `find <dir> -maxdepth 1 \( -name '...' -o -name '...' \) -delete` for multi-pattern cleanup.
  2. **No word-splitting of unquoted vars.** `for pair in "d sister-call"; do set -- $pair; ad=$1; slug=$2; ...` does NOT split in zsh — `$1` becomes the whole `"d sister-call"` and `$2` is empty (a caption batch silently rendered the wrong paths). Either write explicit per-item commands (most reliable), use a real array, or force-split with `${=pair}`. Don't assume bash word-splitting in loops.

### Transcript word-matching QA — canonicalize before comparing (K-Veo, 2026-06)

Any QA that compares a Scribe transcript word-by-word against the scripted line (clean-verify
reject logic, word-aware trims, overlap detection) MUST canonicalize BOTH sides first, or it
false-rejects clips whose audio is actually perfect:
- **Scribe renders spoken amounts as DIGITS** — "a hundred and sixteen million dollars" comes back
  as "$116 million", which breaks exact-word subsequence matching ("missing words"). Fold any
  number phrase (number-words + glue + currency) to a single `#num#` token on both sides.
- **Benign colloquial swaps** — `got to↔gotta`, `going to↔gonna`, `an↔a` read as missing/extra words.
- **Reaction chains** ("Mm-hmm", "uh-huh") carry internal hyphens — strip nasal/vowel-only chains.
- **Check defects (false-start hyphen, stutter) ONLY inside the kept span** — trailing/leading
  improv is trimmed at assembly anyway; rejecting on it re-rolls clips you'd trim regardless.

Reference implementation: `_prep` / `_prep_ts` in `scripts/podcast_omni_produce.py` (the trim
matcher uses the same canonicalization with timestamps so the cut still lands on the intended
words). Diagnostic rule: when several clips fail the SAME reject reason on a new model, read the
actual rejected transcripts before burning re-rolls — on K-Veo, 3 of 7 beats were false-rejected
3× each (~9 wasted generations) and all cleared first-try once the checker was fixed.

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

### Two-speaker interview trap — correct lip-sync can still be the wrong voice (2026-06-12)

For reporter/interviewee, host/guest, or other 2-speaker clips, do **NOT** stop at "the right mouth is moving." Veo/Kling can assign the mouth movements correctly while both lines still sound like the same man. On the IL JDC Chicago-El interview test, reporter vs interviewee landed at ~130.2 Hz and ~128.8 Hz (`Δ≈1.4 Hz`) — visually acceptable, audibly the same voice.

Rules:
- Audit **each speaker turn separately** with `scripts/voice_consistency.py` or at least a quick F0 readout.
- If the two speakers land in nearly the same register/timbre, fail the clip even when lip-sync passes.
- Default rescue path: **restructure to one speaker per clip** (question clip, answer clip) instead of forcing a 2-voice exchange into one generation.
- **Kling 3.0 element refs** hold two faces better than Veo Lite/Fast, but keep continuous 2-person takes short (~7s) because Kling may auto-cut mid-clip even with `multi_shots=False`.

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

## Viewing user-shared CleanShot links — fetch the image, don't guess

The user frequently drops **`https://cleanshot.com/share/<code>`** links to point at a specific frame/issue (a misplaced emoji, an arrow diagram of the motion they want, etc.). You CAN see these — **always fetch and Read the image instead of guessing at its content** (guessing wasted rounds early in the hormozi3 work). The share page is HTML; the real image is its `og:image`:

```bash
html=$(curl -sSL "https://cleanshot.com/share/<code>")
img=$(echo "$html" | grep -oiE 'og:image" content="[^"]+' | sed 's/.*content="//')   # → https://brief.cleanshot.cloud/media/.../*.jpeg
curl -sSL "${img%%\?*}" -o /tmp/shot.jpeg     # strip the ?min_width=... query for full-res
```

Then `Read /tmp/shot.jpeg`. (Often the screenshot is a frame of one of OUR own renders with annotations drawn on top — useful for seeing exactly which moment/element they mean.)

---

## Caption/emoji visual QA — ffmpeg frame-trace (no ImageMagick)

How the hormozi3 look was reverse-engineered + tuned against the reference, and the repeatable method for any caption/overlay QA:

- **Isolate + tile frames with ffmpeg** — `montage` (ImageMagick) is NOT installed on this host. Build contact sheets with the ffmpeg **`tile`** filter: `ffmpeg -i in.mp4 -vf "fps=10,crop=W:H:X:Y,scale=...,tile=4x6" -frames:v 1 grid.jpg`.
- **Trace motion at 0.1s** (`fps=10`) and **crop a thin band** to the caption/emoji zone so a small glyph is trackable; add a reference line with **`drawbox=x=<cx>:y=0:w=2:h=H:color=red@0.9:t=fill`** (vertical = screen-center for horizontal slides; horizontal = chin/baseline for vertical position). Read the tiled grid row-major to see the position over time.
- **Compare against a reference 1:1** when the user has run our clip through the target tool (e.g. Submagic): overlay a screen-center / chin line on BOTH and match positions.
- **Match RELATIVE proportions** (% of frame W/H), never absolute px — see the hormozi3 "Measurement lesson" above. Pixel masks are noisy (emoji color contaminates text measurement); trace the glyph centroid visually instead.

---

## User skills (`~/.codex/skills/`, mirrored in repo `skills/`)

These auto-surface on relevant user phrases. Don't need to invoke manually — Claude does it.

| Skill | Triggers | What it knows |
|---|---|---|
| `yellow-text-sub` | "caption this", "add subtitles", "Submagic style", "yellow highlight subs" | Full settings for `caption_styled.py` — font 0.0336, aspect-aware vertical_pos, yellow_text default, disclaimer integration. |
| `hormozi3` | "Hormozi captions", "Hormozi 3", "Submagic Hormozi", "yellow green red captions" | `caption_hormozi3.py` — Montserrat Black, rotating yellow/green/red per-line accent, text pop, animated emojis sliding across the subtitle. Font fixed 0.0336, 2-words/line, single-pass render. Global parametric rule. |
| `nick-subtitle` | "Nick subtitle", "Submagic Nick", "dark pill captions", "Nick captions" | `caption_nick.py` — sentence-case white bold sans on a dark rounded box, ~2 words/card, no emoji, no color accent. Use for calmer legal/talking-head captioning with exact transcript control. |
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

**Survivor/confession personas must read ORDINARY, not celebrity (2026-05-25).** For abuse-survivor confession ads the persona has to look relatable and real, or it doesn't land. Append a realism tail to the image prompt: *"Photoreal candid documentary photo (NOT a glamour or fashion shoot, NOT a celebrity portrait) — an ordinary everyday-looking man, plain average features. Natural skin with visible pores, blemishes, uneven tone, slight under-eye shadows, imperfect teeth, no beauty retouching, no filter, no makeup."* Reference batch: `scripts/jdc_podcast_real.py` / `real2.py` (real_01–20 hosts). Also: a too-young-reading face can trip Veo's child-safety block on benign lines — pick an age-appropriate persona for abuse dialogue.

**Chicago survivor realism needs fatigue, not polish (2026-06-12).** When the brief is "Chicago victim 10 years later" or "from the streets/hood, realistic," warm/friendly/promotional language produces faces that are too clean and aspirational. Push the prompt toward weary documentary realism: Black man in his 30s, average features, tired eyes, uneven skin tone, slight facial heaviness, no smile, no beauty mode, no retouching, phone-camera or local-news realism. Do NOT write him like a fashion portrait or lifestyle ad.

**Background-preserving person swaps: nano-banana first (2026-06-12).** If the user gives an existing photo and says "keep this exact background, only change the person," default to `generate_nano_banana` or another strict edit model. `gpt-image-2` i2i tends to re-stage the whole car/interior and beautify the face instead of performing a faithful swap. Preserve crop, camera angle, lighting, reflections, seat/interior geometry, and replace only the subject. After picking the right face, re-run **one locked variant** for the required 2K portrait output instead of broad batch re-generation.

### Persona batches need explicit per-persona facial identity (2026-06-11)

gpt-image-2 MODE-COLLAPSES on repeated demographic prompts: 15 "ordinary Latina woman, 40s-60s" prompts varying only age/setting/clothes returned the same face in 15 outfits (user: "they all look the same... we need to generate each separate identity"). **Give every persona an explicit anthropometry block**: face shape (round/long/heart/square/gaunt/angular), skin tone across the real range (light olive ↔ deep brown; indigenous/Afro-Latina features), nose/lips/brows, build (heavyset/athletic/thin), hair texture, distinguishing marks (mole, scar, missing tooth, penciled brows). Reference batch: `scripts/cawp_latina_personas2.py` (l7-l21). For incarcerated-population realism, include a hard-lived subset and fine-line tattoos on FOREARM/HAND/CHEST only — necks stay clean (neck ink + abuse dialogue compounds Veo moderation). One persona = one facility/life story across simultaneously-running ads; don't have the same face claim different prisons or timelines.

### Announcer vs confession register — pick GAZE to match (2026-05-25)
Two distinct talking-head registers, and the **gaze must match the register** or it reads wrong:
- **Confession** (intimate first-person disclosure): GAZE = **off-camera**, talking to a host/someone in the room; viewer is "overhearing." Off-camera gaze sells the candid feel.
- **Announcer** (direct-response, addressing the audience — "Listen up, Illinois"): GAZE = **directly into the lens**. Set `GAZE: talking DIRECTLY INTO the camera lens, addressing the viewer` in the i2v prompt.
Putting a hype direct-response read into a "confession" visual (off-camera gaze) breaks the candid illusion and reads as an ad. Reference: `scripts/jdc_pod_winner_gen.py` (announcer) vs the confession podcasts.

### Reverse-engineering a winning reference ad → new scripts (2026-05-25)
When the user drops a high-performing ad and wants more like it: transcribe it (Scribe), extract its **beat structure** (the IL JDC winner had 9: hook/geo → qualifier (abuse + facilities) → payoff → kill-objection (no paperwork) → urgency → low-risk (no court/cost) → confidential → CTA → FOMO close), then replicate the structure with fresh, compliance-correct copy. Vary hook/facilities/close per variant. **Compliance rewrite is mandatory** — winning ads often say "owed compensation"/"money won for you"/"what's yours" (all imply a guaranteed payout); rewrite to "may qualify for significant compensation" / "Illinois is paying" (never "paid"/"owed"/"settlement").

**If the user wants the SAME winner angle, keep the angle but not the sentence skeleton.** Preserve the winning framing/camera position and overall beat logic only as the scaffold. Rewrite the discovery mechanism, sentence rhythm, and disclosure logic so each variation sounds like a different person telling the same truth, not a synonym-swapped clone of the winner.

**Name approved concepts and finals with descriptive slugs, not just letters.** `A/B/C/D` are fine during ideation, but once a concept survives review, rename it to something human-readable like `confession`, `sister-call`, `read-twice`, or `direct`. This prevents confusion during captioning, re-renders, launch staging, and future session handoff.

### Re-finalize efficiency — clear only the re-rolled clip's VC cache
When you re-roll a single clip and re-run the finalize: the trim step always regenerates, but `voice_changer` is **skip-if-exists** on `vc/clip{N}_vc.mp3`. So delete ONLY the re-rolled clip's `vc/clip{N}_vc.mp3` (and let trim regenerate `trimmed/`); all other clips reuse their cached VC → no wasted ElevenLabs calls, finalize stays cheap.

### Multi-character scenes — composite two-shot anchor (gpt-image-2 i2i merge)

For a two-person scene (e.g. news interview: reporter + interviewee in one frame), don't try to text-prompt both characters from scratch — **merge the two picked persona refs into one composite scene image via gpt-image-2 image-edit**, then use that composite as the video anchor. Pattern (IL JDC news ad, `scripts/jdc_news_composite_anchor.py`):

1. Generate/pick the two persona refs separately (1 reporter, 1 interviewee).
2. `generate_image(prompt="<two-shot composition: X on left in profile holding mic, Y on right 3/4 to camera, under the El tracks>", image_paths=[reporter.png, interviewee.png], ...)` — gpt-image-2 edit mode merges both faces+wardrobe into one scene. Render 2-3 framing variants, user picks one.
3. Feed the composite as the video anchor:
   - **Veo**: `FIRST_AND_LAST_FRAMES_2_VIDEO`, pass composite twice (start=end).
   - **Kling 3.0**: composite as `image_urls` baseline + the two personas as `kling_elements` (`@element_X`) for stronger per-character identity lock. Kling needs **2-4 imgs per element** — generate a 2nd angle of each persona via gpt-image-2 i2i (`scripts/jdc_news_kling_element_variants.py`).

The composite keeps framing/lighting/wardrobe consistent across all clips that reuse it.

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

### Video matting / background removal — VEED on fal (preferred), RVM legacy

**Preferred (user-locked 2026-06-10): VEED background removal on fal** — `fal_client.remove_background(video_path, out_path)`, model `veed/video-background-removal/fast` (~$0.012/30 frames ≈ $0.08 per 8s clip). Default `output_codec="vp9"` returns a webm **with a real alpha channel** → composite with plain ffmpeg `overlay` (put `-c:v libvpx-vp9` BEFORE the webm input to preserve alpha) — **no chromakey, no green spill**. `variant="green-screen"` exists if a keyable green output is needed; the standard (non-fast) variant adds edge refinement at ~2x price.

Replicate RVM below is the **legacy fallback** (`arielreplicate/robust_video_matting`, ~$0.05–0.15 per clip). Specifics from production use:
- **RVM green color is `0x78FF9A`** (light-leaf green), not pure `0x00FF00`. Sampled from actual Replicate output.
- **chromakey settings**: `similarity=0.12, blend=0.04` — milder than defaults. Grey clothing has similar luminance to green; aggressive chromakey eats hoodies.
- **RVM strips audio** — pass the ORIGINAL mp4 as a 3rd input to ffmpeg for the audio map (`-map 2:a`).
- **Watermark on free-tier output**: small green "DLY"/text on the persona's clothing. Not visible after composite if persona scale + position covers it.
- Reusable: ONE matte file (`<persona>_greenscreen.mp4`) works across UNLIMITED background swaps. Generate once, composite many.
- Reference: `replicate_client.py` + `outputs/illinois_jdc_urban_peer/ugc_greenscreen.mp4`.

### gpt-image-2 60s timeout fix

High-quality (`quality="high"`) 1024×1536 or 1536×1024 renders take 60–120s. OpenAI's default httpx timeout is 60s — renders fail with "Connection error." **Already fixed in `openai_image.py`**: client initialized with `timeout=600.0, max_retries=2`. Preserve this when refactoring.

---

## Claymation b-roll explainers (Seedance, prompt-driven)

Built for the IL JDC campaign (2026-05): a ~54s first-person survivor explainer told entirely in **claymation b-roll** (Aardman / Wallace-and-Gromit look) + ElevenLabs VO + Hormozi captions. Scripts: `scripts/jdc_claymation_*.py`, `scripts/jdc_vo_full.py`, `scripts/jdc_claymation_assemble{,_v2}.py`.

### Why claymation for sensitive topics
For sexual-abuse / juvenile-justice creative it's the **moderation-safe AND ethically-sound** way to tell the story:
- **NEVER** depict the act, nudity, or a minor in any sexual context. Hard line.
- Show the horror through the **child's REACTION** (terror in the eyes, curling up, silent tears) — NOT the abuser, NOT the act. The threat stays off-frame.
- For "abuse by a guard," use **power-imbalance metaphor only**: a looming uniformed SHADOW over a small recoiling kid, or a heavy hand on a shoulder. This is standard survivor-PSA / documentary visual language.

### Seedance style is 100% prompt-driven (no preset param)
Style ("claymation", "analog grunge VHS") lives in the **text prompt**. Reliable claymation recipe — a shared style block appended to every shot so clips cut together:
> "Handmade claymation stop-motion, plasticine modeling-clay with visible thumbprints and fingerprint dents, hand-sculpted surfaces, matte clay sheen, gentle jerky frame-stepping stop-motion movement, shallow tabletop miniature depth of field, Aardman Wallace-and-Gromit diorama craft."

Keep a **cold / muted / desaturated** block for dark beats and a separate **BRIGHT / warm / sunny / vivid / golden** block for the hope beats — the tonal contrast IS the emotional payoff.

### Seedance gotchas (learned this campaign)
- **Renders clay figures NUDE/shirtless when clothing isn't specified.** Any figure shown below the neck → add "WEARING a plain t-shirt / hoodie / etc." Tight face shots are mostly safe; group/torso shots came back nude until clothing was forced (hit `news_shock`, `happy_bright`, `justice` shots).
- **OpenRouter has STRICTER output moderation than KIE.** OR rejected a "kid recoiling in fear" clip (`"output video may contain sensitive information"`) that KIE passed. Route sensitive shots (kids, officers, lockup, abuse-adjacent) to **KIE** (permissive); use **OpenRouter** for benign/faceless to save the ~$0.02/sec. Both run Seedance 2.0 Fast.
- **Moderation evasion — decompose the composite.** If "officer + kid + lockup in one frame" is restricted, split into separately-benign clips (kid walking alone + a door closing) and imply it in the EDIT.
- **Skin-tone descriptor, not racial label** (same as the Veo rule): "deep-brown skin" passes where "Black" can flag, and nails the demographic. Avoid the trigger phrase "juvenile detention" — let visual cues (bars, razor wire, El, cells) carry it.

### Assembly — sync b-roll to the VO word timings
- **VO = ElevenLabs TTS** (no lip-sync to preserve → fresh TTS is correct, NOT voice_changer). First-person survivor, **`eleven_v3`** (expressive, supports `[sighs]`/`[exhales]` tags) worked. Weathered male; audition several voices — campaign-cloned persona voices add demographic authenticity. Spell "St." as "Saint" so TTS doesn't say "Street"; verify proper nouns via Scribe (Brian said "Audy"→"AW-dee" correctly).
- Pull **Scribe word timestamps** and cut one clip per beat/word (one clip per facility name; "behind bars" lands exactly on "locked me up"). Pattern in `scripts/jdc_claymation_assemble.py`: `SEGMENTS = (slug, dur[, in_point])`. Per-segment **in-points** catch a specific moment (start the cell-door clip at its 2.0s mark so the bars are already closed).
- **Make an emotion hit instantly.** A "slowly breaks into a smile" clip builds too slowly to land on a 1-word beat; either use a late in-point OR re-roll "beaming from frame one." For a punchy cut the emotion must be present at the clip's FIRST frame.
- **Cumulative trim drift:** concatenating many re-encoded segments accumulates ~0.04s/segment rounding → ~0.4s visual drift by the end (captions stay Scribe-synced to the audio regardless). Fine for b-roll; for frame-tight cuts use precise-PTS trimming.

### Creative
- **Open on a CHARACTER (a face), not an establishing building** — for cold-traffic scroll-stop a scared kid's face >> a skyline. The building/skyline establishing belongs in a LATER beat. (A/B'd both: `explainer_v2` police-open vs `v1` building-open — the face-open hooks harder.)
- **Make proof beats literal, not abstract.** If the line says he saw the news / learned Illinois paid out millions, show the character READING or SEEING the news and reacting in shock. If the line says other people came forward, show MANY survivors, not a single generic figure. If the line says "locked me up," land on bars / a closing cell / escort, not a vague hallway.
- **Hope beats need instant contrast.** When the copy turns toward justice / relief / brighter future, switch to a clip that is already bright and joyful from frame one. A slow emotional transition misses the beat and feels late.
- **A meaningful ending beats an abstract one** — "face turning into the light" read as random; "the man kneeling to comfort his younger self" (closure) was the fix.

---

## Publishing to AdMachin (upload + launch)

Once an ad is finished, push it into **AdMachin** (the user's own ad platform — `github.com/harrymomomedia/admachin`, REST v1 at `https://admachin.com/api/v1`). Two ways in, both wired up:

### Python client + push script (the automation)

- **`admachin_client.py`** — thin REST wrapper, mirrors the other `*_client.py` modules. Reads `ADMACHIN_PAT` + `ADMACHIN_API_BASE` from `.env`. Auto-sends an `Idempotency-Key` on every POST/PATCH (server dedups 24h). Raises `AdMachinError` with `.code` (`FORBIDDEN` = PAT missing a scope, `UNAUTHENTICATED` = bad token, etc.). Functions: `upload_creative`, `create_ad_copy`, `create_ad`, `generate_combos`, `create_link`, `launch_ad`, `pause_launch`, `resume_launch`, plus read helpers (`list_workspaces`, `list_ad_plans`, `list_creatives`, `get_creative`, `get_ad`, `get_launch`).
- **`scripts/admachin_push.py`** — orchestrates **upload → assemble → (gated) launch**:
  ```bash
  # upload + assemble a DRAFT ad, NO spend (stops here by default):
  .venv/bin/python scripts/admachin_push.py outputs/<campaign>/final.mp4 \
    --project-id <uuid> --headline "..." --primary "..." --ad-type my-campaign-2026-06-01
  # go live on Facebook (⚠ SPENDS REAL MONEY) — gated:
  .venv/bin/python scripts/admachin_push.py final.mp4 --campaign <name> --launch        # prompts: type LAUNCH
  .venv/bin/python scripts/admachin_push.py final.mp4 --campaign <name> --launch --yes   # automation (no prompt)
  ```

### API contract gotchas (baked into the client — don't re-learn the hard way)

- **`POST /creatives` is the ONLY multipart endpoint.** ≤200 MiB; MIME must be jpeg/png/webp/gif/mp4/quicktime. Bytes go to Supabase Storage first, then the DB row. Everything else is JSON.
- **Ads have NO link field.** The destination URL is supplied at LAUNCH time as `landing_url` — NOT attached to the ad. `/links` is a separate tracking-link library (`POST /links` needs `name`+`url`); there is **no** `/links/find-or-create` despite the recipe page. So the assemble flow is just creative → copy → ad.
- **No `/projects` or `/me` endpoint yet.** Find `project_id` via `list_ad_plans()` or the web UI. PAT scopes can't be introspected up front — a missing scope only surfaces as `FORBIDDEN` at call time.
- **`launch_ad` needs FB ids that must already exist:** `ad_account_id` (`act_…`), `campaign_id`, `adset_id`, `page_id`, `cta_type` (e.g. `LEARN_MORE`), `landing_url`. Requires the `launch:meta` scope. The client passes a **stable** idempotency key (`launch-<ad_id>`) so a re-run within 24h won't double-spend.

### Copy approval gate (user-locked rule, 2026-06-11)

**Present every headline + primary text VERBATIM in chat and get explicit approval BEFORE creating copy rows or assembling ads.** A template walkthrough or hook-list pick is NOT approval — the final assembled text is what needs sign-off (user: "I need you to present it here for me to approve before you upload it to admachin"). Best pattern (R10): present ~10 lettered options per copy type, the user picks a pool, then sense-pair approved combos across creatives (round-robin, matching copy details like timeframes to each video). If staging ever runs ahead of approval, present everything immediately and amend rejected rows via new copy + `update_ad`. Also: **one writer per JSON state file** — two staging scripts sharing one state file clobbered each other's ids mid-run (read-modify-write race; recover ids from the printed log).

### Launch safety (user-locked rule)

**Launch is gated, never the default.** A plain `admachin_push.py <video>` run stops at a draft ad and prints the id. Launching requires `--launch` AND confirmation: an interactive `type LAUNCH` prompt, or `--yes` for automation. With no TTY and no `--yes`, the launch is **refused** (never silently spends). Per-campaign FB targeting lives in **`admachin_targets/<name>.json`** (gitignored — holds FB ad-account/campaign ids), selected with `--campaign <name>`; CLI flags override. Print a template with `--print-config-template`.

### Secrets

`ADMACHIN_PAT` is in gitignored `.env` (and in `~/.claude.json` for the MCP server). **Never** commit it or put it in `admachin_targets/`. PATs are shown once and look like `admachin_pat_<43 chars>`.

### MCP server (interactive — 75 tools)

The AdMachin MCP server is distributed as the private GitHub Packages npm package `@harrymomomedia/admachin-mcp-server`. Consumer repos like this one should use that installed MCP runtime, not paths into the AdMachin builder checkout. On Harry's Mac, the current local fallback runtime is `/Users/harry/admachin-mcp/dist/index.js` and is registered with Claude Code at **user scope**. It exposes the v1 tools (`upload_creative`, `create_ad`, `launch_ad`, insights, etc.) for interactive use. **MCP config is read on cold start — restart Claude Code to load config changes.**

### MCP limits learned (2026-06) — projects/subprojects are UUID-only

- **No project/subproject NAME lookup exists.** Projects & subprojects are only ever referenced by UUID; there is no `list_projects`/`get_project`. You can only *infer* projects from `list_ad_plans` — and a project/subproject with **no ad plans is invisible to the API**. You also **cannot create** a project/subproject via the MCP (UI-owned). To file creatives under a named project/subproject (e.g. "tort / IL JDC"), get the UUIDs from the **web-UI URL** of that subproject page, or identify the right project by listing its existing `ad_copies`/`creatives` and matching the campaign content.
- `upload_creative` lands in the **default (null) project** if no `project_id` is passed. **`update_creative_metadata` MOVES a creative between projects/subprojects** (re-tag, no re-upload needed) — use it to fix mis-filed uploads.
- `list_ad_plans` / `list_ad_copies` return **huge payloads** (saved to a tool-results file) — query with `jq`, don't dump.
- `find_or_create_ad_plan` is idempotent (key = project_id + subproject_id + title). Upload is free/safe; **launch SPENDS — keep it gated.**

---

## Session Memory Pass

When the user asks to update learnings, save memory, create rules/skills from a completed session, or prevent the same mistakes in future sessions, use the `session-memory-pass` skill. Use judgment: save only durable lessons that are likely to matter again, including user preferences, rejected directions, wording constraints, prompting lessons, model/provider gotchas, production QA findings, scripts/assets/final outputs, and "do not repeat" patterns. Put campaign-only details in `inventory/` or `outputs/<campaign>/`, broad project rules in `CLAUDE.md`, and reusable workflows in `~/.codex/skills/` mirrored to repo `skills/`. Commit/push only the memory/rule changes and leave unrelated dirty files alone.

---

## Git / GitHub Handoff Safety

- **Re-check branch + status immediately before staging and immediately before pushing.** Multiple Codex sessions can operate in this repo at once; another session may checkout a branch, commit the dirty files, or push while this session is still reasoning. Do not trust an earlier `git status`.
- If expected dirty files disappear or the branch changes mid-task, pause and inspect `git status`, `git log --oneline -8`, `git reflog -8`, and `git diff main..HEAD` before doing anything else. Determine whether another session already committed the work instead of creating duplicate or conflicting commits.
- Before pushing a branch that includes newly captured work, run a secret scan over exactly what will be committed or pushed. For a branch already committed by another session, scan `git diff --name-only main..HEAD` file contents before fast-forwarding `main`.
- When a fast-forward is safe but the active worktree is on another session's branch, prefer `git push origin HEAD:main` over switching branches. This avoids disturbing the other session's checkout while still updating GitHub.

### Secret handling (learned the hard way, 2026-06-12)

- **Never write a real secret value into ANY file — including scratch notes and session logs.** `SESSION_LOG.txt` once captured two plaintext API keys (KIE + ElevenLabs) and got pushed; cleanup took a full `git filter-repo` history rewrite + force-push. Reference keys by env-var name only (`KIE_API_KEY`); values live exclusively in gitignored `.env`.
- **A secret pushed to GitHub is compromised — rotation is mandatory, scrubbing is not enough.** `git filter-repo` + force-push rewrites the branches, but GitHub keeps serving orphaned commits by SHA for ~90 days, and any clone/fork retains them. Scrub to stop casual discovery, then tell the user to rotate the key in the provider dashboard.
- **Redact, don't delete (user-locked).** When cleaning secrets out of a useful file, replace only the secret with a `[REDACTED-...]` placeholder and keep the rest of the content. Deleting the whole file threw away session notes the user wanted; the fix was recovering the content from the orphaned commit via the GitHub REST API and restoring it redacted.
- **Positive-control every secret scan.** `grep -E "key1\|key2"` matches a literal pipe in ERE — silent false negatives (this happened during the audit). Before trusting a "no hits" result, confirm the pattern matches a planted test string.

---

## AdMachin Tort / Sensitive UGC Rules

For AdSwipe analysis, tort/legal UGC scripts, women's-prison campaigns, CIW/CCWF ads, Veo talking-head production, or legal captions, use the `admachin-video-ads` skill. Core rules:

- Analyze AdSwipe videos transcript-first; viral metrics are sparse and should not drive the whole decision.
- Put audience + harm + "may qualify for significant potential compensation" in the first 5 seconds.
- For sexual-abuse/prison-abuse/legal ads, avoid flashing per-word captions and emoji-heavy styles; prefer calm phrase captions, Nick, simple `caption.py`, or `caption_hormozi3.py --no-emoji`.
- Avoid "private check" because it can sound like a payment. Prefer "private form," "private page," "free case review," or "private questions."
- If Veo/Scribe mishears a key word repeatedly, rewrite around it instead of retrying forever.
- Verify clip 1 before parallelizing clips 2-N, and QA stitched boundaries for ghost tails or soft-dissolve artifacts.

---

## Do Not

- Combine `reference_image_urls` and `reference_video_urls` in one Seedance call.
- **Kill a KIE/Poyo gen process mid-request thinking it cancels the job — it does NOT.** Once submitted, the job is produced and billed server-side regardless of the local poller (image AND video). Killing only stops local polling/download; it saves zero points and stops zero generation. Let it finish or rely on skip-if-exists on re-run. See the KIE section note.
- Commit `outputs/` or `.env` (both gitignored).
- Hardcode API keys — always from `.env`.
- Invent visual details. If the dissect frames don't show it, don't write it into the analysis.
- For legal services lead-gen (prison-abuse compensation campaigns): use the phrase **"significant potential compensation"** when referring to the recovery. Don't say "compensation" alone, "damages", "settlement", "money owed", or "payout" — unify on "significant potential compensation" across all variations of the same campaign. **Exception — IL JDC (2026-06): the user OK'd dropping "potential" — "significant compensation" is acceptable on that campaign.** "Illinois is paying" is compliant; "paid"/"owed"/"settlement" re the *viewer's* recovery are not (a factual "LA County paid $4B" comparison is allowed but needs firm sign-off + the disclaimer).
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
- **Run >4 `dissect.py` instances in parallel** — transcription is now ElevenLabs Scribe (5-concurrent account cap, shared with TTS/voice_changer). Cap at ~4 with `xargs -P 4` to avoid 429s. (The old MAX-2 rule was about local Whisper memory, which no longer applies.)
- **Burn captions onto deliverables by default** — user does captioning in post. Only burn when explicitly asked ("caption this", "with the disclaimer", "Submagic style").
- **Use frozen frames, frame holds, deshake, or speed changes to hide cut-off words, silence, mic glitches, or bad gestures unless the user explicitly approves that exact post process.** The user finds these unnatural. Prefer re-trimming at original speed or re-rolling the bad clip.
- **Submit >20 Poyo generations in parallel** — submit rate limit is 20/10s account-wide. Use `max_workers=10`.
- **Pass 1 image to Poyo `generation_type: "frame"`** — requires exactly 2. For clip-1 anchor pattern, pass the anchor URL twice (start=end).
- **Naive `crop=720:900:0:0` to make 4:5** — keeps Veo's baked-in letterbox bars. Use `scripts/crop_4x5.py` which runs `cropdetect` first.
- **Paraphrase the Pulaski/Jones disclaimer** — it's REGULATED legal copy. Every comma is intentional. Skill `pulaski-jones-disclaimer` has the verbatim text.
- **Frame Veo dialogue as a news-headline** (e.g., "Women from the X are finding out…") — triggers newscaster TTS that doesn't match intimate UGC tone. Rewrite conversationally.
- **Postprocess AI-video problems with frozen frames, slowdown, stabilization, or forced zoom/crop fixes unless the user explicitly approves** — these make videos feel unnatural. Prefer rerolling the bad clip, changing the seed/avatar, or tightening the prompt/provider route.
- **Wait until after verification/post-production to share generated video chunks or finals** — the user wants the clickable video path/link immediately after generation, before QA or cleanup.
- **Default to ElevenLabs Voice Design for reporter/native-video ads** — user rejected the generated reporter voices as fake. Use model-native audio first; use generated external voices only when explicitly requested.
- **Prompt Replicate p-video with subtitles, lower-thirds, news graphics, or verbose instructions** — it can hallucinate baked text and camera drift. Use short fixed-camera prompts with explicit "no screen text, no graphics, no labels, no logos."
- **Use quote-framing in dialogue** ("And it said…", "She's like…") — Veo sometimes renders the framing as a separate off-screen narrator voice. Drop the framing.
- **End a noun list with an em-dash before the next clause** (e.g., "…Cook County, St. Charles, or Harrisburg — I need…") — Veo invents a noun to complete the list ("Coast Center"). Use a preposition + closing comma: `"locked up in [list], I need…"`.
- **Include "Black man" in Veo prompts paired with sensitive-topic dialogue** (sexual abuse, juvenile center, lawsuit) — deterministic moderation block. Use a skin-tone descriptor only: `"man, medium-dark skin tone"`. Same applies to specific commercial settings ("Chicago corner store"), in-car settings + young Black male persona, and neck-tattoo descriptors. See "Veo content-moderation triggers".
- **Retry voice_changer with higher stability to fix big pitch drift** — STS preserves source pitch by design. If F0 delta from ref clip is >40Hz, re-roll the source via Veo instead. Bumping `stability=0.5 → 0.7` only moves sim ~0.03 (0.724 → 0.752 — still under 0.85 threshold).
- **Skip `voice_consistency.py` when user reports voice changes** — `audio_match.py`'s ±20% centroid tolerance is too loose to catch what humans hear. Always run both detectors.
- **Dissect multiple `clip1.mp4` files in one run** — they all overwrite `outputs/clip1/`. Copy to unique stems first: `outputs/illinois_jdc_<slug>_clip${idx}.mp4`.
- **Reject/re-roll clips on RAW exact-word transcript matching** — canonicalize both sides first (Scribe renders amounts as digits, swaps got to/gotta + an/a, inserts hyphenated reactions) and check hyphen/stutter defects only inside the kept span. Raw matching false-rejected 3 of 7 K-Veo beats ~9 generations' worth; all passed first-try after the fix. See "Transcript word-matching QA" section + `_prep`/`_prep_ts` in `scripts/podcast_omni_produce.py`.
- **Keep submitting Poyo after 10min timeouts on known-good payloads** — that's a Poyo-wide outage. Switch to `kie_client.generate_veo` at $0.30/clip instead of burning budget on retries.
- **Present video file paths as plain text** — the user's chat client only renders a clickable inline preview when the path is wrapped in `` `backticks` ``. Plain text paths, paths inside markdown table cells, paths in markdown link syntax `[label](path)`, `file:///` URLs, and `http://localhost:<port>/` URLs all FAIL to trigger the preview. Every video file (generated clip, source upload, b-roll, composite, stitched final, aspect variant) must be backticked. See the "Presenting videos in chat" section above.
- **Use Veo 3.1 Quality (`veo3`) on KIE** — HARD RULE: NEVER. Always start with Veo 3.1 Lite (`veo3_lite`). Only fall back to Veo 3.1 Fast (`veo3_fast`) after 2-3 Lite failures on the same prompt for the same failure mode. If Fast also fails, stop and escalate to the user — do NOT use Quality. Memory: `feedback_veo_tier_routing.md`.
- **Call `admachin_client.launch_ad` / `POST /launches` without the `--launch` gate** — launching SPENDS REAL MONEY on Facebook. Always go through `scripts/admachin_push.py`; launch is gated behind `--launch` + confirmation (`type LAUNCH`, or `--yes` for automation). No TTY and no `--yes` = refuse, never silently spend. See "Publishing to AdMachin".
- **Commit the `ADMACHIN_PAT` or `admachin_targets/`** — the PAT lives in gitignored `.env` (+ `~/.claude.json` for MCP); the per-campaign FB targeting configs are gitignored. Never hardcode the PAT or paste it into a tracked file.
- **Create AdMachin copy rows or assemble ads before the user has approved the FULL text verbatim in chat** — a template walkthrough or hook-list pick is not approval. Present every headline + primary final-form first. See "Copy approval gate".
- **Verify background stillness from a single frame** — door swings/drum spins are events in time; use the `fps=6` dense tile grid over the whole clip. See "Background stillness".
- **Give a video clip more duration than its dialogue fills** (~2.4wps; ≤10 words → 4s) — Veo fills the void with invented, potentially defamatory monologue. See "Underfilled clips".
