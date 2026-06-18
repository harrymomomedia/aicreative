"""Escalate the stuck/flagged Depo testimonial clips to Veo 3.1 Fast on Poyo ($0.10/clip),
after free google-flow Lite failed them. Same prompt locks + persona-still anchors as
depo_testimonial_gen.py; tighter 'Depo' respell to kill the "depot" mishearing.

Fixes: p4 clip03 (Depo pron), p5 clip01 (6x Lite timeout/captcha), p5 clip03 (burned text + Depo).
  .venv/bin/python scripts/depo_poyo_fix.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))          # scripts/  -> depo_testimonial_gen
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # repo root -> clients
from depo_testimonial_gen import CLIPS, PERSONAS, P, last_word
import kie_client as kie
from poyo_client import generate_veo as poyo_veo, download as poyo_dl

CBY = {c[0]: c for c in CLIPS}
DEPO_TIGHT = ('"Depo" said as "DEP-oh" with a short e like in "deck" — NOT "dee-po", '
              'NOT "depot" (no T sound at the end).')

# (persona, clip id, pron override or None)
FIXES = [
    ("p4", "clip03", DEPO_TIGHT),
    ("p5", "clip01", None),
    ("p5", "clip03", DEPO_TIGHT),
]


def main():
    # upload each needed persona still to KIE once -> anchor URL
    anchor_url = {}
    for pkey in {f[0] for f in FIXES}:
        anchor_url[pkey] = kie.upload_file(PERSONAS[pkey]["anchor"])
        print(f"[{pkey}] anchor uploaded -> {anchor_url[pkey][:60]}...", flush=True)

    for pkey, cid, pron_override in FIXES:
        _, line, dur, tone, body, pron = CBY[cid]
        pron_use = pron_override or pron
        prompt = P(PERSONAS[pkey]["reg"], PERSONAS[pkey]["voice"], line, tone, body, pron_use, last_word(line))
        dest = os.path.join(PERSONAS[pkey]["out"], f"{cid}.mp4")
        print(f"[{pkey} {cid}] submitting to Poyo veo3.1-fast...", flush=True)
        res = poyo_veo(prompt, image_urls=[anchor_url[pkey], anchor_url[pkey]],
                       aspect_ratio="9:16", model="veo3.1-fast", generation_type="frame")
        if res.get("status") == "success" and res.get("urls"):
            poyo_dl(res["urls"][0], dest)
            print(f"[ok] {pkey} {cid} -> {dest}", flush=True)
        else:
            print(f"[FAIL] {pkey} {cid}: {str(res.get('raw'))[:200]}", flush=True)


if __name__ == "__main__":
    main()
