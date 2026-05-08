#!/usr/bin/env python3
"""
Add TikTok-style burned-in captions to a video.

Usage:
  .venv/bin/python caption.py <input.mp4> [--out output.mp4] [--model small] [--max-words 4]

Pipeline:
  1. Extract audio (ffmpeg)
  2. Whisper word-level transcribe
  3. Chunk words into phrase groups (by max length + natural pauses)
  4. Render each chunk as a transparent PNG with PIL (bold all-caps, white + black outline)
  5. Overlay PNGs onto video with ffmpeg `overlay` filter, timed via `enable=between(t,...)`

Why PIL instead of libass: Homebrew's default ffmpeg lacks libass support, so the
`subtitles` filter is unavailable. PIL + overlay gives the same UGC ad caption look
without that dependency.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent

# Default font: heavy bold display face. Single-file TTFs preferred (no index ambiguity).
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",  # macOS — heaviest, cleanest
    "/Library/Fonts/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Avenir Next.ttc",  # has heavy faces, fallback
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
]

# Common Whisper mistranscriptions of proper nouns we use across ad clones.
# Applied case-insensitively to chunk text before rendering.
SUBSTITUTIONS = {
    "CHOWCHILLY": "CHOWCHILLA",
    "CHOW CHILLER": "CHOWCHILLA",
    "CHOW-CHILLER": "CHOWCHILLA",
    "CHOW CHILLA": "CHOWCHILLA",
    "CHOW-CHILLA": "CHOWCHILLA",
    "CHILLAH": "CHILLA",
    "FALSUM": "FOLSOM",
    "FOLSUM": "FOLSOM",
    "CHEENO": "CHINO",
    "CHEE-NO": "CHINO",
    "REPRESSA": "REPRESA",
    "REPRESSER": "REPRESA",
    "CCWS": "CCWF",
    "VSPS": "VSPW",
    "SIW": "CIW",
}


def apply_substitutions(text):
    """Apply proper-noun fixups. Case-insensitive match, preserves UPPER for output."""
    out = text
    for wrong, right in SUBSTITUTIONS.items():
        # Word-boundary replace, case-insensitive
        import re
        out = re.sub(rf"\b{re.escape(wrong)}\b", right, out, flags=re.IGNORECASE)
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def extract_audio(video, out):
    r = run(["ffmpeg", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", "-vn", str(out)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extract failed:\n{r.stderr}")


def probe_size(video):
    r = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", str(video),
    ])
    s = json.loads(r.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def transcribe(audio, model_name):
    import whisper
    model = whisper.load_model(model_name)
    return model.transcribe(str(audio), word_timestamps=True, verbose=False)


def chunk_words(segments, max_words=4, min_pause=0.35):
    """Group word-level timestamps into caption chunks."""
    chunks = []
    current = []
    last_end = None
    for seg in segments:
        for w in seg.get("words", []):
            text = (w.get("word") or "").strip()
            if not text:
                continue
            start = w["start"]
            end = w["end"]
            if current and (start - last_end > min_pause or len(current) >= max_words):
                chunks.append({
                    "start": current[0]["start"],
                    "end": last_end,
                    "text": " ".join(c["text"] for c in current).upper(),
                })
                current = []
            current.append({"start": start, "end": end, "text": text})
            last_end = end
    if current:
        chunks.append({
            "start": current[0]["start"],
            "end": last_end,
            "text": " ".join(c["text"] for c in current).upper(),
        })
    # Extend each chunk so caption stays slightly past last word
    for c in chunks:
        c["end"] = c["end"] + 0.18
    # Avoid overlap with next chunk
    for i in range(len(chunks) - 1):
        chunks[i]["end"] = min(chunks[i]["end"], chunks[i+1]["start"] - 0.02)
    return chunks


def find_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    raise RuntimeError("no suitable system font found; install Arial Black or Helvetica")


def _wrap_to_lines(text, font, draw, max_w, stroke):
    """Greedy word-wrap. Returns list[str]."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font, stroke_width=stroke)
        if bbox[2] - bbox[0] > max_w and cur:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def render_chunk(text, width, height, font_path, png_path,
                  fontsize_ratio=0.035, outline_ratio=0.0028, marginv_ratio=0.16,
                  max_lines=2):
    """Render one caption chunk as a transparent PNG.
    Adaptive font shrink: if wrap exceeds max_lines, shrink fontsize ~8% and retry."""
    from PIL import Image, ImageDraw, ImageFont

    text = apply_substitutions(text)

    base_fontsize = max(20, int(height * fontsize_ratio))
    marginv = int(height * marginv_ratio)
    max_w = int(width * 0.88)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Adaptive shrink loop — find largest fontsize where wrap fits within max_lines
    fontsize = base_fontsize
    for _ in range(10):
        font = ImageFont.truetype(font_path, fontsize)
        # outline scales with current fontsize so it stays proportional
        outline = max(2, int(fontsize * 0.08))
        lines = _wrap_to_lines(text, font, draw, max_w, outline)
        if len(lines) <= max_lines or fontsize <= 18:
            break
        fontsize = int(fontsize * 0.92)

    # Final pass with the chosen fontsize
    font = ImageFont.truetype(font_path, fontsize)
    outline = max(2, int(fontsize * 0.08))
    lines = _wrap_to_lines(text, font, draw, max_w, outline)

    # Measure each line
    line_heights, line_widths = [], []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=outline)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    line_gap = int(fontsize * 0.08)
    total_h = sum(line_heights) + (len(lines) - 1) * line_gap

    y0 = height - marginv - total_h
    cur_y = y0
    for i, line in enumerate(lines):
        x = (width - line_widths[i]) // 2
        draw.text(
            (x, cur_y), line, font=font,
            fill=(255, 255, 255, 255),
            stroke_width=outline,
            stroke_fill=(0, 0, 0, 255),
        )
        cur_y += line_heights[i] + line_gap

    img.save(png_path)


