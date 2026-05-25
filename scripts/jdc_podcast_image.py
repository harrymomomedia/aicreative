"""Podcast / radio-show key image — persona 3 (reflective 34) as host.
Warm & intimate late-night studio. i2i off the persona ref (same face), 9:16, 2K. 4 variations.
Output: outputs/illinois_jdc_podcast_p03/podcast_{1..4}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_gpt_image, download as kie_download

REF = Path("outputs/illinois_jdc_ugc/personas_demographic/persona_03_reflective_34.png")
OUT = Path("outputs/illinois_jdc_podcast_p03")
OUT.mkdir(parents=True, exist_ok=True)

STYLE = (
    " Photoreal, looks like a real photograph — natural skin texture with visible pores, fine lines, "
    "slight asymmetry, no beauty retouching, no filter, no skin smoothing. Warm low-key amber lighting, "
    "dark moody podcast/radio studio, shallow depth of field with soft background bokeh, cozy late-night "
    "atmosphere. Same man as the reference image (keep his exact face, beard, and skin tone). "
    "9:16 vertical. NO on-screen text, NO captions, NO watermarks."
)

PROMPTS = [
    # v1 — medium, leaning into the mic
    "A Black man in his mid-30s hosting a late-night radio show, seated at a podcast desk, leaning "
    "slightly toward a large studio condenser microphone on a boom arm with a pop filter, wearing "
    "over-ear studio headphones, mid-conversation, calm engaged expression looking just off-camera. "
    "Softly lit acoustic foam panels behind him." + STYLE,
    # v2 — 3/4 close, headphones around neck, to camera
    "A Black man in his mid-30s, a radio host, in a 3/4 close portrait at his podcast desk, over-ear "
    "studio headphones resting around his neck, one hand near the condenser microphone, warm rim light "
    "catching the edge of his face, looking directly into the camera, composed and intimate." + STYLE,
    # v3 — wider establishing studio
    "A wider establishing shot of a cozy radio studio: a Black man in his mid-30s sits behind the desk "
    "with a large condenser microphone on a boom arm, wearing over-ear headphones, a small softly "
    "glowing red light blurred in the background, warm practical lamp light, late-night mood." + STYLE,
    # v4 — intimate close mid-speech
    "An intimate close-up of a Black man in his mid-30s speaking into a studio condenser microphone "
    "during a late-night radio show, over-ear headphones on, focused expression, warm amber key light "
    "with deep soft shadows, blurred warm studio lights behind him." + STYLE,
]


def gen(i, prompt, url):
    print(f"[v{i}] submit ({len(prompt)} chars)", flush=True)
    r = generate_gpt_image(prompt=prompt, image_urls=[url], aspect_ratio="9:16", resolution="2K")
    if r["status"] != "success" or not r.get("urls"):
        return i, "FAILED", str(r.get("raw"))[:300]
    dst = OUT / f"podcast_{i}.png"
    kie_download(r["urls"][0], str(dst))
    return i, "success", str(dst)


def main():
    print(f"uploading ref {REF.name}", flush=True)
    url = kie_upload(str(REF))
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen, i, p, url): i for i, p in enumerate(PROMPTS, 1)}
        for f in as_completed(futs):
            i, status, info = f.result()
            print(f"[v{i}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
