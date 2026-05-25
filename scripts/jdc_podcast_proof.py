"""Podcast-monologue FORMAT PROOF — script #1 (age/power) on host real_07.
Clip 1 only, to validate look/voice/pacing of the new conversational podcast format
before batching all 8. KIE Veo 3.1 Lite, i2v off the host image. 9:16 720p.
Output: outputs/jdc_pod_agepower_h07/clip1.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

ANCHOR = Path("outputs/jdc_podcast_personas/real_07.png")
OUT = Path("outputs/jdc_pod_agepower_h07/clip1.mp4")
OUT.parent.mkdir(parents=True, exist_ok=True)

PROMPT = """\
GAZE: Talking to someone just off-camera to the side (a host in the room), natural and conversational, with a couple quick glances to the lens. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast-guest energy, subtle head movement, slight lean in, talking with a touch of his hands. Over-ear headphones on.
VOICE: man, late 30s, conversational, grounded.
TONE: Real, heavy but matter-of-fact — telling a hard truth like he's mid-conversation, NOT performing, NOT announcing.
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "cell".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You was twelve, thirteen years old. He was a grown man with a badge and the keys to your cell."

After "cell" he holds, glancing back to the person off-camera. NO further words.

AUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, NOT muttered. Broadcast quality.

NO on-screen text, NO captions, NO subtitles, NO watermarks."""


def main():
    print(f"upload {ANCHOR.name}", flush=True)
    url = kie_upload(str(ANCHOR))
    print(f"submit veo3_lite ({len(PROMPT)} chars)", flush=True)
    r = kie_generate_veo(prompt=PROMPT, aspect_ratio="9:16", image_urls=[url, url],
                         mode="FIRST_AND_LAST_FRAMES_2_VIDEO", model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        print(f"FAILED: {str(r.get('raw'))[:300]}", flush=True); return
    kie_download(r["urls"][0], str(OUT))
    print(f"DONE -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
