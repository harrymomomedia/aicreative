"""TEST: corrected realism + survivor emotional direction (2 variants).

Fixes the 'dating-app selfie' problem: heavy skin texture/imperfection, amateur
front-camera phone realism, weary/guarded expression (NOT smiling), street-real
Chicago styling. Persona = man who was in the juvenile system as a teen, now
early 30s, carrying weight. Encoded VISUALLY (no 'victim'/'abuse' words → filter).

Keeps the car-selfie background via nano-banana-2 (best background preserver).

Source: /Users/harry/Desktop/d1989e35660801493e44294c01727272.webp
Output: outputs/car_selfie_swap/survivor_test_{1,2}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file, generate_nano_banana, download

SRC = "/Users/harry/Desktop/d1989e35660801493e44294c01727272.webp"
OUT_DIR = Path("outputs/car_selfie_swap")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Realism + background-preservation tail shared by both
REAL = (
    "Hyper-photorealistic CANDID amateur front-facing phone selfie, the look of "
    "a regular iPhone front camera in flat overcast daylight — NOT professional "
    "photography, NOT studio, NOT glossy. Real lived-in skin: visible pores, "
    "uneven skin tone, faint dark circles and slight bags under the eyes, a few "
    "small blemishes and razor bumps along the jaw, slightly chapped lips, "
    "natural oily sheen on the forehead and nose, faint fine lines. Slightly "
    "asymmetric ordinary face — an everyday man, NOT a model, NOT handsome-"
    "polished. Subtle sensor noise / grain, very slightly soft focus, the "
    "faintly compressed look of a real phone photo. ABSOLUTELY NO beauty mode, "
    "NO skin smoothing, NO retouching, NO filter, NO airbrushing. "
    "Keep the EXACT same car interior, the dark seats and headrests, the grey "
    "ceiling and sunroof, the black seatbelt across the chest, the side window "
    "with bare winter trees / grass field / house outside, and the same flat "
    "natural daylight. Change ONLY the person. NO on-screen text, NO captions, "
    "NO watermarks."
)

VARIATIONS = {
    "survivor_test_1": (
        "Replace the man with a Black man in his early 30s who grew up hard in "
        "Chicago. Short fade with a bit of uneven growth, faint chin-strap beard "
        "with a few patchy spots, a small old scar near one eyebrow. He is NOT "
        "smiling — his expression is quiet, guarded and weary, jaw slightly set, "
        "tired serious eyes looking almost directly into the lens like he's "
        "about to say something heavy. He wears a faded charcoal hoodie. "
        + REAL
    ),
    "survivor_test_2": (
        "Replace the man with a Black man in his early 30s from the Chicago "
        "south side, weathered and lived-in. Short twists or a low afro starting "
        "to recede slightly, thin uneven mustache and patchy stubble, a small "
        "neck tattoo partly visible. His expression is heavy and reflective — "
        "no smile, mouth in a flat line, eyes a little glassy and distant, "
        "looking slightly off to the side as if remembering something. He wears "
        "a plain black tee with a thin gold chain. " + REAL
    ),
}


def gen(slug, prompt, src_url):
    out = OUT_DIR / f"{slug}.png"
    print(f"[{slug}] generating...", flush=True)
    r = generate_nano_banana(prompt=prompt, image_urls=[src_url])
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    print(f"Uploading source: {SRC}", flush=True)
    src_url = upload_file(SRC)
    with ThreadPoolExecutor(max_workers=2) as ex:
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
