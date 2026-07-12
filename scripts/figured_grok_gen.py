#!/usr/bin/env python3
"""'Figured It Out' stacked interview — Grok clips. Subject = everyday Latina woman ~55 (gaze
frame-right), Interviewer = the documentarian reused from The Insider (gaze frame-left, listeners
reused). CTA into lens. Durations matched to word count. Em-dashes stripped. Skip-if-exists.
"""
import sys, argparse, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie

R = Path("outputs/depo_figured/reference")
OUT = Path("outputs/depo_figured/clips_grok"); OUT.mkdir(parents=True, exist_ok=True)
SURV = R / "surv_anchor_R.png"
DOC = R / "doc_anchor_L.png"
AMB = "Only her voice and faint room ambience, no other voices, no murmurs, no background chatter."

def surv(line, tone):
    return (f"The woman sits in the armchair, speaking to an interviewer just off to the RIGHT side of "
            f"the frame, looking toward them, not at the camera. {tone} She says: \"{line}\" {AMB}")
def doc(line, tone):
    return (f"The woman sits in the armchair, speaking to someone just off to the LEFT side of the "
            f"frame, looking toward them, not at the camera. {tone} She says: \"{line}\" {AMB}")

TALK = [
 ("doc_0", DOC, "6", doc("When you were diagnosed with a brain meningioma, did anyone ever tell you why?", "Warm, gentle, curious.")),
 ("surv_1", SURV, "8", surv("No. Not one doctor. They said sometimes these things just happen. I believed that for two years.", "Quiet, resigned, weathered.")),
 ("doc_2", DOC, "6", doc("So how did you find out it might not be random?", "Gently probing.")),
 ("surv_3", SURV, "14", surv("I was scrolling one night and saw a lawsuit. Women on the Depo shot for over a year were up to five times more likely to get a meninjioma. My stomach dropped.", "Quiet, then a jolt of realization.")),  # respell meningioma->meninjioma (TTS slurred it)
 ("surv_4", SURV, "6", surv("Because that was me. Same shot, for years. And nobody had ever said a word.", "Wounded, plain.")),
 ("doc_5", DOC, "6", doc("Most women are finding out the exact same way, on their own.", "Warm, knowing.")),
 ("surv_6", SURV, "10", surv("Nobody calls you. I pieced it together myself. Thousands of women are doing the same thing right now. There's a federal lawsuit.", "Steady, resolved.")),
 ("doc_7", DOC, "6", doc("For someone who just realized this watching you, what's the first step?", "Practical, gentle.")),
 ("surv_8", SURV, "8", surv("You answer a few private questions online. Your diagnosis, how long you were on Depo. About a minute.", "Helpful, calm.")),
 ("surv_9", SURV, "9", surv("A lawyer reviews it for free. No court, it's confidential. And even if your diagnosis was years ago, you may still qualify.", "Warm, reassuring, low-key.")),
 ("doc_cta", DOC, "11",
   "The woman sits in the armchair and looks DIRECTLY INTO the camera lens, speaking straight to the "
   "viewer, warm and sincere with a small caring nod. She says: \"If you or someone you love has a "
   "brain meningioma and was ever on Deppo, you may qualify for significant compensation. Tap below "  # Depo->Deppo (TTS said 'Depot')
   "and take the two-minute check.\" " + AMB),
]
# subject listeners only (doc listeners reused from The Insider)
LISTEN = [
 ("surv_listen_1", SURV, "10", "The woman sits calmly in the armchair, listening quietly to an interviewer just off to the RIGHT side of the frame, gentle nods, natural blinks, a warm attentive expression, lips closed, calm and still. Faint room ambience, no talking, no voices."),
 ("surv_listen_2", SURV, "10", "The woman sits in the armchair, listening thoughtfully to someone off to the RIGHT, a slow nod and a soft breath, natural blinks, lips closed, still. Faint room ambience, no talking, no voices."),
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
