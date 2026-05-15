#!/usr/bin/env python3
"""Convert a tall/portrait video (9:16, 3:5, etc.) to 4:5 with letterbox auto-detection.

Veo outputs at 720x1280 with ~64-100px black letterbox bars baked in. Naive cropping
to 4:5 keeps those bars in the result. This script:

  1. Runs `ffmpeg cropdetect` to find the actual non-black content region
  2. Computes the largest 4:5 crop window that fits inside the content area,
     biased toward the TOP (keeps face / upper body, drops couch / floor)
  3. Crops + re-encodes

Usage:
  .venv/bin/python scripts/crop_4x5.py <in.mp4> [--out out.mp4]
  .venv/bin/python scripts/crop_4x5.py <in.mp4> --bias center    # center crop instead of top
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def probe_dims(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(video)],
        capture_output=True, text=True, check=True,
    )
    w, h = (int(x) for x in r.stdout.strip().split("x"))
    return w, h


def detect_content_region(video):
    """Run cropdetect on ~3s of the middle of the video. Returns (x, y, w, h) of content."""
    # Sample 100 frames starting at 2s in (skip any intro fade)
    r = subprocess.run(
        ["ffmpeg", "-ss", "2", "-i", str(video),
         "-vf", "cropdetect=24:2:0", "-frames:v", "100", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    # Get the last reported crop= value (stable after warm-up)
    crops = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", r.stderr)
    if not crops:
        return None
    cw, ch, cx, cy = (int(v) for v in crops[-1])
    return cx, cy, cw, ch


def detect_face_y(video, sample_time=2.5):
    """Detect face on a sampled frame; return (face_top_y, face_bottom_y) in source pixels.
    Returns None if no face found. Uses OpenCV Haar cascade (no model download needed).
    """
    try:
        import cv2
    except ImportError:
        return None
    tmp = "/tmp/_crop_4x5_face.jpg"
    subprocess.run(["ffmpeg", "-y", "-ss", str(sample_time), "-i", str(video),
                    "-frames:v", "1", "-q:v", "2", tmp], capture_output=True, check=True)
    img = cv2.imread(tmp)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, 1.1, 5)
    if len(faces) == 0:
        return None
    # Largest face by area
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return y, y + h


def compute_4x5_crop(src_w, src_h, content_x, content_y, content_w, content_h,
                     bias="top", face_y_range=None):
    """Compute the largest 4:5 (w/h = 0.8) crop window inside the content region.

    Bias controls where the crop sits within the content area when the content is
    taller than the target 4:5:
      'top'    — anchor at top of content (keeps face, drops floor)
      'center' — center vertically (balanced)
      'bottom' — anchor at bottom (keeps floor, drops headroom — rare)
      'golden' — anchor face so eyes land at ~38% from top of output (rule of thirds /
                 golden-third composition). Requires face_y_range from detect_face_y().
                 Falls back to 'top' if face not provided.
    """
    # Target aspect 4:5 means height = width * 5/4 = width / 0.8
    # We want the LARGEST 4:5 window inside (content_w × content_h).
    # If content_w / content_h <= 0.8: content is wider than 4:5 → use full height, narrower width
    # If content_w / content_h >  0.8: content is taller than 4:5 → use full width, shorter height
    ratio = content_w / content_h
    if ratio <= 0.8:
        # Use full content width, shrink height
        crop_w = content_w
        crop_h = int(crop_w / 0.8)
        crop_x = content_x
        # Vertical bias
        if bias == "top":
            crop_y = content_y
        elif bias == "bottom":
            crop_y = content_y + content_h - crop_h
        elif bias == "golden" and face_y_range is not None:
            # Anchor face so eyes (~38% down from face top) land at 38% of output height
            face_top, face_bot = face_y_range
            eyes_y = face_top + int((face_bot - face_top) * 0.38)
            target_output_eyes_y = int(crop_h * 0.38)
            crop_y = eyes_y - target_output_eyes_y
            # Clamp to content bounds
            crop_y = max(content_y, min(crop_y, content_y + content_h - crop_h))
        elif bias == "golden":
            # Fallback when face detection failed: shift down ~10% from top
            # (works for upper-body talking-head selfies where face is in upper third)
            crop_y = content_y + int(content_h * 0.10)
            crop_y = min(crop_y, content_y + content_h - crop_h)
        else:  # center
            crop_y = content_y + (content_h - crop_h) // 2
    else:
        # Use full content height, shrink width
        crop_h = content_h
        crop_w = int(crop_h * 0.8)
        crop_y = content_y
        crop_x = content_x + (content_w - crop_w) // 2  # always center horizontally

    # Make even (h264 requires even dimensions)
    crop_w = (crop_w // 2) * 2
    crop_h = (crop_h // 2) * 2
    return crop_x, crop_y, crop_w, crop_h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--bias", choices=["top", "center", "bottom", "golden"], default="golden",
                    help="Vertical bias. 'golden' = eyes on upper-third (rule of thirds, default). "
                         "'top' = anchor at top, 'center' = balanced, 'bottom' = rare.")
    args = ap.parse_args()

    src = Path(args.video).resolve()
    if not src.exists():
        sys.exit(f"not found: {src}")
    out = Path(args.out).resolve() if args.out else src.with_name(src.stem + "_4x5.mp4")

    src_w, src_h = probe_dims(src)
    print(f"input:  {src.name}  {src_w}x{src_h}  (ratio {src_w/src_h:.3f})", flush=True)

    region = detect_content_region(src)
    if region is None:
        print("  [warn] cropdetect found no crop — using full frame", flush=True)
        region = (0, 0, src_w, src_h)
    cx, cy, cw, ch = region
    print(f"content: x={cx} y={cy} w={cw} h={ch}  (ratio {cw/ch:.3f})", flush=True)

    face_y_range = None
    if args.bias == "golden":
        face_y_range = detect_face_y(src)
        if face_y_range:
            print(f"face: y_top={face_y_range[0]} y_bot={face_y_range[1]}", flush=True)
        else:
            print("face: NOT DETECTED — falling back to fixed offset", flush=True)

    fx, fy, fw, fh = compute_4x5_crop(src_w, src_h, cx, cy, cw, ch,
                                       bias=args.bias, face_y_range=face_y_range)
    print(f"4:5 crop: x={fx} y={fy} w={fw} h={fh}  (ratio {fw/fh:.3f}, bias={args.bias})", flush=True)

    subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"crop={fw}:{fh}:{fx}:{fy}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "copy",
        str(out),
    ], check=True)
    print(f"\nDONE → {out}", flush=True)


if __name__ == "__main__":
    main()
