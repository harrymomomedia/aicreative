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
| `--font-ratio` | `0.0336` | Font size, WIDTH-anchored (see sizing below). Keeps its historical 9:16 meaning but is now aspect-independent. |
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
- **Size is essentially FIXED at `font_ratio 0.0336`** (≈ a ~2-word line fills ~42% of frame width — measured directly off the reference). It is NOT fit-to-width/area growth — short and long cards are the **same glyph size**. Font only shrinks if a single line/card overflows the width or 3 lines.
- **Font is sized relative to WIDTH, not height** (`_font_px(width, ratio)` + `REF_ASPECT = 16/9`). A phone shows the SAME horizontal width whether the video is 9:16 / 4:5 / 1:1, so the caption must be the SAME physical size across aspects. Sizing to height made 4:5 captions ~70% the size of 9:16's despite identical 720px width (user-flagged 2026-05-22). `font_ratio` keeps its historical 9:16 meaning (there `height = width·16/9`, so `height·ratio == width·(16/9)·ratio`) → 9:16 output unchanged, 4:5/1:1 now match it.
- **Wrapping: ~2 words per line** (`words_per_line = 2`), with a width fallback so long single words drop to 1/line. This tight stacking is what keeps the size looking uniform and "not too big" (e.g. "I WAS / WRONG", "YOU SITTING / DOWN", "SIGNIFICANT / POTENTIAL / COMPENSATION").
- Position: text-block center ~**0.70** of frame height — **lower third, well clear below the chin** even when she leans/tilts (`vertical_pos` default 0.70). 0.60/0.64 still caught the jaw on some clips; 0.70 keeps the caption + its 'down' emoji clear of the face AND above the bottom disclaimer band (~0.88–1.0). User-approved 2026-05-21.

**Color / stroke:**
- Default word = WHITE `#FFFFFF`; the **active LINE** is the card's accent (whole line, not single word).
- Accent **rotates per card**: 🟡 `#FCFB14` → 🟢 `#2AF82B` → 🔴 `#EE1916` → repeat.
- Stroke: black, ~`0.06 × fontsize`. Subtle drop shadow (offset 0.04, blur 0.03, ~45% alpha). **No glow** (glow = the newer Impact template, not Hormozi 3).

**Animation (measured + approved):**
- **Captions stay ON continuously** — no per-word flashing (cards are back-to-back; the active line flips per spoken line).
- **Text pop:** on each card's appearance the text scales **96% → 105% (peak ~+0.04s) → 100% (settled ~0.12s)** — a subtle ~10% overshoot (`TEXT_POP_DUR 0.12`).
**Emoji motion — LOCKED-IN system (user-approved 2026-05-21, the GO-TO settings):**
- **Bound to its text card** — the emoji appears with its card and disappears the instant the caption advances (no cross-card linger; Submagic ties the emoji to the text segment).
- **Directional slide set** (`EMOJI_PRESETS`, rotates per emoji): the 4 cardinals + 4 diagonals + one **static**: `right, up_right, up, up_left, left, down, static, down_right, down_left`. Each travels in its compass direction (matching the user's arrow diagram).
- **Fixed distance + same speed for ALL:** horizontal travel = width of the word **"INSIDE"** (I→E), centered (±half) — a SINGLE fixed distance, NOT relative to the subtitle/word lengths (california / full-subtitle / edge-to-edge all read as too far). Computed once in `burn()` (`slide_half`). Motion is **EASE-IN-OUT** (accelerate→decelerate, like a car; uses `_smooth` smoothstep) over a **FIXED** `SLIDE_ENTER_DUR 0.30s` (same speed every time, NOT card-relative), then **HOLDS at the destination** for the rest of the card (so it's clearly seen parked — not a slow crawl that vanishes on arrival).
- **Stays close to the text:** vertical travel is capped to **< 1 line** (`slide_v ≈ 0.85×fontsize`) and `sdy/rdy ≥ 0` so the emoji **never rises INTO the text** (no blocking) and is **never more than ~1 line away** (no double-space gap). "up" rests just below the caption; "down" rests ~1 line below. Diagonals are deliberately shallow (full horizontal + capped vertical) to stay close.
- **High emoji rate (~60% of cards):** `KEYWORD_EMOJI` is broadly expanded with the campaign vocabulary (told/say/voice→🗣️, inside/locked→🔒, found→🔍, sitting→🪑, two/couple→✌️, thirty/seconds→⏱️, listen→👂, buried→🕳️, form/filled→📝, lawyers→⚖️, complete/done→✅, …) and `EMOJI_MIN_GAP 0.4s` is a low throttle, so most keyword cards show one (natural gaps remain on filler cards).
- **Emoji art = PREFER the animated Noto GIF** when one exists for the glyph (animated beats static), else fall back to **Apple Color Emoji static** (PIL `embedded_color` 160px sbix strike, single-codepoint only), else Twemoji PNG. A `.nogif` marker caches 404s. All get the transform motion regardless of art source.

## Emoji system

Keyword → emoji map in `caption_hormozi3.py:KEYWORD_EMOJI` (lowercased; first match per card; broadly expanded for ~60% card coverage). **No back-to-back repeats** — `pick_emoji(words, exclude=last_placed)` skips the previously placed glyph and prefers a different keyword's emoji in the same card (else places nothing), so the same emoji never appears on two consecutive placements (distracting). Render order in `render_emoji_frames()`: **Noto animated GIF first** (for ANY glyph that has one — flags 🇺🇸 work here), else **Apple Color Emoji static** (PIL `embedded_color`, 160px sbix strike), else Twemoji. **Prefer single-codepoint emojis** — the Apple fallback can't shape ZWJ families (👩‍👧) and renders a placeholder box. Cached in `assets/emoji/` (`.nogif` marker caches Noto 404s). `--no-emoji` skips.

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
