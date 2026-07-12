"""Finalize a series-2 video: verify each solo clip (Chowchilla + line-present), reroll bad ones
(<=MAX), trim each to its intended line, concat in order + loudnorm, Nick captions + Pulaski/Jones
disclaimer. 9:16 out.  Usage: wp_series2_finalize.py <video>   (relationship|moved|kids)
"""
import subprocess, re, sys, pathlib, os
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe
from wp_series2_produce import VIDEOS

MAX = 3; LEAD, TRAIL = 0.05, 0.25
def toks(s): return re.findall(r"[a-z0-9]+", s.lower())
def wt(w): return (w.get("text") or w.get("word") or "")

def analyze(path, line):
    res = scribe(path, biased_keywords=["Chowchilla"])
    ws = [w for w in res.get("words", []) if w.get("type") == "word"]
    if not ws: return None, False, "no speech"
    exp = toks(line); trans = [re.sub(r"[^a-z0-9]", "", wt(w).lower()) for w in ws]
    matched_idx = []; ei = 0
    for j, t in enumerate(trans):
        if ei < len(exp) and t == exp[ei]: matched_idx.append(j); ei += 1
    ok = ei >= 0.8 * len(exp)
    reason = "ok" if ok else f"missing ({ei}/{len(exp)}, {len(trans)}w)"
    if ok and "chowchilla" in line.lower():
        full = " ".join(wt(w).lower() for w in scribe(path).get("words", []))
        if "chauch" in full or "chochil" in full: ok, reason = False, "Chowchilla mispron"
        elif "chowchill" not in full: ok, reason = False, "Chowchilla unclear"
    span = None
    if matched_idx:
        span = (max(0, ws[matched_idx[0]]["start"] - LEAD), ws[matched_idx[-1]]["end"] + TRAIL)
    return span, ok, reason

def main():
    video = sys.argv[1]
    cfg = VIDEOS[video]; D = pathlib.Path(f"outputs/wp_series2/{video}")
    pieces, lines = [], []
    for idx, spk, line in cfg["turns"]:
        path = D / f"t{idx:02d}_{spk}.mp4"; span = None
        for a in range(1, MAX + 1):
            if not path.exists():
                subprocess.run([".venv/bin/python", "scripts/wp_series2_produce.py", video, str(idx)],
                               capture_output=True, env={**os.environ, "PYTHONPATH": "."})
            if not path.exists(): print(f"{video} t{idx} GEN FAILED"); break
            span, ok, reason = analyze(str(path), line)
            print(f"{video} t{idx} a{a}: {reason}", flush=True)
            if ok: break
            path.unlink(missing_ok=True); span = None
        if span is None: continue
        s, e = span; p = str(D / f"_c{idx:02d}.mp4")
        subprocess.run(["ffmpeg","-y","-i",str(path),"-ss",str(round(s,2)),"-to",str(round(e,2)),
            "-vf","scale=720:1280,setsar=1,fps=30","-c:v","libx264","-preset","fast","-crf","20",
            "-c:a","aac","-b:a","192k",p],capture_output=True)
        pieces.append(p); lines.append(f"file '{pathlib.Path(p).resolve()}'")

    lst = D / "_concat.txt"; lst.write_text("\n".join(lines) + "\n")
    raw = str(D / f"{video}_9x16.mp4")
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-preset","fast","-crf","20",
        "-c:a","aac","-b:a","192k",raw],capture_output=True)
    # Nick captions + Pulaski/Jones disclaimer
    nick = f"/tmp/{video}_nick.mp4"
    subprocess.run([".venv/bin/python","scripts/caption_nick.py",raw,"--out",nick],
                   capture_output=True, env={**os.environ,"PYTHONPATH":"."})
    final = str(pathlib.Path(f"outputs/wp_series2/FINAL_{video}.mp4"))
    subprocess.run([".venv/bin/python","scripts/burn_disclaimer.py",nick,final],
                   capture_output=True, env={**os.environ,"PYTHONPATH":"."})
    web = final.replace(".mp4","_web.mp4")
    subprocess.run(["ffmpeg","-y","-i",final,"-c:v","libx264","-preset","fast","-crf","26",
        "-c:a","aac","-b:a","128k",web],capture_output=True)
    dur = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",final],
                         capture_output=True,text=True).stdout.strip()
    print(f"SERIES2 FINAL {video} -> {final} ({dur}s)")

if __name__ == "__main__":
    main()
