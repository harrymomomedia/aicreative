"""IL JDC explainer — CLAYMATION EMOTIONAL ARC (Seedance KIE 480p 9:16).

The emotional spine. Tells "how bad it was" through ONE clay character —
a child, then the same person grown up — using the expressive clay face and
body to carry raw emotion (Aardman's superpower). The threat and the act are
NEVER on screen; the horror is felt entirely through the child's reaction and
the adult's haunted aftermath.

ABSOLUTE GUARDRAILS (ethics + moderation):
  - NEVER the act. NEVER nudity. NEVER a minor in any sexual context.
  - NO abuser shown. NO bed/bunk/shower. Figure always clothed.
  - Emotion only: fear, despair, numbness, grief, then hope/release.
  - Showing the child's terrified/crying FACE (reaction) is safer than
    showing a menacing adult, AND hits harder.

  e1 fear_eyes      — terror, staring up at unseen off-frame threat
  e2 recoil_corner  — backing into a corner, shielding face, shrinking
  e3 curled_sobbing — fetal on cold floor, silent sobs
  e4 hollow_tear    — numb hollow face, single tear
  e5 adult_haunted  — same person grown, carrying it alone for years
  e6 lifting_hope   — head lifts, fragile flicker of hope / being seen
  e7 release_light   — face up to warm light, weight released

Output: outputs/illinois_jdc_claymation/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_claymation")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLAY = (
    " Handmade claymation stop-motion, nobody speaking, no dialogue. A plasticine "
    "modeling-clay world with visible thumbprints and fingerprint dents in the soft "
    "clay, hand-sculpted surfaces, matte clay sheen, gentle jerky frame-stepping "
    "stop-motion movement, shallow tabletop miniature depth of field, Aardman "
    "Wallace-and-Gromit craft. A deeply expressive, emotive sculpted clay face that "
    "carries strong raw emotion. Muted, slightly desaturated, melancholic. No "
    "dialogue, no captions, no subtitles, no on-screen text, no readable words."
)

SHOTS = {
    "clay_e1_fear_eyes": (
        "Extreme close-up of a young clay teenager's face filling the frame, huge "
        "expressive sculpted clay eyes wide with raw fear, eyebrows pulled up and "
        "together, lower lip trembling, breath held, frozen stiff. The young face "
        "stares up at something terrifying just off-frame that is never shown. A "
        "single bead of cold sweat. The horror lives entirely in the eyes. Cold "
        "blue-grey light." + CLAY
    ),
    "clay_e2_recoil_corner": (
        "A young clay teenager backs away into the corner of a bare cold clay room, "
        "sliding down the wall to the floor, knees coming up, one arm raised weakly "
        "to shield their face, head turned away, mouth open in a frightened silent "
        "gasp, the whole small body trembling and shrinking smaller. Something "
        "terrible is off-frame and never shown. Pure fear and helplessness in the "
        "body language. Cold dim light." + CLAY
    ),
    "clay_e3_curled_sobbing": (
        "A young clay teenager curled up tight in the fetal position on the cold hard "
        "floor of a bare clay room, knees hugged to the chest, face buried down into "
        "the arms, shoulders heaving and shaking with silent sobs, hands clenched. "
        "Utter despair, shame, abandonment. A thin shaft of cold light from a small "
        "high barred window falls across them. Heartbreaking, raw." + CLAY
    ),
    "clay_e4_hollow_tear": (
        "Close-up of the young clay teenager's face, hollow and blank and far away, "
        "the light gone from the dull eyes, staring at nothing. A single fat clay "
        "tear slowly wells up, spills over, and rolls down the cheek while the face "
        "stays frozen and numb, trying to feel nothing. Devastating quiet emptiness. "
        "Dim cold light." + CLAY
    ),
    "clay_e5_adult_haunted": (
        "The same person now grown into a weary adult clay figure years later, "
        "sitting alone and hunched in a chair in a dim plain clay room at night, "
        "elbows on knees, staring down at the floor with exhausted haunted eyes, jaw "
        "tight, carrying a heavy unspoken weight. A slow heavy blink, a single tear, "
        "a long shaky breath. Hollowed out by years of silence. Deep grief on the "
        "clay face." + CLAY
    ),
    "clay_e6_lifting_hope": (
        "The weary adult clay figure slowly lifts their head and looks up, tired eyes "
        "glistening and searching, the faintest flicker of disbelief and fragile hope "
        "breaking across the clay face for the first time — the look of someone "
        "realizing they are not alone and it was not their fault. Lips part slightly, "
        "a shaky hopeful breath, eyebrows lifting. Soft warm light begins to touch "
        "the face. Tender, raw." + CLAY
    ),
    "clay_e7_release_light": (
        "The adult clay figure rises and turns their face up toward a growing warm "
        "golden light, eyes closing, shoulders finally dropping and releasing the "
        "weight carried for years, a single tear sliding down but the mouth softening "
        "into the smallest exhale of relief and peace. Finally seen, finally heard. "
        "The warm light glows brighter and fills the frame. Cathartic, hopeful." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (Seedance KIE 480p 9:16 5s)...", flush=True)
    r = generate_seedance(
        prompt=prompt,
        duration=5,
        aspect_ratio="9:16",
        generate_audio=False,
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in SHOTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
