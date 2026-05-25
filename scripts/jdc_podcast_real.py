"""10 MORE podcast personas — ages 27-37, ORDINARY/REAL-looking (NOT celebrity/model).
Context: survivors who will confess childhood abuse, so they must read as everyday, relatable,
vulnerable people. Podcast-mic setting, v4 close-up framing. Mix of warm/bright/neutral moods.
t2i, 9:16, 2K. Output: outputs/jdc_podcast_personas/real_{01..10}.png
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
    "microphone in the frame. Shallow depth of field, soft background bokeh. 9:16 vertical. "
    "NO on-screen text, NO captions, NO watermarks."
)

HOSTS = [
    ("real_01", "An ordinary Black man, age 32, short fade with light stubble, plain navy t-shirt, "
     "reflective and serious expression looking just off-camera, headphones resting on the desk. "
     "Warm intimate low light, cozy studio."),
    ("real_02", "An ordinary Black man, age 28, short twists and a patchy beard, grey hoodie, "
     "mid-sentence telling a story, earnest, over-ear headphones on. Soft neutral daylight studio."),
    ("real_03", "An ordinary Black man, age 36, short hair with a slightly receding hairline and a "
     "full beard with grey flecks, plain flannel shirt, heavy tired expression. Warm low light."),
    ("real_04", "An ordinary Black man, age 30, bald with light stubble, a bit heavyset, plain black "
     "t-shirt, quiet and vulnerable, looking down slightly. Dim warm lighting."),
    ("real_05", "An ordinary Black man, age 34, short waves, a mustache and thin-framed glasses, "
     "button-up work shirt, sincere mid-speech. Bright clean studio, soft cool light."),
    ("real_06", "An ordinary Black man, age 27, short afro, clean-shaven, lean build, plain white "
     "t-shirt, nervous and vulnerable, headphones around his neck. Soft natural light."),
    ("real_07", "An ordinary Black man, age 37, shoulder-length locs tied back with some grey, short "
     "beard, dark hoodie, somber and reflective. Moody warm lighting."),
    ("real_08", "An ordinary Black man, age 31, fade with a side part and a goatee, a little "
     "overweight, plain polo shirt, sincere and open mid-speech. Neutral bright studio."),
    ("real_09", "An ordinary Black man, age 29, short curly hair, light stubble, a small gap in his "
     "front teeth, plain heather-grey t-shirt, an uneasy faint half-smile. Warm soft light."),
    ("real_10", "An ordinary Black man, age 35, shaved sides going bald on top with a full beard, "
     "plain dark t-shirt, intense quiet eye contact with the camera, over-ear headphones on. "
     "Cool neutral lighting."),
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
