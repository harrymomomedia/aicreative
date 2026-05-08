# SOP — UGC Ad Cloning End-to-End

Standard operating procedure for cloning short-form UGC video ads (TikTok / Meta / YouTube Shorts) using Claude Code as the orchestrator and KIE / ElevenLabs as the generation backends.

This SOP covers everything from a fresh empty folder to a captioned, stitched, deliverable mp4. Built and validated on the `ad-967437869241001` project (legal services testimonial). Generalize as needed.

---

## 0. When to Use This SOP

Use this when:
- A user wants to clone a competitor ad with their own product/character/cause
- The source is a video file or URL
- The target output is a vertical 9:16 short-form ad, 15–60 seconds
- You have 10–30 minutes of compute time and ~$2–10 in API spend

Do **not** use this for:
- Long-form content (>2 min)
- Live-action shoots (this is generative-only)
- Anything where the original ad's faces/names are reused (legal risk)

---

## 1. One-Time Workspace Setup

### 1.1 System Prerequisites

| Tool | Why | Install |
|---|---|---|
| Python 3.10+ | Whisper, clients, caption pipeline | `brew install python` |
| ffmpeg + ffprobe | Frame extraction, audio extraction, stitch, overlay | `brew install ffmpeg` |
| Git + gh CLI | Backup to GitHub | `brew install git gh` |
| Claude Code | Orchestrator | from claude.ai/code |

Verify ffmpeg has the codecs you need:
```bash
ffmpeg -version | head -3
ffmpeg -hide_banner -filters | grep -E "subtitles|overlay"
```

If `subtitles` filter is missing (Homebrew default does this), the captioning pipeline auto-falls back to PIL+overlay. No action needed.

### 1.2 Create Workspace

```bash
mkdir <project-name>
cd <project-name>
git init -b main
gh repo create <project-name> --private --source=. --remote=origin
```

### 1.3 Copy Core Scripts

These four files are the entire pipeline. Copy from `~/aicreative/`:

```
dissect.py             # video → frames + transcript + scenes
kie_client.py          # 5 KIE generators (Seedance/Kling/Veo/GPT Image/Nano Banana)
elevenlabs_client.py   # ElevenLabs TTS + voice cloning
caption.py             # Whisper → PIL PNGs → ffmpeg overlay
```

Plus the docs:
```
CLAUDE.md              # workflow instructions for Claude Code
LEARNINGS.md           # gotchas captured from prior projects
```

