---
name: street-interview
description: Produce a STREET-INTERVIEW / VOX-POP UGC ad — a reporter with a handheld mic stops people on a sidewalk and one turns out to be affected (a survivor / claimant), delivering the hook and CTA through a candid back-and-forth. Covers the whole pipeline learned on the Chowchilla / CCWF women's-prison vox-pop build (2026-07): street-casual personas, the two-shot composite anchor (interviewer + respondent) via identity-preserving i2i, Grok-vs-Veo speaker routing, the wide-16:9 → punch-in-to-9:16 reframe, word-timing trim + assemble, and the Chowchilla pronunciation lock. Use when the user asks for a "street interview", "vox pop", "man on the street", "sidewalk interview", "reporter with a mic asking people", "person on the street interview ad", or wants more videos in this format. For the INDOOR seated two-person documentary/podcast format (reverse-angle chest-up talking heads stacked top/bottom) use `interview-scene` + `stacked-podcast-broll` instead.
---

# Street Interview / Vox-Pop (man-on-the-street UGC ad)

The format: a **reporter/interviewer** with a black foam-windscreen **handheld mic** stops a
passerby on a **sunny sidewalk**; the passerby turns out to be **affected** (a survivor / former
inmate / claimant) and the two have a candid **back-and-forth** that carries the hook, the
qualifier, and the CTA. Shot **WIDE 16:9, locked static camera**, then **punched-in to a vertical
9:16** window on whoever is speaking. Reads as real local-news / social vox-pop, NOT a polished ad.

Two shapes of the same format:
- **Vox-pop (many voices):** the SAME interviewer + a **different respondent per clip** (each their
  own persona). Feels like the reporter walked the block asking everyone. One two-shot anchor per
  respondent.
- **Conversational street interview (one pair):** one reporter + one survivor, a **multi-clip
  back-and-forth** (Q → A → follow-up → CTA). One two-shot anchor reused across all clips.

> **Read the general `interview` skill first** — it carries the cross-cutting patterns (speaker
> matching, one-speaker-per-clip, model routing, gaze, dialogue locks, QA gates, assembly
> primitives). This skill covers only what's specific to the STREET pipeline.
>
> Every rule below was a specific fix on the Chowchilla/CCWF women's-prison vox-pop build
> (`claude/womens-prison-video-xvzdh8`, 2026-07). Follow them up front instead of re-deriving.
> Reference scripts (that branch): `scripts/wp_voxpop_personas.py`, `wp_voxpop_twoshot.py` +
> `wp_voxpop_twoshot_bc.py`, `wp_voxpop_grok_produce.py` / `wp_voxpop_interview_produce.py`,
> `wp_voxpop_grok_test.py` / `wp_voxpop_veo_test.py` / `wp_voxpop_convo_test.py`,
> `wp_voxpop_assemble.py`, `wp_voxpop_reframe.py`. `generate_grok` lives in that branch's
> `kie_client.py`; if it's not present, call KIE jobs directly (payload in §3).

---

## 0. Concept + copy (sign-off BEFORE producing)

- **Structure:** reporter's question carries the HOOK (audience + harm + the recovery phrase in the
  first line), respondent reacts with lived credibility ("my cousin was in there…"), a middle beat
  kills the main objection (too late / never reported / must go to court), a final clip is the CTA
  (name the real facilities + the private form). ~3 clips, ~12–15s each.
- **Lead the hook with the qualifying condition/audience, never the product.** "Women abused at
  Chowchilla…" not a drug/brand shot.
- **Compliance (tort/legal): present every line VERBATIM in chat for approval before producing.**
  Carry the campaign's locked recovery phrase — for CCWF/Chowchilla: **"may qualify for significant
  potential compensation"** (never "compensation" alone / "damages" / "settlement" / "owed" /
  "payout"); "free", "confidential", "no court", "private two-minute form"; name REAL facilities
  (Chowchilla, Valley State, Folsom); a qualifying-harm beat; no guaranteed outcome; generic
  reporter (never impersonate a named attorney); no disclaimer lingo on the creative unless asked.
- **Match dialogue length to clip duration (~2.4 words/sec)** so the model doesn't improvise —
  a short line in a long clip invites invented (potentially defamatory) filler.

## 1. Personas (gpt-image-2 t2i, 2K, 9:16)

One **interviewer** + N **respondents**, each a distinct face. Reference: `wp_voxpop_personas.py`.

- **Interviewer:** warmer / younger / brighter, holds the mic, a simple denim jacket. Reads as a
  friendly local reporter — NOT a news-blazer anchor.
- **Respondents:** ordinary, hard-lived, weathered — "someone who's done time." Tired, guarded
  eyes; no makeup / retouch / filter.
