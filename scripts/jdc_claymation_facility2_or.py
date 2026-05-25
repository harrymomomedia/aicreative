"""IL JDC explainer — CLAYMATION faceless EXPANSION (OpenRouter Seedance 480p).

Additional faceless prison/institutional b-roll to round out the library and
give cutting variety. ALL faceless (environment / detail / hands only) — no
identifiable faces — so the cheaper OpenRouter route loses nothing (text-to-
video, no identity to lock). ~$0.05/clip vs KIE's ~$0.35.

  p7  hands_bars        — small clay hands gripping steel cell bars
  p8  lights_out        — dark cellblock at night, dim red emergency light
  p9  clock_wall        — institutional clock on a cracked wall (time passing)
  p10 tray_slot         — food-tray slot in a steel door, tray pushed through
  p11 barred_window_rain— high barred window, rain streaks, cold grey light
  p12 bars_shadow_floor — bar-shadows creeping across a bare cell floor
  p13 intake_bench      — empty holding bench, folded uniform clothes
  p14 gate_closing      — heavy barred gate slowly rolling shut

Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openrouter_video import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLAY = (
    " Handmade claymation stop-motion b-roll, no people speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "in the soft clay, hand-sculpted surfaces, matte clay sheen, gentle jerky "
    "frame-stepping stop-motion movement, shallow tabletop miniature depth of field, "
    "Aardman Wallace-and-Gromit diorama craft. Cold, muted, slightly desaturated, "
    "bleak institutional mood. No dialogue, no captions, no subtitles, no on-screen "
    "text, no readable words or signage."
)

SHOTS = {
    "clay_p7_hands_bars": (
        "Close-up of two small clay hands gripping a set of thick cold steel cell "
        "bars from the inside, knuckles tight and pale, fingers wrapped around the "
        "bars. Cold pale light spills through from beyond the bars. Only the hands "
        "and the bars are shown, no face. Quiet desperation and confinement. Slow "
        "subtle push-in." + CLAY
    ),
    "clay_p8_lights_out": (
        "A dark clay cellblock tier at night with the lights out: long rows of black "
        "shuttered cell doors fading into shadow, a single dim red emergency light "
        "glowing low on the wall, faint cold moonlight from a high window. Deep "
        "blackness, heavy silence, dread. A very slow creeping dolly forward." + CLAY
    ),
    "clay_p9_clock_wall": (
        "A plain round institutional clay clock mounted high on a cracked and "
        "water-stained painted cinderblock wall, its simple hands ticking, cold flat "
        "light across the wall. The endless slow passage of time, years lost. Slow "
        "steady push-in toward the clock." + CLAY
    ),
    "clay_p10_tray_slot": (
        "A heavy grey steel clay cell door with a horizontal hinged food-tray slot in "
        "the middle. A clay food tray is slowly pushed through the slot from outside "
        "by an unseen hand. Only the door, slot and tray are shown, no face. Cold "
        "corridor light, institutional, impersonal." + CLAY
    ),
    "clay_p11_barred_window_rain": (
        "A small high window crossed with steel bars set in a bare clay cell wall, "
        "cold grey rain streaking down the glass beyond the bars, weak overcast "
        "daylight seeping in. Empty, lonely, melancholic. Slow gentle push-in toward "
        "the rain-streaked barred window." + CLAY
    ),
    "clay_p12_bars_shadow_floor": (
        "Looking down at a bare scuffed clay cell floor as the hard striped shadow of "
        "vertical window bars slowly creeps and stretches across the floor with the "
        "shifting light, marking the slow passage of a long day. Empty, still, "
        "lonely. No people. Cold light slowly warming then fading." + CLAY
    ),
    "clay_p13_intake_bench": (
        "An empty institutional intake holding area: a long bare bench bolted to a "
        "cold tiled wall, a single neatly folded set of plain grey uniform clothes "
        "resting on the bench, harsh flat overhead light, scuffed floor. Empty, "
        "impersonal, processing. Slow static-feeling slow push-in." + CLAY
    ),
    "clay_p14_gate_closing": (
        "A heavy barred steel sliding gate at the end of a cold clay corridor slowly "
        "rolling shut, the thick bars sliding across the frame to seal the passage, "
        "cold pale light beyond. The feeling of being closed in and locked away. No "
        "people. Slow deliberate movement of the gate." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (OpenRouter Seedance 480p 9:16 5s)...", flush=True)
    try:
        r = generate_seedance(
            prompt=prompt,
            duration=5,
            resolution="480p",
            aspect_ratio="9:16",
            audio=False,
        )
    except Exception as e:
        return slug, "failed", f"EXC {e}"[:400]
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
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
