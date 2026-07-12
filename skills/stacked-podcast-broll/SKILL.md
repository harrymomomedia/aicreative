---
name: stacked-podcast-broll
description: Produce a two-person STACKED documentary/podcast interview UGC ad (subject on top, interviewer on bottom, both panes visible) with b-roll cut over the voice — end to end, from concept to the final stacked + cut deliverables and the AdMachin B-Roll library. Covers the LOCKED pipeline learned on the Depo-Provera meningioma build (2026-07): Grok for clean talking + genuine silent listeners, the stereo-audio concat rule, b-roll-over-VO placement, real-text credibility b-roll, and uploading b-roll to the RIGHT endpoint (/brolls/clips, not /creatives). Use when the user asks for a "stacked interview", "stacked podcast", "two-person interview ad with b-roll", "documentary/podcast testimonial ad", "interview ad stacked top and bottom", or wants more videos in this format.
---

# Stacked Podcast / Interview + B-Roll (full pipeline)

A two-person documentary interview delivered as **both panes stacked vertically** — the **subject
(survivor/patient) on TOP**, the **interviewer (a documentarian, NOT a reporter) on BOTTOM** — cut
on the same beats, with **b-roll cut in over the speaker's voice** on the answer/question beats.
Also ship a **CUT** (shot-reverse full-frame) version from the same clips.

> Every rule below was a specific fix on the Depo-Provera meningioma build. Follow them up front.
> For the ANCHOR-IMAGE stage (same-room/opposite-wall set, exact-face i2i, iPhone look, chest-up,
> 3/4 gaze, facing each other via flip + text-free backdrop) use the **`interview-scene`** skill —
> this skill assumes the two locked anchors already exist and covers concept → video → b-roll →
> assembly → library.

Reusable reference scripts (Depo build): `scripts/depo_grok_talk.py` + `depo_grok_talk_rest.py`
(talking clips), `scripts/depo_grok_listen.py` (silent listeners), `scripts/depo_grok_full_assemble.py`
(stacked + cut + b-roll-over-VO), `scripts/depo_broll_future_stills.py` +
`depo_broll_future_animate_upload.py` (b-roll gen + upload), `admachin_client.upload_broll_clip`.

---

## 0. Concept stage (get sign-off BEFORE producing)

- **Format:** subject + documentarian, ~11 beats, ~75s. Interviewer asks short questions; subject
  carries the answers. A separate full-frame **CTA** (direct-to-lens) breaks the two-shot at the end.
- **Hook variety:** each new script must be a *foundationally different angle*, not a synonym swap
  (the number / insider / convenience / misdiagnosis / two-survivors / family / self-discovery /
  duration / too-young / not-too-late). NEVER open on the product/drug shot — it draws the wrong
  audience. Lead the hook with the qualifying condition.
- **Compliance (tort/legal): present every headline + line VERBATIM for approval before producing.**
  Carry the campaign's locked recovery phrase (e.g. "may qualify for significant compensation");
  qualifying condition named FIRST, the drug revealed mid-script; no guaranteed outcome; generic
  interviewer (never impersonate a named attorney); no disclaimer lingo on the creative unless asked.
- **Match dialogue length to clip duration** (~2.4 words/sec): a short line in a long clip makes the
  model improvise. ≤10 words → 4s; ~15-19 words → 8s.

## 1. Video generation — GROK IMAGINE for everything (locked)

Use **Grok Imagine on KIE** (`grok-imagine/image-to-video`) for BOTH the talking clips AND the
silent-listener clips. It gives **clean audio** (no Veo phantom "mm-hmm / oh-ya" reaction murmurs)
and a **genuine closed-mouth listener** (every Veo tier animates the mouth). This is the single
biggest lesson — do not use Veo tiers for this format.

