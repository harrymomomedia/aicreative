---
name: video-style-stacked-documentary-interview
description: Produce a two-person STACKED documentary / podcast INTERVIEW UGC ad — a subject (survivor / patient / claimant) answering an off-camera-ish documentarian (NOT a news reporter), shot as reverse-angle chest-up talking heads that read as the SAME ROOM, delivered with the subject on TOP and the interviewer on BOTTOM (both panes visible, cut on the same beats) with b-roll cut over the voice. Covers the whole pipeline end-to-end: the two same-room anchor images (exact-face i2i, iPhone-video look, chest-up, 3/4 gaze, facing each other via flip + text-free backdrop), Grok clips for clean talkers AND genuine silent listeners, the stacked/cut assembly (stereo-concat rule, static-gain loudness, watermark delogo, hybrid fallback), b-roll over the VO, and the AdMachin B-Roll library. Use when the user asks for a "stacked interview", "stacked podcast", "documentary interview ad", "podcast-style interview", "two-person interview ad with b-roll", "interview stacked top and bottom", "subject + interviewer testimonial", or wants more videos in this format. For the OUTDOOR sidewalk vox-pop format (reporter with a mic, wide-16:9 punched-in to 9:16) use `video-style-street-interview` instead. Learned on the Depo-Provera meningioma build (2026-07).
---

# Stacked Documentary / Podcast Interview + B-Roll (full pipeline)

A two-person documentary interview delivered as **both panes stacked vertically** — the **subject
(survivor/patient) on TOP**, the **interviewer (a *documentarian*, NOT a reporter) on BOTTOM** — cut
on the same beats, with **b-roll cut in over the speaker's voice**. One person speaks per clip; the
other listens/reacts. Also ship a **CUT** (shot-reverse full-frame) version from the same clips.

> **Read the general `video-style-interview` skill first** — it carries the cross-cutting patterns (speaker
> matching, one-speaker-per-clip, model routing, gaze, dialogue locks, QA gates, assembly
> primitives). This skill covers only what's specific to the STACKED pipeline.
>
> Every rule below was a specific correction on the Depo-Provera meningioma build
> (`claude/ugc-video-style-q4vcfx`, 2026-07). Follow them up front instead of re-deriving.
> For the OUTDOOR sidewalk vox-pop format use the **`video-style-street-interview`** skill.

Reference scripts (that branch): anchors — `depo_interview_set_iphone.py`, `depo_interview_facing.py`,
`depo_doc_notext.py`, `depo_doc_alone.py`; clips — `depo_grok_talk.py` + `depo_grok_talk_rest.py`,
`depo_grok_listen.py`; assembly — `depo_grok_full_assemble.py`, `depo_stacked_grok.py`,
`depo_stacked_hybrid.py`; b-roll — `depo_broll_future_stills.py` + `depo_broll_future_animate_upload.py`;
a second persona pair — `insider_grok_gen.py`. Helper: `admachin_client.upload_broll_clip` /
`list_broll_clips`. `generate_grok` lives on that branch's `kie_client.py`; if absent, POST KIE jobs
directly (payload in §2).

---

## 0. Concept stage (sign-off BEFORE producing)

- **Format:** subject + documentarian, ~11 beats, ~75s. Interviewer asks short questions; the subject
  carries the answers. A separate full-frame **CTA** (direct-to-lens) breaks the two-shot at the end.
- **Hook variety:** each new script must be a *foundationally different angle*, not a synonym swap
  (the number / insider / convenience / misdiagnosis / two-survivors / family / self-discovery /
  duration / too-young / not-too-late). **NEVER open on the product/drug shot** — it draws the wrong
  audience. Lead the hook with the qualifying condition.
- **Compliance (tort/legal): present every headline + line VERBATIM in chat for approval before
  producing.** Carry the campaign's locked recovery phrase (e.g. "may qualify for significant
  compensation"); qualifying condition named FIRST, the drug revealed mid-script; no guaranteed
  outcome; generic interviewer (never impersonate a named attorney); no disclaimer lingo on the
  creative unless asked.
- **Match dialogue length to clip duration (~2.4 words/sec)** — a short line in a long clip makes the
  model improvise. ≤10 words → 4s; ~15–19 words → 8s. Strip em-dashes/trailing colons from spoken
  lines (Veo/Grok "finish the thought" with an invented word).