- **Defeat gpt-image-2 mode-collapse — give EVERY persona an explicit anthropometry block**
  (face shape, skin tone across the real range, nose/lips/brows, build, hair texture, distinguishing
  marks: scar, missing tooth, penciled brows, fine-line **forearm/hand** tattoo). Repeated
  demographic-only prompts return the same face in different outfits.
- **Shared realism + framing tail** on every persona:
  > "Photoreal candid documentary street photo (NOT glamour, NOT fashion, NOT a celebrity portrait)
  > — an ordinary hard-lived working-class woman… weathered sun-worn skin, visible pores, deep
  > lines, uneven tone, heavy under-eye shadows, no makeup, no beauty retouching, no filter, tired
  > guarded eyes. Bright natural daylight on a plain urban sidewalk with softly out-of-focus
  > storefronts behind (no readable signage). Waist-up vox-pop framing, a black foam-windscreen
  > handheld microphone held into frame from the side toward her. NO tattoos on the neck."
- **NO neck tattoos** — neck ink + abuse/prison dialogue compounds Veo/Grok moderation risk (keep
  ink on forearm/hand only).

## 2. The two-shot composite anchor (identity-preserving i2i) — the linchpin

Merge the interviewer + one respondent into ONE **wide 16:9** street-interview frame via
`generate_gpt_image` **image-to-image** (KIE `gpt-image-2-image-to-image`). This single anchor is
what makes both faces stay consistent across every clip. Reference: `wp_voxpop_twoshot.py`,
`wp_voxpop_twoshot_bc.py`.

- **`upload_file()` BOTH faces first** and pass the hosted URLs as `image_urls=[interviewer, respondent]`
  (the client sends them under the JSON key **`input_urls`** — the fixed key that actually preserves
  identity; if faces come back as strangers, that payload key is the first thing to check).
- **MINIMAL prompt — describe ONLY the scene/composition, NOT the people.** Re-describing appearance
  fights the reference faces and drifts identity. e.g.:
  > "Put these two exact people together in ONE candid documentary street-interview photo, wide 16:9
  > horizontal framing on a sunny sidewalk. FIRST person = the interviewer holding the microphone,
  > on the LEFT facing right. SECOND person = the woman being interviewed, on the RIGHT facing left,
  > microphone between them near center, both faces clearly visible. No on-screen text."
- **Framings to render (pick one):** `v2_profile` **balanced two-shot** (interviewer LEFT facing
  right, respondent RIGHT facing left, mic near center, both faces visible) is the **workhorse** —
  it punches-in cleanly to either speaker. Alternates: over-the-shoulder (`v1_ots`), foreground-
  shoulder-and-mic (`v3_foreground`).
- **Layout convention (keep it consistent — the reframe depends on it):** interviewer on the **LEFT**,
  respondent on the **RIGHT**.
- **Per respondent, build its own two-shot** reusing the same interviewer face
  (`v2_profile`, `v2_profile_B`, `v2_profile_C`) so the vox-pop reads as one reporter, many people.
- 16:9, 2K.

## 3. Video generation — route by beat: Grok for back-and-forth, Veo for single-speaker

Anchor every clip from its two-shot (`upload_file` the anchor → hosted URL). Wide **16:9, 720p,
locked static camera.**

**Grok Imagine (KIE `grok-imagine/image-to-video`) — PREFERRED for the conversational back-and-forth.**
It carries a **multi-turn exchange in ONE clip** (both people take turns), holds **both identities**
from the two-shot, gives **clean audio with distinct-ish voices** (no phantom Veo reaction murmurs),
and needs no punch-in at generation (do that in post). Duration is a **string**; **~15s is the safe
cap** (docs claim 30 but the playground caps ~15). Reference: `wp_voxpop_grok_produce.py` /
`wp_voxpop_interview_produce.py`.

```python
# generate_grok(prompt, image_urls=[anchor_url], duration="15", resolution="720p", aspect_ratio="16:9")
# If generate_grok isn't present, POST KIE jobs directly:
payload = {"model": "grok-imagine/image-to-video", "input": {
    "image_urls": [anchor_url], "prompt": prompt, "mode": "normal",
    "duration": "15", "resolution": "720p", "aspect_ratio": "16:9"}}
# POST kie.JOBS_CREATE -> data.taskId -> kie._poll_jobs(tid, "GrokImagine") -> download urls[0]
```

**Poyo Veo 3.1 Fast (frame mode, anchor passed twice) — for a SINGLE speaker per clip.** Two voices
in one Veo clip collapse to the same pitch (CLAUDE.md Veo gotcha), so on Veo do **one speaker per
clip**: the talker answers, the other person stays **SILENT, mouth CLOSED** the whole clip; cut
Q → A in the edit. Reference: `wp_voxpop_veo_test.py` / `wp_voxpop_veo_question.py`.

```python
# generate_veo(prompt, image_urls=[anchor_url, anchor_url], aspect_ratio="16:9",
#              resolution="720p", generation_type="frame")   # Poyo, $0.10/clip
```

