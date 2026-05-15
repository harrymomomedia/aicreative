#!/usr/bin/env python3
"""Burn TikTok-style captions with per-word yellow highlight + optional legal disclaimer overlay.

Caption style (matches user's reference UGC ad):
  - ALL CAPS, bold sans-serif (Arial Black), white fill + black stroke
  - Currently-spoken word has a bright YELLOW box highlight; other chunk words plain
  - 2-3 word chunks, position ~70% from top of frame
  - Adaptive font shrink when wrap exceeds max-lines

Disclaimer style:
  - White text + black stroke, smaller font, multi-line, left-justified
  - Bottom 25% of frame
  - Hard cut in/out at specified window (default 0s-5s)

Usage:
  .venv/bin/python scripts/caption_styled.py <in.mp4> [--out out.mp4]
       [--disclaimer-text "Paid legal advertisement..." | --no-disclaimer]
       [--disclaimer-start 0 --disclaimer-end 5]
       [--model small] [--max-words 3]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Arial Black.ttf",
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

# Whisper mistranscription fixups for proper nouns in our scripts
SUBSTITUTIONS = {
    "CHOWCHILLY": "CHOWCHILLA",
    "CHOW CHILLER": "CHOWCHILLA",
    "CHOW-CHILLER": "CHOWCHILLA",
    "CHOW CHILLA": "CHOWCHILLA",
    "CHOW-CHILLA": "CHOWCHILLA",
    "CHILLAH": "CHILLA",
    "MIHA": "MIJA",
    "MEHA": "MIJA",
    "NIHA": "MIJA",
    "MI-HA": "MIJA",
    "MEE-HAH": "MIJA",
}

DEFAULT_DISCLAIMER = (
    "Paid legal advertisement. Jordan M. Jones, Attorney at Law "
    "(360 E 2nd St #820, Los Angeles, CA 90012) and Adam Pulaski, Attorney "
    "at Law (2925 Richmond Ave #1725, Houston, TX 77098) are responsible "
    "for this advertisement. A California-licensed attorney is associated "
    "for CA cases. This ad uses paid actors, dramatizations, and AI-generated "
    "imagery for illustration only and does not depict real clients or events. "
    "No guarantee or prediction of outcome is made. Cases may be referred to "
    "other attorneys."
)

YELLOW = (252, 222, 0, 255)


def apply_subs(text):
    out = text
    for wrong, right in SUBSTITUTIONS.items():
        out = re.sub(rf"\b{re.escape(wrong)}\b", right, out, flags=re.IGNORECASE)
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def extract_audio(video, out):
    r = run(["ffmpeg", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", "-vn", str(out)])
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extract failed:\n{r.stderr}")


def probe_size(video):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "json", str(video)])
    s = json.loads(r.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def transcribe(audio, model_name):
    import whisper
    model = whisper.load_model(model_name)
    return model.transcribe(str(audio), word_timestamps=True, verbose=False)


def find_font():
    for p in FONT_CANDIDATES:
        if Path(p).exists():
            return p
    raise RuntimeError("no suitable font found")


def chunk_words(segments, max_words=3, min_pause=0.35):
    """Group words into caption chunks. Returns list of {start, end, words:[{text,start,end},...]}."""
    chunks = []
    current = []
    last_end = None
    for seg in segments:
        for w in seg.get("words", []):
            text = (w.get("word") or "").strip()
            if not text:
                continue
            text = apply_subs(text.upper())
            start, end = w["start"], w["end"]
            if current and (start - last_end > min_pause or len(current) >= max_words):
                chunks.append({
                    "start": current[0]["start"],
                    "end": last_end,
                    "words": current,
                })
                current = []
            current.append({"text": text, "start": start, "end": end})
            last_end = end
    if current:
        chunks.append({
            "start": current[0]["start"],
            "end": last_end,
            "words": current,
        })
    return chunks


def layout_chunk(words, font, draw, max_w, outline):
    """Word-wrap chunk into lines. Returns [(line_words, line_width), ...] where
    line_words is the list of word dicts on that line."""
    # measure each word
    measured = []
    for w in words:
        bbox = draw.textbbox((0, 0), w["text"], font=font, stroke_width=outline)
        measured.append({**w, "w": bbox[2] - bbox[0], "h": bbox[3] - bbox[1]})
    space_bbox = draw.textbbox((0, 0), " ", font=font, stroke_width=outline)
    space_w = space_bbox[2] - space_bbox[0]

    lines = []
    cur = []
    cur_w = 0
    for m in measured:
        trial = cur_w + (space_w if cur else 0) + m["w"]
        if cur and trial > max_w:
            lines.append((cur, cur_w))
            cur = [m]
            cur_w = m["w"]
        else:
            cur.append(m)
            cur_w = trial
    if cur:
        lines.append((cur, cur_w))
    return lines, space_w


def render_chunk_highlighted(chunk_words, highlight_idx, width, height, font_path, png_path,
                             fontsize_ratio=0.0336, vertical_pos=0.72, max_lines=2,
                             highlight_style="box"):
    """highlight_style: 'box' (yellow rect behind white text) or 'yellow_text' (yellow fill, no rect)."""
    """Render one frame: chunk text with `chunk_words[highlight_idx]` boxed in yellow."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    max_w = int(width * 0.85)

    fontsize = max(20, int(height * fontsize_ratio))
    # Adaptive shrink if wrap > max_lines
    for _ in range(8):
        font = ImageFont.truetype(font_path, fontsize)
        outline = max(2, int(fontsize * 0.09))
        lines, space_w = layout_chunk(chunk_words, font, draw, max_w, outline)
        if len(lines) <= max_lines or fontsize <= 22:
            break
        fontsize = int(fontsize * 0.92)

    # Final layout
    font = ImageFont.truetype(font_path, fontsize)
    outline = max(2, int(fontsize * 0.09))
    lines, space_w = layout_chunk(chunk_words, font, draw, max_w, outline)

    line_h = int(fontsize * 1.15)
    line_gap = int(fontsize * 0.08)
    total_h = len(lines) * line_h + (len(lines) - 1) * line_gap
    y0 = int(height * vertical_pos) - total_h // 2

    # Walk layout. For the highlighted word we draw a yellow rectangle FIT to the actual
    # glyph bounding box (textbbox), not the line-height box. line_h includes leading
    # which makes the rectangle hang below the text — using textbbox fixes that.
    word_counter = 0
    cur_y = y0
    for line_words, line_w in lines:
        x = (width - line_w) // 2
        for m in line_words:
            is_hi = (word_counter == highlight_idx)
            if is_hi and highlight_style == "box":
                # True bounding box of where this word's glyphs will render at (x, cur_y)
                wb = draw.textbbox((x, cur_y), m["text"], font=font, stroke_width=outline)
                pad_x = max(4, int(fontsize * 0.10))
                pad_y = max(3, int(fontsize * 0.08))
                draw.rectangle(
                    [wb[0] - pad_x, wb[1] - pad_y, wb[2] + pad_x, wb[3] + pad_y],
                    fill=YELLOW,
                )
            # Draw the word text. Yellow fill if yellow_text mode + highlighted; else white.
            text_fill = YELLOW if (is_hi and highlight_style == "yellow_text") else (255, 255, 255, 255)
            draw.text((x, cur_y), m["text"], font=font,
                      fill=text_fill,
                      stroke_width=outline,
                      stroke_fill=(0, 0, 0, 255))
            x += m["w"] + space_w
            word_counter += 1
        cur_y += line_h + line_gap

    img.save(png_path)


