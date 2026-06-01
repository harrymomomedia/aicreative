"""
IL JDC V1 — "Most people don't realize the laws changed"
Persona Q v1 (male 32, driver seat, windshield light) | 10 clips × 8s
useapi.net Google Flow veo-3.1-lite | car interior / dashboard cam framing
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:4e533b60-f94f-47e5-91d6-736759a01b2c"
OUT = Path("outputs/il_jdc_v1_q")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes aimed down toward the phone on the dash — direct, calm, like he's recording "
            "a voice note to someone he knows. Holds the camera the whole clip.\n"
            "BODY LANGUAGE: Seated in driver seat of a parked car. Phone mounted low on dashboard "
            "or resting near the steering wheel — camera looks up slightly at his face. "
            "Leaning slightly toward the wheel. One hand loosely on the wheel, other in his lap. "
            "Head level, still. No extended arm.\n"
            "VOICE STYLE: Low, measured, early 30s. Like he's telling a friend something real.\n"
            "TONE: Controlled. The tone of someone dropping important information — not an ad.\n"
            "SPEED: ~2.0 wps. Deliberate. Slight weight on 'recently changed.'\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection inside the car. "
            "NOT whispered. ONLY the exact scripted words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay aimed at the phone/lens the entire clip. "
            "Does NOT look away.\n\n"
            "CRITICAL — NO SMILE EVER: Mouth flat and neutral. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Most people don\'t realize. The laws for Illinois juvenile center '
            'abuse claims recently changed."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on the dash camera — steady, unhurried. Letting the information land.\n"
            "BODY LANGUAGE: Same parked-car driver seat position. Phone low on dash, camera "
            "angle looking up. One hand on wheel, other in lap. Leaning slightly forward. Still.\n"
            "VOICE STYLE: Same low measured voice. Slightly slower — spacing each phrase.\n"
            "TONE: Quiet revelation. 'Even if it happened decades ago' lands with weight.\n"
            "SPEED: ~1.9 wps. 'Even if it happened decades ago' delivered slowly and plainly.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes aimed at the lens the entire clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
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
            "GAZE: Eyes on the dash camera — heavier now. He is stating a personal fact. "
            "Holds the look steady.\n"
            "BODY LANGUAGE: Same parked-car driver seat. Phone low on dash, slight upward camera angle. "
            "Both hands relaxed — one on wheel. Head level. Very still. Might lean slightly forward "
            "on 'abused me in there.' No extended arm.\n"
            "VOICE STYLE: Same low voice. Heavier — naming something personal.\n"
            "TONE: Heavy and plain. No drama in the voice — just the truth delivered directly.\n"
            "SPEED: ~2.1 wps. Brief pause after 'juvenile center.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "PRONUNCIATION LOCK: Illinois = Ill-ih-NOY. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the complete clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I was just a kid when I went into that Illinois juvenile center. '
            'A staff member abused me in there. I buried it."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on the dash camera. Quiet. The weight of what he just said is still in the air.\n"
            "BODY LANGUAGE: Same parked-car seat. Phone low on dash. "
            "Leaning slightly back — the exhale after naming something heavy. Very still. "
            "One hand on wheel, head level.\n"
            "VOICE STYLE: Same low voice. Quieter — almost to himself. Flat.\n"
            "TONE: The flatness of a buried thing. 'Closed for good' lands like a lid coming down.\n"
            "SPEED: ~1.8 wps. Slow and deliberate. Each phrase its own beat.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite quiet tone. NOT inaudible. "
            "ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay aimed at the lens.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Told myself that chapter was closed for good. Then I found out."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on the dash camera — a controlled lift. Something is opening. "
            "Still direct, still aimed at the lens.\n"
            "BODY LANGUAGE: Same parked-car seat, phone low on dash. "
            "Slight forward lean — the energy shifts slightly. Head level. One hand on wheel.\n"
            "VOICE STYLE: Same low voice, fractionally warmer. A door opening.\n"
            "TONE: The pivot. 'Actually paying' lands with quiet certainty. Not triumphant — factual.\n"
            "SPEED: ~2.2 wps. 'Significant potential compensation' delivered clearly and evenly.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO non-verbal sounds. ONLY the exact words.\n\n"
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
            "BODY LANGUAGE: Same parked-car seat, phone low. Head level, still. "
            "One hand resting on wheel. Completely grounded.\n"
            "VOICE STYLE: Same low voice. The solidarity beat — weight in 'not just me.'\n"
            "TONE: Collective. Quiet but certain. The number lands — 'a thousand of us.'\n"
            "SPEED: ~2.1 wps. Brief beat before 'I already filed mine.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "And it\'s not just me. It\'s almost a thousand of us who\'ve '
            'come forward."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on the dash camera — practical and direct. Making it simple.\n"
            "BODY LANGUAGE: Same parked-car seat. Phone low on dash. "
            "Slight shrug energy — this is easier than you think. Both hands relaxed. "
            "Head level, still.\n"
            "VOICE STYLE: Same low voice, fractionally warmer — a friend explaining something easy.\n"
            "TONE: Stripping the intimidation out. 'Two minutes' lands plain and final.\n"
            "SPEED: ~2.2 wps. 'You know what it took?' slight pause, then 'Two minutes' flat.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
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
            "GAZE: Eyes on the dash camera. Completely calm. Just facts.\n"
            "BODY LANGUAGE: Same parked-car seat, phone low on dash. "
            "Arms relaxed, one hand resting in lap, other on wheel. Unhurried. Very still.\n"
            "VOICE STYLE: Same low voice, flat and practical. Reading off a short list.\n"
            "TONE: Plain as a receipt. Each phrase drops cleanly.\n"
            "SPEED: ~2.0 wps. Even delivery throughout. No rushing.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the full clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "There\'s a form online. You just put where you were and '
            'what happened."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Eyes on the dash camera. The most grounded look in the video — "
            "killing every objection one by one. Eyes stay steady and forward.\n"
            "BODY LANGUAGE: Same parked-car seat, phone low. Head level, completely still. "
            "Both hands loose. He has nowhere else to be.\n"
            "VOICE STYLE: Same low voice, quietest of the ad. Flat and certain.\n"
            "TONE: Removing every reason not to act. Each phrase its own breath.\n"
            "SPEED: ~1.9 wps. Distinct pause after 'No police report.' 'No court date.' "
            "'No calls to your house.' 'Nobody even finds out you looked.'\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite quiet tone. NOT inaudible. "
            "ZERO fillers. ONLY the exact words.\n\n"
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
            "GAZE: Eyes on the dash camera — the quietest, most direct look. The close. "
            "He holds the lens until the last word.\n"
            "BODY LANGUAGE: Same parked-car seat, phone low. Leaning slightly back — "
            "everything has been said. Head level. Hands loose. Still.\n"
            "VOICE STYLE: Same low voice. Lowest energy of the ad — not quiet, just settled.\n"
            "TONE: Final. 'It hasn't' lands heavy and real. 'Don't sleep.' is for one person.\n"
            "SPEED: ~1.8 wps. 'I thought the clock ran out on this years ago.' slow and certain. "
            "Long beat on 'It hasn't.' Then 'Don't sleep.' and the CTA plain and direct.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite low tone. NOT inaudible. "
            "ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON CAMERA: Eyes stay on the lens the complete clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Do NOT add anything after 'qualify.' "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I thought the clock ran out on this years ago. It hasn\'t. '
            'Don\'t sleep on this. Tap the button and see if you qualify."\n\n'
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
    print(f"IL JDC V1 — 'Most people don't realize the laws changed'")
    print(f"Persona: Q_v1 | Model: veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
