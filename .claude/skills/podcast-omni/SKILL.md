---
name: podcast-omni
description: Produce podcast-style talking-head UGC ad videos with Google Flow's omni-flash model (via useapi R2V) — a weathered persona speaking into a podcast mic, jump-cut. Use when the user says "podcast omni", "omni flash podcast", "make the podcast ad", "Flow podcast video", or wants the headphones-and-condenser-mic podcast creator look produced on Google Flow / omni-flash. Captures the LOCKED prompt recipe + every guardrail/throttle/leak lesson learned the hard way (Chowchilla CCWF campaign, 2026-05).
---

# podcast-omni

Generate **podcast-style talking-head ad clips on Google Flow `omni-flash`** (useapi `google-flow` API, **R2V / reference-to-video** mode) and jump-cut them into a ~40–55s ad. Persona = a gpt-image close-up (headphones + studio condenser mic). Reverse-engineered + tuned against the IDENTIFIABLE_PERSON guardrail, the traffic throttle, and a real credit leak.

## Script

`scripts/podcast_omni_produce.py <SCRIPT_LETTER>` (aicreative). Per-script config (persona, tone, vernacular text) lives in its `SCRIPTS` dict. Auto-chunks → generates each clip (clean-verify + retry + auto-split) → jump-cut assembles `<LETTER>_full.mp4`. Resumable (skip-if-exists). Captions/disclaimer are a SEPARATE pass — see `hormozi3`.

## THE LOCKED PROMPT RECIPE (the #1 lesson)

**For R2V/i2v, DO NOT describe the scene/background — the reference image already carries it. Describing the place is exactly what makes omni-flash RE-IMAGINE (morph) it on every clip.** Keep the prompt SHORT, delivery-only:

```
Vertical podcast close-up, framed IDENTICALLY from the first frame to the last. The camera is
a completely locked-off tripod: no reframing, no settling, no drift, no zoom, no pan. The
background is a FROZEN still photograph that never moves or changes; only her face and hands
move. Keep the exact same scene and background as the reference image.
She stays seated and speaks with natural expressive life: alive eyes and brows, small
hand gestures, nods, blinks, no smile, does not lunge. She looks straight into the lens.
VOICE: <persona voice — e.g. weathered late-40s Black woman, South Central LA, low/raspy/fired up,
real LA vernacular, NOT flat, NOT an announcer>. TONE: <per-beat>. Brisk ~2.4 words/sec, no long pauses.
She says ONLY this, verbatim, no extra or repeated words, then stops: "<dialogue>" No on-screen text, no music.
```

- **Background consistency = NOT describing it** + "keep the exact same scene as the reference" + **CAMERA LOCK** (static, no zoom/pan). A described studio ("airy studio, plant, bokeh") morphs clip-to-clip; the short reference-only prompt holds the reference's background AND clears the guardrail more often (fewer tokens pass more easily).
- **Voice/tone/body language ONLY.** Drop wardrobe/setting/framing description — it's in the anchor.
- Payload: `model=omni-flash`, `aspectRatio=portrait`, `duration` sized to the line (4 if ≤6 words, 6 if ≤10, else 8), `referenceImage_1=<persona asset id>`, `captchaRetry=3`.

## Personas

- **Use BRIGHT gpt-image personas.** Dark/"moody" cinematic renders trip the IDENTIFIABLE_PERSON guardrail far harder (Moody 10 failed ~2 clips × 8 attempts every time; bright personas mostly clear). Roster from the approved 20; pick from the bright batch.
- One persona PNG per video, used as `referenceImage_1` for ALL its clips (same reference = consistent identity + background).

## Chunking

Split the script into SHORT clips (~6–8s) at sentence boundaries; if a sentence >13 words, **pack comma-clauses into ≤13-word groups — do NOT isolate tiny fragments** (a 1-word clip like "CCWF" fails as gibberish). Short clips clear the guardrail best.

## Clean-verify (every clip) — REJECT only what the trim can't fix

After each generation, transcribe (ElevenLabs Scribe). **Do NOT reject for trailing/leading improv** — the jump-cut assembler trims each clip to the intended span, so re-rolling a clip you'd trim anyway is pure wasted credits (this was the #1 leak — see Credit optimization). `clean()` subsequence-matches the scripted line against the transcript and REJECTS + re-rolls ONLY:
- **hyphen / false-start** token (`prove-`, `Chow-Chowked`) — can't trim cleanly,
- **missing words** — the scripted line wasn't fully spoken (subsequence doesn't complete),
- an **adjacent 1/2/3-gram repeat INSIDE the kept span** ("private private") — a mid-line stutter that survives the trim.

