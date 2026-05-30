"""
CA JDC V4 — "They told me to keep my mouth shut"
Persona N v1 (male 38, deep dark-brown skin, overcast alley) | 7 clips × 8s
useapi.net Google Flow veo-3.1-lite | closeup documentary framing
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:6a037964-e7e0-4c68-b94f-9099c264fdfd"
OUT = Path("outputs/ca_jdc_v4_n")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes LOCKED on the lens from the very first frame — heavy, direct, never breaks. "
            "The look of someone who has been sitting with something for a long time.\n"
            "BODY LANGUAGE: Close-up documentary framing — camera at eye level, held by another person "
            "or on a tripod, NOT a selfie. Both arms relaxed at sides, one hand loosely in pocket. "
            "Head level. Completely still. NO extended arm, NO phone visible.\n"
            "VOICE STYLE: Deep, low, measured. Late 30s. Controlled. Not shouting — cutting through.\n"
            "TONE: Carrying something heavy. The weight of a statement that has been held for years.\n"
            "SPEED: ~2.2 wps. Deliberate pause after 'shut.' 'troubled kid' lands flat and final.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "NOT whispered. NO filler sounds. ONLY the exact scripted words.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes stay OPEN and LOCKED on the lens "
            "for the COMPLETE clip. Does NOT look away for even a moment.\n\n"
            "CRITICAL — NO SMILE EVER: Mouth stays flat and neutral throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No filler words. No extra words. "
            "No trailing words. Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "They told me to keep my mouth shut. That nobody would believe a troubled kid."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes still LOCKED on the lens — steady, heavier. He is stating a fact "
            "that cost him something. Not performing — disclosing.\n"
            "BODY LANGUAGE: Same closeup documentary hold — camera at eye level by another person "
            "or tripod, NOT a selfie. Both arms relaxed. One hand loosely in pocket. "
            "Very still. Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep low voice. Slightly slower — the weight of naming it.\n"
            "TONE: Heavy and plain. Stating what happened. No drama. The truth is the drama.\n"
            "SPEED: ~2.3 wps. Distinct pause after 'facility.' 'Changed my whole life.' delivered quietly.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "PRONUNCIATION LOCK: California = Cal-ih-FOR-nee-uh. juvenile = JOO-ven-ile. "
            "facility = fuh-SIL-ih-tee. fourteen = FOR-teen.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes OPEN and LOCKED throughout the ENTIRE clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No added words. No trailing word. "
            "Speak ONLY the EXACT words below and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "I was fourteen, in a California juvenile facility. '
            'What happened to me in there changed my whole life."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes LOCKED — a controlled lift in energy. He is turning something over. "
            "Still serious, but something is opening. NEVER looks away.\n"
            "BODY LANGUAGE: Same closeup documentary framing — camera at eye level, NOT selfie. "
            "Arms relaxed at sides. Very slight forward shift in weight on 'they were wrong.' "
            "Then still. Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep voice, slightly warmer — a door opening.\n"
            "TONE: The pivot. Not triumphant — quiet but sure. 'They were wrong' lands with certainty.\n"
            "SPEED: ~2.2 wps. Brief weight on 'wrong.' Then steady through to 'compensating survivors.'\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO non-verbal sounds. ONLY the exact words.\n\n"
            "PRONUNCIATION LOCK: California = Cal-ih-FOR-nee-uh. compensating = COM-pen-say-ting. "
            "survivors = sur-VY-verz.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes OPEN and LOCKED on the lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No added words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "But they were wrong. People do believe you. And right now, '
            'California is compensating survivors"\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes LOCKED — delivering the most important information in the video. "
            "Steady and certain. NEVER breaks contact.\n"
            "BODY LANGUAGE: Same closeup documentary hold — camera at eye level, NOT selfie. "
            "Arms relaxed, one hand in pocket. Completely still. Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep voice. Factual. Grounded. Each phrase has its own weight.\n"
            "TONE: Naming what this is worth. Quiet gravity. 'Significant potential compensation' "
            "lands with space around it. 'Nothing to find out' is plain and reassuring.\n"
            "SPEED: ~2.0 wps. Brief pause after 'those places.' Each phrase delivered clean.\n\n"
            "AUDIO CRITICAL: FULL projection. ABSOLUTELY NO non-verbal sounds. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes stay OPEN and LOCKED on the lens "
            "for the ENTIRE clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "who were abused in those places. Significant potential compensation. '
            'It costs nothing to find out."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes LOCKED — making the next step feel simple and easy. Direct, practical.\n"
            "BODY LANGUAGE: Same closeup documentary hold — camera at eye level, NOT selfie. "
            "Arms relaxed. Both hands visible but loose. Calm, slightly warmer energy. "
            "Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep voice, slightly warmer and more practical. A friend explaining "
            "something straightforward.\n"
            "TONE: Removing friction. Making the process feel effortless. Calm and matter-of-fact.\n"
            "SPEED: ~2.25 wps. Even delivery. 'Sixty seconds' lands simply — no buildup.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes stay OPEN and LOCKED on the lens "
            "for the COMPLETE clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Tap the link, answer a few questions, sixty seconds. '
            'And you will know if you have a claim."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes LOCKED — quiet and certain. Closing every objection one by one. "
            "The steadiest gaze in the video. NEVER looks away.\n"
            "BODY LANGUAGE: Same closeup documentary hold — camera at eye level, NOT selfie. "
            "Arms relaxed at sides. Completely still. Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep voice, slightly quieter. Practical and plain.\n"
            "TONE: Stripping away every reason not to act. Each short phrase lands as its own beat. "
            "Then slightly earnest on the final line.\n"
            "SPEED: ~1.9 wps. 'Free.' pause. 'Private.' pause. 'No pressure.' pause. "
            "Then the final sentence is even and clear.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite quieter tone. NOT inaudible. "
            "NO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes stay OPEN and LOCKED for the COMPLETE clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile in face or voice.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Free. Private. No pressure. Even if you are not sure it applies to you. '
            'Just check."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: The softest, most direct look in the video — eyes still locked, but warmer now. "
            "Genuine. This is a real ask. NEVER breaks eye contact.\n"
            "BODY LANGUAGE: Same closeup documentary hold — camera at eye level, NOT selfie. "
            "Arms relaxed. Posture opens slightly — everything has been said, now he is asking "
            "something personal. Head level. NO phone in hand.\n"
            "VOICE STYLE: Same deep voice, lowest energy of the video. Almost a personal aside.\n"
            "TONE: Earnest. Not salesy — he actually means it. 'Someone on your feed might really need "
            "this today' lands with warmth and weight.\n"
            "SPEED: ~1.9 wps. 'Share this too, please.' very slow and direct. "
            "Then the final sentence with a natural close.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite quiet tone. NOT inaudible. "
            "NO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES ON LENS AT ALL TIMES: Eyes stay OPEN and LOCKED for the COMPLETE clip.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Share this too, please. Someone on your feed might really need '
            'this today."\n\n'
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
    print(f"CA JDC V4 — 'They told me to keep my mouth shut'")
    print(f"Persona: N_v1 | Model: veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
