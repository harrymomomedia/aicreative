#!/usr/bin/env python3
"""Doc alone (no over-the-shoulder foreground), looking RIGHT into text-free reverse room,
then flip -> clean screen-LEFT. Chest-up 3/4, iPhone look.
"""
import concurrent.futures as cf, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download
REF = Path("outputs/depo_interview/reference")
DOC = REF / "doc_B_woman_gray.png"; ROOM = REF / "rev_room_notext.png"
IPHONE = ("candid vertical iPhone video frame, deep focus, flat even indoor exposure, realistic "
    "smartphone color, slight sensor grain, no bokeh, no cinematic grade. 9:16 vertical.")
PROMPT = ("Put the woman from the first image into the room from the second image, sitting in the "
    "cream armchair. She is ALONE in the frame — NO other person, and NO out-of-focus foreground "
    "shoulder, head or figure anywhere; only her and the room behind her. Tight CHEST-UP close-up, "
    "podcast/documentary 3/4 angle: she looks toward the RIGHT side of the frame at someone "
    "off-camera, relaxed conversational gaze angled right, not dead into the lens, not full "
    "profile. Keep the second image's exact camera look. " + IPHONE)
def gen(name):
    out = REF / f"{name}.png"; flip = REF / f"{name}_L.png"
    if flip.exists(): print(f"[skip] {flip}"); return
    fu, ru = upload_file(str(DOC)), upload_file(str(ROOM))
    res = generate_gpt_image(PROMPT, image_urls=[fu, ru], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}"); return
    download(res["urls"][0], out)
    Image.open(out).transpose(Image.FLIP_LEFT_RIGHT).save(flip)
    print(f"[done] {flip}")
with cf.ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(gen, ["doc_alone_v1", "doc_alone_v2"]))
print("ALL DONE")