---

## 1. The two anchor images — 10 LOCKED RULES (each was a correction)

This is the hard part — getting the two same-room reverse-angle anchors right took many rounds.

1. **Same room, but OPPOSITE-wall backdrops (shot-reverse-shot)** — real two-camera coverage: the
   chairs face each other, so each camera sees a **different wall**. Give the subject one wall (e.g.
   family-photo wall) and the interviewer the **opposite** wall (bookshelf/window). Keep the SAME
   warm palette / wall color / wood tones / light so both still read as one home. Do NOT put both in
   the identical backdrop/chair — reads as one person cloned.
2. **Exact faces — real i2i, and the `input_urls` gotcha.** KIE `gpt-image-2-image-to-image` reads
   **`input_urls`, NOT `image_urls`** (an `image_urls` JSON key is silently ignored → the job runs as
   pure text-to-image and returns a different person). `generate_gpt_image` already sends `input_urls`
   for i2i — if faces ever drift wildly, check this FIRST. nano-banana accepts both keys.
3. **On i2i, NEVER describe the person.** Words like "short gray hair, wire glasses" COMPETE with the
   face reference and pull the output toward the words → likeness drift. Keep i2i prompts MINIMAL:
   only action / framing / gaze / setting. The face image drives the likeness.
4. **iPhone-VIDEO look, not polished photo.** Append: *"candid vertical iPhone video frame, deep
   focus with the background in focus, flat even indoor exposure, realistic smartphone color, slight
   sensor grain, no bokeh, no cinematic grade."* (Shallow bokeh + warm grade reads as a staged photo.)
5. **CHEST-UP close-up (waist-up is too wide):** *"tight CHEST-UP close-up, head and chest fill the
   frame, no arms, hands or lap visible."*
6. **Podcast/documentary 3/4 gaze — NOT dead-lens, NOT profile.** Body turned a little, eyeline lands
   just ahead of them (at the person beside the camera). "Mostly forward but a little off to the side."
7. **They must FACE EACH OTHER — opposite gaze directions.** Subject looks screen-RIGHT, interviewer
   screen-LEFT (or vice versa). Same direction on both = broken.
8. **Gaze is set by the SOURCE face + a FLIP, not the prompt.** i2i carries the source's gaze and
   ignores "look left/right". Generate the person looking the direction the model gives easily, then
   **horizontal-flip the whole composite** (PIL `FLIP_LEFT_RIGHT`) for the opposite gaze. BUT a flip
   mirrors backdrop text into backwards letters — so build that person's backdrop **text-free**
   (blurred book spines, "absolutely NO readable text or letters") BEFORE compositing. Flip the FINAL
   composite (flipping only the source face lets the model re-pose to center).
9. **No unwanted over-the-shoulder foreground figure:** *"She is ALONE in the frame — NO other
   person, and NO out-of-focus foreground shoulder, head or figure anywhere; only her and the room
   behind her."*
10. **Keep the subject's ORIGINAL clothing/look** — i2i will "upgrade" a casual gray tee into a
    styled top and beautify the face. Keep them ordinary/real; preserve the exact original wardrobe +
    lav mic (survivor especially).

**Pipeline (order):** resolution **2K** default (4K fine for an establishing empty room), 9:16.
(1) pick the two faces — documentary-real personas (see the persona rules below); interviewer =
documentarian look (casual knit/chambray, warm, NO news blazer, no mic flag). (2) build the subject's
room (t2i, iPhone look). (3) composite the subject (i2i `input_urls`, minimal, chest-up, 3/4, gaze
toward one side, keep wardrobe). (4) build the interviewer's reverse-angle room **text-free** (opposite
wall, blurred spines, same palette/light). (5) composite the interviewer (i2i, minimal, chest-up, 3/4,
ALONE) → **flip** so the gaze opposes the subject. (6) verify: faces preserved · chest-up · iPhone look
· opposite gazes · one-home continuity · no backwards text · no foreground blob. Surface for approval.

**Personas:** ordinary, documentary-real (visible pores, uneven tone, no makeup/retouch/filter — NOT
glamour/fashion/celebrity). Give each an explicit anthropometry block or gpt-image-2 mode-collapses to
one face. `insider_grok_gen.py` is a second worked pair (former-nurse subject gaze frame-RIGHT +
documentarian gaze frame-LEFT).

