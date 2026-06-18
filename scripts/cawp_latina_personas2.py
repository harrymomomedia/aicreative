"""CA women's-prison campaign — Latina persona pool BATCH 2 (l7-l21), same iPhone-VIDEO-frame
spec as the approved l1/l2/l4 batch. 15 candidates for user rotation picks.
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
    "l7_laundromat": "A 47-year-old Afro-Latina woman with a round full face, deep brown skin, broad nose, full lips, tight curls escaping a messy bun, a dark mole on her left cheek, sitting in a laundromat, washers blurred behind her, flat fluorescent light, oversized grey tee.",
    "l8_backyard": "A 52-year-old Latina woman with a long narrow face, light olive skin, an aquiline nose, thin lips, deep nasolabial folds, wavy grey-streaked dark hair, in a plastic chair in a small backyard, chain-link fence and a lemon tree out of focus, late-morning sun, floral house dress and cardigan.",
    "l9_balcony": "A 48-year-old Latina woman with strong indigenous features, high wide cheekbones, hooded eyes, medium-brown skin, straight black hair, a faint scar through one eyebrow, on a narrow apartment balcony at dusk, city haze behind, denim shirt.",
    "l10_truck": "A 58-year-old Latina woman with an oval weathered face, fair olive sun-damaged and freckled skin, light-brown eyes, strong dark brows, silver-grey waves loose, in the passenger seat of an older pickup truck, parked, window light, quilted flannel jacket.",
    "l11_diningtable": "A 49-year-old Latina woman with a heart-shaped face, medium olive skin, downturned tired eyes, full lips, fine-line script tattoo on her forearm, dark hair in a low side braid, at a dining table with a crocheted runner, family photos blurred behind, evening lamp light, maroon blouse.",
    "l12_frontyard": "A 55-year-old Latina woman with a broad square face, deep tan leathery skin, a wide flat nose, heavy jaw, salt-and-pepper hair in a tight bun, standing in a front yard by a low stucco wall, midday open shade, plain black tee.",
    "l13_stairwell": "A 48-year-old Latina woman with a thin gaunt face, sharp cheekbones, olive skin with rough texture, thin penciled eyebrows, dark lip liner, small faded lettering tattoo on the back of one hand, dark hair slicked into a tight ponytail, sitting on carpeted interior apartment stairs, warm bulb light, hoodie.",
    "l14_patio": "A 61-year-old Latina woman with a soft round deeply wrinkled face, light warm skin, drooping eyelids, thin grey curls, small gold stud earrings, on a covered patio in a rocking chair, potted plants blurred, soft overcast light, beige knit sweater.",
    "l15_breakroom": "A 46-year-old heavyset Latina woman with a wide round face, double chin, medium-deep brown skin, small close-set eyes, hair clipped back tight, in a workplace break room, vending machine blurred behind, fluorescent light, grey work polo.",
    "l16_parkbench": "A 53-year-old Latina woman with an angular bony face, dark indigenous skin, a prominent strong nose, short practical grey-flecked crop haircut, on a park bench, trees and path out of focus, golden late light, navy windbreaker.",
    "l17_kitchen2": "A 64-year-old Latina woman with a deeply lined oval face, warm brown skin, a strong jaw, silver hair in a high bun, age spots on her cheeks, missing a lower tooth just visible, at a tiled kitchen counter, cafetera on the stove blurred behind, morning light, apron over a housecoat.",
    "l18_garage": "A 48-year-old athletic broad-shouldered Latina woman with a strong chin, tan freckled skin, fine-line lettering tattoo along her forearm, dark hair in a short rough ponytail, sitting on a folding chair in an open garage, shelves blurred, daylight from the open door, denim overalls.",
    "l19_couch2": "A 57-year-old Latina woman with a full soft face, pale olive skin, dyed-black hair with grey roots showing, very thin penciled-on eyebrows, dark-lined lips, in the corner of a worn leather couch, crocheted blanket on the armrest, warm lamp light, black v-neck.",
    "l20_porch2": "A 45-year-old Latina woman with a narrow face, medium brown skin, a slight overbite, long straight black hair, the top edge of a fine-line script chest tattoo visible at her collar, leaning on a porch railing, screen door blurred, afternoon shade, athletic jacket.",
    "l21_bedroom2": "A 50-year-old Latina woman with a round face, deep brown skin, wide-set dark eyes, loose coily natural hair, a small nose stud, sitting against a headboard, plain comforter, bedside lamp on, plain white v-neck tee.",
}


def gen_one(slug, desc):
    out_path = os.path.join(OUT_DIR, f"{slug}.png")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"[skip] {slug}")
        return
    res = generate_gpt_image(desc + TAIL, aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {slug}: {str(res.get('raw'))[:140]}")
        return
    img = requests.get(res["urls"][0], timeout=120)
    img.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(img.content)
    print(f"[ok] {out_path}")


with ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(gen_one, s, d) for s, d in CANDIDATES.items()]
    for f in as_completed(futs):
        f.result()
print("done — persona batch 2 complete")