### 1.4 Dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install openai-whisper requests python-dotenv Pillow
```

`requirements.txt`:
```
openai-whisper
requests
python-dotenv
Pillow
```

### 1.5 API Keys

Create `.env` (gitignored):
```
KIE_API_KEY=<get from kie.ai/api-key>
ELEVENLABS_API_KEY=<get from elevenlabs.io>
```

Create `.env.example`:
```
KIE_API_KEY=
ELEVENLABS_API_KEY=
```

### 1.6 .gitignore

```
.venv/
__pycache__/
*.pyc
.env
outputs/
.DS_Store
```

### 1.7 Verify Setup

```bash
which ffmpeg && which ffprobe
.venv/bin/python -c "import whisper, requests, dotenv, PIL; print('ok')"
.venv/bin/python -c "from kie_client import upload_file; print('kie ok')"
.venv/bin/python -c "from elevenlabs_client import list_voices; print(len(list_voices()), 'voices')"
```

Last check confirms ElevenLabs key works. KIE key gets exercised on first generation.

---

## 2. Project Workflow (Per Ad)

### Phase 0 — Intake (2 min)

User drops a competitor video in chat. Capture:
- **Source path** (local) or **URL** (yt-dlp first if URL)
- **What the user wants to clone** — style? script? structure? all three?
- **Their assets** — product images, character preferences, brand
- **Their angle** — same product/cause as original or different?

**Approval gate:** before dissecting, confirm with user: "I'll dissect this and produce a beat-by-beat analysis. Cost: $0 (local Whisper). OK?"

### Phase 1 — Dissect (1–2 min)

```bash
.venv/bin/python dissect.py /path/to/video.mp4
```

Produces `outputs/<videoname>/`:
- `metadata.json` — duration, fps, resolution
- `scenes.json` — scene-cut timestamps
- `frames/` — one jpg per scene boundary, plus interval samples (default every 1.5s)
- `audio.wav`
- `transcript.json` — Whisper word-level

**Auto-fallback for single-shot videos**: dissect.py samples at `--interval` (default 1.5s) when scene detection finds zero cuts. This catches body language and expression changes that scene detection misses.

### Phase 2 — Synthesize Analysis (3–5 min)

Read 5–8 frames spread across the video + the full transcript. Write `outputs/<videoname>/analysis.md` with these sections:

```
## Setting    — location, lighting, time of day, background details
## Character  — age, ethnicity, build, hair, clothing, accessories, energy
## Camera     — angle, distance, handheld vs static, selfie vs tripod
## Beats      — timestamped lines with action notes
## Tone       — emotional register
## Style      — grain, color, audio character, captions, disclaimer
## Notes      — what to clone, what to change, moderation risks, length constraints
```

**Hard rules:**
- Don't invent visual details. If frames don't show it, don't write it.
- Note if the source uses AI-generated imagery (look for disclaimer footer) — informs fidelity bar.
- Flag content moderation risks early (bare skin, sexual references, violence).

**Approval gate:** show analysis to user. Get their angle (same/different product, character changes, script tweaks).

### Phase 3 — Reference Character Generation (3–5 min, parallel)

Run **4–6 candidate references in parallel** so the user can pick the emotional register that matches their script.

Use **GPT Image 2** for photoreal UGC (`gpt-image-2-text-to-image`, aspect_ratio `9:16`, resolution `2K`). Vary across:

- Setting (kitchen, bedroom, car, porch, hallway, garage, etc.)
- Time of day (golden hour, blue hour, fluorescent night, overcast)
- Hair / clothing / accessories
- Age range (typically 30s–50s for survivor scripts; younger for product UGC)

**Photorealism prompt rules** (these are the difference between "AI photo" and "passes as iPhone"):
- "Photorealistic iPhone selfie" / "Raw iPhone selfie photo"
- Force imperfections: "visible pores, fine lines around the eyes and mouth, faint under-eye darkness, dry lips, slight asymmetry, small mole, faint old acne scars"
- Forbid: "no makeup, no beauty mode, no retouching, no filter"
- Camera character: "phone-camera grain, natural unprocessed color, slightly underexposed"

**Forbidden words** (will trigger generic AI aesthetic): cinematic, professional, stunning, 8k, studio, perfect.

**Moderation dodges** for sensitive ads: don't write "victim" / "just out of prison" / explicit harm. Encode visually instead (tan institutional pants, weary look, kitchen-at-night setting).

Save as `outputs/<videoname>/reference/character_<letter>_<setting>.png`.

**Approval gate:** show all candidates side-by-side; user picks one anchor.

### Phase 4 — Script Adaptation (5–15 min, iterative)

Take the original script from the dissect transcript. Decide angle:
- **Verbatim** (if cloning style only) — keep exact words
- **Voice swap** (e.g., lawyer → survivor) — rewrite first-person
- **Same voice, different angle** (e.g., awareness → compensation lead) — rewrite for new hook

Critical legal/copy rules for ads:
- **Never claim outcomes:** "significant compensation" → **"significant potential financial compensation"** (the word "potential" is non-negotiable for legal ads in most US jurisdictions)
- **Never name competitors' attorneys verbatim** — that's their licensed liability
- **Match script tone to character emotion.** A weary kitchen character + composed lawyer-firm voice produces awkward output. Either rewrite the script or pick a different character.

Compute clip split based on Seedance limits (4s min, 15s max):
- 35s ad → 14 + 11 + 10 split at natural beat boundaries
- 60s ad → 15 + 15 + 15 + 15
- 20s ad → 10 + 10 or 7 + 7 + 6

**Approval gate:** show full script with timestamps + clip split + chosen character. Wait for explicit "go" / "approved" / "run."

### Phase 5 — Pronunciation Validation (2–4 min)

**Always test proper nouns at 4s before committing to longer clips.** Seedance native audio mangles unfamiliar names.

```python
from kie_client import upload_file, generate_seedance, download
url = upload_file("outputs/<videoname>/reference/character_X.png", "image/png")
result = generate_seedance(
    "...prompt with proper noun, 4s beat...",
    duration=4,
    aspect_ratio="9:16",
    ref_images=[url],
)
download(result['urls'][0], "outputs/<videoname>/generations/test_4s_pronoun_v1.mp4")
```

**Phonetic respells** that work:
- `Chowchilla` → `Chow-chilluh` (hyphen + "uh" ending)
- `Chino` → `Chee-no`
- `Folsom` → usually fine
- `Represa` → `Re-press-uh`
- Acronyms: drop them, use the city name instead. "CCWF in Chowchilla" → just "Chowchilla."

**If respell fails at longer durations:** try a different respell, OR plan to dub with ElevenLabs at the end (lock voice via fixed `voice_id`).

**Min duration trap:** Seedance rejects `duration<4` with `data: null` (silently). The patched client surfaces this; if you see a NoneType error on `taskId`, check your duration arg.

### Phase 6 — Generate Clips (5–15 min, parallel)

Run all clips in parallel via concurrent Bash invocations. Each clip:
- Same `character_<letter>.png` anchor → consistent character/voice across clips
- Same `setting` description copy/pasted across clips → consistent environment
- Different `Beats:` block per clip
- 9:16, 480p (Seedance), `generate_audio=True` for talking-head, `False` for b-rolls

Save as `outputs/<videoname>/generations/part1_v1.mp4`, `part2_v1.mp4`, `part3_v1.mp4`.

**Approval gate:** user watches each part and approves before stitching.

### Phase 7 — Stitch (1 min)

If all clips share codec params (h264 24fps 496×864 aac 44.1kHz — the Seedance default), use lossless concat demuxer:

```bash
printf "file '/abs/path/part1_v1.mp4'\nfile '/abs/path/part2_v1.mp4'\nfile '/abs/path/part3_v1.mp4'\n" > /tmp/concat.txt
ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy final_v1.mp4
```

**Trim trailing content** (e.g., dropping a closing line):
```bash
ffmpeg -i partN.mp4 -af silencedetect=noise=-30dB:d=0.4 -f null - 2>&1 | grep silence
# find a natural pause >0.4s, cut at midpoint of that pause
ffmpeg -y -i partN.mp4 -t 8.5 -c copy partN_trimmed.mp4
```

**Hard rule:** absolute paths in concat list. Relative paths break because they resolve relative to the list file's directory.

### Phase 8 — B-Rolls (10–20 min, parallel)

**Decide first:** does this ad need b-rolls? They reinforce credibility and pace the talking head, but more than 30% b-roll loses the intimate "she's just talking to me" feel.

Suggested ratio: **20–25% b-roll, 75–80% face**. For a 33s ad: 7–8 seconds of b-roll across 3–5 cut points.

**Always show character first** (no b-roll at 0–4s) — establishes identity before cutting away.

**Two methods:**

A) **Seedance i2v from a still** (preferred — matches main footage dimensions)
1. Generate or pick a reference image (GPT Image 2 for atmospheric shots)
2. `generate_seedance(prompt, duration=4, ref_images=[image_url], generate_audio=False)`
3. Trim to needed length when stitching

B) **Direct text-to-video** for simple shots (`generate_seedance` with no `ref_images`)

**Multi-reference doesn't storyboard.** Passing `[img1, img2, img3]` and prompting "shot 1 / shot 2 / shot 3" blends features into one scene. Use separate calls + ffmpeg concat for hard cuts.

**B-roll insert via filter_complex** (preserves source audio, replaces video segments):
```bash
ffmpeg -y \
  -i source.mp4 \
  -i broll1.mp4 -i broll2.mp4 -i broll3.mp4 \
  -filter_complex "\
[0:v]trim=0:4,setpts=PTS-STARTPTS[s1];\
[1:v]trim=0:2,setpts=PTS-STARTPTS[b1];\
[0:v]trim=6:17,setpts=PTS-STARTPTS[s2];\
[2:v]trim=0:3,setpts=PTS-STARTPTS[b2];\
[0:v]trim=20:31,setpts=PTS-STARTPTS[s3];\
[3:v]trim=0:2,setpts=PTS-STARTPTS[b3];\
[0:v]trim=33,setpts=PTS-STARTPTS[s4];\
[s1][b1][s2][b2][s3][b3][s4]concat=n=7:v=1:a=0[vout]" \
  -map "[vout]" -map 0:a -c:v libx264 -preset fast -crf 19 -c:a copy \
  final_with_brolls.mp4
