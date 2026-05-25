"""IL JDC explainer — CLAYMATION EMOTIONAL ARC v2 (demographic re-roll).

The v1 arc (jdc_claymation_emotion.py) rendered the adult survivor as an older
~50-60s white man — off-demographic (audience is Black/Latino men 18-39) and
breaking the "same kid grown up" continuity. This re-roll locks the whole arc
to ONE consistent survivor with deep-brown clay skin: a boy, then the same
person as a man in his early 30s.

Skin-tone descriptor ("deep-brown clay skin"), NOT a racial label — per the
project moderation rule ("Black man" + sensitive context trips moderation; a
skin-tone descriptor passes). No dialogue, no explicit abuse — emotion only.

Route: OpenRouter Seedance FAST (bytedance/seedance-2.0-fast), 480p 9:16 5s,
~$0.05/s. Saved as _v2 alongside the originals for comparison.

Output: outputs/illinois_jdc_claymation/clay_e{1-7}_*_v2.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from openrouter_video import generate_seedance, download

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

# child = e1-e4, adult (same person, early 30s) = e5-e7
SHOTS = {
    "clay_e1_fear_eyes_v2": (
        "Extreme close-up of a young clay teenage boy's face filling the frame — warm "
        "deep-brown clay skin, short dark hair. Huge expressive sculpted clay eyes "
        "wide with raw fear, eyebrows pulled up and together, lower lip trembling, "
        "breath held, frozen stiff. He stares up at something terrifying just "
        "off-frame that is never shown. A single bead of cold sweat. The horror lives "
        "entirely in the eyes. Cold blue-grey light." + CLAY
    ),
    "clay_e2_recoil_corner_v2": (
        "A young clay teenage boy with deep-brown clay skin and short dark hair backs "
        "away into the corner of a bare cold clay room, sliding down the wall to the "
        "floor, knees coming up, one arm raised weakly to shield his face, head turned "
        "away, mouth open in a frightened silent gasp, his whole small body trembling "
        "and shrinking smaller. Something terrible is off-frame and never shown. Pure "
        "fear and helplessness in the body language. Cold dim light." + CLAY
    ),
    "clay_e3_curled_sobbing_v2": (
        "A young clay teenage boy with deep-brown clay skin and short dark hair curled "
        "up tight in the fetal position on the cold hard floor of a bare clay room, "
        "knees hugged to his chest, face buried down into his arms, shoulders heaving "
        "and shaking with silent sobs, hands clenched. Utter despair, shame, "
        "abandonment. A thin shaft of cold light from a small high barred window falls "
        "across him. Heartbreaking, raw." + CLAY
    ),
    "clay_e4_hollow_tear_v2": (
        "Close-up of the young clay teenage boy's face — deep-brown clay skin, short "
        "dark hair — hollow and blank and far away, the light gone from his dull eyes, "
        "staring at nothing. A single fat clay tear slowly wells up, spills over, and "
        "rolls down his cheek while his face stays frozen and numb, trying to feel "
        "nothing. Devastating quiet emptiness. Dim cold light." + CLAY
    ),
    "clay_e5_adult_haunted_v2": (
        "The same person now grown into a weary adult clay man in his early thirties, "
        "with deep-brown clay skin, short hair and a short beard, sitting alone and "
        "hunched in a chair in a dim plain clay room at night, elbows on knees, "
        "staring down at the floor with exhausted haunted eyes, jaw tight, carrying a "
        "heavy unspoken weight. A slow heavy blink, a single tear, a long shaky "
        "breath. Hollowed out by years of silence. Deep grief on the clay face." + CLAY
    ),
    "clay_e6_lifting_hope_v2": (
        "The weary adult clay man in his early thirties — deep-brown clay skin, short "
        "hair, short beard — slowly lifts his head and looks up, tired eyes "
        "glistening and searching, the faintest flicker of disbelief and fragile hope "
        "breaking across his clay face for the first time — the look of someone "
        "realizing they are not alone and it was not their fault. Lips part slightly, "
        "a shaky hopeful breath, eyebrows lifting. Soft warm light begins to touch his "
        "face. Tender, raw." + CLAY
    ),
    "clay_e7_release_light_v2": (
        "The adult clay man in his early thirties — deep-brown clay skin, short hair, "
        "short beard — rises and turns his face up toward a growing warm golden light, "
        "eyes closing, shoulders finally dropping and releasing the weight carried for "
        "years, a single tear sliding down but his mouth softening into the smallest "
        "exhale of relief and peace. Finally seen, finally heard. The warm light glows "
        "brighter and fills the frame. Cathartic, hopeful." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (OpenRouter Seedance FAST 480p 9:16 5s)...", flush=True)
    try:
        r = generate_seedance(
            prompt=prompt,
            duration=5,
            resolution="480p",
            aspect_ratio="9:16",
            audio=False,
        )
    except Exception as e:
        return slug, "failed", f"EXC {e}"[:400]
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
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
