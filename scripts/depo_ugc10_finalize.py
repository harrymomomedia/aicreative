"""Finalize + Nick-caption the 10 UGC meningioma ads (9:16).
Per ad: dissect each clip -> word-aware trailing trim (intended line vs Scribe transcript, drops
Veo trailing improv) -> per-clip loudness gain to -18 LUFS -> concat -> master gain to -16 +
true-peak limiter -> ad{NN}_..._final.mp4, then caption_nick.py -> ad{NN}_..._nick.mp4.

  python scripts/depo_ugc10_finalize.py auto   # finalize every ad whose clips are ALL present (+ not done)
  python scripts/depo_ugc10_finalize.py 3      # finalize ad 3 only
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from depo_ugc10_gen import ADS, segment

OUT = Path("outputs/depo_ugc10")
TARGET_CLIP, TARGET_MASTER = -18.0, -16.0


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def measure_i(p):
    r = subprocess.run(["ffmpeg", "-i", str(p), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = r.stderr
    try:
        return float(json.loads(t[t.rfind("{"):t.rfind("}") + 1])["input_i"])
    except Exception:
        return -20.0


def _tok(s):
    return re.sub(r"[^\w\s]", "", s.lower()).split()


def bounds(line, tx):
    """first->last INTENDED word span; trailing/leading improv falls outside. None if no full match."""
    intended = _tok(line)
    words = [w for seg in tx.get("segments", []) for w in seg.get("words", [])]
    j, fs, le = 0, None, None
    for w in words:
        t = re.sub(r"[^\w]", "", w.get("word", "").lower())
        if not t:
            continue
        if j < len(intended) and t == intended[j]:
            if fs is None:
                fs = w["start"]
            le = w["end"]
            j += 1
    return (fs, le) if (fs is not None and le is not None and j >= len(intended)) else None


def transcript_for(clip, stem):
    txp = Path("outputs") / stem / "transcript.json"
    if not txp.exists():
        tmp = Path("outputs") / f"{stem}.mp4"
        shutil.copy(clip, tmp)
        run([".venv/bin/python", "dissect.py", str(tmp), "--interval", "1.0", "--no-ocr",
             "--biased-keywords", "meningioma", "Depo"])
    return json.loads(txp.read_text()) if txp.exists() else {"segments": []}


def finalize(ad):
    adir = OUT / f"ad{ad['n']:02d}_{ad['slug']}"
    work = adir / "fin"
    work.mkdir(exist_ok=True)
    lines = segment(ad["script"])
    present = []
    print(f"== ad{ad['n']:02d} {ad['slug']} ({len(lines)} clips) ==", flush=True)
    for i, line in enumerate(lines, 1):
        clip = adir / f"clip{i:02d}.mp4"
        if not clip.exists() or clip.stat().st_size < 50000:
            print(f"  clip{i:02d} MISSING — abort ad", flush=True)
            return None
        tx = transcript_for(clip, f"u10_a{ad['n']:02d}c{i:02d}")
        b = bounds(line, tx)
        tcl = work / f"t{i:02d}.mp4"
        if b:
            s, e = max(0.0, b[0] - 0.06), b[1] + 0.12
            fc = (f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v];"
                  f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS[a]")
            run(["ffmpeg", "-y", "-i", str(clip), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(tcl)])
            tag = "trim"
        else:
            run(["ffmpeg", "-y", "-i", str(clip), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(tcl)])
            tag = "whole"
        gi = measure_i(tcl)
        gcl = work / f"g{i:02d}.mp4"
        run(["ffmpeg", "-y", "-i", str(tcl), "-af", f"volume={TARGET_CLIP - gi:.2f}dB",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(gcl)])
        present.append(gcl)
        print(f"  clip{i:02d} {tag}", flush=True)

    listf = work / "concat.txt"
    listf.write_text("".join(f"file '{p.resolve()}'\n" for p in present))
    stitched = work / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(stitched)])
    mi = measure_i(stitched)
    final = adir / f"ad{ad['n']:02d}_{ad['slug']}_final.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-af", f"volume={TARGET_MASTER - mi:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    nick = adir / f"ad{ad['n']:02d}_{ad['slug']}_nick.mp4"
    run([".venv/bin/python", "scripts/caption_nick.py", str(final), "--out", str(nick),
         "--biased", "meningioma:3.0,Depo:2.0,Provera:2.0"])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", str(final)], capture_output=True, text=True).stdout.strip()
    print(f"DONE ad{ad['n']:02d}: {dur}s  final={final}  nick={nick}", flush=True)
    return nick


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if arg == "auto":
        for ad in ADS:
            adir = OUT / f"ad{ad['n']:02d}_{ad['slug']}"
            if (adir / f"ad{ad['n']:02d}_{ad['slug']}_nick.mp4").exists():
                print(f"ad{ad['n']:02d} already done", flush=True)
                continue
            n = len(segment(ad["script"]))
            if all((adir / f"clip{i:02d}.mp4").exists() for i in range(1, n + 1)):
                try:
                    finalize(ad)
                except Exception as e:
                    print(f"ad{ad['n']:02d} finalize ERR: {str(e)[:160]}", flush=True)
            else:
                print(f"ad{ad['n']:02d} waiting on clips", flush=True)
    else:
        finalize(next(a for a in ADS if a["n"] == int(arg)))


if __name__ == "__main__":
    main()