```

The math must add up: each segment's length × count = source duration. Audio passes through untouched.

### Phase 9 — Captions (3–5 min)

```bash
.venv/bin/python caption.py <input.mp4> --out <output.mp4>
```

Pipeline: extract audio → Whisper word-level transcribe → chunk into 3–4 word phrases (split on >0.35s pauses or word count) → render each as PIL PNG (Arial Black, white fill, black stroke, max 2 lines, adaptive font shrink) → ffmpeg `overlay` filter with `enable=between(t,...)`.

**Caption style defaults** (Submagic / TikTok aesthetic):
- Font size: ~3.5% of frame height (`--fontsize-ratio` not exposed; edit `caption.py` if needed)
- Outline: ~8% of font size, scales with adaptive shrink
- Position: 16% from bottom (lower-third)
- Max 2 lines per chunk; shrink fontsize 8% per attempt up to 10× until it fits

**Whisper mistranscription substitution:**
- caption.py has `SUBSTITUTIONS` dict at top — add proper-noun fixes here
- Common ones already mapped: `CHOWCHILLY` / `CHOW CHILLER` → `CHOWCHILLA`, `FALSUM` → `FOLSOM`, etc.
- Substitution applies AFTER chunking, BEFORE rendering — so case doesn't matter, but watch for new misspellings on each project

### Phase 10 — Disclaimer Overlay (optional, 2 min)

For legal services and other regulated verticals. Tiny lock-bottom strip throughout the video.

(Currently not built into caption.py. Either bake into ffmpeg with a static PNG overlay, or extend caption.py with a `--disclaimer-text` flag. Layout: ~3% from bottom, tiny font ~1.5% of height, captions bumped up to ~22% margin to clear it.)

### Phase 11 — Variant Builds (optional)

To produce variants (different character, different hair, different setting) of the same script:
1. Pick a different character anchor from the reference set
2. Re-run Phase 6–9 with the new anchor
3. Same script copy, only character/setting in the prompt changes
4. Output as `outputs/<videoname>/generations/<X>_final_captioned.mp4` where `X` is a character letter

A/B test which lands harder for the audience.

---

## 3. Quality Gates (when to ask for approval)

| Gate | When | What to show user |
|---|---|---|
| Intake | Before dissect | "I'll dissect, cost $0, OK?" |
| Analysis | After dissect | Full `analysis.md` |
| Character | After reference gen | All candidates inline |
| Script | Before generation | Full timed script + clip split |
| Pronunciation | After 4s test | "Does proper noun sound right?" |
| Each clip | After each Seedance gen | mp4 + task ID |
| Pre-stitch | Before final concat | Confirm all parts approved |
| B-rolls | Before insert | Watch each + confirm timing |
| Captions | After burn | Visual check of styling + content |
| Final | After full pipeline | Final mp4 |

**Hard rule:** never run a paid generation without explicit user approval ("go", "run", "yes", "approved").

---

## 4. File Organization

```
<workspace-root>/
├── .env                       (gitignored)
├── .env.example
├── .gitignore
├── CLAUDE.md                  (workflow instructions for Claude Code)
├── SOP.md                     (this file)
├── LEARNINGS.md               (cumulative gotchas)
├── SESSION_LOG.txt            (optional — chronological transcripts per project)
├── requirements.txt
├── .venv/                     (gitignored)
├── dissect.py
├── kie_client.py
├── elevenlabs_client.py
├── caption.py
└── outputs/                   (gitignored — heavy + often copyrighted source)
    └── <videoname>/
        ├── metadata.json
        ├── scenes.json
        ├── transcript.json
        ├── audio.wav
        ├── analysis.md
        ├── frames/
        │   └── scene_NN_at_TT.TTs.jpg
        ├── reference/
        │   ├── character_<letter>_<setting>.png
        │   └── broll_<letter>_<concept>.png
        └── generations/
            ├── test_*.mp4              (pronunciation tests)
            ├── part1_v1.mp4
            ├── part2_v1.mp4
            ├── part3_v1.mp4
            ├── final_v1.mp4            (raw stitch)
            ├── final_v2.mp4            (trimmed)
            ├── broll<X>_v1.mp4
            ├── final_v3_brolls.mp4     (with b-rolls)
            └── final_v4_captioned.mp4  (FINAL deliverable)
