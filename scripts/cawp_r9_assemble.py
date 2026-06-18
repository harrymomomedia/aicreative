"""R9 'Mija' — assemble all 12 hook versions from the l2 spine.
Each ad = hook_<slug> + bridge_<map> + body3..body10 (shared), word-aware trimmed,
per-clip gain, concat, limiter, Nick captions + disclaimer -> ONE combo per hook.
Run AFTER all clips + the body4/5 anger re-rolls are landed and dissected.
Usage: cawp_r9_assemble.py [hook_slug ...]   (default: all 12)"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cawp_r9_mija_gen import BODY_LINES, BRIDGES, HOOKS

SRC = "outputs/cawp_r9_mija_l2"
FPS = 30


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


def trim_clip(stem, line, out):
    """Word-aware trim of outputs/<stem>.mp4 using its unique-stem dissect transcript."""
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return
    burn_path = f"outputs/cawp_r9_mija_l2_{stem}/burned_text.json"
    if os.path.exists(burn_path):
        b = json.load(open(burn_path))
        if b.get("flagged"):
            print(f"!! BURN-FLAG {stem}: {b.get('reason','')} — band-sheet before shipping",
                  flush=True)
    t = json.load(open(f"outputs/cawp_r9_mija_l2_{stem}/transcript.json"))
    ws = []
    for seg in t["segments"]:
        ws += seg.get("words", [])
    toks = [norm(x) for x in line.split() if norm(x)]
    first_w, last_w = toks[0], toks[-1]
    start = next((w["start"] for w in ws if norm(w["word"]).startswith(first_w)), 0.0)
    end = next((w["end"] for w in reversed(ws) if norm(w["word"]).startswith(last_w)), None)
    if end is None:
        raise RuntimeError(f"{stem}: last word '{last_w}' not found")
    start = max(0.0, start - 0.12)
    end = end + 0.15
    raw = out + ".raw.mp4"
    run(["ffmpeg", "-y", "-i", f"{SRC}/{stem}.mp4", "-ss", f"{start:.3f}",
         "-t", f"{end - start:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", raw])
    g = -16.0 - loudness(raw)
    run(["ffmpeg", "-y", "-i", raw, "-af", f"volume={g:+.2f}dB",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    os.remove(raw)
    print(f"[trim] {stem} ({g:+.1f}dB)", flush=True)


def main():
    picks = sys.argv[1:] or list(HOOKS.keys())
    tdir = f"{SRC}/assemble/trimmed"
    os.makedirs(tdir, exist_ok=True)

    # shared pieces
    for i, line in enumerate(BODY_LINES, 3):
        trim_clip(f"body{i}", line, f"{tdir}/body{i}.mp4")
    for bslug, line in BRIDGES.items():
        trim_clip(f"bridge_{bslug}", line, f"{tdir}/bridge_{bslug}.mp4")

    for slug in picks:
        line, bslug = HOOKS[slug]
        trim_clip(f"hook_{slug}", line, f"{tdir}/hook_{slug}.mp4")
        lst = f"{SRC}/assemble/concat_{slug}.txt"
        parts = [f"{tdir}/hook_{slug}.mp4", f"{tdir}/bridge_{bslug}.mp4"] + \
                [f"{tdir}/body{i}.mp4" for i in range(3, 11)]
        with open(lst, "w") as f:
            for p in parts:
                f.write(f"file '{os.path.abspath(p)}'\n")
        master = f"{SRC}/r9_mija_{slug}_v1.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
             "-af", "alimiter=limit=0.794:level=disabled:asc=1",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", master])
        nick = f"{SRC}/r9_mija_{slug}_v1_nick.mp4"
        combo = f"{SRC}/r9_mija_{slug}_v1_nick_disclaimer.mp4"
        run([".venv/bin/python", "scripts/caption_nick.py", master, "--out", nick,
             "--biased", "Chowchilla:3.0,CCWF:2.0,CIW:2.0,Mija:2.0"])
        run([".venv/bin/python", "scripts/burn_disclaimer.py", nick, combo])
        os.remove(nick)
        print(f"[final] {combo}", flush=True)
    print("done — r9 assembly complete", flush=True)


if __name__ == "__main__":
    main()
