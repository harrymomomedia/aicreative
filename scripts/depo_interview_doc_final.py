#!/usr/bin/env python3
"""Final documentarian anchor: doc_B's EXACT face composited into the survivor's approved
iPhone-look frame (surv_iph) as the room reference — guarantees same room + same look.
Primary engine = nano-banana-2 (identity-preserving composition; gpt-image-2 i2i drifts faces).
Also renders one gpt-image-2 2K candidate for comparison. Waist-up, screen-LEFT gaze.

Run: .venv/bin/python scripts/depo_interview_doc_final.py
"""
import concurrent.futures as cf
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_nano_banana, generate_gpt_image, upload_file, download

REF = Path("outputs/depo_interview/reference")
DOC = REF / "doc_B_woman_gray.png"     # identity to keep, exactly
ROOM = REF / "surv_iph.png"            # approved iPhone frame = room + look reference

PROMPT = (
    "Create the reverse interview angle. Take the woman from the FIRST image and keep her "
    "likeness EXACTLY — identical face, identical short gray hair, thin wire glasses, light "
    "chambray button shirt. Seat her in the SAME living room shown in the SECOND image, in the "
    "same cream fabric armchair, as the interviewer holding a small notepad. COMPLETELY REMOVE "
    "the woman in the gray t-shirt from the SECOND image — only the interviewer appears. "
    "FRAMING: tight WAIST-UP medium close-up like a locked-off interview camera; no legs or "
    "knees visible. GAZE: her head is turned so she looks toward the LEFT edge of the frame "
    "(viewer's left) at the off-camera subject; never toward the right, never into the lens. "
    "Warm attentive listening expression. Match the SECOND image's exact look: candid vertical "
    "iPhone video frame, deep focus, flat even indoor exposure, smartphone color, slight sensor "
    "grain, no bokeh, no cinematic grade. 9:16 vertical."
)


def gen_nano(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC))
    room_url = upload_file(str(ROOM))
    print(f"[nano] {name} …")
    try:
        res = generate_nano_banana(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16")
    except RuntimeError as e:
        print(f"[warn] aspect_ratio rejected ({e}); retrying without")
        res = generate_nano_banana(PROMPT, image_urls=[doc_url, room_url])
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


def gen_gpt(name):
    out = REF / f"{name}.png"
    if out.exists():
        print(f"[skip] {out}")
        return
    doc_url = upload_file(str(DOC))
    room_url = upload_file(str(ROOM))
    print(f"[gpt ] {name} …")
    res = generate_gpt_image(PROMPT, image_urls=[doc_url, room_url], aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {name}: {res.get('raw')}")
        return
    download(res["urls"][0], out)
    print(f"[done] {out}")


with cf.ThreadPoolExecutor(max_workers=3) as ex:
    futs = [ex.submit(gen_nano, "docF_nano_v1"), ex.submit(gen_nano, "docF_nano_v2"),
            ex.submit(gen_gpt, "docF_gpt_v1")]
    for f in futs:
        f.result()
print("ALL DONE")
