"""Depo Pixar Myth-buster — ASSEMBLY.

Sync 12 Pixar b-roll shots to outputs/depo_pixar_myth/vo.mp3. All clips 9:16 480p (Seedance Fast).
Pipeline: trim each shot to its target dur from its in-point → concat (demuxer) → mux VO → raw.
Captions are a separate step (Hormozi 3 --no-emoji per the storyboard).

Output: outputs/depo_pixar_myth/depo_pixar_myth_raw.mp4
Run:  .venv/bin/python scripts/depo_pixar_myth_assemble.py
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "outputs/depo_pixar_myth"
ASM = CLIPS / "assembly"; ASM.mkdir(parents=True, exist_ok=True)
VO = CLIPS / "vo.mp3"
RAW = CLIPS / "depo_pixar_myth_raw.mp4"

# (slug, duration, in_point) — sums to ~51s, aligned to VO beats
SEGMENTS = [
    ("s01_host_open",        6.00, 0.20),  # "If you've got a meningioma..."
    ("s02_calendar_years",   3.20, 0.40),  # "years ago, it's too late"
    ("s03_calendar_stop",    2.40, 0.40),  # "it's not"
    ("s04_empty_wallet",     3.60, 0.40),  # "can't afford a lawyer"
    ("s05_phone_free",       3.60, 0.40),  # "costs you nothing to find out"
    ("s06_not_sue",          3.80, 0.40),  # "not the type to sue"
    ("s07_host_neither",     2.80, 0.30),  # "neither am I"
    ("s08_folder_studies",   4.40, 0.30),  # "isn't about that, it's about what they didn't tell us"
    ("s09_mri_tumor",        3.80, 0.40),  # "I have a meningioma, a brain tumor"
    ("s10_vial_calendar",    3.60, 0.40),  # "on that shot for a long time"
    ("s11_connection_line",  4.00, 0.40),  # "those two things are connected, company knew"
    ("s12_host_cta",         6.00, 0.20),  # "checking is free... I had the same one... Go see"
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED: {' '.join(str(c) for c in cmd[:6])}…\n{r.stderr[-600:]}", flush=True)
        sys.exit(1)
    return r


def main():
    if not VO.exists():
        print(f"MISSING VO: {VO} — run depo_pixar_myth_vo.py first"); sys.exit(1)
    total = sum(s[1] for s in SEGMENTS)
    print(f"segments: {len(SEGMENTS)}  total video: {total:.2f}s  VO: {VO.name}", flush=True)

    seg_paths = []
    for i, (slug, dur, in_pt) in enumerate(SEGMENTS):
        src = CLIPS / f"{slug}.mp4"
        if not src.exists():
            print(f"MISSING clip: {src}", flush=True); sys.exit(1)
        dst = ASM / f"seg_{i:02d}.mp4"
        run(["ffmpeg", "-y", "-ss", f"{in_pt:.2f}", "-i", str(src), "-t", f"{dur:.2f}",
             "-an", "-r", "24", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
             "-pix_fmt", "yuv420p", "-video_track_timescale", "24000", str(dst)])
        seg_paths.append(dst)
    print(f"  trimmed {len(seg_paths)} segments", flush=True)

    concat_list = ASM / "concat.txt"
    concat_list.write_text("".join(f"file '{p.absolute()}'\n" for p in seg_paths))
    video_only = ASM / "video_only.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(video_only)])

    run(["ffmpeg", "-y", "-i", str(video_only), "-i", str(VO),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(RAW)])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", str(RAW)],
                         capture_output=True, text=True).stdout.strip()
    print(f"  RAW assembled → {RAW}  ({dur}s)", flush=True)


if __name__ == "__main__":
    main()
