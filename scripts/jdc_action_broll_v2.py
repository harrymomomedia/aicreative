"""IL JDC action b-rolls v2 (clips 4-6) via OpenRouter Seedance 2.0 (NON-fast / quality).

Three high-action JDC scenes — text-to-video, no reference image. Black teen persona.
  4. solitary_slam      — guard slams cell door on lone teen
  5. cell_shakedown     — guards toss belongings during search
  6. intake_processing  — teen receives jumpsuit at intake counter

Specs: 720p / 9:16 / 8s / t2v / audio on.
Model: bytedance/seedance-2.0 (quality tier, NOT fast). 720p minimum.
Cost: pay-per-use, costlier than fast tier (no flat quote — check OpenRouter dashboard).
Outputs: outputs/illinois_jdc_action_broll/broll_{slug}_q.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openrouter_video import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_action_broll")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPTS = {
    "solitary_slam": (
        "Cinematic medium shot inside a small concrete solitary confinement cell from the perspective "
        "of just outside the doorway. A Black teenage boy in an orange jumpsuit sits hunched on a thin "
        "mattress on the floor, knees pulled to his chest, head down. A uniformed adult guard's "
        "silhouette fills the doorway, backlit by the harsh fluorescent corridor light spilling in. "
        "The guard grips the heavy painted metal door and SLAMS it shut with force — the door swings "
        "fast across frame, the cell plunges into near darkness with only a thin strip of light under "
        "the door remaining. Camera holds steady on a tripod, no movement. Cold blue-grey light from "
        "the corridor cuts to a dim greenish-amber from a single recessed cell bulb after the slam. "
        "35mm cinematic look, real-world lighting, desaturated naturalistic palette, subtle film grain. "
        "Documentary drama realism — like a scene from 'Short Term 12' or 'The Wire'. Atmosphere: "
        "suffocating, isolating, final. ABSOLUTELY NO on-screen text, NO captions, NO watermarks."
    ),
    "cell_shakedown": (
        "Cinematic handheld wide shot inside a juvenile detention cell. 2 uniformed adult guards "
        "conduct a fast aggressive shakedown — first guard yanks the thin mattress off the metal bunk "
        "and flips it against the wall, second guard pulls a plastic storage bin from under the bunk "
        "and dumps the contents across the floor: socks, paperback books, a worn family photo, "
        "toothbrush, folded letters scattering. Both guards move with practiced speed and zero care, "
        "hands moving fast. A Black teenage boy in orange stands pressed against the far wall with his hands "
        "behind his head, watching silently. Camera handheld with natural shake, tracks slowly across "
        "the chaos at chest height. Cold fluorescent overhead light, painted cinderblock walls, "
        "polished concrete floor. 35mm cinematic look, desaturated palette, motion blur on the guards' "
        "arms, subtle grain. Documentary drama realism — gritty prestige cable atmosphere. Sounds of "
        "dumped contents hitting the floor, boots, breathing implied. "
        "ABSOLUTELY NO on-screen text, NO captions, NO watermarks."
    ),
    "intake_processing": (
        "Cinematic medium shot in a stark fluorescent-lit intake processing room. A Black teenage boy stands "
        "facing the camera in a folded orange jumpsuit held in his arms, barefoot on cold concrete, "
        "shoulders slumped, eyes down. A uniformed adult female guard stands beside him holding a "
        "clipboard, mouth moving as she reads instructions in a flat institutional monotone. A second "
        "uniformed adult guard behind a steel counter slides a pair of canvas slip-on shoes and a "
        "bedroll across to him without looking up. The boy stares at the floor, holding the jumpsuit "
        "like it weighs a hundred pounds. Camera slowly pushes in on a dolly at a steady creep — from "
        "medium-wide to medium-close on the boy's face. Cold blue-white fluorescent overhead, painted "
        "cinderblock walls, a faded eagle-and-shield state seal on the wall behind the counter. "
        "35mm cinematic look, real-world lighting, desaturated naturalistic palette, subtle film grain. "
        "Documentary drama realism — like the intake scene from 'Boys State' or 'When They See Us'. "
        "Atmosphere: dehumanizing, processed, alone. "
        "ABSOLUTELY NO on-screen text, NO captions, NO watermarks."
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"broll_{slug}_q.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] submitting...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=8,
        resolution="720p",
        aspect_ratio="9:16",
        audio=True,
        model="bytedance/seedance-2.0",
    )
    if r["status"] != "success" or not r["urls"]:
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=3) as ex:
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
