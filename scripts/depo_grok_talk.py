#!/usr/bin/env python3
"""First 16s TALKING clips on Grok Imagine (KIE) — test whether Grok avoids Veo's phantom
'mm-hmm/oh ya' reaction murmurs. Speech is specified in the prompt ("she says: ...").
Gaze: speaker looks at the OTHER person off-camera (not the lens), except CTA (into lens).
"""
import sys, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kie_client as kie
REF=Path("outputs/depo_interview/reference"); OUT=Path("outputs/depo_interview/clips_grok"); OUT.mkdir(parents=True,exist_ok=True)

CLIPS = [
 ("gtalk_doc_1", REF/"doc_alone_v1_L.png", "8",
  "The woman sits in the armchair, speaking warmly and gently to someone off to her left, looking "
  "toward them, not at the camera. She says clearly: \"When they told you it was a brain "
  "meningioma, did anyone ever explain why you got it?\" Calm, caring, unhurried. Only her voice "
  "and faint room ambience — no other voices, no background chatter."),
 ("gtalk_surv_1", REF/"surv_face_v1.png", "8",
  "The woman sits in the armchair, speaking quietly and wearily to an interviewer off to her "
  "right, looking toward them, not at the camera. She says: \"No. Bad luck, they kept saying. "
  "Over and over. And for a long time, I believed that.\" Resigned, heavy, natural. Only her "
  "voice and faint room ambience — no other voices, no murmurs, no background chatter."),
]
def gen(name, anchor, dur, prompt):
    out=OUT/f"{name}.mp4"
    if out.exists(): print("skip",name); return
    url=kie.upload_file(str(anchor))
    payload={"model":"grok-imagine/image-to-video","input":{"image_urls":[url],"prompt":prompt,
             "mode":"normal","duration":dur,"resolution":"720p","aspect_ratio":"9:16"}}
    r=requests.post(kie.JOBS_CREATE, headers=kie.HEADERS, json=payload)
    tid=(r.json().get("data") or {}).get("taskId")
    if not tid: print("FAIL create",name,r.json()); return
    res=kie._poll_jobs(tid,"Grok")
    if res.get("status")=="success" and res.get("urls"):
        kie.download(res["urls"][0],out); print("done",name)
    else: print("FAIL",name,str(res.get("raw"))[:160])
for c in CLIPS: gen(*c)
print("ALL DONE")
