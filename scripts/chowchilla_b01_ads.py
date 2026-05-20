"""Chowchilla Black-woman (b01) ads — scripts D, E, C — Veo 3.1 Fast on KIE.

Persona anchor: outputs/chowchilla_black_personas/reference/b01.png (mid-40s Black woman,
afro puff w/ grey edges, grey sweatshirt, apartment living room). Clip-1 anchor pattern +
SMART per-clip frame rotation (eyes-open frames only, via OpenCV).

Lessons baked in from the w05 run:
  - Generate on KIE veo3_fast (Poyo was in a wide outage).
  - Em-dashes in dialogue cause Veo to insert names/words → all em-dashes pre-removed here.
  - Eye-color drift → explicit dark-brown eye-color lock in the prompt.
  - Blink/averted anchor seeds → select_clean_anchor_times() filters to eyes-open frontal frames.

Phases:
  test  — clip 1 of each ad (validate identity + pronunciation + voice + no burned text).
  rest  — pick clean anchors from each clip 1, generate clips 2..N.

Usage:
  .venv/bin/python scripts/chowchilla_b01_ads.py --phase test --ads D,E,C
  .venv/bin/python scripts/chowchilla_b01_ads.py --phase rest --ads D,E,C
"""
import argparse
import concurrent.futures
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path("/Users/harry/aicreative")
sys.path.insert(0, str(ROOT))
import kie_client

ANCHOR_SRC = ROOT / "outputs/chowchilla_black_personas/reference/b01.png"
EYE_COLOR = "warm dark-brown"

# Each ad = ordered ~8s clips. NO em-dashes in dialogue (they trigger Veo word/name inserts).
SCRIPTS = {
    "D": [
        "My daughter called me on a Sunday after church. Didn't even say hey, just, Mama, you sitting down?",
        "She'd found an article about women from the California prisons.",
        "About significant potential compensation for what the guards did. The sexual abuse.",
        "And she knew. She always knew what Chowchilla really did to me, even though I never told her all of it.",
        "I got quiet, because there was my whole story, right there on that little screen.",
        "Mine, and so many of ours. She filled the form out with me right there at the table.",
        "When you were in, what happened, and it all stays private.",
        "Couple minutes, that was it. I spent years thinking it was too late for me.",
        "I was wrong. Go on and tap that button, see if you qualify.",
    ],
    "E": [
        "Chowchilla. I don't even say that word out loud, most days.",
        "For years, that was the rule. Don't look back, don't dig none of it up.",
        "Then this article shows up in front of me, and there it is, plain as day.",
        "Women from the California prisons. Significant potential compensation. For what those guards did.",
        "The sexual abuse. The thing I never told a soul.",
        "And I'm sitting there like, that's me. That's a whole lot of us.",
        "There's a form. Short. When you were there, what happened, that's all.",
        "Stays confidential, just between you and them. Filled mine out in the time it takes to fix a plate.",
        "I'd written it off. Figured that door closed on me a long time ago. It didn't.",
        "Press the button. See if you qualify.",
    ],
    "C": [
        "If you spent any time inside Chowchilla, give me thirty seconds.",
        "I know you probably did what I did. Buried it, told yourself it was over and done.",
        "But women who were in the California prisons can qualify now for significant potential compensation,",
        "for what those guards did to us. The sexual abuse.",
        "I'm not talking about no strangers. I'm talking about me and you.",
        "It's a form. When you were locked up, what happened.",
        "And it's held in complete confidence, just between you and the lawyers.",
        "Took me two minutes, I'm not exaggerating. And that voice telling you it's too late?",
        "Don't listen. It lied to me for years. Tap the button. See if you qualify.",
    ],
}

TONES = {
    "D": "warm but heavy, a mother recounting a phone call that shook her",
    "E": "quiet, haunted, confessional — heavy and low, but she says every word clearly",
    "C": "direct and earnest, talking straight to one person who needs to hear it",
}

NEWS_GUARD = (" SAME intimate quiet tone, NOT news-anchor, NOT informational, NOT energetic — "
             "she is just repeating what she read, in her own quiet voice.")


def build_prompt(line, tone):
    guard = NEWS_GUARD if ("California prison" in line or "compensation" in line) else ""
    return (
        f"EYES: {EYE_COLOR} eyes that stay the SAME {EYE_COLOR} throughout (never lighter, never "
        "changing color), OPEN and looking into the lens the whole time, natural slow blinks only, "
        "never half-closed or squinting. "
        "GAZE: steady eye contact into the lens, one small glance down and back up. "
        "BODY: weary, grounded, subtle head tilt and micro-movements, soft neutral mouth, NO smile. "
        "VOICE: tired, low, plainspoken Black American woman, mid-40s, warm but weary timbre, "
        f"intimate and quiet. TONE: {tone}.{guard} SPEED: ~2.3 words/sec, unhurried, conversational.\n"
        "AUDIO: clean close-mic selfie, quiet room, no music, no background voices, ONE speaker only.\n"
        "LOCKS: English only; say ONLY the SPOKEN DIALOGUE verbatim, in order, no fillers, no extra or "
        "trailing words, STOP after the final word; NO laughing, NO \"um\"/\"uh\", NO sniffing, NO "
        "hesitation sounds, NO breath words — just the clean spoken line; "
        "\"Chowchilla\" is pronounced \"Chow-CHILL-uh\"; "
        "absolutely NO on-screen text, captions, subtitles, or watermark.\n"
        f"SPOKEN DIALOGUE (verbatim, stop after final word): \"{line}\""
    )


