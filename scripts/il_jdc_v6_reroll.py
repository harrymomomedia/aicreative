"""Re-roll clips 1, 2, 4, 5 for IL JDC V6 persona G."""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:e8141e6a-de5b-41ad-a55e-fca41845f4c6"
OUT = Path("outputs/il_jdc_v6_g")

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Locked into lens from frame one. Heavy, daring the viewer to keep watching.\n"
            "BODY LANGUAGE: Arms crossed, leaned back into brick wall. Still. Slight confident chin tilt.\n"
            "VOICE STYLE: Late-30s man, deep warm voice, Chicago cadence. Deliberate and controlled.\n"
            "TONE: Pattern interrupt. Bold claim, daring you to doubt it. Quiet authority.\n"
            "SPEED: ~1.8 wps. Full beat after first sentence before second.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. NOT whispered. "
            "NO non-verbal sounds. NO filler sounds. ONLY the scripted words.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No inserted words. No extra numbers. "
            "No trailing words. Do NOT add anything before, between, or after the lines. "
            "Speak ONLY the EXACT words below in order and STOP.\n\n"
            'SPOKEN DIALOGUE: "Sixty seconds could be worth six figures. Hear me out."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on lens, steady and serious. Laying down facts.\n"
            "BODY LANGUAGE: Arms crossed. Near-still. Slight lean off the wall on the word locked up.\n"
            "VOICE STYLE: Same deep voice, drops half a register.\n"
            "TONE: Naming the situation directly. No drama. Just facts.\n"
            "SPEED: ~2.0 wps. Illinois juvenile spot lands deliberately.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "NO fillers, NO hesitation sounds (no ah, uh, well, like), NO extra words inserted anywhere. "
            "ONLY the scripted words.\n\n"
            "PRONUNCIATION LOCK: Illinois = ILL-ih-noy.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. Absolutely NO filler words. "
            "No extra words inserted before, after, or between any words. "
            "Speak ONLY the EXACT words below and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "If you was a kid locked up in any Illinois juvenile spot."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes lift slightly, forward and present. Delivering key information.\n"
            "BODY LANGUAGE: Very small forward lean on right now. Arms stay crossed. "
            "NO head nods. NO nodding between sentences. Head stays level and still throughout.\n"
            "VOICE STYLE: Same deep voice, lifts just slightly. Informational but intimate.\n"
            "TONE: Important news delivered quietly. Not a sales tone.\n"
            "SPEED: ~2.1 wps. Each No lands short and flat.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "ABSOLUTELY NO non-verbal sounds. NO mm-hmm, NO throat clearing, NO breathing sounds, "
            "NO agreement sounds between sentences. ONLY the scripted spoken words.\n\n"
            "PRONUNCIATION LOCK: Illinois = ILL-ih-noy. compensation = com-pen-SAY-shun.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. Do NOT add The state of or any prefix before Illinois. "
            "No fillers. No non-verbal sounds. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Illinois is paying significant potential compensation right now. No police report. No paperwork."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Direct into lens, steady. Confirming what the viewer already suspected.\n"
            "BODY LANGUAGE: ONE single small nod on the point then completely still. Arms crossed throughout.\n"
            "VOICE STYLE: Matter-of-fact. Calm street logic.\n"
            "TONE: Validation. Naming the system plainly.\n"
            "SPEED: ~2.0 wps. The final sentence lands flat and final, spoken ONCE only.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "No fillers. Do NOT repeat any sentence. ONLY the scripted words spoken ONCE each.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. Do NOT repeat any sentence or phrase. "
            "Each sentence is spoken EXACTLY ONCE. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP immediately after the final word. "
            "Do NOT say That is the point or That's the point twice.\n\n"
            'SPOKEN DIALOGUE: "Most of these cases never even made it to court. That\'s the point."\n\n'
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
    print(f"Re-rolling clips 1, 2, 4, 5 → {OUT}\n")
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(gen, c): c["n"] for c in CLIPS}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                fut.result()
                print(f"✓ clip{n} re-rolled")
            except Exception as e:
                print(f"✗ clip{n} ERROR: {e}")
    print("Done.")
