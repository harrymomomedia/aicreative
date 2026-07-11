"""Assemble the VEO interview (one-speaker-per-clip). Each clip -> crop to its speaker (L/R from
filename), trim to speech span (Scribe word-timings), concat + loudnorm. Output 9:16 master.
"""
import subprocess, glob, pathlib, sys, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe
from wp_interview_veo_produce import TURNS

D = pathlib.Path("outputs/wp_voxpop/interview_veo")
CROP_W, H = 405, 720
X_L, X_R = 120, 740
LEAD, TRAIL = 0.05, 0.22
TARGET_WPS = 2.3
LINES = {idx: line for idx, spk, line in TURNS}   # idx -> intended line

def _tok(s): return re.findall(r"[a-z0-9]+", s.lower())

def span(f, intended):
    """Trim to ONLY the intended scripted line (subsequence match) — drops Veo improv/backchannels
    before and after, and the silent-other's leaked words."""
    res = scribe(f, biased_keywords=["Chowchilla"])
    ws = [w for w in res.get("words", []) if w.get("type") == "word"]
    if not ws: return 0.0, None, 0
    exp = _tok(intended)
    # greedy subsequence: find matched transcript indices for exp
    def wt(w): return (w.get("text") or w.get("word") or "")
    matched, ei = [], 0
    for j, w in enumerate(ws):
        if ei < len(exp) and re.sub(r"[^a-z0-9]", "", wt(w).lower()) == exp[ei]:
            matched.append(j); ei += 1
    if len(matched) < max(2, len(exp)//2):     # weak match -> fall back to full span
        return max(0.0, ws[0]["start"]-LEAD), ws[-1]["end"]+TRAIL, len(ws)
    s = max(0.0, ws[matched[0]]["start"] - LEAD)
    e = ws[matched[-1]]["end"] + TRAIL
    return s, e, len(matched)

clips = sorted(glob.glob(str(D / "t[0-9][0-9]_*.mp4")))
clips = [c for c in clips if "_qa" not in c]
pieces, lines = [], []
for i, c in enumerate(clips):
    spk = "L" if c.rstrip(".mp4").endswith("_L") else "R"
    x = X_L if spk == "L" else X_R
    idx = int(re.search(r"t(\d+)_", pathlib.Path(c).name).group(1))
    s, e, n = span(c, LINES[idx])
    dur = (e - s) if e else 8.0
    # pace-correct: if the clip drags (Veo stretched a short line), speed it up toward TARGET_WPS
    factor = 1.0
    if n and dur > 0:
        wps = n / dur
        if wps < 1.5:                      # only rescue genuinely dragging clips, gently
            factor = min(1.35, 2.0 / wps)
    to = ["-to", str(round(e, 2))] if e else []
    vf = f"crop={CROP_W}:{H}:{x}:0,scale=720:1280,setsar=1,setpts=PTS/{factor:.3f},fps=30"
    af = f"atempo={factor:.3f}"
    p = str(D / f"_p{i:02d}.mp4")
    subprocess.run(["ffmpeg","-y","-i",c,"-ss",str(round(s,2)),*to,
        "-vf",vf,"-af",af,
        "-c:v","libx264","-preset","fast","-crf","20","-c:a","aac","-b:a","192k",p],
        capture_output=True)
    pieces.append(p); lines.append(f"file '{pathlib.Path(p).resolve()}'")
    print(f"[{pathlib.Path(c).name}] {spk} {round(s,2)}->{round(e,2) if e else 'end'} n={n} x{factor:.2f}")

lst = D / "_concat.txt"; lst.write_text("\n".join(lines) + "\n")
out = str(D / "interview_veo_9x16.mp4")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-preset","fast","-crf","20",
    "-c:a","aac","-b:a","192k",out],capture_output=True)
subprocess.run(["ffmpeg","-y","-i",out,"-c:v","libx264","-preset","fast","-crf","26",
    "-c:a","aac","-b:a","128k",out.replace(".mp4","_web.mp4")],capture_output=True)
dur = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",out],
                     capture_output=True,text=True).stdout.strip()
print(f"[done] {out}  ({dur}s)")
