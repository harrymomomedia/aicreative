"""Finalize a series-2 video: verify each solo clip (Chowchilla + line-present), reroll bad ones
(<=MAX), trim each to its intended line, concat in order + loudnorm, Nick captions + Pulaski/Jones
disclaimer. 9:16 out.  Usage: wp_series2_finalize.py <video>   (relationship|moved|kids)
"""
import subprocess, sys, pathlib, os, shutil
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from wp_series2_produce import VIDEOS
from veo_clip_qa import qa_clip                # consolidated 7-check per-clip QA gate

MAX = 3

def analyze(path, line):
    """Thin adapter over the shared veo_clip_qa gate -> (span, recall, reason) for the assemble loop.
    A clip that fails ANY check (transcript / improv / male-voice / two-voice / pronunciation /
    underfill) gets recall forced to 0 so keep-best prefers a clean take."""
    pron = ["Chowchilla"] if "chowchilla" in line.lower() else []
    v = qa_clip(path, line, gender="female", proper_nouns=pron)
    recall = v["recall"] if v["ok"] else 0.0
    reason = "ok" if v["ok"] else ",".join(v["fails"])
    return v["span"], recall, reason

def main():
    video = sys.argv[1]
    cfg = VIDEOS[video]; D = pathlib.Path(f"outputs/wp_series2/{video}")
    pieces, lines = [], []
    for idx, spk, line in cfg["turns"]:
        path = D / f"t{idx:02d}_{spk}.mp4"
        best = None  # (recall, span, saved_take_path)
        for a in range(1, MAX + 1):
            if not path.exists():
                subprocess.run([".venv/bin/python", "scripts/wp_series2_produce.py", video, str(idx)],
                               capture_output=True, env={**os.environ, "PYTHONPATH": "."})
            if not path.exists(): print(f"{video} t{idx} a{a}: GEN FAILED", flush=True); continue
            span, recall, reason = analyze(str(path), line)
            print(f"{video} t{idx} a{a}: {reason} r={recall:.2f}", flush=True)
            if span and (best is None or recall > best[0]):
                take = D / f"_take{idx:02d}.mp4"; shutil.copy(str(path), str(take))
                best = (recall, span, str(take))
            if recall >= 0.8: break
            path.unlink(missing_ok=True)          # reroll for a better take
        if best is None: print(f"{video} t{idx} DROPPED"); continue
        # keep the BEST take across attempts (never drop a present-but-imperfect beat)
        recall, span, take = best
        if not path.exists(): shutil.copy(take, str(path))
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
