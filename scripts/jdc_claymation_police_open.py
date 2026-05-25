"""IL JDC explainer v2 — opening "taken by police" shot (shows the kid's FACE).

Director note: open on a CHARACTER, not the lockup building — a face is more
relatable / scroll-stopping than an establishing shot. Show the kid being
taken by police before he's locked up.

Two angles to pick from (both show the boy's scared face clearly):
  police_street  — boy led along a Chicago street toward a squad car
  police_car     — boy's face at the back-seat window of a police car

Deep-brown-skin boy, Chicago cues (brick, El). KIE (permissive). 480p 9:16 5s.
Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")

CLAY = (
    " Handmade claymation stop-motion b-roll, nobody speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "in the soft clay, hand-sculpted surfaces, matte clay sheen, gentle jerky "
    "frame-stepping stop-motion movement, shallow tabletop miniature depth of field, "
    "Aardman Wallace-and-Gromit diorama craft. Cold, muted, slightly desaturated, "
    "bleak urban mood. No captions, no subtitles, no on-screen text, no readable words."
)

SHOTS = {
    "clay_police_street": (
        "A young deep-brown-skinned boy with short dark hair, in plain street clothes, "
        "is being led along a Chicago street by a uniformed police officer who has a "
        "hand on his shoulder. The boy's frightened young face is turned toward the "
        "camera in three-quarter view, eyes wide and worried, lip tight. A police car "
        "with red and blue lights sits behind them, red-brick buildings and an elevated "
        "train line in the background under a grey overcast sky. We clearly see the "
        "boy's scared, relatable face. Cold urban Chicago tones." + CLAY
    ),
    "clay_police_car": (
        "A young deep-brown-skinned boy with short dark hair sits small in the back "
        "seat of a police car, his frightened young face close to the window looking "
        "out, faint red and blue light reflecting on the glass, a blurred Chicago "
        "street with red-brick buildings outside. We clearly see the boy's scared, "
        "vulnerable face up close. Cold, lonely, urban." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (KIE Seedance Fast 480p 9:16 5s)...", flush=True)
    r = generate_seedance(prompt=prompt, duration=5, aspect_ratio="9:16", generate_audio=False)
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in SHOTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            slug, status, info = f.result()
            print(f"[{slug}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
