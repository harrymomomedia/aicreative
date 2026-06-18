"""Depo-Provera brain-meningioma — CLAYMATION B-ROLL set (Seedance 2 Fast, KIE, 480p 9:16).

Diagnosis-first explainer, ~41s VO (depo_claymation_vo.py). Aardman/Wallace-&-Gromit clay.
REAL medical settings (radiology suite, neurology exam room, clinic, pharmacy, hospital waiting
room) and meningioma-forward visuals (MRI brain scans, rotating 3D brain, the tumor highlighted).

FACE CONSISTENCY: a single locked clay face (outputs/depo_claymation/face/face_01_round_twistout.png,
a Black woman ~45) is uploaded and passed as a Seedance reference_image on every PROTAGONIST shot,
so she's the same woman throughout (Seedance has no built-in identity lock). Pure scan/object shots
carry no face ref. Tonal arc COLD (diagnosis) -> WARM (lawsuit/relief/CTA). Crowd = Black women
(the target audience). SPECIFY CLOTHING on all figures (Seedance renders nude otherwise). NO text.

11 shots over the 8 VO beats (some beats get 2 shots):
  s01 mri_reveal*   s02 exam_news   s03 her_stunned   s04 brain_rotate*   s05 injection
  s06 calendar*     s07 leaflet     s08 waiting_room  s09 tv_news         s10 attorney   s11 phone_cta
  (* = no face / scan-or-object shot)

480p hardcoded in kie_client.generate_seedance. generate_audio off (VO replaces).
Run:  .venv/bin/python scripts/depo_claymation_broll.py [--only s01_mri_reveal,s02_exam_news,s05_injection] [--dur 6]
Output: outputs/depo_claymation/{slug}.mp4
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download, upload_file

OUT_DIR = Path("outputs/depo_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FACE_PNG = OUT_DIR / "face" / "face_01_round_twistout.png"

CLAY = (
    " Handmade claymation stop-motion b-roll, no dialogue. A plasticine modeling-clay world with "
    "visible thumbprints and fingerprint dents in the soft clay, slightly uneven hand-sculpted "
    "surfaces, matte clay sheen, gentle jerky frame-stepping stop-motion movement, shallow tabletop "
    "miniature depth of field, Aardman Wallace-and-Gromit diorama craft. No dialogue, no captions, "
    "no subtitles, no on-screen text, no readable words or signage."
)
COLD = " Muted, desaturated, melancholic cold blue-grey light."
WARM = " Warm golden hopeful light, gentle and reassuring."
# Body/wardrobe only — the FACE comes from the reference image.
PROT = "an ordinary Black woman about 45 in a plain knit cardigan over a blouse"

# (slug, use_face, prompt)
SHOTS = [
    ("s01_mri_reveal", False,
     "A real clay hospital radiology reading room, dim: a large backlit wall monitor shows a "
     "detailed clay MRI brain scan in cross-section, and a pale rounded mass — a meningioma tumor — "
     "sits clearly against the brain. A clay radiologist's hand slowly points at the mass. Realistic "
     "clinical reading room with dark monitors and a keyboard. Slow push-in on the scan." + COLD + CLAY),
    ("s02_exam_news", True,
     "A real clay hospital neurology exam room with an anatomical brain poster on the wall and an "
     "exam table: a clay doctor in a white coat gently holds up a clay brain scan and shows it to " + PROT
     + ", who is seated. Her clay face slowly falls and one hand rises toward her mouth as the news "
     "lands heavy. Slow steady push-in." + COLD + CLAY),
    ("s03_her_stunned", True,
     "Intimate close-up of " + PROT + " in the clay exam room, eyes lowered, one clay hand pressed "
     "to her temple, absorbing the diagnosis. Very slow drift in. Still, stunned, alone with it." + COLD + CLAY),
    ("s04_brain_rotate", False,
     "Close on a glowing clay anatomical 3D brain model slowly rotating on a clay clinic desk, a pale "
     "rounded meningioma tumor clearly highlighted on its surface; behind it a monitor shows the "
     "matching clay MRI slice. Clinical, precise, cold." + COLD + CLAY),
    ("s05_injection", False,
     "A real clay clinic exam room with a paper-covered exam table, YEARS AGO: a clay nurse in scrubs "
     "gives an ordinary YOUNG Black woman in her early-to-mid 20s, in a casual t-shirt, an injection in "
     "her upper arm with a small clay syringe; the young woman looks away calmly, trusting — a routine "
     "birth-control shot. Soft neutral daytime light with a faintly warm nostalgic tint (this is the "
     "past)." + CLAY),
    ("s06_calendar", False,
     "A clay clinic counter: a small wall calendar rapidly flips its pages season after season, a "
     "round wall clock ticks, and a neat row of small clay medication vials lines the counter — years "
     "of repeated shots, like clockwork. Methodical, repeating." + COLD + CLAY),
    ("s07_leaflet", True,
     "" + PROT + " stands in a clay pharmacy aisle holding a tiny folded clay medication leaflet, "
     "reading it, her brow furrowing. Behind her a large dark clay shadow looms and grows across the "
     "shelves — the warning she was never given. Foreboding, the shadow creeping." + COLD + CLAY),
    ("s08_waiting_room", False,
     "A real clay hospital waiting room with rows of chairs: many ordinary Black clay women of "
     "different ages and builds, ALL in plain everyday clothes — sweaters, blouses, headscarves — sit "
     "and stand quietly together, with " + PROT + " among them in the foreground. A soft warm shaft of "
     "light begins to break through a window. Quiet solidarity, a hopeful turn." + CLAY),
    ("s09_tv_news", True,
     "A warm clay living room at dusk: " + PROT + " sits holding a small glowing clay smartphone while "
     "a clay television in the background glows with an abstract news broadcast graphic (colored "
     "shapes, no readable text). Her clay face slowly lifts, a first flicker of hope. Warm light grows "
     "and enters the room." + CLAY),
    ("s10_attorney", True,
     "A warm, calm clay law office with a desk, shelves and a window: " + PROT + " sits across from a "
     "reassuring clay attorney in a suit who listens and gently nods. Private, safe, unhurried." + WARM + CLAY),
    ("s11_phone_cta", True,
     "" + PROT + " sits in warm golden light holding a small clay smartphone that shows a simple clay "
     "form (clean rows of colored shapes, no readable text), a calm hopeful look on her face as her "
     "clay thumb gently taps it. Reassuring, private, hopeful, the warm glow on her face." + WARM + CLAY),
]


def gen(slug, use_face, prompt, dur, face_url):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    refs = [face_url] if (use_face and face_url) else None
    print(f"[{slug}] generating (Seedance-2-Fast 480p 9:16 {dur}s, face={'Y' if refs else 'N'})...", flush=True)
    r = generate_seedance(prompt=prompt, duration=dur, aspect_ratio="9:16",
                          ref_images=refs, generate_audio=False)
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma slugs")
    ap.add_argument("--dur", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    shots = SHOTS
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        shots = [s for s in SHOTS if s[0] in want]

    # upload the locked face fresh (KIE URLs expire ~24h) if any selected shot needs it
    face_url = None
    if any(uf for _, uf, _ in shots):
        print(f"Uploading locked face: {FACE_PNG}", flush=True)
        face_url = upload_file(str(FACE_PNG))
        print(f"  face_url: {face_url}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(gen, slug, uf, pr, args.dur, face_url): slug for slug, uf, pr in shots}
        for f in as_completed(futs):
            slug = futs[f]
            try:
                s, status, info = f.result()
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{slug}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
