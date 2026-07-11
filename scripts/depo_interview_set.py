#!/usr/bin/env python3
"""Build ONE interview room, then composite each REAL face into it (gpt-image-2 i2i,
multi-image) — user-proven method that keeps the exact face while locking a shared
room/chair. Stage 1 = text-to-image empty room. Stage 2 = i2i [face, room] per person.

Run: .venv/bin/python scripts/depo_interview_set.py --bg bg_room_v1
"""
import argparse
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
SURV = REF / "survivor_A_twistout.png"
DOC = REF / "doc_B_woman_gray.png"

ROOM_PROMPT = (
    "Photoreal documentary photograph of an EMPTY warm home living room set up for a sit-down "
    "interview: one cream-beige upholstered armchair with a woven texture in the center, angled "
    "slightly toward camera; behind it a warm beige wall with a cluster of framed family "
    "photographs, a warm wooden cabinet holding books and a small lamp, and a leafy houseplant; "
    "soft warm daylight from a window at camera-left; cozy muted warm earth tones; NO people in "
    "the room. Shallow depth of field, muted realistic warm color. 9:16 vertical."
)

REAL = (
    "Keep it a natural candid documentary photo, natural skin texture, no beauty retouching, no "
    "filter, no smile, muted realistic warm color matching the room. Medium chest-up framing. "
    "9:16 vertical."
)


def surv_prompt():
    return (
        "Place the woman from the FIRST image seated in the cream armchair in the room shown in "
        "the SECOND image. Keep her EXACT face, short gray natural twist-out hair, gray t-shirt "
        "and small clip-on lav mic — do NOT change her appearance or clothing. She sits back in "
        "the chair, turned slightly so she looks to camera-RIGHT at an off-camera interviewer "
        "(NOT into the lens). Match the room's warm window light. " + REAL
    )


def doc_prompt():
    return (
        "Place the woman from the FIRST image seated in the cream armchair in the room shown in "
        "the SECOND image. Keep her EXACT face, short gray hair, thin wire glasses and light "
        "chambray button shirt — do NOT change her appearance or clothing. She sits back in the "
        "chair, turned slightly so she looks to camera-LEFT toward an off-camera subject with a "
        "warm attentive listening expression (NOT into the lens). Match the room's warm window "
        "light. " + REAL
    )


def gen_room(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return out
    print(f"[room] {name} …")
    res = generate_gpt_image(ROOM_PROMPT, aspect_ratio="9:16", resolution="4K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return None
    download(res["urls"][0], out)
    print(f"[done] {out}")
    return out


def composite(name, face_path, prompt, room_path):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    face_url = upload_file(str(face_path))
    room_url = upload_file(str(room_path))
    print(f"[comp] {name} …")
    res = generate_gpt_image(prompt, image_urls=[face_url, room_url], aspect_ratio="9:16", resolution="4K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default="bg_room_v1", help="which background to composite into")
    args = ap.parse_args()

    # Stage 1: two empty-room options
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(gen_room, ["bg_room_v1", "bg_room_v2"]))

    room = REF / f"{args.bg}.png"
    if not room.exists():
        print(f"[abort] background {room} missing")
        return

    # Stage 2: composite both faces into the chosen room
    jobs = [
        (f"surv_set_{args.bg}", SURV, surv_prompt(), room),
        (f"doc_set_{args.bg}", DOC, doc_prompt(), room),
    ]
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(lambda j: composite(*j), jobs))
    print("ALL DONE")


if __name__ == "__main__":
    main()
