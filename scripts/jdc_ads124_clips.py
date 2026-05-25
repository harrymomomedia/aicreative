"""Ads 1, 2, 4 — remaining clips (2+), all on ONE host (KIE Veo 3.1 Lite), parallel.

Ad 1 (Confession, persona 3 / 34):     clips 2,3,4,5
Ad 2 (Memory Trigger, persona 2 / 26): clips 2,3,4
Ad 4 (You Were a Kid, persona 1 / 20): clips 2,3

Clip 1 of each is already done. Short i2v prompts (persona/setting in the anchor).
Anchors = eyes-open, forward-gaze frames rotated from each ad's clip 1.
Em-dashes stripped from all spoken lines (Veo invents words at em-dashes).
Neutral voice descriptors (no racial term) — identity is carried by the anchor,
and every ad gets voice-unified via ElevenLabs at finalize anyway.

Output: outputs/illinois_jdc_<ad>/clip{N}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

OUT = Path("outputs")
CONF = OUT / "illinois_jdc_confession_p03"
MEM = OUT / "illinois_jdc_memorytrigger_p02"
KID = OUT / "illinois_jdc_youwereakid_p01"

TAIL = (
    "\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
    "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks."
)

# ---------- Ad 1 — Confession (persona 3, reflective/heavy, 34) ----------
A1_C2 = """\
GAZE: Into the phone lens, heavy, a slow downward blink. Warm dark-brown eyes, same color throughout, open.
BODY: Head still, faint jaw tension, slow breath. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Reflective, heavy, the weight of years of silence. Reluctant.
SPEED: ~2.4 words/sec, slow, real pause between the sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "years".

SPOKEN DIALOGUE (verbatim, stop after final word):
"I didn't tell a single person. For almost twenty years."

After "years" he holds, eyes on camera, a slow breath. NO further words.""" + TAIL

A1_C3 = """\
GAZE: Into the lens, a small lift of hope under the weight. Warm dark-brown eyes, same color throughout, open.
BODY: Still, a single slow nod somewhere in the line. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Subdued but lifting slightly — "I found out I could do something." Quiet resolve, NOT upbeat.
SPEED: ~2.4 words/sec, deliberate, beats between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "know".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Last month I found out I could do something about it. Quietly. No one had to know."

After "know" he holds, calm eye contact. NO further words.""" + TAIL

A1_C4 = """\
GAZE: Into the lens, steady, a flicker of connection. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Quiet realization — not alone. Steady, subdued, a touch of solidarity.
SPEED: ~2.4 words/sec, deliberate.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "one".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Turns out I'm nowhere near the only one."

After "one" he holds, eyes on camera. NO further words.""" + TAIL

A1_C5 = """\
GAZE: Direct into the lens, calm, level. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Quiet, matter-of-fact, like a friend telling you something true. NOT a pitch, NO emphasis on "free", NO upbeat lift, NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "free".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"If a guard or staff sexually abused you in an Illinois juvie, you can check too. It's free."

After "free" he holds briefly, calm eye contact. NO further words.""" + TAIL

# ---------- Ad 2 — Memory Trigger (persona 2, visceral/knowing, 26) ----------
A2_C2 = """\
GAZE: Locked on the lens, intense, knowing. Warm dark-brown eyes, same color throughout, open.
BODY: Very still, minimal movement, slow blink. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Visceral, knowing, empathetic-but-direct — naming what the viewer carries.
SPEED: ~2.4 words/sec, slow, weighted, pause between the sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "loud".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You remember exactly what he did. And you've never once said it out loud."

After "loud" he holds, eyes locked on camera. NO further words.""" + TAIL

A2_C3 = """\
GAZE: On the lens, softer now, steadier. Warm dark-brown eyes, same color throughout, open.
BODY: Still, a small reassuring settle. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Reassuring, quiet — lifting the pressure. Gentle, NOT salesy.
SPEED: ~2.4 words/sec, calm, beat between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "confidential".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You don't have to. It stays confidential."

After "confidential" he holds, calm eye contact. NO further words.""" + TAIL

A2_C4 = """\
GAZE: Direct into the lens, calm, level. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Quiet, matter-of-fact close. NOT a commercial, NO upbeat lift on "compensated" or "tap", NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "check".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"Survivors of Illinois juvenile sexual abuse are being compensated. Tap to check."

After "check" he holds briefly, calm eye contact. NO further words.""" + TAIL

# ---------- Ad 4 — You Were a Kid (persona 1, stark/righteous, 20) ----------
A4_C2 = """\
GAZE: Into the lens, steady, unflinching. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, a subtle firm nod. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Stark, righteous, matter-of-fact — stating a hard truth plainly. Firm.
SPEED: ~2.4 words/sec, deliberate, clear pause between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "survivors".

SPOKEN DIALOGUE (verbatim, stop after final word):
"That was a crime. And Illinois is paying survivors."

After "survivors" he holds, eyes on camera. NO further words.""" + TAIL

A4_C3 = """\
GAZE: Direct into the lens, calm, level. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Quiet, matter-of-fact close. NOT a commercial, NO emphasis on "free", NO upbeat lift, NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "link".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"Free, confidential, fifteen-second check. Tap the link."

After "link" he holds briefly, calm eye contact. NO further words.""" + TAIL

# (slug, anchor, prompt, out)
CLIPS = [
    ("conf_clip2", CONF / "anchors/_anchor_1.jpg", A1_C2, CONF / "clip2.mp4"),
    ("conf_clip3", CONF / "anchors/_anchor_4.jpg", A1_C3, CONF / "clip3.mp4"),
    ("conf_clip4", CONF / "anchors/_anchor_0.jpg", A1_C4, CONF / "clip4.mp4"),
    ("conf_clip5", CONF / "anchors/_anchor_3.jpg", A1_C5, CONF / "clip5.mp4"),
    ("mem_clip2",  MEM / "anchors/_anchor_0.jpg",  A2_C2, MEM / "clip2.mp4"),
    ("mem_clip3",  MEM / "anchors/_anchor_1.jpg",  A2_C3, MEM / "clip3.mp4"),
    ("mem_clip4",  MEM / "anchors/_anchor_0.jpg",  A2_C4, MEM / "clip4.mp4"),
    ("kid_clip2",  KID / "anchors/_anchor_1.jpg",  A4_C2, KID / "clip2.mp4"),
    ("kid_clip3",  KID / "anchors/_anchor_0.jpg",  A4_C3, KID / "clip3.mp4"),
]


def submit_one(slug, anchor, prompt, out):
    if out.exists() and out.stat().st_size > 100_000:
        return slug, "skip", f"{out} exists"
    print(f"[{slug}] upload {anchor.name}", flush=True)
    url = kie_upload(str(anchor))
    print(f"[{slug}] submit ({len(prompt)} chars)", flush=True)
    r = kie_generate_veo(
        prompt=prompt,
        aspect_ratio="9:16",
        image_urls=[url, url],
        mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
        model="veo3_lite",
        resolution="720p",
    )
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:300]
    kie_download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=9) as ex:
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
