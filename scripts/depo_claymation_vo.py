"""Depo-Provera brain-meningioma CLAYMATION explainer — first-person female VO.

Voice: Black_F_49Y (LENRS9nvWdqPqUc8kYRq) — African-American female ~49, matches the persona
(Black woman ~45). Tries eleven_v3 (expressive, [sighs]/[softly] tags); falls back to
multilingual_v2 with tags stripped if v3 isn't enabled for the voice.

Locked copy: DIAGNOSIS-FIRST (brain tumor / meningioma leads, Depo is the link), explicit
"meningioma" + "Depo-Provera", "may qualify for significant compensation" (no owed/settlement/
payout), lawyers-do-call-but-confidential, "see if you qualify".

Output: outputs/depo_claymation/vo/survivor_f49.mp3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import tts

OUT = Path("outputs/depo_claymation/vo/survivor_f49.mp3")
OUT.parent.mkdir(parents=True, exist_ok=True)
VOICE_ID = "LENRS9nvWdqPqUc8kYRq"  # Black_F_49Y

TEXT_V3 = (
    "When the doctor said I had a brain tumor, everything went quiet.\n"
    "[sighs] A meningioma. And all I could think was, where did this come from?\n"
    "The one thing I'd done for years was the Depo-Provera shot. Every three months, like clockwork.\n"
    "Nobody ever warned me it could cause something like this.\n"
    "But I wasn't the only one. Thousands of women got the same diagnosis.\n"
    "[softly] There's a lawsuit now, and women like me may qualify for significant compensation.\n"
    "It's free and private to check. No court. An attorney handles everything.\n"
    "If you have a meningioma and you used Depo-Provera, tap below and see if you qualify."
)

TEXT_PLAIN = (
    "When the doctor said I had a brain tumor, everything went quiet. "
    "A meningioma. And all I could think was, where did this come from? "
    "The one thing I'd done for years was the Depo-Provera shot. Every three months, like clockwork. "
    "Nobody ever warned me it could cause something like this. "
    "But I wasn't the only one. Thousands of women got the same diagnosis. "
    "There's a lawsuit now, and women like me may qualify for significant compensation. "
    "It's free and private to check. No court. An attorney handles everything. "
    "If you have a meningioma and you used Depo-Provera, tap below and see if you qualify."
)


def main():
    try:
        print("Trying eleven_v3 (expressive)...", flush=True)
        tts(text=TEXT_V3, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_v3", stability=0.4, similarity_boost=0.8,
            speed=0.96, output_format="mp3_44100_192")
        print("v3 OK ->", OUT, flush=True)
    except Exception as e:
        print(f"v3 failed ({str(e)[:160]}) — falling back to multilingual_v2", flush=True)
        tts(text=TEXT_PLAIN, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_multilingual_v2", stability=0.45, similarity_boost=0.85,
            speed=0.96, output_format="mp3_44100_192")
        print("multilingual_v2 OK ->", OUT, flush=True)


if __name__ == "__main__":
    main()
