#!/usr/bin/env python3
"""User-insight version: i2i with a MINIMAL prompt — zero description of the person, so the
image reference fully drives the likeness (text descriptions compete with the ref and cause
drift). img1 = doc face, img2 = survivor's approved iPhone frame (room + look ref).

Run: .venv/bin/python scripts/depo_interview_doc_minimal.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, generate_nano_banana, upload_file, download

REF = Path("outputs/depo_interview/reference")
DOC = REF / "doc_B_woman_gray.png"
ROOM = REF / "surv_iph.png"

# Minimal — no appearance description, only the action/framing/gaze.
PROMPT = (
    "Put the woman from the first image into the room from the second image, replacing the "
    "person there. She sits in the cream armchair as the interviewer, holding a small notepad, "
    "waist-up shot, looking toward the left edge of the frame at someone off-camera. Keep the "
    "second image's exact camera look. 9:16 vertical."
)


def gen(name, engine):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC))
    room_url = upload_file(str(ROOM))
    print(f"[{engine}] {name} …")
    if engine == "nano":
        res = generate_nano_banana(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16")
    else:
        res = generate_gpt_image(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=3) as ex:
    futs = [ex.submit(gen, "docM_gpt_v1", "gpt"), ex.submit(gen, "docM_gpt_v2", "gpt"),
            ex.submit(gen, "docM_nano_v1", "nano")]
    for f in futs:
        f.result()
print("ALL DONE")
