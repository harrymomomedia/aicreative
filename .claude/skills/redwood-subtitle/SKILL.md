---
name: redwood-subtitle
description: Burn "Redwood" captions — ALL-CAPS tracked Anton, white with black stroke, and a hot-pink rounded box that karaoke-tracks the spoken word (synced to Scribe word timings). Use when the user says "Redwood captions/subtitles", "pink karaoke captions", "pink highlight subtitles", or wants the reference style from ad-1926019294732556. Engine: scripts/caption_redwood.py.
---

# redwood-subtitle

```bash
.venv/bin/python scripts/caption_redwood.py <in.mp4> --out <out.mp4> --vertical-pos <ASK>
.venv/bin/python scripts/caption_redwood.py <in.mp4> --preview 8      # vpos candidates first
.venv/bin/python scripts/burn_disclaimer.py <out.mp4> <out>_disclaimer.mp4   # combo
```

LOCKED spec (do NOT re-derive; calibrated vs the reference 2026-07-15):
- Font **Anton** (`assets/fonts/Anton-Regular.ttf`) + **tracking 0.055em** (tracked Anton = the
  reference look; Montserrat is too wide, untracked Anton too tight).
- **Width-anchored size** `px = width * 16/9 * 0.0336` (Hormozi guideline).
- ALL-CAPS, punctuation KEPT. White fill, black stroke 0.08em, soft shadow 0.045em.
- **Pink box `rgb(219,18,86)` karaoke-tracks the spoken word**: fires on each Scribe word start,
  HOLDS until the next word. Box = real stroked ink bbox (textbbox) + symmetric **0.10em margin**
  on all four sides, radius 0.22*box_h. Words drawn at explicit cursor positions (same coordinate
  system as the box — never anchor="mm" + advance math).
- ~4 words/card, cards never straddle sentence ends, card pop 0.95→1.0 over 0.10s.
- **vpos is per-video — run --preview and ASK the user** (0.80 for the 2026-07 DJI yapper set).
- Pilot ONE video for sign-off before batching a set.

Built with the `caption-engine-builder` method; sister engines: nick-subtitle, hormozi3.