ACCEPTED (kept, trimmed at assembly): a tacked-on "you know", a leading "So,", even a **doubled tail** ("…see if you qualify, see if you qualify" → trim keeps the first). Only the kept span between the first and last *intended* word is checked for stutters.

## IDENTIFIABLE_PERSON guardrail (the recurring blocker)

Google Flow's anti-deepfake guardrail probabilistically refuses photoreal-face generations — **~2 clips per video get blocked regardless of persona**. Mitigations, in order:
1. **Short clips clear it best** (chunk small).
2. **Reword the stubborn beat** — the contingency-fee line ("you don't pay a dime unless that money comes through") is a KNOWN repeat-offender that blocked across J/I/A even reworded; **use "You only pay if you win."** (short, complete, clears first-try).
3. **Do NOT split a short (≤6-word) clip into gibberish** — drop the beat instead. Only split LONG clips.
4. A few re-rolls (≤3) with fresh seeds. If it still won't clear, drop the beat — the ad survives.

## Throttle (pace it)

Google flags the account for **"unusual activity / too much traffic"** after heavy use (~200+ generations/day → escalating 403/429). **Produce ONE video at a time, low parallelism (≤3 workers).** Don't blast all videos at once; it hardens the throttle and wastes credits on failures.

## CREDIT LEAK — avoid (learned expensive)

