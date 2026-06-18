"""R-batch finisher — one command per ad, end to end:
word-aware trim (intended first/last words derived from the script registry) -> per-clip
static gain -> concat -> true-peak limiter -> Nick captions -> disclaimer -> ONE combo file.
Usage: cawp_r_assemble.py <ad_slug>   (e.g. r2_believed)
Requires: all 9 clips landed + dissected to outputs/cawp_<ad>_<persona>_clip{N}/transcript.json
(unique-stem dissect dirs, same pattern as F1/F5)."""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cawp_r_batch_gen import SCRIPTS

AD = sys.argv[1]
CFG = SCRIPTS[AD]
PERSONA = CFG["persona"]
SRC = f"outputs/cawp_{AD}_{PERSONA}"
WORK = f"{SRC}/assemble"
FPS = 30
os.makedirs(f"{WORK}/trimmed", exist_ok=True)


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd[:6])}...\n{r.stderr[-300:]}")


def loudness(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    return float(j["input_i"])


def main():
    trimmed_all = []
    for n, line in enumerate(CFG["lines"], 1):
        toks = [norm(t) for t in line.split() if norm(t)]
        first_w, last_w = toks[0], toks[-1]
        burn_path = f"outputs/cawp_{AD}_{PERSONA}_clip{n}/burned_text.json"
        if os.path.exists(burn_path):
            burn = json.load(open(burn_path))
            if burn.get("flagged"):
                print(f"!! BURN-FLAG clip{n}: {burn.get('reason','')} — confirm with a band sheet "
                      f"before shipping (texture false-positives are common)", flush=True)
        t = json.load(open(f"outputs/cawp_{AD}_{PERSONA}_clip{n}/transcript.json"))
        ws = []
        for seg in t["segments"]:
            ws += seg.get("words", [])
        start = next((w["start"] for w in ws if norm(w["word"]) == first_w), 0.0)
        end = next((w["end"] for w in reversed(ws) if norm(w["word"]) == last_w), None)
        if end is None:
            raise RuntimeError(f"clip{n}: last intended word '{last_w}' not found in transcript")
        start = max(0.0, start - 0.12)
        end = end + 0.15
        out = f"{WORK}/trimmed/clip{n}.mp4"
        trimmed_all.append(out)
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            print(f"[skip] clip{n}", flush=True)
            continue
        raw = f"{WORK}/trimmed/_raw{n}.mp4"
        run(["ffmpeg", "-y", "-i", f"{SRC}/clip{n}.mp4", "-ss", f"{start:.3f}",
             "-t", f"{end - start:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
             "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", raw])
        g = -16.0 - loudness(raw)
        run(["ffmpeg", "-y", "-i", raw, "-af", f"volume={g:+.2f}dB",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
        os.remove(raw)
        print(f"[trim+gain] clip{n}: {start:.2f}-{end:.2f}s ({g:+.1f}dB)", flush=True)

    lst = f"{WORK}/concat.txt"
    with open(lst, "w") as f:
        for s in trimmed_all:
            f.write(f"file '{os.path.abspath(s)}'\n")
    master = f"{SRC}/{AD}_{PERSONA}_v1.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", master])
    print(f"[master] {master}", flush=True)

    nick = f"{SRC}/{AD}_{PERSONA}_v1_nick.mp4"
    combo = f"{SRC}/{AD}_{PERSONA}_v1_nick_disclaimer.mp4"
    run([".venv/bin/python", "scripts/caption_nick.py", master, "--out", nick,
         "--biased", "Chowchilla:3.0,CCWF:2.0,CIW:2.0"])
    run([".venv/bin/python", "scripts/burn_disclaimer.py", nick, combo])
    os.remove(nick)
    print(f"[final] {combo}", flush=True)


if __name__ == "__main__":
    main()
