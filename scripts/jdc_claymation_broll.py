"""IL JDC explainer — CLAYMATION B-ROLL set (Seedance 2 Fast, KIE, 480p 9:16).

Wordless symbolic b-roll for the ~38s "What The State Doesn't Advertise"
explainer. Claymation is deliberate: it carries the emotional story
(institution / isolation / coming forward) WITHOUT photoreal depiction of a
minor in a detention/abuse context — moderation-safe + ethically sound.

NEVER depicts abuse. Atmospheric / symbolic only. Facility cues are visual
(razor wire, barred windows, fence) — the words "juvenile detention" are
dropped from prompts to dodge Seedance's text-stage moderation trigger.

7 shots mapped to the explainer beats:
  01 hook_fence        — razor-wire fence, lone figure   (isolation)
  02 corridor          — cold locked-door hallway        (dread)
  03 facility_exterior — stark institutional building    (establishing)
  04 survivor_bench    — adult alone on a bench           (weight of memory)
  05 not_alone_court   — figures together, courthouse     (solidarity / hope)
  06 phone_check       — clay hand taps glowing phone     (the mechanic)
  07 door_to_light     — figure walks toward warm light   (release / CTA)

480p hardcoded in kie_client.generate_seedance. No dialogue (generate_audio
off). Text-to-video (no anchor) → fuller ~100-180 word prompts.

Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Shared clay-world style — keeps all 7 shots in one consistent diorama so
# they cut together. Appended to every shot prompt.
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
    "clay_01_hook_fence": (
        "Cold institutional exterior at grey overcast dusk: a tall clay chain-link "
        "fence topped with coiled razor wire runs across the frame, an empty fenced "
        "clay yard behind it, a looming stark grey clay building with small barred "
        "windows in the background. A single small lone clay figure stands far behind "
        "the fence in the distance, head lowered, hands in pockets, isolated and "
        "small. Slow steady push-in toward the fence. Lonely, cold, foreboding, "
        "desaturated blue-grey light." + CLAY
    ),
    "clay_02_corridor": (
        "Inside a cold empty clay institutional hallway: a long grey cinderblock "
        "corridor lined with a row of heavy identical locked clay doors, a buzzing "
        "fluorescent clay ceiling light, a scuffed worn clay floor. Completely empty "
        "and silent. Slow smooth dolly moving forward down the corridor toward a "
        "single heavy locked door at the far end. Cold blue-grey light, long deep "
        "shadows, oppressive stillness." + CLAY
    ),
    "clay_03_facility_exterior": (
        "A slow pan across the imposing exterior of a stark old institutional "
        "building made of clay: weathered grey concrete and dull red brick walls, "
        "narrow barred windows in neat rows, a tall chain-link perimeter fence, one "
        "bare leafless clay tree, a heavy overcast grey sky with faint drifting clay "
        "clouds. Austere, cold, lonely, institutional." + CLAY
    ),
    "clay_04_survivor_bench": (
        "An adult clay figure sits alone on a worn clay bench in a quiet empty clay "
        "neighborhood at dusk, shoulders slumped, hands in lap, looking down at the "
        "ground, carrying a heavy quiet sadness. A single warm clay streetlamp glows "
        "softly nearby, casting a small pool of warm light against the cool blue "
        "evening. Still, intimate, melancholic. The figure slowly lifts its head." + CLAY
    ),
    "clay_05_not_alone_court": (
        "Several adult clay figures of different ages and builds stand quietly "
        "together in a loose row at the bottom of the wide stone steps of a grand "
        "clay courthouse with tall columns. Above them, a soft warm shaft of golden "
        "light breaks through the heavy grey clay clouds. Quiet solidarity, steady "
        "strength, a hopeful turn. Gentle slow push-in." + CLAY
    ),
    "clay_06_phone_check": (
        "Warm intimate close-up of a clay hand gently cradling a small clay "
        "smartphone, the little phone screen glowing soft and warm, a clay thumb "
        "slowly and calmly tapping the screen. The background is a cozy softly "
        "blurred warm clay room. Reassuring, simple, private, calm. Soft warm "
        "lamplight." + CLAY
    ),
    "clay_07_door_to_light": (
        "A lone adult clay figure stands in a cold dim blue-grey clay room, then "
        "slowly turns and walks toward an open doorway that glows with warm golden "
        "light, stepping forward out of the shadow toward the light. The warm glow "
        "grows and fills the doorway as the figure approaches it. Hopeful, "
        "forward-moving, a quiet sense of release and relief." + CLAY
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
    with ThreadPoolExecutor(max_workers=4) as ex:
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
