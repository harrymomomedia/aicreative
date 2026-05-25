"""Swap the person in the car-selfie photo with a different Black man in his
early 30s, keeping the EXACT car interior / seatbelt / selfie angle / daylight.

gpt-image-2 image-edit via KIE (default image provider per CLAUDE.md 2026-05-20).
5 variations — varied face/hair/grooming so the user can pick one.

Source: /Users/harry/Desktop/d1989e35660801493e44294c01727272.webp
Output: outputs/car_selfie_swap/swap_{1..5}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file, generate_gpt_image, download

SRC = "/Users/harry/Desktop/d1989e35660801493e44294c01727272.webp"
OUT_DIR = Path("outputs/car_selfie_swap")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEEP = (
    "KEEP EVERYTHING ELSE IN THE PHOTO EXACTLY THE SAME: the same car interior "
    "(grey/black seats, rear headrests visible behind, light-grey ceiling, "
    "sunroof edge), the same driver's-seat selfie POV and framing, the same "
    "black seatbelt running diagonally across the chest, the same side window "
    "with bare winter trees and a grassy field and a house outside in soft "
    "daylight, the same warm natural candid lighting and casual phone-selfie "
    "feel. He wears a plain heather-grey crew-neck t-shirt (NO text, NO logo, "
    "NO graphics). Photoreal, real skin texture, visible pores, slight "
    "asymmetry, no beauty retouching, no filter. Looks like a real candid "
    "phone selfie. NO on-screen text, NO captions, NO watermarks."
)

VARIATIONS = {
    "swap_1": (
        "Replace the man in this photo with a DIFFERENT Black man in his early "
        "30s: short clean fade haircut, clean-shaven, no sunglasses (warm "
        "friendly eyes visible), genuine relaxed smile. " + KEEP
    ),
    "swap_2": (
        "Replace the man in this photo with a DIFFERENT Black man in his early "
        "30s: short rounded afro, neat short full beard, dark aviator "
        "sunglasses, easy confident smile. " + KEEP
    ),
    "swap_3": (
        "Replace the man in this photo with a DIFFERENT Black man in his early "
        "30s: short freeform twists with a clean taper, light goatee and "
        "mustache, no sunglasses, calm soft smile. " + KEEP
    ),
    "swap_4": (
        "Replace the man in this photo with a DIFFERENT Black man in his early "
        "30s: clean-shaven bald / shaved head, short trimmed beard, sunglasses "
        "pushed up resting on top of his head, broad warm smile. " + KEEP
    ),
    "swap_5": (
        "Replace the man in this photo with a DIFFERENT Black man in his early "
        "30s: short 360-waves haircut, light mustache and a little chin "
        "stubble, clear thin-framed glasses, friendly approachable smile. "
        + KEEP
    ),
}


def gen(slug, prompt, src_url):
    out = OUT_DIR / f"{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating...", flush=True)
    r = generate_gpt_image(
        prompt=prompt,
        image_urls=[src_url],
        aspect_ratio="3:4",
        resolution="2K",
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    print(f"Uploading source: {SRC}", flush=True)
    src_url = upload_file(SRC)
    print(f"Source URL: {src_url}", flush=True)

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(gen, s, p, src_url): s for s, p in VARIATIONS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                _, status, info = f.result()
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
