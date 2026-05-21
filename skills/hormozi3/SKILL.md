---
name: hormozi3
description: Burn Submagic-style "Hormozi 3" captions onto a video — Montserrat Black all-caps, white text with the active LINE highlighted in a rotating YELLOW/GREEN/RED accent (per card), black stroke, subtle shadow, a small text pop on appearance, and animated emojis that slide across the subtitle. Use when the user says "Hormozi captions", "Hormozi 3", "Submagic Hormozi", "Hormozi style subs", "yellow green red captions", or wants the Alex-Hormozi creator-caption look.
---

# hormozi3

Burns **Submagic "Hormozi 3"** captions. Reverse-engineered + tuned frame-by-frame (incl. 0.04s motion analysis) against a real Submagic Hormozi 3 export and user-approved 2026-05-21. **Everything below is a GLOBAL, parametric rule** — there are NO word-specific hacks, so any new video (any transcript) comes out looking like Submagic.

## When to invoke

"Hormozi captions" / "Hormozi 3" / "Submagic Hormozi" / "yellow green red captions" / "the Alex Hormozi caption look". Distinct from **`yellow-text-sub`** (single fixed-yellow highlight + legal disclaimer). Hormozi 3 = rotating 3-color accent + animated slide-in emojis + text pop.

## The script

`scripts/caption_hormozi3.py` (aicreative). Depends on `caption_styled.py` (audio/probe helpers) + `elevenlabs_client.scribe_whisper_compat`. Assets in `assets/fonts/Montserrat-Black.ttf` and `assets/emoji/` (cached).

```bash
.venv/bin/python scripts/caption_hormozi3.py <in.mp4> --out <out.mp4>
# generic text (no campaign proper-nouns): add  --biased ""
```

| Flag | Default | Notes |
|---|---|---|
| `--font-ratio` | `0.0336` | Font as fraction of frame height (see sizing below). |
| `--max-words` | `3` | Words per caption card (split on >0.35s pause). |
| `--max-lines` | `3` | Up to 3 lines; long cards stack to 3. |
| `--vertical-pos` | auto (~0.68–0.70) | Lower-third. |
| `--no-emoji` | off | Disable the emoji layer. |
| `--disclaimer` | off | Overlay the verbatim Pulaski/Jones legal disclaimer at the bottom (under captions), auto-placed at the calmest "most boring" window (motion analysis), for `--disclaimer-secs` (6s). Override window with `--disclaimer-start <sec>`. |
| `--biased` | `Chowchilla:3.0,CCWF:2.0` | Scribe proper-noun bias; set `""` for generic text. |
| `--end <sec>` | — | Caption only first N seconds (fast tests). |

## GLOBAL RULE — verified spec (the look)

