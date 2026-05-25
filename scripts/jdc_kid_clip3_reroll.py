"""Re-roll Ad 4 (You Were a Kid) clip 3 — the CTA clip came out with a broad SMILE,
which reads commercial/wrong on a sexual-abuse CTA. Regenerate with a hard VISUAL
no-smile lock (the prior prompt only said "no smile in the VOICE"). Persona 1, KIE Veo Lite.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

ANCHOR = Path("outputs/illinois_jdc_youwereakid_p01/anchors/_anchor_1.jpg")  # verified forward, neutral
OUT = Path("outputs/illinois_jdc_youwereakid_p01/clip3.mp4")

PROMPT = """\
GAZE: Direct into the lens, calm, level, serious. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
MOUTH: stays in a soft neutral line the ENTIRE clip — ZERO smile, NO teeth, NO grin, somber and serious throughout.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Quiet, somber, matter-of-fact close. NOT a commercial, NO emphasis on "free", NO upbeat lift, NO smile in the voice, NO brightness.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "link".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly and seriously without commercial inflection):
"Free, confidential, fifteen-second check. Tap the link."

After "link" he holds briefly, calm serious eye contact, NO smile. NO further words.

AUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, NOT muttered. Broadcast quality.

NO on-screen text, NO captions, NO subtitles, NO watermarks."""


def main():
    print(f"upload {ANCHOR.name}", flush=True)
    url = kie_upload(str(ANCHOR))
    print(f"submit ({len(PROMPT)} chars)", flush=True)
    r = kie_generate_veo(prompt=PROMPT, aspect_ratio="9:16", image_urls=[url, url],
                         mode="FIRST_AND_LAST_FRAMES_2_VIDEO", model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        print(f"FAILED: {str(r.get('raw'))[:300]}", flush=True); return
    kie_download(r["urls"][0], str(OUT))
    print(f"DONE -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
