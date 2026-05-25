"""Stage 1 re-rolls: remove headphones (prompt said 'headphones on' — that was the bug; host images
are clean). clip1 redos start from the source host IMAGE; clip 2+ re-rolls start from an existing
clean clip-1 anchor. Hard no-filler lock added. real_06 keeps neck headphones.
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

PERS = Path("outputs/jdc_podcast_personas")
TAIL = ("\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
        "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks.")


def P(age, tone, dialogue, last, hp):
    hp_line = {
        "none": "He is NOT wearing headphones — NO headphones anywhere, none on his head, none on his neck.",
        "neck": "Over-ear headphones resting around his neck (NOT on his ears), as in the reference.",
    }[hp]
    return f"""\
GAZE: Talking to someone just off-camera, conversational, a couple quick glances to the lens. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast-guest energy, subtle head movement. {hp_line}
FRAMING: ONLY him in the shot — NO other person visible, solo framing.
VOICE: man, {age}, conversational, grounded.
TONE: {tone}
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers (NO "yeah", NO "mm-hmm", NO "uh"). NO trailing words. NO additions. NO repetition. STOP after final word "{last}".

SPOKEN DIALOGUE (verbatim, stop after final word):
"{dialogue}"

After "{last}" he holds, glancing back to the person off-camera. NO further words.""" + TAIL


# (slug, clipname, source_path, dialogue, last, hp, age, tone)
JOBS = [
    # clip-1 redos from the source host image (no headphones)
    ("jdc_pod_agepower_h07", "clip1", PERS / "real_07.png", "late 30s",
     "Heavy, matter-of-fact, mid-conversation.",
     "You was twelve, thirteen years old. He was a grown man with a badge and the keys to your cell.", "cell", "none"),
    ("jdc_pod_barbershop_h08", "clip1", PERS / "real_08.png", "early 30s",
     "Casual storytelling, then quiet when it gets personal.",
     "Yo, last week, barbershop, dude brings up the juvie lawsuits. I got real quiet. 'Cause that was me.", "me", "none"),
    # clip 2+ re-rolls from existing clean anchors (no headphones)
    ("jdc_pod_cookstat_h08", "clip2", "outputs/jdc_pod_cookstat_h08/anchors/_anchor_0.jpg", "early 30s",
     "Weighty, credible.", "These was kids. Locked up, supposed to be protected.", "protected", "none"),
    ("jdc_pod_theydont_h09", "clip2", "outputs/jdc_pod_theydont_h09/anchors/_anchor_0.jpg", "late 20s",
     "Reassuring, knowing.", "You think you gotta stand up, say it in front of everybody? Nah. You don't.", "don't", "none"),
    ("jdc_pod_theydont_h09", "clip3", "outputs/jdc_pod_theydont_h09/anchors/_anchor_1.jpg", "late 20s",
     "Low, real.", "It's confidential. No name. No face. I filed mine, quiet.", "quiet", "none"),
    ("jdc_pod_theydont_h09", "clip4", "outputs/jdc_pod_theydont_h09/anchors/_anchor_2.jpg", "late 20s",
     "Insider, leaning in.", "Illinois is payin' for this right now, and you may qualify for significant compensation.", "compensation", "none"),
    ("jdc_pod_theydont_h09", "clip5", "outputs/jdc_pod_theydont_h09/anchors/_anchor_3.jpg", "late 20s",
     "Defiant close.", "Free. Two minutes. They been bankin' on your silence. Not no more. Tap in.", "in", "none"),
    # moneyreveal: keep NECK headphones, fix the broken dialogue (clip2 tripled, clip4 gibberish)
    ("jdc_pod_moneyreveal_h06", "clip2", "outputs/jdc_pod_moneyreveal_h06/anchors/_anchor_0.jpg", "around 27",
     "Urgent, real.", "You may qualify for significant compensation. Could be life changing.", "changing", "neck"),
    ("jdc_pod_moneyreveal_h06", "clip4", "outputs/jdc_pod_moneyreveal_h06/anchors/_anchor_0.jpg", "around 27",
     "Push.", "That was you in there? Don't sleep. Go look right now.", "now", "neck"),
]


def submit(slug, clipname, source, age, tone, dialogue, last, hp):
    out = Path(f"outputs/{slug}/{clipname}.mp4")
    url = kie_upload(str(source))
    r = kie_generate_veo(prompt=P(age, tone, dialogue, last, hp), aspect_ratio="9:16",
                         image_urls=[url, url], mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
                         model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        return f"{slug}/{clipname}", "FAILED", str(r.get("raw"))[:200]
    kie_download(r["urls"][0], str(out))
    return f"{slug}/{clipname}", "success", ""


def main():
    with ThreadPoolExecutor(max_workers=9) as ex:
        futs = {ex.submit(submit, s, c, src, age, tone, d, last, hp): f"{s}/{c}"
                for s, c, src, age, tone, d, last, hp in JOBS}
        for f in as_completed(futs):
            name = futs[f]
            try:
                n, status, info = f.result()
                print(f"[{n}] {status} {info}", flush=True)
            except Exception as e:
                print(f"[{name}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
