---
name: interview
description: The GENERAL cross-cutting patterns for ANY two-person interview UGC video, whatever the format — the shared rules that both `street-interview` (outdoor sidewalk vox-pop) and `stacked-documentary-interview` (indoor seated stacked) build on. Its centerpiece is SPEAKER MATCHING (the two hard problems: making two speakers in one piece sound DISTINCT, and keeping ONE speaker CONSISTENT across clips), plus one-speaker-per-clip routing, face/identity anchoring, gaze geometry, dialogue locks, the QA gates (Scribe + F0 + speaker-embedding), and the reusable assembly primitives (word-anchored turn alignment, word-aware trim, the stereo-concat rule, static-gain loudness). Read this FIRST for any interview video; then read the format-specific skill for the pipeline. Use when the user asks about "interview video/ad" patterns, "matching between speakers", "two speakers sound the same", "voice consistency across clips", "interviewer and subject", or is producing any interview format. Learned across the Chowchilla/CCWF vox-pop and Depo-Provera stacked builds (2026-07).
---

# Interview Video — general patterns (read this first, then the format skill)

Two format skills sit on top of this one:
- **`street-interview`** — outdoor sidewalk vox-pop: reporter + mic, wide 16:9 → punch-in to 9:16.
- **`stacked-documentary-interview`** — indoor seated: subject + documentarian, reverse-angle
  chest-up, stacked top/bottom + b-roll.

Everything below applies to **both**. The format skills carry only what's specific to their pipeline.

---

## 1. SPEAKER MATCHING — the two hard problems (the heart of interview video)

An interview is two voices and two faces that have to stay believable relative to each other and
across time. There are **two distinct matching problems**; conflating them wastes re-rolls.

### Problem A — two speakers in one piece must sound DISTINCT ("the two-speaker trap")
When an interviewer and a subject appear together, the trap is that the video model gives them the
**same voice** even when the lip-sync is correct. On our IL-JDC reporter/interviewee test, reporter
F0 = 130.2 Hz and interviewee F0 = 128.8 Hz → **ΔF0 ≈ 1.4 Hz, below the human-perception threshold**
→ it sounds like one person doing both parts, even though the right mouth moves at the right time.
Per-prompt "distinct voices" descriptions barely move Veo (F0 stayed clustered 84–109 Hz across 5
personas with explicit distinct profiles). So:
- **Default fix — one speaker per clip** (see §2). Generate the exchange as separate single-voice
  clips and cut turns in the edit. This sidesteps the collapse entirely.
- **When speakers DO share a clip (a Grok back-and-forth) — force distinctness in post with
  per-speaker `voice_changer`.** Crop to the active speaker per turn → STS that turn's audio to a
  DISTINCT cloned voice per role → remux → concat. Our locked settings:
  `voice_changer(seg, VOICE[spk], out, model_id="eleven_english_sts_v2", stability=0.5,
  similarity_boost=0.7)`, one voice_id per role (e.g. reporter = brighter Latina voice, survivor =
  weathered older Latina voice). Reference: `wp_interview_grok_voiceswap.py`.
- **Verify per turn, not per clip:** extract each speaker span and run F0 (`librosa.pyin`,
  fmin=70/fmax=400) or `scripts/voice_consistency.py`. **If two on-camera speakers land within
  ~10 Hz of each other, they read as the same person — fail the clip** even if lip-sync passes.

### Problem B — ONE speaker must stay CONSISTENT across clips
The same person, generated across N clips, drifts in timbre / loudness / pitch (Veo TTS is
non-deterministic; loudness can span ~40 dB, mic character shifts). Audit and lock:
- **Run BOTH detectors:** `scripts/audio_match.py` (loudness/noise/spectral outliers) AND
  `scripts/voice_consistency.py` (speaker-embedding cosine + F0). Each misses what the other catches.
  Thresholds: **speaker sim ≥ 0.85**, **ΔF0 ≤ 8 Hz** (≤15 Hz tolerable). audio_match's ±20% centroid
  is too loose to catch "wrong person" — that's why you need voice_consistency too.
- **STS pitch-delta zones (know when voice_changer will actually work):** STS preserves the source's
  pitch, so it can unify TIMBRE but **cannot fix pitch drift**. ≤10 Hz off ref → clean; 25–40 Hz →
  hit-or-miss; **>40 Hz off → STS FAILS** (output sounds like a different person). If a clip's F0 is
  >40 Hz from the reference clip, **re-roll the source clip**, don't chase it with higher `stability`
  (bumping 0.5→0.7 only moved sim 0.724→0.752 on a +45 Hz clip).
- **Clone once, reuse the voice_id** across every clip of that person / campaign (cache
  `outputs/<persona>/<persona>_voice_id.txt`). Clone from the **cleanest** clips (rank by spectral
  centroid, isolate audio first). One clone → the whole ad sounds like the same person.
- **When NOT to STS:** for a single-persona video where every clip is the same seeded anchor, Veo's
  voice is already consistent — raw is preferred; STS only adds processing. STS earns its place when
  fixing cross-clip drift or unifying a recurring host across multiple videos.

### Face/identity matching (the visual half of "matching")
- **Anchor everything.** Every clip of a person is generated from a locked anchor image so the face
  stays put. Multi-person scenes use a **two-shot composite anchor** (both faces merged into one
  frame via i2i) so identities hold together.
- **Identity-preserving i2i:** `gpt-image-2` image-to-image reads references from the JSON key
  **`input_urls`** (an `image_urls` key is silently ignored → new person). `generate_gpt_image`
  sends `input_urls`; `upload_file()` every reference to a hosted URL first; keep the prompt MINIMAL
  (never describe the person — words fight the reference). This one fix retroactively explained the
  old "i2i can't hold a face" belief.
