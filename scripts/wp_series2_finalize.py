"""Finalize a series-2 video: verify each solo clip (Chowchilla + line-present), reroll bad ones
(<=MAX), trim each to its intended line, concat in order + loudnorm, Nick captions + Pulaski/Jones
disclaimer. 9:16 out.  Usage: wp_series2_finalize.py <video>   (relationship|moved|kids)
"""
import subprocess, re, sys, pathlib, os, shutil, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe
from wp_series2_produce import VIDEOS

# --- voice-gender gate: every persona is female; flag any clip where a male voice appears
# (Veo TTS non-deterministically renders a male voice or injects a 2nd speaker, esp. in
# underfilled clips). male_frac = fraction of voiced frames in male pitch range (<160 Hz). ---
MALE_MAX = 0.22
def male_frac(mp4):
    try:
        import numpy as np, librosa
    except Exception:
        return 0.0
    wav = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg","-y","-i",mp4,"-ac","1","-ar","16000",wav], capture_output=True)
    try:
        y, sr = librosa.load(wav, sr=16000)
    finally:
        try: os.remove(wav)
        except OSError: pass
    import numpy as np, librosa
    f0, _, _ = librosa.pyin(y, fmin=70, fmax=350, sr=sr)
    v = f0[~np.isnan(f0)]
    if len(v) == 0: return 0.0
    return float(np.sum(v < 160) / len(v))

MAX = 3; LEAD, TRAIL = 0.05, 0.25
# number-word <-> digit + benign colloquial folds so Scribe's rendering ("11" for "eleven",
# "gonna" for "going to") doesn't false-reject an otherwise-correct free-tier take.
NUMS = {"11": "eleven", "31": "thirtyone", "2": "two", "6": "six", "eleven": "eleven",
        "thirtyone": "thirtyone", "two": "two", "six": "six"}
def _canon(tok):
    return NUMS.get(tok, tok)
def _clean(t):
    # strip ALL non-alphanumerics WITHIN a token (apostrophes, hyphens, periods) so both the
    # expected line and the Scribe words tokenize identically ("didn't"->"didnt", not "didn"+"t").
    return re.sub(r"[^a-z0-9]", "", t.lower())
def toks(s):
    out = []
    for t in s.split():
        c = _canon(_clean(t))
        if c: out.append(c)
    return out
def wt(w): return (w.get("text") or w.get("word") or "")

def tight_span(exp, trans):
    """Return (i,j,matched) for the window in `trans` best matching `exp` as an ordered subsequence,
    trimming leading/mid/trailing improv. Tolerates a corrupted leading/trailing expected word by
    allowing the match to begin a few expected-words in (Scribe sometimes garbles the first word,
    e.g. 'Shame'->'deshame'). Picks max matched words, then tightest span."""
    best = None  # (start, last, span_len, matched)
    for off in range(0, min(3, len(exp))):          # tolerate up to 2 corrupted leading exp words
        e0 = exp[off]
        for start in range(len(trans)):
            if trans[start] != e0:
                continue
            ei, j, last = off, start, start
            while j < len(trans) and ei < len(exp):
                if trans[j] == exp[ei]:
                    ei += 1; last = j
                j += 1
            matched = ei - off
            if matched > 0:
                span_len = last - start
                if best is None or matched > best[3] or (matched == best[3] and span_len < best[2]):
                    best = (start, last, span_len, matched)
    if best is None:
        return None
    return best[0], best[1], best[3]

def analyze(path, line):
    res = scribe(path, biased_keywords=["Chowchilla"])
    ws = [w for w in res.get("words", []) if w.get("type") == "word"]
    if not ws: return None, 0.0, "no speech"
    exp = toks(line)
    trans = [_canon(_clean(wt(w))) for w in ws]
    ts = tight_span(exp, trans)
    if ts is None: return None, 0.0, f"nomatch (0/{len(exp)}, {len(trans)}w)"
    i, j, matched = ts
    recall = matched / len(exp)
    reason = "ok" if recall >= 0.8 else f"low ({matched}/{len(exp)}, {len(trans)}w)"
    if recall >= 0.8 and "chowchilla" in line.lower():
        full = " ".join(wt(w).lower() for w in scribe(path).get("words", []))
        if "chauch" in full or "chochil" in full: reason = "Chowchilla mispron"; recall = 0.0
        elif "chowchill" not in full: reason = "Chowchilla unclear"; recall = 0.0
    mf = male_frac(path)
    if recall >= 0.8 and mf > MALE_MAX:
        reason = f"MALE VOICE ({mf*100:.0f}%)"; recall = 0.0   # female persona -> reject male/2-voice
    span = (max(0, ws[i]["start"] - LEAD), ws[j]["end"] + TRAIL)
    return span, recall, reason

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
