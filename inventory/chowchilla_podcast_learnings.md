# Chowchilla podcast campaign — learnings

Podcast-style talking-head ads (letters A–M), persona = gpt-image close-up with headphones +
condenser mic. Producer: `scripts/podcast_omni_produce.py`. Generation lessons live in the
`podcast-omni` skill (`.claude/skills/podcast-omni/SKILL.md`); this file is the campaign log.

## K on Veo 3.1 Lite low-priority (free path) — 2026-06

A SEPARATE deliverable from the completed omni `K_full.mp4` (41.98s — do not touch). User asked
for the same K script regenerated on the free `veo-3.1-lite-low-priority` google-flow model.

- **Persona M8** (moody #8), I2V `startImage` mode. 7 curated chunks (`VEO_CHUNKS["K"]`),
  13–23 words each at 6s/8s. Final 41.2s ≈ omni's 42.0s.
- **Deliverables** (`outputs/chowchilla_podcast/`):
  - `K_veo_full.mp4` — assembled, still watermarked (reference only)
  - `K_veo_clean.mp4` — **clean master**: ratio-preserving watermark crop + −15 LUFS master
  - `K_veo_clean_submagic_hormozi3.mp4` — Submagic "Hormozi 3" captions only
  - `K_veo_clean_submagic_hormozi3_disclaimer.mp4` — **combo final** (captions + Pulaski/Jones
    disclaimer, hard cut, auto window 5.5–11.5s)
- **Watermark crop** (user-locked: NEVER stretch): one pass on the assembled file, before captions —
  center-crop `675:1200` (= 9:16 exactly, drops the bottom 80px "Veo" mark, x≈22) → `scale=720:1280`,
  uniform 16/15× on both axes, zero distortion.
- **Pacing** measured from trimmed `_jt` spans (intended words ÷ span): mean 2.92 wps, spread 0.79
  (min 2.43 clip05, max 3.22 clip06) — user-acceptable, shipped without rebalancing.
- **The clean() false-reject epidemic** cost ~9 wasted generations and initially dropped the 3 most
  important beats (hook, facility list, $116M). All were transcript-matching false positives, not bad
  audio. Root causes + fix are now global rules — see "Transcript word-matching QA" in `CLAUDE.md`
  and the Veo section of the `podcast-omni` skill. After the fix, all 3 beats cleared FIRST attempt.
- **Submagic QA result:** dictionary `["Chowchilla","CCWF","CIW"]` held all proper nouns;
  "SIGNIFICANT POTENTIAL COMPENSATION" rendered intact; Submagic reformatted the spoken
  "a hundred and sixteen million dollars" → caption **"$116 MILLION"** — accurate, user-acceptable
  (punchier as a caption). Digit reformatting is only a problem when it changes meaning.
