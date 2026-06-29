"""Depo Pixar Myth-buster — first-person female VO (ElevenLabs).

Voice: Black_F_49Y (LENRS9nvWdqPqUc8kYRq) — same voice as depo_claymation / depo_pixar so the
campaign's Pixar-style ads sound like the same woman. Tries eleven_v3 (expressive, [softly] tags);
falls back to multilingual_v2 with tags stripped if v3 isn't enabled for the voice.

Locked copy: MYTH-BUSTER register (knowing, gently challenging). Diagnosis-first: "meningioma"
+ "Depo" land early. "may qualify for significant compensation" (no owed/settlement/payout).
NO disclaimer lingo (feedback_no_disclaimer_lingo_in_copy). ~50s at ~2.4 wps.

Output: outputs/depo_pixar_myth/vo.mp3
"""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import tts

OUT = Path("outputs/depo_pixar_myth/vo.mp3"); OUT.parent.mkdir(parents=True, exist_ok=True)
VOICE_ID = "LENRS9nvWdqPqUc8kYRq"  # Black_F_49Y

TEXT_V3 = (
    "If you've got a meningioma and you took the Depo shot, let me guess what you're thinking, "
    "because I thought all of it too.\n"
    "You're thinking it was years ago. It's too late. [softly] It's not.\n"
    "You're thinking you can't afford a lawyer. It costs you nothing to find out.\n"
    "You're thinking you're not the type to sue anybody. Neither am I.\n"
    "But this isn't about that. It's about what they didn't tell us.\n"
    "Here's the deal. I have a meningioma, a brain tumor, and I was on that shot for a long time. "
    "Those two things are connected, and the company knew before I did.\n"
    "Checking is free, it's private, and you never step foot in a courtroom.\n"
    "[softly] So whatever reason you've got. I promise I had the same one. And I was wrong. Go see."
)
TEXT_PLAIN = re.sub(r"\[[^\]]+\]\s*", "", TEXT_V3)


def main():
    try:
        print("Trying eleven_v3...", flush=True)
        tts(text=TEXT_V3, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_v3", stability=0.4, similarity_boost=0.8)
        print(f"OK eleven_v3 -> {OUT}", flush=True)
    except Exception as e:
        print(f"v3 failed ({str(e)[:120]}) — falling back to multilingual_v2 (tags stripped)", flush=True)
        tts(text=TEXT_PLAIN, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_multilingual_v2", stability=0.5, similarity_boost=0.85)
        print(f"OK multilingual_v2 -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
