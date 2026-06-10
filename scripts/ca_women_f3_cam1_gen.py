"""
CA Women (CCWF/CIW) — cam1 with CW_F3
Persona: CW_F3 — Latina 60yo, older sedan / parking lot, overcast
Script: C5-COLD — State Counting on Silence, Information Angle
11 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# CW_F3 — Latina 60, older sedan lot, navy fleece, deeply weathered, greying short hair
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:3ed8647d-a569-41e5-b697-58306628aeb1"
OUT = Path("outputs/ca_women_f3_cam1")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes locked into the lens from the first frame. Completely level.\n"
            "BODY LANGUAGE: Completely still. Head level. Jaw set. A slow breath before speaking.\n"
            "VOICE STYLE: Flat measured 60s Latina. Plain California. Quiet authority. Not announcer.\n"
            "TONE: Documentary. Stating a documented fact plainly — no drama, no sell.\n"
            "SPEED: ~2.3 wps. Even.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet projection. NOT whispered. Every word distinct.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout. Same eye color first to last frame.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "California settled a women\'s prison abuse case last year. Over a hundred million dollars."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes steady on lens. Direct. A quiet weight behind 'didn't know.'\n"
            "BODY LANGUAGE: Still. Slight settle on 'just didn't know in time.'\n"
            "VOICE STYLE: Same flat measured voice. 'Didn't know' delivered plain, not sad.\n"
            "TONE: Quiet information. The irony of it — not owed, just uninformed.\n"
            "SPEED: ~2.1 wps. Slight natural pause after 'disqualified.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "The women who got nothing were not disqualified. They just didn\'t know in time."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes direct on lens. A slight forward steadiness — naming the gap.\n"
            "BODY LANGUAGE: Still. Head level. Arms at sides.\n"
            "VOICE STYLE: Same flat voice. 'The part nobody tells you' clipped and certain.\n"
            "TONE: Plain exposure of a gap. Not outrage — just the record.\n"
            "SPEED: ~2.3 wps. Even.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "That is the part nobody tells you. The state is not going to call you. The facility is not going to send you a letter."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on lens. Level, carrying quiet certainty.\n"
            "BODY LANGUAGE: Still. No gesture. Just the words.\n"
            "VOICE STYLE: Same flat voice. 'Found out and came forward' plain and final.\n"
            "TONE: Documentary. How these cases were built — from women who acted, not a list.\n"
            "SPEED: ~2.2 wps. Even.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "The attorneys who built these cases did not have a list of names. They had women who found out and came forward on their own."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on lens. Direct. This sentence is addressed to one person.\n"
            "BODY LANGUAGE: Still. A very slight forward lean on 'something happened to you.'\n"
            "VOICE STYLE: Same flat voice, slight quieting on 'something happened to you.'\n"
            "TONE: Precise and personal. The conditional is real.\n"
            "SPEED: ~2.1 wps. Even. Natural pause after 'facility.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "If you were incarcerated at Chowchilla, Chino, or another California women\'s facility, and something happened to you."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on lens. Direct. Each example named flat and separate.\n"
            "BODY LANGUAGE: Still. 'A guard. A staff member.' each its own beat.\n"
            "VOICE STYLE: Same flat voice. 'Significant potential compensation' plain, not hyped.\n"
            "TONE: Specificity without drama. Naming who did it, naming what it means.\n"
            "SPEED: ~2.1 wps. Pause after each 'A guard.' and 'A staff member.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "A guard. A staff member. Someone in a position of authority. You may qualify for significant potential compensation from those same settlements."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on lens. Level. Removing each barrier one at a time.\n"
            "BODY LANGUAGE: Still. Each 'You don't need' flat and separate.\n"
            "VOICE STYLE: Same flat voice. 'You don't need' repeated — not emphatic, just plain.\n"
            "TONE: Simple removal of obstacles. No urgency. Just fact.\n"
            "SPEED: ~2.2 wps. Brief pause after each item.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You don\'t need records. You don\'t need proof. You don\'t need a previous attorney."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Eyes on lens. Still and direct.\n"
            "BODY LANGUAGE: Completely still. 'Completely private' with quiet emphasis.\n"
            "VOICE STYLE: Same flat voice. 'You only pay if you win' final and plain.\n"
            "TONE: Clean close on the terms. No drama. No surprise.\n"
            "SPEED: ~2.0 wps. Pause after 'court' and 'private.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You do not go to court. It is completely private. You only pay if you win."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Eyes on lens. A slight forward steadiness on 'before the window closes.'\n"
            "BODY LANGUAGE: Still. The faintest weight entering on 'window closes.'\n"
            "VOICE STYLE: Same flat voice. 'Moving right now' clipped and real.\n"
            "TONE: Quiet real urgency. Not hype. The clock is running — stated plain.\n"
            "SPEED: ~2.3 wps. Even.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "But you have to come forward before the window closes. The women who are already moving are moving right now."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 10,
        "prompt": (
            "GAZE: Eyes on lens. Level. 'Because they didn't know' lands flat and heavy.\n"
            "BODY LANGUAGE: Still. The slight weight of the final point settling.\n"
            "VOICE STYLE: Same flat voice. 'Because they didn't know' the quietest beat.\n"
            "TONE: The quiet tragedy of it. No drama — just the fact.\n"
            "SPEED: ~2.0 wps. Slow. Pause after 'nothing.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "The ones who wait past the deadline get nothing. Not because they didn\'t qualify. Because they didn\'t know."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 11,
        "prompt": (
            "GAZE: Eyes on lens. Still. Direct close.\n"
            "BODY LANGUAGE: Completely still. A final settled breath.\n"
            "VOICE STYLE: Same flat voice. 'Now you know' its own beat. 'Tap below' plain.\n"
            "TONE: Quiet close. The information has been given. The rest is up to her.\n"
            "SPEED: ~2.0 wps. Pause after 'Now you know.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Now you know. Tap below. The check is free and takes less than a minute."\n\n'
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
    print(f"CA Women F3 cam1 — CW_F3 (Sedan lot) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
