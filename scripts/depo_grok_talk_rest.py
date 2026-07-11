#!/usr/bin/env python3
"""Remaining Grok talking beats (3-11) for the Depo interview, clean audio.
Gaze: speaker looks at the OTHER person off-camera (doc=left, surv=right), NOT the lens —
EXCEPT the CTA (doc_cta) which looks DIRECTLY INTO the lens per user lock.
Skip-if-exists. Run: .venv/bin/python scripts/depo_grok_talk_rest.py [--only a,b]
"""
import sys, argparse, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/clips_grok"); OUT.mkdir(parents=True, exist_ok=True)
SURV = REF / "surv_face_v1.png"
DOC = REF / "doc_alone_v1_L.png"

AMB = "Only her voice and faint room ambience — no other voices, no murmurs, no background chatter."

def surv(dialogue, tone):
    return (f"The woman sits in the armchair, speaking to an interviewer off to her right, looking "
            f"toward them, not at the camera. {tone} She says: \"{dialogue}\" {AMB}")

def doc(dialogue, tone):
    return (f"The woman sits in the armchair, speaking warmly to someone off to her left, looking "
            f"toward them, not at the camera. {tone} She says: \"{dialogue}\" {AMB}")

# (name, anchor, duration_str, prompt)
CLIPS = [
 ("gtalk_doc_2", DOC, "6",
   doc("So what changed your mind about it just being bad luck?", "Gently probing, curious.")),
 ("gtalk_surv_2", SURV, "10",
   surv("A lawyer showed me the studies. Women on the Depo shot for over a year were up to five "
        "times more likely to get one.", "Quiet, steady, a little disbelief.")),
 ("gtalk_surv_3", SURV, "6",
   surv("Five times. That is not bad luck. And nobody ever warned me.", "Firm, wounded, plain.")),
 ("gtalk_doc_3", DOC, "7",
   doc("And you are not alone in this. So many other women are finding out the very same thing.",
       "Warm, reassuring.")),
 ("gtalk_surv_4", SURV, "8",
   surv("Not even close. Thousands of women. Same diagnosis, same shot. There is a federal lawsuit "
        "now.", "Steady, connected, quiet resolve.")),
 ("gtalk_doc_4", DOC, "6",
   doc("So what can someone actually do about it? Where would a person even start?",
       "Practical, gentle.")),
 ("gtalk_surv_5", SURV, "9",
   surv("You answer a few private questions online. Your diagnosis, how long you were on Depo. It "
        "takes about a minute.", "Helpful, calm, encouraging.")),
 ("gtalk_surv_6", SURV, "10",
   surv("A lawyer reviews it for free. No court, it is confidential, and even if it was years ago, "
        "you may still qualify.", "Warm, reassuring, low-key.")),
 ("gtalk_doc_cta", DOC, "9",
   "The woman sits in the armchair and looks DIRECTLY INTO the camera lens, speaking straight to "
   "the viewer, warm and sincere with a small caring nod. She says: \"If you or someone you love "
   "has a brain meningioma and was ever on Depo, you may qualify for significant compensation. Tap "
   "below and take the two-minute check.\" " + AMB),
]

def gen(name, anchor, dur, prompt):
    out = OUT / f"{name}.mp4"
    if out.exists(): print("skip", name); return
    url = kie.upload_file(str(anchor))
    payload = {"model":"grok-imagine/image-to-video","input":{"image_urls":[url],"prompt":prompt,
               "mode":"normal","duration":dur,"resolution":"720p","aspect_ratio":"9:16"}}
    r = requests.post(kie.JOBS_CREATE, headers=kie.HEADERS, json=payload)
    tid = (r.json().get("data") or {}).get("taskId")
    if not tid: print("FAIL create", name, r.json()); return
    res = kie._poll_jobs(tid, f"Grok {name}")
    if res.get("status") == "success" and res.get("urls"):
        kie.download(res["urls"][0], out); print("done", name)
    else: print("FAIL", name, str(res.get("raw"))[:200])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="")
    a = ap.parse_args()
    items = CLIPS
    if a.only:
        keep = set(a.only.split(",")); items = [c for c in CLIPS if c[0] in keep]
    for c in items: gen(*c)
    print("ALL DONE")

if __name__ == "__main__":
    main()
