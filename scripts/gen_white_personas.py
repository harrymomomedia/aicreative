"""Generate mid-40s WHITE-woman photoreal living-room personas via KIE gpt-image-2 (2K, 9:16).

Theme: white women who could plausibly have been incarcerated at California women's prisons
(CCWF / Chowchilla) ~1995-2010 — so mid-40s today (was inside late-20s/early-30s). Working-class
American. Varied hair, build, tattoos, region/socioeconomic living rooms. Quiet, weary,
contemplative — the look of "considering speaking up".

All photoreal handheld phone selfies, eye contact, soft neutral mouth, NO smile.

Routing: KIE gpt-image-2 at resolution=2K, aspect_ratio=9:16 (per 2026-05-20 rule change —
GPT Image goes through KIE, not OpenAI direct). Memory: feedback_image_gen_provider.md

Output: outputs/chowchilla_white_personas/reference/w01.png … w06.png
"""
import concurrent.futures
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import kie_client

OUT_DIR = pathlib.Path("outputs/chowchilla_white_personas/reference")
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_STEM = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic, "
    "available light only, soft natural indoor light. Fully photorealistic photograph — "
    "NOT animated, NOT stylized, NOT 3D, NOT Pixar. Real photo with photographic imperfections: "
    "visible pores, fine lines, faint under-eye darkness, dry lips, slight facial asymmetry, "
    "no makeup or minimal, no beauty mode, no retouching, no filter, no smile. Expression: "
    "quiet, weary, composed — eyes direct to the camera, soft neutral mouth — the look of a "
    "white working-class woman in her own living room considering speaking up about something "
    "heavy from her past. NOT smiling, NOT crying — just present and contemplative. "
    "No on-screen text, no captions, no subtitles."
)

PERSONAS = {
    "w01": (
        "Subject: 44-year-old white woman, fair skin with mild sun damage and faint freckles, "
        "dirty-blonde hair with darker roots pulled into a messy low bun with strands escaping, "
        "thin pale eyebrows, faint under-eye darkness, no makeup, small silver stud earrings, a "
        "faded old blue-line tattoo just visible on the inside of her left forearm. Wears a worn "
        "heather-grey zip hoodie over a plain t-shirt. Background: small rural double-wide trailer "
        "living room, faux wood-paneling on the walls, a worn plaid recliner partially visible, a "
        "framed photo of her kids and a small wooden cross on the wall behind her, a box-style TV "
        "on a low stand, warm dim lamp light."
    ),
    "w02": (
        "Subject: 45-year-old white woman, fair skin, medium-brown hair shot with grey cut to her "
        "shoulders and tucked behind one ear, soft tired face, crow's feet, no makeup, simple "
        "thin gold hoop earrings, a plain thin gold chain, no tattoos. Wears a plain navy "
        "long-sleeve henley. Background: modest working-class suburban living room, off-white "
        "walls, a beige microfiber sofa with a folded fleece blanket over the arm, a cluster of "
        "framed family photographs on the wall behind her, a flat-screen TV (off) on a wooden "
        "stand, late-afternoon natural light through a window."
    ),
    "w03": (
        "Subject: 43-year-old white woman, fair skin, dark brown hair pulled back tight into a "
        "sleek low ponytail, thin penciled eyebrows, smudged dark eyeliner worn off, a small thin "
        "script tattoo on the side of her neck and a faded line tattoo across the back of one "
        "hand, hoop earrings, a hard weathered look. Wears a plain black ribbed tank top with a "
        "flannel shirt hanging open over it. Background: cramped apartment living room, plain "
        "off-white walls with one large framed photo of a teenage kid, a dark couch with a "
        "mismatched throw pillow, a small unlit candle on a side table, dim warm tungsten light."
    ),
    "w04": (
        "Subject: 46-year-old white woman, fair ruddy skin, shoulder-length auburn / reddish-brown "
        "hair with greys parted in the middle, slightly heavier round face, gold-rimmed reading "
        "glasses pushed down her nose, faint freckles, no makeup, small pearl stud earrings. Wears "
        "a soft oversized maroon knit cardigan over a t-shirt. Background: cozy cluttered older "
        "home living room, warm beige walls, an overstuffed floral-print sofa with crocheted "
        "afghan, several mismatched framed photos and a small wall clock behind her, a houseplant "
        "on a side table, warm late-afternoon light."
    ),
    "w05": (
        "Subject: 47-year-old white woman, weathered fair skin with sun damage and deep smile/frown "
        "lines, thin ash-blonde hair going grey pulled half-back, gaunt tired face, no makeup, a "
        "thin silver chain, simple small stud earrings, no visible tattoos. Wears a faded denim "
        "button-up shirt over a white tee. Background: small country home living room, knotty "
        "wood-paneled wall, a mounted set of deer antlers and a framed landscape print behind her, "
        "a worn brown leather recliner partially visible, an old lamp casting warm light."
    ),
    "w06": (
        "Subject: 44-year-old white woman, fair skin with freckles across the nose and cheeks, "
        "light-brown hair in a loose messy bun with wisps at the temples, faint under-eye "
        "darkness, no makeup, simple silver stud earrings, a thin gold chain. Wears a plain "
        "soft sage-green t-shirt. Background: small tidy apartment living room, plain light-grey "
        "walls, framed school photographs of two young kids crowded above a low entertainment "
        "center, a muted TV on it, a small folded stack of kids' laundry on the arm of a low "
        "couch, warm tungsten light."
    ),
}


def gen_one(slug, persona):
    t0 = time.time()
    print(f"[{slug}] start", flush=True)
    full_prompt = f"{persona}\n\n{STYLE_STEM}"
    try:
        res = kie_client.generate_gpt_image(
            full_prompt, aspect_ratio="9:16", resolution="2K",
        )
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
    print(f"Generating {len(PERSONAS)} white-woman living-room personas (KIE 2K) → {OUT_DIR}", flush=True)
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
