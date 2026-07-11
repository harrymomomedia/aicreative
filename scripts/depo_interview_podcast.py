#!/usr/bin/env python3
"""Podcast/documentary 3/4 angle: camera slightly off-axis, body angled a touch, eyeline
lands JUST AHEAD (at the conversation partner beside the camera) — not dead-lens, not profile.
Chest-up. Same room, opposite-wall backdrops. Survivor angled gently screen-right, doc gently
screen-left (they read as facing each other). Minimal i2i prompts.

Run: .venv/bin/python scripts/depo_interview_podcast.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
SURV = REF / "survivor_A_twistout.png"
DOC = REF / "doc_B_woman_gray.png"
SURV_ROOM = REF / "bg_room_iph.png"
DOC_ROOM = REF / "rev_room_v1.png"

IPHONE = (
    "candid vertical iPhone video frame, deep focus with the background in focus, flat even "
    "indoor exposure, realistic smartphone color, slight sensor grain, no bokeh, no cinematic "
    "grade. 9:16 vertical."
)

def pod(side):
    return (
        "Tight CHEST-UP close-up, podcast/documentary style. The camera is slightly off to one "
        "side (a gentle three-quarter angle), and she sits with her body turned just a little. "
        f"Her eyeline lands JUST AHEAD of her, angled slightly to the {side}, looking at the "
        "person she is talking with who sits just beside the camera — a natural relaxed "
        "conversational gaze, MOSTLY forward but a little off to the side. NOT staring dead into "
        "the lens, and NOT a full side profile. Keep the second image's exact camera look. "
    )

SURV_PROMPT = "Put the woman from the first image into the room from the second image, sitting in the cream armchair. " + pod("RIGHT") + IPHONE
DOC_PROMPT = "Put the woman from the first image into the room from the second image, sitting in the cream armchair. " + pod("LEFT") + IPHONE


def compose(name, face, room, prompt):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}"); return
    face_url = upload_file(str(face)); room_url = upload_file(str(room))
    print(f"[comp] {name} …")
    res = generate_gpt_image(prompt, image_urls=[face_url, room_url], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}"); return
    download(res["urls"][0], out); print(f"[done] {out}")


jobs = [
    ("surv_pod_v1", SURV, SURV_ROOM, SURV_PROMPT),
    ("surv_pod_v2", SURV, SURV_ROOM, SURV_PROMPT),
    ("doc_pod_v1", DOC, DOC_ROOM, DOC_PROMPT),
    ("doc_pod_v2", DOC, DOC_ROOM, DOC_PROMPT),
]
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(lambda j: compose(*j), jobs))
print("ALL DONE")
