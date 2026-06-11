"""
CA Women CWL4_F3 cam1 gen:
  Persona: CWL4_F3_v1 — Latina 42, Peruvian/Andean, Sacramento apt living room, medium close-up
  Script: "The fear was never the lawyers..." — family secrecy / private filing reassurance
  7 clips × 8s | useapi.net Google Flow veo-3.1-lite | low priority
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
# CWL4_F3_v1 — Latina 42, Peruvian/Andean, Sacramento apartment living room
# rectangular face, angular jaw, medium warm brown skin, wavy auburn-brown hair, hazel-brown eyes
ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:f1de9947-9f06-47fb-9d23-fdefb4e623bc"
OUT = Path("outputs/ca_women_cwl4f3_cam1")
OUT.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes on lens from first frame. Steady. Knowing. She sees through the viewer.\n"
            "BODY LANGUAGE: Completely still. A quiet certainty — she has been here, she knows the real thing.\n"
            "VOICE STYLE: Warm 40s Latina, slightly husky. Low and even. Plain California. Not dramatic.\n"
            "TONE: Naming a hidden truth the viewer hasn't admitted. No judgment. Just recognition.\n"
            "SPEED: ~2.0 wps. Slow and deliberate. Full beat after 'lawyers.' Full stop after 'out.'\n\n"
            "EMOTION: Quiet knowing. She is not accusing. She is recognizing. A soft gravity in the eyes.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full quiet conversational projection. NOT whispered.\n\n"
            "EYES LOCK: Warm hazel-brown eyes stay OPEN and on the lens throughout. Same eye color first to last frame.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners throughout.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "The fear was never the lawyers. It was your husband finding out."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Eyes on lens. A slight inward pull — she is recounting something she understands deeply.\n"
            "BODY LANGUAGE: Still. On 'kids' — the faintest tightening around the eyes. On 'ten times' — a very slight nod.\n"
            "VOICE STYLE: Same warm voice. 'You never told your kids' — quiet and plain, not dramatic.\n"
            "TONE: Deep recognition without pity. She is saying: I see exactly why you kept scrolling.\n"
            "SPEED: ~2.2 wps. Even. Brief pause after 'in there.' Slight weight on 'ten times.'\n\n"
            "EMOTION: Heavy empathy with no performance. The eyes carry the weight more than the voice.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You never told your kids what happened in there. That is the real reason you have scrolled past this ten times."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Eyes on lens. 'Not the police' — flat and clean. 'Your family' — a beat of stillness.\n"
            "BODY LANGUAGE: Completely still. After 'Your family' — one slow breath. On 'I get it' — the slightest softening.\n"
            "VOICE STYLE: Same warm voice. 'Not the police.' stark and clipped. 'Your family.' even quieter. 'I get it.' — warmest moment.\n"
            "TONE: Three beats: stark truth, then the warmest pivot of the whole ad, then quiet reassurance.\n"
            "SPEED: ~1.8 wps. Slowest clip. Long natural pause after 'Your family.' Then 'I get it' almost a whisper-level warmth.\n\n"
            "EMOTION: This is the emotional center. Genuine compassion on 'I get it.' Not pity — solidarity.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words. 'I get it' warmer and softer than surrounding lines.\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens. A thread of warmth visible on 'I get it.'\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Not the police. Your family. I get it. Checking this does not change that."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes on lens. A return to steady factual directness. The pivot from emotion to information.\n"
            "BODY LANGUAGE: Completely still. Head level. 'Sexually abused by staff' spoken without flinching.\n"
            "VOICE STYLE: Same warm voice. Plain and steady. Naming what happened — clear, not dramatized.\n"
            "TONE: Informational but not cold. She is stating the legal fact as a peer, not a lawyer.\n"
            "SPEED: ~2.2 wps. Even. Slight pause after 'prisons.'\n\n"
            "EMOTION: Flat calm with resolve. The emotional processing is behind her. This is the offer.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "There is a lawsuit for women sexually abused by staff inside California women\'s prisons."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Eyes on lens. A direct address — she is talking to exactly one person.\n"
            "BODY LANGUAGE: Still. 'Without a single person in your life ever finding out' — slight lean of emphasis. No gesture.\n"
            "VOICE STYLE: Same warm voice. 'You may qualify' — plain, not salesy. 'Finding out you looked' — the key phrase, delivered carefully.\n"
            "TONE: The central promise of the whole ad — this stays secret. Delivered like a guarantee, not a pitch.\n"
            "SPEED: ~2.1 wps. Deliberate. Full emphasis on 'without a single person in your life ever finding out.'\n\n"
            "EMOTION: Quiet conviction. She wants this person to believe they are safe. No sales energy.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words. NO commercial inflection on 'qualify.'\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You may qualify for significant potential compensation without a single person in your life ever finding out you looked."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes on lens. Each phrase is its own landing. She is removing fears one at a time.\n"
            "BODY LANGUAGE: Completely still. Each 'No' delivered with a flat finality — no gesture, just the word.\n"
            "VOICE STYLE: Same warm voice. Each phrase clipped and clean. 'Nobody calls your house' — the last one, final.\n"
            "TONE: Four quiet reassurances in a row, each one removing a specific fear. Matter-of-fact.\n"
            "SPEED: ~2.0 wps. Natural pause between each sentence. Each one its own beat.\n\n"
            "EMOTION: Calm authority. She has answered these fears before. No performance — just clarity.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words.\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens.\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "There is no public filing. No letter in the mail. Nobody knocks on your door. Nobody calls your house."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes on lens. Open and still. The gentlest moment in the ad.\n"
            "BODY LANGUAGE: Completely still. 'This stays yours' — spoken with a quiet care, like handing something back.\n"
            "VOICE STYLE: Same warm voice. Quieter. 'Completely private' plain. 'This stays yours' — the warmest delivery.\n"
            "TONE: Quiet close. No urgency. She is handing the viewer their own privacy back as a gift.\n"
            "SPEED: ~1.9 wps. Slowest. Natural pause after each sentence. Silence after 'Tap below.'\n\n"
            "EMOTION: Warm stillness. A soft release — like the weight has been lifted. 'This stays yours' carries genuine care.\n\n"
            "AUDIO CRITICAL: Full projection. ONLY exact words. NOT upbeat, NOT commercial, NOT TV-ad delivery.\n\n"
            "EYES LOCK: Warm hazel-brown eyes OPEN and on lens. Slight warmth in the eyes on 'This stays yours.'\n\n"
            "CRITICAL — NO SMILE: ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "It is completely private. It takes one minute to fill out the form. This stays yours. Tap below."\n\n'
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
    print(f"CA Women CWL4_F3 cam1 — Latina 42, Peruvian/Andean (Sacramento apt) | veo-3.1-lite | {len(CLIPS)} clips → {OUT}\n")

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
