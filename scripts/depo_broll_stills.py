#!/usr/bin/env python3
"""Recovery/surgery/scan b-roll stills for the Depo interview, documentary-news realistic.
- scan: MRI brain scan on a radiology monitor with a visible meningioma mass (t2i)
- surgery: neurosurgery OR, masked team under overhead lights (t2i)
- recovery: THE survivor resting in a hospital bed, small head bandage (i2i from surv_face_v1 -> keep face)
Skip-if-exists. Run: .venv/bin/python scripts/depo_broll_stills.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/broll"); OUT.mkdir(parents=True, exist_ok=True)
SURV = str(REF / "surv_face_v1.png")

DOC = ("Photoreal news b-roll cinematography, shot like a Frontline / PBS Newshour documentary "
       "segment. Natural color grading, real-world hospital lighting, slight handheld feel, slight "
       "grain. NOT cinematic, NOT stylized. No on-screen text, no captions, no logos.")

STILLS = [
 ("scan", None,
  "A neurologist's dim reading room. A radiology monitor shows an MRI brain scan with a clear "
  "rounded meningioma mass near the surface of the brain; a doctor's hand points at it with a pen. "
  "Close, over-the-shoulder documentary framing. " + DOC),
 ("surgery", None,
  "A neurosurgery in progress: a masked surgical team in scrubs works under bright overhead "
  "operating-room lights, focused, vital-sign monitors glowing in the background. Documentary "
  "middle framing, identities partly obscured by masks and angle. " + DOC),
 ("recovery", SURV,
  "resting in a hospital bed, propped on a pillow, a small gauze bandage on the side of her head, "
  "a hospital gown, an IV line and a vitals monitor beside her, eyes softly open, calm and tired. "
  "Documentary framing, natural hospital light. " + DOC),
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
