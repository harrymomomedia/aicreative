"""Generate 8 IL JDC mistreatment B-roll clips via OpenRouter Seedance 2.0 Fast.

Text-to-video only (no reference images → OpenRouter privacy filter doesn't trigger).
480p 9:16, 5s each, no audio (B-roll inserts).

Beats: implied institutional control / mistreatment — no explicit violence,
no graphic abuse — just heavy emotional cues that read as "the system" did
something wrong. Camera and framing do the work; faces stay off or away.

Cost: ~$0.27/clip × 8 = ~$2.16 total.

Outputs: outputs/illinois_jdc_urban_peer/broll_mt_{slug}.mp4
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

COMMON = (
    "Photoreal documentary cinematography, handheld feel, natural color grading, "
    "no stylization. Cold institutional palette — fluorescent overhead lighting with "
    "blue-grey cast. Real-world textures, peeling paint, scuffed walls, polished checkered "
    "linoleum floor. ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks."
)

PROMPTS = {
    "mt1_door_slam": (
        "Wide low-angle medium shot of a uniformed adult guard's back as he pushes a teenage "
        "boy in an orange jumpsuit (back to camera, no face visible) into a small holding cell, "
        "then slams the heavy metal door shut. Cold fluorescent corridor outside, dim cell "
        "interior beyond. The door slam impacts at the end of the clip. " + COMMON
    ),
    "mt2_solitary_bunk": (
        "Slow static medium shot of a teenage boy in an orange jumpsuit (back to camera, head "
        "bowed) sitting alone on a metal bunk in a small concrete-block solitary cell. Single "
        "small barred window high on the wall casting one thin bar of daylight on the opposite "
        "wall. Stillness. He does not move. " + COMMON
    ),
    "mt3_shadow_looming": (
        "Static low-angle wide shot of a long fluorescent-lit corridor. A teenage boy in an "
        "orange jumpsuit stands against the cinderblock wall on the left, head down. A much "
        "larger adult guard's shadow stretches across the floor toward him from the right edge "
        "of frame (guard himself off-screen). Tension. No actual contact. " + COMMON
    ),
    "mt4_cuffed_bench": (
        "Static medium close-up of a teenager's hands cuffed with steel handcuffs to a metal "
        "bracket on an institutional bench. The teen sits beyond the cuffs, body partially "
        "visible, face out of frame above the top edge. Orange jumpsuit. Cold fluorescent "
        "intake-room light, beige wall behind, faint security camera in upper corner of frame. " + COMMON
    ),
    "mt5_cell_pov": (
        "POV from inside a small solitary cell looking out through the small reinforced glass "
        "and bars in the heavy metal cell door. Outside the cell: a uniformed adult guard "
        "stands directly across the corridor, back to the door, baton on his belt visible. "
        "Cold fluorescent corridor lighting beyond the door. The guard does not move. " + COMMON
    ),
    "mt6_empty_cafeteria": (
        "Wide static shot of a long empty institutional cafeteria with rows of stainless-steel "
        "tables and bolted-down benches. One single teenage boy in an orange jumpsuit (back to "
        "camera) sits alone at the far end, head down over an untouched plastic tray. "
        "Industrial overhead fluorescents, polished floor reflecting the cold light. " + COMMON
    ),
    "mt7_guard_boots": (
        "Static low-angle ground-level shot of the polished checkered linoleum floor of a long "
        "institutional corridor. A uniformed adult guard's heavy black boots and the lower half "
        "of his dark-navy uniform pants walk slowly toward the camera. The boots are the focus. "
        "Cold fluorescent ceiling reflections on the floor. Slight slow motion. " + COMMON
    ),
    "mt8_tally_marks": (
        "Extreme close-up of a section of peeling beige concrete-block wall inside a cell. "
        "Rows and rows of scratched tally marks have been carved into the painted surface — "
        "hundreds of them, organized in groups of five, accumulating across the wall. Faint "
        "dim daylight from off-camera. Slow subtle push-in. " + COMMON
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"broll_mt_{slug}.mp4"
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
        return slug, "failed", str(r.get("raw"))[:300]
    # OpenRouter URLs need auth header to download
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
