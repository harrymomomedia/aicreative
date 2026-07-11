"""Women's-Prison vox-pop — street-casual persona references (gpt-image-2 via KIE, 2K 9:16).
1 interviewer (holds mic, silent-on-camera) + 3 distinct respondents.
Explicit per-persona anthropometry to defeat gpt-image-2 mode-collapse.
"""
import os, pathlib, concurrent.futures as cf, requests
from kie_client import generate_gpt_image

OUT = pathlib.Path("outputs/wp_voxpop/reference"); OUT.mkdir(parents=True, exist_ok=True)

REAL = ("Photoreal candid documentary street photo (NOT a glamour or fashion shoot, NOT a "
        "celebrity portrait) — an ordinary everyday person, plain average features. Natural skin "
        "with visible pores, fine lines, uneven tone, no makeup, no beauty retouching, no filter. "
        "Bright natural daylight, sunny urban sidewalk with softly out-of-focus storefronts and a "
        "faded awning edge behind (no readable signage). Waist-up, casual vox-pop framing.")

PERSONAS = {
 "interviewer": (
   "A friendly female street interviewer, late 20s, warm approachable smile, medium-tan skin, oval "
   "face, brown wavy shoulder-length hair, small silver stud earrings, casual light-blue denim "
   "jacket over a white tee. She holds up a black foam-windscreen handheld microphone with a small "
   "BLANK news cube (no logo) toward the camera, arm extended. Looking slightly off-camera as if "
   "listening. " + REAL),
 "respondent_a": (
   "A young woman, early 20s, round face, light-olive skin, dark brown hair in a claw clip with "
   "loose strands, a few freckles, expressive raised eyebrows (surprised look), plain grey zip "
   "hoodie. Ordinary passerby. " + REAL),
 "respondent_b": (
   "A woman in her 30s, heart-shaped face, deep-brown skin, Afro-textured hair pulled back into a "
   "puff, gold hoop earrings, lively animated expression, denim jacket over a mustard top. "
   "Ordinary passerby. " + REAL),
 "respondent_c": (
   "A woman in her late 50s, long slightly gaunt face, fair weathered sun-lined skin, grey-streaked "
   "hair to the shoulders, reading glasses pushed up on her head, calm serious warm expression, "
   "soft oatmeal cardigan. Ordinary passerby. " + REAL),
}

def gen(name, prompt):
    print(f"[gen] {name}\n  gpt-image-2 (t2i, 2K, 9:16): {prompt[:110]}...")
    r = generate_gpt_image(prompt, aspect_ratio="9:16", resolution="2K")
    if r.get("status") != "success" or not r.get("urls"):
        return name, None, r
    url = r["urls"][0]
    dst = OUT / f"{name}.png"
    dst.write_bytes(requests.get(url, timeout=120).content)
    return name, str(dst), url

with cf.ThreadPoolExecutor(max_workers=4) as ex:
    for name, path, extra in ex.map(lambda kv: gen(*kv), PERSONAS.items()):
        print(f"[done] {name} -> {path if path else 'FAILED: '+str(extra)[:160]}")
print("ALL DONE")
