"""Quick QA for the 11 new clip-1 generations.

For each variation:
  - Extract two QA frames (t=0.5s, t=7s) via ffmpeg in parallel
  - Transcribe via ElevenLabs Scribe (with biased_keywords for proper nouns)
  - Print spoken text vs intended

Output: prints a comparison table + the JPG paths so they can be Read inline.

Why Scribe (not Whisper): catches proper nouns ("Chowchilla", "Miha") and
near-homophones ("past"/"passed", "below"/"the low") that Whisper-small misses.
"""
import sys, subprocess, concurrent.futures, pathlib
sys.path.insert(0, "/Users/harry/aicreative")
from scripts.chowchilla_a2_variations import VARIATIONS
from elevenlabs_client import scribe

BASE = pathlib.Path("/Users/harry/aicreative/outputs/0502_a2_variations")
TARGETS = ["V4", "V5", "V7", "V8", "V9", "V10", "V12", "V14", "V15", "V18", "V20"]
BIASED = ["Chowchilla:3.0", "Miha:2.5", "CCWF:2.0"]


def extract_frame(v, t):
    src = BASE / v / "clip1_poyo.mp4"
    dst = BASE / v / f"qa_t{int(t*10):02d}.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dst)],
        capture_output=True,
    )
    return dst


print("[1/2] extracting QA frames in parallel", flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs = []
    for v in TARGETS:
        futs.append(ex.submit(extract_frame, v, 0.5))
        futs.append(ex.submit(extract_frame, v, 7.0))
    for f in concurrent.futures.as_completed(futs):
        f.result()

print("[2/2] ElevenLabs Scribe transcribe (parallel, max 4 concurrent)", flush=True)


def transcribe_one(v):
    src = BASE / v / "clip1_poyo.mp4"
    r = scribe(str(src), biased_keywords=BIASED, language_code="en",
               timestamps_granularity="none")
    actual = r.get("text", "").strip()
    intended = VARIATIONS[v]["clips"][0]
    match = actual.lower().replace(".", "").replace(",", "") == intended.lower().replace(".", "").replace(",", "")
    return v, intended, actual, match


results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(transcribe_one, v) for v in TARGETS]
    for f in concurrent.futures.as_completed(futs):
        results.append(f.result())

# Sort by original order for predictable output
order = {v: i for i, v in enumerate(TARGETS)}
results.sort(key=lambda r: order[r[0]])

print("\n=== TRANSCRIPT vs INTENDED ===")
for v, intended, actual, match in results:
    flag = "✓" if match else "✗"
    print(f"\n{flag} {v}")
    print(f"  intended: {intended}")
    print(f"  actual:   {actual}")
