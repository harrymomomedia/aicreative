# Minimalist Text-on-Black Ad — Design Spec

**Date:** 2026-05-10
**Project:** Chowchilla / California women's prison compensation campaign
**Source:** `/Users/harry/Desktop/0502(2).mp4` (the "winning script" — 61.81s, 1080×1920 9:16, talking-head delivery)
**Goal:** Re-cut the same audio script as a minimalist text-on-black ad (no person on screen) for A/B testing against the talking-head version.

---

## Output spec

| Property | Value |
|---|---|
| Resolution | 1080 × 1350 (4:5 portrait) |
| Frame rate | 30 fps |
| Duration | ~61.8s (matches source audio length) |
| Codec | H.264 (libx264, CRF 19, preset fast), yuv420p |
| Audio | AAC, 192 kbps, mono or stereo (matches source) |
| Container | MP4 |
| Output count | **2 files** (one per disclaimer-fade variant — see below) |

## Visual composition

**Background:** Pure flat #000 black, full-frame, full duration. No texture, no vignette, no grain, no gradient.

**Subtitles:**
- Source: original audio from `0502(2).mp4`, transcribed via Whisper (`small` model)
- Phrasing: 2–4 word chunks, split on >0.35s pauses or word count (current `caption.py` default)
- Style: bold heavy sans-serif (Arial Black or equivalent), white fill, thin black outline, soft drop shadow (matches existing `caption.py` look)
- Font size: ~3.5% of frame height (existing default), with adaptive shrink up to 10× if a chunk exceeds 2 lines
- Position: **dead center vertically (y ≈ 50% of frame height)** — change from default 16%-from-bottom
- Position horizontally: centered
- Whisper proper-noun substitutions: existing `SUBSTITUTIONS` dict in `caption.py` (handles "Chow-chilluh" → "Chowchilla", etc.)

**Disclaimer overlay:**
- Text (verbatim): "Paid legal advertisement. Jordan M. Jones, Attorney at Law (360 E 2nd St #820, Los Angeles, CA 90012) and Adam Pulaski, Attorney at Law (2925 Richmond Ave #1725, Houston, TX 77098) are responsible for this advertisement. A California-licensed attorney is associated for CA cases. This ad uses paid actors, dramatizations, and AI-generated imagery for illustration only and does not depict real clients or events. No guarantee or prediction of outcome is made. Cases may be referred to other attorneys."
- Window: visible from **t = 5.0s to t = 10.0s** (5-second window)
- Position: bottom-anchored, ~10% from frame bottom edge
- Style: small white text (no background box), center-aligned, multi-line wrapped to fit ~90% of frame width
- Font: regular sans-serif, ~1.6% of frame height (small enough to feel "fine print," large enough to be legible at 1080w)

## Two output variants

**Variant A — hard cut disclaimer:**
- Disclaimer appears instantly at t=5.0s, disappears instantly at t=10.0s

**Variant B — soft-fade disclaimer:**
- 0.3s fade-in starting at t=4.85s (fully opaque at t=5.15s)
- 0.3s fade-out starting at t=9.85s (fully transparent at t=10.15s)
- Total visible window unchanged (~5.0s of fully-opaque time)

Both variants use identical subtitles, identical BG, identical audio. Only the disclaimer overlay's enable/alpha behavior differs.

## Build pipeline

A single new script: `scripts/render_minimal_ad.py <source.mp4> <out_dir>`

Steps:

1. **Extract audio for Whisper** from `<source.mp4>` → `<out_dir>/tmp/audio.wav` (mono, 16kHz). This is for transcription only; the final mux pulls the audio stream directly from `<source.mp4>` via ffmpeg `-map 1:a -c:a aac -b:a 192k` (re-encoded to AAC for MP4 compatibility, no extra extract step).
2. **Whisper transcribe** with `small` model, word-level timestamps → `<out_dir>/tmp/transcript.json`
3. **Chunk into caption phrases** using existing logic in `caption.py` (refactor that function out into a reusable helper if needed)
4. **Generate base black video** with audio:
   ```
   ffmpeg -f lavfi -i color=c=black:s=1080x1350:d=<dur>:r=30 -i <source.mp4> \
     -map 0:v -map 1:a -c:v libx264 -crf 19 -preset fast -pix_fmt yuv420p \
     -c:a aac -b:a 192k -shortest <out_dir>/tmp/base.mp4
   ```
5. **Render caption PNGs** (one per chunk) using PIL — extend `caption.py` to accept a `position` parameter ("bottom" default | "center")
6. **Render disclaimer PNG** once (multi-line wrapped, white text on transparent BG)
7. **Single ffmpeg `filter_complex` pass**: overlay all caption PNGs with `enable=between(t,start,end)` + disclaimer PNG with `enable=between(t,5,10)` (variant A) or with alpha-fade expression (variant B)
8. Output two files: `<out_dir>/minimal_ad_hardcut.mp4` and `<out_dir>/minimal_ad_softfade.mp4`

**One ffmpeg encode pass at the end** — captions and disclaimer go on in the same `filter_complex`, not chained, so video is encoded once per variant. (Alternatively: render once with hardcut, then run a second pass that only re-overlays the disclaimer with fade — but a single pass per variant is cleaner.)

## Files touched / created

- **New:** `scripts/render_minimal_ad.py` (the orchestrator)
- **Modified:** `caption.py` — add a `position` parameter (`"bottom"` default | `"center"`) to the function that renders the per-chunk PNG and computes its y-coordinate. Default behavior unchanged for existing CLI users. The new script imports and calls this function directly with `position="center"`.
- **Output dir:** `outputs/0502_minimal/` (already exists from BG mockup work)

## Out of scope

- No voice changer / TTS / audio normalization (using source audio as-is)
- No b-roll, no background animation, no progress bar, no logo, no end card
- No video model generation (no Veo/Kling/Seedance — the ad has no scene to generate)
- No batching / variant generation beyond the two disclaimer-fade variants

## Acceptance criteria

1. Both output MP4s play 61.8s ± 0.2s with original audio audible and undistorted
2. Captions appear on the same words as the source audio (Whisper word timing within ~150ms)
3. Captions are vertically centered, horizontally centered, all chunks fit within frame
4. Disclaimer is fully readable on a phone screen (1080w viewport) and visible only during 5–10s window
5. Variant B's disclaimer fades in/out smoothly (no flicker, no double-render)
6. No on-screen artifacts, no clipping, no caption text overflowing frame edges
