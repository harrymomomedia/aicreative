"""
CA Women CWL9_F2 — 'Chowchilla Confession' — 13 clips
Persona: CWL9_F2 — Cuban-American 55, Bay Area front porch selfie
13 clips × 8s | useapi google-flow veo-3.1-lite-low-priority (free tier)
9:16 portrait | confession register (off-cam storytelling → direct lens CTA)
~88s total | no disclaimer
"""
import os, sys, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from googleflow_client import upload_asset

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

OUT = Path("outputs/ca_women_cwl9f2_cam1")
OUT.mkdir(parents=True, exist_ok=True)

ANCHOR_IMG = Path("outputs/ca_women_latina_personas_v9/persona_CWL9_F2.jpg")
MGID_FILE  = OUT / "anchor_mgid.txt"

# Clip dialogue split (em-dashes → periods per CLAUDE.md):
# C1:  "If you were at Chow-chilluh or any other women's prison in California,"
# C2:  "I'm going to say something that's going to make a lot of women uncomfortable."
# C3:  "When I was at Central California Women's Facility, there was a correctional officer."
# C4:  "Not even a CO, actually. He was medical staff. Who made me feel like he was the only person in that building"
# C5:  "who saw me as human. Extra snacks. Checking on me after lights out."
# C6:  "Letting small violations slide. I thought it was kindness until I was sexually abused."
# C7:  "I carried that silence for years. Then I saw this. The state of California paid out over one hundred million dollars"
# C8:  "because what happened to me happened to hundreds of us. Correctional officers. Medical staff. Contractors."
# C9:  "It didn't matter what title they had. But there is a deadline. And once it passes, you can't file. Period."
# C10: "So if a staff member, any staff member, did something to you that you never asked for,"
# C11: "take the 30-second quiz below. No phone call. No lawyer showing up at your door. No court."
# C12: "Just answer a few questions privately and see if your case qualifies for significant potential compensation."
# C13: "It's free. It's confidential. Nobody in your life will ever know unless you want them to. Tap below."

