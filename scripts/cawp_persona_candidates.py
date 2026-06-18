"""CA women's-prison campaign (cawp) — persona reference candidates for ads F1 (news-reaction PIP)
and F5 (three-questions announcer). 6 candidates, user picks one per ad.
Skip-if-exists; KIE gpt-image-2 t2i @ 2K 9:16."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from kie_client import generate_gpt_image

OUT_DIR = os.path.join("outputs", "cawp_personas", "reference")
os.makedirs(OUT_DIR, exist_ok=True)

TAIL = (
    " Photoreal candid documentary photo, not a glamour shoot, not a fashion shoot, not a celebrity "
    "portrait. An ordinary everyday-looking woman with plain average features. Natural skin with "
    "visible pores, blemishes, uneven tone, faint under-eye darkness, fine lines, slight asymmetry, "
    "imperfect teeth, no makeup, no beauty mode, no retouching, no filter. Vertical 9:16 framing like "
    "a phone front camera, chest-up, looking directly into the lens, eyes open, calm neutral "
    "expression with a hint of resolve. No on-screen text, no captions, no watermark."
)

CANDIDATES = {
    "a_kitchen": (
        "A 52-year-old Black woman, salt-and-pepper box braids tied back, sitting at a worn kitchen "
        "table, soft morning window light, plain mustard cardigan over a grey tee, modest lived-in "
        "kitchen slightly out of focus behind her."
    ),
    "b_stucco": (
        "A 48-year-old Latina woman, dark hair with grey strands in a low bun, small gold hoop "
        "earrings, faded denim jacket over a black tee, standing against a beige stucco apartment "
        "wall in open afternoon shade."
    ),
    "c_livingroom": (
        "A 55-year-old white woman, weathered face, dishwater-blonde greying hair worn down, plaid "
        "flannel shirt, sitting on a couch in a modest living room, framed family photos slightly "
        "out of focus behind her, warm lamp light."
    ),
    "d_porch": (
        "A 63-year-old Black woman, short natural grey hair, thin-framed glasses, plain lavender "
        "blouse, sitting in a chair on a small apartment porch, soft overcast daylight, front door "
        "slightly out of focus behind her."
    ),
    "e_bedroom": (
        "A 58-year-old Latina woman, grey-streaked dark hair loose at her shoulders, plain navy "
        "t-shirt, sitting on the edge of a made bed, warm bedside lamp light, plain bedroom wall "
        "behind her."
    ),
    "f_wall": (
        "A 47-year-old Black woman, shoulder-length locs tied back, plain dark green crewneck, "
        "seated square to the camera against a plain warm-grey interior wall, even soft window "
        "light, facing the lens straight on."
    ),
}


def gen_one(slug, desc):
    out_path = os.path.join(OUT_DIR, f"character_{slug}.png")
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
