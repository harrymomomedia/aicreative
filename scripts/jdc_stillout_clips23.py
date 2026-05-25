"""Ad 3 (He's Still Out There) — clips 2 + 3, persona 2, parallel.

Clip 1 (done): "The staff member who sexually abused you in that juvenile
hall? He got away with it."

Clip 2: "Survivors are changing that right now. And getting compensated."
  → tone shifts from anger to righteous empowerment.
Clip 3: "Free to check. Confidential. Tap the link."
  → CTA, QUIET, NOT commercial (no emphasis on "Free", no salesy lift).

Rotated anchors from clip 1: _anchor_3 (clip2), _anchor_0 (clip3).
KIE Veo Lite 720p, short i2v prompts, parallel.

Output: outputs/illinois_jdc_stillout_p02/clip{2,3}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

ANCHOR_DIR = Path("outputs/illinois_jdc_stillout_p02/anchors")
OUT_DIR = Path("outputs/illinois_jdc_stillout_p02")

TAIL = (
    "\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
    "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks."
)

CLIP2_PROMPT = """\
GAZE: Direct into the phone camera, steady, a touch less hard than before — a shift toward resolve.
BODY: Still, composed, a single slow assured nod somewhere in the line. No hand gestures.
VOICE: Black man, late 20s, mid-to-low register.
TONE: Righteous turn — from anger to empowerment. Firm, resolute, "this is being made right." NOT salesy, NOT upbeat-commercial.
SPEED: ~2.4 words per second, deliberate, beat between the two sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "compensated".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Survivors are changing that right now. And getting compensated."

After "compensated" he holds, steady eye contact. NO further words.""" + TAIL

CLIP3_PROMPT = """\
GAZE: Direct into the phone camera, calm, level.
BODY: Still, composed, slow blink. No gestures.
VOICE: Black man, late 20s, mid-to-low register.
TONE: Quiet, matter-of-fact close — like a friend telling you something true. NOT a commercial, NOT a pitch. NO emphasis on "Free", NO salesy inflection, NO upbeat lift, NO smile in the voice.
SPEED: ~2.4 words per second, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "link".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"Free to check. Confidential. Tap the link."

After "link" he holds briefly, calm eye contact. NO further words.""" + TAIL

CLIPS = [
    ("clip2", ANCHOR_DIR / "_anchor_3.jpg", CLIP2_PROMPT, OUT_DIR / "clip2.mp4"),
    ("clip3", ANCHOR_DIR / "_anchor_0.jpg", CLIP3_PROMPT, OUT_DIR / "clip3.mp4"),
]


def submit_one(slug, anchor, prompt, out):
    print(f"[{slug}] uploading anchor {anchor.name}", flush=True)
    url = kie_upload(str(anchor))
    print(f"[{slug}] submitting (prompt {len(prompt)} chars)", flush=True)
    r = kie_generate_veo(
        prompt=prompt,
        aspect_ratio="9:16",
        image_urls=[url, url],
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
        model="veo3_lite",
        resolution="720p",
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "failed", str(r.get("raw"))[:300]
    kie_download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(submit_one, s, a, p, o): s for s, a, p, o in CLIPS}
        for f in as_completed(futures):
            s = futures[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
