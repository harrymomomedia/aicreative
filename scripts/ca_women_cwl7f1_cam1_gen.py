"""
CA Women CWL7_F1 — 'Chest Tightening' — 7 clips
Persona: CWL7_F1_cam_v2_3 — Mexican-American 52, Central Valley, indoor kitchen selfie
7 clips × 8s | useapi google-flow veo-3.1-lite-low-priority (free tier)
9:16 portrait | bit emotions, deliberate pacing | no disclaimer
"""
import os, sys, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from googleflow_client import upload_asset

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

OUT = Path("outputs/ca_women_cwl7f1_cam1")
OUT.mkdir(parents=True, exist_ok=True)

ANCHOR_IMG = Path("outputs/ca_women_latina_personas_v7/persona_CWL7_F1_cam_v2_3.jpg")
MGID_FILE = OUT / "anchor_mgid.txt"

# ── clip dialogue split ────────────────────────────────────────────────────────
#  C1: "There are women who did time in California women's prisons."
#  C2: "Women who can't walk past a corrections officer without their chest tightening."
#  C3: "If staff sexually abused you in there, and that's still with you,
#       there's a compensation claim you may qualify for right now."
#  C4: "Chow-chilluh, Valley State, Folsom, and CIW.
#       The law has caught up to what happened behind those walls."
#  C5: "Women who stayed quiet, women who reported and were ignored,
#       women who thought their chance was gone."
#  C6: "Hundreds have already come forward. Your memory alone is enough to check."
#  C7: "Free. Completely private. No one in your life finds out you looked. Tap below."

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Looking directly into the camera lens from the first frame. "
            "Eyes present but carrying a distant quality — like she's speaking from memory "
            "about women she knows about.\n"
            "BODY LANGUAGE: Nearly motionless. One slow breath through the nose before she speaks. "
            "Head still, shoulders settled. A quiet groundedness.\n"
            "VOICE: Warm, lived-in, 52-year-old Mexican-American woman. "
            "Medium-low pitch. Subdued and unhurried.\n"
            "TONE: Distant and reflective. Naming something she knows is true. "
            "Not performing — just stating it.\n"
            "SPEED: ~1.5 wps. Slowest clip. Full space around each word.\n\n"
            "EMOTION: The opening note of recognition — she knows exactly who she is about to speak to.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio that fills the foreground.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color. She does NOT close her eyes during dialogue.\n\n"
            "CRITICAL — NO SMILE: Mouth stays in a soft neutral line throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words, no improvisation. "
            "STOP speaking after the final word.\n\n"
            'SPOKEN DIALOGUE: "There are women who did time in California women\'s prisons."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Directly into the camera lens. Eyes carry a quiet heaviness — a knowing weight.\n"
            "BODY LANGUAGE: One slow blink at the very start, then eyes stay open and steady. "
            "A faint micro-tension in the jaw that gently releases. No other movement.\n"
            "VOICE: Same warm midlife woman. Slightly more inward, a fraction quieter.\n"
            "TONE: Weight of recognition. The physical detail — 'chest tightening' — delivered plainly. "
            "Like naming something everyone in the room already knows.\n"
            "SPEED: ~1.5 wps. Deliberate. Space around each word.\n\n"
            "EMOTION: She knows this feeling is real. The body keeps the record.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Women who can\'t walk past a corrections officer without their chest tightening."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Directly into the camera lens, more present now — making direct eye contact. "
            "She has shifted from describing 'women' to addressing this viewer.\n"
            "BODY LANGUAGE: A barely perceptible forward lean at the word 'you.' "
            "A fractional nod mid-sentence.\n"
            "VOICE: Warmer and more direct. Same midlife woman — register shifts to steady and matter-of-fact.\n"
            "TONE: Controlled clarity. She is handing over a fact. "
            "'May qualify for right now' — plain, no pitch energy.\n"
            "SPEED: ~2.0 wps. Slightly faster than clips 1–2.\n\n"
            "EMOTION: The pivot. She sees the viewer and speaks to them directly. Quiet authority.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners. NOT commercial.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "If staff sexually abused you in there, and that\'s still with you, '
            'there\'s a compensation claim you may qualify for right now."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Steady directly into the lens. Eyes present and even. "
            "This is the factual beat — she is naming real places.\n"
            "BODY LANGUAGE: Almost completely still. Chin very slightly down. "
            "A barely audible breath between the facility list and 'The law has caught up.'\n"
            "VOICE: Measured and factual. Same midlife woman. Each facility name is its own moment.\n"
            "TONE: Grounded authority. She names the facilities with confidence. "
            "'The law has caught up' — quiet finality.\n"
            "SPEED: ~1.8 wps. Brief natural pause between each facility name.\n\n"
            "PRONUNCIATION LOCK: 'Chow-chilluh' = Chowchilla (CHOW-chill-uh). "
            "Valley State. Folsom. CIW. All delivered clearly.\n\n"
            "EMOTION: Flat calm with resolve. The weight is in the facts.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Chow-chilluh, Valley State, Folsom, and CIW. '
            'The law has caught up to what happened behind those walls."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Into the camera lens, eyes carrying building quiet weight.\n"
            "BODY LANGUAGE: A very slight sideways head tilt at the start — thinking through each item. "
            "By 'women who thought their chance was gone,' a fractional softening in the eyes.\n"
            "VOICE: Careful and measured. The rhythm of the list has a natural falling cadence — "
            "each 'women who' phrase slightly quieter than the last.\n"
            "TONE: Gravity building. Not dramatic — like listing women she knows about. "
            "'Thought their chance was gone' lands the heaviest — delivered quietest.\n"
            "SPEED: ~2.0 wps. Each 'women who' clause its own small space.\n\n"
            "EMOTION: Quiet acknowledgment of three distinct silences.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Women who stayed quiet, women who reported and were ignored, '
            'women who thought their chance was gone."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Into the lens, eyes a trace warmer now — a small opening. Like something has released.\n"
            "BODY LANGUAGE: A barely visible exhale after 'come forward.' "
            "A single slow blink. On 'enough to check,' chin very slightly drops and eyes settle.\n"
            "VOICE: Same midlife woman, a touch softer. The most intimate register yet.\n"
            "TONE: A quiet turning point. 'Hundreds have already come forward' — plain good news, "
            "a trace of warmth. 'Your memory alone is enough to check' — the gift, delivered gently.\n"
            "SPEED: ~1.8 wps. Unhurried.\n\n"
            "EMOTION: The first thread of reassurance. A small unlocking.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Hundreds have already come forward. Your memory alone is enough to check."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Into the lens — the softest and most personal gaze of the entire ad. "
            "A quiet, almost tender steadiness.\n"
            "BODY LANGUAGE: Completely still. A tiny barely-visible nod at 'Tap below.' "
            "Mouth softly closed. No performance.\n"
            "VOICE: Same midlife woman — most private and quiet register. "
            "NOT commercial. NOT TV-ad delivery. NOT upbeat. 'Free' gets no emphasis. "
            "'Private' is plain. 'Tap below' is the quietest invitation.\n"
            "TONE: Quiet close. She steps back and leaves the rest to the viewer. "
            "'No one in your life finds out you looked' — quiet assurance, not a selling point.\n"
            "SPEED: ~1.5 wps. Full pause between 'Free.' and 'Completely private.' Between each phrase.\n\n"
            "EMOTION: Warm stillness. The last thing she gives is privacy itself.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection. "
            "NOT whispered but very quiet. Clean clear audio. NO commercial inflection.\n\n"
            "EYES LOCK: Warm medium-dark brown eyes stay OPEN and looking directly into the lens "
            "throughout. Same color.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words. STOP after 'below.'\n\n"
            'SPOKEN DIALOGUE: "Free. Completely private. No one in your life finds out you looked. Tap below."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
]


