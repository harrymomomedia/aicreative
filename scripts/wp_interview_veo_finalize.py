"""Autonomous finalize for the VEO interview: for each turn clip, dissect + check
(1) no heavy improv (transcript ~matches the intended line) and (2) Chowchilla pronunciation
if applicable; RE-ROLL bad clips up to MAX times; then assemble. Prints a problem report.
"""
import subprocess, re, sys, pathlib, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe
from wp_interview_veo_produce import TURNS

D = pathlib.Path("outputs/wp_voxpop/interview_veo")
MAX = 3

def toks(s): return re.findall(r"[a-z0-9]+", s.lower())
def wt(w): return (w.get("text") or w.get("word") or "")

def check(path, line):
    """Return (ok, reason). Bad if improv (weak subsequence match OR too many extra words)
    or Chowchilla mispronounced."""
    res = scribe(path, biased_keywords=["Chowchilla"])
    ws = [w for w in res.get("words", []) if w.get("type") == "word"]
    if not ws: return False, "no speech"
    exp = toks(line); trans = [re.sub(r"[^a-z0-9]", "", wt(w).lower()) for w in ws]
    # subsequence match count
    ei = 0
    for tw_ in trans:
        if ei < len(exp) and tw_ == exp[ei]: ei += 1
    matched = ei
    if matched < 0.7 * len(exp): return False, f"missing words ({matched}/{len(exp)})"
    if len(trans) > len(exp) * 1.7 + 3: return False, f"improv ({len(trans)} words vs {len(exp)})"
    if "chowchilla" in line.lower():
        # isolate the word, transcribe unbiased
        hit = next((w for w in ws if "chow" in wt(w).lower() or "chau" in wt(w).lower()
                    or "chill" in wt(w).lower()), None)
        if hit:
            wav = tempfile.mktemp(suffix=".wav")
            subprocess.run(["ffmpeg","-y","-i",path,"-ss",str(max(0,hit["start"]-0.15)),
                "-to",str(hit["end"]+0.2),"-vn","-ar","22050","-ac","1",wav],capture_output=True)
            iso = scribe(wav).get("text","").lower()
            if not ("chowchill" in iso or ("chow" in iso and "chill" in iso)):
                return False, f"Chowchilla mispron ({iso.strip()!r})"
        else:
            return False, "Chowchilla not found"
    return True, "ok"

report = []
for idx, spk, line in TURNS:
    path = D / f"t{idx:02d}_{spk}.mp4"
    for attempt in range(1, MAX + 1):
        if not path.exists():
            subprocess.run(["python", "scripts/wp_interview_veo_produce.py", str(idx)],
                           capture_output=True, env={**__import__("os").environ, "PYTHONPATH": "."})
        if not path.exists():
            report.append((idx, "GEN FAILED")); break
        ok, reason = check(str(path), line)
        print(f"t{idx:02d} attempt {attempt}: {reason}", flush=True)
        if ok:
            report.append((idx, "ok")); break
        path.unlink(missing_ok=True)           # reroll
        if attempt == MAX: report.append((idx, f"STILL BAD: {reason}"))
print("=== VEO CLIP REPORT ===")
for idx, st in report: print(f"  t{idx}: {st}")
print("VEO FINALIZE DONE")
