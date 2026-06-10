"""Generate more grounded CIW private-form personas.

These are fictional reentry/community-helper style references: lived-in faces,
plain clothes, modest environments, and imperfect phone-camera realism.

Output: outputs/ciw_private_form/personas_v2/<slug>.png
"""
import concurrent.futures
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import download, generate_gpt_image

OUT_DIR = Path("outputs/ciw_private_form/personas_v2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TAIL = (
    " Candid low-production iPhone front-camera video still, vertical 9:16, "
    "chest-up frame, slightly imperfect angle, real social-media UGC not a "
    "professional portrait. Unretouched photographic realism: uneven skin tone, "
    "visible pores, natural wrinkles, under-eye darkness, flyaway hair, dry lips, "
    "slight facial asymmetry, faint sensor noise, mixed household/car daylight, "
    "no beauty filter, no smooth skin, no glam makeup, no studio light. Serious "
    "direct-to-camera expression, mouth closed. No text, no captions, no logos, "
    "no watermarks, no readable documents."
)

PERSONAS = {
    "01_latina_50_car_tattoos": (
        "Fictional Latina woman, age 50, warm olive skin, salt-and-pepper dark hair "
        "pulled into a messy low bun, tired eyes, crow's feet, faint acne scars, "
        "small hoop earrings, old faded script tattoo partly visible at the upper "
        "chest and a small faded wrist tattoo, not gang-coded. Wearing a black "
        "zip hoodie over a faded grey t-shirt. Sitting in the passenger seat of "
        "an older compact car in a laundromat parking lot, overcast Los Angeles "
        "daylight, worn fabric headliner, clutter-free but ordinary."
        + TAIL
    ),
    "02_black_48_kitchen_table": (
        "Fictional Black woman, age 48, medium-dark skin, shoulder-length box braids "
        "grown out slightly at the roots, clear square glasses, natural face, faint "
        "neck crease, tired but steady eyes. Small gold hoops, plain dark crewneck. "
        "A small faded forearm tattoo is barely visible near the sleeve. Sitting at "
        "a small kitchen table in a modest South Los Angeles apartment, old mug, "
        "phone and notebook nearby, mixed window and ceiling light."
        + TAIL
    ),
    "03_chicana_43_stucco_wall": (
        "Fictional Chicana woman, age 43, light-medium tan skin, dark hair in a claw "
        "clip with loose strands, thin eyebrows, faint sun spots, no glam makeup, "
        "small nose stud, simple hoop earrings. One faded floral tattoo peeks from "
        "the collarbone above a stretched black t-shirt. Standing outside against "
        "a beige stucco apartment wall, parking lot and palm tree blurred behind, "
        "flat grey LA afternoon light."
        + TAIL
    ),
    "04_afro_latina_36_bathroom_mirror": (
        "Fictional Afro-Latina woman, age 36, medium-brown skin, hair wrapped in a "
        "plain black scarf, small hoop earrings, bare face with under-eye shadows "
        "and real skin texture. Wearing a faded burgundy thermal shirt. Shot like "
        "a front-camera clip in a modest apartment bathroom doorway with warm bulb "
        "light, tiled wall softly visible behind, intimate and unpolished."
        + TAIL
    ),
    "05_latina_58_porchtop": (
        "Fictional Latina woman, age 58, olive skin, grey-streaked hair in a loose "
        "braid, deep crow's feet, soft jowls, thin lips, no makeup. Wearing a faded "
        "denim overshirt over a white tank. Small old rose tattoo on one forearm, "
        "worn and faded. Sitting on the front steps of a modest Southern California "
        "apartment building, stucco wall, metal railing, late afternoon shade."
        + TAIL
    ),
    "06_black_34_reentry_center": (
        "Fictional Black woman, age 34, dark brown skin, natural hair pulled into a "
        "simple low puff, no makeup, tired eyes, faint cheek scar, small studs. "
        "Wearing a plain grey sweatshirt. Sitting in a modest community-center room "
        "with beige walls, folding chair, corkboard blurred behind, phone propped "
        "close. Feels like a formerly incarcerated woman now helping others check a "
        "private form, grounded and real."
        + TAIL
    ),
    "07_latina_45_bus_stop": (
        "Fictional Latina woman, age 45, medium olive skin, long dark hair tied back, "
        "weathered face, no glam makeup, small silver hoops, faint small tattoo near "
        "the wrist. Wearing a black puffer vest over a faded hoodie. Standing near "
        "a Los Angeles bus stop under overcast light, storefronts and traffic blurred "
        "behind, selfie held slightly low like a quick real clip."
        + TAIL
    ),
    "08_black_latina_52_window": (
        "Fictional Black Latina woman, age 52, medium-brown skin, short natural curls "
        "with grey at the temples, clear tired eyes, slight smile gone serious, no "
        "makeup, old thin gold chain, faded collarbone tattoo mostly hidden by a "
        "dark v-neck t-shirt. Sitting beside a window in a small apartment, blinds "
        "casting soft uneven lines, laundry basket blurred behind."
        + TAIL
    ),
    "09_latina_39_phone_form": (
        "Fictional Latina woman, age 39, light-medium tan skin, tired but focused "
        "eyes, dark hair in a practical ponytail, small acne marks, no glam makeup, "
        "plain black hoodie. Seated at a kitchen counter holding a smartphone just "
        "below frame, glancing directly into the camera as if explaining a private "
        "online eligibility form. Background: modest rental kitchen, sink, dish towel, "
        "daylight from one side."
        + TAIL
    ),
    "10_native_latina_47_motel_room": (
        "Fictional Native-Latina woman, age 47, medium tan skin, long dark hair with "
        "grey strands worn loose, strong cheekbones, sun-weathered skin, faint lines "
        "around mouth, no makeup, small silver earrings. Wearing a faded brown hoodie. "
        "Sitting on the edge of a bed in a plain budget motel-style room or temporary "
        "housing room, beige wall, curtain, small lamp, very ordinary low-income "
        "setting, direct and serious."
        + TAIL
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
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(gen_one, slug, prompt): slug for slug, prompt in PERSONAS.items()}
        for future in concurrent.futures.as_completed(futures):
            slug, path = future.result()
            print(f"RESULT {slug}: {path}", flush=True)


if __name__ == "__main__":
    main()