EYE_LOCK = (
    "EYES LOCK: Warm hazel-brown eyes stay OPEN and the SAME color throughout. "
    "She does NOT close her eyes during dialogue.\n\n"
)
NO_SMILE = "CRITICAL — NO SMILE: Mouth stays in a soft neutral line throughout. ZERO upturned corners.\n\n"
AUDIO    = (
    "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
    "Clean clear audio that fills the foreground.\n\n"
)
DLG_LOCK = (
    "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words, no improvisation. "
    "STOP speaking after the final word.\n\n"
)
NO_TEXT  = "No on-screen text, no captions, no subtitles, no watermarks."

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Looking DIRECTLY into the camera lens from the first frame. "
            "Eyes carry a focused, quiet authority — she is about to say something real.\n"
            "BODY LANGUAGE: Still. A brief settling before she begins. Chin level. No tilt.\n"
            "VOICE: Warm, lived-in 55-year-old woman. Medium pitch. Measured and unhurried.\n"
            "TONE: Grounded. Addressing a specific person — a woman who was there.\n"
            "SPEED: ~2.2 wps. Each word deliberate.\n\n"
            "EMOTION: Calm authority. She is calling someone in.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + "PRONUNCIATION LOCK: 'Chow-chilluh' = Chowchilla (CHOW-chill-uh).\n\n"
            + 'SPOKEN DIALOGUE: "If you were at Chow-chilluh or any other women\'s prison in California,"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Still directly into the lens. Eyes slightly more weighted — she knows this will land.\n"
            "BODY LANGUAGE: A fractional forward lean, barely visible. Chin steady. "
            "Eyes hold through the full sentence.\n"
            "VOICE: Same woman. Tone drops slightly — this is the honest part.\n"
            "TONE: Measured discomfort. Not anger. She is acknowledging something real.\n"
            "SPEED: ~2.2 wps. Unhurried.\n\n"
            "EMOTION: The quiet before an honest thing is said.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "I\'m going to say something that\'s going to make a lot of women uncomfortable."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Shifts slightly off-camera — looking left of the lens, into memory. "
            "She is no longer addressing the viewer. She is remembering.\n"
            "BODY LANGUAGE: A barely perceptible head turn left. Shoulders still. "
            "Something settles in her face — she is going back there.\n"
            "VOICE: Same woman. Quieter now. The storytelling register.\n"
            "TONE: Quiet and personal. She is inside the memory, not performing it.\n"
            "SPEED: ~2.0 wps. Measured. Natural pause after the sentence.\n\n"
            "EMOTION: The stillness of someone going back to a place they'd rather not.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "When I was at Central California Women\'s Facility, there was a correctional officer."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Off-camera, slightly left — still inside the memory. "
            "Eyes carry a complicated weight — something that confused her for a long time.\n"
            "BODY LANGUAGE: A small shake of the head on 'Not even a CO.' — correcting herself. "
            "Jaw settles on 'medical staff.' Slight brow crease. She is placing this carefully.\n"
            "VOICE: Same woman. Unhurried. Almost working through it as she speaks.\n"
            "TONE: Conflicted recollection. She is naming something that didn't make sense then.\n"
            "SPEED: ~2.0 wps. Natural pauses between sentences.\n\n"
            "EMOTION: The confusion of a memory that still hasn't fully landed.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "Not even a CO, actually. He was medical staff. '
            + 'Who made me feel like he was the only person in that building"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Off-camera, eyes low or slightly left — the most uncomfortable territory. "
            "She is saying things she hasn't said in a long time.\n"
            "BODY LANGUAGE: The quietest clip. A fractional breath before 'Extra snacks.' "
            "On 'after lights out,' the jaw tightens almost imperceptibly. Eyes stay low-steady.\n"
            "VOICE: Same woman. Softest register so far. These words cost something.\n"
            "TONE: Subdued. She is listing things that felt kind. They didn't feel wrong yet.\n"
            "SPEED: ~1.8 wps. Each item its own beat.\n\n"
            "EMOTION: The remembered confusion of being singled out in a place where no one sees you.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "who saw me as human. Extra snacks. Checking on me after lights out."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes slightly down at the start — then returning slowly to off-camera level "
            "on 'until I was sexually abused.' Not looking away. Just settling.\n"
            "BODY LANGUAGE: The most still clip of the ad. A long breath before she starts. "
            "On 'I thought it was kindness,' a micro-nod — she did think that. "
            "On 'sexually abused,' gaze holds steady. She does not look away.\n"
            "VOICE: Same woman. Most subdued. Not broken — just honest.\n"
            "TONE: Quiet disclosure. She is not performing pain. She is stating a fact she carried alone.\n"
            "SPEED: ~1.6 wps. The slowest speech of the confession section.\n\n"
            "EMOTION: The weight of something finally said plainly.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "Letting small violations slide. I thought it was kindness until I was sexually abused."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Begins slightly off-camera — then on 'Then I saw this' her eyes return "
            "slowly to the lens. By 'one hundred million dollars' she is looking directly at us.\n"
            "BODY LANGUAGE: On 'Then I saw this,' a subtle physical settling — she lands back. "
            "A barely visible breath of disbelief that became resolve. Eyes return forward.\n"
            "VOICE: Same woman. Tone shifts — quieter but fuller. The turn of the ad.\n"
            "TONE: Quiet discovery. Not triumphant — something closer to vindication.\n"
            "SPEED: ~2.2 wps. Natural pause between 'for years.' and 'Then I saw this.'\n\n"
            "EMOTION: The moment a long silence finds a name.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "I carried that silence for years. Then I saw this. '
            + 'The state of California paid out over one hundred million dollars"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Directly into the lens. Eyes even and steady — she is connecting now.\n"
            "BODY LANGUAGE: A fractional nod after 'hundreds of us.' "
            "On 'Contractors.' the jaw sets — the scope is bigger than one man.\n"
            "VOICE: Same woman. Fuller now — the turn is complete.\n"
            "TONE: Grounded authority. She names each category deliberately. They all count.\n"
            "SPEED: ~2.0 wps. Brief beat between each noun category.\n\n"
            "EMOTION: The relief of a story that isn't just hers.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "because what happened to me happened to hundreds of us. '
            + 'Correctional officers. Medical staff. Contractors."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Directly into the lens. Eyes forward and steady — urgency, not alarm.\n"
            "BODY LANGUAGE: On 'there is a deadline,' a barely visible forward lean. "
            "On 'Period.' — completely still. Eyes hold. That's all.\n"
            "VOICE: Same woman. Most direct register. Not shouting — clear.\n"
            "TONE: Factual urgency. She is not scaring — she is informing. "
            "'Period.' is not dramatic. It is simply final.\n"
            "SPEED: ~2.2 wps. Clean and even. 'Period.' has its own full beat.\n\n"
            "EMOTION: The weight of a closing door — said plainly so it's heard.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "It didn\'t matter what title they had. '
            + 'But there is a deadline. And once it passes, you can\'t file. Period."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 10,
        "prompt": (
            "GAZE: Directly and warmly into the lens — she is speaking to one specific woman now.\n"
            "BODY LANGUAGE: A subtle softening around the eyes on 'did something to you.' "
            "She is not accusing — she is opening a door.\n"
            "VOICE: Same woman. Softer now. The CTA is not a pitch — it is an invitation.\n"
            "TONE: Quiet, direct, personal. She is speaking to one woman at a time.\n"
            "SPEED: ~2.0 wps. Unhurried. The sentence ends — she stops.\n\n"
            "EMOTION: A private conversation with someone who understands.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "So if a staff member, any staff member, '
            + 'did something to you that you never asked for,"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 11,
        "prompt": (
            "GAZE: Directly into the lens — calm and even. She is removing every barrier.\n"
            "BODY LANGUAGE: Still. A brief natural pause between each 'No.' statement. "
            "Eyes stay steady and present throughout.\n"
            "VOICE: Same woman. Even and plain. NOT commercial. NOT TV-ad delivery.\n"
            "TONE: Quiet reassurance. Each 'No' removes a fear she knows the viewer has.\n"
            "SPEED: ~2.0 wps. Each 'No.' lands cleanly. No rushing.\n\n"
            "EMOTION: The relief of something being made simple.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "take the 30-second quiz below. '
            + 'No phone call. No lawyer showing up at your door. No court."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 12,
        "prompt": (
            "GAZE: Directly into the lens. Eyes warm and even — she is nearly done.\n"
            "BODY LANGUAGE: Completely still. A slight settling before she speaks. "
            "Eyes hold through the end of the sentence.\n"
            "VOICE: Same woman. Quiet, plain, non-commercial.\n"
            "TONE: Factual and calm. 'Significant potential compensation' — not a promise, a possibility.\n"
            "SPEED: ~2.0 wps. Even. NOT upbeat. NOT emphasizing 'compensation.'\n\n"
            "EMOTION: The quiet close of a door left open for someone.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "Just answer a few questions privately and see if your case '
            + 'qualifies for significant potential compensation."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 13,
        "prompt": (
            "GAZE: Directly into the lens — the most personal gaze of the ad. "
            "Warm and steady. She means every word.\n"
            "BODY LANGUAGE: Still. A barely visible nod on 'Tap below.' "
            "Mouth softly closed after she finishes. No performance.\n"
            "VOICE: Same woman — quietest and warmest register. NOT commercial.\n"
            "TONE: Quiet, private close. She steps back. The final gift is ease.\n"
            "SPEED: ~1.8 wps. Full pause after 'confidential.' 'Tap below.' — the softest invitation.\n\n"
            "EMOTION: Warm stillness. She has said what needed to be said.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + "NO commercial inflection on 'free', 'confidential', or 'Tap below.' "
            + "Deliver like a quiet afterthought, same subdued register throughout.\n\n"
            + 'SPOKEN DIALOGUE: "It\'s free. It\'s confidential. '
            + 'Nobody in your life will ever know unless you want them to. Tap below."\n\n'
            + NO_TEXT
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
    print("CA Women CWL9_F2 — 'Chowchilla Confession'")
    print("Persona: Cuban-American 55 — Bay Area front porch selfie")
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

    total = len(CLIPS)
    print(f"\nCompleted: {len(results)}/{total}")
    for n in sorted(results):
        print(f"  clip{n}: {results[n]}")
    if len(results) < total:
        missing = [c["n"] for c in CLIPS if c["n"] not in results]
        print(f"\nMissing: clips {missing} — re-run to retry (skip-if-exists active)")
