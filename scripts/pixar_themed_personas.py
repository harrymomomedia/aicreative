"""Generate 10 themed Pixar-style Latina personas (5 living room, 5 kitchen) via OpenAI gpt-image-2 t2i.

Theme: Latina women's prison survivors (Chowchilla / California women's prisons).
Tone: weary, composed, contemplative — the look of someone considering speaking up about
something heavy from her past.

Style: Pixar 3D character composited onto photorealistic real-world background.
Output: outputs/1777697550119-gyvk6m8/reference_pixar_themed/
"""
import os
import base64
import concurrent.futures
import pathlib
import time

import requests
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("OPENAI_API_KEY")
if not KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")

OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/reference_pixar_themed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_STEM = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic. "
    "The PERSON is rendered in Pixar/Disney 3D animated character style — large expressive "
    "eyes with cartoon highlights, soft stylized facial features, smooth shaded 3D skin, "
    "slightly enlarged head proportions in Pixar's signature character design, painterly "
    "hair texture, vivid clean color. The BACKGROUND is a fully photorealistic real-world "
    "photograph with all real-world lighting, textures, depth, and photographic detail. "
    "Final image is a hybrid composite: a real photograph with a Pixar 3D animated character "
    "composited into the scene. "
    "Expression: quiet, weary, composed — eyes direct to the camera, soft neutral mouth, the "
    "look of a Latina woman in her own home considering speaking up about something heavy "
    "from her past. NOT smiling, NOT crying — just present and contemplative. "
    "No on-screen text, no captions, no subtitles."
)

