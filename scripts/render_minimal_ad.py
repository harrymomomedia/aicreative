#!/usr/bin/env python3
"""
Render a minimalist 4:5 text-on-black ad from a source talking-head video.

  Input:  any video with usable audio (the "winning script")
  Output: two MP4s in <out_dir>/
            minimal_ad_hardcut.mp4   — disclaimer hard cut on at t=5, off at t=10
            minimal_ad_softfade.mp4  — disclaimer fades in/out (0.3s each side)

Usage:
  .venv/bin/python scripts/render_minimal_ad.py <source.mp4> <out_dir> \\
      [--model small] [--width 1080] [--height 1350] \\
      [--disclaimer-start 5.0] [--disclaimer-duration 5.0]

The script:
  1. Probes source duration
  2. Extracts mono 16k audio for Whisper
  3. Transcribes with word-level timestamps
  4. Chunks words into caption phrases via caption.chunk_words
  5. Renders each chunk PNG via caption.render_chunk(position="center")
  6. Renders the disclaimer PNG (multi-line, bottom-anchored, white text on transparent)
  7. For each variant: builds an ffmpeg filter_complex that overlays:
        - A blank 1080x1350 black source as the base video
        - The source audio (re-encoded AAC for MP4 compat)
        - All caption PNGs with enable=between(t,start,end)
        - The disclaimer PNG (hard cut OR alpha fade depending on variant)
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Reuse caption.py helpers
from caption import (
    SUBSTITUTIONS,
    apply_substitutions,
    chunk_words,
    extract_audio,
    find_font,
    render_chunk,
    transcribe,
    _wrap_to_lines,
)

DISCLAIMER_TEXT = (
    "Paid legal advertisement. Jordan M. Jones, Attorney at Law "
    "(360 E 2nd St #820, Los Angeles, CA 90012) and Adam Pulaski, Attorney at Law "
    "(2925 Richmond Ave #1725, Houston, TX 77098) are responsible for this advertisement. "
    "A California-licensed attorney is associated for CA cases. "
    "This ad uses paid actors, dramatizations, and AI-generated imagery for illustration only "
    "and does not depict real clients or events. No guarantee or prediction of outcome is made. "
    "Cases may be referred to other attorneys."
)

DISCLAIMER_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe_duration(video):
    r = run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", str(video),
    ])
    return float(json.loads(r.stdout)["format"]["duration"])


def find_disclaimer_font():
    for p in DISCLAIMER_FONT_CANDIDATES:
        if Path(p).exists():
            return p
    # Fall back to caption font (heavy, but readable shrunk)
    return find_font()


def render_disclaimer_png(text, width, height, font_path, png_path,
                          fontsize_ratio=0.016, marginv_ratio=0.10,
                          line_spacing_ratio=0.12, max_width_ratio=0.90):
    """Render the static disclaimer as a transparent PNG.
    Bottom-anchored at marginv_ratio from the bottom edge. Center-aligned text."""
    from PIL import Image, ImageDraw, ImageFont

    fontsize = max(14, int(height * fontsize_ratio))
    marginv = int(height * marginv_ratio)
    max_w = int(width * max_width_ratio)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, fontsize)

    # Wrap to fit max_w. No stroke for the small fine-print text.
    lines = _wrap_to_lines(text, font, draw, max_w, stroke=0)

    # Measure heights/widths
    line_widths, line_heights = [], []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    line_gap = int(fontsize * line_spacing_ratio)
    total_h = sum(line_heights) + (len(lines) - 1) * line_gap

    # Bottom-anchor: top of the block sits (marginv + total_h) up from bottom
    y0 = height - marginv - total_h
    cur_y = y0
    for i, line in enumerate(lines):
        x = (width - line_widths[i]) // 2
        # Subtle dark drop shadow for readability over any color (here pure black, so minor)
        draw.text((x + 1, cur_y + 1), line, font=font, fill=(0, 0, 0, 220))
        draw.text((x, cur_y), line, font=font, fill=(255, 255, 255, 255))
        cur_y += line_heights[i] + line_gap

    img.save(png_path)


def build_filtergraph(num_captions, width, height, duration, fps,
                      disclaimer_start, disclaimer_dur, fade_dur):
    """Build the filter_complex string.

    Inputs (in order):
      [0:v]  → black base (lavfi color)
      [1:a]  → source audio
      [2:v]  → disclaimer PNG (looped)
      [3:v]..[N+2:v] → caption PNGs (one per chunk)

    fade_dur > 0 → variant B (soft fade); = 0 → variant A (hard cut).
    """
    parts = []

    # Disclaimer: looped to full duration. Hard cut OR soft fade.
    if fade_dur > 0:
        # alpha fade in starting at (start - fade_dur/2), fade out at (end - fade_dur/2)
        # so the *fully opaque* window stays exactly disclaimer_start → disclaimer_start + disclaimer_dur
        fi_st = max(0.0, disclaimer_start - fade_dur / 2)
        fo_st = disclaimer_start + disclaimer_dur - fade_dur / 2
        parts.append(
            f"[2:v]loop=loop=-1:size=1:start=0,setpts=N/{fps}/TB,format=yuva420p,"
            f"fade=in:st={fi_st:.3f}:d={fade_dur:.3f}:alpha=1,"
            f"fade=out:st={fo_st:.3f}:d={fade_dur:.3f}:alpha=1[disc]"
        )
        # Always overlay (alpha controls visibility)
        parts.append("[0:v][disc]overlay=0:0[v0]")
    else:
        parts.append(
            f"[2:v]loop=loop=-1:size=1:start=0,setpts=N/{fps}/TB,format=yuva420p[disc]"
        )
        end = disclaimer_start + disclaimer_dur
        parts.append(
            f"[0:v][disc]overlay=0:0:enable='between(t,{disclaimer_start:.3f},{end:.3f})'[v0]"
        )

    # Captions: chained overlays
    prev = "[v0]"
    for i in range(num_captions):
        in_idx = 3 + i  # caption PNGs start at input index 3
        out_label = f"[v{i+1}]"
        # Loop each caption PNG to full duration so its timestamps align with `enable`
        cap_label = f"[cap{i}]"
        parts.append(
            f"[{in_idx}:v]loop=loop=-1:size=1:start=0,setpts=N/{fps}/TB,format=yuva420p{cap_label}"
        )
        # Use chunk-specific enable window — the caller passes intervals via parts list (we do it differently)
        parts.append(f"{prev}{cap_label}overlay=0:0:enable='__ENABLE_{i}__'{out_label}")
        prev = out_label

    return ";".join(parts), prev


def render_variant(out_path, source_video, base_dur, fps, width, height,
                   chunks, caption_pngs, disclaimer_png,
                   disclaimer_start, disclaimer_dur, fade_dur):
    """Single ffmpeg pass: build base black video + audio + overlays in one shot."""
    # Inputs: lavfi black, source audio, disclaimer png, then all caption pngs
    inputs = [
        "-f", "lavfi", "-i", f"color=c=black:s={width}x{height}:d={base_dur:.3f}:r={fps}",
        "-i", str(source_video),                # for audio (-map 1:a)
        "-i", str(disclaimer_png),
    ]
    for p in caption_pngs:
        inputs += ["-i", str(p)]

    fg, last_v = build_filtergraph(
        num_captions=len(caption_pngs),
        width=width, height=height, duration=base_dur, fps=fps,
        disclaimer_start=disclaimer_start, disclaimer_dur=disclaimer_dur,
        fade_dur=fade_dur,
    )
    # Substitute __ENABLE_i__ tokens with per-chunk intervals
    for i, c in enumerate(chunks):
        token = f"__ENABLE_{i}__"
        fg = fg.replace(token, f"between(t,{c['start']:.3f},{c['end']:.3f})")

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", fg,
        "-map", last_v,
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{base_dur:.3f}",
        str(out_path),
    ]
    print(f"  ffmpeg: {len(caption_pngs)} caption overlays + disclaimer ({'fade' if fade_dur>0 else 'hardcut'})", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        # Print last chunk of stderr — full stderr is huge
        raise RuntimeError(f"ffmpeg failed (variant out={out_path.name}):\n{r.stderr[-3000:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="path to source video (audio used)")
    ap.add_argument("out_dir", help="output directory (created if missing)")
    ap.add_argument("--model", default="small", help="whisper model")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--disclaimer-start", type=float, default=5.0)
    ap.add_argument("--disclaimer-duration", type=float, default=5.0)
    ap.add_argument("--fade-dur", type=float, default=0.3, help="fade duration for soft-fade variant (only used with --also-fade)")
    ap.add_argument("--also-fade", action="store_true", help="also produce a softfade variant (default: hardcut only)")
    ap.add_argument("--keep-tmp", action="store_true")
    args = ap.parse_args()

    source = Path(args.source).resolve()
    if not source.exists():
        raise SystemExit(f"not found: {source}")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = probe_duration(source)
    print(f"source: {source.name}  duration={duration:.2f}s", flush=True)
    print(f"output: {args.width}x{args.height} @ {args.fps}fps → {out_dir}", flush=True)

    work = out_dir / "tmp"
    work.mkdir(exist_ok=True)
    cap_dir = work / "captions"
    cap_dir.mkdir(exist_ok=True)

    audio = work / "audio.wav"
    print(f"[1/5] extract audio for whisper", flush=True)
    extract_audio(source, audio)

    print(f"[2/5] whisper transcribe ({args.model})", flush=True)
    result = transcribe(audio, args.model)
    (work / "transcript.json").write_text(json.dumps(result, indent=2, default=str))

    print(f"[3/5] chunk words", flush=True)
    chunks = chunk_words(result["segments"], max_words=args.max_words)
    print(f"      {len(chunks)} caption chunks", flush=True)
    for c in chunks[:5]:
        print(f"      {c['start']:5.2f}-{c['end']:5.2f}  {c['text']}", flush=True)
    if len(chunks) > 5:
        print(f"      ... +{len(chunks)-5} more", flush=True)

    print(f"[4/5] render caption + disclaimer PNGs", flush=True)
    cap_font = find_font()
    caption_pngs = []
    for i, c in enumerate(chunks):
        p = cap_dir / f"chunk_{i:03d}.png"
        render_chunk(c["text"], args.width, args.height, cap_font, p, position="center")
        caption_pngs.append(p)

    disc_font = find_disclaimer_font()
    disclaimer_png = work / "disclaimer.png"
    render_disclaimer_png(DISCLAIMER_TEXT, args.width, args.height, disc_font, disclaimer_png)

    n_variants = 2 if args.also_fade else 1
    print(f"[5/5] render {n_variants} ffmpeg variant{'s' if n_variants > 1 else ''}", flush=True)

    out_hard = out_dir / "minimal_ad_hardcut.mp4"
    render_variant(
        out_hard, source, duration, args.fps, args.width, args.height,
        chunks, caption_pngs, disclaimer_png,
        args.disclaimer_start, args.disclaimer_duration, fade_dur=0.0,
    )
    print(f"  → {out_hard}", flush=True)

    if args.also_fade:
        out_soft = out_dir / "minimal_ad_softfade.mp4"
        render_variant(
            out_soft, source, duration, args.fps, args.width, args.height,
            chunks, caption_pngs, disclaimer_png,
            args.disclaimer_start, args.disclaimer_duration, fade_dur=args.fade_dur,
        )
        print(f"  → {out_soft}", flush=True)

    if not args.keep_tmp:
        shutil.rmtree(work, ignore_errors=True)
        print("  (cleaned tmp/)", flush=True)

    print("\nDONE", flush=True)


if __name__ == "__main__":
    main()