```

**Never commit `outputs/`** — videos are heavy and source content is often copyrighted.

---

## 5. Cost Estimation

Rough per-project budget (KIE credits, USD-equivalent):

| Step | Cost |
|---|---|
| Dissect | $0 (local Whisper) |
| 4 character refs (GPT Image 2 9:16 2K) | ~$0.40 |
| 4 b-roll refs (GPT Image 2) | ~$0.40 |
| 1 pronunciation test (Seedance 4s 480p) | ~$0.05 |
| 3 talking-head clips (14 + 11 + 10s Seedance 480p) | ~$0.70 |
| 4–5 b-rolls (Seedance 4s each) | ~$0.25 |
| Captioning | $0 (local) |
| ElevenLabs dub if needed (turbo, 35s) | ~$0.05 |
| **Total typical** | **~$1.85** |

Variant build adds ~$0.95 (3 more clips + caption pass).

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `AttributeError: 'NoneType' object has no attribute 'get'` from kie_client | Invalid API params (e.g., `duration=3`, missing model field) | Check `body` printed in error — KIE returns reason in `message`. Min Seedance duration is 4. |
| Pronunciation drifts at long duration but worked at 4s | Model context shifts with longer audio | Try a more phonetically explicit respell, or generate without proper nouns and dub |
| Seedance ignores motion direction | Prompt too vague | Use explicit verbs: "STEPS INTO", "REACHES BACK", not "moves" or "closes" |
| Multi-reference produces blended scene, not cuts | Not what multi-ref is for | Use separate i2v calls + ffmpeg concat |
| Concat fails with codec errors | Mismatched codec/fps/dimensions | Either re-encode all to common params, or pick one model for the whole ad |
| `No such filter: 'subtitles'` | ffmpeg built without libass | caption.py auto-uses PIL+overlay path; ignore |
| Caption shows zebra-striped text | Font index loaded italic variant of .ttc | Use `.ttf` single-face font (caption.py default is Arial Black) |
| Caption chunks > 2 lines | Long words exceed line width at default size | Adaptive shrink in caption.py handles this; verify it's running |
| Whisper mistranscribes proper noun | Phonetic respell not in Whisper's vocab | Add to `SUBSTITUTIONS` dict at top of caption.py |
| Veo output 720×1280 won't concat with Seedance 480p | Resolution mismatch | Pick one model for whole ad, or rescale with ffmpeg |
| GPT Image 2 returns 1024×1024 when you wanted 9:16 | `aspect_ratio: "auto"` defaults to 1:1 | Specify `aspect_ratio: "9:16"` and `resolution: "2K"` explicitly |

---

## 7. Reusable Prompt Templates

### 7.1 GPT Image 2 — UGC Selfie Reference

```
Raw iPhone selfie photo of a [age] [ethnicity] [woman/man] [pose: sitting/standing] [setting]. [Build: slim/athletic/etc]. [Hair: detailed]. [Clothing: plain/specific]. No makeup. Real skin texture: visible pores, fine lines around the eyes and mouth, faint under-eye darkness, [optional: small mole, faint old acne scars, sun spots]. Slightly chapped lips. [Expression: composed/weary/etc] — [eye direction]. [Lighting: source + quality]. Behind [subject]: [background details, blurred]. Phone-camera grain, natural unprocessed color, slightly underexposed, no filter, no beauty mode, no retouching. Real, candid, [intimate/lived-in/raw]. Tight head-and-shoulders framing, vertical 9:16. No on-screen text.
```

### 7.2 Seedance i2v Talking Head Clip

```
Setting: [location], [time of day]. [Lighting description].

