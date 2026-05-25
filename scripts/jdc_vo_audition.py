"""IL JDC claymation explainer — first-person survivor VO auditions.

Generates the opening lines with 4 candidate voices so the user can pick.
2 campaign clones (demographically authentic — cloned from our IL JDC
Black-male personas) + 2 clean ElevenLabs library males.

Weathered male, 30s-40s, grounded, NOT announcer. multilingual_v2 for a
reliable cross-voice comparison; the winner can be upgraded to eleven_v3
with emotion tags for the final.

Output: outputs/illinois_jdc_claymation/vo_auditions/{slug}.mp3
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import tts

OUT_DIR = Path("outputs/illinois_jdc_claymation/vo_auditions")
OUT_DIR.mkdir(parents=True, exist_ok=True)

AUDITION_TEXT = (
    "When I was a kid, Illinois locked me up. And something happened in there "
    "I never told anybody. For years. A guard sexually abused me. I buried it. "
    "Figured nobody would ever believe a kid like me."
)

# (slug, voice_id) — 2 campaign clones + 2 library males
VOICES = [
    ("01_jdc_reflective_clone", "aUZVK6pojWGqbSu2qApB"),   # jdc_p3_reflective_clean
    ("02_jdc_confession_clone", "KkWf4Ko4HqpDqmk9WFNK"),   # illinois_jdc_confession_p03_v2
    ("03_eric_trustworthy",     "cjVigY5qzO86Huf0OWal"),   # Eric - Smooth, Trustworthy
    ("04_brian_deep_comfort",   "nPczCjzI2devNBz1zQrb"),   # Brian - Deep, Resonant, Comforting
]


def gen(slug, voice_id):
    out = OUT_DIR / f"{slug}.mp3"
    try:
        tts(
            text=AUDITION_TEXT,
            voice_id=voice_id,
            out_path=str(out),
            model_id="eleven_multilingual_v2",
            stability=0.45,
            similarity_boost=0.85,
            style=0.0,
            speed=0.95,
            output_format="mp3_44100_192",
        )
        return slug, "ok", str(out)
    except Exception as e:
        return slug, "failed", str(e)[:300]


def main():
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(gen, s, v): s for s, v in VOICES}
        for f in as_completed(futures):
            slug, status, info = f.result()
            print(f"[{slug}] {status}: {info}", flush=True)


if __name__ == "__main__":
    main()
