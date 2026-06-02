"""
IL JDC V2 — Persona S v1 (male 41, dark brown, full beard, white tee, driver seat)
11 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:ee38a59d-640e-42fa-9bbe-0c50c0ad51b0"
OUT = Path("outputs/il_jdc_v2_s")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes on the dash camera. Direct, steady. Like he's telling someone something important.\n"
            "BODY LANGUAGE: Seated in driver seat. Hand resting on wheel. Head level. Still.\n"
            "VOICE STYLE: Low, measured, early 40s. Calm authority.\n"
            "TONE: Informational. Dropping a fact someone needs to hear.\n"
            "SPEED: ~2.0 wps. Deliberate. Weight on 'recently changed.'\n\n"
            "AUDIO CRITICAL: FULL conversational projection. NOT whispered. ZERO fillers. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Most people don\'t realize that the laws for Illinois juvenile center '
            'abuse claims recently changed."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on the dash camera. Calm and direct. Letting the information settle.\n"
            "BODY LANGUAGE: Same driver seat. Hand on wheel. Head level. Completely still.\n"
            "VOICE STYLE: Same low voice. Steady.\n"
            "TONE: Quiet revelation. 'Even if it happened decades ago' lands with weight.\n"
            "SPEED: ~1.9 wps. 'Even if it happened decades ago' slow and plain.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: compensation = com-pen-SAY-shun.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "You might actually be eligible for significant potential compensation. '
            'Even if it happened decades ago."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes on the dash camera. Heavier now. He is naming a personal truth.\n"
            "BODY LANGUAGE: Same driver seat. Both hands loose. Head level. Still. Very grounded.\n"
            "VOICE STYLE: Same low voice. Weight on every word.\n"
            "TONE: Plain and heavy. No drama — just the truth delivered straight.\n"
            "SPEED: ~2.0 wps. Brief pause after 'juvenile center.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the entire clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I was just a kid when I went into that Illinois juvenile center. '
            'A staff member abused me in there."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on the dash camera. Flat. The weight of a buried thing.\n"
            "BODY LANGUAGE: Same driver seat. Hand on wheel. Head level. Leaning slightly back. Still.\n"
            "VOICE STYLE: Same low voice. Quieter and flat.\n"
            "TONE: The flatness of something kept locked away. Each phrase its own breath.\n"
            "SPEED: ~1.8 wps. Slow. 'Closed for good' lands like a lid coming down.\n\n"
            "AUDIO CRITICAL: CLEARLY AUDIBLE despite quiet tone. NOT inaudible. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I buried it. Told myself that chapter was closed for good."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on the dash camera. A slight controlled lift — something opening.\n"
            "BODY LANGUAGE: Same driver seat. Slight forward lean. Head level. One hand on wheel.\n"
            "VOICE STYLE: Same low voice, fractionally warmer.\n"
            "TONE: The pivot. Quiet certainty. 'Actually paying' lands as plain fact.\n"
            "SPEED: ~2.1 wps. 'Significant potential compensation' delivered evenly.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO non-verbal sounds. ONLY exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. compensation = com-pen-SAY-shun.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the entire clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Then I found out Illinois is actually paying significant potential '
            'compensation to guys this happened to. Right now."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on the dash camera. Steady. Naming a number that matters.\n"
            "BODY LANGUAGE: Same driver seat. Hand on wheel. Head level. Completely grounded. Still.\n"
            "VOICE STYLE: Same low voice. Solidarity. Weight in 'not just me.'\n"
            "TONE: Collective. Quiet but certain. 'A thousand of us' lands with size.\n"
            "SPEED: ~2.0 wps. Even throughout.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "And it\'s not just me. It\'s almost a thousand of us who\'ve come forward."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on the dash camera. Practical and direct. Making it simple.\n"
            "BODY LANGUAGE: Same driver seat. Both hands loose. Head level. Still.\n"
            "VOICE STYLE: Same low voice. A friend explaining something easy.\n"
            "TONE: Stripping the intimidation out. 'Two minutes' lands plain and final.\n"
            "SPEED: ~2.1 wps. 'You know what it took?' slight pause, then 'Two minutes' flat.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I already filed mine. You know what it took? Two minutes."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Eyes on the dash camera. Calm. Just facts. Plain as a receipt.\n"
            "BODY LANGUAGE: Same driver seat. Arms relaxed. Head level. Unhurried. Very still.\n"
            "VOICE STYLE: Same low voice. Flat and practical.\n"
            "TONE: Plain. Each phrase drops cleanly.\n"
            "SPEED: ~2.0 wps. Even throughout.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "There\'s a form online. You just put where you were and what happened."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Eyes on the dash camera. The most grounded look of the video. Killing every objection.\n"
            "BODY LANGUAGE: Same driver seat. Head level. Completely still. Both hands loose.\n"
            "VOICE STYLE: Same low voice, quietest of the ad. Flat and certain.\n"
            "TONE: Removing every reason not to act. Each phrase its own breath.\n"
            "SPEED: ~1.9 wps. Distinct pause after each phrase.\n\n"
            "AUDIO CRITICAL: CLEARLY AUDIBLE despite quiet tone. NOT inaudible. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the complete clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "No police report. No court date. No calls to your house. '
            'Nobody even finds out you looked."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 10,
        "prompt": (
            "GAZE: Eyes on the dash camera. Quiet and certain. The close is coming.\n"
            "BODY LANGUAGE: Same driver seat. Head level. Leaning slightly back. Completely settled.\n"
            "VOICE STYLE: Same low voice. Lowest energy of the ad. Settled.\n"
            "TONE: Final. 'It hasn't' lands heavy and real.\n"
            "SPEED: ~1.8 wps. Slow and certain. Long beat on 'It hasn't.'\n\n"
            "AUDIO CRITICAL: CLEARLY AUDIBLE despite low tone. NOT inaudible. ZERO fillers. ONLY exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I thought the clock ran out on this years ago. It hasn\'t."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 11,
        "prompt": (
            "GAZE: Eyes on the dash camera. The most direct look of the video. Speaking to one person.\n"
            "BODY LANGUAGE: Same driver seat. Slight forward lean on 'that was you.' Head level. Still.\n"
            "VOICE STYLE: Same low voice. Directest delivery of the ad.\n"
            "TONE: Personal. 'That was you' is for one person watching. 'Don't sleep on this' is a quiet command.\n"
            "SPEED: ~2.0 wps. 'Don't sleep on this.' lands slow. CTA plain and direct.\n\n"
            "AUDIO CRITICAL: CLEARLY AUDIBLE. ZERO fillers. ONLY exact words. "
            "Do NOT add anything after 'qualify.'\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the complete clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "If that was you in there. Don\'t sleep on this. '
            'Tap the button and see if you qualify."\n\n'
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
    print(f"IL JDC V2 — Persona S v1 | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
