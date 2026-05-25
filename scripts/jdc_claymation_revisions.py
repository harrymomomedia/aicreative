"""IL JDC explainer — CLAYMATION revision clips (round 2, KIE Seedance Fast).

Addresses director notes:
  - "paid out millions" -> survivor sees NEWS on his phone, totally SHOCKED
  - "to people it happened to" -> MANY survivors
  - "most of us" -> young survivors on the STREETS OF CHICAGO (El tracks, brick),
    before justice (somber)
  - hope/ending -> DRAMATICALLY BRIGHT & HAPPY (strong contrast), deep-brown survivor
  - last clip -> MEANINGFUL: man comforting his younger self (closure)
  - setting -> more CHICAGO (El, skyline, three-flats); affected kid deep-brown

Skin-tone descriptor ("deep-brown skin"), NOT racial label, + no "juvenile"
trigger word — moderation-safe. Route: KIE (permissive). 480p 9:16 5s, no audio.

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
    " Handmade claymation stop-motion b-roll, nobody speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "in the soft clay, hand-sculpted surfaces, matte clay sheen, gentle jerky "
    "frame-stepping stop-motion movement, shallow tabletop miniature depth of field, "
    "Aardman Wallace-and-Gromit diorama craft. Cold, muted, slightly desaturated, "
    "bleak mood. No captions, no subtitles, no on-screen text, no readable words."
)

CLAY_BRIGHT = (
    " Handmade claymation stop-motion b-roll, nobody speaking, no dialogue. A "
    "plasticine modeling-clay world with visible thumbprints and fingerprint dents "
    "in the soft clay, hand-sculpted surfaces, matte clay sheen, gentle jerky "
    "frame-stepping stop-motion movement, shallow tabletop miniature depth of field, "
    "Aardman Wallace-and-Gromit diorama craft. BRIGHT, warm, sunny, vivid saturated "
    "cheerful colors, golden sunlight, uplifting hopeful joyful mood. No captions, "
    "no subtitles, no on-screen text, no readable words."
)

SHOTS = {
    # beat 3 — "paid out millions" (shock) + "to people / people like me" (many)
    "clay_news_shock": (
        "An adult clay man with deep-brown skin, short dark hair and a short beard "
        "sits in a dim room holding a glowing smartphone in both hands, his eyes going "
        "wide and his mouth falling open in stunned disbelief at what he is reading on "
        "the screen, one hand rising toward his open mouth. The cold light of the phone "
        "screen lights up his shocked face. He has just seen the news. Shock, "
        "disbelief, a jolt." + CLAY
    ),
    "clay_many_survivors": (
        "A large group of many adult clay people standing together in rows facing the "
        "camera — mostly men with deep-brown skin, plus some women, of different ages "
        "— solemn, dignified, standing shoulder to shoulder in quiet solidarity. So "
        "many of them, many faces stretching back into the distance. Soft even "
        "daylight. A crowd of survivors." + CLAY
    ),
    # beat 5 — "most of us" on the streets of Chicago, before justice
    "clay_chicago_victims": (
        "Several young clay men and teenage boys with deep-brown skin standing together "
        "on a gritty Chicago street: red-brick three-flat buildings, an elevated train "
        "track running overhead, a grey overcast sky, cracked sidewalk. They look "
        "toward the camera with quiet, weary, serious faces. Survivors who have not yet "
        "seen justice. Muted Chicago city tones." + CLAY
    ),
    # hope turn — DRAMATICALLY bright & happy
    "clay_happy_bright": (
        "An adult clay man with deep-brown skin, short dark hair and a short beard "
        "slowly breaks into a wide, genuine, joyful smile, his eyes shining bright with "
        "relief and happiness, head lifting, a heavy weight finally gone. His face is "
        "bathed in warm bright golden sunlight. Pure relief and joy." + CLAY_BRIGHT
    ),
    "clay_justice_chicago_bright": (
        "A group of clay men and women with deep-brown skin standing close together, "
        "smiling and embracing, on a bright sunny Chicago street with red-brick "
        "buildings, blue sky and an elevated train in the distance, warm golden "
        "sunlight washing over them. A feeling of justice, relief and community. "
        "Joyful, hopeful, vivid and bright." + CLAY_BRIGHT
    ),
    # meaningful ending — man comforts his younger self (closure)
    "clay_ending_reunion": (
        "An adult clay man with deep-brown skin, short hair and a short beard kneels "
        "down and gently rests a reassuring hand on the shoulder of his younger self — "
        "a small deep-brown-skinned clay boy — both bathed in warm bright golden light, "
        "the man smiling softly and at peace, the boy looking up at him with relief and "
        "trust. Healing, closure, it is going to be okay. Warm, bright, tender." + CLAY_BRIGHT
    ),
    # Chicago lockup establishing (avoids the word 'juvenile')
    "clay_chicago_juvie_ext": (
        "The exterior of a grim hulking institutional lockup building at dusk in "
        "Chicago: grey concrete and red-brick walls with narrow barred windows and a "
        "tall razor-wire fence, an elevated train track curving past nearby, the faint "
        "Chicago city skyline behind under a heavy grey sky. Cold, imposing, urban. "
        "Slow push-in." + CLAY
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] generating (KIE Seedance Fast 480p 9:16 5s)...", flush=True)
    r = generate_seedance(prompt=prompt, duration=5, aspect_ratio="9:16", generate_audio=False)
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
