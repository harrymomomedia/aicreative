"""Two quick STYLE TESTS via Seedance 2 Fast on KIE (480p, 9:16, no dialogue).

Generic/neutral subjects — the point is to see how each aesthetic renders,
not to carry a script. Two separate clips:

  analog_grunge  — 1990s VHS camcorder tape-degradation look
  claymation     — handmade clay stop-motion b-roll (no people speaking)

Seedance style is prompt-driven (no preset param). 480p is hardcoded in
kie_client.generate_seedance. Text-to-video (no anchor) → fuller descriptive
prompts (~100-260 words per the Seedance prompt rule).

Output: outputs/style_tests/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/style_tests")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANALOG_GRUNGE = (
    "Vintage early-1990s VHS camcorder footage aesthetic. A young man in a plain "
    "grey hoodie walks slowly down an empty urban side street at dusk, hands in his "
    "pockets, head slightly down, passing a weathered brick wall and a flickering "
    "streetlight. Heavy analog-grunge degradation: visible horizontal tracking lines "
    "and magnetic tape distortion, soft chromatic-aberration color fringing on edges, "
    "rolling scanline jitter, dense video grain and noise, blown-out highlights and "
    "crushed muddy shadows, faded washed-out colors with a sickly green-and-magenta "
    "tint, slight tape warble and image wobble. Handheld home-camcorder feel, slightly "
    "soft focus, low resolution, smeary motion trails behind movement. A small glowing "
    "retro camcorder timecode and date-stamp sits in the lower corner. Moody, lonely, "
    "lo-fi, degraded, nostalgic. No captions, no subtitles, no modern graphics."
)

CLAYMATION = (
    "Handmade claymation stop-motion b-roll, nobody speaking. A small plasticine clay "
    "figure of a person sits alone on a tiny clay bench in a miniature handcrafted clay "
    "city block at dusk: little clay buildings, a small clay streetlamp glowing warm, "
    "textured clay sidewalk. Charming tactile stop-motion craft: visible thumbprints "
    "and fingerprint dents pressed into the soft modeling clay, slightly uneven sculpted "
    "surfaces, matte clay sheen, gentle jerky frame-stepping stop-motion movement, "
    "shallow tabletop miniature depth of field, warm soft practical lighting. The clay "
    "figure breathes and shifts slightly, looks down at the ground, then slowly lifts "
    "its head. Cozy, handcrafted, slightly melancholic Aardman Wallace-and-Gromit "
    "diorama feel. No dialogue, no captions, no subtitles, no on-screen text."
)

CLIPS = [
    ("analog_grunge", ANALOG_GRUNGE),
    ("claymation",    CLAYMATION),
]


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (Seedance 2 Fast, KIE, 480p 9:16, 5s)...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=5,
        aspect_ratio="9:16",
        generate_audio=False,
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in CLIPS}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
