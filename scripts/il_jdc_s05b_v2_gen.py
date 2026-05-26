"""
Script 05-B v2 — Regenerate all 7 clips with PORTRAIT anchor (9:16 native).
Uses Google Flow Veo 3.1 Lite via useapi.net.
"""
import os, sys, json, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/il_jdc_script05_b_v2")
OUT.mkdir(exist_ok=True)

ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:a08d887a-711c-4256-bc8e-28d159ce34b6"

# ── Clip definitions ────────────────────────────────────────────────────────
CLIPS = [
    {
        "n": 1,
        "duration": 8,
        "dialogue": "If you were in an Illinois juvenile detention center and somebody on staff did something to you sexually, stop scrolling.",
        "prompt": """GAZE: Eyes locked dead into the lens, unblinking, unwavering — he is calling someone out.
BODY LANGUAGE: Jaw set, brows slightly furrowed, completely still — coiled intensity.
VOICE STYLE: Low, steady, mid-30s Black man, gravel-tinged street-level delivery.
TONE: Hard confrontational hook. He KNOWS who is watching.
SPEED: ~2.3 words per second, each word lands.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection — NOT whispered, NOT soft. Clean foreground audio filling the mic.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy (never "ill-ih-NOY"). "juvenile" = JOO-veh-nile.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no improvisation. Speak ONLY the listed words in order. Stop speaking after the final word.

SPOKEN DIALOGUE: "If you were in an Illinois juvenile detention center and somebody on staff did something to you sexually, stop scrolling."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 2,
        "duration": 8,
        "dialogue": "I know you never told nobody. I didn't either, for 15 years.",
        "prompt": """GAZE: Starts briefly downcast — memory — then returns to lens, soft and steady.
BODY LANGUAGE: Slight exhale before speaking, shoulders drop — the guard comes down. A tiny head nod of shared truth.
VOICE STYLE: Quieter, intimate — same voice, lower register, almost private.
TONE: Vulnerable confession. He is WITH the viewer, not above them.
SPEED: ~2.0 words per second, unhurried — each phrase breathes.

AUDIO CRITICAL: Voice clear and audible despite soft tone. NOT inaudible — still fills the foreground.

PRONUNCIATION LOCK: "nobody" = NO-buh-dee (natural, not clipped).

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "I know you never told nobody. I didn't either, for 15 years."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 3,
        "duration": 8,
        "dialogue": "Then I found out Illinois changed the law. Guys from those facilities, guys like us are getting real compensation for what they did to us.",
        "prompt": """GAZE: Eyes stay on lens throughout. A slight lift — he found a way out.
BODY LANGUAGE: Very subtle lean forward as he gets to "compensation" — energy rises just a little, not performative.
VOICE STYLE: Same register as clip 2 but slight lift — factual, grounded hope.
TONE: Discovery. The shift from "I suffered alone" to "there is something we can do."
SPEED: ~2.4 words per second, steady.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy. "compensation" = COM-pen-SAY-shun (natural).

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "Then I found out Illinois changed the law. Guys from those facilities, guys like us are getting real compensation for what they did to us."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 4,
        "duration": 8,
        "dialogue": "I'm not talking about pennies. I'm talking about lawyers who already know what happened in there. They've seen the files. They know what those guards did.",
        "prompt": """GAZE: Direct, unwavering — he needs the viewer to feel the weight of this.
BODY LANGUAGE: Slow single nod on "lawyers who already know" — conviction, not performance. Head steady, jaw set.
VOICE STYLE: Measured, serious, credibility voice — this is real, not a pitch.
TONE: Gravity. He is vouching for these lawyers personally.
SPEED: ~2.5 words per second, steady rhythm with micro-pauses at periods.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "lawyers" = LAW-yers (2 syllables, natural). "guards" = GARDZ.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no trailing words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "I'm not talking about pennies. I'm talking about lawyers who already know what happened in there. They've seen the files. They know what those guards did."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 5,
        "duration": 8,
        "dialogue": "There's a form, two minutes, you don't talk to nobody in person, you type what happened, a lawyer tells you if you've got a case.",
        "prompt": """GAZE: Eyes on lens, steady — calm and clear.
BODY LANGUAGE: Relaxed, open — the relief of explaining something simple. Slight nod on "two minutes."
VOICE STYLE: Informational but still personal — friend walking you through steps.
TONE: Practical reassurance. No big ask, no risk.
SPEED: ~2.4 words per second, even pacing — list-like clarity.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "nobody" = NO-buh-dee. "lawyer" = LAW-yer.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no trailing words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "There's a form, two minutes, you don't talk to nobody in person, you type what happened, a lawyer tells you if you've got a case."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 6,
        "duration": 8,
        "dialogue": "No one calls your job. No one shows up at your house. Nobody in your life finds out unless you decide to tell them.",
        "prompt": """GAZE: Eyes on lens, soft and steady — the most reassuring moment of the video.
BODY LANGUAGE: Small deliberate shake of the head on "No one calls your job" — emphasizing the privacy. Calm, unhurried.
VOICE STYLE: Warm, low — the tone of someone who understands the fear.
TONE: Safety. He is lifting the biggest fear off the viewer's chest.
SPEED: ~2.0 words per second, slow and deliberate — let each "No one" land.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "No one calls your job. No one shows up at your house. Nobody in your life finds out unless you decide to tell them."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 7,
        "duration": 8,
        "dialogue": "The window on this is not open forever. Illinois set a deadline. I almost missed it. Don't miss it. Tap below. Two minutes. Free. Private. You've carried this long enough.",
        "prompt": """GAZE: Eyes on lens throughout. The look of someone who has been where you are.
BODY LANGUAGE: Very slight forward lean as urgency builds — then settles into stillness on "You've carried this long enough."
VOICE STYLE: Low urgency — NOT salesy, NOT energetic. Subdued gravitas. The final word of someone who made it through.
TONE: Quiet urgency bleeding into compassion. The CTA delivered like a personal favor, not an ad.
SPEED: ~2.5 wps for the deadline section, then SLOWER on the final phrase — "You've carried this long enough" has space.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. NO rising inflection on "Free" or "Private." NOT TV-ad voice. NOT commercial. Calm, private, like he is talking to one person.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy. "deadline" = DEAD-line (natural).

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no trailing words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "The window on this is not open forever. Illinois set a deadline. I almost missed it. Don't miss it. Tap below. Two minutes. Free. Private. You've carried this long enough."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
]


# ── Generation helpers ───────────────────────────────────────────────────────
def submit_clip(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: already exists ({out_path.stat().st_size//1024}KB), skipping")
        return n, str(out_path), "skipped"

    payload = {
        "prompt": clip["prompt"],
        "model": "veo-3.1-lite",
        "startImage": ANCHOR,
        "aspectRatio": "portrait",
        "duration": clip["duration"],
        "async": True,
        "captchaRetry": 5,
    }
    r = requests.post("https://api.useapi.net/v1/google-flow/videos",
                      headers=HEADERS, json=payload, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Submit clip{n} failed: {r.status_code} {r.text[:200]}")
    job_id = r.json().get("jobid")
    if not job_id:
        raise RuntimeError(f"clip{n} no jobid: {r.text[:200]}")
    print(f"  clip{n}: submitted → job {job_id}")
    return n, job_id, "submitted"


def poll_job(job_id, n, timeout=600, interval=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"https://api.useapi.net/v1/google-flow/jobs/{job_id}",
                         headers=HEADERS, timeout=30)
        if r.status_code != 200:
            time.sleep(interval)
            continue
        data = r.json()
        status = data.get("status", "")
        resp = data.get("response", {})

        if status == "completed":
            media = (resp.get("media") or [{}])
            video_url = media[0].get("videoUrl", "") if media else ""
            if video_url:
                return video_url
            raise RuntimeError(f"clip{n} completed but no videoUrl: {data}")
        elif status == "failed":
            raise RuntimeError(f"clip{n} FAILED: {data.get('error', data)}")
        else:
            pct = data.get("progressRatio", "?")
            eta = data.get("estimatedTimeToStartSeconds", "?")
            print(f"    clip{n}: {status} ({pct}) eta={eta}s …", flush=True)
            time.sleep(interval)
    raise TimeoutError(f"clip{n} timed out after {timeout}s")


def download_clip(url, n):
    out_path = OUT / f"clip{n}.mp4"
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    size = out_path.stat().st_size
    print(f"  clip{n}: downloaded → {size//1024}KB")
    return str(out_path)


def generate_clip(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: already exists, skipping")
        return n, str(out_path)

    _, job_id, status = submit_clip(clip)
    if status == "skipped":
        return n, str(out_path)

    video_url = poll_job(job_id, n)
    path = download_clip(video_url, n)
    return n, path


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating {len(CLIPS)} clips → {OUT}")
    print(f"Anchor: {ANCHOR[:60]}…\n")

    results = {}
    # Submit all in parallel (max 5 at once to stay under rate limits)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(generate_clip, c): c["n"] for c in CLIPS}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                n, path = fut.result()
                results[n] = path
                print(f"✓ clip{n} done: {path}")
            except Exception as e:
                print(f"✗ clip{n} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/{len(CLIPS)} clips")
    for n in sorted(results):
        print(f"  clip{n}: {results[n]}")
