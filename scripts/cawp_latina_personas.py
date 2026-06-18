"""CA women's-prison campaign — LATINA persona candidates with iPhone-VIDEO-frame look
(user spec 2026-06-10: "image that will look like it's shot on iphone video, not photo").
For ads F1 (news-reaction PIP) and F5 (three-questions announcer). 6 candidates.
Skip-if-exists; KIE gpt-image-2 t2i @ 2K 9:16."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from kie_client import generate_gpt_image

OUT_DIR = os.path.join("outputs", "cawp_personas_latina", "reference")
os.makedirs(OUT_DIR, exist_ok=True)

TAIL = (
    " Frame grabbed from a vertical 9:16 iPhone front-camera selfie VIDEO, paused mid-moment: she "
    "looks directly into the lens, mouth relaxed and closed, about to speak. Handheld feel with "
    "slightly imperfect framing, a touch of motion softness in the background, subtle video sensor "
    "noise and compression texture, natural unflattering ambient light. Photoreal ordinary "
    "everyday-looking Latina woman, plain average features, natural skin with visible pores, "
    "blemishes, uneven tone, fine lines, faint under-eye darkness, imperfect teeth, no makeup, no "
    "retouching, no filter, no beauty mode. Looks like a real person's phone video, not a posed "
    "photo, not a portrait session. No on-screen text, no captions, no watermark."
)

CANDIDATES = {
    "l1_car": (
        "A 49-year-old Latina woman in the driver's seat of a parked car, daylight through the "
        "windshield, dark hair in a low ponytail, grey zip-up hoodie, seatbelt off, holding the "
        "phone slightly below eye level."
    ),
    "l2_kitchen": (
        "A 54-year-old Latina woman leaning on her kitchen counter, morning window light, dark "
        "hair with grey strands clipped back, floral blouse under an open cardigan, coffee mug "
        "out of focus nearby."
    ),
    "l3_couch": (
        "A 58-year-old Latina woman sitting on a couch in the evening, warm lamp light, "
        "grey-streaked dark hair loose at her shoulders, plain navy t-shirt, framed family photos "
        "blurred on the wall behind her."
    ),
    "l4_porch": (
        "A 46-year-old Latina woman sitting on concrete porch steps outside a stucco apartment "
        "building, open afternoon shade, faded denim jacket over a black tee, small gold hoop "
        "earrings."
    ),
    "l5_bedroom": (
        "A 61-year-old Latina woman sitting on the edge of a made bed, soft window light, "
        "grey-heavy dark hair pulled back loosely, reading glasses pushed up on her head, beige "
        "cardigan over a white tee."
    ),
    "l6_wall": (
        "A 50-year-old Latina woman with olive skin, dark hair with a grey streak pulled back, "
        "plain dark green crewneck, facing the camera square-on against a plain warm hallway wall "
        "with even soft light, phone held at chest height angled slightly up."
    ),
}


def gen_one(slug, desc):
    out_path = os.path.join(OUT_DIR, f"{slug}.png")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"[skip] {slug} exists")
        return slug, out_path
    res = generate_gpt_image(desc + TAIL, aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {slug}: {res.get('raw')}")
        return slug, None
    img = requests.get(res["urls"][0], timeout=120)
    img.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(img.content)
    print(f"[ok] {slug} -> {out_path}")
    return slug, out_path


def main():
    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen_one, s, d): s for s, d in CANDIDATES.items()}
        for fut in as_completed(futs):
            slug, path = fut.result()
            results[slug] = path
    ok = sum(1 for p in results.values() if p)
    print(f"\ndone: {ok}/{len(CANDIDATES)} candidates in {OUT_DIR}")


if __name__ == "__main__":
    main()
