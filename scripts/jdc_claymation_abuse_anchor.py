"""IL JDC explainer — CLAYMATION ABUSE-ANCHOR shots (Seedance KIE 480p 9:16).

The context b-roll (jdc_claymation_broll.py) reads as generic institutional
sadness. Per the campaign's locked rule, the ad must explicitly be ABOUT
sexual abuse by guards/staff to filter intake. These two shots carry that
beat — using ONLY non-explicit power-imbalance metaphor.

ABSOLUTE GUARDRAILS (ethics + moderation):
  - NEVER the act. NEVER nudity. NEVER a minor in any sexual context.
  - NO bed / bunk / shower / undressing scenes.
  - Figure always clothed. Threat lives ENTIRELY in implication —
    a looming shadow, scale/power imbalance, an unwanted hand on a shoulder.
  - This is the standard survivor-PSA / documentary visual language.

  08 looming_shadow — teen pressed to wall, towering uniformed shadow over them
  09 heavy_hand     — large uniformed hand resting on a tense teen's shoulder

Note: this combo (young figure + uniformed authority + menace) is the most
likely to trip Seedance text moderation. If either 422s/fails, fall back to a
more abstract metaphor (a small wilting object under a large shadow) or route
to another model.

Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLAY = (
    " Handmade claymation stop-motion b-roll, nobody speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "pressed into the soft clay, slightly uneven hand-sculpted surfaces, matte clay "
    "sheen, gentle jerky frame-stepping stop-motion movement, shallow tabletop "
    "miniature depth of field, Aardman Wallace-and-Gromit diorama craft. Muted, "
    "slightly desaturated, melancholic mood. No dialogue, no captions, no subtitles, "
    "no on-screen text, no readable words or signage."
)

SHOTS = {
    "clay_08_looming_shadow": (
        "A cold clay institutional hallway. A small lone clay figure of a teenager "
        "stands pressed back against the cinderblock wall, shoulders hunched, looking "
        "up and afraid. Across the wall and floor stretches the long dark looming "
        "shadow of a tall adult figure in a uniform and peaked cap, standing unseen "
        "just out of frame in the doorway. Only the menacing shadow is shown — no "
        "contact and no action of any kind. A heavy sense of dread, fear, and power "
        "imbalance: a young person made small and unsafe by looming authority. Cold "
        "blue-grey light, deep long shadows." + CLAY
    ),
    "clay_09_heavy_hand": (
        "Close on a small clay figure of a teenager seen from behind, sitting very "
        "still and tense, shoulders rigid. A large heavy adult clay hand in a dark "
        "uniform sleeve reaches in from the side and rests on the young person's "
        "shoulder. The teenager stiffens and goes still. Unsettling, unwanted, wrong "
        "— nothing else is shown, just the heavy hand and the tension. Cold "
        "institutional light, quiet menace, a feeling of violated safety." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (Seedance KIE 480p 9:16 5s)...", flush=True)
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
        futures = {ex.submit(gen, s, p): s for s, p in SHOTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
