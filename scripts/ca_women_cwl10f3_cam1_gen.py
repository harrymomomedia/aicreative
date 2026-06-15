"""
CA Women CWL10_F3 — '$115M Settlement' — 11 clips
Persona: CWL10_F3 — Latina 51, warm medium-dark skin, natural curly hair
11 clips × 8s | useapi google-flow veo-3.1-lite-low-priority (free tier)
9:16 portrait | announcer register — direct lens, factual authority + emotion
~88s total | no disclaimer

Clip dialogue plan:
  C1:  "California just paid over one hundred fifteen million dollars to women who were sexually abused by staff inside women's prisons."
  C2:  "And most of the women who qualified had no idea they had a case. This isn't a rumor. This isn't a maybe."
  C3:  "This is public record. One of the largest prison sexual abuse settlements in American history."
  C4:  "If you were incarcerated at either facility and any employee, a correctional officer, medical staff, kitchen worker, contractor, or counselor,"
  C5:  "engaged in sexual contact with you, whether through coercion, threats to your parole, manipulation, or force,"
  C6:  "you may be entitled to significant individual compensation."
  C7:  "But that window does not stay open indefinitely. If you wait too long, you lose your right to compensation permanently."
  C8:  "Tap the button below right now. It's a thirty-second confidential quiz."
  C9:  "No court appearances. No cost. Ever. The legal team only gets paid if you get paid."
  C10: "Your employer, your PO, your family. None of them are contacted or notified."
  C11: "The state already admitted fault. The money is there. The only question is whether you claim it before the deadline passes."
"""
import os, sys, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from googleflow_client import upload_asset

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

OUT = Path("outputs/ca_women_cwl10f3_cam1")
OUT.mkdir(parents=True, exist_ok=True)

ANCHOR_IMG = Path("outputs/ca_women_latina_personas_v10/persona_CWL10_F3.jpg")
MGID_FILE  = OUT / "anchor_mgid.txt"

