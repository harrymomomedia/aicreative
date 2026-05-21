#!/usr/bin/env python3
"""
Dissect a competitor / generated video into beat-by-beat artifacts.

Usage: python dissect.py <path-to-video> [--biased-keywords Chowchilla Mija] [--no-ocr]

Produces outputs/<videoname>/:
  metadata.json    — duration, fps, resolution, aspect ratio
  scenes.json      — scene-cut timestamps (ffmpeg scene detection)
  frames/          — one jpg per scene boundary + every --interval seconds
  audio.wav        — extracted mono 16k audio
  transcript.json  — ElevenLabs Scribe output with word-level timestamps
  burned_text.json — tesseract OCR per-frame, flagging Veo-hallucinated subtitles

Transcription is API-based (ElevenLabs Scribe) — needs ELEVENLABS_API_KEY set.
OCR step requires tesseract on PATH. Skip with --no-ocr.

Scribe catches what was SAID. OCR catches what was burned ON the frame —
specifically, Veo's habit of hallucinating subtitle text despite "no on-screen text"
prompts. A clip is FLAGGED if any frame has 2+ words at confidence >= 60 outside the
"Veo" watermark, OR a single word repeats across 2+ frames (stable text = real burn-in).
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"


def run(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True)


def probe(video):
    r = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(video),
    ])
    data = json.loads(r.stdout)
    v = next(s for s in data["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    fps = num / den if den else 0
    w, h = int(v["width"]), int(v["height"])
    return {
        "duration_s": float(data["format"]["duration"]),
        "fps": round(fps, 3),
        "width": w,
        "height": h,
        "aspect_ratio": f"{w}:{h}",
        "codec": v.get("codec_name"),
    }


def detect_scenes(video, threshold=0.3):
    r = run([
        "ffmpeg", "-i", str(video),
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-",
    ])
    times = []
    for line in r.stderr.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m and "showinfo" in line:
            times.append(float(m.group(1)))
    return sorted(set(round(t, 3) for t in times))


def extract_frames(video, times, frames_dir):
    frames_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i, t in enumerate(times):
        out = frames_dir / f"scene_{i:02d}_at_{t:.2f}s.jpg"
        run([
            "ffmpeg", "-y", "-ss", f"{t}", "-i", str(video),
            "-frames:v", "1", "-q:v", "2", str(out),
        ])
        saved.append(str(out.relative_to(ROOT)))
    return saved


def extract_audio(video, audio_path):
    run([
        "ffmpeg", "-y", "-i", str(video),
        "-ac", "1", "-ar", "16000", "-vn", str(audio_path),
    ])


def transcribe(audio_path, biased_keywords=None, language="en"):
    """Transcribe via ElevenLabs Scribe (speech-to-text API).

    Returns Whisper-compatible JSON: {text, segments:[{words:[{start,end,word}]}], language}.
    biased_keywords: proper nouns to bias toward, e.g. ['Chowchilla', 'Mija'] — sharply
    improves proper-noun accuracy on legal/place-name-heavy ads.

    Backend routing: prefer fal.ai (FAL_KEY) if set, else direct ElevenLabs
    (ELEVENLABS_API_KEY). Both expose the same scribe_whisper_compat contract.
    Lazy import so probe/frames/OCR still run without any key.
    """
    from dotenv import load_dotenv
    load_dotenv()
    if os.getenv("FAL_KEY"):
        from fal_client import scribe_whisper_compat
    else:
        from elevenlabs_client import scribe_whisper_compat
    return scribe_whisper_compat(str(audio_path), biased_keywords=biased_keywords,
                                 language_code=language)


# ─── Burned-in text detection (OCR) ─────────────────────────────────────────────

WATERMARK_WORDS = {"veo", "veo3", "fast"}  # bottom-right corner watermark — ignore


def _ocr_frame(jpg_path, drop_top_pct=0.04, drop_bottom_pct=0.05):
    """Run tesseract via stdin (macOS sandbox blocks file reads).

    Crops out the top letterbox + bottom watermark band before OCR. Returns a list
    of (word, confidence) tuples. Filters out the "Veo" watermark and very-low-conf noise.
    """
    # Get frame dimensions
    probe_r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", str(jpg_path)],
        capture_output=True, text=True,
    )
    if probe_r.returncode != 0:
        return []
    w, h = (int(x) for x in probe_r.stdout.strip().split("x"))
    drop_top = int(h * drop_top_pct)
    drop_bottom = int(h * drop_bottom_pct)
    crop_h = h - drop_top - drop_bottom
    # Crop and pipe to tesseract
    crop = subprocess.run(
        ["ffmpeg", "-y", "-i", str(jpg_path), "-vf", f"crop={w}:{crop_h}:0:{drop_top}",
         "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True,
    )
    if crop.returncode != 0:
        return []
    ocr = subprocess.run(
        ["tesseract", "stdin", "-", "--psm", "11", "-l", "eng", "tsv"],
        input=crop.stdout, capture_output=True,
    )
    if ocr.returncode != 0:
        return []
    words = []
    for line in ocr.stdout.decode("utf-8", errors="ignore").splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 12:
            continue
        try:
            conf = float(parts[10])
        except ValueError:
            continue
        if conf < 60:
            continue
        word = parts[11].strip()
        if len(word) < 3:
            continue
        if sum(c.isalpha() for c in word) < 3:
            continue
        if word.lower().strip(".,?!:;\"'") in WATERMARK_WORDS:
            continue
        words.append((word, round(conf, 1)))
    return words


def scan_frames_for_burned_text(frames_dir):
    """Run OCR on every saved frame. Return {flagged: bool, frames: [...], reason: str}.

    Flagging logic:
      - Frame has 2+ words → likely a real burned subtitle line  → flag
      - Same word appears in 2+ different frames → stable text = real burn-in → flag
      - Single one-off word in one frame → could be Pixar feature noise → not flagged
        (the visual scan / re-roll budget catches these manually)
    """
    if not frames_dir.exists():
        return {"flagged": False, "frames": [], "reason": "no frames"}
    per_frame = []
    word_frame_count = {}  # word -> list of frame paths it appeared in
    for jpg in sorted(frames_dir.glob("*.jpg")):
        words = _ocr_frame(jpg)
        per_frame.append({
            "frame": jpg.name,
            "words": [{"text": w, "conf": c} for w, c in words],
        })
        for w, _ in words:
            wl = w.lower().strip(".,?!:;\"'")
            word_frame_count.setdefault(wl, []).append(jpg.name)

    reasons = []
    # Multi-word frames
    multiword = [f for f in per_frame if len(f["words"]) >= 2]
    if multiword:
        reasons.append(f"{len(multiword)} frame(s) with 2+ words")
    # Stable repeated words across frames
    repeated = {w: fs for w, fs in word_frame_count.items() if len(fs) >= 2}
    if repeated:
        sample = ", ".join(f"{w!r}×{len(fs)}" for w, fs in list(repeated.items())[:3])
        reasons.append(f"repeated word(s): {sample}")

    return {
        "flagged": bool(reasons),
        "reason": "; ".join(reasons) if reasons else "clean",
        "frames": per_frame,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", help="path to competitor video")
    ap.add_argument("--biased-keywords", nargs="+", default=None,
                    help="proper nouns to bias Scribe toward, e.g. --biased-keywords Chowchilla Mija")
    ap.add_argument("--language", default="en", help="ISO-639-1 language code for Scribe (default en)")
    ap.add_argument("--scene-threshold", type=float, default=0.3)
    ap.add_argument("--interval", type=float, default=1.0, help="sample a frame every N seconds via ffmpeg (default 1.0; 0 to disable)")
    ap.add_argument("--no-ocr", action="store_true", help="skip burned-text OCR step (faster, but won't catch Veo subtitle hallucinations)")
    args = ap.parse_args()

    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        sys.exit(f"not found: {video}")

    name = video.stem
    out = OUTPUTS / name
    out.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] probe", flush=True)
    meta = probe(video)
    (out / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"      {meta['duration_s']:.2f}s  {meta['width']}x{meta['height']}  {meta['fps']} fps", flush=True)

    print(f"[2/5] scene detection (threshold={args.scene_threshold})", flush=True)
    cuts = detect_scenes(video, args.scene_threshold)
    times = [0.0] + cuts
    if args.interval > 0:
        t = args.interval
        while t < meta["duration_s"]:
            if all(abs(t - x) > 0.5 for x in times):
                times.append(t)
            t += args.interval
        times = sorted(times)
    (out / "scenes.json").write_text(json.dumps({"cuts": cuts, "extracted_at": times}, indent=2))
    print(f"      {len(cuts)} cuts, {len(times)} frames total", flush=True)

    print(f"[3/5] extract frames", flush=True)
    extract_frames(video, times, out / "frames")

    print(f"[4/5] extract audio", flush=True)
    audio = out / "audio.wav"
    extract_audio(video, audio)

    n_steps = 5 if args.no_ocr else 6
    print(f"[5/{n_steps}] transcribe — ElevenLabs Scribe", flush=True)
    result = transcribe(audio, biased_keywords=args.biased_keywords, language=args.language)
    (out / "transcript.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    n_words = sum(len(s.get("words", [])) for s in result.get("segments", []))
    print(f"      {len(result.get('segments', []))} segments, {n_words} words", flush=True)

    if not args.no_ocr:
        print(f"[6/6] burned-text OCR (tesseract)", flush=True)
        try:
            burned = scan_frames_for_burned_text(out / "frames")
            (out / "burned_text.json").write_text(json.dumps(burned, indent=2))
            marker = "✗ FLAGGED" if burned["flagged"] else "✓ clean"
            print(f"      {marker} — {burned['reason']}", flush=True)
        except FileNotFoundError:
            print(f"      [skipped] tesseract not installed (brew install tesseract)", flush=True)

    print(f"\nDONE → {out.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
