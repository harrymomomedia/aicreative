"""Generate 6 IL JDC physical-abuse-suggestive B-roll clips via OpenRouter Seedance 2.0 Fast.

Documentary observational style — hallway scenes. Implied physical abuse via grip,
posture, framing, and aftermath — NOT explicit violence (would fail moderation).
Camera reads as handheld news/documentary footage.

Cost: ~$0.27/clip × 6 = ~$1.62 total.
Outputs: outputs/illinois_jdc_urban_peer/broll_pa_{slug}.mp4
"""
import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openrouter_client import generate_video

OUT_DIR = Path("outputs/illinois_jdc_urban_peer")
KEY = os.getenv("OPENROUTER_API_KEY") or open(".env").read().split("OPENROUTER_API_KEY=")[1].split("\n")[0]

DOC_STYLE = (
    "Documentary observational cinematography, handheld camera shake, slightly off-axis framing, "
    "natural color grading like real news footage from the early 2000s. Cold institutional palette — "
    "blue-grey fluorescent overhead lighting. Real-world textures: scuffed cinderblock walls, "
    "polished checkered linoleum floor catching reflections, painted metal doors. "
    "Photoreal, no stylization, no illustration. "
    "ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks, no logos."
)

PROMPTS = {
    "pa1_pin_against_wall": (
        "Documentary handheld wide-medium shot down a long institutional corridor. An adult uniformed "
        "guard has a teenage boy in an orange jumpsuit pressed face-forward against the cinderblock "
        "wall on the right side. Guard's back to the camera, both hands on the teen's shoulders "
        "holding him against the wall. Teen's hands flat on the wall. No actual strikes, just held in "
        "place. Static moment, slight camera handheld sway. " + DOC_STYLE
    ),
    "pa2_collar_grip_escort": (
        "Documentary handheld medium-wide tracking shot following from behind as a uniformed adult "
        "guard walks fast down a long fluorescent corridor, gripping the back of a teenage boy's "
        "orange jumpsuit collar firmly with one hand, propelling him forward. Teen's back to camera, "
        "head slightly lowered. Camera follows ~3 meters behind. " + DOC_STYLE
    ),
    "pa3_two_guard_escort": (
        "Documentary handheld wide hallway shot, slight low angle. Two uniformed adult guards walk "
        "down a long fluorescent corridor toward the camera, each holding one of a teenage boy's "
        "upper arms tightly. Teen is in an orange jumpsuit between them, head down, walking fast to "
        "keep up. All three figures in deep one-point perspective. " + DOC_STYLE
    ),
    "pa4_aftermath_floor": (
        "Documentary handheld wide static shot looking down a long empty institutional corridor at "
        "dusk. At the far end of the corridor, a single teenage boy in an orange jumpsuit sits on "
        "the floor with his back against the cinderblock wall, knees pulled to his chest, head down "
        "and hidden in his arms. Cold fluorescent overhead light on him. No one else in frame. "
        "Stillness, after-the-fact. " + DOC_STYLE
    ),
    "pa5_shadow_looming": (
        "Documentary handheld medium shot in an institutional corridor. A teenage boy in an orange "
        "jumpsuit stands flat against the right cinderblock wall, facing forward, hands at sides, "
        "shoulders tense. A large adult guard's full silhouette (just the dark shadow cast on the "
        "wall and floor) looms over him from the left edge of frame — the guard himself just "
        "out-of-frame on the left. Cold fluorescent light. " + DOC_STYLE
    ),
    "pa6_hallway_witness": (
        "Documentary handheld wide shot of a long institutional corridor. In the immediate "
        "foreground, two uniformed adult guards stand with their backs to the camera, having a "
        "quiet conversation, baton and handcuffs visible on their belts. At the far end of the "
        "corridor, a single teenage boy in an orange jumpsuit sits hunched on a wooden bench against "
        "the wall, alone, distant, small. " + DOC_STYLE
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"broll_pa_{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] submitting...", flush=True)
    r = generate_video(
        prompt=prompt,
        model="bytedance/seedance-2.0-fast",
        aspect_ratio="9:16",
        resolution="480p",
        duration=5,
        generate_audio=False,
    )
    if r["status"] != "success" or not r["urls"]:
        return slug, "failed", str(r.get("raw"))[:400]
    r2 = requests.get(r["urls"][0], stream=True, headers={"Authorization": f"Bearer {KEY}"})
    r2.raise_for_status()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        for chunk in r2.iter_content(1 << 16):
            f.write(chunk)
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in PROMPTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                _, status, info = f.result()
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
