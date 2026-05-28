"""Re-roll clips 2 and 4 — rephrased to break Veo improv patterns."""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:e8141e6a-de5b-41ad-a55e-fca41845f4c6"
OUT = Path("outputs/il_jdc_v6_g")

CLIPS = [
    {
        "n": 2,
        # Rephrased: "did time in" instead of "locked up in" to break the "on-" filler trigger
        "prompt": (
            "GAZE: Eyes on lens, steady and serious. Laying down facts.\n"
            "BODY LANGUAGE: Arms crossed. Near-still throughout. Grounded and still.\n"
            "VOICE STYLE: Same deep voice, drops half a register. Plain and direct.\n"
            "TONE: Naming the situation. No drama. Just facts.\n"
            "SPEED: ~2.0 wps. Illinois juvenile spot lands deliberately.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "Absolutely NO filler sounds (no ah, uh, on, well, like, you know). "
            "No hesitation sounds. ONLY the exact scripted words, nothing else.\n\n"
            "PRONUNCIATION LOCK: Illinois = ILL-ih-noy.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No filler words of any kind. "
            "No words added before, between, or after any scripted word. "
            "Do NOT improvise or continue after the final word. "
            "Speak ONLY the EXACT words below and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "If you did time as a kid in any Illinois juvenile spot."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        # Rephrased: lead with "Right now" to prevent "The State of" prefix
        # Shortened No list to reduce mm-hmm insertion opportunities
        "prompt": (
            "GAZE: Eyes forward and present, delivering key information directly.\n"
            "BODY LANGUAGE: Arms crossed. Head completely level and still. "
            "NO nodding, NO head movements between sentences.\n"
            "VOICE STYLE: Same deep voice, matter-of-fact. Informational but intimate.\n"
            "TONE: Important news delivered quietly. Not a sales tone.\n"
            "SPEED: ~2.0 wps. Each No sentence is flat and staccato.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "ZERO non-verbal sounds. No mm-hmm, no yeah, no throat sounds, no breathing sounds. "
            "SILENCE between sentences, not sounds. ONLY the exact scripted words.\n\n"
            "PRONUNCIATION LOCK: Illinois = ILL-ih-noy. compensation = com-pen-SAY-shun.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No non-verbal sounds. "
            "No trailing words or sentences. Each sentence spoken ONCE only. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Right now, Illinois is paying significant potential compensation. No police report. No paperwork."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
]


def poll(job_id, n, timeout=600, interval=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"https://api.useapi.net/v1/google-flow/jobs/{job_id}",
                         headers=HEADERS, timeout=30)
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
            raise RuntimeError(f"clip{n}: completed but no videoUrl")
        elif status == "failed":
            raise RuntimeError(f"clip{n} FAILED: {data}")
        print(f"    clip{n}: {status} …", flush=True)
        time.sleep(interval)
    raise TimeoutError(f"clip{n} timeout")


def gen(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists():
        out_path.unlink()
    payload = {
        "prompt": clip["prompt"],
        "model": "veo-3.1-fast",
        "startImage": ANCHOR,
        "aspectRatio": "portrait",
        "duration": 8,
        "async": True,
        "captchaRetry": 5,
    }
    r = requests.post("https://api.useapi.net/v1/google-flow/videos",
                      headers=HEADERS, json=payload, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Submit clip{n}: {r.status_code} {r.text[:200]}")
    job_id = r.json().get("jobid")
    print(f"  clip{n}: submitted {job_id[:50]}…", flush=True)
    url = poll(job_id, n)
    r2 = requests.get(url, timeout=120, stream=True)
    r2.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r2.iter_content(65536):
            f.write(chunk)
    print(f"  clip{n}: saved {out_path.stat().st_size // 1024}KB")
    return n


if __name__ == "__main__":
    print(f"Re-rolling clips 2, 4 → {OUT}\n")
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(gen, c): c["n"] for c in CLIPS}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                fut.result()
                print(f"✓ clip{n} re-rolled")
            except Exception as e:
                print(f"✗ clip{n} ERROR: {e}")
    print("Done.")
