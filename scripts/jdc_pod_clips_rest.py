"""Podcast monologues — clips 2+ for the 6 ready videos. Parallel on KIE Veo 3.1 Lite.

Rules baked in:
  - SOLO framing lock (no second person in shot) — kept the off-camera conversational gaze.
  - kid/child word and "sexually abused" NEVER in the same clip/generation (moderation).
Anchors rotate from each video's clip-1 (real_06 uses the solo _anchor_0).
Output: outputs/<slug>/clip{N}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

TAIL = ("\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
        "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks.")


def P(age, tone, dialogue, last):
    return f"""\
GAZE: Talking to someone just off-camera, conversational, a couple quick glances to the lens. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast-guest energy, subtle head movement, headphones on.
FRAMING: ONLY him in the shot — NO other person visible, NO second person, solo framing.
VOICE: man, {age}, conversational, grounded.
TONE: {tone}
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers. NO trailing words. NO additions. NO repetition. STOP after final word "{last}".

SPOKEN DIALOGUE (verbatim, stop after final word):
"{dialogue}"

After "{last}" he holds, glancing back to the person off-camera. NO further words.""" + TAIL


# (slug, age, [(clipname, anchor_idx, tone, dialogue, last), ...])
VIDEOS = [
    ("jdc_pod_agepower_h07", "late 30s", [
        ("clip2", 0, "Heavy, firm.", "Whatever happened in there? That's on him, not you. Period.", "Period"),
        ("clip3", 1, "Validating, gentle.", "You was just a kid. None of that was on you. None of it.", "it"),
        ("clip4", 2, "Grounded, informational.", "If you was sexually abused in Illinois juvie, you may qualify for significant compensation.", "compensation"),
        ("clip5", 0, "Quiet push.", "Free, two minutes. Quit blamin' that little kid you was. Go check.", "check"),
    ]),
    ("jdc_pod_cookstat_h08", "early 30s", [
        ("clip2", 0, "Weighty, credible.", "These was kids. Locked up, supposed to be protected.", "protected"),
        ("clip3", 1, "Firm.", "The staff sexually abused us instead. If that's where they had you, listen close.", "close"),
        ("clip4", 2, "Matter-of-fact close.", "Almost a thousand men already filed. You may qualify for significant compensation. Free, two minutes. Go see if you qualify.", "qualify"),
    ]),
    ("jdc_pod_theydont_h09", "late 20s", [
        ("clip2", 0, "Reassuring, knowing.", "You think you gotta stand up, say it in front of everybody? Nah. You don't.", "don't"),
        ("clip3", 1, "Low, real.", "It's confidential. No name. No face. I filed mine, quiet.", "quiet"),
        ("clip4", 2, "Insider, leaning in.", "Illinois is payin' for this right now, and you may qualify for significant compensation.", "compensation"),
        ("clip5", 3, "Defiant close.", "Free. Two minutes. They been bankin' on your silence. Not no more. Tap in.", "in"),
    ]),
    ("jdc_pod_moneyreveal_h06", "around 27", [
        ("clip2", 0, "Urgent, real.", "You may qualify for significant compensation. Could be life-changing.", "changing"),
        ("clip3", 0, "Direct.", "I already filed mine. You check it private, free, two minutes.", "minutes"),
        ("clip4", 0, "Push.", "That was you in there? Don't sleep. Go look right now.", "now"),
    ]),
    ("jdc_pod_barbershop_h08", "early 30s", [
        ("clip2", 0, "Quiet, personal.", "He sexually abused me in there. I buried it for years.", "years"),
        ("clip3", 1, "Casual.", "Went home, checked it. Two minutes. Nobody knew. Filed it.", "it"),
        ("clip4", 2, "Real, a little surprised.", "Now they sayin' I may qualify for significant compensation. Nobody was in my business.", "business"),
        ("clip5", 3, "Reassuring.", "You don't gotta say it out loud. Nowhere. Just you. Go look.", "look"),
    ]),
    ("jdc_pod_familymoney_h06", "around 27", [
        ("clip2", 0, "Sincere.", "If you was sexually abused in Illinois juvie, you may qualify for significant compensation.", "compensation"),
        ("clip3", 0, "Hopeful.", "That's a different life for you and yours. I filed mine quiet.", "quiet"),
        ("clip4", 0, "Sincere close.", "Check it free, private, two minutes. You owe it to your people. Go look.", "look"),
    ]),
]


def submit(slug, age, clipname, anchor_idx, tone, dialogue, last):
    out = Path(f"outputs/{slug}/{clipname}.mp4")
    if out.exists() and out.stat().st_size > 100_000:
        return f"{slug}/{clipname}", "skip", ""
    anchor = Path(f"outputs/{slug}/anchors/_anchor_{anchor_idx}.jpg")
    url = kie_upload(str(anchor))
    r = kie_generate_veo(prompt=P(age, tone, dialogue, last), aspect_ratio="9:16",
                         image_urls=[url, url], mode="FIRST_AND_LAST_FRAMES_2_VIDEO",
                         model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        return f"{slug}/{clipname}", "FAILED", str(r.get("raw"))[:200]
    kie_download(r["urls"][0], str(out))
    return f"{slug}/{clipname}", "success", ""


def main():
    jobs = []
    for slug, age, clips in VIDEOS:
        for clipname, ai, tone, dia, last in clips:
            jobs.append((slug, age, clipname, ai, tone, dia, last))
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(submit, *j): f"{j[0]}/{j[2]}" for j in jobs}
        for f in as_completed(futs):
            name = futs[f]
            try:
                n, status, info = f.result()
                print(f"[{n}] {status} {info}", flush=True)
            except Exception as e:
                print(f"[{name}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
