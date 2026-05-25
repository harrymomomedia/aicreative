"""IL JDC claymation explainer — ASSEMBLY (sync 22 clips to Brian VO + caption).

VO: outputs/illinois_jdc_claymation/vo/survivor_brian.mp3 (54.64s, eleven_v3).
Beat timings (from Scribe word-timestamps):
  0.00 hook/lockup | 8.98 abuse | 15.02 reveal | 22.70 facility list
  (St.Charles 22.7, Joliet 23.9, Harrisburg 24.9, Warrenville 26.0, Audy 27.4,
   "touched you" 28.8) | 32.56 not-alone | 40.84 mechanic | 49.48 CTA → 54.64

All clips 496x864 @ 24fps (uniform) → clean concat, no scaling.
Pipeline: trim each segment → concat (demuxer) → mux VO → yellow-text captions.

Output:
  explainer_v1_raw.mp4        (video + VO, no captions)
  explainer_v1_captioned.mp4  (+ yellow-text captions, no disclaimer)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "outputs/illinois_jdc_claymation"
ASM = CLIPS / "assembly"
ASM.mkdir(parents=True, exist_ok=True)
VO = CLIPS / "vo/survivor_brian.mp3"
RAW = CLIPS / "explainer_v2_raw.mp4"
CAPTIONED = CLIPS / "explainer_v2_hormozi.mp4"

IN = 0.2  # skip first 0.2s settle of each clip

# (slug, duration) — durations sum to 54.64 = VO length, aligned to beats
SEGMENTS = [
    # beat 1 — TAKEN BY POLICE -> locked up (0.00–8.12); CHARACTER-FIRST open
    ("clay_police_car",           1.00, 0.50),   # 0.00 "When I" — terrified face at window (thumb-stop)
    ("clay_police_street",        0.90),         # 1.00 "was a kid, Illinois" — taken by police (Chicago)
    ("lockup_02_cell_door",       2.30, 2.00),   # 1.90 "locked me up" — behind bars (in=2.0)
    ("lockup_03_corridor_escort", 1.80),         # 4.20 "something happened in there"
    ("clay_02_corridor",          2.12),         # 6.00 "never told anybody, for years"
    # beat 2 — abuse (8.12–14.34)
    ("clay_08_looming_shadow",    2.28),         # 8.12 "A guard sexually abused me"
    ("clay_e1_fear_eyes_v2",      1.80),         # 10.40 "I buried it"
    ("clay_e3_curled_sobbing_v2", 2.14),         # 12.20 "nobody would believe a kid like me"
    # beat 3 — reveal (14.34–22.82)
    ("clay_news_shock",           3.58),         # 14.34 "found out... paid out millions" (SHOCK)
    ("clay_many_survivors",       2.38),         # 17.92 "to people it happened to" (MANY)
    ("clay_e5_adult_haunted_v2",  2.52),         # 20.30 "people like me" (back to him)
    # beat 4 — facility list + "sexually abused you, it counts" (22.82–32.98)
    ("clay_p3_empty_cell",        0.84),         # 22.82 St. Charles
    ("clay_p5_yard",              0.96),         # 23.66 Joliet
    ("clay_p4_dayroom",           1.22),         # 24.62 Harrisburg
    ("clay_p2_cell_bars",         1.36),         # 25.84 Warrenville
    ("clay_p6_steel_door",        1.38),         # 27.20 Audy Home
    ("clay_08_looming_shadow",    1.76),         # 28.58 "and a guard or staff member sexually"
    ("clay_09_heavy_hand",        1.34),         # 30.34 "abused you"
    ("clay_p9_clock_wall",        1.30),         # 31.68 "it counts"
    # beat 5 — most of us / Chicago / BRIGHT happy turn (32.98–40.80)
    ("clay_chicago_victims",      2.48),         # 32.98 "I wasn't the only one" (Chicago streets)
    ("clay_05_not_alone_court",   1.98),         # 35.46 "stayed quiet for years"
    ("clay_happy_bright",         3.36),         # 37.44 "wasn't your fault / not too late" — BRIGHT, beaming throughout
    # beat 6 — mechanic + justice payoff (40.80–49.16)
    ("clay_06_phone_check",       3.40),         # 40.80 "two minutes, private, only lawyers"
    ("clay_justice_chicago_bright", 4.96),       # 44.20 "significant potential compensation" (bright)
    # beat 7 — CTA + MEANINGFUL ending (49.16–53.84)
    ("clay_happy_bright",         1.84, 2.00),   # 49.16 "tap the link, see if you qualify" (full smile)
    ("clay_ending_reunion",       2.84),         # 51.00 "I just wish I'd known sooner" (closure)
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED: {' '.join(cmd[:6])}…\n{r.stderr[-500:]}", flush=True)
        sys.exit(1)
    return r


def main():
    total = sum(seg[1] for seg in SEGMENTS)
    print(f"segments: {len(SEGMENTS)}  total video: {total:.2f}s  (VO 54.64s)", flush=True)

    # 1. trim each segment (re-encode uniform → clean concat), silent
    seg_paths = []
    for i, seg in enumerate(SEGMENTS):
        slug, dur = seg[0], seg[1]
        in_pt = seg[2] if len(seg) > 2 else IN
        src = CLIPS / f"{slug}.mp4"
        if not src.exists():
            print(f"MISSING clip: {src}", flush=True); sys.exit(1)
        dst = ASM / f"seg_{i:02d}.mp4"
        run(["ffmpeg", "-y", "-ss", f"{in_pt:.2f}", "-i", str(src), "-t", f"{dur:.2f}",
             "-an", "-r", "24", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
             "-pix_fmt", "yuv420p", "-video_track_timescale", "24000", str(dst)])
        seg_paths.append(dst)
    print(f"  trimmed {len(seg_paths)} segments", flush=True)

    # 2. concat (demuxer, lossless since params match)
    concat_list = ASM / "concat.txt"
    concat_list.write_text("".join(f"file '{p.absolute()}'\n" for p in seg_paths))
    video_only = ASM / "video_only.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-c", "copy", str(video_only)])

    # 3. mux VO audio
    run(["ffmpeg", "-y", "-i", str(video_only), "-i", str(VO),
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(RAW)])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", str(RAW)],
                         capture_output=True, text=True).stdout.strip()
    print(f"  RAW assembled → {RAW}  ({dur}s)", flush=True)

    # 4. Hormozi3 emoji captions, no disclaimer (IL facility names biased)
    print("  captioning (hormozi3 emoji, no disclaimer)...", flush=True)
    r = subprocess.run([".venv/bin/python", "scripts/caption_hormozi3.py", str(RAW),
                        "--out", str(CAPTIONED),
                        "--biased", "Saint Charles Joliet Harrisburg Warrenville Audy Illinois compensation"],
                       cwd=str(ROOT), capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  caption FAILED:\n{r.stderr[-600:]}", flush=True)
        print(f"  (raw cut is still good at {RAW})", flush=True)
        return
    print(f"  CAPTIONED → {CAPTIONED}", flush=True)


if __name__ == "__main__":
    main()
