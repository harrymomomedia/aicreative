#!/usr/bin/env python3
"""Burn ONLY the legal disclaimer (no captions/subtitles) onto a video.

Reuses the SAME render_disclaimer + find_boring_window as caption_hormozi3.py, so the
disclaimer styling (white + black stroke, fontsize_ratio 0.013, vertical 0.99) and the
auto calmest-window placement match the captioned deliverables exactly — the only
difference is there is NO caption track.

Use this for the "disclaimer-only" deliverable (e.g. when the user adds their own captions
in post). For captions-only use caption_hormozi3.py with NO --disclaimer; for the combo use
caption_hormozi3.py --disclaimer.

  .venv/bin/python scripts/burn_disclaimer.py <in.mp4> <out.mp4>
      [--secs 6.0] [--start <sec>] [--text "..."]
"""
import sys, argparse, subprocess, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from scripts.caption_styled import render_disclaimer, find_font, DEFAULT_DISCLAIMER, probe_size
from scripts.caption_hormozi3 import find_boring_window


def burn_disclaimer(src, out, secs=6.0, start=None, text=None):
    text = text or DEFAULT_DISCLAIMER
    w, h = probe_size(src)
    if start is None:
        start, _ = find_boring_window(src, length=secs)   # calmest window, skips hook/CTA
    end = start + secs
    with tempfile.TemporaryDirectory() as td:
        dp = Path(td) / "disc.png"
        render_disclaimer(text, w, h, find_font(), dp, fontsize_ratio=0.013, vertical_pos=0.99)
        cmd = ["ffmpeg", "-y", "-i", str(src), "-i", str(dp),
               "-filter_complex",
               f"[0:v][1:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})':format=auto[out]",
               "-map", "[out]", "-map", "0:a", "-c:a", "copy",
               "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed:\n{r.stderr[-2000:]}")
    print(f"  {Path(out).name}: disclaimer {start:.1f}-{end:.1f}s (calmest window)", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Burn only the legal disclaimer (no captions).")
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--secs", type=float, default=6.0, help="seconds the disclaimer stays up.")
    ap.add_argument("--start", type=float, default=None,
                    help="force start (sec). Default: auto-detect calmest window.")
    ap.add_argument("--text", default=None, help="override disclaimer text (default: Pulaski/Jones).")
    a = ap.parse_args()
    burn_disclaimer(a.video, a.out, secs=a.secs, start=a.start, text=a.text)


if __name__ == "__main__":
    main()