Payload (note: Grok reads **`input.image_urls`**, not `input_urls`):
```python
payload = {"model":"grok-imagine/image-to-video","input":{
    "image_urls":[anchor_url], "prompt": prompt, "mode":"normal",
    "duration":"8", "resolution":"720p", "aspect_ratio":"9:16"}}
# POST kie.JOBS_CREATE -> taskId -> kie._poll_jobs(tid,...) -> download
```

- **Talking prompt shape:** "The woman sits in the armchair, speaking to [the interviewer off to her
  right / someone off to her left], looking toward them, not at the camera. [tone]. She says:
  \"<verbatim line>\" Only her voice and faint room ambience — no other voices, no murmurs, no
  background chatter." Gaze: **subject looks screen-RIGHT, interviewer looks screen-LEFT** (they face
  each other). **CTA looks DIRECTLY INTO the lens.**
- **Silent-listener prompt:** "sits calmly, listening quietly to someone off to her [left/right],
  gentle nods, natural blinks, warm attentive expression, lips closed, calm and still." Generate
  **~10s** so it trims to any beat with no looping.
- Anchor each person's clips from their locked anchor (`interview-scene`). Upload the anchor via
  `kie.upload_file()` to get a hosted URL first.
- **QA every clip:** dissect the listener at **5fps** (mouth must stay closed); Scribe-transcribe the
  talkers to catch improv/mispronunciation before assembling.

## 2. Assembly — stacked layout + the AUDIO rule

- **Subject ALWAYS top pane, interviewer ALWAYS bottom.** Tight centered close-ups that FILL each
  face. Depo values (tune per anchor): `SURV_CROP="crop=520:462:80:260,scale=720:640,setsar=1,fps=30"`,
  `DOC_CROP="crop=560:498:90:190,scale=720:640,setsar=1,fps=30"` → vstack to 720x1280.
- Per beat: the **talker's audio**; the non-speaker's pane runs a **listener clip**. Cut both panes
  on the same beat boundary.
- **Word-aware trim:** Scribe word timings → cut to the intended first/last word (removes Grok
  leading/trailing improv). Canonicalize both sides before matching (digits vs number-words,
  got-to/gotta) to avoid false rejects.
- **★ THE STEREO RULE (hard bug):** force **every** segment to stereo 48k —
  `aformat=channel_layouts=stereo:sample_rates=48000`, and `-ar 48000 -ac 2` on the final concat. A
  single MONO segment (e.g. a mono ambient bed) breaks the concat demuxer and **SILENCES everything
  after it** (measured -72 dB tail). Verify audio continuity across the whole timeline after building.
- **Loudness:** measure integrated loudness, apply ONE static `volume` gain + `alimiter` (NOT dynamic
  loudnorm — it pumps on short UGC speech).
- Ship **stacked** (both panes) + **cut** (shot-reverse full-frame) from the same trims.

## 3. B-roll OVER the voice (the placement pattern)

B-roll rides a chosen beat: **show ~2s of the speaker's face, then cut to the b-roll montage while
that beat's line keeps playing UNDERNEATH**, then the next beat returns to faces. Keep the emotional
beats, the short questions, and the CTA on faces — don't make every beat b-roll.

Build per b-roll beat: intro (2s stacked/full, `-an`) + b-roll tail (silent, each clip scaled to
720x1280) → concat to ONE silent video → then mux the beat's **full audio** over it (fade video out
at the end). This keeps the speaker's voice continuous under the b-roll. Never insert a separate
silent bridge — a void with no voice reads wrong (and the mono bed silences the rest, see §2).

- **Match b-roll to the line** being spoken (studies → journal/stat; "the shot" → vial/injection;
  "lawsuit" → filing; recovery → post-op).
- **TEXT/document b-roll → deterministic ffmpeg slow push-in** (`zoompan`), NOT Grok — keeps the text
  crisp. **Human/scene b-roll → Grok i2v.**

## 4. B-roll content rules (learned the hard way)

