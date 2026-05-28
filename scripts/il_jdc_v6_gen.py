"""
IL JDC Script V6 — Persona G (brick_wall_closeup_v2) — 7 clips × 8s
"Sixty seconds could be worth six figures."
Veo 3.1 Fast via useapi.net Google Flow
"""
import os, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/il_jdc_v6_g")
OUT.mkdir(exist_ok=True)

ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:e8141e6a-de5b-41ad-a55e-fca41845f4c6"

CLIPS = [
    {
        "n": 1,
        "prompt": """GAZE: Locked into the lens from frame one. Steady, heavy, daring the viewer to keep watching.
BODY LANGUAGE: Arms crossed, weight leaned back into the brick wall. Still and grounded. A slight chin tilt — confident, not aggressive.
VOICE STYLE: Late-30s man, deep warm voice, street-level Chicago cadence. Deliberate and controlled.
TONE: Pattern interrupt. He is making a claim and daring you to doubt it. Quiet authority.
SPEED: ~1.8 wps. "Six figures" lands slowly. "Hear me out" is flat and direct.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection into the phone mic. NOT whispered. Clean foreground audio.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout. Does NOT close eyes during dialogue.

CRITICAL — NO SMILE EVER: Mouth stays in a flat heavy neutral line. ZERO upturned corners.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "Sixty seconds could be worth six figures. Hear me out."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 2,
        "prompt": """GAZE: Eyes on lens, steady and serious. The look of someone laying down facts.
BODY LANGUAGE: Arms still crossed. Near-still. Slight lean off the wall on "locked up" — weight shifts forward slightly then settles back.
VOICE STYLE: Same deep voice. Drops half a register. Calling out something real.
TONE: Naming the situation directly. No drama. Just fact.
SPEED: ~2.0 wps. "Illinois juvenile spot" lands deliberately.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "If you was a kid locked up in any Illinois juvenile spot."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 3,
        "prompt": """GAZE: Direct into the lens. Eyes go slightly heavier on "put hands on you." Holds the gaze after.
BODY LANGUAGE: Jaw tightens slightly on "put hands on you." Arms stay crossed — controlled stillness. The weight of naming something that happened.
VOICE STYLE: Same voice, slightly lower. This is the hardest sentence. He is saying it plainly because it has to be said.
TONE: Grave and direct. Not dramatic. Not performative. Just naming the truth with a man who lived it.
SPEED: ~1.9 wps. "Put hands on you in there" lands slow and deliberate.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "And a staff member, guard, or counselor put hands on you in there."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 4,
        "prompt": """GAZE: Eyes lift slightly — forward and more present. Delivering important information directly.
BODY LANGUAGE: Very small forward lean on "right now." Arms still crossed. The energy shifts from heavy to purposeful.
VOICE STYLE: Same deep voice, lifts just slightly. Informational but still intimate — not a sales tone.
TONE: Important news delivered quietly. Something is happening and he wants this person to know.
SPEED: ~2.1 wps. "Right now" gets slight emphasis. Each "No" lands as a short staccato.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy. "compensation" = com-pen-SAY-shun.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "Illinois is paying significant potential compensation right now. No police report. No paperwork."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 5,
        "prompt": """GAZE: Direct into lens, steady. The look of someone confirming what the viewer already suspected.
BODY LANGUAGE: Slight single nod on "that's the point." Near-still otherwise. Arms still crossed at chest.
VOICE STYLE: Matter-of-fact. Calm street logic. Naming the system's failure plainly.
TONE: Validation. He is explaining WHY they don't know about this — the cases were buried. Not anger. Just truth.
SPEED: ~2.0 wps. "That's the point" lands flat and final.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "Most of these cases never even made it to court. That's the point."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 6,
        "prompt": """GAZE: Eyes stay on lens, soft and reassuring. Stripping away the last hesitations one by one.
BODY LANGUAGE: Arms still crossed but posture opens slightly — the difference between guarded and settled. Head level.
VOICE STYLE: Same voice, slightly warmer and more open. Practical friend voice — the tone of making something simple.
TONE: Relief. Removing every barrier. Each phrase is a door being opened. "100% private" lands as reassurance.
SPEED: ~2.2 wps. Even, matter-of-fact pacing. "100% private" slightly slower.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "No win, no fee. Costs you nothing to look. Takes a minute, stays 100% private."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 7,
        "prompt": """GAZE: Eyes directly into the lens. Soft, completely still, completely present. The quietest most direct look in the video.
BODY LANGUAGE: Completely still. Arms crossed. No lean. Face open and settled. Everything has been said. This is the only thing left.
VOICE STYLE: Warm, low, private. NOT commercial. NOT energetic. The softest clip.
TONE: A personal favor to one person. Not an ad. Just a quiet invitation from someone who knows.
SPEED: ~1.4 wps. Very slow. Full breath between each sentence. Zero rising inflection.

AUDIO CRITICAL: Speaks CLEARLY AUDIBLY despite soft tone. NOT inaudible. Zero rising inflection. Zero smile in the voice.

CRITICAL — EYES OPEN AND ON CAMERA: Eyes stay OPEN looking DIRECTLY at the lens throughout.

CRITICAL — NO SMILE EVER: ZERO smile. Eyes carry warmth, not the mouth.

CRITICAL — DIALOGUE LOCK: English only. No fillers. No extra words. No trailing words. Speak ONLY the words below in order and STOP after the final word.

SPOKEN DIALOGUE: "Tap below. See what comes back."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
]


def submit_clip(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: already exists ({out_path.stat().st_size // 1024}KB), skipping")
        return n, out_path, "skipped"

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
        raise RuntimeError(f"Submit clip{n} failed: {r.status_code} {r.text[:300]}")
    job_id = r.json().get("jobid")
    if not job_id:
        raise RuntimeError(f"clip{n} no jobid: {r.text[:300]}")
    print(f"  clip{n}: submitted → {job_id[:55]}…", flush=True)
    return n, job_id, "submitted"


def poll_job(job_id, n, timeout=600, interval=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = requests.get(f"https://api.useapi.net/v1/google-flow/jobs/{job_id}",
                         headers=HEADERS, timeout=30)
        if r.status_code != 200:
            time.sleep(interval)
            continue
        data = r.json()
        status = data.get("status", "")
        resp = data.get("response", {})
        if status == "completed":
            media = resp.get("media") or [{}]
            video_url = media[0].get("videoUrl", "") if media else ""
            if video_url:
                return video_url
            raise RuntimeError(f"clip{n} completed but no videoUrl: {data}")
        elif status == "failed":
            raise RuntimeError(f"clip{n} FAILED: {data.get('error', data)}")
        else:
            pct = data.get("progressRatio", "?")
            eta = data.get("estimatedTimeToStartSeconds", "?")
            print(f"    clip{n}: {status} ({pct}) eta={eta}s …", flush=True)
            time.sleep(interval)
    raise TimeoutError(f"clip{n} timed out after {timeout}s")


def download_clip(url, n):
    out_path = OUT / f"clip{n}.mp4"
    r = requests.get(url, timeout=120, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    size = out_path.stat().st_size
    print(f"  clip{n}: downloaded → {size // 1024}KB")
    return str(out_path)


def generate_clip(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: already exists, skipping")
        return n, str(out_path)
    _, job_id, status = submit_clip(clip)
    if status == "skipped":
        return n, str(out_path)
    video_url = poll_job(job_id, n)
    path = download_clip(video_url, n)
    return n, path


if __name__ == "__main__":
    print(f"Generating {len(CLIPS)} clips → {OUT}")
    print(f"Model: veo-3.1-fast | Anchor: persona_G_brick_wall_closeup_v2\n")

    results = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(generate_clip, c): c["n"] for c in CLIPS}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                n, path = fut.result()
                results[n] = path
                print(f"✓ clip{n} done: {path}")
            except Exception as e:
                print(f"✗ clip{n} ERROR: {e}")

    print(f"\nCompleted: {len(results)}/{len(CLIPS)} clips")
    for n in sorted(results):
        print(f"  clip{n}: {results[n]}")
