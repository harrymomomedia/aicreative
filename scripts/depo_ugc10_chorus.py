"""5 'chorus of voices' stitch videos from the 10 UGC meningioma ads.
Each chorus intercuts fragments from MANY personas into one arc: a chorus of the meningioma
diagnosis -> the Depo link -> compensation -> CTA. Reuses the already-trimmed + loudness-matched
per-clip building blocks (each ad's fin/g{II}.mp4), re-encodes uniform, concats, master limiter,
Nick caption. Different persona mix per chorus.
  python scripts/depo_ugc10_chorus.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from depo_ugc10_gen import ADS

W = Path("outputs/depo_ugc10")
OUT = W / "chorus"
OUT.mkdir(parents=True, exist_ok=True)
SLUG = {a["n"]: a["slug"] for a in ADS}

# (ad_n, clip_idx) — clip_idx maps to that ad's fin/g{idx}.mp4
# beats: DIAG (meningioma) x3 -> DEPO link x2 -> COMP/CTA close
CHORUS = {
    1: [(1, 1), (7, 1), (6, 1), (3, 4), (10, 3), (9, 6), (2, 7)],
    2: [(4, 1), (9, 1), (3, 1), (8, 2), (10, 3), (6, 7), (7, 7)],
    3: [(6, 1), (1, 1), (10, 2), (3, 4), (6, 2), (10, 5), (5, 7)],
    4: [(7, 1), (4, 1), (9, 1), (3, 1), (8, 2), (9, 6), (8, 5)],
    5: [(3, 1), (6, 1), (7, 1), (10, 3), (3, 4), (6, 7), (2, 7)],
}


def run(c):
    subprocess.run(c, check=True, capture_output=True, text=True)


def measure_i(p):
    r = subprocess.run(["ffmpeg", "-i", str(p), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = r.stderr
    try:
        return float(json.loads(t[t.rfind("{"):t.rfind("}") + 1])["input_i"])
    except Exception:
        return -18.0


def gclip(adn, ci):
    return W / f"ad{adn:02d}_{SLUG[adn]}" / "fin" / f"g{ci:02d}.mp4"


def build(cn, seq):
    work = OUT / f"c{cn}"
    work.mkdir(exist_ok=True)
    parts = []
    for j, (adn, ci) in enumerate(seq):
        src = gclip(adn, ci)
        if not src.exists():
            print(f"  MISSING {src}", flush=True)
            continue
        p = work / f"p{j:02d}.mp4"
        run(["ffmpeg", "-y", "-i", str(src), "-vf", "scale=720:1280,fps=24,setsar=1",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(p)])
        parts.append(p)
    listf = work / "concat.txt"
    listf.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    stitched = work / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(stitched)])
    mi = measure_i(stitched)
    final = OUT / f"chorus{cn}_final.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-af", f"volume={-16.0 - mi:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    nick = OUT / f"chorus{cn}_nick.mp4"
    run([".venv/bin/python", "scripts/caption_nick.py", str(final), "--out", str(nick),
         "--biased", "meningioma:3.0,Depo:2.0,Provera:2.0"])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", str(final)], capture_output=True, text=True).stdout.strip()
    print(f"chorus{cn} -> {nick}  ({dur}s, {len(parts)} fragments)", flush=True)


def main():
    for cn, seq in CHORUS.items():
        try:
            build(cn, seq)
        except Exception as e:
            print(f"chorus{cn} ERR: {str(e)[:160]}", flush=True)


if __name__ == "__main__":
    main()
