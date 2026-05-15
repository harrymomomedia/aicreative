"""Detect burned-in subtitles/text on Veo-generated clips via tesseract OCR.

Veo sometimes hallucinates burned-in subtitle text mid-clip, ignoring our "no on-screen text"
prompt. This is a known failure mode (CLAUDE.md). Manual frame inspection misses it because
the text appears intermittently. This script:

  1. Samples N frames per clip at evenly-spaced timestamps
  2. Crops out the corner watermark + letterbox bars
  3. OCRs each frame with tesseract
  4. Flags any clip where text-like content is detected (longer than the small "Veo" mark)

Usage:
  .venv/bin/python scripts/scan_burned_text.py outputs/.../clip*.mp4
  .venv/bin/python scripts/scan_burned_text.py --frames 5 --min-chars 4 outputs/.../clip*.mp4

Exit code: 1 if any clip flagged, 0 if all clean.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_frame(mp4, t_sec, out_jpg):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t_sec), "-i", str(mp4), "-frames:v", "1", str(out_jpg)],
        capture_output=True, check=True,
    )


WATERMARK_WORDS = {"veo", "veo3", "fast"}  # ignore corner watermark


def ocr_text(img_path, crop_box=None, min_word_conf=60, min_word_len=3):
    """Run tesseract via stdin (macOS sandbox blocks direct file reads).

    Returns words passing per-word confidence + length filters. Excludes the "Veo"
    watermark string in the bottom-right corner. Pixar character details (eyes, hair,
    mouth) sometimes produce false positives — confidence threshold filters them.
    """
    if crop_box:
        x, y, w, h = crop_box
        # Crop via ffmpeg, output PNG to stdout
        crop_proc = subprocess.run(
            ["ffmpeg", "-y", "-i", str(img_path), "-vf", f"crop={w}:{h}:{x}:{y}",
             "-f", "image2pipe", "-vcodec", "png", "-"],
            capture_output=True, check=True,
        )
        img_bytes = crop_proc.stdout
    else:
        with open(img_path, "rb") as f:
            img_bytes = f.read()

    # PSM 11 = sparse text on busy backgrounds. tsv = per-word confidence.
    r = subprocess.run(
        ["tesseract", "stdin", "-", "--psm", "11", "-l", "eng", "tsv"],
        input=img_bytes, capture_output=True, check=False,
    )
    out = r.stdout.decode("utf-8", errors="ignore")
    words = []
    for line in out.splitlines()[1:]:  # skip header
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        try:
            conf = float(parts[10])
        except ValueError:
            continue
        if conf < 0:  # tesseract uses -1 for line/block/paragraph rows
            continue
        word = parts[11].strip()
        if conf < min_word_conf or len(word) < min_word_len:
            continue
        alpha_count = sum(c.isalpha() for c in word)
        if alpha_count < min_word_len:
            continue
        if word.lower().strip(".,?!:;") in WATERMARK_WORDS:
            continue
        words.append(f"{word}({conf})")
    return " ".join(words)


def get_duration(mp4):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp4)],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def get_dimensions(mp4):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(mp4)],
        capture_output=True, text=True, check=True,
    )
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


def scan_clip(mp4, frames=4, min_chars=4):
    """Sample frames and OCR. Returns list of (timestamp, text) for any frame with text > min_chars."""
    duration = get_duration(mp4)
    width, height = get_dimensions(mp4)
    # Drop only bottom ~50px (Veo watermark area) — keep the entire content area scannable.
    # Burned subtitles can appear ANYWHERE in the frame, including near the bottom of content.
    drop_top = int(height * 0.04)   # ~50px letterbox top
    drop_bottom = int(height * 0.05)  # ~64px watermark/letterbox bottom
    crop_w, crop_h = width, height - drop_top - drop_bottom
    crop_box = (0, drop_top, crop_w, crop_h)

    timestamps = [duration * i / (frames + 1) for i in range(1, frames + 1)]
    findings = []
    with tempfile.TemporaryDirectory() as td:
        for i, t in enumerate(timestamps):
            jpg = Path(td) / f"f{i}.jpg"
            try:
                extract_frame(mp4, t, jpg)
                text = ocr_text(jpg, crop_box=crop_box)
                if len(text) >= min_chars:
                    findings.append((round(t, 2), text))
            except subprocess.CalledProcessError as e:
                print(f"    [warn] failed frame at {t:.1f}s: {e}", file=sys.stderr)
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--frames", type=int, default=4, help="frames sampled per clip")
    ap.add_argument("--min-chars", type=int, default=4, help="minimum text length to flag")
    args = ap.parse_args()

    flagged = []
    for clip in args.clips:
        clip_path = Path(clip)
        if not clip_path.exists():
            print(f"✗ {clip_path.name}: file not found")
            continue
        print(f"scanning {clip_path.name}…")
        findings = scan_clip(clip_path, frames=args.frames, min_chars=args.min_chars)
        if findings:
            print(f"  ✗ FLAGGED — burned text detected:")
            for t, txt in findings:
                print(f"      {t:5.2f}s: {txt!r}")
            flagged.append(clip_path.name)
        else:
            print(f"  ✓ clean (no text in {args.frames} sampled frames)")

    print(f"\n{len(flagged)} clip(s) flagged: {flagged}")
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
