"""Generate 10 photoreal Latina living-room personas via OpenAI gpt-image-2.

Theme: women who could plausibly have been incarcerated at California women's prisons
(CCWF / CIW) between 1995-2010 — so 41 to 65 today. Diversity across age, hair, body,
skin tone, tattoos, religious vs secular, urban vs suburban living rooms.

All photoreal selfie portraits (NOT Pixar). Handheld phone selfie aesthetic, eye contact,
quiet contemplative weary expression — the look of "considering speaking up".

Output: outputs/1777697550119-gyvk6m8/reference_living_real/lr01.png … lr10.png
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

OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/reference_living_real")
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_STEM = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic, "
    "available light only, soft natural indoor light. Fully photorealistic photograph — "
    "NOT animated, NOT stylized, NOT 3D, NOT Pixar. Real photo with photographic imperfections: "
    "visible pores, fine lines, faint under-eye darkness, dry lips, slight facial asymmetry, "
    "no makeup or minimal, no beauty mode, no retouching, no filter, no smile. Expression: "
    "quiet, weary, composed — eyes direct to the camera, soft neutral mouth — the look of a "
    "Latina woman in her own living room considering speaking up about something heavy from "
    "her past. NOT smiling, NOT crying — just present and contemplative. "
    "No on-screen text, no captions, no subtitles."
)

PERSONAS = {
    "lr01": (
        "Subject: 47-year-old Latina woman, mid-tone olive skin, dark brown hair pulled half-up "
        "with messy strands escaping at the temples, slight grey at the roots, faint under-eye "
        "darkness, soft full face, no makeup, small thin gold chain at her collarbone, simple "
        "stud earrings, no visible tattoos. Wears a plain heather-grey crewneck sweater. "
        "Background: small Inland Empire apartment living room, beige walls, a cheap dark-wood "
        "entertainment center with a flat-screen TV (off), a low couch with mismatched throw "
        "pillows, framed school portraits of her kids in a cluster on the wall behind her, "
        "warm tungsten light from a corner floor lamp."
    ),
    "lr02": (
        "Subject: 52-year-old Latina woman, light olive skin, dark brown hair shot heavily with "
        "grey, pulled back into a low ponytail, deep crow's feet, a faint mole on her left cheek, "
        "no makeup, simple silver hoop earrings, no necklace, an older faded line tattoo on the "
        "inside of her left forearm just visible at her cuff. Wears a faded red plaid flannel "
        "shirt over a plain white t-shirt. Background: small wood-paneled El Monte living room, "
        "framed photographs of grandchildren in mismatched frames hung on the wall behind her, "
        "a hand-crocheted afghan draped over the back of a faded sofa, a tall white religious "
        "candle on a side table, warm late-afternoon light."
    ),
    "lr03": (
        "Subject: 58-year-old Latina abuelita, pale olive skin, fully grey hair in a tidy low bun, "
        "soft jowls, wire-rim reading glasses, gentle wrinkles around eyes and mouth, a small thin "
        "gold cross necklace at her collarbone, simple pearl stud earrings. Wears a modest dusty "
        "pink knitted cardigan over a buttoned cream blouse. Background: warm-toned older home "
        "living room, lace curtains diffusing afternoon sun, a large framed Virgen de Guadalupe "
        "portrait on the wall behind her, a small prayer card and a lit votive candle on a side "
        "table, a plastic-covered floral-print sofa partially visible, polished hardwood floor."
    ),
    "lr04": (
        "Subject: 44-year-old Latina woman, warm tan skin, jet-black hair pulled back tightly into "
        "a sleek low ponytail, drawn-on thin penciled eyebrows, a tiny dark teardrop tattoo near "
        "her left eye, large silver hoop earrings, dark lipstick worn off and faded, small chin "
        "scar. Wears a plain black ribbed tank top with a denim jacket draped on her shoulders. "
        "Background: cramped East Los Angeles apartment living room, off-white walls with one "
        "large framed black-and-white photograph of her grown children, a low couch with dark "
        "throw pillows, a small lit votive candle on a side table, dim warm overhead light."
    ),
    "lr05": (
        "Subject: 56-year-old Latina-Filipina mixed-heritage woman, warm tan skin, dark brown "
        "hair shoulder-length parted in the middle with grey at the temples, gold-rimmed reading "
        "glasses pushed slightly down her nose, gentle round face, simple small silver hoop "
        "earrings, a thin gold chain. Wears a soft beige knitted cardigan over a fitted heather-"
        "grey t-shirt. Background: small Whittier-style suburban living room, neutral beige walls, "
        "two well-tended houseplants on a wooden side table, a cluster of framed family "
        "photographs above an overstuffed beige sofa partially visible behind her, late afternoon "
        "natural light from a window to her right."
    ),
    "lr06": (
        "Subject: 49-year-old Latina woman, warm olive skin, dark brown wavy hair worn loose past "
        "her shoulders with a few grey strands at the temples, a faint older line-art rose "
        "tattoo on the inside of her right forearm, a small silver stud in her left nostril, "
        "no makeup. Wears a soft loose cotton t-shirt in faded teal. Background: small San "
        "Fernando Valley apartment living room, a woven Mexican wall hanging behind her, two "
        "candles on a low wooden coffee table partially visible, a stack of paperback books, a "
        "small handmade dreamcatcher hanging in a window with mid-day light filtering through."
    ),
    "lr07": (
        "Subject: 61-year-old Latina woman, pale olive skin, fully grey hair cut to her shoulders "
        "with a slight natural curl, wire-rim reading glasses on a beaded chain around her neck, "
        "soft round face, gentle wrinkles, simple small pearl stud earrings, a thin gold chain "
        "with a small saint medal at her collarbone, no tattoos. Wears a navy mock-turtleneck "
        "under an open beige cardigan. Background: small tidy condo living room, beige walls, "
        "several framed family photographs arranged by size on the wall behind her, a flat-screen "
        "TV (off) on a wooden stand partially visible, a leather-bound Bible resting on a polished "
        "coffee table, late morning light."
    ),
    "lr08": (
        "Subject: 42-year-old Latina woman, light olive skin, dark brown hair pulled back into "
        "a thick low ponytail with wisps escaping at her temples, faint freckles across the bridge "
        "of her nose and her cheekbones, simple silver stud earrings, a small thin gold chain at "
        "her collarbone. Wears a plain heather-grey t-shirt. Background: small Pomona apartment "
        "living room, framed school photographs of her two kids crowded above a low entertainment "
        "center, a TV on it playing something muted, a small folded stack of children's laundry "
        "resting on the arm of a low couch, a colorful kids' toy car poking out from under the "
        "sofa, warm tungsten light."
    ),
    "lr09": (
        "Subject: 64-year-old Latina woman, olive-tan skin, fully white hair in a soft loose low "
        "bun, deep wrinkles around her eyes and mouth, fine lines on her forehead, simple small "
        "pearl stud earrings, a thin gold chain with a small Virgen de Guadalupe medal at her "
        "collarbone. Wears a long-sleeved muted floral blouse buttoned to the neck. Background: "
        "small older bungalow living room, warm wood-paneled wall behind her, several saint-medal "
        "candles on a wooden shelf, a large carved wooden crucifix above an antique radio, a "
        "brown corduroy couch with hand-embroidered pillow covers partially visible, warm late-"
        "afternoon natural light."
    ),
    "lr10": (
        "Subject: 53-year-old Latina woman, warm tan skin, dark brown hair shot heavily with grey, "
        "mid-length and pulled half-back, plucked-thin chola-style penciled eyebrows, three small "
        "dot tattoos along the right side of her jaw, a faded line-art tattoo just visible at the "
        "edge of her right sleeve, simple silver hoop earrings, dark eyeliner smudged slightly. "
        "Wears a faded black v-neck band t-shirt. Background: dim East Los Angeles apartment "
        "living room, plain off-white walls with one large framed photograph of her teenage child "
        "in the center, a wooden rosary draped over a side-table lamp, a small unlit candle, dark "
        "couch partially visible, dim warm tungsten light."
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
        print(f"[{slug}] bad response ({dt:.1f}s): {e}", flush=True)
        return slug, None
    out = OUT_DIR / f"{slug}.png"
    out.write_bytes(base64.b64decode(b64))
    print(f"[{slug}] DONE ({dt:.1f}s) → {out}", flush=True)
    return slug, str(out)


def main():
    print(f"Generating {len(PERSONAS)} photoreal living-room personas → {OUT_DIR}", flush=True)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(gen_one, slug, p): slug for slug, p in PERSONAS.items()}
        for fut in concurrent.futures.as_completed(futs):
            slug, path = fut.result()
            results[slug] = path
    print("\n=== summary ===", flush=True)
    for slug in PERSONAS:
        print(f"  {slug} → {results.get(slug) or 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