**Font & size (the part that took the most tuning):**
- Font: **Montserrat Black (900)**, ALL CAPS.
- **Size is essentially FIXED at `font_ratio 0.0336`** (≈ a ~2-word line fills ~42% of frame width — measured directly off the reference). It is NOT fit-to-width/area growth — short and long cards are the **same glyph size** (Submagic's white-cap height is uniform ~2.2% of frame height). Font only shrinks if a single line/card overflows the width or 3 lines.
- **Wrapping: ~2 words per line** (`words_per_line = 2`), with a width fallback so long single words drop to 1/line. This tight stacking is what keeps the size looking uniform and "not too big" (e.g. "I WAS / WRONG", "YOU SITTING / DOWN", "SIGNIFICANT / POTENTIAL / COMPENSATION").
- Position: text-block center ~**0.60** of frame height — **upper chest, just below the chin** (measured off the reference). NOT lower-third. This puts the text near screen-center and the emoji (just below the text) near center too — the Submagic look. (Verified 2026-05-21 by overlaying a screen-center line on the real export: caption block sits at ~0.60, not 0.70.)

**Color / stroke:**
- Default word = WHITE `#FFFFFF`; the **active LINE** is the card's accent (whole line, not single word).
- Accent **rotates per card**: 🟡 `#FCFB14` → 🟢 `#2AF82B` → 🔴 `#EE1916` → repeat.
- Stroke: black, ~`0.06 × fontsize`. Subtle drop shadow (offset 0.04, blur 0.03, ~45% alpha). **No glow** (glow = the newer Impact template, not Hormozi 3).

**Animation (measured + approved):**
- **Captions stay ON continuously** — no per-word flashing (cards are back-to-back; the active line flips per spoken line).
- **Text pop:** on each card's appearance the text scales **96% → 105% (peak ~+0.04s) → 100% (settled ~0.12s)** — a subtle ~10% overshoot (`TEXT_POP_DUR 0.12`).
- **Emoji position (MOST important — verified 2026-05-21 against the real export):** the emoji **HUGS the subtitle** — centered horizontally, just **below** the text block, near screen-center. It does **NOT** fly out to the frame edges, park far above, or sit off to the side. Every preset's REST position is at/near centered-just-below-text; only the **entrance direction** varies. (Measured: reference emoji sits at ~0.63 frame height directly under the caption, centered.)
- **Emoji entrance presets** (rotate per emoji card, all settle centered-below): `slide_across` (slides in across the text from the left, settles center — short traverse, NOT across the whole frame), `fly_out` (drifts up from below to just under the text, centered), `slide_up` (small rise from below), `pop` (scale in place). `EMOJI_ENTER_DUR 0.45s`, smooth ease (`1-(1-p)³`). `PRESET_PATH` amplitudes are deliberately small (≤0.13 width / ≤0.07 height) — the early "edge→edge / fly-outward" versions read as "too far out, too far from the subtitle" vs the reference.
- **Emoji is BOUND TO ITS TEXT CARD** — it disappears the instant the caption advances to the next card (no cross-card linger). Submagic ties the emoji to the text segment; when the text moves on, the emoji goes. `EMOJI_ENTER_DUR 0.25s` (SNAPPY — the fix for "disappears too quickly" was a *faster entrance* so it's settled-visible for most of its short card, NOT a longer linger). `EMOJI_MIN_GAP 0.8s` lightly throttles so most keyword cards show one (gaps on non-keyword cards, like the reference).
- **Emoji art = PREFER the animated Noto GIF** when one exists for the glyph (animated beats static — matches what Submagic uses for the lively ones), else fall back to **Apple Color Emoji static** (exact-Apple look, PIL `embedded_color` 160px sbix strike, single-codepoint only), else Twemoji PNG. A `.nogif` marker caches 404s so we don't refetch. All get the transform motion regardless of art source.

## Emoji system

Keyword → emoji map in `caption_hormozi3.py:KEYWORD_EMOJI` (lowercased; first match per card). **Use single-codepoint emojis** — PIL can't shape ZWJ families (👩‍👧) or flags (🇺🇸) in the Apple font (they render a placeholder box), and Noto lacks animated GIFs for them too. Render: `render_emoji_frames()` → Noto animated GIF if the emoji is in `ANIMATE_VIA_NOTO`, else Apple Color Emoji static (PIL `embedded_color`, 160px sbix strike), else Twemoji. Cached in `assets/emoji/`. `--no-emoji` skips.

## Pipeline (fast single-pass)

1. ffmpeg extracts audio → **ElevenLabs Scribe** word timestamps.
2. Words → ≤3-word cards (split on >0.35s pause).
3. Per card: fixed-size layout, ~2-word wrap, line PNGs (active line accent).
4. **Pre-composite the WHOLE caption track** (text pop + animated-emoji frames + slide motion) to a PNG sequence in PIL, then **overlay in ONE ffmpeg pass**. (~20s for a 60s clip — do NOT chain one ffmpeg `overlay` per card; that's minutes.)

## Gotchas

- **Render is single-pass PNG-sequence + one overlay.** Chaining N `overlay` filters (one per card/emoji) is O(cards) slow — don't.
- **Emoji = Apple static (most) + Noto animated GIF (lively set)**, composited per video-frame with the transform motion. Apple via PIL `embedded_color` — single-codepoint only. There is no free animated-Apple set (paid Lottie packs only); Apple-emoji use in commercial video is a licensing gray area.
- **Font is fixed, wrapping is 2-words/line** — resist "fit-to-width" growth; it makes short cards too big. The uniform size + tight wrap is the Submagic look.
- `%` in argparse help strings must be `%%`.
- Chunking via `caption_styled.chunk_words` → CHOWCHILLA/MIJA substitutions apply.

## Related

- `yellow-text-sub` — single yellow highlight + legal disclaimer (Pulaski/Jones legal-ad look).
- `pulaski-jones-disclaimer` — verbatim legal disclaimer.