def render_disclaimer(text, width, height, font_path, png_path,
                      fontsize_ratio=0.013, vertical_pos=0.99):
    """Render the legal disclaimer PNG — multi-line white text + black stroke, bottom of frame."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    fontsize = max(14, int(height * fontsize_ratio))
    font = ImageFont.truetype(font_path, fontsize)
    outline = max(1, int(fontsize * 0.08))
    max_w = int(width * 0.94)

    # Word-wrap
    words = text.split()
    lines = []
    cur = []
    for w in words:
        trial = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), trial, font=font, stroke_width=outline)
        if cur and (bbox[2] - bbox[0]) > max_w:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))

    line_h = int(fontsize * 1.25)
    total_h = len(lines) * line_h
    # Position: anchor at vertical_pos as the BOTTOM of the text block
    y0 = int(height * vertical_pos) - total_h

    cur_y = y0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=outline)
        line_w = bbox[2] - bbox[0]
        x = (width - line_w) // 2
        draw.text((x, cur_y), line, font=font,
                  fill=(255, 255, 255, 255),
                  stroke_width=outline,
                  stroke_fill=(0, 0, 0, 255))
        cur_y += line_h
    img.save(png_path)


def auto_vertical_pos(width, height):
    """Caption Y position depends on aspect ratio because the subject's chin sits at
    different relative heights:
      - 9:16 / 3:5 (taller frames): chin around 65%, captions at 0.72 just below.
      - 4:5 (squarer): chin around 73%, captions at 0.82 to stay below.
      - 16:9 (wider): captions sit even lower.
    Linear interpolation between known-good anchors; clamped to [0.70, 0.85]."""
    aspect = width / height
    pos = 0.72 + (aspect - 0.6) * 0.5  # 0.6→0.72, 0.8→0.82
    return max(0.70, min(0.85, pos))


def burn(video, chunks, work_dir, out, disclaimer_text=None,
         disclaimer_start=0.0, disclaimer_end=5.0, highlight_style="box",
         vertical_pos=None, fontsize_ratio=0.0336):
    font_path = find_font()
    width, height = probe_size(video)
    if vertical_pos is None:
        vertical_pos = auto_vertical_pos(width, height)
    print(f"      vertical_pos={vertical_pos:.3f} (aspect {width/height:.3f})", flush=True)

    # 1. Render per-word PNGs for each chunk
    word_pngs = []  # [(png_path, word_start, word_end), ...]
    for ci, chunk in enumerate(chunks):
        for wi, w in enumerate(chunk["words"]):
            png = work_dir / f"chunk_{ci:03d}_w{wi:02d}.png"
            render_chunk_highlighted(chunk["words"], wi, width, height, font_path, png,
                                     highlight_style=highlight_style,
                                     vertical_pos=vertical_pos,
                                     fontsize_ratio=fontsize_ratio)
            word_pngs.append((png, w["start"], w["end"]))
    # Each highlight PNG stays up only for the duration of its specific word.
    # Adjacent word frames replace each other immediately. After the last word of a
    # chunk, the caption disappears until the next chunk's first word.

    # 2. Optional disclaimer PNG
    disclaimer_png = None
    if disclaimer_text:
        disclaimer_png = work_dir / "disclaimer.png"
        render_disclaimer(disclaimer_text, width, height, font_path, disclaimer_png)

    # 3. Build ffmpeg command. Layer order: BG video → disclaimer (under) → captions (on top).
    inputs = ["-i", str(video)]
    # Disclaimer goes BEFORE word pngs in inputs so it overlays FIRST.
    disclaimer_input_idx = None
    if disclaimer_png:
        inputs += ["-i", str(disclaimer_png)]
        disclaimer_input_idx = 1  # input 1, since video is input 0
    word_png_start_idx = (2 if disclaimer_input_idx else 1)
    for p, _, _ in word_pngs:
        inputs += ["-i", str(p)]

    parts = []
    prev = "[0:v]"
    if disclaimer_png:
        label = "[vd]"
        parts.append(
            f"{prev}[{disclaimer_input_idx}:v]overlay=0:0:enable='between(t,{disclaimer_start:.3f},{disclaimer_end:.3f})'{label}"
        )
        prev = label
    for i, (png, start, end) in enumerate(word_pngs):
        input_idx = word_png_start_idx + i
        label = f"[v{i+1}]"
        parts.append(
            f"{prev}[{input_idx}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{label}"
        )
        prev = label

    filtergraph = ";".join(parts) if parts else None
    cmd = ["ffmpeg", "-y", *inputs]
    if filtergraph:
        cmd += ["-filter_complex", filtergraph, "-map", prev]
    cmd += ["-map", "0:a",
            "-c:a", "copy", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            str(out)]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg overlay failed:\n{r.stderr[-3000:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="small")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--no-disclaimer", action="store_true")
    ap.add_argument("--disclaimer-text", default=DEFAULT_DISCLAIMER)
    ap.add_argument("--disclaimer-start", type=float, default=7.0,
                    help="seconds when disclaimer hard-cuts IN")
    ap.add_argument("--disclaimer-end", type=float, default=12.0,
                    help="seconds when disclaimer hard-cuts OUT")
    ap.add_argument("--highlight-style", choices=["box", "yellow_text"], default="box",
                    help="'box' = yellow rect behind white text (default); 'yellow_text' = yellow text fill, no rect")
    ap.add_argument("--vertical-pos", type=float, default=None,
                    help="Caption Y position (0-1, fraction of frame height). Default: auto by aspect ratio (0.72 for 9:16, 0.82 for 4:5).")
    ap.add_argument("--font-ratio", type=float, default=0.04,
                    help="Caption font size as fraction of frame height. Default 0.04 (~4%%, campaign-approved 2026-05-12).")
    args = ap.parse_args()

    video = Path(args.video).resolve()
    if not video.exists():
        sys.exit(f"not found: {video}")
    out = Path(args.out).resolve() if args.out else video.with_name(video.stem + "_styled.mp4")

    width, height = probe_size(video)
    print(f"video: {video.name}  {width}x{height}", flush=True)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        audio = td / "audio.wav"
        print("[1/4] extract audio", flush=True)
        extract_audio(video, audio)

        print(f"[2/4] whisper ({args.model})", flush=True)
        result = transcribe(audio, args.model)

        print("[3/4] chunking", flush=True)
        chunks = chunk_words(result["segments"], max_words=args.max_words)
        n_words = sum(len(c["words"]) for c in chunks)
        print(f"      {len(chunks)} chunks, {n_words} words total", flush=True)

        print("[4/4] render PNGs and burn", flush=True)
        burn(
            video, chunks, td, out,
            disclaimer_text=None if args.no_disclaimer else args.disclaimer_text,
            disclaimer_start=args.disclaimer_start,
            disclaimer_end=args.disclaimer_end,
            highlight_style=args.highlight_style,
            vertical_pos=args.vertical_pos,
            fontsize_ratio=args.font_ratio,
        )

    print(f"\nDONE → {out}", flush=True)


if __name__ == "__main__":
    main()
