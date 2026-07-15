# Depo Docu-Series + B-Roll Library — session learnings (2026-07-09)

Captured so a parallel/future session doesn't repeat the same steps. Broad rules already live in
CLAUDE.md (omni-flash silent b-roll @ "Silent b-roll i2v → omni-flash"; b-roll gen-field format @
"FB launch specifics"). This file is the campaign-specific detail + the workflows.

## 1. The Depo docu-series format (YouTube-documentary, validated)

User-picked format after rejecting news-anchor/authority framing: **calm YouTube-docu "receipts"**,
NOT a news clip. Locked shape, every episode = 4 beats:
1. Cold open on an artifact/fact (no ad-voice, no question-to-camera).
2. The receipts walked one at a time: the shot's ubiquity → the **2024 study** → the **label gap**
   (other countries warn of meningioma, US label didn't) → the **filings** piling up.
3. The turn: "if you have a **brain meningioma** and Depo in your history…".
4. Quiet CTA: free · confidential · no courtroom · **may qualify for significant compensation**.

Hard rules (user-locked): **meningioma named in the FIRST sentence** (audience = the diagnosed,
Depo is the reveal); **simple language (10-yr-old reading level)**; **never the word "tumor"**
(targeting — see `feedback_meningioma_only_targeting`); "brain meningioma" preferred.

**June 15, 2026 Pfizer global settlement** = the campaign's strongest FACTUAL urgency. Cite it
**as news, always hedged** ("agreement in principle · not final · terms not public"), **NEVER a
dollar amount** (terms undisclosed; any figure = fabrication). "~5,830 cases" is factual (JPML
July 2026). Verified via web search; user signed off (see `project_depo_meningioma_campaign`).

Picked episodes: **N1 "The Reason"** (cause-reveal), **N3 "Six Thousand"** (number-leads),
**N6 "Good News"** (settlement-as-good-news). Scripts + assets in `outputs/depo_docu/`.

**Production stack:** ElevenLabs VO → Scribe word-timings drive the cut → veo/omni b-roll +
**HyperFrames typography receipt-cards** (2024 STUDY / TWO LABELS ✓vs— / 5,830 ticking counter /
JUNE 15 slam / CTA) → Hormozi captions. Generator `depo_hf/gen_docu.py` (beat-map per episode;
`assets/broll2/` clips). Cards are OUR HTML/CSS — deliberately not news-styled.

## 2. B-roll generation (the reusable library)

- **Silent b-roll i2v = omni-flash** (`omni-flash-useapi`, useapi google-flow) — skips Veo's
  audio-generation step so `AUDIO_GENERATION_FILTERED` (a documented Veo-3.1 RAI false-positive)
  never fires; also cheapest. **Strip audio `-an` on download.** veo-3.1-lite CONTENT-rejects
  clinical/medical stills that fast/omni pass. (Full detail: CLAUDE.md + `feedback_veo_audio_generation_filtered`.)
- **Real product b-roll — gpt-image-2 i2i at `aspect_ratio="9:16"` preserves the label AND is
  vertical.** Feed a real Depo product photo (user stock: box/vial/injection; or online-sourced,
  e.g. InsiderX/Pfizer catalog) as the i2i ref → gpt-image-2 keeps "Depo-Provera"/"Pfizer"/
  "150 mg/mL" faithful in a fresh vertical scene. **nano-banana is UNUSABLE here — it always
  outputs SQUARE** regardless of prompt (see `feedback_nanobanana_square_output`); its scenes had
  to be scrapped and redone on gpt-image-2. i2v the picked stills on omni-flash.
- **Video-frame styling** on gpt-image-2 stills makes them read as real footage: append
  "a single paused FRAME from real documentary VIDEO footage — video color science, slight motion
  blur, handheld softness, muted grade, NOT posed/studio; text soft & unreadable; vertical 9:16".
- Approve stills BEFORE animating (user gate). 44 docu b-roll (v01-24 vertical, nn_* landscape,
  rp_* study pages) + 17 vertical product (pv1-16 + pv_online) in `outputs/depo_docu/broll_clips/`.

## 3. Uploading b-roll to AdMachin (upload + native gen fields)

Reusable: **`scripts/admachin_upload_product_broll.py`**. Two REST calls per clip:
1. **Upload = REST multipart `POST /api/v1/brolls/clips/upload`** (Bearer `ADMACHIN_PAT`),
   `files={"file": (name, bytes, "video/mp4")}`, `data={project_id, subproject_id, title,
   clip_category, tags=json.dumps([...])}`. (MCP `upload_broll` also works but the REST path lets
   one script do upload+PATCH in a loop.) Mirrors `admachin_client.upload_creative`'s multipart.
2. **Gen fields = REST `PATCH /api/v1/brolls/clips/{id}`** (NOT settable at upload, NOT via MCP):
   - `image_generation_model` = **provider/model** → `"poyo/gpt-image-2"` (bare `gpt-image-2` 422s)
   - `video_generation_model` = **BARE id** → `"omni-flash-useapi"` (prefixed `veo/…` 422s)
   - `image_generation_prompt` / `video_generation_prompt` = **free text**
   - Values must be registered Creative Studio ids (`list_image_models` / `list_video_models`).
   - openapi.json is STALE (omits these cols) — trust the upload response, which returns them.

Depo b-roll rows so far: scan/doctor **#68-72** (+#74 dupe), hospital **#75-78**, product **#80-96**.
Project = Tort `e15c60bd…`, subproject = Depo Provera `9cfb5b76…`.

## 4. AdSwipe tort analysis method (metrics are empty → use duplication)

Exported all 533 tort swipes (`export_swipe_creatives_for_agent`, paginate 200/page, results
land in a tool-results file — parse with a merge script). **Engagement metrics are empty**, so use
**duplication-count as the winner proxy** — advertisers only re-run what converts, so the same
script appearing 3-6× is a revealed winner. Findings: **receipts + momentum ("hundreds filing") +
a named villain** win; the top-replicated formats are news-receipts mashups + mechanism-betrayal +
facility/dose name-rolls. Fabricated-amount ads ("six-figure checks waiting, 500 left") run on
disposable burner pages — DON'T copy that; anchor to real checkable events (the June settlement).

## 5. Model / routing quick-refs confirmed this session
- **omni = useapi** (`omni-flash-useapi`, google-flow). Poyo = video-only (no image gen).
- Parallel i2v on omni-flash is fine (`ThreadPoolExecutor`, ~6 workers) — no audio-filter, so
  near-100% first-try; foreground 2-min tool timeout cuts long runs → run batches in background.

## 6. Voice / TTS — the narrator bake-off (2026-07-09)

- **Docu narration MUST be ElevenLabs `eleven_v3`, NOT `eleven_multilingual_v2`.** v2 reads FLAT —
  the user flagged "emotion not realistic" and the fix was the MODEL, not the voice; v3 delivers
  real emotion on the SAME voice. Picked narrator: **Jessica Anne Bogart** ("Narration VO Pro",
  voice_id `lxYfHSkYm1EzQzGhdbfc`), stability 0.5, similarity 0.8. (Also `feedback_docu_voice_v3_captions`.)
- **ElevenLabs Voice Design = the "voice creator"** (distinct from the v3 MODEL): describe a voice
  in words → it generates a NEW one. `POST /v1/text-to-voice/create-previews {voice_description,
  text}` → base64 previews + `generated_voice_id`; finalize via create-voice-from-preview.
- **Alternative TTS providers** — audition when ElevenLabs emotion isn't enough. The pipeline is
  voice-agnostic: `gen_docu.py` auto-rescales every beat to the ACTUAL VO mp3 duration (ffprobe →
  scale = actual/hardcoded), so swapping narrators re-syncs the b-roll automatically.
  - **MiniMax Speech-02** — best for emotion + cost; via **Replicate** `minimax/speech-02-hd`
    (voices `Wise_Woman`/`Calm_Woman`/`Deep_Voice_Man`, an `emotion` param, ~$0.01-0.02/clip). Load
    `REPLICATE_API_TOKEN` into env first — the `replicate` lib reads it from env (inline scripts
    must set `os.environ`). Also on **fal** + MiniMax direct. **KIE has MiniMax VIDEO only, no TTS.**
  - **OpenAI `gpt-4o-mini-tts`** — STEERABLE (an `instructions` field shapes tone/emotion), cheap,
    voices ash/sage/nova/coral. Direct `POST /v1/audio/speech`. Needs a FUNDED OpenAI key (429 quota
    until topped up — `/v1/models` 200 = key valid but no TTS credit).
  - **Hume Octave** (emotion-first) + **Cartesia Sonic** — need their own keys (`HUME_API_KEY`,
    `CARTESIA_API_KEY`); **Cartesia is NOT on fal** (404 "Application cartesia not found"); our local
    `fal_client` only exposes bg-removal + Scribe, not generic TTS.
- **Docu-montage captions = Reels LOWER-THIRD `--vertical-pos 0.78`** (NOT the top/forehead 0.30 —
  that's for talking-head/PIP layouts). **Text cards render OVER b-roll + a dark gradient scrim**
  (`.cardov`), never plain black cards — user: "black bg + text too weak." Reusable generator saved:
  **`scripts/depo_docu_montage_gen.py`** (cards-over-broll + auto-rescale + beat maps for N1/N3/N6).
