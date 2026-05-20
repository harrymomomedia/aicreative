"""Chowchilla white-woman (w05) ads — scripts E, D, A, C — Veo 3.1 Fast on Poyo.

Persona anchor: outputs/chowchilla_white_personas/reference/w05.png (weathered ash-blonde
mid-40s woman, country living room). Clip-1 anchor pattern + per-clip frame rotation.

Phases:
  test  — generate clip 1 of each ad (validate w05 identity + Chowchilla pronunciation +
          voice quality + no burned text) BEFORE committing to the rest.
  rest  — extract rotation frames from each ad's clip 1, generate clips 2..N.
  all   — test then rest.

Usage:
  .venv/bin/python scripts/chowchilla_w05_ads.py --phase test
  .venv/bin/python scripts/chowchilla_w05_ads.py --phase rest --ads E,D,A,C
"""
import argparse
import concurrent.futures
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import poyo_client

ROOT = pathlib.Path("/Users/harry/aicreative")
ANCHOR_SRC = ROOT / "outputs/chowchilla_white_personas/reference/w05.png"
ANCHOR_CACHE = ROOT / "outputs/chowchilla_white_personas/w05_anchor_url.txt"

# Each ad = ordered list of spoken-dialogue clips (~8s each, natural breaks).
SCRIPTS = {
    "E": [
        "Chowchilla. I don't even like saying the name out loud.",
        "For years that was my rule. Don't look back, don't dig it up.",
        "Then this article lands in front of me, and there it is, in plain words.",
        "women from the California prisons, significant potential compensation, for what the guards did.",
        "The sexual abuse. The thing I never told anybody.",
        "And I'm reading it thinking, that's me. That's a lot of us.",
        "There's a form. Short one. When you were there, what happened, nothing more.",
        "It stays confidential, just between you and them. I filled it out in the time it takes to make a sandwich.",
        "I'd written it off completely. Figured that window closed a long time ago. It hadn't.",
        "Press the button. See if you qualify.",
    ],
    "D": [
        "My sister called me on a Tuesday. She didn't even say hello, just, are you sitting down.",
        "She'd found an article about women from the California prisons,",
        "about significant potential compensation for what the guards did. The sexual abuse.",
        "And she knew. She always knew what Chowchilla really was for me.",
        "I went quiet on the phone, because there was my whole story, right there on the screen.",
        "Mine, and so many others'. She walked me through the form herself.",
        "When you were in, what they did, and that's it. And it all stays private.",
        "Couple minutes, done. I'd spent years certain it was too late for me to say anything.",
        "I was wrong. Go tap that button and see if you qualify.",
    ],
    "A": [
        "You want to know what's crazy? I'd gone years without letting myself even think about Chowchilla.",
        "Packed it away, locked it, moved on. Then a friend forwards me something, tells me to read it.",
        "And it's about women from the California prisons getting significant potential compensation for what the guards put us through.",
        "The sexual abuse. I had to read it twice, because they were describing my life.",
        "Not just mine. Half the women I knew in there.",
        "Turns out you fill out one little form. When you were inside, what was done to you.",
        "And it never leaves the attorneys, totally confidential. I did the whole thing before my coffee got cold.",
        "Whatever you've been telling yourself, that it's too late, that nobody cares.",
        "that's what I believed too, and it wasn't true. Hit that button, find out if you've got a case.",
    ],
    "C": [
        "If you ever spent time inside Chowchilla, give me thirty seconds.",
        "I know you probably did what I did. Buried it, told yourself it was over.",
        "But women who were in the California prisons can now qualify for significant potential compensation,",
        "for what those guards did to us. The sexual abuse.",
        "I'm not talking about strangers. I'm talking about you and me.",
        "All it is is a form. When you were locked up, what happened.",
        "and it's held in complete confidence, just between you and the lawyers.",
        "Took me two minutes, no exaggeration. And if a voice tells you it's too late, ignore it,",
        "because that voice lied to me for years. Tap the button. See if you qualify.",
    ],
}

TONES = {
    "E": "quiet, haunted, confessional — heavy and low, but she says every word clearly",
    "D": "warm but heavy, recounting a phone call that shook her",
    "A": "disbelieving at first, then leveling with you — honest and a little raw",
    "C": "direct and earnest, talking straight to one person who needs to hear it",
}

# Lines that read like a headline → guard against newscaster TTS.
NEWS_GUARD = (" SAME intimate quiet tone, NOT news-anchor, NOT informational, NOT energetic — "
             "she is just repeating what she read, in her own quiet voice.")