- **Clip-1 anchor + eyes-open frames + eye-color lock** (standard CLAUDE.md rules) still apply when
  chaining multiple clips of one face.

---

## 2. One speaker per clip — the governing routing rule

- Two voices in one **Veo** clip collapse to one pitch (Problem A). So on Veo, exactly one person
  talks per clip; the other stays **SILENT, mouth CLOSED, makes NO sound**, and you cut turns in the
  edit. Add an explicit *"ONLY <X> speaks this entire clip; <Y>'s mouth STAYS CLOSED"* lock.
- **Grok Imagine can carry a genuine multi-turn back-and-forth in one clip** (both voices, clean
  audio) — the exception to one-speaker-per-clip — but still post-process with per-speaker STS
  (Problem A) if the two Grok voices land too close.

## 3. Model routing (which generator for which job)

| Job | Use | Why |
|---|---|---|
| Talking clips (either format) | **Grok Imagine** (KIE `grok-imagine/image-to-video`) | Clean audio, holds anchor identity, no Veo phantom "mm-hmm" murmurs |
| **Silent listener pane** | **Grok Imagine** | The ONLY model that renders a real closed-mouth listener (blinks/nods, mouth shut). Every Veo tier animates the mouth; google-flow Veo Lite trips `AUDIO_GENERATION_FILTERED`; omni-flash blocks the prompt |
| Single-speaker beat | **Poyo Veo 3.1 Fast**, frame mode (`image_urls=[url,url]`, `generation_type="frame"`) | Cheap ($0.10), clean single voice; other person silent |
| 2-turn chunks alt | omni-flash (google-flow) | Works but Grok is cleaner |

Grok reads `input.image_urls`; `duration` is a **string**, **~15s is the safe cap** (docs say 30).

## 4. Gaze / eyeline geometry

- **The two speakers must face EACH OTHER** — opposite gaze directions (subject screen-RIGHT,
  interviewer screen-LEFT, or vice versa). Same direction on both reads as broken / two monologues.
- **Register sets the gaze:** documentary/podcast/confession → **3/4 off-camera** (talking to the
  person beside the lens); direct-response / announcer / **CTA** → **directly into the lens**.
- **Gaze is carried by the source face + a horizontal FLIP, not the prompt** — i2i largely ignores
  "look left/right". Generate the easy direction, flip the composite for the opposite (build that
  backdrop text-free first so the flip doesn't reveal mirrored letters).

## 5. Dialogue locks (cut model improvisation)

- **Match dialogue length to clip duration (~2.4 words/sec)** — a short line in a long clip makes the
  model invent (potentially defamatory) filler. ≤10 words → 4s; ~15–19 words → 8s.
- **No em-dash or trailing colon in a spoken line** — the model "finishes the thought" with an
  invented word (often a name). Closed sentences, periods/commas only.
- **DIALOGUE LOCK clause:** English only, no filler, no extra/trailing words, follow the exact lines
  and speaker order, stop after the final word.
- **Pronunciation locks** for proper nouns (descriptive syllable lock beats respell on Grok/Veo;
  pass `biased_keywords=[...]` to Scribe). **No music:** "clean spoken dialogue + natural ambience,
  NO music/song/score."

## 6. QA gates (before assembling — always)

- **Scribe-transcribe every talker** — catch improv, doubled words, mispronunciation. **Canonicalize
  both sides before matching** (Scribe renders amounts as digits; got-to/gotta, an/a swaps; hyphenated
  reactions) or you false-reject clean clips.
- **Dissect any silent listener at 5fps** — mouth must stay closed the whole clip.
- **Run BOTH audio detectors + per-speaker F0** (see §1). Fail on speaker-sim <0.85, ΔF0 >15 Hz
  across clips, or <~10 Hz between two on-camera speakers.

## 7. Reusable assembly primitives

- **Word-anchored turn alignment** (`align()` in `wp_voxpop_reframe.py`): find each turn's start by
  its **first 1–2 words** and advance a cursor — robust to a mispronounced/missing word MID-turn
  (a naive every-word matcher lets one turn eat the whole clip and the crop never switches speakers).
  This maps Scribe word-timings → per-turn (speaker, start, end) for punch-in or stack cuts.
- **Word-aware trim, NOT `silencedetect`** — interview clips carry ambient noise (street/room) that
  defeats silencedetect; cut leading/trailing dead air on Scribe word-timings (pads ~0.05 / ~0.25s).
- **★ Stereo-concat rule:** force **every** segment to stereo 48k
  (`aformat=channel_layouts=stereo:sample_rates=48000`, `-ar 48000 -ac 2` on concat). One MONO
  segment breaks the concat demuxer and **silences everything after it** (−72 dB tail).
- **Loudness:** ONE static `volume` gain + `alimiter` on the whole ad (dynamic `loudnorm` pumps on
  short UGC speech). `loudnorm=I=-16` is acceptable only for very short single-piece concats.
- **Veo watermark:** `delogo=x=646:y=1222:w=72:h=48` (bottom-right) on any full-frame Veo clip.

## 8. Compliance & surfacing (both formats)

- **Present every headline + line VERBATIM for approval BEFORE producing** — a template/hook pick is
  not approval. Carry the campaign's locked recovery phrase, lead the hook with the qualifying
  audience/condition (never the product), name the qualifying harm, no guaranteed outcome, generic
  interviewer (never impersonate a named attorney).
- **Cloud/web sessions:** surface every asset with `SendUserFile` (`display:"render"`) — backticked
  paths don't open the in-session preview. Ship a web-compressed copy; keep full-res masters.