**Prompt recipe (both providers) — the locked clauses:**
```
Wide 16:9 candid street interview, locked static camera. Natural BACK-AND-FORTH: the two women
TAKE TURNS, only one talks at a time while the other listens with mouth CLOSED. The interviewer on
the LEFT (denim jacket) is warm and friendly; the woman on the RIGHT (grey hoodie) is older,
weathered, honest. ~2.4 words/sec.
<PRONUNCIATION LOCK — see §4>
DIALOGUE LOCK: English only, no filler, no extra words, follow the exact lines and speaker order.
AUDIO: clean spoken dialogue only, natural street ambience, NO background music, NO song, NO score.
No on-screen text, no captions, no subtitles.
SPOKEN DIALOGUE (verbatim, in order):
INTERVIEWER: "..."
WOMAN: "..."
```
For a Veo single-speaker clip, add: *"CRITICAL — ONLY the right woman speaks. The woman on the LEFT
holding the microphone stays SILENT the entire clip, mouth CLOSED… makes NO sound."* plus the
standard `AUDIO CRITICAL: full conversational volume` clause.

**QA every clip before assembling:** Scribe-transcribe the talkers (catch improv, doubled words,
mispronunciation); confirm the silent listener's mouth stays closed. Standard per-clip dissect gate.

## 4. Chowchilla pronunciation lock (descriptive, not respelled)

For Grok/Veo, the reliable lock is **NORMAL spelling in the dialogue** + a **descriptive syllable
lock** in the prompt (beat the phonetic-respell approach here):
```
Pronunciation: 'Chowchilla' is the name of a California women's prison, pronounced as three English
syllables: chow (rhymes with 'cow') + chill + uh, stress on the MIDDLE syllable, said as one fluid
word, NOT spelled out, NEVER as a Spanish word.
```
(A `Chow-CHILL-uh` respell inside the dialogue line also works as a fallback; verify via Scribe.)
Always pass `biased_keywords=["Chowchilla"]` to Scribe when QA-ing/aligning.

## 5. Reframe wide → 9:16 punch-in + assemble

The 16:9 wide two-shot becomes a vertical 9:16 ad by **cropping to the ACTIVE speaker per turn**,
switching L↔R on each turn. Reference: `wp_voxpop_reframe.py` (final) + `wp_voxpop_assemble.py`
(simple concat variant).

- **Per-turn fixed crop → concat** (robust; do NOT use a dynamic-crop expression). From a 1280-wide
  frame: crop `405×720`, `X_L≈120` for the interviewer (LEFT), `X_R≈740` for the respondent (RIGHT).
  Tune per anchor.
- **Turn timings** come from **aligning the Scribe transcript to the known script turns** (you wrote
  the dialogue, so map each turn's word span to L or R).
- **Trim leading/trailing dead air with Scribe WORD-TIMINGS, not `silencedetect`.** Grok clips carry
  ambient street noise, so `silencedetect` misses the trailing pause — word-timings are reliable.
  Pads: `LEAD≈0.05s`, `TRAIL≈0.25s`.
- **Even loudness:** `loudnorm=I=-16:TP=-1.5:LRA=11` is fine for these short vox-pop concats; for a
  longer multi-clip master prefer the static-gain + limiter path (CLAUDE.md "loudnorm PUMPS").
- Ship the 9:16 final + a **web-compressed** copy (`crf 26–28`) for sharing; keep the full-res master.

## 6. Surfacing (cloud sessions)

Surface every asset (personas, two-shot anchors, generated clips, final) with **`SendUserFile`
(`display:"render"`)** so it opens in the preview panel — in a cloud/web session backticked repo
paths do NOT open the in-session preview. Present all final copy verbatim for approval before
producing.

## DO NOT (this format's mistakes)
- Open on the product/brand shot — lead the hook with the qualifying audience/harm.
- Describe the people in the two-shot i2i prompt — describe only scene/composition (identity drift).
- Pass a local file path to `generate_gpt_image` i2i — `upload_file()` to a hosted URL first.
- Put two speakers in ONE **Veo** clip — their voices collapse to one pitch. One speaker per Veo
  clip (other stays silent, mouth closed); use **Grok** for the true back-and-forth.
- Use a dynamic-crop expression for the punch-in — per-turn fixed crops → concat is what's robust.
- Trim Grok clips with `silencedetect` — street ambience defeats it; use Scribe word-timings.
- Let background music/score into the audio — lock "clean spoken dialogue + natural street ambience,
  NO music" in the prompt.
- Put neck tattoos on a persona carrying abuse/prison dialogue (moderation risk).
- Respell "Chowchilla" as a Spanish word — use the descriptive three-syllable lock (§4).
- Skip verbatim copy approval — a template/hook pick is not approval.
