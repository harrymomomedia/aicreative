---
name: interview-scene
description: Build a two-person documentary/podcast INTERVIEW-STYLE UGC video — a subject (e.g. survivor/patient) + an interviewer (documentarian), shot as reverse-angle chest-up talking heads that read as the same room, stacked top/bottom (or intercut). Covers the whole anchor-image pipeline (same-room set, exact-face compositing, iPhone-video look, chest-up framing, podcast 3/4 gaze, facing-each-other direction) plus the clip/stitch plan. Use when the user asks for an "interview video", "documentary interview ad", "two-person interview", "podcast-style interview", "interviewer + subject", "someone being interviewed", or "reporter/documentarian asking questions" — for tort/legal UGC or any two-speaker talking-head ad.
---

# Interview-Scene (two-person documentary/podcast talking-head)

The format: a **subject** (survivor / patient / claimant) answers an off-camera-ish
**interviewer** (a *documentarian*, NOT a news reporter). Delivered as two **reverse-angle
chest-up talking heads** that read as the **same room**, either **stacked top/bottom** (both
panes visible, cut on the same beats) or intercut shot-reverse-shot. One person speaks per clip;
the other listens/reacts.

> This skill exists because getting the two anchor images right took MANY correction rounds
> (Depo-Provera interview, 2026-07-11). Every rule below was a specific piece of user feedback.
> Follow them up front instead of re-deriving.

---

## THE 10 LOCKED RULES (each was a correction the user made)

### 1. Same room, but OPPOSITE-wall backdrops (shot-reverse-shot) — NOT the same chair
Real two-camera interview coverage: the chairs **face each other**, so each camera sees a
**different wall**. Do NOT put both people in the identical backdrop/chair — that reads as one
person cloned. Build ONE room, give the subject one wall (e.g. family-photo wall) and the
interviewer the **opposite** wall (e.g. bookshelf/window). Keep the SAME warm palette, wall
color, wood tones and light so both still read as one home.

### 2. Exact faces — real i2i, and the `input_urls` gotcha
KIE `gpt-image-2-image-to-image` reads **`input_urls`, NOT `image_urls`** (an `image_urls` field
is silently ignored → the job runs as pure text-to-image and returns a totally different person).
`kie_client.generate_gpt_image` already sends `input_urls` for i2i — but if faces ever drift
wildly, check this FIRST. nano-banana-2 accepts both.

### 3. On i2i, NEVER describe the person
Text like "short gray hair, wire glasses, chambray shirt" COMPETES with the face reference and
pulls the output toward the words → likeness drift. Keep i2i prompts **minimal**: only the
**action / framing / gaze / setting**. The face image drives the likeness. (Same as the i2v
short-prompt rule.)

### 4. iPhone-VIDEO look, not polished photo
Append: *"candid vertical iPhone video frame, deep focus with the background in focus, flat even
indoor exposure, realistic smartphone color, slight sensor grain, no bokeh, no cinematic grade."*
Kills the DSLR/glamour look (shallow bokeh + warm grade reads as a staged photo, not a real
phone interview).

### 5. CHEST-UP close-up (waist-up is too wide)
Interview coverage is a tight close-up. Prompt: *"tight CHEST-UP close-up, head and chest fill
the frame, no arms, hands or lap visible."*

### 6. Podcast/documentary 3/4 gaze — NOT dead-lens, NOT profile
- Dead-into-the-lens = too "webcam". Full side-profile = too much.
- Want a gentle **three-quarter** angle: body turned a little, eyeline lands **just ahead of
  them** (at the person beside the camera). "Mostly forward but a little off to the side."

### 7. They must FACE EACH OTHER — opposite gaze directions
Subject looks **screen-RIGHT**, interviewer looks **screen-LEFT** (or vice versa) so they read as
talking to each other across the cut. Same direction on both = broken.