def burn(video, chunks, work_dir, out):
    """Render each chunk as PNG, then build an overlay filtergraph."""
    font_path = find_font()
    width, height = probe_size(video)

    # Render PNG per chunk
    pngs = []
    for i, c in enumerate(chunks):
        p = work_dir / f"chunk_{i:03d}.png"
        render_chunk(c["text"], width, height, font_path, p)
        pngs.append(p)

    # Build ffmpeg command
    inputs = ["-i", str(video)]
    for p in pngs:
        inputs += ["-i", str(p)]

    # Filter complex: chain overlays, each enabled in its window
    parts = []
    prev = "[0:v]"
    for i, c in enumerate(chunks):
        out_label = f"[v{i}]"
        # Each PNG is input N+1
        parts.append(
            f"{prev}[{i+1}:v]overlay=0:0:enable='between(t,{c['start']:.3f},{c['end']:.3f})'{out_label}"
        )
        prev = out_label
    filtergraph = ";".join(parts)

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filtergraph,
        "-map", prev, "-map", "0:a",
        "-c:a", "copy", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr[-2500:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="small", help="whisper model: tiny|base|small|medium|large")
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--keep-pngs", action="store_true")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        raise SystemExit(f"not found: {video}")
    out = Path(args.out).resolve() if args.out else video.with_name(video.stem + "_captioned.mp4")

    width, height = probe_size(video)
    print(f"video: {video.name}  {width}x{height}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        audio = td / "audio.wav"

        print("[1/4] extracting audio", flush=True)
        extract_audio(video, audio)

        print(f"[2/4] whisper transcribe ({args.model})", flush=True)
        result = transcribe(audio, args.model)

        print("[3/4] chunking words", flush=True)
        chunks = chunk_words(result["segments"], max_words=args.max_words)
        print(f"      {len(chunks)} caption chunks", flush=True)
        for c in chunks[:5]:
            print(f"      {c['start']:5.2f}-{c['end']:5.2f}  {c['text']}", flush=True)
        if len(chunks) > 5:
            print(f"      ... +{len(chunks)-5} more", flush=True)

        print("[4/4] rendering PNGs and burning overlays", flush=True)
        burn(video, chunks, td, out)

        if args.keep_pngs:
            kept_dir = out.with_suffix("") / "captions"
            kept_dir.mkdir(parents=True, exist_ok=True)
            for p in td.glob("chunk_*.png"):
                shutil.copy(p, kept_dir / p.name)
            print(f"      kept PNGs → {kept_dir}", flush=True)

    print(f"\nDONE → {out}", flush=True)


if __name__ == "__main__":
    main()
