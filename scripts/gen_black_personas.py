"""Generate mid-40s BLACK-woman photoreal living-room personas via KIE gpt-image-2 (2K, 9:16).

Theme: Black women who could plausibly have been incarcerated at California women's prisons
(CCWF / Chowchilla) ~1995-2010 — so mid-40s today (was inside late-20s/early-30s). Working-class
American. Varied hair (natural, locs, braids, twists, headwrap, short grey TWA), skin tone,
build, tattoos, region/socioeconomic living rooms. Quiet, weary, contemplative — the look of
"considering speaking up".

All photoreal handheld phone selfies, eye contact, soft neutral mouth, NO smile.

Routing: KIE gpt-image-2 at resolution=2K, aspect_ratio=9:16 (per 2026-05-20 rule —
GPT Image goes through KIE, not OpenAI direct). Memory: feedback_image_gen_provider.md

Output: outputs/chowchilla_black_personas/reference/b01.png … b06.png
"""
import concurrent.futures
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import kie_client

OUT_DIR = pathlib.Path("outputs/chowchilla_black_personas/reference")
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_STEM = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic, "
    "available light only, soft natural indoor light. Fully photorealistic photograph — "
    "NOT animated, NOT stylized, NOT 3D, NOT Pixar. Real photo with photographic imperfections: "
    "visible pores, fine lines, faint under-eye darkness, dry lips, slight facial asymmetry, "
    "no makeup or minimal, no beauty mode, no retouching, no filter, no smile. Expression: "
    "quiet, weary, composed — eyes direct to the camera, soft neutral mouth — the look of a "
    "Black working-class woman in her own living room considering speaking up about something "
    "heavy from her past. NOT smiling, NOT crying — just present and contemplative. "
    "No on-screen text, no captions, no subtitles."
)

PERSONAS = {
    "b01": (
        "Subject: 44-year-old Black woman, warm medium-brown skin, natural 4C hair pulled up into "
        "a soft afro puff with a few grey coils at the temples and edges laid, faint under-eye "
        "darkness, no makeup, small gold stud earrings, a thin gold chain at her collarbone, no "
        "visible tattoos. Wears a plain heather-grey crewneck sweatshirt. Background: small "
        "apartment living room, beige walls, a low couch with mismatched throw pillows, a dark-wood "
        "entertainment center with a flat-screen TV (off), framed school portraits of her kids "
        "clustered on the wall behind her, warm tungsten light from a corner lamp."
    ),
    "b02": (
        "Subject: 52-to-mid-40s-looking 45-year-old Black woman, deep dark-brown skin, long thin "
        "box braids gathered back, a few greys, soft full face, gentle smile lines, no makeup, "
        "simple silver hoop earrings, no necklace, a small faded line tattoo on the inside of her "
        "left forearm just visible at her cuff. Wears a faded burgundy plaid flannel shirt over a "
        "plain white t-shirt. Background: small wood-paneled living room, framed photographs of "
        "grandchildren in mismatched frames on the wall, a hand-crocheted afghan over the back of "
        "a faded sofa, a tall white prayer candle on a side table, warm late-afternoon light."
    ),
    "b03": (
        "Subject: 43-year-old Black woman, light-brown / caramel skin, relaxed hair pulled back "
        "tightly into a sleek low bun with a sweep of edges, thin penciled eyebrows, smudged dark "
        "eyeliner worn off, large silver hoop earrings, a small thin script tattoo on the side of "
        "her neck, a hard weathered look, a small chin scar. Wears a plain black ribbed tank top "
        "with a denim jacket draped on her shoulders. Background: cramped apartment living room, "
        "off-white walls with one large framed black-and-white photo of her grown children, a low "
        "couch with dark throw pillows, a small lit votive candle on a side table, dim warm light."
    ),
    "b04": (
        "Subject: 46-year-old Black woman, medium-dark brown skin, short natural TWA (teeny "
        "weeny afro) cut close with visible grey throughout, gold-rimmed reading glasses pushed "
        "down her nose, gentle round face, fine wrinkles around the eyes, small gold stud earrings, "
        "a thin gold chain with a small cross at her collarbone. Wears a soft beige knit cardigan "
        "over a fitted heather-grey t-shirt. Background: tidy suburban living room, neutral beige "
        "walls, two well-tended houseplants on a wooden side table, a cluster of framed family "
        "photographs above an overstuffed beige sofa, late-afternoon light from a window."
    ),
    "b05": (
        "Subject: 47-year-old Black woman, deep dark-brown skin with weathered texture and fine "
        "lines, hair wrapped in a muted patterned head wrap with a few greys showing at the front, "
        "gaunt tired face, deep-set eyes, no makeup, simple small gold stud earrings, a thin gold "
        "chain with a small saint medal. Wears a long-sleeved muted floral blouse buttoned to the "
        "neck. Background: small older Southern bungalow living room, warm wood-paneled wall, a "
        "large framed church fan and a wooden cross on the wall, several saint-medal candles on a "
        "wooden shelf, a brown corduroy couch with embroidered pillow covers, warm light."
    ),
    "b06": (
        "Subject: 44-year-old Black woman, warm brown skin with faint freckles across the nose and "
        "cheeks, medium-length two-strand twists pulled half-back with a few wisps escaping, faint "
        "under-eye darkness, no makeup, simple small gold hoop earrings, a thin gold chain. Wears a "
        "plain soft sage-green t-shirt. Background: small tidy apartment living room, plain "
        "light-grey walls, framed school photographs of two young kids crowded above a low "
        "entertainment center, a muted TV on it, a small folded stack of kids' laundry on the arm "
        "of a low couch, a colorful kids' toy poking out from under the sofa, warm tungsten light."
    ),
}


def gen_one(slug, persona):
    t0 = time.time()
    print(f"[{slug}] start", flush=True)
    full_prompt = f"{persona}\n\n{STYLE_STEM}"
    try:
        res = kie_client.generate_gpt_image(full_prompt, aspect_ratio="9:16", resolution="2K")
    except Exception as e:
        print(f"[{slug}] EXCEPTION ({time.time()-t0:.1f}s): {e}", flush=True)
        return slug, None
    dt = time.time() - t0
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{slug}] FAILED ({dt:.1f}s): {res.get('failMsg') or res.get('raw')}", flush=True)
        return slug, None
    out = OUT_DIR / f"{slug}.png"
    kie_client.download(res["urls"][0], str(out))
    print(f"[{slug}] DONE ({dt:.1f}s) → {out}", flush=True)
    return slug, str(out)


def main():
    print(f"Generating {len(PERSONAS)} Black-woman living-room personas (KIE 2K) → {OUT_DIR}", flush=True)
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
