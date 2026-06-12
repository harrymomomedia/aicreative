"""F1 'Look At This' — assemble one tone wave into the finished PIP ad.
Pipeline: word-aware trim (drop leading/trailing Veo improv) -> per-clip loudness gain ->
veed/fal alpha matting -> composite over docu-zoomed article cards (varied moves) ->
concat -> true-peak limiter. Usage: cawp_f1_assemble.py [tone]  (default: concerned)"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fal_client import remove_background

TONE = sys.argv[1] if len(sys.argv) > 1 else "concerned"
SRC_DIR = "outputs/cawp_f1_l4"
WORK = f"{SRC_DIR}/assemble_{TONE}"
CARDS = os.environ.get("F1_CARDS", "outputs/cawp_f1_news/cards_real")
FPS = 30
W, H = 720, 1280
for sub in ("trimmed", "alpha", "segs"):
    os.makedirs(f"{WORK}/{sub}", exist_ok=True)

# (last intended word, end pad) per clip — tight pad on clip6 to drop appended "here"
INTENDED = {
    1: ("stop", "got", 0.15), 2: ("last", "ciw", 0.15), 3: ("and", "one", 0.15),
    4: ("so", "time", 0.15), 5: ("you", "basically", 0.15), 6: ("where", "check", 0.03),
    7: ("if", "scrolling", 0.15), 8: ("tap", "do", 0.20),
}

# card + zoompan recipe per clip — TOP-LEFT-ANCHORED: x='0' AND y='0' so neither the
# left text edge nor the page top (masthead) ever crops at any zoom (user rules
# 2026-06-10). Only clips 1-3 use cards now (4-8 = full-frame UGC).
ZP = {
    1: ("card1_sentence", "z='min(1+0.14*on/{F},1.14)':x='0':y='0'"),
    2: ("card2_doj",      "z='min(1+0.12*on/{F},1.12)':x='0':y='0'"),
    3: ("card3_filings",  "z='min(1+0.18*on/{F},1.18)':x='0':y='0'"),
}
HL_T0, HL_DUR = 0.35, 0.9  # marker sweep: starts after the cut lands, draws in ~0.9s


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def words_for(n):
    t = json.load(open(f"outputs/cawp_f1_l4_clip{n}_{TONE}/transcript.json"))
    out = []
    for seg in t["segments"]:
        out += seg.get("words", [])
    return out


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"cmd failed: {' '.join(cmd[:8])}...\n{r.stderr[-400:]}")
    return r


def loudness(path):
    r = subprocess.run(["ffmpeg", "-i", path, "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    return float(j["input_i"])


def main():
    segs = []
    for n in range(1, 9):
        src = f"{SRC_DIR}/clip{n}_{TONE}.mp4"
        trimmed = f"{WORK}/trimmed/clip{n}.mp4"
        alpha = f"{WORK}/alpha/clip{n}.webm"
        seg = f"{WORK}/segs/seg{n}.mp4"
        segs.append(seg)
        if os.path.exists(seg) and os.path.getsize(seg) > 1000:
            print(f"[skip] seg{n}", flush=True)
            continue

        # 1. word-aware trim (transcript only needed when the trim isn't cached)
        if not os.path.exists(trimmed):
            first_w, last_w, pad = INTENDED[n]
            ws = words_for(n)
            start = next((w["start"] for w in ws if norm(w["word"]) == first_w), 0.0)
            end = next((w["end"] for w in reversed(ws) if norm(w["word"]) == last_w), None)
            if end is None:
                raise RuntimeError(f"clip{n}: last word '{last_w}' not found")
            start = max(0.0, start - 0.12)
            end = end + pad
            run(["ffmpeg", "-y", "-i", src, "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS),
                 "-c:a", "aac", "-b:a", "192k", trimmed])
            print(f"[trim] clip{n}: {start:.2f}-{end:.2f}s", flush=True)

        gain = -16.0 - loudness(trimmed)
        probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                                "-of", "csv=p=0", trimmed], capture_output=True, text=True)
        dur = float(probe.stdout.strip())

        if n <= 3:
            # ARTICLE SECTION (clips 1-3): matte + composite over the zoomed real article.
            # Persona ~69% of height (+33% per user 2026-06-10), bottom-pinned, slight x-sway
            # for the TikTok-dynamic feel. Title zone stays clear.
            if not os.path.exists(alpha):
                remove_background(trimmed, alpha)
                print(f"[matte] clip{n}", flush=True)
            frames = max(1, int(dur * FPS))
            card, recipe = ZP[n]
            zp = recipe.replace("{F}", str(frames))
            # animated marker: xfade-wiperight from the CLEAN page to the STROKED page in
            # page-space BEFORE zoompan — the highlight draws on L->R while the camera zooms
            # (crop can't animate w/h, so the wipe is done as a transition between layers)
            fc = (f"[0:v]scale=2160:3840,setsar=1,split=2[baseA][baseB];"
                  f"[3:v]scale=2160:3840,setsar=1[hl];"
                  f"[baseB][hl]overlay=x=0:y=0[stroked];"
                  f"[baseA][stroked]xfade=transition=wiperight:duration={HL_DUR}:offset={HL_T0}[page];"
                  f"[page]zoompan={zp}:d=1:s={W}x{H}:fps={FPS},setsar=1[bg];"
                  f"[1:v]scale=-2:880,setsar=1[fg];"
                  f"[bg][fg]overlay=x='(W-w)/2+5*sin(2*PI*t/4.5)':y=H-h:shortest=1,"
                  f"format=yuv420p[v]")
            run(["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-r", str(FPS),
                 "-i", f"{CARDS}/{card}.png",
                 "-c:v", "libvpx-vp9", "-i", alpha, "-i", trimmed,
                 "-loop", "1", "-t", f"{dur:.3f}", "-r", str(FPS),
                 "-i", f"{CARDS}/hl_{card}.png",
                 "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
                 "-af", f"volume={gain:+.2f}dB",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS),
                 "-c:a", "aac", "-b:a", "192k", "-shortest", seg])
            print(f"[seg/article] {seg} ({dur:.1f}s, gain {gain:+.1f}dB)", flush=True)
        else:
            # UGC SECTION (clips 4-8): back to full-frame talking head — no card, no matte
            # (user 2026-06-10: "after she goes through the article, get back to her ugc")
            run(["ffmpeg", "-y", "-i", trimmed, "-af", f"volume={gain:+.2f}dB",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-r", str(FPS),
                 "-c:a", "aac", "-b:a", "192k", seg])
            print(f"[seg/ugc] {seg} ({dur:.1f}s, gain {gain:+.1f}dB)", flush=True)

    # 4. concat + true-peak limiter
    lst = f"{WORK}/concat.txt"
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    final = f"{SRC_DIR}/f1_l4_{TONE}_v1.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-af", "alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", final])
    print(f"[final] {final}", flush=True)


if __name__ == "__main__":
    main()