def build_prompt(line, tone):
    guard = NEWS_GUARD if ("California prison" in line or "compensation" in line) else ""
    return (
        "EYES: pale blue-grey eyes that stay the SAME pale blue-grey throughout (never brown, never dark, never green), "
        "OPEN and looking into the lens the whole time, natural slow blinks only, never half-closed or squinting. "
        "GAZE: steady eye contact into the lens, one small glance down and back up. "
        "BODY: weary, grounded, subtle head tilt and micro-movements, soft neutral mouth, NO smile. "
        "VOICE: tired, low, plainspoken American woman, late 40s, slightly weathered timbre, intimate and quiet. "
        f"TONE: {tone}.{guard} SPEED: ~2.3 words/sec, unhurried, conversational.\n"
        "AUDIO: clean close-mic selfie, quiet room, no music, no background voices, ONE speaker only.\n"
        "LOCKS: English only; say ONLY the SPOKEN DIALOGUE verbatim, in order, no fillers, no extra or "
        "trailing words, STOP after the final word; NO laughing, NO \"um\"/\"uh\", NO sniffing, NO "
        "hesitation sounds, NO breath words — just the clean spoken line; "
        "\"Chowchilla\" is pronounced \"Chow-CHILL-uh\"; "
        "absolutely NO on-screen text, captions, subtitles, or watermark.\n"
        f"SPOKEN DIALOGUE (verbatim, stop after final word): \"{line}\""
    )


def out_dir(ad):
    d = ROOT / f"outputs/chowchilla_w05_{ad.lower()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def anchor_url():
    return ANCHOR_CACHE.read_text().strip()


def gen_clip(ad, idx, anchor):
    """idx is 0-based. Writes clip{idx+1}.mp4. Skips if exists."""
    dest = out_dir(ad) / f"clip{idx+1}.mp4"
    if dest.exists() and dest.stat().st_size > 50_000:
        print(f"[{ad}{idx+1}] skip (exists)", flush=True)
        return ad, idx, str(dest)
    line = SCRIPTS[ad][idx]
    prompt = build_prompt(line, TONES[ad])
    t0 = time.time()
    print(f"[{ad}{idx+1}] submit", flush=True)
    try:
        res = poyo_client.generate_veo(
            prompt, image_urls=[anchor, anchor],
            aspect_ratio="9:16", resolution="720p",
            model="veo3.1-fast", generation_type="frame",
        )
    except Exception as e:
        print(f"[{ad}{idx+1}] EXC ({time.time()-t0:.0f}s): {e}", flush=True)
        return ad, idx, None
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{ad}{idx+1}] FAIL ({time.time()-t0:.0f}s): {res.get('raw')}", flush=True)
        return ad, idx, None
    poyo_client.download(res["urls"][0], str(dest))
    print(f"[{ad}{idx+1}] DONE ({time.time()-t0:.0f}s) → {dest}", flush=True)
    return ad, idx, str(dest)


def extract_rotation_frames(ad, n):
    """Pull n clean frames from clip1 at varied timestamps, upload, return list of URLs."""
    clip1 = out_dir(ad) / "clip1.mp4"
    times = [0.5, 1.8, 3.0, 4.2, 5.5, 6.8][:n]
    urls = []
    for i, t in enumerate(times):
        f = out_dir(ad) / f"_anchor_{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", str(clip1),
                        "-frames:v", "1", "-q:v", "2", str(f)],
                       capture_output=True, check=True)
        urls.append(poyo_client.upload_file(str(f)))
    print(f"[{ad}] {len(urls)} rotation anchors from clip1", flush=True)
    return urls


def run_phase(phase, ads, workers=8):
    base_anchor = anchor_url()

    if phase in ("test", "all"):
        print("=== PHASE test: clip 1 of each ad ===", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(gen_clip, ad, 0, base_anchor) for ad in ads]
            for f in concurrent.futures.as_completed(futs):
                f.result()

    if phase in ("rest", "all"):
        print("=== PHASE rest: clips 2..N ===", flush=True)
        # Build per-ad rotation anchors from each clip1 first (sequential, light).
        rotations = {}
        for ad in ads:
            if not (out_dir(ad) / "clip1.mp4").exists():
                print(f"[{ad}] no clip1 — run test phase first; skipping", flush=True)
                continue
            rotations[ad] = extract_rotation_frames(ad, 6)
        jobs = []
        for ad in ads:
            if ad not in rotations:
                continue
            for idx in range(1, len(SCRIPTS[ad])):
                anchor = rotations[ad][(idx - 1) % len(rotations[ad])]
                jobs.append((ad, idx, anchor))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(gen_clip, ad, idx, anchor) for ad, idx, anchor in jobs]
            for f in concurrent.futures.as_completed(futs):
                f.result()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["test", "rest", "all"], default="test")
    ap.add_argument("--ads", default="E,D,A,C")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    ads = [a.strip().upper() for a in args.ads.split(",") if a.strip()]
    run_phase(args.phase, ads, args.workers)
    print("\n=== summary ===", flush=True)
    for ad in ads:
        d = out_dir(ad)
        have = sorted(p.name for p in d.glob("clip*.mp4") if p.stat().st_size > 50_000)
        print(f"  {ad}: {len(have)}/{len(SCRIPTS[ad])} clips — {have}", flush=True)


if __name__ == "__main__":
    main()