---

## 2. Clips — GROK IMAGINE for talkers AND silent listeners (locked)

Use **Grok Imagine on KIE** (`grok-imagine/image-to-video`) for BOTH the talking clips and the
silent-listener clips. It gives **clean audio** (no Veo phantom "mm-hmm" reaction murmurs) and — the
big lesson — a **genuine closed-mouth listener** (mouth CLOSED + natural blinks + small head moves +
attentive micro-expressions, identity preserved). **Do not use Veo tiers for this format.**

Grok reads **`input.image_urls`**; duration is a **string** (generate ~10s for listeners so they trim
to any beat with no looping); ~15s is the safe cap.
```python
payload = {"model":"grok-imagine/image-to-video","input":{
    "image_urls":[anchor_url], "prompt":prompt, "mode":"normal",
    "duration":"10", "resolution":"720p", "aspect_ratio":"9:16"}}
# POST kie.JOBS_CREATE -> data.taskId -> kie._poll_jobs(tid,"GrokImagine") -> download urls[0]
```
- **Talking prompt shape:** *"The woman sits in the armchair, speaking to [the interviewer off to her
  RIGHT / someone off to her LEFT], looking toward them, not at the camera. [tone]. She says:
  \"<verbatim line>\" Only her voice and faint room ambience — no other voices, no murmurs, no
  background chatter."* Gaze: **subject frame-RIGHT, interviewer frame-LEFT** (facing each other);
  **CTA looks DIRECTLY INTO the lens.**
- **Silent-listener prompt:** *"sits calmly, listening quietly to someone off to her [left/right],
  gentle nods, natural blinks, warm attentive expression, lips closed, calm and still."*
- Anchor each person's clips from their locked anchor (`kie.upload_file()` → hosted URL first);
  durations matched to word count.
- **Why NOT Veo (all tried, all failed):** Veo is a talking-head model and animates the mouth no
  matter what; free google-flow Veo Lite ALWAYS talks (+ "silent" prompts trip
  `AUDIO_GENERATION_FILTERED`); omni-flash blocks the sensitive listening prompt (`PROHIBITED_INPUT`);
  Poyo holds a *calm* face closed but an *expressive* face still talks. Grok avoids all of this.
- **QA every clip:** dissect the listener at **5fps** (mouth must stay closed); Scribe-transcribe the
  talkers to catch improv/mispronunciation before assembling; canonicalize transcript vs script.

---

## 3. Assembly — stacked layout + the AUDIO rule

- **Subject ALWAYS top pane, interviewer ALWAYS bottom.** Tight centered close-ups that FILL each
  face. Depo values (tune per anchor): `SURV_CROP="crop=520:462:80:260,scale=720:640,setsar=1,fps=30"`,
  `DOC_CROP="crop=560:498:90:190,scale=720:640,setsar=1,fps=30"` → vstack to 720×1280.
- Per beat: the **talker's audio**; the non-speaker's pane runs a **listener clip**. Cut both panes
  on the same beat boundary.
- **Word-aware trim:** Scribe word timings → cut to the intended first/last word (removes Grok
  leading/trailing improv). Canonicalize both sides before matching (digits vs number-words,
  got-to/gotta) to avoid false rejects.
- **★ THE STEREO RULE (hard bug):** force **every** segment to stereo 48k —
  `aformat=channel_layouts=stereo:sample_rates=48000`, and `-ar 48000 -ac 2` on the final concat. A
  single MONO segment (e.g. a mono ambient bed) breaks the concat demuxer and **SILENCES everything
  after it** (measured −72 dB tail). Verify audio continuity across the whole timeline after building.
- **Loudness:** measure integrated loudness, apply ONE static `volume` gain + `alimiter` (NOT dynamic
  loudnorm — it pumps on short UGC speech).
- **Veo watermark on a full-frame CTA:** `delogo=x=646:y=1222:w=72:h=48` (bottom-right).
- Ship **stacked** (both panes) + **cut** (shot-reverse full-frame) from the same trims.
- **Hybrid fallback** (`depo_stacked_hybrid.py`) if a genuine silent-listener pane is ever
  unattainable: split the two-shot only when the *interviewer* asks (subject silently listens — which
  Grok does well), go **full-frame** for the subject's answers and the CTA.

---

