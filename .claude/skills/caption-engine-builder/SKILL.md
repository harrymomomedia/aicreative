---
name: caption-engine-builder
description: The general method for building a NEW caption/subtitle engine from a reference video — reverse-engineering workflow, sizing/geometry/timing laws, render architecture, and verification loop. Use when the user shares a subtitle style to clone ("create this subtitle style", "new caption format", "make captions like this video") or asks to build/tune a caption engine. Distills the Hormozi-3, Nick, and Redwood builds.
---

# caption-engine-builder

How to clone a caption style into a new in-house engine (`scripts/caption_<name>.py`). The PIL +
ffmpeg stack is the default — a new style is a fork of an existing engine with a new draw
function; only consider HyperFrames when the style needs real motion graphics the PIL path can't do.

## Reverse-engineering workflow (in order)

1. **Contact sheet first**: `fps=1, tile` over the whole reference → see card rhythm, position,
   words-per-card, highlight behavior across time. Then full-res band crops at the caption zone.
2. **Measure RELATIVE proportions** (% of frame W/H), never absolute px. Pixel masks are noisy —
   verify visually at zoom, sample colors numerically (PIL pixel counters over the element).
3. **Font ID by cap-matched shootout**: render candidate fonts at the SAME cap height as the
   reference, stack against the ref crop, compare letterform WIDTH and skeleton. Letter TRACKING
   is a separate dial from font choice — a "wider" look is often the same font + tracking
   (Redwood = Anton + 0.055em tracking, NOT a wider font).
4. **Watch for per-word behavior**: a highlight that appears on different words in different
   frames is KARAOKE (synced to spoken word), not a static keyword pick. Sample 4-6 fps across
   one card to see it move.

## The laws (apply to every new engine)

- **Sizing is WIDTH-anchored (the Hormozi guideline)**: `px = width * (16/9) * ratio`, standard
  ratio **0.0336**. Same physical size across 9:16 / 4:5 / 1:1. Never height-anchored. Font only
  SHRINKS on overflow (per-card, `> width*0.92`) — never fit-to-width growth.
- **Geometry from INK, not advance math**: draw words at explicit cursor positions (one
  coordinate system for text AND decorations). Boxes/underlines/highlights are built from
  `d.textbbox(..., stroke_width=stroke)` REAL stroked ink bounds + SYMMETRIC margins on all four
  sides. anchor="mm" + separate advance math drifts — the Redwood box landed beside its word
  until the renderer was rewritten cursor-based.
- **Timing**: cards from Scribe words (verbatim ours, never auto-transcribe); never straddle a
  sentence boundary (track an `eos` flag per word); word-level highlights fire on each word's
  `start` and HOLD until the next word's start. Match the reference's punctuation/case policy
  exactly (Nick strips all punctuation; Redwood keeps it; verify against a real export).
- **Vertical position is PER-VIDEO, confirmed by asking**: ship a `--preview <t>` mode that
  composites a sample card at candidate vpos values on a real frame; the user picks per video
  (faces/mics sit differently per framing). Never hardcode the reference's vpos.
- **Render architecture**: pre-render card images (one per highlight state — N words = N
  variants), frame loop picks by time, dedupe identical frames by cache key (card id, state,
  rounded scale), write PNG sequence, ONE ffmpeg overlay pass. Never per-card filter chains.
- **Subtle card pop**: ~0.94→1.0 scale over ~0.10-0.12s ease-out matches most modern styles.
- **Disclaimer is a separate layer** (`burn_disclaimer.py` on the captioned output); keep the
  clean master untouched; suffix naming `<master>_<style>.mp4`.

## Verification loop (until 1:1)

- **A/B strip against the reference**: ref band and our band stacked at the same scale, every
  iteration. "Compare with the original carefully" — the user will.
- Dense grid (4-6 fps over a few seconds) to verify highlight motion/timing, not single frames.
- **Pilot ONE video → show → get sign-off → THEN batch** the rest. Local re-renders are cheap;
  repeated user review isn't.
- Interface parity with existing engines: `--out --vertical-pos --max-words --min-pause --biased
  --end --preview`, venv invocation, works with the existing combo/burn scripts.

## Existing engines to fork from

`caption_nick.py` (box card, sentence-case), `caption_hormozi3.py` (per-line color + emoji,
width-anchor reference implementation), `caption_redwood.py` (karaoke pink-box word tracking,
tracked font, ink-bbox geometry), `caption_styled.py` (yellow per-word legacy).
