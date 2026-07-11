#!/usr/bin/env python3
"""'The Insider' stacked interview — Grok Imagine clips (clean audio + silent listeners).
Subject = former nurse (gaze frame-right), Interviewer = documentarian (gaze frame-left).
CTA looks into the lens. Durations matched to word count (~2.4 wps). Em-dashes stripped.
Skip-if-exists. Run: [--only name1,name2]
"""
import sys, argparse, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

R = Path("outputs/depo_insider/reference")
OUT = Path("outputs/depo_insider/clips_grok"); OUT.mkdir(parents=True, exist_ok=True)
SURV = R / "surv_anchor_R.png"   # nurse-survivor, gaze frame-right
DOC = R / "doc_anchor_L.png"     # documentarian, gaze frame-left
AMB = "Only her voice and faint room ambience, no other voices, no murmurs, no background chatter."

def surv(line, tone):
    return (f"The woman sits in the armchair, speaking to an interviewer just off to the RIGHT side of "
            f"the frame, looking toward them, not at the camera. {tone} She says: \"{line}\" {AMB}")
def doc(line, tone):
    return (f"The woman sits in the armchair, speaking to someone just off to the LEFT side of the "
            f"frame, looking toward them, not at the camera. {tone} She says: \"{line}\" {AMB}")

# (name, anchor, duration, prompt)
TALK = [
 ("doc_0", DOC, "10", doc("You were a nurse for almost twenty years. When they told you it was a brain meningioma, did you already know what that meant?", "Warm, gentle, curious.")),
 ("surv_1", SURV, "8", surv("I knew exactly what it meant. I'd seen the scans. I just never thought I'd be the one on the table.", "Quiet, weathered, a little disbelief.")),
 ("doc_2", DOC, "6", doc("You gave that injection every day. Did you ever connect it to your own diagnosis?", "Gently probing.")),
 ("surv_3", SURV, "14", surv("Not at first. Then a lawyer showed me the studies. Women on the Depo shot for over a year were up to five times more likely to get one. I gave that shot for years.", "Steady, stunned, plain.")),
 ("surv_4", SURV, "8", surv("To hundreds of women. And nobody ever told us it could do this. Not the reps, not the label. Nobody.", "Wounded, firm.")),
 ("doc_5", DOC, "6", doc("And it turns out you're far from the only one.", "Warm, reassuring.")),
 ("surv_6", SURV, "8", surv("Not even close. Thousands of women now. Same diagnosis, same shot. There's a federal lawsuit.", "Steady, resolved.")),
 ("doc_7", DOC, "6", doc("So for a woman watching this, where does she even start?", "Practical, gentle.")),
 ("surv_8", SURV, "8", surv("You answer a few private questions online. Your diagnosis, how long you were on Depo. Takes about a minute.", "Helpful, calm.")),
 ("surv_9", SURV, "9", surv("A lawyer reviews it for free. No court, it's confidential. And even if it was years ago, you may still qualify.", "Warm, reassuring, low-key.")),
 ("doc_cta", DOC, "11",
   "The woman sits in the armchair and looks DIRECTLY INTO the camera lens, speaking straight to the "
   "viewer, warm and sincere with a small caring nod. She says: \"If you or someone you love has a "
   "brain meningioma and was ever on Depo, you may qualify for significant compensation. Tap below "
   "and take the two-minute check.\" " + AMB),
]
# silent listeners (~10s), two of each for variety
LISTEN = [
 ("surv_listen_1", SURV, "10", "The woman sits calmly in the armchair, listening quietly to an interviewer just off to the RIGHT side of the frame, gentle nods, natural blinks, a warm attentive expression, lips closed, calm and still. Faint room ambience, no talking, no voices."),
 ("surv_listen_2", SURV, "10", "The woman sits in the armchair, listening thoughtfully to someone off to the RIGHT, a slow nod and a soft breath, natural blinks, lips closed, still. Faint room ambience, no talking, no voices."),
 ("doc_listen_1", DOC, "10", "The woman sits calmly in the armchair, listening intently to the person just off to the LEFT side of the frame, slow empathetic nods, soft micro-expressions, natural blinks, lips closed, calm and still. Faint room ambience, no talking, no voices."),
 ("doc_listen_2", DOC, "10", "The woman sits in the armchair, listening to someone off to the LEFT, a gentle understanding nod, natural blinks, lips closed, still and attentive. Faint room ambience, no talking, no voices."),
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
    else: print("FAIL", name, str(res.get("raw"))[:180])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default="")
    a = ap.parse_args()
    items = TALK + LISTEN
    if a.only: items = [x for x in items if x[0] in set(a.only.split(","))]
    for it in items: gen(*it)
    print("ALL DONE")

if __name__ == "__main__":
    main()
