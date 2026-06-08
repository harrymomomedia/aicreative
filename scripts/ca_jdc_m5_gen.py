"""
CA JDC — Persona M5 (Urban Rooftop) | "You Were a Kid" script
8 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# persona_M5_v3 — urban rooftop, 33yo, low fade, light stubble, dark jacket
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:4bcd974e-ef12-4b0f-9e1c-ae3161bfef03"
OUT = Path("outputs/ca_jdc_m5")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes locked directly into the lens. Still. Calm. Holding the viewer from the first frame.\n"
            "BODY LANGUAGE: Standing still. Head level, maybe a slight tilt down at the start as if gathering weight, then leveling. Arms at sides. No movement.\n"
            "VOICE STYLE: Low, early 30s, plain. NOT a narrator. Like talking directly to one person in private.\n"
            "TONE: Quiet gravity. Each phrase lands separately with space between — like placing something heavy down gently.\n"
            "SPEED: ~1.6 wps. Very slow and deliberate. Silence between phrases.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet projection. NOT whispered. NOT announcer-voiced. Clean foreground voice.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and looking DIRECTLY into the lens throughout. Never close. Never drift.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You were a kid. Maybe twelve. Maybe fourteen. Locked up for something small."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on camera. Jaw set. Delivering this plain — not dramatic, not emotional. Just naming it.\n"
            "BODY LANGUAGE: Standing completely still. Head level. Slight tension in the jaw. Arms at sides.\n"
            "VOICE STYLE: Same low plain voice. Controlled. Each word gets equal weight — no word is emphasized over another.\n"
            "TONE: Quiet indictment. Not angry. Not emotional. Just naming a documented truth.\n"
            "SPEED: ~2.0 wps. Even throughout.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And someone who was supposed to be in charge of you used that to sexually abuse you. That was never supposed to happen."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes on camera. Softer. Like remembering something that was buried.\n"
            "BODY LANGUAGE: Standing still. A very slight inward settle — not a collapse, just a breath drawn in. Head level.\n"
            "VOICE STYLE: Same low plain voice. Quieter on this line. The words come slower.\n"
            "TONE: The quiet of after. Suppression named, not dramatized.\n"
            "SPEED: ~1.8 wps. Slower than clip 2. Each word its own space.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT whispered. NOT announcer-voiced. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And when it was over, you didn\'t call it what it was."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on camera. Direct. Explaining, not accusing — just stating the logic of silence.\n"
            "BODY LANGUAGE: Standing still. Head level. Arms at sides. No movement.\n"
            "VOICE STYLE: Same low plain voice. Factual. Removing all judgment from the silence.\n"
            "TONE: Explaining the math of staying quiet. Not sad — just plain and honest.\n"
            "SPEED: ~2.0 wps. Even, unhurried.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Because you were in a place where calling it what it was cost you more time."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on camera. The pivot. Calm certainty — not triumph, just truth.\n"
            "BODY LANGUAGE: Standing still. Very slight forward settle on the first 'abuse.' Head level. Arms at sides.\n"
            "VOICE STYLE: Same low plain voice. 'But it was abuse' — plain, firm, unhurried. Repeat of 'was abuse' lands slightly heavier.\n"
            "TONE: Absolution through plain truth. NOT dramatic. NOT emotional. Just a fact being stated for the first time out loud.\n"
            "SPEED: ~1.8 wps. Slower on 'But it was abuse.' Even on the rest.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "But it was abuse. What they did to you, as a child, in a California juvenile facility, was abuse."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on camera. Head lifts slightly. Pivot to present — facts, not emotion.\n"
            "BODY LANGUAGE: Standing still. Very slight head lift on 'And right now.' Arms at sides.\n"
            "VOICE STYLE: Same low plain voice. 'California is being sued' — plain statement of fact, NOT triumphant. 'Settling these cases' flat.\n"
            "TONE: Factual present. Not a reveal — just what is happening right now.\n"
            "SPEED: ~2.0 wps. Even throughout. Short natural pause after 'sued.'\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And right now, California is being sued. Hundreds of survivors have come forward. The state is settling these cases."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on camera. Direct and calm. Removing every obstacle one by one.\n"
            "BODY LANGUAGE: Standing still. Head level. Arms at sides. Completely still.\n"
            "VOICE STYLE: Same low plain voice. 'Zero' beats delivered flat — NOT emphatic, NOT punchy. Just plain facts.\n"
            "TONE: Quiet removal of barriers. NOT a sales pitch. Just stating what is and isn't required.\n"
            "SPEED: ~2.0 wps. Even. A very brief natural pause before each 'Zero' beat.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You may be owed significant potential compensation. Zero proof from back then. Zero police reports. Zero contact with anyone from that facility."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Eyes on camera. The final beat — a slight softening. Still direct, but the weight lifts fractionally.\n"
            "BODY LANGUAGE: Standing still. Head level. Arms at sides. On 'You were a kid' — very slight nod, almost imperceptible.\n"
            "VOICE STYLE: Same low plain voice. Punchy and short on 'Private. Free. One form.' Then slows on 'You were a kid. You don't have to carry this the same way anymore.'\n"
            "TONE: Release. The CTA is not urgency — it is setting something down. NOT salesy, NOT energetic. Quiet closing.\n"
            "SPEED: ~2.2 wps on the first beats (Private. Free.), then ~1.6 wps on the final two sentences.\n\n"
            "AUDIO CRITICAL: FULL projection. NOT announcer-voiced. ZERO fillers. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout.\n\n"
            "CRITICAL — NO SMILE: ZERO smile. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Private. Free. One form. 60 seconds. Tap below. You were a kid. You don\'t have to carry this the same way anymore."\n\n'
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
            raise RuntimeError(f"clip{n} FAILED: {data.get('error', data)}")
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
        headers=HEADERS, json=payload, timeout=120,
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
    print(f"CA JDC — Persona M5 (Rooftop) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
