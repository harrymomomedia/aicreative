"""real_02 replacements — clip-1 of #3 (Number bomb -> real_01) and #8 (Scale money -> real_05).
No headphones, split-safe clip-1 (no 'sexually abused' + 'kid' in the same generation).
KIE Veo 3.1 Lite, i2v from the source host image. 9:16 720p.
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import upload_file as kie_upload, generate_veo as kie_generate_veo, download as kie_download

PERS = Path("outputs/jdc_podcast_personas")
TAIL = ("\nAUDIO CRITICAL: clearly audible at FULL conversational projection, NOT whispered, "
        "NOT muttered. Broadcast quality.\n\nNO on-screen text, NO captions, NO subtitles, NO watermarks.")


def P(age, tone, dialogue, last):
    return f"""\
GAZE: Talking to someone just off-camera, conversational, a couple quick glances to the lens. Warm dark-brown eyes, same color throughout, open.
BODY: Relaxed podcast-guest energy, subtle head movement. He is NOT wearing headphones — NO headphones anywhere, none on his head, none on his neck.
FRAMING: ONLY him in the shot — NO other person visible, solo framing.
VOICE: man, {age}, conversational, grounded.
TONE: {tone}
SPEED: ~2.4 words/sec, natural conversational rhythm.

DIALOGUE LOCK: ENGLISH only. NO fillers (NO "yeah", NO "mm-hmm"). NO trailing words. NO additions. NO repetition. STOP after final word "{last}".

SPOKEN DIALOGUE (verbatim, stop after final word):
"{dialogue}"

After "{last}" he holds, glancing back to the person off-camera. NO further words.""" + TAIL


JOBS = [
    ("jdc_pod_thousand_h01", PERS / "real_01.png", P("early 30s", "Real, heavy, the scale of it hitting him.",
        "Almost a thousand of us. For real. We was locked up in Illinois juvie.", "juvie")),
    ("jdc_pod_scalemoney_h05", PERS / "real_05.png", P("mid 30s", "Matter-of-fact, a touch of disbelief, real-talk money energy.",
        "This ain't a couple hundred dollars. Nah. Not for this.", "this")),
]


def submit(slug, src, prompt):
    out = Path(f"outputs/{slug}/clip1.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    url = kie_upload(str(src))
    r = kie_generate_veo(prompt=prompt, aspect_ratio="9:16", image_urls=[url, url],
                         mode="FIRST_AND_LAST_FRAMES_2_VIDEO", model="veo3_lite", resolution="720p")
    if r["status"] != "success" or not r.get("urls"):
        return slug, "FAILED", str(r.get("raw"))[:200]
    kie_download(r["urls"][0], str(out))
    return slug, "success", ""


def main():
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(submit, s, src, p): s for s, src, p in JOBS}
        for f in as_completed(futs):
            s = futs[f]
            try:
                slug, status, info = f.result()
                print(f"[{slug}] {status} {info}", flush=True)
            except Exception as e:
                print(f"[{s}] EXC: {e}", flush=True)


if __name__ == "__main__":
    main()
