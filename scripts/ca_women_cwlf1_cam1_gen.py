"""
CA Women CWL_F1 cam1 gen:
  Persona: CWL_F1 — Latina 45, East LA apartment courtyard
  Script: "I was number four hundred and twelve..." — social proof / deadline urgency
  6 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# CWL_F1 — Latina 45, East LA apartment courtyard, warm afternoon light
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:8c8fe788-89a6-4ccd-ae85-eea40988fb5e"
OUT = Path("outputs/ca_women_cwlf1_cam1")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes on lens from the first frame. Direct. Owning the number.\n"
            "BODY LANGUAGE: Still. Head level. A quiet settled confidence — she knows this fact cold.\n"
            "VOICE STYLE: Warm slightly husky 40s Latina. Plain California. Conversational. Not announcer.\n"
            "TONE: Matter-of-fact personal disclosure. She's stating her own fact. No drama.\n"
            "SPEED: ~2.3 wps. Even. Brief natural pause after 'twelve.'\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet conversational projection. NOT whispered. Every word distinct.\n\n"
            "EYES LOCK: Warm dark-brown eyes stay OPEN and on the lens throughout. Same eye color first to last frame.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "I was number four hundred and twelve. I know that because they told me when I called."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on lens. A slight quiet weight — the scale of it landing.\n"
            "BODY LANGUAGE: Still. The number settles on her as she says it.\n"
            "VOICE STYLE: Same warm husky voice. 'Four hundred and eleven' delivered plain, not dramatic.\n"
            "TONE: Documentary. Stating the count. The weight is in the number itself.\n"
            "SPEED: ~2.0 wps. Measured. Slight pause after 'eleven women.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Four hundred and eleven women had already come forward by the time I found this."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes direct on lens. This sentence is addressed to the viewer.\n"
            "BODY LANGUAGE: Still. Head level. 'Sexually abused' spoken without flinching.\n"
            "VOICE STYLE: Same warm voice. Plain and steady. Not whispered, not dramatized.\n"
            "TONE: Factual and precise. Naming what happened. Then the offer — same plain register.\n"
            "SPEED: ~2.4 wps. Even. Brief pause after 'prisons.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "All of them were sexually abused inside California women\'s prisons. All of them may qualify for significant potential compensation."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on lens. A slight inward pull — this is her own near-miss.\n"
            "BODY LANGUAGE: Still. A very faint weight on 'I almost wasn't.' No gesture.\n"
            "VOICE STYLE: Same warm voice. 'Didn't know how close' delivered with quiet honesty.\n"
            "TONE: Personal confession of almost missing it. Not sad — just honest.\n"
            "SPEED: ~2.0 wps. Slightly slower. Pause after 'one of them.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "I almost wasn\'t one of them because I didn\'t know how close the deadline was."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on lens. Level and still. Each phrase its own beat.\n"
            "BODY LANGUAGE: Completely still. 'No court' flat and final. No movement.\n"
            "VOICE STYLE: Same warm voice. Plain removal of obstacles, one at a time.\n"
            "TONE: Quiet reassurance from personal experience. Not a pitch.\n"
            "SPEED: ~2.2 wps. Brief natural pauses after 'confidential' and 'No court.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Completely private and confidential. No court. The check to find out takes less than a minute and costs nothing."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on lens. Still and direct. The invitation.\n"
            "BODY LANGUAGE: Completely still. A last quiet breath before 'Tap below.'\n"
            "VOICE STYLE: Same warm voice. 'What number you'd be' — plain and open.\n"
            "TONE: Quiet close. She's already in. She's inviting you to join.\n"
            "SPEED: ~2.0 wps. Slow. Pause after 'below.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm dark-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Tap below. Find out what number you\'d be."\n\n'
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
    print(f"CA Women CWL_F1 cam1 — Latina 45 (East LA courtyard) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