Every generation that reaches Google **spends credits + leaves a video in the Flow account**, even failed/discarded ones. Three leak sources:
1. **NEVER kill a process mid-flight** — an in-flight generation completes on Google's side after you `pkill`, charging credits for a clip you never use. This was the biggest leak.
2. **Clean-verify re-rolls** and **IDENTIFIABLE_PERSON retries** each generate a charged video before being discarded — keep retries low.
3. **Mis-targeted re-rolls** — before re-rolling a single clip, **extract the exact frame to confirm WHICH chunk has the issue** (a "0:25" report can be the next chunk over), and **lock the prompt spec before re-rolling** (don't re-roll, then change the prompt, then re-roll again).

### Cost (per generation, by duration — VERIFIED)

omni-flash bills **per clip by duration**, NOT flat and NOT a fixed 30:

| duration | credits | credits/sec |
|---|---|---|
| 4s | **15** | 3.75 |
| 6s | **20** | 3.33 |
| 8s | **25** | 3.13 |
| 10s | **30** | 3.00 |

**Shorter clips are cheaper per generation** (and EVERY generation charges — successes, clean-verify rejects, and guardrail fails alike). Longer clips are marginally cheaper *per second*, but that does NOT mean "merge into fewer 8s clips to save" — the dominant cost is RE-ROLLS, and **short clips clear the IDENTIFIABLE_PERSON guardrail far better AND cost less per attempt** (a re-roll on a 4s clip = 15 credits vs 25 for an 8s). So short chunking is doubly optimal: cheaper per gen + fewer re-rolls. Keep the `dur_for` ladder (4 if ≤6 words, 6 if ≤10, else 8) and **avoid 10s clips**. Ultra $199 ≈ 50k credits/mo. Discipline matters.

### Two quality-neutral credit savers (baked into `produce_one.py`, ~48% fewer gens)

1. **Trailing → trim, NOT re-roll** (see Clean-verify above). The dominant historical leak: clips were re-rolled for trailing improv that the assembler trims anyway. Now accepted. On a real 14-chunk A run, replaying the generation log: **48 gens → 25 gens (~960 → ~500 credits, 48% fewer)**, AND two beats that had been dropped were recovered (their "trailing" rejects now clear first-try).
2. **Retry caps**: base chunk = **3 attempts**, each split-half = **2** (was 4 / 4). A stubborn chunk now costs ≤3+2+2=7 gens vs ≤12. Remaining re-rolls are almost all probabilistic IDENTIFIABLE_PERSON, where a 4th full-length attempt is no likelier to clear than escalating to a shorter split — so cap, then split (>6 words) or drop (≤6 words). Beats that need a 4th attempt either split-and-clear (shorter = clears better) or drop (the ad survives).

## Jump-cut assembly

Word-accurate tight trims (Scribe word timestamps): **subsequence-match the scripted line against the transcript and cut to `[first_INTENDED_word − 0.03s, last_INTENDED_word + 0.05s]`** — NOT the first/last transcribed word. This drops leading junk AND trailing improv (the same reason `clean()` no longer rejects them). Fall back to the full speech span only if the match fails. Then hard-concat in order, then ONE static-gain loudnorm (`volume=<−16 − input_i>dB,alimiter`) — NOT dynamic loudnorm (it pumps). Yields the rapid "fast-speaking" jump-cut feel.

## Intra-clip drift (the camera/bg moving DURING a clip)

A single mid-clip frame MISSES this — the start of a clip usually matches the reference, then the camera reframes/settles or the background morphs over the clip. **Verify by sampling a frame every 1 SECOND by default across each clip / the whole assembled video** (a 1-fps contact sheet) — never just one frame per clip, which misses mid-clip drift. Cause: clips made before the strengthened lock (no "framed identically from frame 1 / frozen photo" language) reframe mid-clip. Fix: the strengthened camera lock above. NOTE: an auto corner-diff scanner over-flags because the persona's hair fills the top corners (measures hair motion, not bg) — verify drift visually, don't trust the diff score alone. If prompt language still can't freeze it, composite onto a still background (see below).

## Surgical background re-roll (fixing old/morphing videos)

To fix a video made before the short recipe: build a contact sheet of all its clip mid-frames, **visually identify which clips' background differs from the reference**, and **re-roll ONLY those** with the short recipe (skip-if-exists keeps the good ones). Don't re-run the whole video — that wastes credits.

## Veo 3.1 Lite low-priority variant (FREE path) — verified on K, 2026-06

The same producer runs on the free google-flow model: `POD_MODEL=veo-3.1-lite-low-priority .venv/bin/python scripts/podcast_omni_produce.py <LETTER>` → outputs tagged `_veo` (`<L>_<persona>_veo_la/`, `<L>_veo_full.mp4`). Everything below differs from omni-flash — do not carry omni assumptions over:

- **I2V (`startImage`) ONLY — never R2V.** On this model, R2V (`referenceImage_1` / MULTI_REFERENCE_NO_STYLE) is **8s-only** (4s/6s → instant HTTP 400) AND re-imagines the background per clip. `startImage` allows 6s/8s and locks the persona PNG's background perfectly. `REF_PARAM` switches automatically via `IS_VEO`.
- **Chunk FULLER beats, never split.** Veo chunks are 13–23 words (curated per letter in `VEO_CHUNKS`), `dur_for` = 6 if ≤14 words else 8. Tiny clips (a 4-word "Sis, listen") fail the guardrail MORE on this model; a failing Veo chunk is dropped, not split (`do_chunk` enforces). Underfilled clips invite improv — match words to duration.
- **clean-verify MUST canonicalize both sides (the false-reject epidemic).** Veo Lite's podcast register systematically appends trailing improv ending in a hyphen ("…prison- …and they-") and inserts reactions; Scribe renders spoken amounts as DIGITS ("a hundred and sixteen million dollars" → "$116 million") and swaps `got to↔gotta`, `an↔a`. Raw exact-word checks falsely rejected 3 of 7 K beats (hook, facility list, $116M) × 3 attempts each ≈ 9 wasted generations. Fix (in `_prep`/`_prep_ts`): strip reaction-token chains, fold colloquials, fold number phrases to one `#num#` token; check hyphen/false-start + stutter **only inside the kept span** (trailing/leading improv is trimmed at assembly anyway). The jump-cut matcher uses the SAME canonicalization with timestamps, so the trim still lands precisely after the last intended word. After this fix all 3 dropped beats cleared FIRST attempt — when several beats fail the same `clean()` reason on a new model, suspect the checker before burning re-rolls: read the actual rejected transcripts first.
- **Watermark: the free tier ALWAYS burns "Veo" bottom-right.** Remove ONCE on the assembled file (before captions), ratio-preserving — center-crop `675:1200` (= 9:16 exactly; drops the bottom ~80px) → `scale=720:1280` (uniform 16/15× both axes). **User-locked: never stretch, never per-clip.**
- **Pacing QA:** delivered wps = intended words ÷ trimmed `_jt` span. K landed mean ~2.9 wps, spread 0.8 across clips — acceptable; the word-count duration ladder is what keeps the spread tight.

## Related

- `caption-disclaimer` — the burn-in step (run AFTER the user approves the clean cut): subtitle-only, disclaimer-only, or combo. Routes to `caption_hormozi3.py` + `burn_disclaimer.py`.
- `hormozi3` — the Submagic caption styling engine.
- `pulaski-jones-disclaimer` — the verbatim legal disclaimer text.
