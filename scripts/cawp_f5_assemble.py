"""F5 'Three Questions' — assemble one tone wave: word-aware trim -> per-clip static gain
-> concat -> true-peak limiter (announcer register overshoots 0 dBFS; limiter mandatory).
Plain talking head — no PIP/matting. Usage: cawp_f5_assemble.py [tone]"""
import json
import os
import re
import subprocess
import sys

TONE = sys.argv[1] if len(sys.argv) > 1 else "firedup"
SRC = "outputs/cawp_f5_l1"
WORK = f"{SRC}/assemble_{TONE}"
FPS = 30
os.makedirs(f"{WORK}/trimmed", exist_ok=True)

INTENDED = {
    1: ("three", "ciw", 0.15), 2: ("two", "once", 0.15), 3: ("even", "years", 0.15),
    4: ("if", "you", 0.12), 5: ("what", "compensation", 0.15), 6: ("the", "video", 0.12),
    7: ("it", "too", 0.05), 8: ("and", "now", 0.15), 9: ("the", "started", 0.20),
}


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
    for n in range(1, 10):
        src = f"{SRC}/clip{n}_{TONE}.mp4"
        t = json.load(open(f"outputs/cawp_f5_l1_clip{n}_{TONE}/transcript.json"))
        ws = []
        for seg in t["segments"]:
            ws += seg.get("words", [])
        first_w, last_w, pad = INTENDED[n]
        start = next((w["start"] for w in ws if norm(w["word"]) == first_w), 0.0)
        end = next((w["end"] for w in reversed(ws) if norm(w["word"]) == last_w), None)
        if end is None:
            raise RuntimeError(f"clip{n}: '{last_w}' not found")
        start = max(0.0, start - 0.12)
        out = f"{WORK}/trimmed/clip{n}.mp4"
        trimmed_all.append(out)
        if os.path.exists(out):
            print(f"[skip] clip{n}", flush=True)
            continue
        gain_src = f"{WORK}/trimmed/_raw{n}.mp4"
        run(["ffmpeg", "-y", "-i", src, "-ss", f"{start:.3f}", "-t", f"{end + pad - start:.3f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", gain_src])
        g = -16.0 - loudness(gain_src)
        run(["ffmpeg", "-y", "-i", gain_src, "-af", f"volume={g:+.2f}dB",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out])
        os.remove(gain_src)
        print(f"[trim+gain] clip{n}: {start:.2f}-{end + pad:.2f}s ({g:+.1f}dB)", flush=True)

    lst = f"{WORK}/concat.txt"
    with open(lst, "w") as f:
        for s in trimmed_all:
            f.write(f"file '{os.path.abspath(s)}'\n")
    final = f"{SRC}/f5_l1_{TONE}_v1.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final])
    print(f"[final] {final}", flush=True)


if __name__ == "__main__":
    main()
