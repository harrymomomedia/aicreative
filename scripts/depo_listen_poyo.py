#!/usr/bin/env python3
"""Silent mouth-closed listening clips on Poyo (Veo 3.1 Fast) — the free Lite tier can't stop
animating the mouth. 2 generic clips (survivor + doc), reused across the whole stacked edit.
"""
import concurrent.futures as cf, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import poyo_client as poyo
REF = Path("outputs/depo_interview/reference")
OUT = Path("outputs/depo_interview/clips_poyo"); OUT.mkdir(parents=True, exist_ok=True)
NT = "No on-screen text, no captions, no subtitles."
def listen(persona):
    side = "right" if persona=="surv" else "left"
    who = ("A weary middle-aged Black woman" if persona=="surv"
           else "A warm middle-aged woman documentary interviewer")
    return (f"{who} sitting in an armchair, silently LISTENING to someone off-camera on her "
        f"{side}.\nCRITICAL — MOUTH STAYS CLOSED: her lips stay gently closed and still the ENTIRE "
        "clip. She does NOT speak, does NOT open her mouth, does NOT mouth or form any words at any "
        "moment.\nShe only listens: a few slow small nods, natural blinks, a calm breath, tiny "
        f"weary shifts.\nGAZE: steady on the person to her {side}, never into the lens.\nShe makes "
        "NO vocal sound — completely silent listening, only faint room ambience.\n" + NT)
CLIPS = {"surv_listen_poyo": (REF/"surv_face_v1.png","surv"),
         "doc_listen_poyo": (REF/"doc_alone_v1_L.png","doc")}
def gen(name):
    anchor, persona = CLIPS[name]; out = OUT/f"{name}.mp4"
    if out.exists(): print(f"[skip] {out}"); return
    url = poyo.upload_file(str(anchor))
    print(f"[gen ] {name}")
    res = poyo.generate_veo(listen(persona), image_urls=[url,url], generation_type="frame",
                            aspect_ratio="9:16", resolution="720p")
    if res.get("status")!="success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}"); return
    poyo.download(res["urls"][0], out); print(f"[done] {out}")
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(gen, CLIPS))
print("ALL DONE")