### 8. Gaze direction is set by the SOURCE face + a FLIP, not by the prompt
i2i **carries the source face's gaze** and largely ignores "look left/right" in the prompt (it
keeps re-posing toward the source's original direction / toward center). The reliable method:
1. Generate the person looking the direction the model gives you easily (usually toward one side).
2. **Horizontal-flip the whole composite** (PIL `FLIP_LEFT_RIGHT`) to get the opposite gaze.
- **BUT a flip mirrors backdrop text into backwards letters (a dead giveaway).** So build that
  person's backdrop **text-free** (blurred book spines, "absolutely NO readable text or letters")
  BEFORE compositing, so the flip has nothing to reveal. Flipping only the *source face* first
  does NOT reliably flip the gaze (the model re-poses to center) — flip the **final composite**.

### 9. No unwanted over-the-shoulder foreground figure
The model likes to add a blurry foreground shoulder/head of "the other person." If unwanted, add:
*"She is ALONE in the frame — NO other person, and NO out-of-focus foreground shoulder, head or
figure anywhere; only her and the room behind her."*

### 10. Keep the subject's ORIGINAL clothing/look — don't let i2i restyle
i2i will "upgrade" a real casual gray tee into a clean styled top and beautify the face if you let
it. Keep them ordinary/real ("not styled, not a professional set"). For the survivor especially,
preserve the exact original wardrobe + lav mic.

---

## Pipeline (order of operations)

Resolution: **2K default** (user pref; 4K for the establishing empty room is fine). Aspect 9:16.

1. **Pick the two faces** — generate persona candidates (gpt-image-2 t2i, documentary-real,
   `admachin-video-ads` / persona rules) → user picks a subject + an interviewer. Interviewer =
   documentarian look (casual knit/chambray, warm, NOT a news blazer, no mic flag).
2. **Build the subject's room** (t2i, iPhone look, one cream armchair + that wall's features).
3. **Composite the subject** into it (i2i `input_urls`, minimal prompt, chest-up, 3/4, gaze toward
   one side — keep original wardrobe).
4. **Build the interviewer's reverse-angle room, TEXT-FREE** (t2i: opposite wall, blurred book
   spines, no letters, same palette/light).
5. **Composite the interviewer** into it (i2i, minimal, chest-up, 3/4, ALONE, looking toward the
   model-preferred side) → **flip** the result so the gaze opposes the subject.
6. **VERIFICATION PASS — mandatory GATE before any video (user-locked 2026-07).** Do NOT generate a
   single interview clip until BOTH anchors pass. Run
   `scripts/interview_anchor_verify.py <subject> <interviewer>` (stacks them with center-line +
   eyeline guides) and confirm every item:
   - **Gaze/facing:** subject looks screen-RIGHT, interviewer screen-LEFT — opposite, a real 3/4
     turn, NOT frontal, NOT into-lens (except CTA). Both frontal = the "weird angle" that breaks
     the two-camera illusion (caught on the Figured-It-Out build).
   - **Looking-room:** each face sits on the OPPOSITE side of its gaze (subject left-of-center with
     room on the right; interviewer right-of-center with room on the left). Centered/edge-jammed =
     reads as looking at the camera, not each other.
   - **Eyeline height** matches · **framing scale** (head size) matches · both eye-level · level horizon.
   - **180° axis:** gazes converge (camera stays one side of the line between them).
   - **Background:** same palette/decor, DIFFERENT walls of the SAME room (not identical, not two rooms).
   - **Lighting:** consistent color temp / softness / exposure; coherent light direction.
   - Also: faces preserved · chest-up · iPhone look · no backwards text · no foreground blob.
   **i2i defaults to FRONTAL**, so the first composite is usually too straight-on — re-composite with
   an explicit strong 3/4 turn + off-center placement, use the flip trick for the opposite side (over
   a text-free backdrop), and re-run the pass until it's clean. Then surface via `SendUserFile`
   (render) for approval. Every clip inherits the anchor's angle, so fixing it here is free and
   fixing it later means re-generating the whole clip set.

7. **CLOSE-UP FACE FRAMING — never cut the chin (user-locked 2026-07).** The panes are wide-ish
   (~720x640), so a tight/low anchor + a blind fixed crop clips the chin. (a) Compose the anchor as a
   **MEDIUM close-up** — head AND shoulders, HEADROOM above the hair, space BELOW the chin (face
   ~40–50% of frame height, upper-middle), NOT a tight face-filling crop (ask for medium-CU AND the
   3/4 turn together). (b) Crop each pane **FACE-AWARE**, never blind: `scripts/face_crop.py`
   `pane_crop(clip)` detects the face and keeps the whole face with **chin inside + ≥6% margin**,
   eyeline in the **upper third**, and a **matched face-fill** across both panes. Verify on a rendered
   stacked frame (no chin within ~6% of a pane edge; heads same size). Needs `opencv-python-headless<5`.

