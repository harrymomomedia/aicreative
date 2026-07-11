#!/usr/bin/env python3
"""Animate the new Depo b-roll stills via Grok Imagine (subtle motion, silent), then UPLOAD each
clip into the AdMachin Depo Provera b-roll database (Tort project / Depo Provera subproject).
Skip-if-exists on the local clip; uploads any clip not yet recorded in uploaded.json.
Run: .venv/bin/python scripts/depo_broll_animate_upload.py [--no-upload]
"""
import sys, json, argparse, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie
from admachin_client import upload_creative

BROLL = Path("outputs/depo_interview/broll")
CLIPS = Path("outputs/depo_interview/broll_clips"); CLIPS.mkdir(parents=True, exist_ok=True)
STATE = CLIPS / "uploaded.json"
TORT = "e15c60bd-95c2-47b9-9730-c29fb5325461"
DEPO = "9cfb5b76-1dd3-4e07-b037-2dda178ac266"

# (still_name, grok motion prompt) — subtle, silent, no talking
ITEMS = [
 ("study_pages", "The hands slowly turn a page and slide the highlighter along a line of text, small quiet movement. Quiet room, no talking, no voices."),
 ("depo_vial", "The blue-gloved hands steadily finish drawing the liquid up into the syringe, a small controlled motion. Quiet clinic, no talking, no voices."),
 ("depo_injection", "The nurse steadily gives the injection with a small press of the plunger while the patient sits still. Minimal quiet motion, no talking, no voices."),
 ("women_group", "The women sit and listen, small natural nods and shifts of posture, one glances toward another. Quiet room, no talking, no voices."),
 ("legal_docs", "A hand sets another folder onto the stack and the top page settles, then stillness. Quiet office, no talking, no voices."),
 ("phone_form", "The thumb taps the button on the phone screen, a small natural hand movement. Quiet, no talking, no voices."),
 ("lawyer_review", "The attorney turns a page in the open folder and reads it, small calm natural movements. Quiet office, no talking, no voices."),
]

def animate(name, prompt):
    out = CLIPS / f"{name}.mp4"
    if out.exists(): print("skip anim", name); return out
    still = BROLL / f"broll_{name}.png"
    url = kie.upload_file(str(still))
    payload = {"model":"grok-imagine/image-to-video","input":{"image_urls":[url],"prompt":prompt,
               "mode":"normal","duration":"8","resolution":"720p","aspect_ratio":"9:16"}}
    r = requests.post(kie.JOBS_CREATE, headers=kie.HEADERS, json=payload)
    tid = (r.json().get("data") or {}).get("taskId")
    if not tid: print("FAIL create", name, r.json()); return None
    res = kie._poll_jobs(tid, f"Grok {name}")
    if res.get("status") == "success" and res.get("urls"):
        kie.download(res["urls"][0], out); print("anim done", name); return out
    print("FAIL anim", name, str(res.get("raw"))[:180]); return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--no-upload", action="store_true")
    a = ap.parse_args()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for name, prompt in ITEMS:
        clip = animate(name, prompt)
        if not clip: continue
        if a.no_upload or name in state: continue
        try:
            c = upload_creative(str(clip), type="video", project_id=TORT, subproject_id=DEPO)
            cid = c.get("id") if isinstance(c, dict) else None
            state[name] = cid; STATE.write_text(json.dumps(state, indent=1))
            print(f"UPLOADED {name} -> creative {cid}")
        except Exception as e:
            print(f"UPLOAD FAIL {name}: {type(e).__name__} {e}")
    print("ALL DONE")
    print("AdMachin creative ids:", json.dumps(state, indent=1))

if __name__ == "__main__":
    main()
