"""Depo Myth-buster — PIXAR-style B-ROLL set (Seedance 2 Fast, KIE, 480p 9:16).

12 shots for the myth-buster register (objection-killer, knowing host + b-roll metaphor for each
myth). FACE CONSISTENCY: face_01_round_twistout (warm round face, twistout, knit cardigan — the
maternal "I've-been-there" energy that fits myth-buster) uploaded once + passed as Seedance
reference_image on the 3 HOST shots (s01, s07, s12). All other shots are pure b-roll, no face ref.

Locked diagnosis-first language: meningioma / Depo / "may qualify for significant compensation".
No disclaimer lingo on screen (per feedback_no_disclaimer_lingo_in_copy).

Run:  .venv/bin/python scripts/depo_pixar_myth_broll.py [--only s01,s07] [--dur 6]
Output: outputs/depo_pixar_myth/{slug}.mp4
"""
import argparse, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download, upload_file

OUT_DIR = Path("outputs/depo_pixar_myth"); OUT_DIR.mkdir(parents=True, exist_ok=True)
FACE_PNG = Path("outputs/depo_pixar/face/face_01_round_twistout.png")  # the picked host

PIXAR = (
    " Rendered in modern 3D animated feature-film style, high-end CG animation (Pixar-DreamWorks "
    "look): smooth stylized characters with large warm expressive eyes, soft subsurface skin, "
    "appealing rounded proportions, polished cinematic studio lighting, shallow depth of field. "
    "No dialogue, no captions, no subtitles, no on-screen text, no readable words or signage, "
    "no watermark."
)
WARM = " Warm golden afternoon interior light."
COOL = " Cool blue-grey interior light, slightly desaturated."

HOST = ("an ordinary Black woman about 45, soft round kind face with full cheeks, deep brown skin, "
        "short tightly-coiled natural twist-out hair with a few silver strands, warm tired eyes, "
        "wearing a soft mauve cardigan over a plain top")

# (slug, use_face, prompt)
SHOTS = [
    # ── HOST OPEN — establishes who's talking, instantly knowing
    ("s01_host_open", True,
     f"A warm cozy living-room couch in soft afternoon light. {HOST} sits on the couch, looking "
     "gently into the camera with a knowing half-smile, the kind that says 'I've been there too'. "
     "She tilts her head slightly, a small reassuring nod. Wide medium shot, very slow push-in." + WARM + PIXAR),

    # ── MYTH 1: TOO LATE
    ("s02_calendar_years", False,
     "Pixar-style close-up of a paper wall calendar in a quiet bedroom; the pages flip rapidly "
     "forward through season after season — many years passing in a blur. A small wedding ring "
     "sits on a side table beside the calendar, gathering dust. Soft amber dusk light." + COOL + PIXAR),
    ("s03_calendar_stop", False,
     "Same Pixar wall calendar from before — the rapidly-flipping pages suddenly STOP on the "
     "current month, then one page gently flutters backward. A small soft glowing green check "
     "mark appears in the corner of the calendar. Light warms from cool to gentle gold." + PIXAR),

    # ── MYTH 2: TOO EXPENSIVE
    ("s04_empty_wallet", False,
     "Pixar-style close-up: an empty open leather wallet sits on a warm wooden kitchen counter, a "
     "single folded bill and a couple of coins beside it. A weary hand sets it down with a soft "
     "sigh. Soft afternoon kitchen window light." + COOL + PIXAR),
    ("s05_phone_free", False,
     "Pixar-style close-up: the same hand picks up a smartphone instead of the wallet; the phone "
     "screen shows a clean tidy form with neat colored rows and a soft glowing green check "
     "appearing. Light warms and brightens, hopeful." + WARM + PIXAR),

    # ── MYTH 3: NOT THE SUING TYPE
    ("s06_not_sue", False,
     "Pixar-style medium shot of a DIFFERENT ordinary Black woman about 50 — soft full face, neat "
     "low ponytail, wearing a simple navy sweater — sitting at her own kitchen table, gently "
     "shaking her head with hands raised in a small 'not me' gesture. Warm window light." + PIXAR),
    ("s07_host_neither", True,
     f"Return to the same warm living-room couch. {HOST} looks directly into the camera, gives a "
     "small honest half-smile, and tilts her head slightly as if saying 'me neither'. Close medium "
     "shot, very gentle push-in." + WARM + PIXAR),

    # ── THE PIVOT — what they didn't tell us
    ("s08_folder_studies", False,
     "Pixar-style close-up: a manila file folder slides across a warm wooden desk and gently opens, "
     "revealing a stack of stylized medical study pages with abstract colored graphs and shapes "
     "spreading out (NO readable text). Warm desk-lamp light from the side." + WARM + PIXAR),

    # ── THE REVEAL — diagnosis + the link
    ("s09_mri_tumor", False,
     "Pixar-style stylized MRI brain scan glowing on a backlit hospital lightbox, soft cinematic "
     "glow. A pale rounded shape — a meningioma tumor — gently pulses in the lining of the brain. "
     "No people. Cool teal-white clinical light." + COOL + PIXAR),
    ("s10_vial_calendar", False,
     "Pixar-style close-up: a stylized birth-control injection vial sits on a clean white tray on a "
     "counter; above it a small calendar shows a repeated soft glowing dot every three months "
     "across several rows of months, marking years of repeated shots. No needles in motion. Clean "
     "neutral light." + PIXAR),
    ("s11_connection_line", False,
     "Pixar-style medium shot: the stylized MRI lightbox from before sits on the left, the vial on "
     "its tray sits on the right; a soft glowing line gently draws between them, connecting the "
     "two. A closed folder with abstract graphs sits softly out of focus behind. Warm-cool mixed "
     "light." + PIXAR),

    # ── CTA — host close, reassuring
    ("s12_host_cta", True,
     f"Return to the warm living-room couch one final time. {HOST} leans very slightly toward the "
     "camera with a calm reassuring look, a small nod, her hand resting open on the couch beside "
     "her — gentle, warm, sincere. Medium shot, very slow gentle push-in." + WARM + PIXAR),
]


def gen(slug, use_face, prompt, dur, face_url):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists() and out.stat().st_size > 50000:
        return slug, "exists", str(out)
    refs = [face_url] if (use_face and face_url) else None
    print(f"[{slug}] gen Seedance-Fast 480p 9:16 {dur}s face={'Y' if refs else 'N'}", flush=True)
    r = generate_seedance(prompt=prompt, duration=dur, aspect_ratio="9:16",
                          ref_images=refs, generate_audio=False)
    if r.get("status") != "success" or not r.get("urls"):
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
        print(f"Uploading host face: {FACE_PNG}", flush=True)
        face_url = upload_file(str(FACE_PNG))
        print(f"  face_url: {face_url[:70]}...", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(gen, slug, uf, pr, args.dur, face_url): slug for slug, uf, pr in shots}
        for f in as_completed(futs):
            slug = futs[f]
            try:
                s, status, info = f.result()
                print(f"[{s}] {status}: {info[:120]}", flush=True)
            except Exception as e:
                print(f"[{slug}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
