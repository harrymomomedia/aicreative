"""Person-swap that PRESERVES the original background — nano-banana-2 (Gemini edit).

gpt-image-2 edit mode re-imagines the whole scene; nano-banana-2 does targeted
edits that keep the rest of the photo pixel-faithful. Goal: keep the EXACT car
interior / seatbelt / window-trees / daylight, change ONLY the person.

Source: /Users/harry/Desktop/d1989e35660801493e44294c01727272.webp
Output: outputs/car_selfie_swap/nb_swap_{1..5}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file, generate_nano_banana, download

SRC = "/Users/harry/Desktop/d1989e35660801493e44294c01727272.webp"
OUT_DIR = Path("outputs/car_selfie_swap")
OUT_DIR.mkdir(parents=True, exist_ok=True)

KEEP = (
    "Keep EVERYTHING else in the photo identical and untouched: the exact same "
    "car interior, the same seats and rear headrests, the same light-grey "
    "ceiling and sunroof, the same black seatbelt across the chest, the same "
    "side window with the bare winter trees, grass field and house outside, the "
    "same warm natural daylight, the same selfie camera angle and framing, and "
    "the same grey t-shirt. Change ONLY the person's face, head and skin. Do "
    "NOT alter the background, the car, the lighting, the seatbelt, or the "
    "clothing. Keep it a realistic candid phone selfie."
)

VARIATIONS = {
    "nb_swap_1": (
        "Replace the man in this photo with a different Black man in his early "
        "30s with a short clean fade haircut, clean-shaven, no sunglasses, "
        "warm genuine smile. " + KEEP
    ),
    "nb_swap_2": (
        "Replace the man in this photo with a different Black man in his early "
        "30s with a short rounded afro, neat short full beard, dark aviator "
        "sunglasses, easy confident expression. " + KEEP
    ),
    "nb_swap_3": (
        "Replace the man in this photo with a different Black man in his early "
        "30s with short freeform twists and a clean taper, light goatee and "
        "mustache, no sunglasses, calm soft smile. " + KEEP
    ),
    "nb_swap_4": (
        "Replace the man in this photo with a different Black man in his early "
        "30s with a clean-shaven shaved/bald head, short trimmed beard, "
        "sunglasses pushed up on top of his head, broad warm smile. " + KEEP
    ),
    "nb_swap_5": (
        "Replace the man in this photo with a different Black man in his early "
        "30s with a short 360-waves haircut, light mustache and chin stubble, "
        "clear thin-framed glasses, friendly approachable smile. " + KEEP
    ),
}


def gen(slug, prompt, src_url):
    out = OUT_DIR / f"{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating...", flush=True)
    r = generate_nano_banana(prompt=prompt, image_urls=[src_url])
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
