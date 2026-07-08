"""Depo TikTok-voice series (depo_tt) — persona candidates.
Ad 05 "THE GATEKEEPER": direct, confident, playful-stern Black woman ~45, talking straight into
the lens. 3 candidate identities (explicit anthropometry each — gpt-image-2 mode-collapses on
demographic-only prompts), all NEW faces vs the ugc10 ten. Static indoor scenes only (no cars,
no windows-to-street). gpt-image-2 (KIE) 9:16 2K, iPhone-front-camera-frame look.

  .venv/bin/python scripts/depo_tt_personas.py [--only 1,3]
"""
import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_tt"
os.makedirs(OUT, exist_ok=True)

STYLE = (
    " Photoreal vertical 9:16 still that looks like a FRAME GRABBED FROM A REAL iPHONE FRONT-CAMERA "
    "VIDEO — slightly soft, natural phone-camera look, mild sensor noise, ordinary indoor lighting, "
    "NOT a crisp DSLR photo, NOT glamour, NOT a studio portrait. She looks STRAIGHT INTO the lens "
    "with a confident, direct, slightly playful no-nonsense expression, chin a touch raised, about "
    "to tell you something. An ordinary everyday-looking woman, plain average features, natural skin "
    "with visible pores, uneven tone, fine lines, little or no makeup, no retouching, no filter. "
    "STATIC indoor home background — NO window showing a street, NO cars, nothing in motion. "
    "Absolutely NO text, captions, watermark, or logo."
)

PERSONAS = [
    dict(n=1, slug="couch_pixie",
         desc="Black woman about 45. OVAL-SQUARE face with a defined jaw, medium-deep brown skin, "
              "strong arched brows, short relaxed pixie cut, small stud earrings, average build. "
              "Sitting forward on a slate-grey couch, warm floor lamp behind, plain wall."),
    dict(n=2, slug="bedroom_twists",
         desc="Black woman about 45. LONG face, deep rich brown skin, high cheekbones, long thin "
              "senegalese twists falling past her shoulders, one brow slightly raised, slim build. "
              "Sitting cross-legged on her bed against the headboard, soft warm bedroom lamp light."),
    dict(n=3, slug="kitchen_puff",
         desc="Black woman about 45. ROUND-OVAL face, warm brown skin with light freckles, a natural "
              "afro puff held with a wide black headband, hoop earrings, fuller build. Standing at a "
              "kitchen island, mug beside her, plain cabinets behind, bright even indoor light."),
]


def run(p):
    dest = os.path.join(OUT, f"gate_persona_{p['n']:02d}_{p['slug']}.png")
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
    args = ap.parse_args()
    ps = PERSONAS
    if args.only:
        want = {int(x) for x in args.only.split(",") if x.strip().isdigit()}
        ps = [p for p in PERSONAS if p["n"] in want]
    with ThreadPoolExecutor(max_workers=3) as ex:
        for f in as_completed({ex.submit(run, p): p for p in ps}):
            p, path, status = f.result()
            print(f"[{status}] {p['n']} {p['slug']} -> {path}", flush=True)


if __name__ == "__main__":
    main()
