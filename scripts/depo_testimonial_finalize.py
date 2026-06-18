"""Finalize the Depo testimonial ads (p4, p5).
Per clip: word-aware trailing trim (subsequence-match the intended line in the Scribe transcript,
cut to the last INTENDED word -> drops Veo trailing improv like "I thought-", "So-", "And-") ->
normalize to 720x1280@24 (+ optional watermark crop) -> per-clip static gain to -18 LUFS.
Then concat (lossless) -> master gain to -16 LUFS + true-peak limiter.

Single persona per ad -> NO voice_changer (raw Veo is cleaner; STS only earns its keep on
multi-clip speaker drift). No frozen-frame leadpad.

Transcripts expected at outputs/depo_<pkey>_<cid>/transcript.json (unique stems).
  .venv/bin/python scripts/depo_testimonial_finalize.py            # both
  .venv/bin/python scripts/depo_testimonial_finalize.py p4
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from depo_testimonial_gen import CLIPS, PERSONAS

LINES = [c[1] for c in CLIPS]                      # intended line per clip (shared by both personas)
TARGET_CLIP, TARGET_MASTER = -18.0, -16.0
CROP_WATERMARK = False                             # user OK'd the Veo corner -> keep it (no crop/rescale loss)
VF_CROP = "crop=664:1180:28:0,scale=720:1280,setsar=1,fps=24"
VF_PLAIN = "scale=720:1280,setsar=1,fps=24"


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def measure_i(path):
    p = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = p.stderr
    return float(json.loads(t[t.rfind("{"):t.rfind("}") + 1])["input_i"])


def _tok(s):
    # strip punctuation WITHOUT inserting spaces so contractions match the per-word cleaning
    # ("I'm" -> "im" on both sides; otherwise the subsequence match breaks on every contraction)
    return re.sub(r"[^\w\s]", "", s.lower()).split()


def intended_bounds(line, transcript):
    """(first_start, last_end) spanning the first->last INTENDED word; trailing/leading improv falls out."""
    intended = _tok(line)
    words = []
    for seg in transcript.get("segments", []):
        words.extend(seg.get("words", []))
    j, first_start, last_end = 0, None, None
    for w in words:
        tok = re.sub(r"[^\w]", "", w.get("word", "").lower())
        if not tok:
            continue
        if j < len(intended) and tok == intended[j]:
            if first_start is None:
                first_start = w["start"]
            last_end = w["end"]
            j += 1
    if first_start is None or last_end is None or j < len(intended):
        return None
    return first_start, last_end


def transcript_path(pkey, cid):
    return Path(f"outputs/depo_{pkey}_{cid}/transcript.json")


def trim_clip(pkey, cid, line, dest, lead=0.06, tail=0.12):
    src = Path(PERSONAS[pkey]["out"]) / f"{cid}.mp4"
    tp = transcript_path(pkey, cid)
    s, e = None, None
    if tp.exists():
        b = intended_bounds(line, json.loads(tp.read_text()))
        if b:
            s, e = max(0.0, b[0] - lead), b[1] + tail
    vf = VF_CROP if CROP_WATERMARK else VF_PLAIN
    if s is not None:
        fc = (f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS,{vf}[v];"
              f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS[a]")
        run(["ffmpeg", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(dest)])
        return f"trim[{s:.2f}-{e:.2f}]"
    # no transcript/match -> normalize whole clip
    run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-ac", "2", str(dest)])
    return "whole(no-match)"


def finalize(pkey):
    out_dir = Path(PERSONAS[pkey]["out"])
    work = out_dir / "finalize"
    work.mkdir(exist_ok=True)
    print(f"== [{pkey}] trim + normalize + gain ==", flush=True)
    present = []
    for i, line in enumerate(LINES, start=1):
        cid = f"clip{i:02d}"
        if not (out_dir / f"{cid}.mp4").exists():
            print(f"  {cid} MISSING — skip", flush=True)
            continue
        trimmed = work / f"{cid}_t.mp4"
        info = trim_clip(pkey, cid, line, trimmed)
        gi = measure_i(trimmed)
        final_c = work / f"{cid}.mp4"
        run(["ffmpeg", "-y", "-i", str(trimmed), "-af", f"volume={TARGET_CLIP - gi:.2f}dB",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final_c)])
        present.append(cid)
        print(f"  {cid}: {info}  {gi:.1f}->{TARGET_CLIP} LUFS", flush=True)

    listf = work / "concat.txt"
    listf.write_text("".join(f"file '{(work / f'{c}.mp4').resolve()}'\n" for c in present))
    stitched = work / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(stitched)])
    mi = measure_i(stitched)
    final = out_dir / f"depo_testimonial_{pkey}_final.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-af", f"volume={TARGET_MASTER - mi:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(final)], capture_output=True, text=True).stdout.strip()
    print(f"FINAL [{pkey}] -> {final}  {dur}s  {measure_i(final):.1f} LUFS", flush=True)
    return final


def main():
    who = sys.argv[1] if len(sys.argv) > 1 else "both"
    for pkey in (["p4", "p5"] if who == "both" else [who]):
        finalize(pkey)


if __name__ == "__main__":
    main()
