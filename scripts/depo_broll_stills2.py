#!/usr/bin/env python3
"""Two more clean b-roll stills matching the existing AdMachin Depo library style
(ad 00 bandaged-head hospital-bed recovery, ad 06 surgical scar) but WITHOUT burned captions/PIP,
so they cut cleanly into the interview.
- recovery: THE survivor (i2i from surv_face_v1) in a hospital bed, white head bandage, IV, resting.
- scar: close-up of a fresh curved surgical scar/staples along a shaved scalp (t2i, generic).
Run: .venv/bin/python scripts/depo_broll_stills2.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/broll"); OUT.mkdir(parents=True, exist_ok=True)
SURV = str(REF / "surv_face_v1.png")

DOC = ("Photoreal, real hospital lighting, shot like a candid phone photo / documentary segment, "
       "slight grain, NOT cinematic, NOT stylized. No on-screen text, no captions, no logos.")

STILLS = [
 ("recovery", SURV,
  "lying in a hospital bed propped on a pillow, a white gauze bandage wrapped around the top of her "
  "head, a hospital gown, an IV line in her hand and a vitals monitor beside the bed, eyes closed "
  "or softly open, resting and tired after brain surgery. Chest-up framing. " + DOC),
 ("scar", None,
  "Extreme close-up of the side of a woman's head after brain surgery: a fresh curved surgical "
  "incision with neat staples runs along the shaved scalp, short dark regrowing hair around it, "
  "skin slightly bruised. Documentary close-up framing. " + DOC),
]

def gen(name, ref, prompt):
    out = OUT / f"broll_{name}.png"
    if out.exists(): print("skip", name); return
    kw = {"aspect_ratio":"9:16","resolution":"2K"}
    if ref: kw["image_urls"] = [ref]
    res = kie.generate_gpt_image(prompt, **kw)
    if res.get("status") == "success" and res.get("urls"):
        kie.download(res["urls"][0], out); print("done", name, out)
    else: print("FAIL", name, str(res.get("raw"))[:200])

for s in STILLS: gen(*s)
print("ALL DONE")
