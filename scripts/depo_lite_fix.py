"""Re-roll the problem Depo clips on useapi google-flow Veo 3.1 Lite (the locked generation path).
Fixes: p4 clip03 (Depo pron), p5 clip01 (was missing — Lite failed it earlier), p5 clip03 (burned
text + Depo). Tighter 'Depo' respell to kill the "depot" mishearing. Persona-still anchor (startImage).
Downloads ONLY on success, so a failed re-roll never clobbers an existing clip.

  .venv/bin/python scripts/depo_lite_fix.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from depo_testimonial_gen import CLIPS, PERSONAS, P, last_word
from googleflow_client import generate_veo, upload_asset, download   # useapi google-flow veo-3.1-lite

CBY = {c[0]: c for c in CLIPS}
DEPO_TIGHT = ('"Depo" said as "DEP-oh" with a short e like in "deck" — NOT "dee-po", '
              'NOT "depot" (no T sound at the end).')

FIXES = [
    ("p4", "clip03", DEPO_TIGHT),
    ("p5", "clip01", None),
    ("p5", "clip03", DEPO_TIGHT),
]


def main():
    mgid = {}
    for pkey in {f[0] for f in FIXES}:
        mgid[pkey] = upload_asset(PERSONAS[pkey]["anchor"])
        print(f"[{pkey}] anchor uploaded", flush=True)

    for pkey, cid, pron_ovr in FIXES:
        _, line, dur, tone, body, pron = CBY[cid]
        prompt = P(PERSONAS[pkey]["reg"], PERSONAS[pkey]["voice"], line, tone, body, pron_ovr or pron, last_word(line))
        dest = os.path.join(PERSONAS[pkey]["out"], f"{cid}.mp4")
        print(f"[{pkey} {cid}] useapi lite (dur={dur}) ...", flush=True)
        r = generate_veo(prompt=prompt, image_mgid=mgid[pkey], duration=dur, aspect_ratio="portrait")
        if r.get("status") == "success" and r.get("urls"):
            download(r["urls"][0], dest)
            print(f"[ok] {pkey} {cid} -> {dest}", flush=True)
        else:
            print(f"[FAIL] {pkey} {cid}: {str(r.get('raw'))[:200]}", flush=True)


if __name__ == "__main__":
    main()
