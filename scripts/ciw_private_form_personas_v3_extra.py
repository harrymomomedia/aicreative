"""Generate 5 extra realistic CIW private-form persona references."""
import concurrent.futures
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import download, generate_gpt_image

OUT_DIR = Path("outputs/ciw_private_form/personas_v3_extra")
OUT_DIR.mkdir(parents=True, exist_ok=True)

TAIL = (
    " Low-production iPhone front-camera video still, vertical 9:16, chest-up, "
    "slightly imperfect selfie angle, real UGC realism. Uneven skin texture, "
    "visible pores, tired eyes, flyaway hair, dry lips, faint sensor noise, "
    "mixed natural/practical light, no beauty filter, no retouching, no studio "
    "lighting, no polished influencer styling. Serious direct expression, mouth "
    "closed. No text, no captions, no logos, no watermark, no readable documents."
)

PERSONAS = {
    "11_latina_49_night_car": (
        "Fictional Latina woman, age 49, warm olive skin, greying dark hair pulled "
        "back loosely, tired eyes, fine mouth lines, no glam makeup, small hoop "
        "earrings, faded wrist tattoo near a black hoodie sleeve. Sitting in an "
        "older parked car at dusk outside a laundromat, dim dashboard glow and "
        "parking-lot light, ordinary worn car interior, private serious feeling."
        + TAIL
    ),
    "12_black_56_motel_table": (
        "Fictional Black woman, age 56, deep brown skin, short natural hair with "
        "grey at the temples, visible forehead lines, under-eye darkness, small "
        "gold studs, plain faded navy t-shirt. Sitting at a small table in a plain "
        "budget motel or temporary housing room, beige wall, cheap lamp, curtain, "
        "phone on table, grounded reentry feel."
        + TAIL
    ),
    "13_chicana_38_apartment_hall": (
        "Fictional Chicana woman, age 38, light-medium tan skin, dark hair in a "
        "messy bun, thin brows, faint acne scars, small nose stud, old faded floral "
        "collarbone tattoo partly visible above a stretched black tee. Standing in "
        "a narrow apartment hallway near a front door, beige walls, peephole, keys "
        "hanging softly out of focus, quick phone-selfie framing."
        + TAIL
    ),
    "14_afro_latina_44_reentry_office": (
        "Fictional Afro-Latina woman, age 44, medium-brown skin, curly hair tied "
        "back, no makeup, tired kind eyes, slight cheek scar, simple silver hoops. "
        "Wearing a faded olive sweatshirt. Sitting in a small reentry nonprofit "
        "office, folding chair, beige wall, corkboard and pamphlets blurred with "
        "no readable text, one hand near a phone."
        + TAIL
    ),
    "15_native_latina_53_bus_bench": (
        "Fictional Native-Latina woman, age 53, medium tan skin, long dark hair "
        "with grey strands, weathered cheekbones, fine lines around eyes and mouth, "
        "no makeup, small silver earrings, faded brown hoodie. Sitting at an LA bus "
        "bench under overcast light, traffic and storefronts blurred behind, selfie "
        "held close and slightly low, quiet but direct."
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
