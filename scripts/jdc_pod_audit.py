"""Full per-clip audit of the podcast videos:
  - mouth-region motion (dead lip-sync proxy: low motion + present audio = static mouth)
  - full-frame motion (frozen-frame proxy)
  - audio mean/max dB (inaudible / clipping)
  - transcript (gibberish / doubling / fillers)
Headphones are checked visually (separate). Prints a table; flags suspicious clips.
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import fal_client as fc

VIDEOS = {
    "agepower_h07": 5, "cookstat_h08": 4, "theydont_h09": 5,
    "moneyreveal_h06": 4, "barbershop_h08": 5, "familymoney_h06": 4,
}


def motion(path):
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    idxs = np.linspace(0, n - 1, min(24, n)).astype(int)
    mouth_prev = full_prev = None
    md, fd = [], []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, fr = cap.read()
        if not ok:
            continue
        h, w = fr.shape[:2]
        g = cv2.cvtColor(cv2.resize(fr, (320, int(320 * h / w))), cv2.COLOR_BGR2GRAY)
        H, W = g.shape
        mouth = g[int(H * 0.55):int(H * 0.90), int(W * 0.25):int(W * 0.75)]
        if mouth_prev is not None:
            md.append(np.mean(np.abs(mouth.astype(int) - mouth_prev.astype(int))))
            fd.append(np.mean(np.abs(g.astype(int) - full_prev.astype(int))))
        mouth_prev, full_prev = mouth, g
    cap.release()
    return (np.mean(md) if md else 0), (np.mean(fd) if fd else 0)


def audio_db(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    def grab(k):
        for ln in r.splitlines():
            if k in ln:
                return ln.split(k)[1].split("dB")[0].strip().strip(":").strip()
        return "?"
    return grab("mean_volume"), grab("max_volume")


def main():
    print(f"{'clip':28} {'mouthMot':>8} {'fullMot':>7} {'meanDB':>7} {'maxDB':>6}  transcript")
    print("-" * 120)
    for v, n in VIDEOS.items():
        for i in range(1, n + 1):
            p = f"outputs/jdc_pod_{v}/clip{i}.mp4"
            if not Path(p).exists():
                continue
            mm, fm = motion(p)
            mean_db, max_db = audio_db(p)
            try:
                tx = fc.scribe_whisper_compat(p, language_code="en")["text"].strip()
            except Exception as e:
                tx = f"ERR {e}"
            flag = ""
            if mm < 6: flag += "⚠LIPS "
            try:
                if float(mean_db) < -26: flag += "⚠QUIET "
                if float(max_db) > -0.5: flag += "⚠CLIP "
            except Exception:
                pass
            print(f"{v}/clip{i:<2} {mm:8.1f} {fm:7.1f} {str(mean_db):>7} {str(max_db):>6}  {flag}{tx[:70]}")
        print()


if __name__ == "__main__":
    main()
