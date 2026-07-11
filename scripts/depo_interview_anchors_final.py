#!/usr/bin/env python3
"""FINAL anchors — real i2i (input_urls fix) + minimal prompts (no person description,
so the reference image fully drives likeness). Both people composited into the SAME
empty iPhone-look room (bg_room_iph) => identical room/chair/light, exact faces.

Survivor: waist-up, looks screen-RIGHT. Documentarian: waist-up, notepad, looks screen-LEFT.
Run: .venv/bin/python scripts/depo_interview_anchors_final.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
ROOM = REF / "bg_room_iph.png"

SURV_PROMPT = (
    "Put the woman from the first image into the empty room from the second image. She sits in "
    "the cream armchair giving an interview, waist-up shot, looking toward the right edge of the "
    "frame at someone off-camera, calm serious expression. Keep the second image's exact camera "
    "look. 9:16 vertical."
)
DOC_PROMPT = (
    "Put the woman from the first image into the empty room from the second image. She sits in "
    "the cream armchair as the interviewer holding a small notepad, waist-up shot, looking toward "
    "the left edge of the frame at someone off-camera, warm attentive listening expression. Keep "
    "the second image's exact camera look. 9:16 vertical."
)

JOBS = [
    ("survF_v1", REF / "survivor_A_twistout.png", SURV_PROMPT),
    ("survF_v2", REF / "survivor_A_twistout.png", SURV_PROMPT),
    ("docFF_v1", REF / "doc_B_woman_gray.png", DOC_PROMPT),
    ("docFF_v2", REF / "doc_B_woman_gray.png", DOC_PROMPT),
]


def gen(name, face, prompt):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    face_url = upload_file(str(face))
    room_url = upload_file(str(ROOM))
    print(f"[gen ] {name} …")
    res = generate_gpt_image(prompt, image_urls=[face_url, room_url], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=4) as ex:
    list(ex.map(lambda j: gen(*j), JOBS))
print("ALL DONE")
