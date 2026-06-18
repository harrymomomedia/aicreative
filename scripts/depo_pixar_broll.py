"""Depo-Provera brain-meningioma — PIXAR-style B-ROLL set (Seedance 2 Fast, KIE, 480p 9:16).

Pixar/3D-CG sibling of depo_claymation_broll.py. Same diagnosis-first beats, same ~41s VO
(outputs/depo_claymation/vo/survivor_f49.mp3 — style-independent, reused). REAL medical settings
(radiology, neurology exam, clinic, pharmacy, hospital waiting room, law office) and meningioma-
forward visuals (MRI brain scans, rotating 3D brain w/ the tumor highlighted).

FACE CONSISTENCY: locked Pixar face (face/face_02_oval_bun_glasses.png, a Black woman ~45 with
glasses + low bun) uploaded and passed as a Seedance reference_image on every PROTAGONIST shot.
Crowd shot + young-injection flashback carry NO face ref (diversity / a younger woman).

11 shots over the 8 VO beats. 480p hardcoded; generate_audio off (VO replaces).
Run:  .venv/bin/python scripts/depo_pixar_broll.py [--only s01_mri_reveal,s02_exam_news,s09_tv_news] [--dur 6]
Output: outputs/depo_pixar/{slug}.mp4
"""
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download, upload_file

OUT_DIR = Path("outputs/depo_pixar")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FACE_PNG = OUT_DIR / "face" / "face_02_oval_bun_glasses.png"

PIXAR = (
    " Rendered in a modern 3D animated feature-film style, high-end CG animation (big-studio 3D "
    "animated movie / Pixar-DreamWorks look): smooth stylized characters with large warm expressive "
    "eyes, soft subsurface skin, appealing rounded proportions, cinematic depth of field and "
    "lighting, polished high-quality 3D render. No dialogue, no captions, no subtitles, no on-screen "
    "text, no readable words or signage."
)
COLD = " Muted, desaturated, melancholic cold blue-grey light."
WARM = " Warm golden hopeful light, gentle and reassuring."
PROT = "an ordinary Black woman about 45 with glasses and dark hair in a low bun, in a plain knit cardigan over a blouse"

# (slug, use_face, prompt)
SHOTS = [
    ("s01_mri_reveal", False,
     "A real hospital radiology reading room, dim: a large backlit wall monitor shows a detailed MRI "
     "brain scan in cross-section, with a pale rounded mass — a meningioma tumor — clearly visible "
     "against the brain. A radiologist's hand slowly points at the mass. Realistic clinical reading "
     "room with dark monitors and a keyboard. Slow push-in on the scan." + COLD + PIXAR),
    ("s02_exam_news", True,
     "A real hospital neurology exam room with an anatomical brain poster on the wall and an exam "
     "table: a doctor in a white coat gently holds up a brain scan and shows it to " + PROT + ", who "
     "is seated. Her face slowly falls and one hand rises toward her mouth as the news lands heavy. "
     "Slow steady push-in." + COLD + PIXAR),
    ("s03_her_stunned", True,
     "Intimate close-up of " + PROT + " in the exam room, eyes lowered, one hand pressed to her "
     "temple, absorbing the diagnosis. Very slow drift in. Still, stunned, alone with it." + COLD + PIXAR),
    ("s04_brain_rotate", False,
     "Close on a glowing anatomical 3D brain model slowly rotating on a clinic desk, a pale rounded "
     "meningioma tumor clearly highlighted on its surface; behind it a monitor shows the matching MRI "
     "slice. Clinical, precise, cold." + COLD + PIXAR),
    ("s05_injection", False,
     "A real clinic exam room with a paper-covered exam table, YEARS AGO: a nurse in scrubs gives an "
     "ordinary YOUNG Black woman in her early-to-mid 20s, in a casual t-shirt, an injection in her "
     "upper arm with a small syringe; the young woman looks away calmly, trusting — a routine "
     "birth-control shot. Soft neutral daytime light with a faintly warm nostalgic tint (the past)." + PIXAR),
    ("s06_calendar", False,
     "A clinic counter: a small wall calendar rapidly flips its pages season after season, a round "
     "wall clock ticks, and a neat row of small medication vials lines the counter — years of "
     "repeated shots, like clockwork. Methodical, repeating." + COLD + PIXAR),
    ("s07_leaflet", True,
     "" + PROT + " stands in a pharmacy aisle holding a small folded medication leaflet, reading it, "
     "her brow furrowing. Behind her a large dark shadow looms and grows across the shelves — the "
     "warning she was never given. Foreboding, the shadow creeping." + COLD + PIXAR),
    ("s08_waiting_room", False,
     "A real hospital waiting room with rows of chairs: many ordinary Black women of different ages "
     "and builds, ALL in plain everyday clothes — sweaters, blouses, headscarves — sit and stand "
     "quietly together. A soft warm shaft of light breaks through a window. Quiet solidarity, a "
     "hopeful turn." + PIXAR),
    ("s09_tv_news", True,
     "A warm living room at dusk: " + PROT + " sits holding a glowing smartphone while a television "
     "in the background glows with an abstract news broadcast graphic (colored shapes, no readable "
     "text). Her face slowly lifts, a first flicker of hope. Warm light grows and enters the room." + PIXAR),
    ("s10_attorney", True,
     "A warm, calm law office with a desk, shelves and a window: " + PROT + " sits across from a "
     "reassuring attorney in a suit who listens and gently nods. Private, safe, unhurried." + WARM + PIXAR),
    ("s11_phone_cta", True,
     "" + PROT + " sits in warm golden light holding a smartphone that shows a simple form (clean "
     "rows of colored shapes, no readable text), a calm hopeful look on her face as her thumb gently "
     "taps it. Reassuring, private, hopeful, the warm glow on her face." + WARM + PIXAR),
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
    ap.add_argument("--only", default="")
    ap.add_argument("--dur", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    shots = SHOTS
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        shots = [s for s in SHOTS if s[0] in want]

    face_url = None
    if any(uf for _, uf, _ in shots):
        print(f"Uploading locked Pixar face: {FACE_PNG}", flush=True)
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
