"""Generate 4 reference persona portraits in parallel via GPT Image 2."""
import sys, pathlib, concurrent.futures
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download

OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/reference")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PERSONAS = {
    "a_la_sidewalk": (
        "Selfie portrait of a 52-year-old Latina woman, weary expression, eye contact with the camera. "
        "Salt-and-pepper hair pulled back loosely with wisps escaping at her temples, deep forehead lines, "
        "faint under-eye darkness, dry lips, no makeup, slight facial asymmetry, visible pores, sun-touched olive skin. "
        "Distinctive markings: small dark teardrop tattoo under her right eye, large dark script and floral tattoos "
        "covering the full front of her neck and upper chest, visible above the collar of an oversized light-blue chambray "
        "button-up shirt worn open over a white tank top. Large silver hoop earrings. "
        "She stands on a cracked Los Angeles industrial sidewalk against a heavily graffitied dark-brick wall "
        "(faded mural with circular motifs left of frame), with a wide empty industrial street and low-rise warehouses "
        "receding behind her under hazy golden-hour light. "
        "Vertical 9:16 framing, chest-up portrait, handheld phone selfie aesthetic, available light only, "
        "soft natural side-rim from off-camera-left sun, no retouching, no beauty filter. "
        "No on-screen text, no captions, no subtitles."
    ),
    "b_kitchen": (
        "Portrait of a 64-year-old Latina grandmother seated at her own kitchen table, holding a ceramic coffee mug "
        "in both hands, gentle regretful expression, eye contact with the camera. "
        "Fully grey hair in a loose low bun, wire-rim reading glasses pushed slightly up on her nose, soft jowls, "
        "light age spots across her cheekbones, fine vertical lip lines, no makeup, slight facial asymmetry, "
        "visible pores, warm olive skin. No tattoos visible. "
        "She wears a modest knitted cardigan in a muted colour over a pastel pink button-down blouse, "
        "with a small thin gold cross necklace at her collarbone. "
        "Setting: a lived-in working-class Latina home kitchen, warm morning sunlight streaming through faded yellow "
        "curtains behind her, framed family photographs softly out of focus on a wooden sideboard in the background, "
        "tile counter edge visible. "
        "Vertical 9:16 framing, chest-up portrait, handheld phone selfie aesthetic, soft natural window light, "
        "no retouching, no beauty filter. No on-screen text, no captions, no subtitles."
    ),
    "c_car": (
        "Selfie portrait of a 43-year-old Latina woman seated in the driver's seat of a parked car, matter-of-fact "
        "expression, eye contact with the camera. "
        "Dark brown hair in a low practical ponytail with a few flyaway strands, faint under-eye darkness from tiredness, "
        "light freckles across her nose and upper cheekbones, dry lips, no makeup, slight facial asymmetry, visible pores, "
        "warm olive skin. No tattoos visible above the neck or on the arms within frame, except one small simple line "
        "tattoo on the inside of her left wrist. "
        "She wears a plain dark fitted henley t-shirt and small simple silver hoop earrings; a thin work-badge lanyard "
        "is half-visible at her chest. "
        "Setting: interior of a midsize sedan in a strip-mall parking lot, daylight streaming through the windshield "
        "behind her shoulder, blurred storefronts and parked cars visible through the rear side window, faded fabric "
        "headliner above. "
        "Vertical 9:16 framing, chest-up portrait, handheld phone selfie aesthetic, available daylight only, "
        "no retouching, no beauty filter. No on-screen text, no captions, no subtitles."
    ),
    "d_orchard": (
        "Portrait of a 56-year-old Latina woman standing on a dirt-and-gravel farm road at the edge of a Central Valley "
        "California orange grove, plain grounded expression, eye contact with the camera. "
        "Hair in a practical low braid, sun-weathered skin with reddened cheekbones, deep crow's feet, faint forehead lines, "
        "fine vertical lip lines, dry lips, no makeup, slight facial asymmetry, visible pores, suntanned olive skin. "
        "Light faded older forearm tattoos only, work-worn and abstract, not gang-coded, visible on the inside of her "
        "right forearm where her sleeve is rolled up. No face or neck tattoos. "
        "She wears a faded denim work shirt with the sleeves rolled to her elbows over a white tank top, "
        "simple small silver hoop earrings. "
        "Setting: agricultural Central Valley landscape, dense rows of orange trees with green leaves and orange fruit "
        "receding behind her, chain-link fence and a section of black PVC irrigation pipe visible to one side, "
        "flat horizon under bright slightly hazy mid-afternoon natural light. "
        "Vertical 9:16 framing, chest-up portrait, handheld phone selfie aesthetic, harsh natural daylight, "
        "no retouching, no beauty filter. No on-screen text, no captions, no subtitles."
    ),
}


def gen_one(slug, prompt):
    print(f"[{slug}] start", flush=True)
    res = generate_gpt_image(prompt, aspect_ratio="9:16", resolution="2K")
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{slug}] FAILED: {res.get('raw')}", flush=True)
        return slug, None
    url = res["urls"][0]
    dest = OUT_DIR / f"character_{slug}.png"
    download(url, dest)
    print(f"[{slug}] DONE → {dest}", flush=True)
    return slug, str(dest)


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen_one, slug, prompt): slug for slug, prompt in PERSONAS.items()}
        for fut in concurrent.futures.as_completed(futs):
            slug, path = fut.result()
            print(f"-> {slug}: {path}")


if __name__ == "__main__":
    main()
