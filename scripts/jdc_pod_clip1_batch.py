"""Podcast monologue ads — clip 1 (opener) of the 7 remaining scripts, parallel on KIE Veo 3.1 Lite.
(#1 agepower/real_07 already done as the format proof.)

Conversational podcast-guest i2v off each host image. 9:16 720p. Neutral voice descriptors.
Output: outputs/<slug>/clip1.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

PERS = Path("outputs/jdc_podcast_personas")
TAIL = ("\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
        "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks.")


def prompt(age, tone, dialogue, lastword):
    return f"""\
GAZE: Talking to someone just off-camera to the side (a host in the room), natural and conversational, with a couple quick glances to the lens. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast-guest energy, subtle head movement, slight lean, talking with his hands a touch. Headphones on.
VOICE: man, {age}, conversational, grounded.
TONE: {tone}
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "{lastword}".

SPOKEN DIALOGUE (verbatim, stop after final word):
"{dialogue}"

After "{lastword}" he holds, glancing back to the person off-camera. NO further words.""" + TAIL


# (slug, host_png, prompt)
JOBS = [
    ("jdc_pod_cookstat_h08", "real_08.png", prompt(
        "early 30s", "Grounded, credible, a little stunned at the number he's sharing.",
        "One building. The Cook County juvenile center, in Chicago. A third of all these abuse cases came outta that one spot.",
        "spot")),
    ("jdc_pod_thousand_h02", "real_02.png", prompt(
        "late 20s", "Real, heavy, scale of it hitting him — outrage under the surface.",
        "Almost a thousand of us. For real. Locked up as kids in Illinois juvie, and the staff sexually abused us.",
        "us")),
    ("jdc_pod_theydont_h09", "real_09.png", prompt(
        "late 20s", "Lower voice, knowing, leaning in like he's putting you on to something.",
        "Real quick. They don't want you knowin' this. You was a kid in juvie, somebody on staff sexually abused you.",
        "you")),
    ("jdc_pod_moneyreveal_h06", "real_06.png", prompt(
        "around 27", "Direct, urgent, dead-serious, looking to draw you in.",
        "Illinois is payin' out for this. I'm dead serious. A guard or staff sexually abused you as a kid in juvie?",
        "juvie")),
    ("jdc_pod_barbershop_h08", "real_08.png", prompt(
        "early 30s", "Casual storytelling, relaxed, then quiet when it gets personal.",
        "Yo. Last week. Barbershop. Dude brings up the juvie lawsuits. I got real quiet. 'Cause that was me.",
        "me")),
    ("jdc_pod_scalemoney_h02", "real_02.png", prompt(
        "late 20s", "Matter-of-fact, a touch of disbelief, real-talk money energy.",
        "This ain't a couple hundred dollars. Nah. A staff member sexually abused you as a kid in Illinois juvie?",
        "juvie")),
    ("jdc_pod_familymoney_h06", "real_06.png", prompt(
        "around 27", "Sincere, hopeful, talking about what it could mean for his people.",
        "This the kind of money that change your whole family's situation. For real.",
        "real")),
]


def submit_one(slug, host, p):
    out = Path(f"outputs/{slug}/clip1.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 100_000:
        return slug, "skip", str(out)
    url = kie_upload(str(PERS / host))
    r = kie_generate_veo(prompt=p, aspect_ratio="9:16", image_urls=[url, url],
                         mode="FIRST_AND_LAST_FRAMES_2_VIDEO", model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:300]
    kie_download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    with ThreadPoolExecutor(max_workers=7) as ex:
        futs = {ex.submit(submit_one, s, h, p): s for s, h, p in JOBS}
        for f in as_completed(futs):
            s = futs[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status}: {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
