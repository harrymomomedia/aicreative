"""Generate persona references for the CIW private-form explainer ad.

Output: outputs/ciw_private_form/personas/<slug>.png
Provider: KIE gpt-image-2 at 2K, 9:16.
"""
import concurrent.futures
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import download, generate_gpt_image

OUT_DIR = Path("outputs/ciw_private_form/personas")
OUT_DIR.mkdir(parents=True, exist_ok=True)

REALISM_TAIL = (
    " Candid iPhone 14 Pro front-camera video still, vertical 9:16, chest-up "
    "portrait, eye-level, real social-media UGC frame. Photographic realism: "
    "visible skin pores, natural under-eye shadows, slight facial asymmetry, "
    "faint sensor noise in shadows, mild handheld softness, natural catchlight, "
    "no beauty filter, no retouching, no studio lighting. Serious, direct, "
    "compassionate expression, mouth closed. No on-screen text, no captions, "
    "no watermark, no logo, no readable documents."
)

PERSONAS = {
    "latina_la_car_46": (
        "Latina woman, age 46, warm olive skin, dark brown hair in a low practical "
        "ponytail with a few flyaway strands, faint freckles across nose and cheeks, "
        "minimal makeup, small silver hoop earrings. Wearing a plain black zip hoodie "
        "over a faded charcoal t-shirt. She is seated in the driver's seat of a parked "
        "older sedan in a Los Angeles strip-mall parking lot, daylight through the "
        "windshield, blurred storefronts and parked cars through the rear window. "
        "She holds a smartphone low near her chest, screen turned slightly away so no "
        "text is readable. Feels like a trusted auntie explaining a private form."
        + REALISM_TAIL
    ),
    "afro_latina_home_39": (
        "Afro-Latina woman, age 39, medium-brown skin, shoulder-length loose curls "
        "pulled back with a simple clip, natural face, small gold studs, faint tired "
        "under-eye shadows. Wearing a muted burgundy long-sleeve top. Sitting at a "
        "small kitchen table in a modest Los Angeles apartment with a laptop and a "
        "phone nearby, warm late-afternoon window light, soft background of blinds, "
        "fridge magnets, and a mug. Feels like a calm community-helper creator."
        + REALISM_TAIL
    ),
    "black_la_commentary_42": (
        "Black woman, age 42, medium-dark skin, neat shoulder-length box braids, clear "
        "square acetate glasses, bare natural makeup, small gold hoops. Wearing a dark "
        "denim jacket over a plain white tee. Seated at a kitchen counter in a modest "
        "South Los Angeles apartment, phone propped at eye level, one hand resting near "
        "a closed notebook. Calm but firm LA commentary energy, not a lawyer, not a "
        "news anchor."
        + REALISM_TAIL
    ),
    "latina_auntie_table_55": (
        "Latina woman, age 55, sun-touched olive skin, salt-and-pepper hair pulled "
        "into a loose low bun, soft jowls, crow's feet, no glam makeup, simple thin "
        "gold hoop earrings. Wearing a faded light-blue chambray shirt over a white "
        "tank top. Sitting at a small round kitchen table with a smartphone and reading "
        "glasses beside her, warm morning light through beige curtains, lived-in "
        "working-class Southern California home. Trustworthy older-sister/auntie feel."
        + REALISM_TAIL
    ),
    "latina_form_demo_hands": (
        "Faceless close-up UGC video still of a Latina woman's hands holding a modern "
        "smartphone over a kitchen table. Warm medium-olive hands with short natural "
        "nails, one simple silver ring, slightly worn knuckles, phone screen angled so "
        "it is glowing but no text is readable. Background: coffee mug, legal-pad edge, "
        "soft morning window light, modest apartment kitchen table. Private form demo "
        "feeling, intimate and safe. Photorealistic iPhone 14 Pro frame, vertical 9:16, "
        "no readable text, no logos, no captions, no watermark."
    ),
    "latina_parking_lot_33": (
        "Latina woman, age 33, light-medium tan skin, dark hair in a claw clip, faint "
        "acne texture and natural pores, no glam makeup, small hoop earrings. Wearing "
        "a plain gray crewneck sweatshirt. Standing outside in a quiet Los Angeles "
        "parking lot near a beige stucco wall, late-afternoon overcast light, blurred "
        "palm tree and parked cars in background. She holds a phone in one hand and "
        "looks into the camera like she is about to explain something practical and "
        "private."
        + REALISM_TAIL
    ),
}


def gen_one(slug: str, prompt: str):
    print(f"[{slug}] start", flush=True)
    result = generate_gpt_image(prompt=prompt, aspect_ratio="9:16", resolution="2K")
    if result.get("status") != "success" or not result.get("urls"):
        print(f"[{slug}] failed: {result.get('failMsg') or result.get('raw')}", flush=True)
        return slug, None
    dest = OUT_DIR / f"{slug}.png"
    download(result["urls"][0], dest)
    print(f"[{slug}] done -> {dest}", flush=True)
    return slug, str(dest)


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(gen_one, slug, prompt): slug for slug, prompt in PERSONAS.items()}
        for future in concurrent.futures.as_completed(futures):
            slug, path = future.result()
            print(f"RESULT {slug}: {path}", flush=True)


if __name__ == "__main__":
    main()
