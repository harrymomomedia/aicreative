"""IL JDC claymation explainer — FULL first-person survivor VO (Brian).

Voice: Brian - Deep, Resonant and Comforting (nPczCjzI2devNBz1zQrb), user-picked.
Tries eleven_v3 (expressive, supports [sighs]/[exhales] tags); if v3 isn't
enabled on the account, falls back to multilingual_v2 with a tag-stripped text.

Locked copy elements: explicit "sexual abuse", "significant potential
compensation", real IL facilities, confidential / lawyers-do-call, never-your-
fault. "St." spelled "Saint" so TTS doesn't read "Street".

Output: outputs/illinois_jdc_claymation/vo/survivor_brian.mp3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import tts

OUT = Path("outputs/illinois_jdc_claymation/vo/survivor_brian.mp3")
OUT.parent.mkdir(parents=True, exist_ok=True)
VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian

# eleven_v3 version (with emotion tags)
TEXT_V3 = (
    "When I was a kid, Illinois locked me up. And something happened in there "
    "I never told anybody. For years.\n"
    "[exhales] A guard sexually abused me. I buried it. Figured nobody would "
    "believe a kid like me.\n"
    "Then I found out the state already paid out millions. To people it happened "
    "to. People like me.\n"
    "If you did time at Saint Charles, Joliet, Harrisburg, Warrenville, or the "
    "Audy Home, and a guard or staff member sexually abused you, it counts.\n"
    "I wasn't the only one. Most of us stayed quiet for years. [softly] It wasn't "
    "your fault. And it's not too late.\n"
    "Checking took me two minutes. It's private. Only the lawyers see it. There's "
    "significant potential compensation for what they did.\n"
    "Tap the link. See if you qualify. [sighs] I just wish I'd known sooner."
)

# plain version (tags stripped) for the multilingual_v2 fallback
TEXT_PLAIN = (
    "When I was a kid, Illinois locked me up. And something happened in there "
    "I never told anybody. For years. "
    "A guard sexually abused me. I buried it. Figured nobody would believe a "
    "kid like me. "
    "Then I found out the state already paid out millions. To people it happened "
    "to. People like me. "
    "If you did time at Saint Charles, Joliet, Harrisburg, Warrenville, or the "
    "Audy Home, and a guard or staff member sexually abused you, it counts. "
    "I wasn't the only one. Most of us stayed quiet for years. It wasn't your "
    "fault. And it's not too late. "
    "Checking took me two minutes. It's private. Only the lawyers see it. There's "
    "significant potential compensation for what they did. "
    "Tap the link. See if you qualify. I just wish I'd known sooner."
)


def main():
    try:
        print("Trying eleven_v3 (expressive)...", flush=True)
        tts(text=TEXT_V3, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_v3", stability=0.4, similarity_boost=0.8,
            speed=0.95, output_format="mp3_44100_192")
        print("v3 OK", flush=True)
    except Exception as e:
        print(f"v3 failed ({str(e)[:160]}) — falling back to multilingual_v2", flush=True)
        tts(text=TEXT_PLAIN, voice_id=VOICE_ID, out_path=str(OUT),
            model_id="eleven_multilingual_v2", stability=0.45, similarity_boost=0.85,
            speed=0.95, output_format="mp3_44100_192")
        print("multilingual_v2 OK", flush=True)


if __name__ == "__main__":
    main()
