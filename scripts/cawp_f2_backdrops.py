"""F2 redesign — documentary b-roll backdrop images for each card beat (gpt-image-2 @2K 9:16).
Faceless, no readable text in image, news-b-roll style. Type gets comped over these."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests

from kie_client import generate_gpt_image

OUT_DIR = "outputs/cawp_f2_form/backdrops"
os.makedirs(OUT_DIR, exist_ok=True)

TAIL = (" Photoreal documentary news b-roll photograph, natural real-world light, slight grain, "
        "shot like a Frontline segment on a news camera. NOT stylized, NOT staged-looking. "
        "No people's faces visible, no readable text or lettering anywhere, no watermark. "
        "Vertical 9:16 composition with calm negative space.")

SHOTS = {
    "bd0_phone_porch": "Close over-the-shoulder detail of a woman's hands holding a smartphone with a dark blank screen, sitting on concrete apartment steps, warm late-afternoon light.",
    "bd1_fence": "Tall chain-link prison fence with coiled razor wire against a hazy golden-hour sky, low beige institutional buildings far in the background.",
    "bd2_years": "Old wall calendar pages and a few faded loose photographs lying face-down on a worn wooden table, soft window light.",
    "bd3_corridor": "Empty institutional corridor with painted cinder-block walls and a line of identical heavy doors, flat fluorescent light.",
    "bd4_ownwords": "A spiral notebook open to blank lined pages with a ballpoint pen resting on it, kitchen table, morning light.",
    "bd5_norecords": "A single closed manila folder on an otherwise empty wooden table, soft side light, shallow depth of field.",
    "bd6_private": "The front door of a modest apartment seen from inside, closed, brass deadbolt detail, quiet warm hallway light.",
    "bd7_qualify": "Morning sunlight coming through window blinds into a modest living room, visible light beams, dust motes.",
    "bd8_free": "A kitchen table with a coffee mug and a smartphone lying face-down, morning light, shallow depth of field.",
    "bd9_cta": "A woman's hand reaching to pick up a smartphone from a wooden table, screen dark, warm evening lamp light.",
}


def gen(slug, desc):
    out = os.path.join(OUT_DIR, f"{slug}.png")
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f"[skip] {slug}")
        return
    res = generate_gpt_image(desc + TAIL, aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[FAIL] {slug}: {str(res.get('raw'))[:160]}")
        return
    img = requests.get(res["urls"][0], timeout=120)
    img.raise_for_status()
    with open(out, "wb") as f:
        f.write(img.content)
    print(f"[ok] {out}")


with ThreadPoolExecutor(max_workers=4) as ex:
    futs = [ex.submit(gen, s, d) for s, d in SHOTS.items()]
    for f in as_completed(futs):
        f.result()
print("backdrops done")
