"""
IL JDC — Couch Persona | "Illinois settling quietly" script
11 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:5be727ed-24ad-4800-bd66-da4aeeec0263"
OUT = Path("outputs/il_jdc_couch")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes straight into the camera. Calm. Deliberate. Like he's about to tell you something real.\n"
            "BODY LANGUAGE: Seated on couch, leaning slightly forward, elbows on knees. Hands clasped. Head level. Still.\n"
            "VOICE STYLE: Low, measured, early 30s. Controlled. Not aggressive — just certain.\n"
            "TONE: Quiet revelation. The tone of someone dropping information the audience doesn't know yet.\n"
            "SPEED: ~1.9 wps. Slow and deliberate. Weight on 'quietly.'\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. NOT whispered. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the entire clip.\n\n"
            "CRITICAL — NO SMILE: Mouth flat and neutral. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "What if I told you Illinois has been settling these cases quietly. '
            'And most survivors don\'t even know they\'re entitled to be part of it."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on camera. Heavier now. Personal. He is naming a real thing.\n"
            "BODY LANGUAGE: Same couch position. Slight forward lean. Head level. Very still.\n"
            "VOICE STYLE: Same low voice. Slower — naming something serious.\n"
            "TONE: Heavy and plain. The weight of a specific truth.\n"
            "SPEED: ~1.8 wps. Deliberate pause after 'as a child.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "If you were in an Illinois juvenile facility as a child, '
            'and you were abused or neglected."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes straight on the camera. Urgent but controlled. Delivering a fact.\n"
            "BODY LANGUAGE: Seated on couch. Leans slightly more forward. Jaw set. Still.\n"
            "VOICE STYLE: Same low voice. Slightly more direct — the urgency beat.\n"
            "TONE: Matter-of-fact urgency. 'Right now' lands with weight.\n"
            "SPEED: ~2.1 wps. Steady and clear throughout.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Active legal claims are happening right now on behalf of survivors like you."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on camera. Direct. Delivering the consequence.\n"
            "BODY LANGUAGE: Seated on couch. Completely still. Head level. Hands clasped.\n"
            "VOICE STYLE: Same low voice. Flat and final — no inflection rise.\n"
            "TONE: The weight of a deadline. 'Period' lands hard and flat.\n"
            "SPEED: ~1.9 wps. Slight pause before 'Period.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "If you don\'t come forward before the deadline, '
            'you won\'t be included. Period."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on camera. Soft but steady. Reassuring.\n"
            "BODY LANGUAGE: Seated on couch. Slight lean back — relaxing slightly. Head level. Hands easy.\n"
            "VOICE STYLE: Same low voice. Fractionally softer — the reassurance beat.\n"
            "TONE: Quiet reassurance. 'Nobody finds out' lands like a promise.\n"
            "SPEED: ~2.0 wps. Even and unhurried.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Everything is completely confidential and private. '
            'Nobody in your life finds out you did this."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on camera. Practical. Stripping the intimidation away.\n"
            "BODY LANGUAGE: Seated on couch. Slight shrug energy — this is easy. Hands relaxed. Head level.\n"
            "VOICE STYLE: Same low voice. Plain and factual.\n"
            "TONE: Reducing the barrier. 'Sixty seconds' lands casual and certain.\n"
            "SPEED: ~2.1 wps. Even. 'Sixty seconds' delivered flat.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And the process couldn\'t be simpler. '
            'You just fill out a form. Sixty seconds."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on camera. Calm and direct. Just facts.\n"
            "BODY LANGUAGE: Seated on couch. Completely still. Head level. Hands in lap.\n"
            "VOICE STYLE: Same low voice. Flat and practical.\n"
            "TONE: Plain as a fact. No emphasis. 'No cost unless they win for you' delivered evenly.\n"
            "SPEED: ~2.0 wps. Even delivery throughout.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "A legal team reviews it immediately and tells you if you qualify."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Eyes on camera. Steady and plain.\n"
            "BODY LANGUAGE: Seated on couch. Still. Head level. Arms relaxed.\n"
            "VOICE STYLE: Same low voice. Flat and matter-of-fact.\n"
            "TONE: No sales pitch. Just a simple fact. 'Unless they win for you' plain and final.\n"
            "SPEED: ~1.9 wps. Even and unhurried.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "No cost unless they win for you."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Eyes on camera. Heaviest, most direct look of the ad. Delivering urgency.\n"
            "BODY LANGUAGE: Seated on couch. Leans slightly forward again. Jaw set. Completely still.\n"
            "VOICE STYLE: Same low voice. Slightly heavier — the clock is running.\n"
            "TONE: Real urgency without panic. 'Getting closer every single day' lands with weight.\n"
            "SPEED: ~1.8 wps. Slow and deliberate. Each phrase its own beat.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "The deadline is real. It is not flexible. '
            'And it is getting closer every single day."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 10,
        "prompt": (
            "GAZE: Eyes on camera. Direct. The CTA — talking to one person.\n"
            "BODY LANGUAGE: Seated on couch. Still. Head level. Hands calm.\n"
            "VOICE STYLE: Same low voice. Slightly more direct on 'right now.'\n"
            "TONE: Calm command. 'Right now' has weight but no panic.\n"
            "SPEED: ~2.0 wps. Even and clear.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Tap below right now. Just fill out the form. '
            'Make sure you don\'t get left out."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
]


def poll(job_id, n, timeout=600, interval=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(
            f"https://api.useapi.net/v1/google-flow/jobs/{job_id}",
            headers=HEADERS, timeout=30,
        )
        if r.status_code != 200:
            time.sleep(interval)
            continue
        data = r.json()
        status = data.get("status", "")
        if status == "completed":
            media = data.get("response", {}).get("media") or [{}]
            url = media[0].get("videoUrl", "") if media else ""
            if url:
                return url
            raise RuntimeError(f"clip{n}: completed but no videoUrl — {data}")
        elif status == "failed":
            raise RuntimeError(f"clip{n} FAILED: {data}")
        pct = data.get("progressRatio", "?")
        print(f"    clip{n}: {status} ({pct}) …", flush=True)
        time.sleep(interval)
    raise TimeoutError(f"clip{n} timeout after {timeout}s")


def gen(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: exists ({out_path.stat().st_size // 1024}KB), skipping")
        return n, str(out_path)

    payload = {
        "prompt": clip["prompt"],
        "model": "veo-3.1-lite",
        "startImage": ANCHOR,
        "endImage": ANCHOR,
        "aspectRatio": "portrait",
        "duration": 8,
        "async": True,
        "captchaRetry": 5,
    }
    r = requests.post(
        "https://api.useapi.net/v1/google-flow/videos",
        headers=HEADERS, json=payload, timeout=60,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Submit clip{n}: {r.status_code} {r.text[:300]}")
    job_id = r.json().get("jobid")
    print(f"  clip{n}: submitted {job_id[:55]}…", flush=True)

    url = poll(job_id, n)
    r2 = requests.get(url, timeout=120, stream=True)
    r2.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r2.iter_content(65536):
            f.write(chunk)
    print(f"  clip{n}: saved {out_path.stat().st_size // 1024}KB")
    return n, str(out_path)


if __name__ == "__main__":
    print(f"IL JDC — Couch Persona | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(gen, c): c["n"] for c in CLIPS}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                n, path = fut.result()
                results[n] = path
                print(f"✓ clip{n} done")
            except Exception as e:
                print(f"✗ clip{n} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/{len(CLIPS)}")
    for n in sorted(results):
        print(f"  clip{n}: {results[n]}")
