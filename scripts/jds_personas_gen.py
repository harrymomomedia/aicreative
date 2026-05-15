"""Generate gpt-image-2 reference frames for the 5 Illinois JDC personas.

All 5 personas: Black men, authentic Chicago neighborhood / streetwear aesthetic.
Demographic mix mirrors actual IL juvenile detention survivor population
(~70% Black at Cook County JTDC, predominantly male, ages now 20s-50s).

Style brief: lived-in urban realism — NOT glamorized "trap" aesthetic,
NOT clean studio — actual peer-to-peer UGC from people who were in the system.

One image per persona, 1024x1536 portrait. Output to:
  outputs/illinois_jdc_<persona-slug>/reference/1.png
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openai_image import generate_image

OUT_ROOT = Path("outputs")

COMMON_FRAMING = (
    "Photoreal handheld phone selfie video frame, 9:16 portrait orientation, "
    "tight selfie framing chin-to-forehead, eye-level, lens close to face, "
    "subject looking DIRECTLY into the camera lens, mouth in soft neutral line, "
    "NO smile, eyes open and engaged, slightly serious, eyebrows relaxed. "
    "Visible pores, faint razor bumps where applicable, fine lines, faint under-eye darkness, "
    "dry lips, slight skin asymmetry, slight oil shine on forehead/nose. "
    "NO makeup, NO beauty mode, NO retouching, NO filter, NO smoothing. "
    "Natural overcast daylight, soft shadows, slightly desaturated color, ordinary phone-camera color science. "
    "Mild front-camera lens distortion, faint handheld micro-shake blur. "
    "Working-class urban Chicago aesthetic — authentic, lived-in, NOT styled, NOT a model shoot, "
    "NOT glamorized, NOT a music-video aesthetic, NOT exaggerated jewelry or flashy clothing. "
    "Looks like a real person recording on their phone in their neighborhood. "
    "ABSOLUTELY NO on-screen text, no captions, no subtitles, no watermarks, no logos."
)

PERSONAS = {
    "urban_peer": {
        "slot": "A",
        "prompt": (
            "Black man, mid-20s, medium-dark skin tone, lean athletic build, short 360 waves haircut with a clean line-up at the forehead, "
            "thin chinstrap beard, no jewelry visible except a small plain silver hoop in left ear, "
            "plain heather-grey pullover hoodie (worn-in, not new). "
            "Background: Chicago neighborhood side street in autumn — brick three-flat building behind him "
            "with chipped paint on the trim, chain-link fence partly visible, overcast grey sky, "
            "a few yellow leaves on the sidewalk. Cool overcast daylight on his face. "
            "Expression: calm, direct, slightly guarded — peer-to-peer voice. "
            + COMMON_FRAMING
        ),
    },
    "blue_collar": {
        "slot": "B",
        "prompt": (
            "Black man, mid-30s, medium-dark skin tone, stocky working build, low fade haircut, "
            "full but neatly trimmed beard with faint grey just beginning at the chin, "
            "small forearm tattoo just visible at the wrist edge of frame, plain black durag tied at the back "
            "(visible at the hairline), oversized faded navy work hoodie with a faint old paint stain on one sleeve. "
            "Background: outside a Chicago corner store / bodega — chipped brick wall, faded red awning edge, "
            "a fragment of an old hand-painted sign out of focus, daylight overcast. "
            "Expression: plainspoken, tired around the eyes, talking from experience. "
            + COMMON_FRAMING
        ),
    },
    "stoop_calm": {
        "slot": "C",
        "prompt": (
            "Black man, early 30s, dark skin tone, medium build, short freeform locs pulled back into a loose puff, "
            "thin mustache and short beard, plain white cotton t-shirt under an unzipped grey track jacket, "
            "no chain. Faint small tattoo on the side of the neck (geometric, not flashy). "
            "Background: front stoop of a Chicago three-flat brick building — weathered concrete steps, "
            "iron railing in soft focus behind him, daylight overcast, hint of a neighbor's porch railing in the distance. "
            "Expression: quiet, deliberate, calm — like he's about to say something he's thought about for a long time. "
            + COMMON_FRAMING
        ),
    },
    "weathered_survivor": {
        "slot": "D",
        "prompt": (
            "Black man, late 40s, medium-brown skin tone, medium build, close-cut hair with clear grey at the temples, "
            "salt-and-pepper full beard, deep forehead lines, faded older tattoo just visible at the inside wrist "
            "(letters, blurred with age — not legible), weathered hands faintly visible holding the phone, "
            "plain dark-navy henley shirt with the top two buttons undone, no jewelry. "
            "Background: front porch of a modest older Chicago two-flat — weathered wood porch railing, "
            "hint of an aluminum screen door behind him, soft late-afternoon overcast daylight. "
            "Expression: reflective, patient, older-brother gravity, eye contact steady. "
            + COMMON_FRAMING
        ),
    },
    "block_serious": {
        "slot": "E",
        "prompt": (
            "Black man, late 20s, lighter-medium skin tone, lean build, medium-length freeform dreads loose to "
            "just past the shoulders, thin chinstrap beard, small simple gold-tone stud earring (left ear only, "
            "no chains), plain black pullover hoodie with the hood down. "
            "Background: interior of a parked older sedan during daylight — driver's seat, headrest visible "
            "behind his shoulder, soft daylight coming through the side window on the left side of his face, "
            "slightly cool color, faint blur of a neighborhood street through the window. Seatbelt strap faintly "
            "visible across one shoulder. "
            "Expression: dry, matter-of-fact, slightly tired — not amused, not angry, just done. "
            + COMMON_FRAMING
        ),
    },
}


def gen_one(slug, persona):
    out_dir = OUT_ROOT / f"illinois_jdc_{slug}" / "reference"
    out_path = out_dir / "1.png"
    print(f"[{persona['slot']}] {slug} → generating…")
    result = generate_image(
        prompt=persona["prompt"],
        out_path=str(out_path),
        size="1024x1536",
        quality="high",
        n=1,
    )
    if result["status"] != "success":
        print(f"[{persona['slot']}] {slug} FAILED: {result['raw'].get('error')}")
        return slug, None
    print(f"[{persona['slot']}] {slug} → {result['paths'][0]}")
    return slug, result["paths"][0]


def main():
    results = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(gen_one, slug, p): slug for slug, p in PERSONAS.items()}
        for fut in as_completed(futures):
            slug, path = fut.result()
            results[slug] = path
    print("\nSUMMARY")
    for slug, path in results.items():
        print(f"  {slug}: {path}")


if __name__ == "__main__":
    main()
