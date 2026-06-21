"""Depo meningioma UGC scale-out — 10 distinct Black-woman ~45 personas for 10 unique scripts.
Diagnosis-first testimonial messengers. gpt-image-2 (KIE) 4:5 2K, iPhone-front-camera-frame look.
STATIC INDOOR settings ONLY — no cars, no street/window-to-road, nothing in motion (keeps the Veo
scene consistent). Each persona = an explicit distinct anthropometry block (gpt-image-2 mode-collapses
on demographic-only prompts). Survivor realism: ordinary, weathered, NOT glam/celebrity.

  .venv/bin/python scripts/depo_ugc10_personas.py [--only 1,3]
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_ugc10"
os.makedirs(OUT, exist_ok=True)

STYLE = (
    " Photoreal vertical 9:16 still that looks like a FRAME GRABBED FROM A REAL iPHONE FRONT-CAMERA "
    "VIDEO — slightly soft, natural phone-camera look, mild sensor noise, ordinary indoor lighting, "
    "NOT a crisp DSLR photo, NOT glamour, NOT a studio portrait. She looks toward the phone, calm and "
    "a little tired, about to speak. An ORDINARY everyday-looking woman, plain average features, "
    "natural skin with visible pores, uneven tone, fine lines, faint under-eye shadows, little or no "
    "makeup, no retouching, no filter, no smoothing. STATIC indoor home background — NO window showing "
    "a street, NO cars, nothing in motion. Absolutely NO text, captions, watermark, or logo."
)

PERSONAS = [
    dict(n=1, slug="couch_round_twa",
         desc="Black woman about 45. ROUND full-cheeked face, deep brown skin, broad nose, warm tired "
              "eyes, small mole on left cheek, short tightly-coiled natural hair (TWA) with a few greys, "
              "slightly heavyset. Sitting on a beige living-room couch, warm lamp behind her."),
    dict(n=2, slug="kitchen_oval_braids",
         desc="Black woman about 45. LONG oval face, medium-brown skin, high cheekbones, slim nose, thin "
              "reading glasses pushed up on her forehead, shoulder-length box braids, slim build. Seated "
              "at a plain kitchen table, cabinets behind her."),
    dict(n=3, slug="bedroom_heart_afro",
         desc="Black woman about 45. HEART-shaped face, rich dark mahogany skin, fuller lips, small gap in "
              "front teeth, short rounded natural afro greying at the edges, average build. Sitting on the "
              "edge of her bed, soft bedroom lamp light."),
    dict(n=4, slug="desk_angular_locs",
         desc="Black woman about 45. ANGULAR narrow face, warm medium-brown skin, light freckles across the "
              "nose, defined jaw, shoulder-length locs pulled back with a few grey strands, lean build. "
              "Sitting at a small home desk, plain wall behind."),
    dict(n=5, slug="couch_full_headwrap",
         desc="Black woman about 45. FULL rounded face with a soft double chin, deep ebony skin, kind "
              "heavy-lidded tired eyes, a patterned cloth headwrap, heavyset build. On a couch with a knit "
              "throw blanket, warm low lamp light."),
    dict(n=6, slug="dining_thin_tapered",
         desc="Black woman about 45. THIN drawn face, medium tan-brown skin, sharper cheekbones, faint "
              "worry lines, short neatly-tapered relaxed hair, small gold hoop earrings, slender. Seated in "
              "a dining nook, plain wall and a framed picture behind."),
    dict(n=7, slug="armchair_square_twists",
         desc="Black woman about 45. SQUARE strong-jawed face, deep brown skin, wide-set eyes, shoulder "
              "two-strand twists, reading glasses on a beaded chain, sturdy build. Seated in a living-room "
              "armchair, bookshelf softly out of focus behind."),
    dict(n=8, slug="counter_long_bun",
         desc="Black woman about 45. LONG face, medium-brown skin, high cheekbones, a small mole near the "
              "lip, sleek low bun, average build. Standing at a kitchen counter, plain backsplash behind."),
    dict(n=9, slug="bedroom_soft_curly",
         desc="Black woman about 45. SOFT round face, rich brown skin, short curly natural hair with a "
              "faint copper tint, fuller build, gentle tired eyes. Sitting in a softly lamp-lit bedroom, "
              "headboard behind."),
    dict(n=10, slug="hall_broad_cornrows",
         desc="Black woman about 45. BROAD face, deep brown skin, strong brows, neat cornrows braided "
              "straight back, heavier athletic build. Standing against a plain interior hallway wall, soft "
              "indoor light."),
]


def run(p):
    dest = os.path.join(OUT, f"persona_{p['n']:02d}_{p['slug']}.png")
    if os.path.exists(dest):
        return p, dest, "skip"
    try:
        res = kie.generate_gpt_image(p["desc"] + STYLE, aspect_ratio="9:16", resolution="2K")
    except Exception as e:
        return p, None, f"err:{e}"
    if res.get("status") != "success" or not res.get("urls"):
        return p, None, f"fail:{str(res.get('raw'))[:120]}"
    kie.download(res["urls"][0], dest)
    return p, dest, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    ps = PERSONAS
    if args.only:
        want = {int(x) for x in args.only.split(",") if x.strip().isdigit()}
        ps = [p for p in PERSONAS if p["n"] in want]
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run, p): p for p in ps}
        for fut in as_completed(futs):
            p, path, status = fut.result()
            print(f"[{status}] {p['n']:02d} {p['slug']} -> {path}", flush=True)


if __name__ == "__main__":
    main()
