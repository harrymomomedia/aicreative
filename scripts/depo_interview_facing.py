#!/usr/bin/env python3
"""Podcast 3/4 angle but with CLEARLY OPPOSITE gazes so the two read as facing each other:
survivor looks toward screen-RIGHT, documentarian looks toward screen-LEFT. Chest-up,
same room / opposite-wall backdrops, exact faces, iPhone look. Minimal i2i prompts.
"""
import concurrent.futures as cf, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
SURV = REF / "survivor_A_twistout.png"; DOC = REF / "doc_B_woman_gray.png"
SURV_ROOM = REF / "bg_room_iph.png"; DOC_ROOM = REF / "rev_room_v1.png"
IPHONE = ("candid vertical iPhone video frame, deep focus with the background in focus, flat "
    "even indoor exposure, realistic smartphone color, slight sensor grain, no bokeh, no "
    "cinematic grade. 9:16 vertical.")

def prompt(side):
    opp = "LEFT" if side == "RIGHT" else "RIGHT"
    return ("Put the woman from the first image into the room from the second image, sitting in "
        "the cream armchair. Tight CHEST-UP close-up, podcast/documentary framing: she sits at a "
        f"clear three-quarter angle, her body and face turned so she looks toward the {side} side "
        f"of the frame at the person she is talking with (seated just off the {side} edge). "
        f"Relaxed conversational gaze angled to the {side} — clearly NOT toward the {opp} side and "
        "NOT dead into the lens, but not a full side profile either (most of her face still "
        "visible). Keep the second image's exact camera look. " + IPHONE)

def compose(name, face, room, side):
    out = REF / f"{name}.png"
    if out.exists(): print(f"[skip] {out}"); return
    fu, ru = upload_file(str(face)), upload_file(str(room))
    print(f"[comp] {name} …")
    res = generate_gpt_image(prompt(side), image_urls=[fu, ru], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}"); return
    download(res["urls"][0], out); print(f"[done] {out}")

jobs = [("surv_face_v1", SURV, SURV_ROOM, "RIGHT"), ("surv_face_v2", SURV, SURV_ROOM, "RIGHT"),
        ("doc_face_v1", DOC, DOC_ROOM, "LEFT"), ("doc_face_v2", DOC, DOC_ROOM, "LEFT")]
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(lambda j: compose(*j), jobs))
print("ALL DONE")
