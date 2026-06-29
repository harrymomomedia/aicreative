"""Batch 3 — 14 CREATIVE, prison-grounded image-ad concepts (deliberately NOT the card/UI/screenshot
style of batches 1-2). Cinematic documentary photography with the prison as the hero: return/at-the-
fence portraits, before/after diptych anchored to the same fence, atmospheric empty-prison place
shots, plus 3 bold formats (redacted grievance, editorial PSA poster, torn-and-mended photo).
gpt-image-2 (KIE, 2K, 1:1). Black + Latina personas, factual. Mostly text-free (primary carries copy);
disclaimer bar added later. QA the 3 text ones for spelling.

  python scripts/ccwf_creative_concepts.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/ccwf_women/creative_concepts")
PHOTO = (" Photoreal documentary photograph, cinematic natural light, real skin texture and "
         "imperfections, no beauty retouching, no filter, not stylized — like a real photojournalist "
         "shot. NO on-screen text, captions, headlines, logos, or watermarks anywhere in the image.")
TEXTRULE = (" Render the quoted text EXACTLY as written, spelled perfectly and legible; NO other "
            "text, letters, logos, or watermarks anywhere.")

CONCEPTS = [
    # --- prison-grounded return / testimonial portraits (no text) ---
    ("m01_return_gate",
     "An ordinary weathered Black woman in her 40s in plain street clothes standing on the road just "
     "outside a large California state prison's main gate, turned to look back at the tall chain-link "
     "fence topped with razor wire and a guard tower behind her, flat overcast daylight, shot from a "
     "respectful distance, cinematic and somber." + PHOTO),
    ("m02_at_fence_now",
     "A Latina woman in her 40s in everyday clothes standing on the OUTSIDE of a prison chain-link "
     "fence, one hand resting on the wire, looking through it at the empty prison yard and buildings "
     "beyond, razor wire above, harsh daylight, quiet and reflective." + PHOTO),
    ("m03_windshield_lookback",
     "From inside a parked car: a Black woman in the driver's seat seen partly in profile and "
     "reflected in the side mirror, looking out through the windshield at a California prison's "
     "perimeter fence and guard tower ahead, soft daylight, contemplative, cinematic shallow depth "
     "of field." + PHOTO),
    ("m04_small_against_wall",
     "A wide cinematic shot: a lone Latina woman standing small in the frame at the base of a "
     "massive grey prison wall topped with coils of razor wire, dwarfed by its scale, flat dramatic "
     "daylight, somber." + PHOTO),
    # --- before/after anchored to the prison ---
    ("m05_then_now_fence",
     "A vertical split-screen documentary diptych of the SAME Black woman. Left half: an aged faded "
     "photo of her as a young woman in a pale-blue prison uniform standing in a prison yard, with a "
     "small caption 'THEN'. Right half: her today, older, in plain clothes standing outside that same "
     "razor-wire chain-link fence, with a small caption 'NOW'. Photoreal, cinematic, documentary."
     + TEXTRULE),
    ("m06_photo_held_at_prison",
     "A weathered Latina woman in her 50s standing just outside a California prison gate, holding up "
     "toward the camera an old faded prison visitation photo of her younger self in a pale-blue "
     "uniform; the real prison fence and guard tower are softly out of focus behind her, overcast "
     "daylight, moving and quiet." + PHOTO),
    ("m07_two_survivors_gate",
     "Two ordinary women, one Black and one Latina, in their 40s in plain clothes, standing close "
     "together just outside a California prison's gate, the razor-wire fence and guard tower behind "
     "them, both looking at the camera with quiet resolve, flat daylight." + PHOTO),
    # --- the prison as the hero (atmospheric, no person) ---
    ("m08_empty_visiting_room",
     "An empty California women's prison visitation room: rows of bolted plastic stools and small "
     "tables, a faded painted tropical-beach mural on the cinderblock wall, harsh fluorescent light, "
     "no people, eerie and still." + PHOTO),
    ("m09_payphone",
     "A single battered stainless-steel inmate wall phone mounted on a scuffed cinderblock wall in "
     "an empty prison corridor, the metal cord hanging, fluorescent light, no people, lonely and "
     "stark." + PHOTO),
    ("m10_gate_dusk",
     "A California state prison entrance at dusk: the lit guard tower and razor-wire perimeter fence "
     "silhouetted against a deep blue-and-orange sky, distant security lighting, cinematic and "
     "ominous, news-documentary feel. No readable signage." + PHOTO),
    ("m11_made_bunk",
     "An empty prison cell: a single tightly-made narrow bunk with a thin mattress and folded grey "
     "blanket against a cinderblock wall, a small stainless toilet-sink, hard fluorescent light, "
     "shadows of bars, no people, stark." + PHOTO),
    # --- bold formats we haven't done ---
    ("m12_redacted_grievance",
     "A photoreal close-up of an official inmate grievance complaint form lying on a desk, titled "
     "'INMATE GRIEVANCE FORM', with most of the body text heavily blacked out under thick redaction "
     "bars, and ONE line left clearly readable in the middle: 'staff sexual misconduct — no action "
     "taken'. Realistic paper with a slight shadow, looks like a real redacted document."
     + TEXTRULE),
    ("m13_editorial_poster",
     "A bold high-design editorial PSA poster, magazine-cover art direction, with a stark cinematic "
     "photo of a prison fence and guard tower on a deep muted background. One powerful bold modern "
     "headline: 'They were supposed to be safe.'. A small line near the bottom: 'California women's "
     "prison survivors deserve to be heard.'. Premium and art-directed, NOT a flat lead-gen card."
     + TEXTRULE),
    ("m14_torn_mended",
     "A close-up still life: an old faded prison visitation photo of a young Black woman in a "
     "pale-blue uniform that was torn in half and carefully taped back together, lying on a dark "
     "wooden table, soft window light, intimate and symbolic." + PHOTO),
]


def gen(slug, prompt):
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(prompt, aspect_ratio="1:1", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, p) for s, p in CONCEPTS]
        for f in as_completed(futs):
            print(f.result(), flush=True)
