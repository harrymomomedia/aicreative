#!/usr/bin/env python3
"""Doc looks screen-LEFT: composite the FLIPPED doc source (already gazing left) into the
reverse-angle room. i2i carries the source gaze, so flipping the source is what actually
flips the look. Chest-up 3/4 podcast angle, iPhone look.
"""
import concurrent.futures as cf, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download
REF = Path("outputs/depo_interview/reference")
DOC = REF / "doc_B_flip.png"; ROOM = REF / "rev_room_v1.png"
IPHONE = ("candid vertical iPhone video frame, deep focus, flat even indoor exposure, realistic "
    "smartphone color, slight sensor grain, no bokeh, no cinematic grade. 9:16 vertical.")
PROMPT = ("Put the woman from the first image into the room from the second image, sitting in the "
    "cream armchair. Tight CHEST-UP close-up, podcast/documentary 3/4 angle: she looks toward the "
    "LEFT side of the frame at the person she is talking with off the left edge — relaxed "
    "conversational gaze, mostly forward but angled to the left, not dead into the lens, not full "
    "profile. Keep the second image's exact camera look. " + IPHONE)
def gen(name):
    out = REF / f"{name}.png"
    if out.exists(): print(f"[skip] {out}"); return
    fu, ru = upload_file(str(DOC)), upload_file(str(ROOM))
    print(f"[comp] {name}")
    res = generate_gpt_image(PROMPT, image_urls=[fu, ru], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}"); return
    download(res["urls"][0], out); print(f"[done] {out}")
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(gen, ["doc_left_v1", "doc_left_v2"]))
print("ALL DONE")