- **Use the EXISTING AdMachin B-Roll library FIRST** (`list_broll_clips`, filter subproject) before
  generating anything. The user curates a rich library (post-op recovery set, real drug branding,
  scans, legal). Regenerating what already exists wastes time and looks off-brand.
- **REAL TEXT ONLY on credibility shots.** Verify facts (WebSearch) and render the exact wording;
  gpt-image-2 at 2K renders short verbatim text cleanly if you specify it exactly + "render ONLY this
  text, spelled correctly, fully in frame, no extra words." Verify each; re-roll garbled.
- **NEVER fabricate a government-branded record** (no FDA seal / "Drug Safety Communication" that
  didn't happen). Use a plain MANUFACTURER label/insert warning instead — factually defensible.
- **No empty/blank screens** — an empty phone form read as fake. Use a PAPER form with real
  handwriting (real field labels + a real diagnosis), or skip the beat.
- **Avoid broad-traffic symptom hooks** (headache / blurred vision / dizziness) — they pull
  unqualified leads. Use QUALIFYING visuals: long-term use of the drug, the specific diagnosis /
  surgery / recovery, the claim process.
- **Survivor's own face into a scene (e.g. recovery bed) = gpt-image-2 i2i** — but **upload the face
  to a hosted URL FIRST** (`kie.upload_file`); `generate_gpt_image` does NOT auto-upload, so a local
  path → KIE `image fetch failed / state:fail`. i2i reads `input_urls` (already in `kie_client`);
  keep the prompt MINIMAL (don't describe the person).

## 5. Save b-roll to the AdMachin B-ROLL library (NOT creatives!)

The B-Roll page (`admachin.com/b-roll`) is a **separate endpoint** from Creatives. Uploading b-roll
to `/creatives` puts it on the wrong page.

```python
from admachin_client import upload_broll_clip   # POST /brolls/clips/upload
upload_broll_clip(path, title="...", project_id=TORT, subproject_id=DEPO,
                  platform="ai_video", clip_category="...", tags=[...], note="...")
```
Endpoint gotchas (baked into the client):
- Route is **`/brolls/clips`** — a bare `/brolls` returns `401 Authentication required` (looks
  missing but isn't). Report to admachin: unknown routes should 404, not 401.
- **`video_generation_model` 500s** server-side on arbitrary values — omit it (the prompt/`gen_prompt`
  is fine).
- **DELETE needs `?confirm=true`**; `list_broll_clips` returns soft-deleted rows (`status:deleted`) —
  filter them out.
- Creatives have **no DELETE** and `status:"deleted"`/`"archived"` fail — a mis-filed creative can
  only be **moved to a null project** (`PATCH project_id=null`).
- Give every clip a descriptive **title** + tags + `clip_category` so it's findable in the library.

## 6. Surfacing (cloud) & deliverables

- **Cloud/web session:** surface every asset with **`SendUserFile` (`display:"render"`)** so it opens
  in the preview panel. Backticked repo paths and hosted URLs do NOT open the in-session preview in
  cloud — send the file. (Backticked paths only preview on the local desktop CLI.)
- Web-compress for sharing (`crf 28`, `scale 540:960`). Keep the full-res masters.

## DO NOT (this session's mistakes — do not repeat)
- Upload b-roll to `/creatives` — use `/brolls/clips` (`upload_broll_clip`).
- Let a MONO segment into the concat — it silences the rest; force stereo 48k everywhere.
- Insert a separate silent b-roll bridge — put b-roll OVER the voice instead.
- Fabricate FDA/government-branded documents — use a plain manufacturer label.
- Use empty/blank-text screens (empty phone form) — paper form with real writing, or skip.
- Use broad symptom hooks — use qualifying visuals.
- Pass a local file path to `generate_gpt_image` i2i — `kie.upload_file()` to a URL first.
- Generate new b-roll before checking the existing library.
- Use Veo tiers for talking/listening in this format — Grok gives clean audio + real silent listeners.
- Open the ad on the product/drug shot.