## 4. B-roll OVER the voice (placement + content)

B-roll rides a chosen beat: show ~2s of the speaker's face, then cut to the b-roll montage **while
that beat's line keeps playing UNDERNEATH**, then the next beat returns to faces. Keep the emotional
beats, the short questions, and the CTA on faces — don't make every beat b-roll.

- Build per beat: intro (2s stacked/full, `-an`) + b-roll tail (silent, each clip scaled to 720×1280)
  → concat to ONE silent video → mux the beat's **full audio** over it (fade video out at the end).
  Keeps the speaker's voice continuous under the b-roll. **Never insert a separate silent bridge** —
  a void reads wrong (and a mono bed silences the rest, see §3).
- **Match b-roll to the line** (studies → journal/stat; "the shot" → vial/injection; "lawsuit" →
  filing; recovery → post-op). **Text/document b-roll → deterministic ffmpeg `zoompan` push-in**
  (keeps text crisp), NOT Grok. **Human/scene b-roll → Grok i2v.**
- **Use the EXISTING AdMachin B-Roll library FIRST** (`list_broll_clips`, filter subproject) before
  generating — the user curates a rich library (post-op recovery, real drug branding, scans, legal).
- **REAL TEXT ONLY on credibility shots.** Verify facts (WebSearch), render exact wording at 2K
  ("render ONLY this text, spelled correctly, fully in frame, no extra words"); re-roll garbled.
- **NEVER fabricate a government-branded record** (no fake FDA seal / "Drug Safety Communication") —
  use a plain MANUFACTURER label/insert warning (factually defensible). **No empty/blank screens** (an
  empty phone form reads fake — use a PAPER form with real handwriting, or skip the beat).
- **Avoid broad-traffic symptom hooks** (headache/blurred vision/dizziness) — use QUALIFYING visuals
  (long-term use of the drug, the specific diagnosis/surgery/recovery, the claim process).
- **Survivor's own face into a scene** (e.g. recovery bed) = gpt-image-2 i2i — `kie.upload_file()` the
  face to a hosted URL FIRST, keep the prompt MINIMAL.

---

## 5. Save b-roll to the AdMachin B-ROLL library (NOT creatives)

The B-Roll page is a **separate endpoint** from Creatives — uploading b-roll to `/creatives` puts it
on the wrong page.
```python
from admachin_client import upload_broll_clip   # POST /brolls/clips/upload
upload_broll_clip(path, title="...", project_id=TORT, subproject_id=DEPO,
                  platform="ai_video", clip_category="...", tags=[...], note="...")
```
- Route is **`/brolls/clips`** — a bare `/brolls` returns a misleading `401` (looks missing but isn't).
- **`video_generation_model` 500s** on arbitrary values — omit it.
- **DELETE needs `?confirm=true`**; `list_broll_clips` returns soft-deleted rows (filter `status:deleted`).
- Creatives have **no DELETE** (`status:"deleted"/"archived"` fail) — a mis-filed creative can only be
  **moved to a null project** (`PATCH project_id=null`).
- Give every clip a descriptive title + tags + `clip_category` so it's findable.

---

## 6. Surfacing (cloud) & deliverables

- **Cloud/web session:** surface every asset with **`SendUserFile` (`display:"render"`)** so it opens
  in the preview panel — backticked repo paths and hosted URLs do NOT open the in-session preview in
  cloud. Web-compress for sharing (`crf 26–28`, `scale 540:960`); keep full-res masters.

## DO NOT (this session's mistakes)
- Upload b-roll to `/creatives` — use `/brolls/clips` (`upload_broll_clip`).
- Let a MONO segment into the concat — it silences the rest; force stereo 48k everywhere.
- Insert a separate silent b-roll bridge — put b-roll OVER the voice instead.
- Fabricate FDA/government-branded documents — use a plain manufacturer label.
- Use empty/blank-text screens (empty phone form) — paper form with real writing, or skip.
- Use broad symptom hooks — use qualifying visuals.
- Pass a local file path to `generate_gpt_image` i2i — `kie.upload_file()` to a URL first.
- Describe the person in an i2i anchor prompt — describe only action/framing/gaze/setting.
- Generate new b-roll before checking the existing library.
- Use Veo tiers for talking/listening in this format — Grok gives clean audio + real silent listeners.
- Open the ad on the product/drug shot.
