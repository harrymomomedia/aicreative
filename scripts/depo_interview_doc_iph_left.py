#!/usr/bin/env python3
"""Regen documentarian into the iPhone room (bg_room_iph) with an unambiguous SCREEN-LEFT
gaze so she faces the survivor (who looks screen-right). iPhone-video aesthetic. Exact face.

Run: .venv/bin/python scripts/depo_interview_doc_iph_left.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
DOC = REF / "doc_B_woman_gray.png"
ROOM = REF / "bg_room_iph.png"

PROMPT = (
    "Place the woman from the FIRST image seated in the cream armchair in the room from the SECOND "
    "image, holding a small notepad. FRAMING: tight WAIST-UP medium close-up, like a locked-off interview camera — her head and torso fill the frame, do NOT show her legs or knees, do NOT go wide. Keep her EXACT face, short gray hair, thin wire glasses and "
    "light chambray shirt — do NOT change her appearance. CRITICAL GAZE: she turns her head to HER "
    "OWN RIGHT so her eyes look toward the LEFT edge of the frame (the viewer's left / screen-left), "
    "at an off-camera person seated just past the left edge of the frame. She must NOT look toward "
    "the right side and must NOT look into the lens. Warm attentive listening expression. Make the "
    "whole image look like a candid VERTICAL iPhone VIDEO FRAME: shot on an iPhone, DEEP focus with "
    "the background also in focus, flat even natural indoor exposure, realistic smartphone color, "
    "slight sensor grain, NO shallow depth of field, NO bokeh, NO cinematic grade. 9:16 vertical."
)


def gen(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC))
    room_url = upload_file(str(ROOM))
    print(f"[gen ] {name} …")
    res = generate_gpt_image(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16", resolution="4K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(gen, ["doc_iphL_v3", "doc_iphL_v4"]))
print("ALL DONE")
