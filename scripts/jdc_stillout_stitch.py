"""Ad 3 (He's Still Out There) stitch — trim → loudnorm -16 → concat → 4:5.

3 clips, no overlap-trim needed. ElevenLabs Scribe for speech-window trim.

Output:
  outputs/illinois_jdc_stillout_p02/final.mp4       (9:16)
  outputs/illinois_jdc_stillout_p02/final_4x5.mp4   (4:5)
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat

OUT_DIR = Path("outputs/illinois_jdc_stillout_p02")
TRIM_DIR = OUT_DIR / "trimmed"
TRIM_DIR.mkdir(parents=True, exist_ok=True)

CLIPS = [OUT_DIR / "clip1.mp4", OUT_DIR / "clip2.mp4", OUT_DIR / "clip3.mp4"]
LEAD_PAD = 0.10
TAIL_PAD = 0.22
FINAL = OUT_DIR / "final.mp4"
FINAL_4X5 = OUT_DIR / "final_4x5.mp4"


def speech_window(video):
    r = scribe_whisper_compat(str(video), language_code="en")
    words = [w for s in r["segments"] for w in s.get("words", [])]
    if not words:
        return None, None
    return words[0]["start"], words[-1]["end"]


def get_duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def trim_norm(src, dst, start, end):
    cmd = ["ffmpeg", "-y", "-i", str(src), "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
           "-c:v", "libx264", "-preset", "fast", "-crf", "19",
           "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(dst)]
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def main():
    print("=== TRIM + NORMALIZE ===")
    trimmed = []
    for i, src in enumerate(CLIPS, 1):
        dur = get_duration(src)
        first, last = speech_window(src)
        start = max(0.0, first - LEAD_PAD)
        end = min(dur, last + TAIL_PAD)
        dst = TRIM_DIR / f"clip{i}.mp4"
        print(f"[clip{i}] trim [{start:.2f}-{end:.2f}s] + loudnorm", flush=True)
        if trim_norm(src, dst, start, end):
            trimmed.append(dst)
            print(f"  → {get_duration(dst):.2f}s", flush=True)

    print("\n=== CONCAT ===")
    cl = TRIM_DIR / "concat.txt"
    cl.write_text("".join(f"file '{p.absolute()}'\n" for p in trimmed))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
                    "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                    "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(FINAL)],
                   capture_output=True, text=True)
    print(f"DONE → {FINAL} ({get_duration(FINAL):.2f}s)", flush=True)

    print("\n=== 4:5 CROP ===")
    r = subprocess.run([".venv/bin/python", "scripts/crop_4x5.py", str(FINAL),
                        "--out", str(FINAL_4X5)], capture_output=True, text=True)
    print(f"DONE → {FINAL_4X5}" if r.returncode == 0 else f"4:5 failed: {r.stderr[-200:]}", flush=True)


if __name__ == "__main__":
    main()
