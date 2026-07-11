#!/usr/bin/env python3
"""Generic MOUTH-CLOSED listening clips (one per person, reused across all beats).
Hard lip-lock; mentions ambient sound so the free tier's audio filter doesn't reject it.
"""
import concurrent.futures as cf, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import googleflow_client as gf
REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/clips_useapi"); OUT.mkdir(parents=True, exist_ok=True)
NOTEXT = "No on-screen text, no captions, no subtitles."
def listen(persona):
    side = "right" if persona=="surv" else "left"
    who = ("A weary middle-aged Black woman" if persona=="surv"
           else "A warm middle-aged woman documentary interviewer")
    return (f"{who} sitting in an armchair, quietly LISTENING to someone speaking off-camera on "
        f"her {side}.\nHARD LIP LOCK: her lips stay gently CLOSED and still the entire clip. She "
        "does NOT talk, does NOT open her mouth, does NOT mouth or form any words at any point.\n"
        f"She only listens: slow thoughtful nods, soft natural blinks, tiny weary shifts, a calm "
        f"breath.\nGAZE: steady on the person to her {side}, never into the lens.\n"
        "The soundtrack is only soft natural room ambience (a faint room hum) — calm and quiet.\n"
        + NOTEXT)
CLIPS = {"surv_listen_pure": (REF/"surv_face_v1.png","surv"),
         "doc_listen_pure": (REF/"doc_alone_v1_L.png","doc")}
def gen(name):
    anchor, persona = CLIPS[name]; out = OUT/f"{name}.mp4"
    if out.exists(): print(f"[skip] {out}"); return
    print(f"[gen ] {name}")
    res = gf.generate_veo(listen(persona), image_path=str(anchor), duration=8, aspect_ratio="portrait")
    if res.get("status")!="success" or not res.get("urls"):
        print(f"[FAIL] {name}: {str(res.get('raw'))[:140]}"); return
    gf.download(res["urls"][0], out); print(f"[done] {out}")
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(gen, CLIPS))
print("ALL DONE")
