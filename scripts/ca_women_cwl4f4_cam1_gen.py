"""
CA Women CWL4_F4 cam1 gen:
  Persona: CWL4_F4_v1 — Latina 44, Nicaraguan, San Diego coastal boardwalk, extreme close-up
  Script: "You think it doesn't count because you didn't scream..." — survival reframe / no-fight defense
  7 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# CWL4_F4_v1 — Latina 44, Nicaraguan, San Diego boardwalk, extreme close-up
# light peachy-olive tan, loose 2C-3A spiral curls, hazel-brown melancholy eyes
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:3276f6d9-5c50-4f4c-8cd1-ab5defa18cce"
OUT = Path("outputs/ca_women_cwl4f4_cam1")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes on the lens — direct, unwavering, slightly challenging. She's addressing someone specific.\n"
            "BODY LANGUAGE: Head level. Jaw very slightly set. A still intensity — not aggressive, but not soft.\n"
            "VOICE STYLE: Warm 40s Latina, slightly husky. Plain California. Low and even, not announcer.\n"
            "TONE: Direct challenge — not angry, but clear. 'You think' spoken with quiet authority to the viewer.\n"
            "SPEED: ~2.2 wps. Deliberate. Brief pause after 'scream.' Full stop pause after 'fight.'\n\n"
            "EMOTION: A focused quiet challenge. She's been there. She's correcting something she knows is wrong.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet conversational projection. NOT whispered. Every word distinct.\n\n"
            "EYES LOCK: Light hazel-brown eyes stay OPEN and on the lens throughout. Same eye color first to last frame.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You think it doesn\'t count because you didn\'t scream. Because you didn\'t fight."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on lens. A slight lean-in energy — she's pulling the viewer into the truth.\n"
            "BODY LANGUAGE: Very slight forward lean on 'Let me tell you.' Then still. Head steady.\n"
            "VOICE STYLE: Same warm husky voice. 'Let me tell you something' — low and serious, not dramatic.\n"
            "TONE: Corrective insider knowledge. She's explaining what the viewer doesn't understand.\n"
            "SPEED: ~2.4 wps. Each clause lands. Brief pause after 'something.' Slight urgency building.\n\n"
            "EMOTION: Controlled authority. She's lived this. She knows what he couldn't.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Let me tell you something. In a California women\'s prison, you couldn\'t fight. He had the keys. He had the write-ups."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes on lens. Each item she lists lands separately — she's counting his power.\n"
            "BODY LANGUAGE: Completely still. A very slight tightening around the eyes on 'daylight.'\n"
            "VOICE STYLE: Same warm husky voice. Each 'if' clause its own weight.\n"
            "TONE: The enumeration of powerlessness. Slow and deliberate. Each item is a memory.\n"
            "SPEED: ~2.0 wps. Slower. Micro-pause after each 'if you ate,' 'if you got moved.'\n\n"
            "EMOTION: A soft heaviness. Not grief — the flat weight of documented fact. Slight moisture at the eye corners.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "He decided if you ate, if you got moved, if you ever saw daylight."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on lens. The most direct emotional contact of the whole ad. She's saying what she wished someone had said to her.\n"
            "BODY LANGUAGE: Still. On 'Going still wasn't saying yes' — the faintest softening around the eyes.\n"
            "VOICE STYLE: Same warm voice. 'Going still wasn't saying yes' — deliberate, each word weighted.\n"
            "TONE: Core reframe. Gentle but firm. She's releasing something. Not reassurance — truth.\n"
            "SPEED: ~1.9 wps. Slowest clip. Full pause between the two sentences.\n\n"
            "EMOTION: Quiet conviction with a thread of grief underneath. Compassion for the viewer. Near-still face but weight in the eyes.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens. Slight warmth, NOT pity.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Going still wasn\'t saying yes. It was the only way to survive him."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on lens. A return to quiet factual directness — the pivot from pain to possibility.\n"
            "BODY LANGUAGE: Completely still. 'Still abuse' spoken without breaking.\n"
            "VOICE STYLE: Same warm voice. Plain and steady. 'Lawsuit' delivered matter-of-fact, not triumphant.\n"
            "TONE: Naming it without flinching, then stating the legal fact. Informational but not cold.\n"
            "SPEED: ~2.3 wps. Even. Slight pause between 'still abuse' and 'There's a lawsuit.'\n\n"
            "EMOTION: Flat calm with quiet resolve. The grief is behind her — this is the actionable part.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "What a staff member did to you behind those walls was still abuse. There\'s a lawsuit now for exactly this."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on lens. A direct address — she's talking to the specific woman who stayed quiet.\n"
            "BODY LANGUAGE: Still. 'Never fought back' spoken with a very faint recognition — she may have been that woman.\n"
            "VOICE STYLE: Same warm voice. 'May qualify for significant potential compensation' — plain, not salesy.\n"
            "TONE: Direct inclusion. Not a pitch. She's saying: you too, specifically you.\n"
            "SPEED: ~2.1 wps. Deliberate. Pause after 'never fought back.'\n\n"
            "EMOTION: Quiet solidarity. A small softening at the corners of the eyes on 'never fought back.'\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words. NO commercial inflection on 'may qualify' — flat and plain.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Women who never fought back may qualify for significant potential compensation."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on lens. Still and open. The quietest, most gentle moment.\n"
            "BODY LANGUAGE: Completely still. A last soft breath. 'Tap below' delivered like a gift.\n"
            "VOICE STYLE: Same warm voice. Quieter. Plain. No urgency.\n"
            "TONE: Quiet close. Low stakes — confidential, costs nothing. She's taking the pressure off.\n"
            "SPEED: ~2.0 wps. Slowest. Natural pause between each sentence. Silence after 'Tap below.'\n\n"
            "EMOTION: Warm stillness. A subtle release of tension. NOT commercial, NOT upbeat — just calm and open.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words. NO TV-ad delivery, NO upbeat inflection.\n\n"
            "EYES LOCK: Light hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "It\'s confidential. It costs nothing. Just see if you\'re one of them. Tap below."\n\n'
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
    print(f"CA Women CWL4_F4 cam1 — Latina 44, Nicaraguan (San Diego boardwalk) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
