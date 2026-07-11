#!/usr/bin/env python3
"""Keep documentarian B's EXACT face; only swap her background into survivor A's room.
Uses nano-banana-2 (KIE) — a strict identity-preserving edit model (unlike gpt-image-2 i2i,
which re-imagines the face). img1 = doc (keep exactly), img2 = room reference.

Run: .venv/bin/python scripts/depo_interview_doc_nanobanana.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_nano_banana, upload_file, download

REF = Path("outputs/depo_interview/reference")
DOC_SRC = REF / "doc_B_woman_gray.png"        # KEEP this face exactly
ROOM_SRC = REF / "survivor_A_twistout.png"    # room to match

PROMPT = (
    "Keep the woman from the FIRST image EXACTLY as she is — identical face, identical short gray "
    "hair, identical thin wire glasses, identical light chambray button shirt, same age and "
    "expression. Do NOT redraw or beautify her face; preserve her likeness pixel-faithfully. "
    "ONLY change her surroundings: place her seated as the interviewer in the SAME warm home room "
    "shown in the SECOND image (its wooden cabinet, beige wall, framed family photos, warm soft "
    "light), at a reverse camera angle across from the subject. She looks slightly to camera-left "
    "toward an off-camera subject. Do NOT include the woman from the second image. Keep it a "
    "natural documentary photo, muted realistic warm color, 9:16 vertical."
)


def gen(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC_SRC))
    room_url = upload_file(str(ROOM_SRC))
    print(f"[gen ] {name} …")
    res = generate_nano_banana(PROMPT, image_urls=[doc_url, room_url])
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(gen, ["doc_nb_v1", "doc_nb_v2", "doc_nb_v3"]))
print("ALL DONE")
