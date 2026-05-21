"""Generate reference-character candidates for the IL juvenile-detention survivor ad
(Script A persona: Black man, early-to-mid 30s, survivor testimonial).

6 candidates varied by setting / hair / wardrobe / lighting. All home interiors —
NO parked-car setting, NO neck tattoo, NO durag (these are Veo moderation triggers
downstream, and these stills become the i2v anchors).

Output: outputs/il_juvie_a/reference/character_<letter>_<slug>.png

Run:  .venv/bin/python scripts/il_juvie_personas.py [--only A C] [--max-workers 6]
"""
import argparse
import concurrent.futures
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from kie_client import generate_gpt_image, download

OUT = ROOT / "outputs" / "il_juvie_a" / "reference"
OUT.mkdir(parents=True, exist_ok=True)

FRAMING = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld front-facing phone selfie "
    "aesthetic, the man looking directly into the camera lens."
)
REALISM = (
    "Photorealistic real-world photograph. Visible skin pores, fine lines, faint under-eye "
    "darkness, slight razor bumps, dry lips, slight facial asymmetry, no makeup, no beauty "
    "mode, no retouching, no filter, no skin smoothing. Natural available light, slight "
    "handheld feel, faint sensor grain."
)
REGISTER = (
    "Weary, serious, reflective expression. Tired but composed. Not smiling. Direct, heavy "
    "eye contact with the camera, like a man about to say something difficult about his past."
)
NO_TEXT = "No on-screen text, no captions, no logos, no watermarks, no graphics."

# letter: (slug, hair+facial hair, wardrobe, setting+lighting)
CANDIDATES = {
    "A": ("livingroom",
          "short fade haircut, neat short full beard",
          "a plain dark charcoal hoodie",
          "sitting on a worn fabric couch in a small apartment living room, a few framed "
          "family photos on the wall behind him slightly out of focus, warm afternoon light "
          "from a window off to one side"),
    "B": ("kitchen",
          "short twists, light stubble",
          "a plain white cotton t-shirt",
          "standing leaning against the counter in a small home kitchen at evening, soft warm "
          "overhead light, refrigerator and cabinets blurred behind him"),
    "C": ("bedroom",
          "clean shaved bald head, short goatee",
          "a charcoal-gray henley shirt",
          "sitting on the edge of a made bed in a modest bedroom, soft muted morning light "
          "through a curtained window, plain wall behind him"),
    "D": ("porch",
          "short afro, light beard",
          "an olive-green zip-up hoodie over a gray tee",
          "sitting on a front porch step of a residential home, a brick wall slightly out of "
          "focus behind him, flat overcast daytime light"),
    "E": ("hallway",
          "short waves under a black wave cap tied at the back, short beard",
          "a black crewneck sweatshirt",
          "standing in a dim apartment hallway near a doorway, a warm lamp glow from one side, "
          "muted shadows"),
    "F": ("table",
          "low fade, neat mustache and short chin beard",
          "a navy and gray plaid flannel shirt unbuttoned over a gray tee",
          "sitting at a small table in a spare room, a phone face-down on the table near his "
          "hand, daylight from a window in front of him"),
}


def build_prompt(letter):
    slug, hair, wardrobe, setting = CANDIDATES[letter]
    character = (
        f"A Black man in his early-to-mid 30s, medium-dark to dark skin tone, {hair}. "
        f"He wears {wardrobe}. {setting}."
    )
    return "\n\n".join([FRAMING, character, REGISTER, REALISM, NO_TEXT])


def generate_one(letter):
    slug = CANDIDATES[letter][0]
    out_path = OUT / f"character_{letter}_{slug}.png"
    if out_path.exists():
        return (letter, "exists", str(out_path))
    t0 = time.time()
    res = generate_gpt_image(build_prompt(letter), aspect_ratio="9:16", resolution="2K")
    if res["status"] != "success" or not res.get("urls"):
        return (letter, "failed", res.get("failMsg") or res.get("raw"))
    download(res["urls"][0], str(out_path))
    return (letter, "success", f"{out_path}  ({round(time.time()-t0,1)}s)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+", default=None, help="subset of letters, e.g. --only A C")
    ap.add_argument("--max-workers", type=int, default=6)
    args = ap.parse_args()

    letters = args.only or list(CANDIDATES.keys())
    print(f"generating {len(letters)} persona candidate(s): {letters}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futs = {ex.submit(generate_one, L): L for L in letters}
        for f in concurrent.futures.as_completed(futs):
            L = futs[f]
            try:
                print(f"  → {f.result()}", flush=True)
            except Exception as e:
                print(f"  ✗ {L} ERROR: {str(e)[:200]}", flush=True)


if __name__ == "__main__":
    main()
