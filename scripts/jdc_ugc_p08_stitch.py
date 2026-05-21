"""End-to-end stitch: trim → loudnorm → concat → 4:5 crop.

Sources (all Lite 720p):
  clip 1   : p08_clip1_lite720.mp4
  clip 2a  : p08_clip2a_lite720.mp4  (ends with "Just found out" — overlap)
  clip 2b  : p08_clip2b_lite720.mp4  (starts with "Just found out" — overlap)
  clip 3   : p08_clip3_lite720.mp4
  clip 4   : p08_clip4_lite720.mp4

Per-clip processing:
  1. Whisper-medium → get first-word start + last-word end times
  2. Trim each clip to [first-0.15s, last+0.20s]
     SPECIAL clip 2b: trim from end of overlap phrase "Just found out" (so
     stitched audio = clip 2a's full delivery + clip 2b's continuation,
     dropping the duplicate "Just found out").
  3. Loudnorm each to -16 LUFS broadcast standard
  4. Concat all 5 trimmed+normalized clips losslessly

Output:
  outputs/illinois_jdc_ugc/final.mp4         (9:16, 720x1280)
  outputs/illinois_jdc_ugc/final_4x5.mp4     (4:5 crop via crop_4x5.py)
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat

OUT_DIR = Path("outputs/illinois_jdc_ugc")
CLIPS_DIR = OUT_DIR / "clips"
TRIM_DIR = OUT_DIR / "trimmed"
TRIM_DIR.mkdir(parents=True, exist_ok=True)

# Order matters — clip 2b drops its leading "Just found out" overlap
CLIPS = [
    {"name": "clip1",  "src": CLIPS_DIR / "p08_clip1_lite720.mp4",  "overlap_trim_start": None},
    {"name": "clip2a", "src": CLIPS_DIR / "p08_clip2a_lite720.mp4", "overlap_trim_start": None},
    {"name": "clip2b", "src": CLIPS_DIR / "p08_clip2b_lite720.mp4", "overlap_trim_start": ["Just", "found", "out"]},
    {"name": "clip3",  "src": CLIPS_DIR / "p08_clip3_lite720.mp4",  "overlap_trim_start": None},
    {"name": "clip4",  "src": CLIPS_DIR / "p08_clip4_lite720.mp4",  "overlap_trim_start": None},
]

LEAD_PAD = 0.10
TAIL_PAD = 0.20

FINAL = OUT_DIR / "final.mp4"
FINAL_4X5 = OUT_DIR / "final_4x5.mp4"


def get_speech_window(video, overlap_trim_start):
    r = scribe_whisper_compat(str(video), language_code="en")
    words = []
    for s in r["segments"]:
        for w in s.get("words", []):
            words.append((w["start"], w["end"], w["word"].strip().lower().rstrip(".,!?")))
    if not words:
        return None, None
    first = words[0][0]
    last = words[-1][1]

    # If this clip has a leading-overlap phrase to drop, find where it ENDS in the audio
    if overlap_trim_start:
        # Find sequential match of the overlap words at the start
        target = [w.lower() for w in overlap_trim_start]
        for i in range(len(words) - len(target) + 1):
            window = [words[i + j][2] for j in range(len(target))]
            if all(w == t for w, t in zip(window, target)):
                # Overlap ends after this match — start trim after the matched window
                first = words[i + len(target) - 1][1]  # end time of last matched word
                print(f"  overlap '{' '.join(target)}' detected at words [{i}:{i+len(target)}] — "
                      f"trim start moves to {first:.2f}s", flush=True)
                break

    return first, last


def get_duration(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def trim_and_normalize(src, dst, start, end):
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-ss", f"{start:.3f}",
        "-to", f"{end:.3f}",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(dst),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  TRIM/NORM FAILED: {r.stderr[-400:]}", flush=True)
        return False
    return True


def main():
    print("\n=== TRIM + NORMALIZE PASS ===")
    trimmed_paths = []
    for clip in CLIPS:
        src = clip["src"]
        if not src.exists():
            print(f"\n[{clip['name']}] MISSING: {src} — skipping", flush=True)
            continue
        dur = get_duration(src)
        print(f"\n[{clip['name']}] {src.name} (dur {dur:.2f}s)", flush=True)
        first, last = get_speech_window(src, clip.get("overlap_trim_start"))
        if first is None:
            print(f"  No speech — copying as-is", flush=True)
            dst = TRIM_DIR / f"{clip['name']}.mp4"
            subprocess.run(["cp", str(src), str(dst)], check=True)
            trimmed_paths.append(dst)
            continue
        start = max(0.0, first - LEAD_PAD)
        end = min(dur, last + TAIL_PAD)
        dst = TRIM_DIR / f"{clip['name']}.mp4"
        print(f"  trim [{start:.2f}-{end:.2f}s] + loudnorm -16 LUFS → {dst.name}", flush=True)
        if trim_and_normalize(src, dst, start, end):
            new_dur = get_duration(dst)
            print(f"  trimmed dur: {new_dur:.2f}s", flush=True)
            trimmed_paths.append(dst)

    print("\n=== CONCAT ===")
    concat_list = TRIM_DIR / "concat.txt"
    concat_list.write_text("".join(f"file '{p.absolute()}'\n" for p in trimmed_paths))
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(FINAL),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"CONCAT FAILED: {r.stderr[-500:]}", flush=True)
        return
    final_dur = get_duration(FINAL)
    print(f"\nDONE → {FINAL}  ({final_dur:.2f}s)", flush=True)

    # 4:5 crop variant via crop_4x5.py
    print(f"\n=== 4:5 CROP ===")
    cmd45 = [".venv/bin/python", "scripts/crop_4x5.py", str(FINAL), "--out", str(FINAL_4X5)]
    r = subprocess.run(cmd45, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"DONE → {FINAL_4X5}", flush=True)
    else:
        print(f"crop_4x5 failed: {r.stderr[-300:]}", flush=True)


if __name__ == "__main__":
    main()