def out_dir(ad):
    d = ROOT / f"outputs/chowchilla_b01_{ad.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


_upload_cache = {}


def kie_upload(path):
    key = str(path)
    if key not in _upload_cache:
        _upload_cache[key] = kie_client.upload_file(str(path))
    return _upload_cache[key]


def gen_clip(ad, idx, anchor_url):
    """idx 0-based. Writes clip{idx+1}.mp4 via KIE veo3_fast IMAGE_2_VIDEO. Skips if exists."""
    dest = out_dir(ad) / f"clip{idx+1}.mp4"
    if dest.exists() and dest.stat().st_size > 50_000:
        print(f"[{ad}{idx+1}] skip (exists)", flush=True)
        return ad, idx, str(dest)
    prompt = build_prompt(SCRIPTS[ad][idx], TONES[ad])
    t0 = time.time()
    print(f"[{ad}{idx+1}] KIE submit", flush=True)
    try:
        res = kie_client.generate_veo(prompt, aspect_ratio="9:16", image_urls=[anchor_url],
                                      mode="IMAGE_2_VIDEO", model="veo3_fast", resolution="720p")
    except Exception as e:
        print(f"[{ad}{idx+1}] EXC ({time.time()-t0:.0f}s): {e}", flush=True)
        return ad, idx, None
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{ad}{idx+1}] FAIL ({time.time()-t0:.0f}s): {res.get('failMsg') or res.get('raw')}", flush=True)
        return ad, idx, None
    kie_client.download(res["urls"][0], str(dest))
    print(f"[{ad}{idx+1}] DONE ({time.time()-t0:.0f}s) → {dest}", flush=True)
    return ad, idx, str(dest)


def select_clean_anchor_times(clip1, n=6, sample_hz=5):
    """Return up to n well-spaced timestamps where a frontal face has >=2 eyes open
    (filters blinks / averted gaze). Falls back to fixed timestamps if cv2 unavailable."""
    try:
        import cv2
    except ImportError:
        return [0.5, 1.8, 3.0, 4.2, 5.5, 6.8][:n]
    cap = cv2.VideoCapture(str(clip1))
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or int(fps * 8)
    dur = total / fps
    face_c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_c = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    good, t = [], 0.3
    while t < dur - 0.2:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if ok:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_c.detectMultiScale(gray, 1.1, 5, minSize=(120, 120))
            if len(faces):
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                roi = gray[y:y + h // 2, x:x + w]
                if len(eye_c.detectMultiScale(roi, 1.1, 6)) >= 2:
                    good.append(round(t, 2))
        t += 1.0 / sample_hz
    cap.release()
    if not good:
        return [0.5, 1.8, 3.0, 4.2, 5.5, 6.8][:n]
    if len(good) <= n:
        return good
    idx = sorted({int(round(i * (len(good) - 1) / (n - 1))) for i in range(n)})
    return [good[i] for i in idx]


def rotation_anchor_urls(ad, n=6):
    """Extract n clean eyes-open frames from clip1, upload to KIE, return URLs."""
    clip1 = out_dir(ad) / "clip1.mp4"
    times = select_clean_anchor_times(clip1, n=n)
    urls = []
    for i, t in enumerate(times):
        f = out_dir(ad) / f"_anchor_{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(clip1),
                        "-frames:v", "1", "-q:v", "2", str(f)], capture_output=True, check=True)
        urls.append(kie_upload(f))
    print(f"[{ad}] {len(urls)} clean eyes-open anchors from clip1 at t={times}", flush=True)
    return urls


def run_phase(phase, ads, workers=4):
    if phase in ("test", "all"):
        print("=== PHASE test: clip 1 of each ad ===", flush=True)
        base = kie_upload(ANCHOR_SRC)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(gen_clip, ad, 0, base) for ad in ads]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    if phase in ("rest", "all"):
        print("=== PHASE rest: clips 2..N ===", flush=True)
        jobs = []
        for ad in ads:
            if not (out_dir(ad) / "clip1.mp4").exists():
                print(f"[{ad}] no clip1 — run test first; skipping", flush=True)
                continue
            anchors = rotation_anchor_urls(ad, 6)
            for idx in range(1, len(SCRIPTS[ad])):
                jobs.append((ad, idx, anchors[(idx - 1) % len(anchors)]))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(gen_clip, ad, idx, a) for ad, idx, a in jobs]
            for f in concurrent.futures.as_completed(futs):
                f.result()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["test", "rest", "all"], default="test")
    ap.add_argument("--ads", default="D,E,C")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    ads = [a.strip().upper() for a in args.ads.split(",") if a.strip()]
    run_phase(args.phase, ads, args.workers)
    print("\n=== summary ===", flush=True)
    for ad in ads:
        have = sorted((p.name for p in out_dir(ad).glob("clip*.mp4") if p.stat().st_size > 50_000),
                      key=lambda n: int(''.join(filter(str.isdigit, n))))
        print(f"  {ad}: {len(have)}/{len(SCRIPTS[ad])} — {have}", flush=True)


if __name__ == "__main__":
    main()
