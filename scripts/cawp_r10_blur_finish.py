"""R10 blur-background finisher: VEED matte (fal) -> gblur composite -> Nick + disclaimer.
Run on an assembled persona master (r10_winner_<slug>_v1.mp4). Produces
r10_winner_<slug>_v2_blurbg_nick_disclaimer.mp4. Skip-if-exists on the matte.
Usage: cawp_r10_blur_finish.py <slug> [slug ...]   [--sigma 7]"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fal_client import remove_background

SIGMA = 7


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd[:6])}...\n{r.stderr[-300:]}")


def finish(slug):
    d = f"outputs/cawp_r10_winner_{slug}"
    master = f"{d}/r10_winner_{slug}_v1.mp4"
    alpha = f"{d}/{slug}_alpha.webm"
    blur = f"{d}/r10_winner_{slug}_v2_blurbg.mp4"
    combo = f"{d}/r10_winner_{slug}_v2_blurbg_nick_disclaimer.mp4"
    if not os.path.exists(master):
        print(f"[skip] {slug}: master not assembled yet", flush=True)
        return
    if os.path.exists(combo) and os.path.getsize(combo) > 1000:
        print(f"[skip] {slug}: blur combo exists", flush=True)
        return
    if not (os.path.exists(alpha) and os.path.getsize(alpha) > 1000):
        remove_background(master, alpha, variant="fast", output_codec="vp9")
        print(f"[ok] matte {slug}", flush=True)
    run(["ffmpeg", "-y", "-i", master, "-c:v", "libvpx-vp9", "-i", alpha,
         "-filter_complex",
         f"[0:v]gblur=sigma={SIGMA}[bg];[bg][1:v]overlay=0:0:shortest=1,format=yuv420p[v]",
         "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-c:a", "copy", blur])
    nick = f"/tmp/{slug}_v2_nick.mp4"
    run([".venv/bin/python", "scripts/caption_nick.py", blur, "--out", nick,
         "--biased", "Chowchilla:3.0,CCWF:2.0,CIW:2.0,Mija:2.0"])
    run([".venv/bin/python", "scripts/burn_disclaimer.py", nick, combo])
    os.remove(nick)
    print(f"[final] {combo}", flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--sigma" in sys.argv:
        SIGMA = int(sys.argv[sys.argv.index("--sigma") + 1])
    for slug in args:
        finish(slug)
    print("done", flush=True)
