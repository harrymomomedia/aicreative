---
name: nick-subtitle
description: Burn Submagic-style "Nick" captions onto a video using the internal `scripts/caption_nick.py` renderer — sentence-case white bold sans on a semi-transparent dark rounded box, centered lower-third, no emoji, no color accent. Use when the user says "Nick subtitle", "Submagic Nick", "dark pill captions", "Nick captions", or wants the calmer creator-caption look with exact transcript control.
---

# Nick Subtitle

Use this skill when the user wants the **Submagic Nick** look, but we need **in-house control** over the exact words.

This is the calmer caption style:
- sentence-case, not all-caps
- white bold sans text
- semi-transparent dark rounded box / pill
- about 2 words per card
- one centered line
- no emoji
- no yellow/green/red accent rotation

## Why this skill exists

Prefer the internal renderer over the Submagic API when the exact wording matters.

- `scripts/caption_nick.py` uses **our Scribe transcript**, so regulated lines stay verbatim.
- Submagic can auto-transcribe or reformat text in ways that are risky for legal ads.
- This keeps the Nick look without paying for or depending on the Submagic render pass.

## When to use it

Invoke for requests like:
- "use Nick subtitle"
- "make it Submagic Nick"
- "dark pill subtitle"
- "calm phrase captions"
- "use the Nick style for this legal ad"

Especially good for:
- women's-prison legal ads
- prison-abuse / sexual-abuse compensation ads
- calm UGC talking-head videos
- any case where Hormozi / yellow-text would feel too loud

## The locked look

- Font: **Helvetica Neue Bold** (`/System/Library/Fonts/HelveticaNeue.ttc`, bold face)
- Text: white `#F8F8F8`
- Box: `rgb(45,45,42)` at about **0.58 opacity**
- Position: lower-third, box center about **0.754 × frame height**
- Grouping: about **2 words per card**, single line, centered
- Punctuation: strip trailing sentence punctuation; keep apostrophes
- Animation: small scale-pop on entry only

If the user wants:
- all-caps + rotating color accent + emoji → use `hormozi3`
- yellow per-word highlight → use `yellow-text-sub`

## Commands

```bash
.venv/bin/python scripts/caption_nick.py <in.mp4> --out <out.mp4>
```

If the campaign also needs the Pulaski/Jones disclaimer:

```bash
.venv/bin/python scripts/caption_nick.py <in.mp4> --out <captions.mp4>
.venv/bin/python scripts/burn_disclaimer.py <captions.mp4> <combo.mp4>
```

The disclaimer text/styling itself is governed by `pulaski-jones-disclaimer`. Do not paraphrase that copy.

## Do not repeat

- Do not convert this style to all-caps. That turns it into a different template.
- Do not add emoji, color accents, or per-word flashing just because the user said "Submagic."
- Do not route legal Nick jobs through the Submagic API by default when exact wording matters.