EYE_LOCK = (
    "EYES LOCK: Warm dark-brown eyes stay OPEN and the SAME color throughout. "
    "She does NOT close her eyes during dialogue.\n\n"
)
NO_SMILE = "CRITICAL — NO SMILE: Mouth stays in a soft neutral line. ZERO upturned corners.\n\n"
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
            "GAZE: Directly into the camera lens from the first frame. "
            "Eyes carry grave, grounded authority — she is delivering a fact.\n"
            "BODY LANGUAGE: Still and centered. Slight weight forward. Chin level.\n"
            "VOICE: Warm authoritative 51-year-old Latina woman. Medium-low pitch. "
            "Measured and unhurried for a statement this serious.\n"
            "TONE: Gravity without drama. This is public record and she needs you to hear it.\n"
            "SPEED: ~2.5 wps. Clear and deliberate on every word.\n\n"
            "EMOTION: The weight of a fact that changes things.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "California just paid over one hundred fifteen million dollars '
            + 'to women who were sexually abused by staff inside women\'s prisons."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Directly into the lens. Eyes shift slightly more personal — "
            "this sentence is for ONE woman watching.\n"
            "BODY LANGUAGE: A barely perceptible lean in on 'had no idea.' "
            "A brief pause before 'This isn't a rumor.' Then eyes steady.\n"
            "VOICE: Same woman. Tone softens briefly on 'had no idea they had a case' — "
            "then firms back up on 'This isn't a rumor.'\n"
            "TONE: Empathy meeting insistence. She knows how this lands.\n"
            "SPEED: ~2.6 wps. 'No idea they had a case' slightly slower.\n\n"
            "EMOTION: The mix of compassion and urgency — knowing something the other person doesn't.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "And most of the women who qualified had no idea they had a case. '
            + 'This isn\'t a rumor. This isn\'t a maybe."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Directly into the lens. Eyes fully settled and steady — "
            "every word here is a declaration.\n"
            "BODY LANGUAGE: Completely still. No movement. She lets the words carry.\n"
            "VOICE: Same woman. Most grounded tone yet — declarative, factual.\n"
            "TONE: Validating. Anchoring. 'I need you to believe this.'\n"
            "SPEED: ~1.9 wps. Each sentence a separate beat.\n\n"
            "EMOTION: The stillness of someone who needs to be believed.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "This is public record. One of the largest prison sexual abuse '
            + 'settlements in American history."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Eyes still on the lens but slightly more angled — "
            "speaking directly to a specific person. Not performing to a crowd.\n"
            "BODY LANGUAGE: A subtle settling before she starts — "
            "she is stepping into the 'if you were there' territory. Brow carries quiet weight.\n"
            "VOICE: Same woman. More careful now — pacing each category deliberately.\n"
            "TONE: Empathetic and specific. She is naming things the viewer has been afraid to name.\n"
            "SPEED: ~2.2 wps. Brief natural pause between each job title.\n\n"
            "EMOTION: The gravity of naming it out loud for the first time.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "If you were incarcerated at either facility and any employee, '
            + 'a correctional officer, medical staff, kitchen worker, contractor, or counselor,"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Slightly off-camera — eyes looking just left of the lens, "
            "as if holding space for the person this happened to. Not avoidant — present.\n"
            "BODY LANGUAGE: The quietest clip. A slow breath before she speaks. "
            "On 'force,' her jaw sets briefly — then releases.\n"
            "VOICE: Same woman. Softest register of the announcement section. "
            "These words are heavy.\n"
            "TONE: Quiet acknowledgment. She is sitting in it with the viewer.\n"
            "SPEED: ~1.9 wps. Each phrase its own beat.\n\n"
            "EMOTION: The recognition of something that was never supposed to be spoken.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "engaged in sexual contact with you, whether through coercion, '
            + 'threats to your parole, manipulation, or force,"\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Eyes return fully to the lens — direct, warm, steady. "
            "She wants the viewer to receive this.\n"
            "BODY LANGUAGE: A barely visible forward lean. Eyes hold. "
            "She is placing this sentence like a gift on a table.\n"
            "VOICE: Same woman. Deliberate and clear. Every word enunciated.\n"
            "TONE: Quiet power. Not triumphant — just certain.\n"
            "SPEED: ~1.1 wps. The slowest clip of the ad. Each word given full weight.\n\n"
            "EMOTION: The moment something that was taken becomes something that can be reclaimed.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "you may be entitled to significant individual compensation."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Directly into the lens. Eyes shift to a measured urgency — "
            "not alarm, but unmistakable importance.\n"
            "BODY LANGUAGE: A barely visible forward lean on 'does not stay open.' "
            "On 'permanently' — completely still. Eyes hold.\n"
            "VOICE: Same woman. Tone becomes fuller and more direct — the stakes are named.\n"
            "TONE: Factual urgency. She is not scaring — she is informing. 'Permanently' lands clean.\n"
            "SPEED: ~2.5 wps. 'Permanently' has its own pause before it.\n\n"
            "EMOTION: The weight of a door about to close.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "But that window does not stay open indefinitely. '
            + 'If you wait too long, you lose your right to compensation permanently."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 8,
        "prompt": (
            "GAZE: Directly into the lens — calm, even, and clear. "
            "Eyes are steady and reassuring.\n"
            "BODY LANGUAGE: Relaxed and still. A gentle nod after 'right now.' "
            "She is making this simple.\n"
            "VOICE: Same woman. Clear and plain — NOT commercial, NOT TV-ad energy.\n"
            "TONE: Calm instruction. She is removing the complexity one piece at a time.\n"
            "SPEED: ~1.8 wps. Each sentence its own clear beat.\n\n"
            "EMOTION: The ease of someone opening a door that seemed locked.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + "NO commercial inflection on 'Tap the button below' or 'quiz'. "
            + "NOT upbeat, NOT rising intonation, NOT TV-ad voice.\n\n"
            + 'SPOKEN DIALOGUE: "Tap the button below right now. '
            + 'It\'s a thirty-second confidential quiz."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 9,
        "prompt": (
            "GAZE: Directly into the lens. Eyes warm and even throughout.\n"
            "BODY LANGUAGE: Still. A brief pause between each 'No' statement. "
            "Eyes hold steady and present.\n"
            "VOICE: Same woman. Even and matter-of-fact.\n"
            "TONE: Quiet reassurance. Each statement removes a fear. "
            "'Ever' lands with its own weight — no upswing.\n"
            "SPEED: ~2.0 wps. Each sentence its own clear landing.\n\n"
            "EMOTION: The relief of something being made simple.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + "NO commercial inflection on 'No cost' or 'only gets paid if you get paid'. "
            + "Deliver flat and factual, same quiet register throughout.\n\n"
            + 'SPOKEN DIALOGUE: "No court appearances. No cost. Ever. '
            + 'The legal team only gets paid if you get paid."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 10,
        "prompt": (
            "GAZE: Directly into the lens — the most personal gaze of the CTA section. "
            "Eyes warm and steady. She is speaking to one person's specific fear.\n"
            "BODY LANGUAGE: Completely still. Eyes hold through the final word. No performance.\n"
            "VOICE: Same woman. Warmest register of the CTA section — not commercial.\n"
            "TONE: Private and personal. She understands the fear of someone finding out.\n"
            "SPEED: ~1.7 wps. Each group of three its own deliberate beat.\n\n"
            "EMOTION: Quiet protection. She is sealing something safe.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + 'SPOKEN DIALOGUE: "Your employer, your PO, your family. '
            + 'None of them are contacted or notified."\n\n'
            + NO_TEXT
        ),
    },
    {
        "n": 11,
        "prompt": (
            "GAZE: Directly into the lens — the most final and settled gaze of the ad. "
            "Eyes carry closure and certainty.\n"
            "BODY LANGUAGE: Completely still. A barely visible breath before the last sentence. "
            "Eyes hold through 'deadline passes.' Then a soft close.\n"
            "VOICE: Same woman. Quietest and most final — NOT commercial. "
            "She is handing something over.\n"
            "TONE: Grounded finality. The state has already moved. The only variable is the viewer.\n"
            "SPEED: ~2.3 wps. 'The only question is' slightly slower.\n\n"
            "EMOTION: Warm certainty. She has said everything. Now she waits.\n\n"
            + AUDIO + EYE_LOCK + NO_SMILE + DLG_LOCK
            + "NO commercial inflection. Deliver like a quiet final truth, NOT a call-to-action rush.\n\n"
            + 'SPOKEN DIALOGUE: "The state already admitted fault. The money is there. '
            + 'The only question is whether you claim it before the deadline passes."\n\n'
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
    print("CA Women CWL10_F3 — '$115M Settlement'")
    print("Persona: Latina 51 — warm medium-dark skin, natural curly hair")
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