def get_anchor_mgid():
    if MGID_FILE.exists():
        mgid = MGID_FILE.read_text().strip()
        if mgid:
            print(f"  anchor: reusing mgid {mgid[:40]}…")
            return mgid
    print(f"  anchor: uploading {ANCHOR_IMG} …")
    mgid = upload_asset(str(ANCHOR_IMG), ctype="image/jpeg")
    MGID_FILE.write_text(mgid)
    print(f"  anchor: mgid {mgid[:40]}… saved")
    return mgid


def poll(job_id, n, timeout=1800, interval=20):
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
            url = (media[0].get("videoUrl", "") or
                   media[0].get("video", {}).get("videoUrl", "")) if media else ""
            if url:
                return url
            raise RuntimeError(f"clip{n}: completed but no videoUrl — {data}")
        elif status == "failed":
            raise RuntimeError(f"clip{n} FAILED: {data.get('error', data)}")
        pct = data.get("progressRatio", "?")
        print(f"    clip{n}: {status} {pct} …", flush=True)
        time.sleep(interval)
    raise TimeoutError(f"clip{n} timed out after {timeout}s")


def gen(clip, anchor_mgid):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: exists ({out_path.stat().st_size // 1024}KB), skipping")
        return n, str(out_path)

    payload = {
        "prompt": clip["prompt"],
        "model": "veo-3.1-lite-low-priority",
        "startImage": anchor_mgid,
        "endImage": anchor_mgid,
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
    print(f"  clip{n}: submitted → {str(job_id)[:55]}…", flush=True)

    url = poll(job_id, n)
    r2 = requests.get(url, timeout=300, stream=True)
    r2.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r2.iter_content(65536):
            f.write(chunk)
    print(f"  clip{n}: ✓ saved {out_path.stat().st_size // 1024}KB")
    return n, str(out_path)


if __name__ == "__main__":
    print("CA Women CWL7_F1 — 'Chest Tightening'")
    print("Persona: Mexican-American 52 — Central Valley — indoor kitchen selfie")
    print("Model: veo-3.1-lite-low-priority (free, ultra-low-priority queue)")
    print(f"Output: {OUT}\n")

    anchor_mgid = get_anchor_mgid()
    print()

    results = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen, c, anchor_mgid): c["n"] for c in CLIPS}
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
    if len(results) < len(CLIPS):
        missing = [c["n"] for c in CLIPS if c["n"] not in results]
        print(f"\nMissing: clips {missing} — re-run to retry (skip-if-exists active)")
