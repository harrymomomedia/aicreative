#!/usr/bin/env python3
"""Keep ORIGINAL survivor_A untouched; place documentarian B into survivor A's OWN room
so the two-shot matches. gpt-image-2 composition: img1 = doc identity, img2 = room reference.

Run: .venv/bin/python scripts/depo_interview_doc_in_room.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
DOC_SRC = REF / "doc_B_woman_gray.png"        # identity to keep
ROOM_SRC = REF / "survivor_A_twistout.png"    # room to match (survivor's real home)

REAL = (
    "Natural real skin texture with visible pores and fine lines, no beauty retouching, no "
    "filter, no smile, casual real look (not styled, not professional set). Documentary camera, "
    "shallow depth of field, muted realistic warm color. Medium chest-up framing. 9:16 vertical."
)

PROMPT = (
    "Compose a new documentary-interview photo. Render ONLY the woman from the FIRST image — keep "
    "her EXACT face, short gray hair, thin wire glasses, light chambray button shirt, and age. "
    "Seat her in the SAME warm home room shown in the SECOND image (match its wooden furniture, "
    "beige walls, warm household clutter and soft warm light) at a reverse camera angle, as the "
    "interviewer sitting across from the subject. She looks slightly to camera-LEFT toward the "
    "off-camera subject with a warm, attentive listening expression (NOT into the lens). Do NOT "
    "include the woman from the second image anywhere in the frame. " + REAL
)


def gen(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC_SRC))
    room_url = upload_file(str(ROOM_SRC))
    print(f"[gen ] {name} …")
    res = generate_gpt_image(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=3) as ex:
    list(ex.map(gen, ["doc_inroom_v1", "doc_inroom_v2", "doc_inroom_v3"]))
print("ALL DONE")
