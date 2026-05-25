"""Generate the 3 'winning-structure' announcer-style podcast videos, start to finish (clips only).
Register = DIRECT-TO-CAMERA announcer (addresses the viewer), NOT off-camera confession.
No headphones. clip1 from the 4K host image; clips 2-5 from eyes-open clip1 anchors (rotated).
Moderation-safe splits: 'sexual abuse' sits with facility names but NEVER with 'kid/juvenile'.

KIE Veo 3.1 Lite, FIRST_AND_LAST_FRAMES_2_VIDEO, 9:16 720p. Skip-if-exists (resumable).
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

TAIL = ("\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
        "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks.")


def P(age, tone, dialogue, last):
    """Announcer register — DIRECT eye contact with the lens (addressing the audience)."""
    return f"""\
GAZE: Talking DIRECTLY INTO the camera lens, addressing the viewer head-on, steady eye contact with a couple of natural blinks. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast energy, leaning slightly toward the mic, subtle head movement, occasional small hand gesture. He is NOT wearing headphones — NO headphones anywhere, none on his head, none on his neck.
FRAMING: ONLY him in the shot — NO other person visible, solo framing, seated at the podcast mic.
VOICE: man, {age}, confident conversational street cadence, grounded.
TONE: {tone}
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers (NO "yeah", NO "mm-hmm", NO "uh"). NO trailing words. NO additions. NO repetition. STOP after final word "{last}".

SPOKEN DIALOGUE (verbatim, stop after final word):
"{dialogue}"

After "{last}" he holds, still looking into the lens. NO further words.""" + TAIL


VIDEOS = {
    "jdc_pod_winnerA_h11": {
        "src": "outputs/jdc_podcast_personas/real_11_4k.png",
        "age": "early 30s",
        "tone": "Confident direct-to-camera, righteous 'I'm putting you on to something real' energy. Grounded, NOT salesy.",
        "clips": [
            "Hey yo, Illinois. This might be your shot at justice. For real.",
            "You went through sexual abuse while locked up in Cook County, Pere Marquette, Warrenville, or Kane County?",
            "You may qualify for significant compensation. No cap. You don't need paperwork, proof, or an old report.",
            "They reviewing cases right now. Most get handled without you ever stepping in court.",
            "Everything stays low-key and confidential. Takes less than a minute to check. Don't sleep on this.",
        ],
    },
    "jdc_pod_winnerB_h15": {
        "src": "outputs/jdc_podcast_personas/real_15_4k.png",
        "age": "late 20s",
        "tone": "Real-talk urgent peer, leaning in, direct to camera. Like he's telling you straight, no hype-man act.",
        "clips": [
            "Ayo, Illinois, real quick. This could be your shot at justice.",
            "A staff member sexually abused you while you was locked up in St. Charles, Harrisburg, or Cook County?",
            "You may qualify for significant compensation. Straight up. You don't need paperwork, no proof, no old report.",
            "They reviewing cases right now. Most get handled without you ever seeing a courtroom.",
            "It all stays private and confidential. Less than a minute to see if you qualify. Don't sleep on this one.",
        ],
    },
    "jdc_pod_winnerC_h14": {
        "src": "outputs/jdc_podcast_personas/real_14_4k.png",
        "age": "mid 30s",
        "tone": "Weathered, serious, grounded authority, direct to camera. Calm weight, every word lands.",
        "clips": [
            "Yo, Illinois, listen. This might be your shot at some real justice.",
            "You went through sexual abuse locked up in Kane County, Warrenville, or Cook County?",
            "You may qualify for significant compensation. No cap. Don't even worry about paperwork, proof, or an old report.",
            "They already reviewing cases right now. Most get handled without you ever stepping in court.",
            "Everything stays low-key, confidential. Takes under a minute to check. Don't sleep on it.",
        ],
    },
}


def last_word(s):
    import re
    toks = [t for t in re.findall(r"[A-Za-z']+", s)]
    return toks[-1] if toks else ""


def gen_clip(out_path, source_img, age, tone, dialogue):
    out = Path(out_path)
    if out.exists() and out.stat().st_size > 50000:
        return str(out), "cached", ""
    out.parent.mkdir(parents=True, exist_ok=True)
    url = kie_upload(str(source_img))
    prompt = P(age, tone, dialogue, last_word(dialogue))
    r = kie_generate_veo(prompt=prompt, aspect_ratio="9:16", image_urls=[url, url],
                         mode="FIRST_AND_LAST_FRAMES_2_VIDEO", model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        return str(out), "FAILED", str(r.get("raw"))[:200]
    kie_download(r["urls"][0], str(out))
    return str(out), "success", ""


def extract_anchors(slug):
    clip1 = f"outputs/{slug}/clip1.mp4"
    adir = f"outputs/{slug}/anchors"
    Path(adir).mkdir(parents=True, exist_ok=True)
    if list(Path(adir).glob("_anchor_*.jpg")):
        return
    subprocess.run([".venv/bin/python", "scripts/pick_clean_anchors.py", clip1,
                    "--out-dir", adir, "--n", "6", "--prefix", "_anchor"], check=False)


def main():
    only = sys.argv[1:] or list(VIDEOS.keys())
    # Wave 1: clip1 for each video (from the 4K source image), in parallel
    print("=== WAVE 1: clip1 (from 4K host image) ===", flush=True)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {}
        for slug in only:
            v = VIDEOS[slug]
            futs[ex.submit(gen_clip, f"outputs/{slug}/clip1.mp4", v["src"], v["age"], v["tone"], v["clips"][0])] = slug
        for f in as_completed(futs):
            slug = futs[f]
            try:
                p, st, info = f.result(); print(f"[{slug}/clip1] {st} {info}", flush=True)
            except Exception as e:
                print(f"[{slug}/clip1] EXC {e}", flush=True)

    # Extract eyes-open anchors from each clip1
    print("=== EXTRACT ANCHORS ===", flush=True)
    for slug in only:
        if Path(f"outputs/{slug}/clip1.mp4").exists():
            extract_anchors(slug)

    # Wave 2: clips 2-5 for each video, from rotated clip1 anchors
    print("=== WAVE 2: clips 2-5 (rotated clip1 anchors) ===", flush=True)
    jobs = []
    for slug in only:
        v = VIDEOS[slug]
        anchors = sorted(Path(f"outputs/{slug}/anchors").glob("_anchor_*.jpg"))
        if not anchors:
            print(f"[{slug}] NO ANCHORS — skipping clips 2-5", flush=True); continue
        for i in range(1, len(v["clips"])):           # clips 2..N
            anchor = anchors[(i - 1) % len(anchors)]   # rotate
            jobs.append((slug, i + 1, str(anchor), v["age"], v["tone"], v["clips"][i]))
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(gen_clip, f"outputs/{s}/clip{n}.mp4", a, age, tone, d): f"{s}/clip{n}"
                for (s, n, a, age, tone, d) in jobs}
        for f in as_completed(futs):
            name = futs[f]
            try:
                p, st, info = f.result(); print(f"[{name}] {st} {info}", flush=True)
            except Exception as e:
                print(f"[{name}] EXC {e}", flush=True)


if __name__ == "__main__":
    main()
