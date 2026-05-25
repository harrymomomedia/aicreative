"""5 NEW distinct podcast-host personas, in the v4 style (intimate close-up speaking into the mic,
headphones on). Mix of moods: warm/intimate + modern/bright + gritty. Distinct people to mix & match.
text-to-image, 9:16, 2K. Output: outputs/jdc_podcast_personas/host_{1..5}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/jdc_podcast_personas")
OUT.mkdir(parents=True, exist_ok=True)

TAIL = (
    " Photoreal close-up, looks like a real photograph — natural skin texture, visible pores, fine "
    "lines, slight asymmetry, no beauty retouching, no filter, no skin smoothing. Over-ear studio "
    "headphones on, speaking into a large studio condenser microphone (mic partly in the frame). "
    "Shallow depth of field, soft background bokeh. 9:16 vertical. NO on-screen text, NO captions, "
    "NO watermarks."
)

# (slug, prompt)
HOSTS = [
    ("host_1_warm_afro",
     "An intimate close-up of a Black man in his late 20s with a short rounded afro and a full "
     "well-groomed beard, deep brown skin, mid-speech into a podcast microphone, focused passionate "
     "expression. Warm amber low-key lighting, dark cozy studio, deep soft shadows." + TAIL),
    ("host_2_bright_glasses",
     "An intimate close-up of a Black man in his early 30s with a clean skin fade, neat goatee, and "
     "clear modern glasses, medium-brown skin, speaking into a podcast microphone with an animated "
     "engaged expression. Bright clean contemporary studio, crisp neutral-cool lighting, light "
     "background with subtle bokeh." + TAIL),
    ("host_3_warm_mature",
     "An intimate close-up of a Black man in his mid-40s with a salt-and-pepper beard and short "
     "greying hair, rich dark skin, seasoned and calm, speaking into a podcast microphone. Warm "
     "intimate lamp light, moody late-night studio, soft shadows." + TAIL),
    ("host_4_bright_locs",
     "An intimate close-up of a Black man in his mid-20s with shoulder-length locs pulled back and a "
     "light beard, warm brown skin, youthful charismatic energy, mid-laugh while speaking into a "
     "podcast microphone. Bright modern studio with subtle teal and purple LED accent lights softly "
     "blurred behind, clean fresh look." + TAIL),
    ("host_5_gritty_bald",
     "An intimate close-up of a Black man in his 30s, bald head with a thick full beard and a thin "
     "gold chain, deep brown skin, confident charismatic expression mid-speech into a podcast "
     "microphone. Slightly gritty documentary lighting, real studio, warm practical light with a "
     "cooler edge." + TAIL),
]


def gen(i, slug, prompt):
    print(f"[{slug}] submit ({len(prompt)} chars)", flush=True)
    r = generate_gpt_image(prompt=prompt, aspect_ratio="9:16", resolution="2K")
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:300]
    dst = OUT / f"host_{i}.png"
    kie_download(r["urls"][0], str(dst))
    return slug, "success", str(dst)


def main():
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(gen, i, slug, p): slug for i, (slug, p) in enumerate(HOSTS, 1)}
        for f in as_completed(futs):
            slug, status, info = f.result()
            print(f"[{slug}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
