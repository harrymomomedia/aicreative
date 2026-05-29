"""
CA JDC V1 — "They called it a search"
Persona A v1 (Black male 33, basketball court)
6 clips × 8s via useapi.net Google Flow veo-3.1-lite
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:da46b194-1b2d-4eca-9acb-fe5000fe2ff2"
OUT = Path("outputs/ca_jdc_v1_a")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Locked on lens from frame one. Heavy, slow. Daring the viewer to keep watching.\n"
            "BODY LANGUAGE: Arms crossed tight at chest. Back against the chain-link fence, "
            "leaned into it. Still and grounded. Slight chin tilt down — weight behind every word.\n"
            "VOICE STYLE: Deep, low, measured. Late 30s. Deliberate and controlled.\n"
            "TONE: Naming something everyone already knows but nobody says out loud. No drama — just weight.\n"
            "SPEED: ~1.3 wps. Full pause after each phrase. Each sentence its own beat.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. "
            "NOT whispered. NO filler sounds (no ah, uh, well, like). "
            "ONLY the exact scripted words.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout. "
            "Does NOT close eyes.\n\n"
            "CRITICAL — NO SMILE EVER: Mouth stays in a flat heavy neutral line. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No filler words. No extra words inserted. "
            "No trailing words. Do NOT add anything before, between, or after the lines. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "They called it a search. A pat-down. Standard procedure."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes still, heavy on the lens. The look of someone who has been carrying this.\n"
            "BODY LANGUAGE: Arms crossed. Near-still. A single beat of stillness after 'was.'\n"
            "VOICE STYLE: Same deep voice. Drops half a register. Plain and direct.\n"
            "TONE: Naming the truth with quiet authority. The silence of knowing.\n"
            "SPEED: ~1.6 wps. 'And so do they' lands flat and final.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN on the lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No extra words. No trailing word. "
            "Speak ONLY the EXACT words below and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "But you know what it really was. And so do they."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes forward, finding the viewer directly. He is talking to one specific person.\n"
            "BODY LANGUAGE: Arms still crossed. Very small forward weight shift on 'California.' "
            "Head stays level and still. NO nodding.\n"
            "VOICE STYLE: Same deep voice. More present. Informational but intimate.\n"
            "TONE: Calm identification. Quiet certainty. Not accusatory — just naming facts.\n"
            "SPEED: ~2.5 wps. Steady and even through the full sentence.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL projection. "
            "NO filler sounds (no ah, uh, on, well). ONLY the exact scripted words.\n\n"
            "PRONUNCIATION LOCK: California = Cal-ih-FOR-nee-uh. juvenile = JOO-ven-ile.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. Absolutely NO filler words. "
            "No extra words inserted anywhere. No trailing words. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "If you were locked up in a California juvenile facility and a staff member put their hands on you."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Direct and steady. Eye contact deepens on 'not the only one.' He means it.\n"
            "BODY LANGUAGE: Arms crossed, head completely level. "
            "ONE small affirming shift on the last sentence then completely still.\n"
            "VOICE STYLE: Same deep voice. Slightly lower. Grave but in control.\n"
            "TONE: Naming the truth plainly. Solidarity without performance. Not theatrical — just true.\n"
            "SPEED: ~2.0 wps. 'Not the only one' is deliberately slower and flatter.\n\n"
            "AUDIO CRITICAL: FULL projection. ZERO non-verbal sounds between sentences. "
            "No mm-hmm, no throat sounds, no breathing sounds. ONLY the exact words.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN on the lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No added words. "
            "Do NOT add 'and' or any word before 'And abused.' "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "And abused you under the excuse of a search. You are not the only one."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes lift slightly, forward and more present. Delivering important information directly.\n"
            "BODY LANGUAGE: Arms crossed. Very small forward lean on 'right now.' Head stays level. "
            "NO nodding between sentences.\n"
            "VOICE STYLE: Same deep voice, slight purposeful lift. Informational but not a sales pitch.\n"
            "TONE: Important news delivered quietly. Something is happening and he wants this person to know.\n"
            "SPEED: ~2.3 wps. Even through both sentences.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL projection. "
            "ABSOLUTELY NO non-verbal sounds. No mm-hmm between sentences. ONLY the exact words.\n\n"
            "PRONUNCIATION LOCK: compensation = com-pen-SAY-shun. lawsuit = LAW-suit.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No filler. No trailing words. "
            "Each sentence spoken ONCE only. "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "Hundreds are coming forward right now. There\'s a major lawsuit happening, and you could be owed significant potential compensation."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Soft and steady on lens. The quietest most direct look in the video.\n"
            "BODY LANGUAGE: Arms crossed but posture opens slightly. Completely still. "
            "Everything has been said. This is just the offer.\n"
            "VOICE STYLE: Same voice, slightly warmer. A practical friend making it simple.\n"
            "TONE: Removing every barrier. Each phrase a door opening. Relief.\n"
            "SPEED: ~1.8 wps. 'No police report.' and 'No proof needed to start.' each land short and flat. "
            "CTA is clean and direct.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite warmer tone. NOT inaudible. "
            "NO fillers. ONLY the exact words.\n\n"
            "CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at lens throughout.\n\n"
            "CRITICAL — NO SMILE EVER: ZERO smile in face or voice.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No trailing words. "
            "Do NOT add anything after 'qualify for.' "
            "Speak ONLY the EXACT words below in order and STOP after the final word.\n\n"
            'SPOKEN DIALOGUE: "No police report. No proof needed to start. Tap below. The quiz takes 30 seconds. See what you could qualify for."\n\n'
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
    print(f"CA JDC V1 — 'They called it a search'")
    print(f"Persona: A_v1 | Model: veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
