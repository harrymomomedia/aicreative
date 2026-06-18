"""R10 — assemble one winner-script ad per persona from outputs/cawp_r10_winner_<slug>/.
Word-aware trim per clip (unique-stem dissect transcripts), per-clip gain to -16 LUFS,
concat, true-peak limiter, Nick captions + disclaimer -> single combo file.
Usage: cawp_r10_assemble.py <slug> [slug ...]   (e.g. l7 l8)"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cawp_r10_winner_gen import LINES, PERSONAS

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


def trim_clip(slug, idx, line, out):
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return
    stem = f"cawp_r10_winner_{slug}_clip{idx}"
    burn = json.load(open(f"outputs/{stem}/burned_text.json"))
    if burn.get("flagged"):
        print(f"!! BURN-FLAG {stem}: {burn.get('reason','')} — band-sheet before shipping", flush=True)
    t = json.load(open(f"outputs/{stem}/transcript.json"))
    ws = []
    for seg in t["segments"]:
        ws += seg.get("words", [])
    toks = [norm(x) for x in line.split() if norm(x)]
    first_w, last_w = toks[0], toks[-1]
    start = next((w["start"] for w in ws if norm(w["word"]).startswith(first_w)), 0.0)
    end = next((w["end"] for w in reversed(ws) if norm(w["word"]).startswith(last_w)), None)
    if end is None:
        raise RuntimeError(f"{stem}: last word '{last_w}' not found in transcript")
    start = max(0.0, start - 0.12)
    end = end + 0.15
    raw = out + ".raw.mp4"
    run(["ffmpeg", "-y", "-i", f"outputs/cawp_r10_winner_{slug}/clip{idx}.mp4",
         "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", raw])
    g = -16.0 - loudness(raw)
    run(["ffmpeg", "-y", "-i", raw, "-af", f"volume={g:+.2f}dB",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
    os.remove(raw)
    print(f"[trim] {slug} clip{idx} ({g:+.1f}dB)", flush=True)


def assemble(slug):
    _, first_sentence = PERSONAS[slug]
    src = f"outputs/cawp_r10_winner_{slug}"
    tdir = f"{src}/trimmed"
    os.makedirs(tdir, exist_ok=True)
    clip_lines = [f"{first_sentence} I thought, okay, that part of my life is over."] + LINES
    for idx, line in enumerate(clip_lines, 1):
        trim_clip(slug, idx, line, f"{tdir}/clip{idx}.mp4")
    lst = f"{src}/concat.txt"
    with open(lst, "w") as f:
        for idx in range(1, len(clip_lines) + 1):
            f.write(f"file '{os.path.abspath(tdir)}/clip{idx}.mp4'\n")
    master = f"{src}/r10_winner_{slug}_v1.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", master])
    nick = f"{src}/r10_winner_{slug}_v1_nick.mp4"
    combo = f"{src}/r10_winner_{slug}_v1_nick_disclaimer.mp4"
    run([".venv/bin/python", "scripts/caption_nick.py", master, "--out", nick,
         "--biased", "Chowchilla:3.0,CCWF:2.0,CIW:2.0,Mija:2.0"])
    run([".venv/bin/python", "scripts/burn_disclaimer.py", nick, combo])
    os.remove(nick)
    print(f"[final] {combo}", flush=True)


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        assemble(slug)
    print("done", flush=True)
