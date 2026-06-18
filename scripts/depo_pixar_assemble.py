"""Depo-Provera brain-meningioma PIXAR explainer — ASSEMBLY.

Same beat map as the claymation assembler; reuses the SAME VO (style-independent). Sync the 11
Pixar b-roll shots to survivor_f49.mp3 (41.3s). All clips 496x864 (480p 9:16).
Pipeline: trim each → concat (demuxer) → mux VO → raw. Captions are a separate step.

Output: outputs/depo_pixar/depo_pixar_v1_raw.mp4
Run:  .venv/bin/python scripts/depo_pixar_assemble.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "outputs/depo_pixar"
ASM = CLIPS / "assembly"
ASM.mkdir(parents=True, exist_ok=True)
VO = ROOT / "outputs/depo_claymation/vo/survivor_f49.mp3"  # reused (style-independent)
RAW = CLIPS / "depo_pixar_v1_raw.mp4"

# (slug, duration, in_point) — identical beat map to the claymation cut (sum ≈ 41.3s).
SEGMENTS = [
    ("s01_mri_reveal",   2.40, 0.30),
    ("s02_exam_news",    2.60, 1.20),
    ("s03_her_stunned",  2.30, 0.40),
    ("s04_brain_rotate", 2.28, 0.40),
    ("s05_injection",    3.30, 0.50),
    ("s06_calendar",     3.00, 0.40),
    ("s07_leaflet",      3.62, 0.80),
    ("s08_waiting_room", 5.00, 0.80),
    ("s09_tv_news",      5.70, 1.00),
    ("s10_attorney",     5.30, 0.60),
    ("s11_phone_cta",    5.80, 0.50),
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED: {' '.join(str(c) for c in cmd[:6])}…\n{r.stderr[-600:]}", flush=True)
        sys.exit(1)
    return r


def main():
    total = sum(s[1] for s in SEGMENTS)
    print(f"segments: {len(SEGMENTS)}  total video: {total:.2f}s  (VO 41.3s)", flush=True)

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
