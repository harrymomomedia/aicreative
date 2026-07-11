"""Objective Chowchilla-pronunciation QA gate (no human ear needed).
Scribe normalizes the word in-sentence even when mispronounced, so we ISOLATE the word
(via word-timings) and transcribe it ALONE, unbiased. A correct take renders 'chow...';
a mispronounced take renders 'chau...'/'cha...'/something else.
Usage: python scripts/wp_verify_chowchilla.py <clip.mp4>   -> prints RENDER + PASS/FAIL, exit 0/1
"""
import sys, subprocess, tempfile, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe

clip = sys.argv[1]
# 1) full transcript (biased) to locate the word
full = scribe(clip, biased_keywords=["Chowchilla"])
words = [w for w in full.get("words", []) if w.get("type") == "word"]
hit = next((w for w in words if "chow" in w["text"].lower() or "chill" in w["text"].lower()
            or "chau" in w["text"].lower()), None)
if not hit:
    print("FAIL: 'Chowchilla' not found in transcript"); sys.exit(1)
s = max(0.0, hit["start"] - 0.15); e = hit["end"] + 0.20
wav = tempfile.mktemp(suffix=".wav")
subprocess.run(["ffmpeg","-y","-i",clip,"-ss",str(s),"-to",str(e),"-vn","-ar","22050","-ac","1",wav],
               capture_output=True)
# 2) transcribe the isolated word UNBIASED — exposes the true phonetics
iso = scribe(wav).get("text", "").strip()
low = iso.lower()
ok = "chowchill" in low or ("chow" in low and "chill" in low)
print(f"isolated render: {iso!r}  -> {'PASS' if ok else 'FAIL (mispronounced)'}")
sys.exit(0 if ok else 1)
