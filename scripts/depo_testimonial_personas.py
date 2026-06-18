"""
Depo-Provera brain-meningioma — First-Person Testimonial persona candidates.
Messenger: ordinary Black woman ~45 (the long-term-Depo / meningioma demographic).
Diagnosis-first confession testimonial. 6 DISTINCT identities (explicit anthropometry per
persona — gpt-image-2 mode-collapses to one face on repeated demographic-only prompts).
Survivor-realism: ordinary, weathered, NOT glam/celebrity.

gpt-image-2 (KIE, 2K, 9:16 vertical talking-head anchor). Skip-if-exists.
Run:  .venv/bin/python scripts/depo_testimonial_personas.py [--only 1,3]
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_testimonial"
os.makedirs(OUT, exist_ok=True)

STYLE = (
    " Photoreal candid vertical 9:16 selfie-style documentary photo, shot on a front phone camera, "
    "soft natural indoor light. She looks toward the camera with a calm, tired, serious expression — "
    "the look of someone about to share something heavy. An ORDINARY everyday-looking woman, plain "
    "average features — NOT a glamour, fashion, or celebrity portrait. Natural skin with visible pores, "
    "uneven tone, fine lines, faint under-eye shadows, little or no makeup, no beauty retouching, no "
    "filter, no smoothing. Plain casual clothing. Absolutely NO text, no captions, no watermark, no logo."
)

PERSONAS = [
    dict(n=1, slug="couch_round_twa",
         desc=("An ordinary Black woman about 45. ROUND full-cheeked face, deep brown skin, broad nose, "
               "warm tired eyes, a small mole on her left cheek, short tightly-coiled natural hair (TWA) "
               "with a few greys. Slightly heavyset. Sitting on a beige living-room couch under a warm "
               "lamp, a throw cushion beside her.")),
    dict(n=2, slug="kitchen_oval_braids",
         desc=("An ordinary Black woman about 45. LONG oval face, medium-brown skin, high cheekbones, "
               "slim straight nose, thin reading glasses pushed up on her forehead, shoulder-length box "
               "braids. Slim build. Sitting at a plain kitchen table by a window in daytime.")),
    dict(n=3, slug="bedroom_heart_afro",
         desc=("An ordinary Black woman about 45. HEART-shaped face, rich dark mahogany skin, fuller lips, "
               "a small gap in her front teeth, short rounded natural afro greying at the edges. Average "
               "build. Sitting on the edge of her bed in a softly-lit bedroom, evening.")),
    dict(n=4, slug="porch_angular_locs",
         desc=("An ordinary Black woman about 45. ANGULAR narrow face, warm medium-brown skin, light "
               "freckles across the nose and cheeks, defined jaw, shoulder-length locs pulled back with a "
               "few grey strands. Lean build. Sitting on a front-porch step in soft natural daylight.")),
    dict(n=5, slug="couch_full_headwrap",
         desc=("An ordinary Black woman about 45. FULL rounded face with a soft double chin, deep ebony "
               "skin, kind heavy-lidded tired eyes, a patterned cloth headwrap. Heavyset build. On a couch "
               "with a knit throw blanket over her lap, warm low lamp light.")),
    dict(n=6, slug="hall_thin_tapered",
         desc=("An ordinary Black woman about 45. THIN drawn face, medium tan-brown skin, sharper "
               "cheekbones, faint worry lines on the forehead, short neatly-tapered relaxed hair, small "
               "gold hoop earrings. Slender. Standing in a plain home hallway, soft overcast window light.")),
]


def run(p):
    dest = os.path.join(OUT, f"persona_{p['n']:02d}_{p['slug']}.png")
    if os.path.exists(dest):
        return p, dest, "skip"
    prompt = p["desc"] + STYLE
    try:
        res = kie.generate_gpt_image(prompt, aspect_ratio="9:16", resolution="2K")
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
