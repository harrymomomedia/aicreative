"""Tier-2 ads — clips 2+ (after clip 1), parallel on KIE Veo 3.1 Lite.

Ad 5 (stopscroll, persona 2):  clips 2,3
Ad 6 (secret, persona 3):      clips 2,3
Ad 7 (statshock, persona 1):   clips 2,3,4
Ad 8 (keptquiet, persona 1):   clips 2,3

Anchors = eyes-open, forward-gaze frames rotated from each ad's clip 1
(verified before filling the CLIPS table). Em-dashes stripped from spoken lines.
Neutral voice descriptors. Outputs: outputs/<slug>/clip{N}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

OUT = Path("outputs")
SS = OUT / "illinois_jdc_stopscroll_p02"   # persona 2
SE = OUT / "illinois_jdc_secret_p03"       # persona 3
ST = OUT / "illinois_jdc_statshock_p01"    # persona 1
KQ = OUT / "illinois_jdc_keptquiet_p01"    # persona 1

TAIL = (
    "\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
    "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks."
)

# ---------- Ad 5 — Pattern Interrupt (persona 2, confrontational) ----------
A5_C2 = """\
GAZE: Hard into the lens, locked, exclusionary. Warm dark-brown eyes, same color throughout, open.
BODY: Still, controlled, a single firm beat. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Direct, firm, factual — "and nobody else", then stating that survivors are getting paid. NOT salesy.
SPEED: ~2.4 words/sec, deliberate, beat between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "now".

SPOKEN DIALOGUE (verbatim, stop after final word):
"And nobody else. Survivors are getting paid right now."

After "now" he holds, hard eye contact. NO further words.""" + TAIL

A5_C3 = """\
GAZE: Direct into the lens, level, steady. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, late 20s, mid-to-low rough register.
TONE: Matter-of-fact close. NO emphasis on "free", NO upbeat lift, NO salesy inflection, NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "going".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"It's confidential. It's free. Tap the link before you keep going."

After "going" he holds briefly, calm eye contact. NO further words.""" + TAIL

# ---------- Ad 6 — The Secret You Never Told (persona 3, intimate) ----------
A6_C2 = """\
GAZE: Into the lens, soft, knowing solidarity. Warm dark-brown eyes, same color throughout, open.
BODY: Head still, slow blink, faint reassuring settle. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Quiet solidarity — "you're not the only one", survivors speaking up. Gentle, NOT performative.
SPEED: ~2.4 words/sec, slow, beat between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "now".

SPOKEN DIALOGUE (verbatim, stop after final word):
"You're not the only one. Survivors of Illinois juvie sexual abuse are speaking up now."

After "now" he holds, soft eye contact. NO further words.""" + TAIL

A6_C3 = """\
GAZE: Into the lens, gentle, reassuring. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, mid 30s, mature deeper register, weathered.
TONE: Reassuring close. NO salesy lift on "qualify", NO upbeat inflection, NO smile in the voice — gentle and private.
SPEED: ~2.4 words/sec, calm, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "qualify".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"A hundred percent confidential. Nobody finds out unless you want them to. Tap to see if you qualify."

After "qualify" he holds briefly, soft eye contact. NO further words.""" + TAIL

# ---------- Ad 7 — Stat Shock (persona 1, credible) ----------
A7_C2 = """\
GAZE: Direct into the lens, steady, grounded. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Grounded, weighty — stating the hard fact plainly. NOT hyped.
SPEED: ~2.4 words/sec, deliberate, clear.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "hall".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Every one of them sexually abused as kids, inside an Illinois juvenile hall."

After "hall" he holds, steady eye contact. NO further words.""" + TAIL

A7_C3 = """\
GAZE: Into the lens, steady, a flicker of anger at the betrayal. Warm dark-brown eyes, same color throughout, open.
BODY: Still, controlled, faint jaw tension. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Firm, the betrayal angle — "paid to protect them". Controlled, NOT pleading.
SPEED: ~2.4 words/sec, deliberate.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "them".

SPOKEN DIALOGUE (verbatim, stop after final word):
"Abused by the guards and staff who were paid to protect them."

After "them" he holds, steady eye contact. NO further words.""" + TAIL

A7_C4 = """\
GAZE: Direct into the lens, level, steady. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Matter-of-fact close. NO upbeat lift, NO salesy inflection on "fifteen seconds" or "qualify", NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "qualify".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"If you were one of them, you can still file. Privately. Fifteen seconds to see if you qualify."

After "qualify" he holds briefly, calm eye contact. NO further words.""" + TAIL

# ---------- Ad 8 — They Kept You Quiet (persona 1, outrage) ----------
A8_C2 = """\
GAZE: Into the lens, hard, then steadying into resolve. Warm dark-brown eyes, same color throughout, open.
BODY: Still, controlled, a single firm nod on "justice". No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Controlled outrage turning to resolve — "he was protecting himself, not you", then survivors getting justice. Firm.
SPEED: ~2.4 words/sec, deliberate, beats between sentences.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "justice".

SPOKEN DIALOGUE (verbatim, stop after final word):
"He was protecting himself. Not you. Now survivors are getting justice."

After "justice" he holds, steady eye contact. NO further words.""" + TAIL

A8_C3 = """\
GAZE: Direct into the lens, level, steady. Warm dark-brown eyes, same color throughout, open.
BODY: Still, composed, slow blink. No gestures.
VOICE: man, around 20, light-to-mid tenor, clear.
TONE: Matter-of-fact close. NO emphasis on "free", NO upbeat lift, NO salesy inflection, NO smile in the voice.
SPEED: ~2.4 words/sec, deliberate, even.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "qualify".

SPOKEN DIALOGUE (verbatim, stop after final word, delivered quietly without commercial inflection):
"Free, confidential, fifteen seconds. Tap to see if you qualify."

After "qualify" he holds briefly, calm eye contact. NO further words.""" + TAIL

# (slug, anchor, prompt, out) — anchor indices CONFIRMED after viewing extracted frames
CLIPS = [
    ("ss_clip2", SS / "anchors/_anchor_0.jpg", A5_C2, SS / "clip2.mp4"),
    ("ss_clip3", SS / "anchors/_anchor_2.jpg", A5_C3, SS / "clip3.mp4"),
    ("se_clip2", SE / "anchors/_anchor_0.jpg", A6_C2, SE / "clip2.mp4"),
    ("se_clip3", SE / "anchors/_anchor_1.jpg", A6_C3, SE / "clip3.mp4"),
    ("st_clip2", ST / "anchors/_anchor_0.jpg", A7_C2, ST / "clip2.mp4"),
    ("st_clip3", ST / "anchors/_anchor_1.jpg", A7_C3, ST / "clip3.mp4"),
    ("st_clip4", ST / "anchors/_anchor_2.jpg", A7_C4, ST / "clip4.mp4"),
    ("kq_clip2", KQ / "anchors/_anchor_0.jpg", A8_C2, KQ / "clip2.mp4"),
    ("kq_clip3", KQ / "anchors/_anchor_1.jpg", A8_C3, KQ / "clip3.mp4"),
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
