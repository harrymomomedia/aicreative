#!/usr/bin/env python3
"""
Dissect a competitor video into beat-by-beat artifacts.

Usage: python dissect.py <path-to-video> [--model small]

Produces outputs/<videoname>/:
  metadata.json   — duration, fps, resolution, aspect ratio
  scenes.json     — scene-cut timestamps (ffmpeg scene detection)
  frames/         — one jpg per scene boundary (plus 0s)
  audio.wav       — extracted mono 16k audio
  transcript.json — Whisper output with word-level timestamps
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


def transcribe(audio_path, model_name):
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path), word_timestamps=True, verbose=False)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video", help="path to competitor video")
    ap.add_argument("--model", default="small", help="whisper model: tiny|base|small|medium|large")
    ap.add_argument("--scene-threshold", type=float, default=0.3)
    ap.add_argument("--interval", type=float, default=1.5, help="also sample a frame every N seconds (0 to disable)")
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

    print(f"[5/5] whisper ({args.model})", flush=True)
    result = transcribe(audio, args.model)
    (out / "transcript.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"      {len(result.get('segments', []))} segments", flush=True)

    print(f"\nDONE → {out.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
