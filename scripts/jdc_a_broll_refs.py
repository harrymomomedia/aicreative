"""Generate gpt-image-2 storyboard reference frames for B-roll scenes.

12 reference images, 9:16 portrait (1024x1536), quality=medium for speed.
Each is a candidate first-frame anchor for Veo/Seedance IMAGE_2_VIDEO.

Naming follows V1-V12 from the original B-roll list.
Output: outputs/illinois_jdc_urban_peer/broll_refs/{V#}_{slug}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openai_image import generate_image

OUT_DIR = Path("outputs/illinois_jdc_urban_peer/broll_refs")

COMMON_STYLE = (
    "Photoreal cinematic still, 9:16 vertical portrait composition. "
    "Documentary realism, no stylization, no illustration. "
    "Natural color grading, real-world textures, ordinary camera depth-of-field. "
    "NO on-screen text, NO captions, NO subtitles, NO watermarks, NO logos "
    "(unless the scene explicitly requires on-screen text as part of the subject — then render that text crisp and correct)."
)

PROMPTS = {
    "v1_corridor": (
        "Deep one-point perspective down an empty institutional corridor at night, single flickering "
        "overhead fluorescent fixture, painted concrete-block walls, heavy metal doors lining both sides, "
        "polished checkered linoleum floor catching cold blue-fluorescent reflections. Eerie, lonely, "
        "static low camera angle. " + COMMON_STYLE
    ),
    "v2_cell_door": (
        "Close-up of a heavy painted metal cell door mid-slam, viewed from inside the cell looking out. "
        "Small reinforced glass window with bars, peeling beige paint on door, harsh fluorescent light "
        "spilling through the closing gap, deep shadow inside the cell. Cold institutional palette. "
        "Sense of motion and finality. " + COMMON_STYLE
    ),
    "v3_cafeteria": (
        "Wide documentary shot of 5 to 6 teenage boys in orange jumpsuits standing single-file in a "
        "fluorescent-lit institutional cafeteria line, holding plastic trays, faces turned away or "
        "out of frame (no clear faces visible). Stainless-steel serving counter, beige walls, "
        "polished linoleum floor. Cold blue overhead lighting. " + COMMON_STYLE
    ),
    "v4_mugshot": (
        "Side-profile medium close-up of a teenage boy's face being photographed against a white "
        "height chart with black-and-white horizontal bands and visible numbers. Harsh white camera "
        "flash key light from the front, hard shadow behind. Cold institutional booking room. "
        "Boy faces fully sideways so no direct identifying features visible. " + COMMON_STYLE
    ),
    "v5_case_file": (
        "Top-down close-up of weathered hands flipping through a thick manila case file at a "
        "warm wooden attorney's desk, late-afternoon window light from the right. Crisp visible "
        "page header text reading exactly: 'COOK COUNTY JTDC'. Tabbed manila dividers, legal "
        "stationery. Selective focus on the page header. " + COMMON_STYLE
    ),
    "v6_stamp": (
        "Slow-motion-style frozen moment of a red rubber stamp pressed onto a legal document. "
        "Crisp red stamp text reading exactly: 'APPROVED'. Hand visible holding the stamp. Crisp "
        "white paper, slight ink bleed at the edges. Warm desk-lamp light, dark wood desk. " + COMMON_STYLE
    ),
    "v7_gavel": (
        "Extreme close-up cinematic side-angle of a heavy polished wooden judge's gavel mid-strike "
        "onto a wooden sound block on a courtroom bench. Warm tungsten key light from the right, "
        "dark mahogany background, slight motion blur on the gavel. Cinematic shallow depth-of-field. " + COMMON_STYLE
    ),
    "v8_envelope": (
        "Close-up of weathered hands sliding a sealed white manila envelope across a polished "
        "wooden attorney's desk toward another pair of waiting hands. Warm soft daylight from a "
        "window to the right, leather-bound law books out-of-focus in the background. " + COMMON_STYLE
    ),
    "v9_check": (
        "Top-down extreme close-up of a freshly-printed cashier's check lying face-up on a warm "
        "wooden desk. Visible 'PAY TO THE ORDER OF' line, signature visible at the bottom, dollar "
        "amount intentionally blurred out (just gray smudge in the amount box). Soft side light "
        "from a desk lamp. Cinematic depth-of-field. " + COMMON_STYLE
    ),
    "v10_counting_cash": (
        "Close-up of hands counting out a fanned stack of crisp US one-hundred-dollar bills on a "
        "kitchen table. Daylight from a window on the left side. Polished wood table grain visible, "
        "casual home setting, slight motion in the counting hand. " + COMMON_STYLE
    ),
    "v11_notification": (
        "Static top-down close-up of a modern smartphone lying face-up on a warm wooden desk. The "
        "screen shows a single clean green notification pill containing only a white checkmark icon "
        "and the short text reading EXACTLY: 'You may qualify'. No other text on screen, no app "
        "icons visible, no clock. Soft warm desk-lamp light from upper-left, coffee cup blurred in "
        "the corner. " + COMMON_STYLE
    ),
    "v12_form_submit": (
        "POV close-up of a person's hand holding a smartphone, thumb hovering over a clean bright "
        "green button on the screen. The button text reads EXACTLY: 'SUBMIT'. The screen above the "
        "button shows a simple form with grey placeholder bars (no real text in the form fields). "
        "Crisp button text, slight thumb motion blur. White background behind the phone. " + COMMON_STYLE
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating...", flush=True)
    r = generate_image(
        prompt=prompt,
        out_path=str(out),
        size="1024x1536",
        quality="medium",
        n=1,
    )
    if r["status"] != "success":
        return slug, "failed", r["raw"].get("error", "unknown")
    return slug, "success", r["paths"][0]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
