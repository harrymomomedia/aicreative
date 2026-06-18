"""One-off: generate the stuck p5 clip01 on the PAID normal-priority useapi google-flow Lite tier
(`veo-3.1-lite`, NOT the free `veo-3.1-lite-low-priority` queue that keeps timing out / hitting the
anti-abuse throttle). Priority is baked into the model id, so the paid tier is what avoids the
preemption. Still useapi Lite. Tries a couple model ids in case the exact name differs.
  .venv/bin/python scripts/depo_p5clip01_hipri.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depo_testimonial_gen import CLIPS, PERSONAS, P, last_word
from googleflow_client import generate_veo, upload_asset, download

cid, line, dur, tone, body, pron = next(x for x in CLIPS if x[0] == "clip01")
pkey = "p5"
mgid = upload_asset(PERSONAS[pkey]["anchor"])
prompt = P(PERSONAS[pkey]["reg"], PERSONAS[pkey]["voice"], line, tone, body, pron, last_word(line))
dest = f"{PERSONAS[pkey]['out']}/clip01.mp4"

for model in ["veo-3.1-lite", "veo-3.1-fast"]:
    print(f"=== trying model={model} (dur={dur}) ===", flush=True)
    r = generate_veo(prompt, image_mgid=mgid, duration=dur, aspect_ratio="portrait",
                     model=model, attempts=2)
    if r.get("status") == "success" and r.get("urls"):
        download(r["urls"][0], dest)
        print(f"[OK] {model} -> {dest}", flush=True)
        break
    print(f"[fail {model}] {str(r.get('raw'))[:180]}", flush=True)
