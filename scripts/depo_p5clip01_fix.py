"""p5 clip01 deterministically TIMES OUT on Veo across all model tiers (free low-pri + paid
veo-3.1-lite/fast) — it's the specific anchor+prompt combo, not priority/throttle. Fix by changing
the inputs: anchor = a clean frame from the already-working p5 clip02 (same persona, Veo-proven),
simpler motion prompt, dur=8. Standard useapi Lite (low-priority, the locked path).
  .venv/bin/python scripts/depo_p5clip01_fix.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depo_testimonial_gen import PERSONAS, P, last_word
from googleflow_client import generate_veo, upload_asset, download

# clean anchor from a WORKING p5 clip (same woman, known-good to Veo)
src = "outputs/depo_testimonial/p5_headwrap/clip02.mp4"
anchor = "/tmp/p5_c01_anchor.jpg"
subprocess.run(["ffmpeg", "-y", "-ss", "1.4", "-i", src, "-frames:v", "1", "-q:v", "2", anchor],
               check=True, capture_output=True)
mgid = upload_asset(anchor, "image/jpeg")

line = "When the doctor said the words brain tumor, everything just stopped. A meningioma."
prompt = P(PERSONAS["p5"]["reg"], PERSONAS["p5"]["voice"], line,
           "Quiet and serious, holding the emotion in.",
           "Small natural movements, a slight nod.",
           '"meningioma" = "men-in-jee-OH-muh".', last_word(line))
dest = "outputs/depo_testimonial/p5_headwrap/clip01.mp4"

print("gen p5 clip01: anchor=working-clip02-frame, simplified prompt, dur=8, useapi lite ...", flush=True)
r = generate_veo(prompt, image_mgid=mgid, duration=8, aspect_ratio="portrait", attempts=3)
if r.get("status") == "success" and r.get("urls"):
    download(r["urls"][0], dest)
    print(f"[OK] -> {dest}", flush=True)
else:
    print(f"[FAIL] {str(r.get('raw'))[:220]}", flush=True)
