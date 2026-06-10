"""Create video-safe anchor variants for CIW persona 05.

The picked source has a hand too close to the lens, which can make Veo drift.
These i2i variants preserve the same woman while changing framing so hands are
below frame or far back from the camera.

Output: outputs/ciw_private_form/porchtop_anchor_variants/<slug>.png
"""
import concurrent.futures
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import download, generate_gpt_image, upload_file


SRC = Path("outputs/ciw_private_form/personas_v2/05_latina_58_porchtop.png")
OUT_DIR = Path("outputs/ciw_private_form/porchtop_anchor_variants")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_LOCK = (
    "Use the reference image as the identity source. Same exact fictional Latina woman, "
    "late 50s, olive skin, grey-streaked loose braid, deep crow's feet, soft jowls, "
    "thin lips, no makeup, faded denim overshirt over white tank, same worn realistic "
    "skin texture and serious direct-to-camera expression. Keep her age and ordinary "
    "formerly-incarcerated/community-helper realism. Photoreal iPhone front-camera "
    "UGC still, vertical 9:16, natural Southern California apartment porch daylight, "
    "unretouched pores, wrinkles, under-eye darkness, flyaway hair, slight sensor noise. "
    "No beauty filter, no studio lighting, no captions, no text, no logos, no watermarks. "
)

NEGATIVE_HAND_LOCK = (
    "Critical for video generation: no hand, fingers, phone, or arm close to the lens. "
    "Hands must be completely below the bottom edge of frame or resting far down in her lap, "
    "small and unobtrusive. Nothing should cover the face, mouth, chest, or camera view."
)

VARIANTS = {
    "05a_front_porch_nohands": (
        BASE_LOCK
        + "Change the shot to a clean medium-close talking-head frame from upper chest up. "
        "She sits on the same modest apartment front steps, stucco wall and metal railing softly behind her. "
        "Phone is held steady at eye level, face centered, shoulders relaxed, both hands out of frame. "
        + NEGATIVE_HAND_LOCK
    ),
    "05b_threequarter_railing": (
        BASE_LOCK
        + "Change the shot to a slightly wider 3/4 angle on the porch, camera at eye level. "
        "She is turned a little toward the railing but still looking into the phone lens, upper torso visible, "
        "late-afternoon shade, apartment walkway softly blurred behind. "
        + NEGATIVE_HAND_LOCK
    ),
    "05c_porch_steps_wider": (
        BASE_LOCK
        + "Change the shot to a more stable waist-up porch-step frame, like the phone is propped on a step. "
        "Her elbows and hands are low in her lap and not emphasized; the face remains the focus. "
        "Background: modest stucco apartment exterior, worn step, plain metal railing, no readable signs. "
        + NEGATIVE_HAND_LOCK
    ),
    "05d_doorway_softshade": (
        BASE_LOCK
        + "Change the shot to her standing or seated just inside the apartment doorway near the porch, "
        "soft shade from the open door, simple stucco exterior and doorframe behind her. "
        "Chest-up direct-to-camera frame, calm serious auntie energy, phone at eye height, hands unseen. "
        + NEGATIVE_HAND_LOCK
    ),
}


def gen_one(slug: str, prompt: str, src_url: str):
    out = OUT_DIR / f"{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating", flush=True)
    result = generate_gpt_image(
        prompt=prompt,
        image_urls=[src_url],
        aspect_ratio="9:16",
        resolution="2K",
    )
    if result.get("status") != "success" or not result.get("urls"):
        return slug, "failed", str(result.get("failMsg") or result.get("raw"))
    download(result["urls"][0], out)
    return slug, "success", str(out)


def main():
    if not SRC.exists():
        raise FileNotFoundError(SRC)
    print(f"Uploading source: {SRC}", flush=True)
    src_url = upload_file(str(SRC), "image/png")
    print(f"Source URL: {src_url}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(gen_one, slug, prompt, src_url): slug
            for slug, prompt in VARIANTS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            slug = futures[future]
            try:
                _, status, info = future.result()
                print(f"RESULT {slug}: {status} {info}", flush=True)
            except Exception as exc:
                print(f"RESULT {slug}: exception {exc}", flush=True)


if __name__ == "__main__":
    main()
