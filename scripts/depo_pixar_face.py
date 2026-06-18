"""Depo PIXAR-style explainer — REFERENCE FACE candidates (the consistent protagonist).

Same role as depo_clay_face.py but in a modern 3D animated feature-film look. The picked face is
uploaded and passed as a Seedance reference_image on every protagonist shot, so she's the same
woman throughout. Black woman ~45 (target audience).

gpt-image-2 (KIE, 2K, 3:4 headshot). 4 candidates.
Run:  .venv/bin/python scripts/depo_pixar_face.py
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_pixar/face"
os.makedirs(OUT, exist_ok=True)

STYLE = (
    " Modern 3D animated feature-film character portrait, high-end CG animation style (big-studio "
    "3D animated movie / Pixar-DreamWorks look): smooth stylized features, large warm expressive "
    "eyes, soft subsurface-scattering skin, gently rounded appealing proportions, polished cinematic "
    "studio lighting, plain warm grey background, head-and-shoulders, looking calmly and a little "
    "wearily toward the camera. High-quality 3D render. No text, no captions, no watermark."
)

FACES = [
    dict(n=1, slug="round_twistout",
         desc=("An ordinary Black woman about 45, warm deep-brown skin, a soft ROUND kind face, full "
               "cheeks, warm tired eyes, short natural twist-out hair with a few greys, wearing a "
               "plain knit cardigan over a blouse.")),
    dict(n=2, slug="oval_bun_glasses",
         desc=("An ordinary Black woman about 45, medium-brown skin, a LONG OVAL face, high "
               "cheekbones, thin reading glasses, dark hair in a low neat bun, wearing a plain "
               "cardigan over a collared blouse.")),
    dict(n=3, slug="full_headwrap",
         desc=("An ordinary Black woman about 45, rich dark-brown skin, a FULL rounded face with a "
               "soft double chin, kind heavy-lidded eyes, a patterned cloth headwrap, wearing a plain "
               "dark top and cardigan.")),
    dict(n=4, slug="heart_afro_grey",
         desc=("An ordinary Black woman about 45, warm brown skin, a HEART-shaped face, fuller lips, a "
               "short rounded natural afro greying at the edges, faint laugh lines, wearing a plain "
               "cardigan.")),
]


def run(p):
    dest = os.path.join(OUT, f"face_{p['n']:02d}_{p['slug']}.png")
    if os.path.exists(dest):
        return p, dest, "skip"
    try:
        res = kie.generate_gpt_image(p["desc"] + STYLE, aspect_ratio="3:4", resolution="2K")
    except Exception as e:
        return p, None, f"err:{e}"
    if res.get("status") != "success" or not res.get("urls"):
        return p, None, f"fail:{str(res.get('raw'))[:120]}"
    kie.download(res["urls"][0], dest)
    return p, dest, "ok"


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(run, p): p for p in FACES}
        for fut in as_completed(futs):
            p, path, status = fut.result()
            print(f"[{status}] {p['n']:02d} {p['slug']} -> {path}", flush=True)


if __name__ == "__main__":
    main()
