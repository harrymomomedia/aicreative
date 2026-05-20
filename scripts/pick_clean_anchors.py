"""Pick EYES-OPEN, frontal-face anchor frames from a clip (for clip-1 rotation anchors).

The naive 'extract at fixed timestamps' approach catches mid-blink frames (eyes closed),
which seed bad clips (closed/averted eyes, drifted eye color). This samples densely, keeps
only frames where a frontal face + TWO open eyes are detected (Haar cascades), and picks N
well-spaced winners.

Usage:
  .venv/bin/python scripts/pick_clean_anchors.py <clip.mp4> --out-dir <dir> --n 6 --prefix _anchor
"""
import argparse, pathlib, subprocess, sys, tempfile

import cv2


def probe_dur(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(v)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def eyes_open_score(img):
    """Return (has_face_and_2_eyes, face_area). Uses Haar frontal-face + eye cascades."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fcasc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    ecasc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    faces = fcasc.detectMultiScale(gray, 1.1, 5, minSize=(120, 120))
    if len(faces) == 0:
        return False, 0
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    roi = gray[y:y + int(h * 0.6), x:x + w]  # upper 60% of face = eye region
    eyes = ecasc.detectMultiScale(roi, 1.1, 6, minSize=(25, 25))
    return (len(eyes) >= 2), w * h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--prefix", default="_anchor")
    ap.add_argument("--step", type=float, default=0.15, help="sample interval (s)")
    args = ap.parse_args()

    clip = pathlib.Path(args.clip)
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dur = probe_dur(clip)

    # Sample candidate timestamps, keep eyes-open ones.
    candidates = []
    t = 0.3
    with tempfile.TemporaryDirectory() as td:
        while t < dur - 0.2:
            f = f"{td}/f.jpg"
            subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(clip),
                            "-frames:v", "1", "-q:v", "2", f], capture_output=True)
            img = cv2.imread(f)
            if img is not None:
                ok, area = eyes_open_score(img)
                if ok:
                    candidates.append((t, area))
            t += args.step

    if not candidates:
        print("WARN: no eyes-open frames found; falling back to fixed timestamps", flush=True)
        candidates = [(x, 0) for x in [0.5, 1.8, 3.0, 4.2, 5.5, 6.8] if x < dur]

    # Pick N well-spaced timestamps across the eyes-open candidates.
    times = [c[0] for c in candidates]
    n = min(args.n, len(times))
    picks = [times[round(i * (len(times) - 1) / max(1, n - 1))] for i in range(n)]
    # de-dup while preserving order
    seen = set()
    picks = [p for p in picks if not (p in seen or seen.add(p))]

    saved = []
    for i, tt in enumerate(picks):
        out = out_dir / f"{args.prefix}_{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{tt:.2f}", "-i", str(clip),
                        "-frames:v", "1", "-q:v", "2", str(out)], capture_output=True, check=True)
        saved.append((i, round(tt, 2), str(out)))
    print(f"eyes-open candidates: {len(candidates)} | picked {len(saved)}", flush=True)
    for i, tt, p in saved:
        print(f"  {args.prefix}_{i}  t={tt}s  {p}", flush=True)


if __name__ == "__main__":
    main()
