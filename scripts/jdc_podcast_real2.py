"""10 MORE podcast personas (real_11..real_20) — ages 27-37, ORDINARY/REAL-looking.
Distinct from real_01..10. Headphone-FREE (headphones caused video-gen issues), podcast-mic studio.
Variety: braids/fade/twists/afro/dreads/bald/salt-pepper, varied facial hair, builds, skin tones,
2 Latino for distribution range, varied wardrobe + lighting + expression.
t2i, 9:16, 2K. Output: outputs/jdc_podcast_personas/real_{11..20}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/jdc_podcast_personas")
OUT.mkdir(parents=True, exist_ok=True)

TAIL = (
    " Photoreal candid documentary photo (NOT a glamour or fashion shoot, NOT a celebrity portrait) — "
    "an ordinary everyday-looking man, plain average features, real and relatable. Natural skin with "
    "visible pores, blemishes, uneven tone, slight under-eye shadows, imperfect teeth, no beauty "
    "retouching, no filter, no makeup, no skin smoothing. In a podcast/radio studio with a condenser "
    "microphone in the frame. NO headphones on his head or neck. Shallow depth of field, soft "
    "background bokeh. 9:16 vertical. NO on-screen text, NO captions, NO watermarks."
)

HOSTS = [
    ("real_11", "An ordinary Black man, age 33, medium-brown skin, short box braids tied back, a thin "
     "chinstrap beard, plain maroon t-shirt, calm and serious looking just off-camera. Warm studio light."),
    ("real_12", "An ordinary Black man, age 28, dark skin, a high-top fade, clean-shaven, slim build, "
     "olive-green crewneck sweatshirt, earnest and leaning forward mid-sentence. Bright neutral studio."),
    ("real_13", "An ordinary Latino man, age 31, medium skin, short slicked-back hair, a full dark beard, "
     "plain charcoal henley, thoughtful and grounded expression. Soft warm light."),
    ("real_14", "An ordinary Black man, age 36, deep dark skin tone, bald head with a graying full beard, "
     "broad heavyset build, plain heather-grey t-shirt, weary and reflective. Moody low light."),
    ("real_15", "An ordinary Black man, age 29, medium-brown skin, short twists with faded sides, a light "
     "mustache, plain rust-orange t-shirt, a soft uneasy expression. Natural daylight studio."),
    ("real_16", "An ordinary Black man, age 34, dark skin, a short afro fade, thin-rimmed glasses, a neat "
     "goatee, plain navy henley, composed and sincere. Clean bright studio."),
    ("real_17", "An ordinary Latino man, age 27, light-brown skin, short curly hair, light stubble, plain "
     "white t-shirt, a nervous faint half-smile. Soft cool light."),
    ("real_18", "An ordinary Black man, age 37, medium skin, neat short salt-and-pepper hair with a "
     "receding hairline, clean-shaven with just a thin mustache, plain collared work shirt, dignified and "
     "weary. Warm dim light."),
    ("real_19", "An ordinary Black man, age 30, dark skin, dreadlocks pulled up into a bun, clean-shaven, "
     "lean build, plain black t-shirt, a quiet intensity looking off-camera. Neutral studio light."),
    ("real_20", "An ordinary Black man, age 32, medium-brown skin, shaved bald head, a thick mustache and "
     "no beard, a bit heavyset, plain grey polo shirt, open and sincere mid-speech. Bright soft light."),
]


def gen(slug, prompt):
    full = prompt + TAIL
    print(f"[{slug}] submit ({len(full)} chars)", flush=True)
    r = generate_gpt_image(prompt=full, aspect_ratio="9:16", resolution="2K")
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:300]
    dst = OUT / f"{slug}.png"
    kie_download(r["urls"][0], str(dst))
    return slug, "success", str(dst)


def main():
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen, slug, p): slug for slug, p in HOSTS}
        for f in as_completed(futs):
            slug, status, info = f.result()
            print(f"[{slug}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