Reusable scripts (Depo build): `scripts/depo_interview_set_iphone.py` (room+composite iPhone),
`scripts/depo_interview_facing.py` (opposite 3/4 gazes), `scripts/depo_doc_notext.py` (text-free
backdrop → composite → flip), `scripts/depo_doc_alone.py` (no foreground → flip). Approved Depo
anchors: `outputs/depo_interview/reference/surv_face_v1.png` + `doc_alone_v1_L.png`.

---

## From anchors → video (the clip + stitch plan)

- **One speaker per clip.** Two voices in one Veo clip collapse to the same pitch (CLAUDE.md Veo
  gotcha). So generate each person's **talking** clips AND **listening/reacting** clips separately
  from their anchor.
- **SILENT listening clips — use GROK IMAGINE (KIE). This is the solved answer (2026-07-11).**
  QA every listen clip by dissecting at **5fps** (`fps=5 … tile`), user-locked.
  - **Grok Imagine i2v (`grok-imagine/image-to-video` on KIE) reliably renders a genuine silent
    listener** — mouth CLOSED the whole clip, with natural blinks + small head movements + attentive
    micro-expressions, identity preserved. It succeeded where every Veo tier failed, on the SAME
    expressive documentarian face. This is THE method for the listener pane. Schema: `input.image_urls`
    (not input_urls here), `prompt`, `mode:"normal"`, `duration` STRING 6–30, `resolution:"720p"`,
    `aspect_ratio:"9:16"`. Generate ~10s so you can trim to any beat with NO looping. Reference:
    `scripts/depo_grok_listen.py`. Prompt: "sits calmly, listening quietly to someone off to her
    left/right, gentle nods, natural blinks, warm expression, lips closed, calm and still."
  - **Why NOT the others (all tried and failed):** Veo is a talking-head model and animates the
    mouth no matter what. Free **google-flow Veo Lite ALWAYS talks** (+ "no audio/silent" prompts
    trip `AUDIO_GENERATION_FILTERED`). **omni-flash** (google-flow R2V) blocks sensitive listening
    prompts with `PROHIBITED_INPUT` (drop "painful story" + the "does NOT…" negation stack and it
    runs, but it's still a talking model). **Poyo Veo 3.1 Fast** holds a *calm* face closed but an
    *expressive* face still talks/smiles every take. A ping-pong loop of a closed-mouth window reads
    robotic; a freeze is rejected. Grok avoids all of this.
  - Fallback if Grok is down: the **CUT (shot-reverse) layout** uses only talking clips, or the
    **hybrid** (split on questions, full-frame on answers) — see `scripts/depo_stacked_hybrid.py`.
- **Stacked top/bottom:** always show both panes; when A talks, B's pane runs a listening clip.
  **Cut both panes on the SAME beat boundaries** so they jump together (clips are ~8s; pick jump
  points on natural speech breaks so the reaction lands at the right moment).
- **Alternate:** generate one horizontal two-shot and reframe vertically — but separate panes give
  cleaner distinct voices and easier reaction timing (preferred).
- Anchor each person's clips from their locked anchor (clip-1-anchor rule), eyes-open frames,
  per-clip Scribe QA gate, voice consistency — all standard CLAUDE.md rules apply.
- **Script shape:** interviewer asks short questions, subject carries the answers. A separate
  full-frame **CTA** clip (breaking the two-shot) delivered by the interviewer or the subject,
  direct-to-lens, works well.

## Compliance (tort/legal interviews)
Carry the campaign's locked rules: recovery phrase verbatim ("may qualify for significant
compensation" etc.), explicit qualifying-harm beat, no guaranteed outcome, no disclaimer lingo on
the creative unless asked, generic interviewer (never impersonate a named attorney). See
`admachin-video-ads` + `ad-format-ideation`. Present all final copy verbatim for approval before
producing.
