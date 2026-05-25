"""IL JDC 'First-Person Confession' ad (Script A) — persona 02, CLIP 1.

Persona 02 = West Side Chicago, 26, dark brown skin, low fade + full beard,
black puffer over grey hoodie, under the L. Guarded confession energy.

Short i2v prompt (persona + setting already in the anchor — only GAZE / BODY /
VOICE / TONE / SPEED + locks).

Anchor: outputs/illinois_jdc_ugc/personas_demographic/persona_02_westside_guarded.png
Output: outputs/illinois_jdc_confession_p02/clip1.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

ANCHOR = Path("outputs/illinois_jdc_ugc/personas_demographic/persona_02_westside_guarded.png")
OUT = Path("outputs/illinois_jdc_confession_p02/clip1.mp4")
OUT.parent.mkdir(parents=True, exist_ok=True)

PROMPT = """\
GAZE: Looks directly into the phone camera the whole clip; a brief downward
glance on "One of the guards" then back to the lens.

BODY: Head mostly still, slow natural blink, faint jaw tension. No hand
gestures. Subtle handheld float.

VOICE: Black man, late 20s, mid-to-low register, slightly rough, quiet.

TONE: Guarded, heavy, reluctant — a confession he's held in for years. NOT
performative, NOT acted.

SPEED: ~2.4 words per second. Slow, deliberate, real pauses between the
short sentences.

AUDIO CRITICAL: clearly audible at FULL conversational projection, like he's
speaking right into the phone mic. NOT whispered, NOT muttered. Broadcast
quality, fills the foreground.

PRONUNCIATION: "Saint Charles" = full word "Saint".

DIALOGUE LOCK: ENGLISH only. NO fillers (uh, um, like). NO trailing words. NO
additions. NO repetition. STOP after final word "guards".

SPOKEN DIALOGUE (verbatim, stop after final word):
"I was fifteen when it happened. Saint Charles. One of the guards."

After "guards" he holds, eyes on camera, a slow breath. NO further words.

NO on-screen text, NO captions, NO subtitles, NO watermarks.
"""


def main():
    print(f"Uploading anchor to KIE storage: {ANCHOR.name}", flush=True)
    url = kie_upload(str(ANCHOR))
    print(f"url: {url}", flush=True)
    print(f"Prompt length: {len(PROMPT)} chars", flush=True)
    print(f"Submitting KIE Veo 3.1 Lite 720p (FIRST_AND_LAST_FRAMES)…", flush=True)
    r = kie_generate_veo(
        prompt=PROMPT,
        aspect_ratio="9:16",
        image_urls=[url, url],
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
        model="veo3_lite",
        resolution="720p",
    )
    if r["status"] != "success" or not r.get("urls"):
        print(f"FAILED: {str(r.get('raw'))[:500]}", flush=True)
        return
    print(f"Downloading: {r['urls'][0]}", flush=True)
    kie_download(r["urls"][0], str(OUT))
    print(f"DONE → {OUT}", flush=True)


if __name__ == "__main__":
    main()
