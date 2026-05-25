"""10 IL JDC abuse-survivor personas spanning the 18-39 demographic.

Demographic basis (from litigation + IL juvenile-justice data):
- Overwhelmingly Black men, secondary Latino, ~85-90% male
- Small but real female-survivor segment (Warrenville / Pere Marquette)
- Chicago South/West Side concentration + downstate clusters (Harrisburg area)
- Age 18-39 today (detained as teens ~2000-2025)
- Working-class, institution-distrustful, testimonial UGC tone

Spread across 10:
  01 — young Black man 20, South Side residential
  02 — Black man 26, West Side, guarded
  03 — Black man 34, reflective (named-plaintiff age band)
  04 — Latino man 24, Little Village / Pilsen
  05 — young Black man 19, CTA bus stop, student-ish
  06 — Black woman 28, South Side (female-survivor segment)
  07 — Black/biracial man 31, downstate small-town (Harrisburg area)
  08 — Black man 36, reentry vibe, intimate indoor
  09 — young Black man 22, neighborhood basketball court
  10 — Black woman 33, indoor intimate (older female segment)

Style: candid iPhone front-camera selfie testimonial still, photoreal,
9:16. gpt-image-2 via KIE @ 2K (current default image provider).

Output: outputs/illinois_jdc_ugc/personas_demographic/persona_{NN}.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download

OUT_DIR = Path("outputs/illinois_jdc_ugc/personas_demographic")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Shared realism tail — the proven iPhone-selfie photoreal recipe
TAIL = (
    " Candid iPhone 14 Pro front-camera selfie video still, 24mm equivalent, f/1.9, "
    "vertical 9:16, head and upper shoulders framed, eye-level. Photographic realism: "
    "visible skin pores, slight oil sheen on the nose and forehead, natural under-eye "
    "shadow, faint razor irritation, individual facial hairs catching the light, "
    "slightly chapped lower lip, a small natural catchlight from the open sky (NOT a "
    "ring light). Subtle handheld micro-blur, faint sensor noise in shadows, very mild "
    "chromatic aberration at high-contrast edges. NO beauty filter, NO skin smoothing, "
    "NO studio key light, NO orange Instagram tint, NO glossy retouch. Looks like a real "
    "iPhone front-camera frame grab from a personal testimonial recording. NO on-screen "
    "text, NO captions, NO watermarks."
)

PROMPTS = {
    "persona_01_southside_young": (
        "Black man, age 20, medium-dark skin, short freeform twists with a clean high "
        "temple-fade taper, faint chin-strap goatee, small gold stud in left ear. "
        "Wearing a charcoal-grey zip hoodie under a tan corduroy jacket. Standing on a "
        "South Side Chicago residential block at overcast late-afternoon: flat cool "
        "daylight, behind him a softly out-of-focus red-brick two-flat and bare-branched "
        "trees, no cars, no street visible. Expression: reserved, guarded, mouth closed."
        + TAIL
    ),
    "persona_02_westside_guarded": (
        "Black man, age 26, dark brown skin, short low fade with tight curls on top, "
        "full short beard. Wearing a black quilted puffer jacket over a grey hoodie, "
        "hood down. Standing under the elevated train tracks on the West Side of Chicago: "
        "cool overcast light, black steel girders softly out of focus overhead, brick "
        "wall behind. Expression: guarded, slightly suspicious, jaw tense, mouth closed."
        + TAIL
    ),
    "persona_03_reflective_34": (
        "Black man, age 34, medium-brown skin, short Caesar cut with a faded line-up, "
        "well-groomed mustache and full short beard with a few early grey hairs, small "
        "healed scar above the left eyebrow. Wearing a worn olive-green hoodie. Standing "
        "on a Chicago residential block at golden hour: warm low side-light from "
        "camera-right, soft fill shadow on the other side, out-of-focus brick three-flat "
        "and a mature elm behind. Expression: serious, weighted, reflective, mouth "
        "closed and slightly tense." + TAIL
    ),
    "persona_04_latino_littlevillage": (
        "Latino man, age 24, light-medium tan skin, short fade with a slick combed top, "
        "thin mustache and light chin stubble, small silver chain at the collar. Wearing "
        "a dark denim trucker jacket over a white tee. Standing on a Little Village / "
        "Pilsen Chicago street at late afternoon: warm overcast light, behind him a "
        "softly out-of-focus brick wall with a faded colorful mural edge, no cars. "
        "Expression: quiet, contemplative, mouth closed." + TAIL
    ),
    "persona_05_busstop_19": (
        "Black man, age 19, deep brown skin, short freeform twists, faint mustache "
        "stubble, no other facial hair. Wearing a faded brown carhartt-style work jacket "
        "over a heather-grey crewneck sweatshirt, a backpack strap visible on one "
        "shoulder. Standing at a Chicago CTA bus stop at overcast afternoon: flat cool "
        "daylight, out-of-focus blue bus-stop sign and a street with parked cars behind. "
        "Expression: young, thoughtful, slightly tired, mouth closed." + TAIL
    ),
    "persona_06_woman_southside_28": (
        "Black woman, age 28, medium-dark skin, shoulder-length box braids pulled half "
        "back, minimal natural makeup look (bare, no glam), small gold hoop earrings. "
        "Wearing a oatmeal-grey hoodie under a denim jacket. Standing on a South Side "
        "Chicago residential block at overcast late-afternoon: soft cool daylight, "
        "out-of-focus brick building and bare trees behind. Expression: quiet strength, "
        "guarded but composed, mouth closed." + TAIL
    ),
    "persona_07_downstate_31": (
        "Biracial Black man, age 31, light-medium brown skin, short low fade with a full "
        "neat beard, no jewelry. Wearing a dark green flannel shirt over a plain grey "
        "thermal henley. Standing on the wooden porch of a small frame house in a "
        "downstate Illinois small town (Harrisburg area, NOT urban) at golden hour: warm "
        "low sun, out-of-focus clapboard siding and a bare yard tree behind, rural quiet "
        "feel. Expression: weathered, serious, mouth closed." + TAIL
    ),
    "persona_08_reentry_36": (
        "Black man, age 36, dark brown skin, clean-shaved bald head, full short beard "
        "with flecks of grey, a small faded tattoo just visible at the side of the neck. "
        "Wearing a plain heather-grey crewneck t-shirt. Standing near a window inside a "
        "small modest Chicago apartment: soft warm late-afternoon daylight through the "
        "window onto his face, out-of-focus interior (blinds, painted wall) behind. "
        "Expression: heavy, contemplative, eyes carrying weight, mouth closed." + TAIL
    ),
    "persona_09_court_22": (
        "Black man, age 22, medium-dark skin, short twists with a high taper fade, faint "
        "goatee, thin gold chain at the collar. Wearing a grey hooded sweatshirt with the "
        "hood up. Standing on an outdoor concrete neighborhood basketball court in "
        "Chicago at overcast late-afternoon: flat cool light, out-of-focus chain-link "
        "fence and faded painted court lines behind. Expression: calm, steady, slightly "
        "guarded, mouth closed." + TAIL
    ),
    "persona_10_woman_indoor_33": (
        "Black woman, age 33, medium-brown skin, natural hair in a low bun, bare face "
        "(no makeup), small stud earrings. Wearing a plain rust-colored long-sleeve top. "
        "Sitting near a window inside a small modest apartment: soft warm late-afternoon "
        "daylight on her face, out-of-focus interior (kitchen counter, family photo frame "
        "on the wall) behind. Expression: reflective, emotional weight held quietly, "
        "mouth closed." + TAIL
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.png"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (KIE gpt-image-2 2K 9:16)...", flush=True)
    r = generate_gpt_image(prompt=prompt, aspect_ratio="9:16", resolution="2K")
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:300]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in PROMPTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
