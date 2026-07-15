#!/usr/bin/env python3
"""CAWP stacked format: top half = rotating static b-roll stills (real news frames +
gpt-image-2 generated), bottom half = yapper persona (face crop), Redwood captions
burned separately at the 50% seam afterwards.

Usage: cawp_stacked_assemble.py <LETTER> [--slot 4.5] [--crop-y 140]
Input : outputs/chowchilla_podcast/<L>_full.mp4  (720x1280 master)
Output: outputs/chowchilla_podcast/<L>_stacked.mp4  (720x1280: 720x640 broll / 720x640 face)
"""
import os, subprocess, sys, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POD = os.path.join(ROOT, "outputs", "chowchilla_podcast")
BR = os.path.join(ROOT, "outputs", "cawp_broll_wp")

# Curated rotation v4 (user rule 2026-07-15): MALE-GUARD interaction shots dominate,
# real news frames + a few inmate/facility shots woven through. Each video gets a
# per-letter OFFSET (see main) so the 8 ads don't open on the same image.
SEQUENCE = [
    "gen/wp41_male_guard_doorway.png",
    "gen/wp42_male_guard_follow.png",
    "gen/wp46_male_guard_towering.png",
    "clean/n05_ccwf_yard_inmates.jpg",
    "gen/wp43_male_guard_over_bunk.png",
    "gen/wp47_male_guard_cell_talk.png",
    "clean/n01_ccwf_monument_sign.jpg",
    "gen/wp44_male_guard_flashlight.png",
    "gen/wp52_male_guard_count_pause.png",
    "clean/n11_cell_bars_dark.jpg",
    "gen/wp48_male_guard_stairwell.png",
    "gen/wp49_male_guards_yard_pair.png",
    "clean/n08_wire_dusk.jpg",
    "gen/wp51_male_guard_cctv.png",
    "gen/wp50_male_guard_door_hold.png",
    "clean/n02_ccwf_tower_trees.jpg",
    "gen/wp45_male_guard_office.png",
    "gen/wp01_yard_walk.png",
]

# Deterministic per-letter start offset into SEQUENCE (variety without templating).
OFFSETS = {"P":0,"S1":2,"S2":5,"S3":7,"S4":9,"S5":11,"S6":13,"S7":15}

def detect_crop_y(src, win=640, canvas_h=1280):
    """Auto: sample frames, find the persona's head-top so the crop begins there
    (top of head lands at the seam). Returns clamped crop_y; falls back to 140."""
    import cv2
    cap = cv2.VideoCapture(src)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 300
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    tops, hs = [], []
    for frac in (0.1, 0.25, 0.4, 0.55, 0.7, 0.85):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total*frac))
        ok, img = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = casc.detectMultiScale(gray, 1.1, 5, minSize=(120, 120))
        if len(faces) == 0:
            continue
        x, y, fw, fh = max(faces, key=lambda f: f[2]*f[3])  # largest = the talker
        tops.append(y); hs.append(fh)
    cap.release()
    if not tops:
        return 140
    tops.sort(); hs.sort()
    mt = tops[len(tops)//2]; mh = hs[len(hs)//2]
    crop_y = int(mt - 0.36*mh)                       # head-top ≈ 0.36 face-height above box
    return max(0, min(crop_y, canvas_h - win))

def main():
    letter = sys.argv[1]
    slot = float(sys.argv[sys.argv.index("--slot")+1]) if "--slot" in sys.argv else 4.5
    crop_y = int(sys.argv[sys.argv.index("--crop-y")+1]) if "--crop-y" in sys.argv else None
    src = os.path.join(POD, f"{letter}_full.mp4")
    out = os.path.join(POD, f"{letter}_stacked.mp4")
    dur = float(subprocess.check_output(
        ["ffprobe","-v","error","-select_streams","v:0","-show_entries","format=duration",
         "-of","csv=p=0", src]).decode().strip())
    if crop_y is None:
        crop_y = detect_crop_y(src)
    print(f"crop_y={crop_y}", flush=True)
    off = int(sys.argv[sys.argv.index("--offset")+1]) if "--offset" in sys.argv else OFFSETS.get(letter, 0)
    n = math.ceil(dur / slot)
    imgs = [os.path.join(BR, SEQUENCE[(i + off) % len(SEQUENCE)]) for i in range(n)]
    for p in imgs:
        assert os.path.exists(p), p

    cmd = ["ffmpeg","-nostdin","-y","-loglevel","error"]
    for p in imgs:
        cmd += ["-loop","1","-t",str(slot),"-i",p]
    cmd += ["-i", src]
    fc = []
    for i in range(n):
        fc.append(f"[{i}:v]scale=720:640:force_original_aspect_ratio=increase,"
                  f"crop=720:640,setsar=1,fps=30,format=yuv420p[im{i}]")
    fc.append("".join(f"[im{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[top]")
    fc.append(f"[{n}:v]crop=720:640:0:{crop_y},setsar=1[bot]")
    fc.append("[top][bot]vstack[v]")
    cmd += ["-filter_complex",";".join(fc),
            "-map","[v]","-map",f"{n}:a","-t",f"{dur:.3f}",
            "-c:v","libx264","-preset","fast","-crf","19","-c:a","aac","-b:a","192k", out]
    subprocess.run(cmd, check=True)
    print("OK", out)

if __name__ == "__main__":
    main()