PERSONAS = {
    # ─── LIVING ROOMS ────────────────────────────────────────────────────────
    "living_01_grandma_religious": (
        "Subject: 68-year-old Latina grandmother, fully grey hair in a low loose bun, "
        "wire-rim reading glasses pushed slightly up on her nose, gentle wrinkles around "
        "the eyes and mouth, soft jowls, light age spots across cheekbones, warm olive skin, "
        "no tattoos, small thin gold cross necklace at collarbone, simple pearl stud earrings. "
        "Wears a long maroon shawl-cardigan over a lavender housedress. "
        "Background: warm-toned 1980s working-class Latina living room, terracotta-painted wall, "
        "framed wooden crucifix and a tall lit Virgen de Guadalupe prayer candle on a small "
        "side table, photo wall behind her cluttered with grad portraits and a wedding photo, "
        "plastic-covered floral-print sofa visible at the edge of frame, lace doily on the side "
        "table, soft warm afternoon light through sheer curtains."
    ),
    "living_02_50s_telenovela": (
        "Subject: 52-year-old Latina woman, dark brown hair shot through with prominent grey "
        "streaks, pulled back into a thick low ponytail with strands escaping at the temples, "
        "faint under-eye shadows, soft crow's feet, penciled chola-style thin eyebrows, simple "
        "silver hoop earrings, no necklace, small chin scar, warm tan skin, no visible face "
        "tattoos. Wears a faded navy zip-up sweatshirt halfway zipped over a plain white tank top. "
        "Background: cramped East Los Angeles apartment living room, wood-paneled accent wall, "
        "an older boxy CRT television on a low entertainment center playing a muted telenovela "
        "(soft glow), tall floor lamp with fringed amber shade in the corner, framed photos of "
        "her kids in school uniforms hung above the TV, window with mini-blinds half-drawn, "
        "twilight blue light filtering through from outside."
    ),
    "living_03_softmom_40s": (
        "Subject: 47-year-old Latina mother, dark brown hair in a low side-swept ponytail with a "
        "soft fringe across her forehead, pleasant round face with a small dark mole on her left "
        "cheek, tired but kind eyes, full cheeks, smooth olive-tan skin, simple gold stud "
        "earrings, faint small letter 'M' tattoo on the inside of her left forearm, no other "
        "visible ink. Wears a soft grey crewneck sweater over a thin black t-shirt. "
        "Background: modest Inland Empire family living room, beige walls, a cluster of framed "
        "kids' school photos arranged in a grid on the wall behind her, a low couch with "
        "mismatched throw pillows, a small folded stack of laundry resting on the arm of the "
        "couch, a small purple Virgen Mary statuette on a wall shelf, warm tungsten light from "
        "a corner lamp, evening."
    ),
    "living_04_younger_survivor": (
        "Subject: 38-year-old Latina woman, jet-black hair in a long center-parted braid resting "
        "over one shoulder, smooth round face, dark almond eyes with subtle hooded lids, a tiny "
        "silver septum hoop, a small dotted-line tattoo trailing along the right side of her "
        "jawline, light makeup smudged slightly at the eyes, warm olive-bronze skin. "
        "Wears an oversized heather-grey hoodie halfway zipped over a black tank top. "
        "Background: a small Echo Park apartment living room, warm dusty-pink accent wall, "
        "two framed minimalist black-and-white portraits hung in black frames, a small monstera "
        "houseplant on a side table beside her, a single lit white candle on a low coffee table, "
        "blue-grey dusk light filtering through a window with rolled-up bamboo blinds."
    ),
    "living_05_trailer_60s": (
        "Subject: 63-year-old Latina woman, mostly grey hair worn very short in natural tight "
        "curls, deep crow's feet, sun-weathered skin with prominent cheekbones and laugh lines, "
        "no makeup, small gold cross stud earrings, no necklace, no visible tattoos. "
        "Wears a faded purple cardigan over a grey mock-turtleneck. "
        "Background: a small mobile-home living room, fake-wood paneling on the walls, a faded "
        "floral curtain pulled shut behind her, a small CRT TV resting on a milk crate in the "
        "corner, a cluttered shelf with framed family photos and a small potted cactus, mixed "
        "harsh fluorescent overhead light combined with the warm glow of a tungsten table lamp."
    ),

    # ─── KITCHENS ────────────────────────────────────────────────────────────
    "kitchen_01_70s_aesthetic": (
        "Subject: 64-year-old Latina grandmother, fully grey hair in a low neat bun, no glasses, "
        "deep smile lines and crow's feet, warm tanned olive skin, dangling silver filigree "
        "earrings, simple thin gold chain at collarbone, no tattoos. "
        "Wears a teal blouse with a small floral pattern under a beige cotton apron tied at her "
        "neck. "
        "Background: yellow-and-brown 1970s-style Mexican-American family kitchen, formica "
        "counter, brown wooden cabinets, a steaming pot on the stove behind her shoulder, "
        "framed Last Supper print on the wall, avocado-green and harvest-gold tile backsplash, "
        "afternoon sunlight streaming through gingham curtains over the kitchen sink."
    ),
    "kitchen_02_workingmom_40s": (
        "Subject: 47-year-old Latina working mother, dark brown hair in a messy half-up ponytail "
        "with strands escaping at the temples, faint dark circles under the eyes, full cheeks, "
        "light freckles across the bridge of her nose, small silver heart pendant necklace, "
        "simple silver hoop earrings, small abstract line tattoo on the inside of her right "
        "wrist, smooth olive skin. "
        "Wears a plain black v-neck t-shirt. "
        "Background: small modern apartment kitchen with white cabinets and grey granite "
        "counters, a microwave and toaster on the counter behind her, a half-eaten cereal bowl "
        "and a kid's lunchbox visible on the counter, a child's small backpack hanging from a "
        "chair back behind her, soft cool morning light through a window."
    ),
    "kitchen_03_abuelita_70s": (
        "Subject: 71-year-old Latina abuelita, fully white hair pulled back in a simple low bun, "
        "deep wrinkles around the eyes and mouth, wire-rim glasses, soft jowls, pale olive skin "
        "with reddened cheeks, no makeup, small pearl stud earrings, a thin gold chain with a "
        "small Saint Jude medal at her chest, no tattoos. "
        "Wears a cream-colored knitted cardigan over a buttoned floral blouse. "
        "Background: traditional Mexican home kitchen, hand-painted Talavera tile counter and "
        "backsplash in blues and yellows, a large carved wooden crucifix on the wall, bunches "
        "of dried herbs (rosemary, oregano) hanging from a wooden beam, a strand of dried red "
        "chiles, soft sunlight streaming through a small window above the sink, a framed photo "
        "of her late husband on a high shelf."
    ),
    "kitchen_04_50s_cluttered": (
        "Subject: 56-year-old Latina woman, dark brown hair heavily streaked with grey worn "
        "loose just past her shoulders, weathered face with deep crow's feet and faint vertical "
        "lip lines, no makeup, simple silver hoop earrings, an older faded abstract tattoo on "
        "the inside of her right forearm, warm olive skin. "
        "Wears a faded chambray button-up shirt over a plain white t-shirt, sleeves rolled to "
        "the elbows. "
        "Background: cluttered small kitchen, an old white refrigerator covered in family photos "
        "and colorful magnets directly behind her, a stack of unopened mail on the counter, a "
        "coffee maker mid-brew, brown wooden cabinets with one door slightly ajar, a small "
        "oscillating fan running on the counter, warm yellow afternoon light."
    ),
    "kitchen_05_60s_dim": (
        "Subject: 61-year-old Latina woman, dark brown hair shot with grey, mid-length and "
        "pulled half back with a brown plastic clip, square jaw with a light double chin, "
        "dark calm eyes, no makeup, plain silver stud earrings, a small thin gold cross "
        "necklace at her collarbone, no visible tattoos. "
        "Wears a maroon button-down blouse. "
        "Background: small older kitchen with white tile counters and dark stained-wood "
        "cabinets, dim natural light filtering through a small window above the sink, a Virgen "
        "de Guadalupe magnet on the fridge behind her, a small ceramic rooster on top of the "
        "refrigerator, a stained-glass cross hanging in the window."
    ),
}

MODEL = "gpt-image-2"
SIZE = "1024x1536"  # portrait, ~2:3


def gen_one(slug, persona):
    t0 = time.time()
    print(f"[{slug}] start", flush=True)
    full_prompt = f"{persona}\n\n{STYLE_STEM}"
    data = {
        "model": MODEL,
        "prompt": full_prompt,
        "n": 1,
        "size": SIZE,
        "quality": "high",
    }
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
        },
        json=data, timeout=600,
    )
    dt = time.time() - t0
    if not r.ok:
        print(f"[{slug}] FAILED ({dt:.1f}s) {r.status_code}: {r.text[:400]}", flush=True)
        return slug, None
    try:
        b64 = r.json()["data"][0]["b64_json"]
    except Exception as e:
        print(f"[{slug}] bad response ({dt:.1f}s): {e} body={r.text[:300]}", flush=True)
        return slug, None
    out = OUT_DIR / f"{slug}.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"[{slug}] DONE ({dt:.1f}s) → {out}", flush=True)
    return slug, str(out)


def main():
    print(f"Generating {len(PERSONAS)} themed Pixar personas → {OUT_DIR}", flush=True)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen_one, slug, p): slug for slug, p in PERSONAS.items()}
        for fut in concurrent.futures.as_completed(futs):
            slug, path = fut.result()
            results[slug] = path
    print("\n=== summary ===", flush=True)
    for slug in PERSONAS:
        print(f"  {slug:36s} → {results.get(slug) or 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
