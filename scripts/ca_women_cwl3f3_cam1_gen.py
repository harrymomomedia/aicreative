"""
CA Women CWL3_F3 cam1 gen:
  Persona: CWL3_F3 — Puerto Rican 43, living room sofa
  Script: "California needed your silence..." — cold accusatory/info angle
  6 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# CWL3_F3 — Puerto Rican 43, round face, caramel-brown, curly hair, living room sofa
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:efbedf99-4463-4692-9394-4705f458e2ad"
OUT = Path("outputs/ca_women_cwl3f3_cam1")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes locked on the lens from the first frame. Unflinching. A cold stillness.\n"
            "BODY LANGUAGE: Completely still. Jaw set. A slow breath before the first word. No movement.\n"
            "VOICE STYLE: Calm measured 40s Puerto Rican woman. Plain California. Quiet cold authority. Not announcer.\n"
            "TONE: Cold indictment. Stating a fact plainly — not angry, not sad. Each word lands like a verdict.\n"
            "SPEED: ~1.9 wps. Deliberate. Natural pause after 'silence' and after 'cooperation.'\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet projection. NOT whispered. Every word distinct.\n\n"
            "EYES LOCK: Warm brown eyes stay OPEN and on the lens throughout. Same eye color first to last frame.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "California needed your silence. Not your cooperation. Your silence. They got it. For decades."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes steady on lens. A slight forward weight as she arrives at the point.\n"
            "BODY LANGUAGE: Still. The faintest forward lean on 'dollar amount.' No gesture.\n"
            "VOICE STYLE: Same calm cold voice. 'Dollar amount attached to it' delivered plain and final.\n"
            "TONE: Quiet revelation. Not outrage — a cold fact being stated for the first time.\n"
            "SPEED: ~2.0 wps. Even. Slight pause after 'decided.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And now a court has decided that silence has a dollar amount attached to it."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes direct on lens. This sentence is addressed to one person.\n"
            "BODY LANGUAGE: Still. A very slight settle on 'sexually abused.' Head level.\n"
            "VOICE STYLE: Same cold calm voice. 'Sexually abused' spoken plain, not whispered, not dramatized.\n"
            "TONE: Precise and factual. Naming the act plainly as a legal qualifier.\n"
            "SPEED: ~2.0 wps. Even. Brief pause after 'prisons.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Women sexually abused inside California women\'s prisons may qualify for significant potential compensation."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on lens. Level. 'What the state already knows happened' lands with quiet weight.\n"
            "BODY LANGUAGE: Completely still. No movement. Each clause its own beat.\n"
            "VOICE STYLE: Same cold calm voice. 'What the state already knows' delivered with quiet certainty.\n"
            "TONE: Plain reframe. Removing the burden of proof. Not owed — known.\n"
            "SPEED: ~2.0 wps. Pause after 'prove.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Not because of what they can prove. Because of what the state already knows happened."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on lens. Direct and completely still. Each phrase a separate beat.\n"
            "BODY LANGUAGE: Absolutely still. Each statement flat and final — delivered like verdicts.\n"
            "VOICE STYLE: Same cold calm voice. 'No court.' 'No public record.' each its own silence after.\n"
            "TONE: Clean removal of fear. Not reassuring — factual. Stated plain.\n"
            "SPEED: ~1.5 wps. Very slow. Long natural pause after each phrase.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "No court. No public record. Private and confidential."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on lens. Still and direct. Final settled close.\n"
            "BODY LANGUAGE: Completely still. A last quiet breath before 'Tap below.'\n"
            "VOICE STYLE: Same cold calm voice. 'Collect what they owe you' flat and final.\n"
            "TONE: Quiet close. The information has been given. This is the door.\n"
            "SPEED: ~2.0 wps. Even. Pause after 'below.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Tap below. It takes 60 seconds to fill out the form. Collect what they owe you."\n\n'
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
    print(f"CA Women CWL3_F3 cam1 — Puerto Rican 43 (living room) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
