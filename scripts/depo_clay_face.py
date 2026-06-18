"""Depo claymation explainer — REFERENCE FACE candidates (the consistent protagonist).

One claymation Black woman ~45 becomes THE face for every shot: the picked candidate is uploaded
and passed as a Seedance reference_image on each protagonist clip, so her face stays consistent
across the whole video (Seedance has no built-in cross-clip identity lock; a face ref is the fix).

Aardman/Wallace-&-Gromit clay portrait, gpt-image-2 (KIE, 2K, 3:4 headshot). 4 candidates.
Run:  .venv/bin/python scripts/depo_clay_face.py
"""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import kie_client as kie

OUT = "outputs/depo_claymation/face"
os.makedirs(OUT, exist_ok=True)

STYLE = (
    " Handmade claymation character portrait, Aardman Wallace-and-Gromit stop-motion style: "
    "plasticine modeling clay with visible thumbprints and fingerprint dents pressed into the soft "
    "clay, slightly uneven hand-sculpted surfaces, matte clay sheen. Head-and-shoulders, looking "
    "calmly and a little wearily toward the camera. Soft neutral studio light, plain warm grey "
    "background. Vertical portrait. No text, no captions, no watermark."
)

FACES = [
    dict(n=1, slug="round_twistout",
         desc=("An ordinary Black woman about 45, warm deep-brown clay skin, a soft ROUND kind face, "
               "full cheeks, warm tired eyes, short natural twist-out hair with a few greys, wearing "
               "a plain knit cardigan over a blouse.")),
    dict(n=2, slug="oval_bun_glasses",
         desc=("An ordinary Black woman about 45, medium-brown clay skin, a LONG OVAL face, high "
               "cheekbones, thin reading glasses, dark hair in a low neat bun, wearing a plain "
               "cardigan over a collared blouse.")),
    dict(n=3, slug="full_headwrap",
         desc=("An ordinary Black woman about 45, rich dark-brown clay skin, a FULL rounded face with "
               "a soft double chin, kind heavy-lidded eyes, a patterned cloth headwrap, wearing a "
               "plain dark top and cardigan.")),
    dict(n=4, slug="heart_afro_grey",
         desc=("An ordinary Black woman about 45, warm brown clay skin, a HEART-shaped face, fuller "
               "lips, a short rounded natural afro greying at the edges, faint laugh lines, wearing a "
               "plain cardigan.")),
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
