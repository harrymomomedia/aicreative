"""Depo-Provera brain-meningioma CLAYMATION explainer — ASSEMBLY.

Sync the 8 clay b-roll shots to the first-person female VO (survivor_f49.mp3, 41.3s).
One shot per VO beat, in order. Durations sum to the VO length (beat boundaries from Scribe
word-timestamps). Per-shot in_point picks the best window of each 7s clip (crowd / door / news
payoffs land at clip-END, so those are end-weighted).

All clips 496x864 (480p 9:16). Pipeline: trim each → concat (demuxer) → mux VO → raw.
Captions are a SEPARATE step (project rule: don't burn captions by default).

Output: outputs/depo_claymation/depo_explainer_v1_raw.mp4
Run:  .venv/bin/python scripts/depo_claymation_assemble.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "outputs/depo_claymation"
ASM = CLIPS / "assembly"
ASM.mkdir(parents=True, exist_ok=True)
VO = CLIPS / "vo/survivor_f49.mp3"
RAW = CLIPS / "depo_explainer_v1_raw.mp4"

# (slug, duration, in_point) — 11 shots over the 8 VO beats; durations sum ≈ 41.3s = VO length.
# in_point picks the best window of each 6s clip (end-weighted payoffs: face-fall, crowd, face-lift).
# Tuned after reviewing the final clips.
SEGMENTS = [
    # beat 1 (0.00–5.00) "brain tumor… everything went quiet" [sigh]
    ("s01_mri_reveal",   2.40, 0.30),   # 0.00  MRI scan, meningioma visible
    ("s02_exam_news",    2.60, 1.20),   # 2.40  doctor tells her, face falls (late)
    # beat 2 (5.00–9.58) "a meningioma… where did this come from?"
    ("s03_her_stunned",  2.30, 0.40),   # 5.00  close, stunned
    ("s04_brain_rotate", 2.28, 0.40),   # 7.30  rotating 3D brain, tumor highlighted
    # beat 3 (9.58–15.88) "the Depo shot… every three months, clockwork"
    ("s05_injection",    3.30, 0.50),   # 9.58  nurse gives her the shot
    ("s06_calendar",     3.00, 0.40),   # 12.88 calendar flips, vials, clock
    # beat 4 (15.88–19.50) "nobody ever warned me"
    ("s07_leaflet",      3.62, 0.80),   # 15.88 reads leaflet, shadow looms
    # beat 5 (19.50–24.50) "I wasn't the only one… same diagnosis"
    ("s08_waiting_room", 5.00, 0.80),   # 19.50 waiting room of Black women
    # beat 6 (24.50–30.20) "lawsuit now… significant compensation"
    ("s09_tv_news",      5.70, 1.00),   # 24.50 sees the news, face lifts
    # beat 7 (30.20–35.50) "free, private, no court, attorney handles it"
    ("s10_attorney",     5.30, 0.60),   # 30.20 attorney's office, reassurance
    # beat 8 (35.50–41.30) "if you have a meningioma… see if you qualify"
    ("s11_phone_cta",    5.80, 0.50),   # 35.50 taps the phone form, hopeful
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
