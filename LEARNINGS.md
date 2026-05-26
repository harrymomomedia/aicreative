# LEARNINGS.md — aicreative

Captured from the end-to-end build of `ad-967437869241001` (California women's prison legal services ad clone). Read this before starting another ad clone — it'll save 10× the time we spent figuring it out.

---

## Generation (Seedance / Kling / Veo)

- **Seedance duration is 4–15s integer.** `duration=3` silently returns `data: null` and crashes the client. Min 4s, max 15s.
- **35s ads need 3 clips** (14 + 11 + 10 split at natural beat boundaries). 2 clips won't fit because 30s loses the CTA.
- **Same anchor image across clips ≠ frame-to-frame continuity.** Each Seedance generation starts fresh from the anchor. You get character/setting consistency but the cut from clip N's last frame to clip N+1's first frame is a visible micro-jump. For seamless continuation, extract last frame of clip N and use it as anchor for clip N+1.
- **Voice is not lockable in Seedance.** No voice ID parameter. Same anchor image biases toward similar voice but each generation re-rolls. For real voice consistency across clips → ElevenLabs dub + lip-sync.
- **Multi-reference is for blending, not storyboarding.** Passing `[img1, img2, img3]` and prompting "shot 1: img1, shot 2: img2..." doesn't produce 3 hard cuts — it blends features into one scene. Use one anchor per clip and stitch with ffmpeg.
- **Veo Fast uses a different endpoint** (`/api/v1/veo/generate` not `/jobs/createTask`) and different polling (`/veo/record-info` with `successFlag` instead of `state`). Output is 720×1280 minimum — won't match Seedance's 480p 496×864 dimensions for clean concat unless you re-encode/rescale.
- **Resolution mismatch breaks concat.** Pick one model for the whole ad (Seedance for 480p, Kling for 720p std) or you'll be re-encoding to normalize. Veo's 720p doesn't match Seedance's 480p.
- **All API responses can have `data: null` on invalid params.** Defensive code: `(body.get("data") or {}).get("taskId")` not `body.get("data").get("taskId")`. And surface the full body in the error message — KIE often puts the validation reason in `body.message`.

## Prompting

- **Forbidden words still apply** (cinematic, professional, stunning, 8k, studio, perfect) — they trigger generic AI-video aesthetic that breaks UGC realism.
- **Photorealism requires explicit imperfection language.** "Visible pores, fine lines, faint under-eye darkness, dry lips, slight asymmetry, no beauty mode, no retouching, no filter" — without these, GPT Image 2 / Nano Banana drift toward the smooth "AI photo" look.
- **i2v needs explicit motion direction.** "He STEPS INTO the cell" produces different result from "He stands at the door." First take of the door-closing shot rendered the guard standing still because the prompt only said "closes the door" without specifying entry direction.
- **Beat-by-beat with timestamps and explicit dialogue** is what unlocks Seedance's audio + lip sync. Free-form description gives lower-quality results.
- **Survivor voice ≠ lawyer voice in visual energy.** A weary/exhausted character reference paired with a composed firm-voice script produces awkward output — Seedance smooths one toward the other and you lose both. Match script tone to the visual character's energy.

## Content moderation

- **Soften abuse language at the prompt level.** "What I went through" passes; "what the guards did to me" risks tripping. The ad's MEANING can stay strong with softer wording.
- **Don't put "just out of prison" or "victim" in image-gen prompts** — GPT Image 2 will refuse or sanitize. Encode the context visually (tan institutional pants, weary look) without naming it.
- **Legal services language has its own rules** outside content moderation, and they're **per-campaign / per-state**. Chowchilla (CA): use "significant **potential** compensation" (keep "potential"). **IL JDC (updated 2026-05): rule is looser — drop "potential", use "significant compensation"; recipient must be "may qualify for" / "may get" (NEVER "owed"/"paid"/"will get"); "Illinois is paying" is OK as a general statement.** Never "settlement"/"damages"/"payout". Same with "what your case is worth" → "check if you may qualify." State bar regulates legal-ad copy independently of platform moderation — confirm phrasing per campaign before bulk-running.

## Voice / pronunciation

- **Seedance native audio mangles proper nouns.** Especially place names. Always test pronunciation in a 4s clip before committing to a 14s generation.
- **Phonetic respells in the prompt fix most of it.** Hyphenated form (`Chow-chilluh`) is more reliable than space-separated (`Chow chilla`). Match the actual sound, not the spelling.
- **Pronunciation can drift at longer durations.** "Chow chilla" worked clean at 4s but drifted to "chowchillala" at 14s with the same prompt. The fix was a different respell (`Chow-chilluh`) — more phonetically explicit.
- **Long-term answer is ElevenLabs dub + lip-sync.** For multi-clip ads with proper nouns, generate Seedance with audio (use it as a guide track for lip motion), replace audio with ElevenLabs (using a fixed `voice_id`), optionally re-sync lips with Sync.so/Hedra via KIE.

## Image generation (GPT Image 2 / Nano Banana 2)

- **GPT Image 2 schema:** `aspect_ratio` + `resolution` ("1K" | "2K" | "4K") — not pixel dimensions. 1:1 can't be 4K. `auto` aspect ratio caps at 1K.
- **GPT Image 2 vs Nano Banana 2:** GPT is sharper and better at instruction-following (specific clothing/glasses/setting); Nano Banana is generally better at skin texture and the "phone camera" feel. For UGC reference shots, both work — GPT 2 has been the workhorse here.
- **Image-to-image vs text-to-image are separate model strings:** `gpt-image-2-text-to-image` vs `gpt-image-2-image-to-image`. Pass `image_urls` to switch.

## Reference characters

- **Generate 4 candidates in parallel** (different settings: bedroom, parking lot, kitchen, porch). Each becomes a different "person" with different vibe — pick the one that matches the script's emotional register.
- **The kitchen-at-night setting reads as the most vulnerable/intimate.** Pairs well with survivor testimonial scripts. Bright daylight + parked car reads as more composed/lawyer-spokesperson.
- **Use the same reference image throughout the 3 clips** for character consistency. Don't try to mix references — they'll drift.

## Captions

- **STT auto-corrects some pronunciations and mangles others.** Phonetic respell `Chow-chilluh` came back as `Chowchilla` (great — captions read clean). But `Chowchilla` (in another segment) came back as `Chowchilly`. Always use a substitution dict for known proper nouns. See `caption.py` `SUBSTITUTIONS`. *(Update 2026-05-20: transcription moved from local Whisper to ElevenLabs Scribe — pass `--biased-keywords` with the proper nouns to cut mistranscriptions at the source; SUBSTITUTIONS remains the post-fix.)*
- **TikTok/Submagic font sizing is ~3–4% of frame height.** Not 6%. ~28–35px on 480p, ~38–45px on 720p. Bigger reads as low-effort/Mr-Beast-ish.
- **Outline scales with fontsize** (~8% of fontsize) so it stays proportional when the font auto-shrinks.
- **Adaptive font shrink for max-2-lines is essential.** Long-word chunks like "SIGNIFICANT POTENTIAL FINANCIAL COMPENSATION" can't fit in 2 lines at default size. The renderer should shrink ~8% per attempt until it fits, with a floor (~18px).
- **Phrase chunking by max_words + natural pauses (>0.35s)** produces TikTok-style timing. Default max_words=4 works; long-word chunks self-shrink.
- **Caption end-time should extend ~0.18s past last word** so it doesn't disappear the instant the word ends.
- **Homebrew ffmpeg on macOS lacks libass.** The `subtitles` filter doesn't exist. Workaround: PIL-rendered PNGs + ffmpeg `overlay` filter with `enable=between(t,start,end)`. More portable anyway.

## Stitching / ffmpeg

- **Concat demuxer is lossless when all clips share codec/fps/dimensions.** All Seedance Fast clips are h264 24fps 496×864 aac 44.1kHz — they concat cleanly.
- **Concat list paths are resolved relative to the list file's location**, not the working directory. Use absolute paths in the list.
- **Filter-complex `concat=n=N:v=1:a=0` for video-only stitching** with audio passthrough from the source via `-map 0:a -c:a copy`. This is how you replace video segments (b-rolls) without disturbing the woman's voice.
- **B-roll insertion timing:** show the character's face first (0–4s) to establish identity. Then cut to b-rolls during content moments. ~20% b-roll / 80% face is the right ratio for a 33s ad — more than that loses the intimate "she's just talking to me" feel.
- **DTS warnings on concat are harmless.** Audio timestamps drift a few microseconds at the cuts; nothing audible.
- **Trim before concat:** `[0:v]trim=4:6,setpts=PTS-STARTPTS` resets the timestamps to start at 0 so the segments line up correctly.

## Workflow

- **Always test pronunciation at 4s before committing to 14s** — saves regenerating 3× the duration if something's off.
- **Generate b-rolls in parallel.** 3–4 simultaneous Seedance/GPT-Image calls is fine; KIE handles concurrent jobs without rate-limit issues.
- **Save reference images by descriptive name** (`character_c_kitchen.png`, `broll_A_silhouette.png`) — easier than v1/v2/v3 when you have variants.
- **Verify a KIE task is real with `recordInfo`** when you're not sure. Returns full task params + result URL — useful for debugging "did this actually run?"
- **The KIE dashboard's task history can lag.** Recently-completed tasks may not appear in the UI for a few minutes. Trust the API response.

## Cost / model picking

| Need | Model | Why |
|---|---|---|
| Vertical UGC talking head | Seedance Fast 480p | Cheapest, native audio, default |
| Better motion fidelity | Kling 3.0 std (720p) | If Seedance fails moderation or motion looks janky |
| Complex physics (pouring, throwing) | Veo 3 Fast 720p | Best physical reasoning, but separate endpoint + 720p won't match 480p footage |
| Character reference shots | GPT Image 2 9:16 2K | Sharp, instruction-following, photoreal-with-prompt-work |
| Establishing/atmospheric b-rolls | Seedance Fast (i2v from a still) | Cheapest, matches main footage dimensions |
| Hand-on-screen / fine motor | Veo 3 Fast | Better hand-object interaction than Seedance |

## What didn't work / dead ends

- **Veo Fast for hand-on-phone tap** — looked stiff and unnatural in our test. Switched to Seedance with phone-camera-grain language and got better result.
- **`subtitles=` filter via libass** — Homebrew ffmpeg 8.1 lacks it. Pivoted to PIL-based PNG renderer.
- **Multi-reference Seedance for storyboard cuts** — model blends instead of cuts. Use separate i2v calls and concat.
- **HelveticaNeue.ttc with `index=8`** for caption font — loaded an italic variant and rendered with weird zebra-stripe outlines. Use single-face TTF (`Arial Black.ttf`) and PIL's native `stroke_width=` for clean outlines.
- **Wrapping ASS path in single quotes for ffmpeg `-vf "subtitles='..'"`** — the shell quotes leak into the filter spec and break parsing. Use no quotes; escape `:` only.