Character: @(img1) — [age] [ethnicity] [gender]. [Build]. [Hair]. [Clothing]. [Expression baseline].

Camera: phone-held selfie, [angle], [stability]. Vertical 9:16. [Framing — typically tight head-and-shoulders].

Body: [pose], [hand position], [head behavior throughout the clip].

Beats:
- 0–[X]s: [delivery cue]: "[exact dialogue]"
- [X]–[Y]s: [delivery cue]: "[exact dialogue]"

Tone: [emotional register]. [What it isn't — "not crying, not angry"]. [Final descriptor].

Style: phone selfie, [grain level], [color treatment], no music, direct-sound voiceover [with optional ambient note].

The feeling of [emotional payoff].

No on-screen text, no captions, no subtitles.
```

### 7.3 Seedance Atmospheric B-Roll

```
Documentary [shot type] of [subject + setting]. [Specific visual details]. [Lighting source + quality]. [Subject motion — minimal, deliberate]. [Camera behavior]. [Background context, blurred]. Realistic photojournalism style, slight grain, natural color, no music. [Optional emotional descriptor]. Vertical 9:16 framing. No on-screen text.
```

---

## 8. Pre-flight Checklist (Before First Project)

- [ ] ffmpeg + ffprobe on PATH
- [ ] Python venv created with all deps installed
- [ ] KIE API key in `.env`, account has credits
- [ ] ElevenLabs API key in `.env` (optional — only if doing voice dub)
- [ ] `outputs/` and `.venv/` and `.env` in `.gitignore`
- [ ] dissect.py runs without error on a test video
- [ ] kie_client imports cleanly
- [ ] Whisper model downloads on first run (~500MB for `small`)
- [ ] Test that GPT Image 2 returns a 9:16 2K image (one-shot smoke test, ~$0.10)

---

## 9. When in Doubt

- Always test pronunciation at 4s before 14s+
- Always show full prompt before running paid generation
- Always show user the script with timestamps before clip generation
- Always run gens in parallel when there are no dependencies between them
- Always trim with ffmpeg after silence detection — never eyeball seconds
- Always check `LEARNINGS.md` for project-specific gotchas before re-discovering them

---

## 10. Reference Documents

- `CLAUDE.md` — abridged workflow for in-session Claude Code instructions
- `LEARNINGS.md` — accumulated gotchas across projects
- `SESSION_LOG.txt` — per-project transcript (optional, useful for handoffs)
- KIE docs: https://docs.kie.ai/
- ElevenLabs docs: https://elevenlabs.io/docs
