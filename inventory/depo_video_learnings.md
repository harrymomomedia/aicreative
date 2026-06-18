# Depo-Provera brain-meningioma — VIDEO production learnings (session 2026-06-18)

Sibling of `inventory/depo_provera_ad_formats.md` (the IMAGE-ad format taxonomy). This file covers
the **video** track: two animated explainers (Claymation + Pixar), same diagnosis-first story.

## Angle (LOCKED) — diagnosis-first

Lead with the **brain-tumor / meningioma diagnosis** (the high-value, claim-ready lead); make
Depo-Provera the *link/cause* revealed second. Compliance phrase: **"significant compensation"**
(Depo drops "potential"), phrased **conversationally/easy**, not stiff-legal. NEVER put a disclaimer
(Attorney Advertising / Dramatization) in the copy, on the creative, or as an end-card unless the
user explicitly asks — see memory `feedback_no_disclaimer_lingo_in_copy`.

## Messenger / persona (user-locked)

- **Black woman ~45** — the target audience (Black women were disproportionately prescribed
  long-term Depo). Applies to the protagonist AND the crowd.
- Locked clay face = `outputs/depo_claymation/face/face_01_round_twistout.png`; locked Pixar face =
  `outputs/depo_pixar/face/face_02_oval_bun_glasses.png`.
- **Face consistency across clips** = Seedance reference-image trick (memory
  `project_seedance_face_consistency_ref`): one locked face PNG passed as `ref_images` on every
  protagonist shot; dropped on the crowd shot (diversity) and the younger-injection shot.

## Creative direction that earned sign-off

- **Real medical settings, not abstract** — radiology/MRI reading room, neurology exam room, clinic,
  pharmacy aisle, hospital waiting room, law office. (User asked for "real settings like hospital.")
- **SHOW the meningioma** — MRI brain scans with the tumor visible, a 3D brain model with the tumor
  highlighted, the radiologist pointing. (User: "more clips that show brain meningioma.")
- **Injection = a YOUNGER woman (her 20s, "years ago")**, not the present ~45 — the Depo→meningioma
  latency means the shots were taken long before diagnosis. (User catch — rerollّed s05 younger.)
- **Crowd = diverse Black women** (no face ref → no cloning).
- **Cold→warm tonal arc**: cold blue clinical (diagnosis/shot/no-warning) → warm gold (lawsuit /
  relief / CTA).

## VO (reused across BOTH styles — style-independent)

- `outputs/depo_claymation/vo/survivor_f49.mp3` — first-person Black woman, ElevenLabs voice
  **Black_F_49Y** (`LENRS9nvWdqPqUc8kYRq`), `eleven_v3` (expressive, `[sighs]` tag), ~41.3s.
- "meningioma" + "Depo-Provera" both pronounced clean (verified via Scribe biased keywords). Script
  in `scripts/depo_claymation_vo.py`. The Pixar cut reuses this exact VO — only the visuals change.

## Pipeline / scripts

- Faces: `scripts/depo_clay_face.py`, `scripts/depo_pixar_face.py` (gpt-image-2 2K 3:4, 4 candidates,
  user picks one).
- B-roll: `scripts/depo_claymation_broll.py`, `scripts/depo_pixar_broll.py` — Seedance-2-Fast 480p
  9:16 (KIE), `(slug, use_face, prompt)` shots, `generate_audio=False`, `--only` / `--dur`. 11 shots
  over 8 VO beats; ~6s each (assembler trims to beat).
- Assembly: `scripts/depo_claymation_assemble.py`, `scripts/depo_pixar_assemble.py` — trim each shot
  to its VO beat → concat → mux VO → raw (496x864). Captions are a separate step.
- Captions: `scripts/caption_nick.py ... --biased "Depo-Provera:3.0,meningioma:3.0"` (Nick style:
  white sentence-case on dark pill).

## Final deliverables

| | Clean master | Nick-captioned |
|---|---|---|
| Claymation | `outputs/depo_claymation/depo_explainer_v1_raw.mp4` | `..._v1_nick.mp4` |
| Pixar | `outputs/depo_pixar/depo_pixar_v1_raw.mp4` | `..._v1_nick.mp4` |

Both ~40.4s, VO synced.

## AdMachin staging (Tort `e15c60bd` → Depo Provera `9cfb5b76`)

- **Uploaded ONLY the captioned cuts** (rule `feedback_admachin_upload_captioned_only`): creative
  **#813** = claymation-nick, **#814** = pixar-nick. (Raws were not kept.)
- Copy: headline **#681** "Diagnosed With a Meningioma?" + primary **#682** (conversational,
  no disclaimer, "you could qualify for significant compensation").
- Draft ads: **#518** (claymation) + **#519** (pixar) — `is_launched: false`, no spend. NOT launched.

## Gotchas this session

- `upload_creative` can return a success record for a file that **doesn't persist** — verify via
  `list_creatives`, not the upload response.
- `compose_ad_with_copy` / `create_ad`: **`ad_type` has a DB check-constraint allowlist** — a
  free-form value (e.g. a campaign slug) errors `ads_ad_type_allowed`. Omit `ad_type` (defaults
  null) or use an allowed value.
- macOS has no `timeout` shim — `timeout 300 .venv/bin/python ...` aborts the run; drop it. (This is
  why the `depo_ads_gen.py` 20-format IMAGE batch never actually generated — only built.)
