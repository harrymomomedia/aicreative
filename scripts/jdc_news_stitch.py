"""Trim weird dead air from each Kling clip, then concat into final ad.

For each clip:
  1. Transcribe with Whisper medium (more accurate than small)
  2. Find first-word start + last-word end
  3. Trim to [first_word_start - 0.15s, last_word_end + 0.25s]
     (small pre-roll for natural breath, slightly longer tail so word doesn't clip)

Then concat all trimmed clips losslessly via ffmpeg concat demuxer.

Source clips (in order):
  clip1_kling_std_v1.mp4   — REPORTER asks question (cut at 'St. Charles,')
  clip2_trimmed.mp4        — INTERVIEWEE 'Yeah, I did' (already trimmed)
  clip3.mp4                — REPORTER abuse + Illinois millions
  clip4.mp4                — INTERVIEWEE 'I didn't know that was even an option'
  clip5.mp4                — REPORTER owed money + CTA

Output: outputs/illinois_jdc_news_eltracks/final.mp4
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat

OUT_DIR = Path("outputs/illinois_jdc_news_eltracks")
TRIM_DIR = OUT_DIR / "trimmed"
TRIM_DIR.mkdir(parents=True, exist_ok=True)

CLIPS = [
    ("clip1", OUT_DIR / "clip1_kling_std_v1.mp4"),
    ("clip2", OUT_DIR / "clip2_trimmed.mp4"),   # already trimmed
    ("clip3", OUT_DIR / "clip3.mp4"),
    ("clip4", OUT_DIR / "clip4.mp4"),
    ("clip5", OUT_DIR / "clip5.mp4"),
]

LEAD_PAD = 0.15   # seconds before first word
TAIL_PAD = 0.25   # seconds after last word

FINAL = OUT_DIR / "final.mp4"


def get_speech_window(video):
    """Transcribe via ElevenLabs Scribe, return (start, end) seconds of actual speech."""
    r = scribe_whisper_compat(str(video), language_code="en")
    words = []
    for s in r["segments"]:
        for w in s.get("words", []):
            words.append((w["start"], w["end"], w["word"].strip()))
    if not words:
        return None
    first = words[0][0]
    last = words[-1][1]
    text = " ".join(w[2] for w in words)
    return first, last, text


def trim(src, dst, start, end):
    """Trim src to [start, end] with re-encode (precise frame-level)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-ss", f"{start:.3f}",
        "-to", f"{end:.3f}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(dst),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  TRIM FAILED: {r.stderr[-300:]}", flush=True)
        return False
    return True


def get_duration(p):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def main():
    print("\n=== TRIMMING ===")
    trimmed_paths = []
    for slug, src in CLIPS:
        dur = get_duration(src)
        print(f"\n[{slug}] {src.name}  (orig dur {dur:.2f}s)")
        win = get_speech_window(src)
        if win is None:
            print(f"  No speech detected — skipping trim, copying as-is")
            dst = TRIM_DIR / f"{slug}.mp4"
            subprocess.run(["cp", str(src), str(dst)], check=True)
            trimmed_paths.append(dst)
            continue
        first, last, text = win
        start = max(0.0, first - LEAD_PAD)
        end = min(dur, last + TAIL_PAD)
        print(f"  speech: [{first:.2f}-{last:.2f}s]  trim: [{start:.2f}-{end:.2f}s]  text: '{text[:80]}'")
        dst = TRIM_DIR / f"{slug}.mp4"
        if trim(src, dst, start, end):
            new_dur = get_duration(dst)
            print(f"  trimmed dur: {new_dur:.2f}s")
            trimmed_paths.append(dst)

    print("\n=== CONCAT ===")
    concat_list = TRIM_DIR / "concat.txt"
    concat_list.write_text(
        "".join(f"file '{p.absolute()}'\n" for p in trimmed_paths)
    )
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
        print(f"CONCAT FAILED: {r.stderr[-500:]}")
        return
    final_dur = get_duration(FINAL)
    print(f"\nDONE → {FINAL}  ({final_dur:.2f}s)")


if __name__ == "__main__":
    main()
