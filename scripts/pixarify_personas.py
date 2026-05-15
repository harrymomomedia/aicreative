"""Stylize 11 Latina persona portraits into Pixar 3D characters via OpenAI gpt-image-2 i2i.

Keeps the background photoreal; only the person is converted to Pixar style.
Runs all 11 in parallel.

Usage: .venv/bin/python scripts/pixarify_personas.py
"""
import os
import base64
import concurrent.futures
import pathlib
import time

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("OPENAI_API_KEY")
if not KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

REF = pathlib.Path("outputs/1777697550119-gyvk6m8/reference")
REF_A2 = pathlib.Path("outputs/1777697550119-gyvk6m8/reference_a2")
OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/reference_pixar")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = (
    "Stylize ONLY the person in this image into Pixar/Disney 3D animated character style: "
    "large expressive eyes with cartoon highlights, soft stylized facial features, smooth shaded "
    "3D skin, slightly enlarged head proportions in Pixar's signature character design, vivid "
    "clean color, painterly hair texture. PRESERVE the person's exact identity — same face shape, "
    "same hair color and style, same age, same clothing (now with stylized fabric folds), same pose, "
    "same expression, same tattoos (now stylized), same skin tone. KEEP the entire background "
    "completely photorealistic and unchanged — real photograph of the original setting with all its "
    "real lighting, depth, textures, and photographic detail. The final image is a hybrid composite: "
    "a real-world photograph with a Pixar 3D animated character composited into it."
)

CHARACTERS = {
    "a_la_sidewalk":          REF / "character_a_la_sidewalk.png",
    "b_kitchen":              REF / "character_b_kitchen.png",
    "c_car":                  REF / "character_c_car.png",
    "d_orchard":              REF / "character_d_orchard.png",
    "a1_la_sidewalk":         REF / "character_a1_la_sidewalk.png",
    "a2_la_sidewalk":         REF / "character_a2_la_sidewalk.png",
    "a3_la_sidewalk":         REF / "character_a3_la_sidewalk.png",
    "a4_la_sidewalk":         REF / "character_a4_la_sidewalk.png",
    "a5_la_sidewalk":         REF / "character_a5_la_sidewalk.png",
    "a4_car_dashmount":       REF / "character_a4_car_dashmount_serious.png",
    "a2_livingroom":          REF_A2 / "a2_livingroom.png",
}

MODEL = "gpt-image-2"
SIZE = "1024x1536"  # portrait, ~2:3 (closest to 9:16 source)


def pixarify(slug, src):
    t0 = time.time()
    print(f"[{slug}] start", flush=True)
    with open(src, "rb") as f:
        files = {"image": (os.path.basename(src), f, "image/png")}
        data = {
            "model": MODEL,
            "prompt": PROMPT,
            "n": "1",
            "size": SIZE,
            "quality": "high",
        }
        r = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {KEY}"},
            files=files, data=data, timeout=600,
        )
    dt = time.time() - t0
    if not r.ok:
        print(f"[{slug}] FAILED ({dt:.1f}s) {r.status_code}: {r.text[:400]}", flush=True)
        return slug, None
    try:
        b64 = r.json()["data"][0]["b64_json"]
    except Exception as e:
        print(f"[{slug}] bad response ({dt:.1f}s): {e} body={r.text[:300]}", flush=True)
        return slug, None
    out = OUT_DIR / f"{slug}_pixar.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"[{slug}] DONE ({dt:.1f}s) → {out}", flush=True)
    return slug, str(out)


def main():
    print(f"Pixarifying {len(CHARACTERS)} characters → {OUT_DIR}", flush=True)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(pixarify, slug, src): slug for slug, src in CHARACTERS.items()}
        for fut in concurrent.futures.as_completed(futs):
            slug, path = fut.result()
            results[slug] = path
    print("\n=== summary ===", flush=True)
    for slug in CHARACTERS:
        print(f"  {slug:24s} → {results.get(slug) or 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
