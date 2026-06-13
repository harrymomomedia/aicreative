"""
CA Women CWL5_F2 — Concept 1A — "You Still Flinch At Keys"
Persona: CWL5_F2_v1 — Colombian mestiza 45, bedroom morning selfie
7 clips × 8s | useapi google-flow veo-3.1-lite-low-priority (free tier)
9:16 portrait | emotion-forward, deliberate pacing | no disclaimer
"""
import os, sys, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from googleflow_client import upload_asset

TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

OUT = Path("outputs/ca_women_cwl5f2_c1a_cam1")
OUT.mkdir(parents=True, exist_ok=True)

ANCHOR_IMG = Path("outputs/ca_women_latina_personas_v5/persona_CWL5_F2_v1.jpg")
MGID_FILE = OUT / "anchor_mgid.txt"

# ── clip definitions ───────────────────────────────────────────────────────────
# Clip 1A dialogue split:
#   C1: "If you flinch when you hear keys. If certain sounds still take you right back."
#   C2: "And staff sexually abused you in a California women's prison, you need to hear this."
#   C3: "At Chow-chilluh, Valley State, Folsom, and CIW, the law now recognizes what happened as abuse."
#   C4: "Hundreds of women have already come forward. You don't need a police report."
#   C5: "You don't need a witness. Even if it happened years ago. Even if you never told a single person."
#   C6: "It's free and completely confidential to check if you qualify for significant potential compensation."
#   C7: "Tap below. Just a few questions, alone on your phone."

CLIPS = [
    {
        "n": 1,
        "prompt": (
            "GAZE: Eyes start slightly averted — she hears something offscreen, a flicker of recognition. "
            "Then she turns directly into the lens and holds steady eye contact to the end. "
            "Dark brown eyes stay OPEN and dark throughout.\n"
            "BODY LANGUAGE: Quiet still-ness at the open, a small involuntary stillness, a barely audible "
            "exhale through the nose, then she settles forward and owns the gaze. Soft neutral mouth throughout. "
            "No smile. A faint heaviness at the brow — quiet recognition, not distress.\n"
            "VOICE: Warm lived-in midlife Colombian-American woman, medium-low pitch, slight weight in the voice. "
            "Like she knows this listener personally.\n"
            "TONE: Quiet recognition. The first line ('flinch when you hear keys') carries a slight involuntary "
            "energy — she understands the reflex. The second line ('certain sounds') settles into directness.\n"
            "SPEED: ~2.0 wps. Slow and deliberate. Full natural pause between the two sentences.\n\n"
            "EMOTION: The first beat of acknowledgment — she sees the viewer without them saying a word.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered, "
            "NOT muttered. Clean clear audio that fills the foreground.\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout. She does NOT close her eyes during dialogue.\n\n"
            "CRITICAL — NO SMILE: Mouth stays in a soft neutral line throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers, no extra words, no improvisation. "
            "STOP speaking after the final word.\n\n"
            'SPOKEN DIALOGUE: "If you flinch when you hear keys. If certain sounds still take you right back."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 2,
        "prompt": (
            "GAZE: Direct and steady into the camera lens from the first frame. "
            "Dark brown eyes OPEN and holding eye contact throughout.\n"
            "BODY LANGUAGE: A small lean forward — the delivery of something important. Jaw set softly. "
            "On 'California women's prison' — a fractional pause, a breath of weight. "
            "Mouth neutral or barely parted. No smile.\n"
            "VOICE: Controlled, intentional. Same midlife woman — slightly lower register, more deliberate. "
            "The words carry consequence.\n"
            "TONE: Controlled urgency — not alarm, not a pitch. The register of someone handing you "
            "information they know you need. 'You need to hear this' is plain, not theatrical.\n"
            "SPEED: ~2.1 wps. Each clause lands before the next. Slight breath after 'prison.'\n\n"
            "EMOTION: Quiet gravity. She is not asking permission to say this. She is saying it because it's true.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout. She does NOT close her eyes.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "And staff sexually abused you in a California women\'s prison, '
            'you need to hear this."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 3,
        "prompt": (
            "GAZE: Direct into the lens throughout. Dark brown eyes OPEN and calm.\n"
            "BODY LANGUAGE: Grounded, still. Head level. This is the factual beat — she is naming "
            "facilities clearly, without hesitation. Soft neutral mouth.\n"
            "VOICE: Even, factual. Same woman — slightly more informational register, but still warm, "
            "not newscaster. Each facility name is its own beat.\n"
            "TONE: Grounded authority. She is naming these places with the confidence of someone "
            "who knows they're real. 'The law now recognizes' — quiet finality.\n"
            "SPEED: ~2.0 wps. Measured. Slight natural pause after each facility name.\n\n"
            "EMOTION: Flat calm with resolve. The emotional weight is carried by what the words mean, "
            "not by performance.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "PRONUNCIATION LOCK: 'Chow-chilluh' = two syllables — CHOW then chilluh. "
            "Stress the first syllable, not the second. NOT 'Chow-CHILL-uh.'\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout.\n\n"
            "CRITICAL — NO SMILE: Mouth stays neutral throughout. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "At Chow-chilluh, Valley State, Folsom, and CIW, '
            'the law now recognizes what happened as abuse."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 4,
        "prompt": (
            "GAZE: Direct into the lens. A steady, unhurried delivery. "
            "Dark brown eyes OPEN and on camera throughout.\n"
            "BODY LANGUAGE: Slight release in the shoulders — a micro-breath of affirmation enters. "
            "Not dramatic. Just a fractional softening. On 'Hundreds of women' — a faint swell. "
            "On 'police report' — flat and clean. No smile.\n"
            "VOICE: Slight warmth entering. Same midlife woman — a fraction of reassurance on the first "
            "sentence, then returning to factual on the second. NOT performative warmth. Real.\n"
            "TONE: Two registers: the first sentence carries a whisper of 'you are not alone.' "
            "The second is plain practicality — removing a fear with a fact.\n"
            "SPEED: ~2.2 wps. Each sentence its own beat. Brief natural pause between them.\n\n"
            "EMOTION: The first shift toward hope — small, earned. Not a wave, a thread.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio.\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth. NO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "Hundreds of women have already come forward. '
            'You don\'t need a police report."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 5,
        "prompt": (
            "GAZE: Direct into the lens throughout. Soft and steady. "
            "Dark brown eyes OPEN, dark, unwavering.\n"
            "BODY LANGUAGE: Complete stillness. This is the most vulnerable beat — permission-giving. "
            "On 'You don't need a witness' — a quiet finality. Between the two 'even if' lines — "
            "a real pause, a breath. Mouth softly closed or barely parted. No smile. "
            "The eyes carry a thread of empathy — not pity, not sympathy, recognition.\n"
            "VOICE: Quieter and gentler. Same woman — the energy drops to something more private, "
            "like she's speaking directly to one person. Each sentence its own small space.\n"
            "TONE: Permission. She is handing the listener permission to have not reported, "
            "not to have told anyone. There is no judgment in any syllable.\n"
            "SPEED: ~2.0 wps. Slowest so far. Real natural pause between each sentence.\n\n"
            "EMOTION: Quiet solidarity. The heaviest empathy of the ad — worn lightly.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection. "
            "NOT whispered but genuinely quiet. Clean clear audio.\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN. She does NOT look away or down.\n\n"
            "CRITICAL — NO SMILE: Soft neutral or fractionally downturned corners. "
            "The weight of the words. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "You don\'t need a witness. Even if it happened years ago. '
            'Even if you never told a single person."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 6,
        "prompt": (
            "GAZE: Direct into the lens, calm and matter-of-fact. "
            "Dark brown eyes OPEN and steady throughout.\n"
            "BODY LANGUAGE: Still and grounded. This is the practical close — no urgency, no sell. "
            "Head level. She is stating a simple fact. Mouth neutral throughout. "
            "No performance, no lift in the face.\n"
            "VOICE: Low-key, matter-of-fact. Same woman — the most subdued register of the ad. "
            "NOT announcer, NOT upbeat, NOT commercial. 'Free' gets no emphasis. "
            "'Confidential' is plain. 'Qualify' is NOT salesy. "
            "She delivers this like a quiet practical afterthought.\n"
            "TONE: Factual reassurance. She is removing the last practical barrier — cost and privacy — "
            "with the same plainness as reading off a fact.\n"
            "SPEED: ~2.1 wps. Even, unhurried.\n\n"
            "EMOTION: Grounded quiet. She has said what needed to be said. This is the handing over.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection, NOT whispered. "
            "Clean clear audio. NO commercial inflection on 'qualify' or 'free.'\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout.\n\n"
            "CRITICAL — NO SMILE: Completely neutral mouth. ZERO upturned corners. NOT performative.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after final word.\n\n"
            'SPOKEN DIALOGUE: "It\'s free and completely confidential to check if you qualify '
            'for significant potential compensation."\n\n'
            "No on-screen text, no captions, no subtitles, no watermarks."
        ),
    },
    {
        "n": 7,
        "prompt": (
            "GAZE: Eyes open and into the lens. Quiet and still. "
            "Dark brown eyes OPEN, dark, holding steady.\n"
            "BODY LANGUAGE: Complete stillness. The softest moment in the ad. "
            "'Tap below' delivered like a quiet gesture, not a command. "
            "'Just a few questions' — plain, unhurried, no sell. "
            "Mouth softly closed or barely parted. No smile.\n"
            "VOICE: Same woman — the most minimal energy. Quietest, most private. "
            "Like the last sentence in a conversation between two people who understand each other.\n"
            "TONE: Quiet close. No urgency. No lift. She lets the offer sit.\n"
            "SPEED: ~1.9 wps. Slowest clip. Real pause after 'Tap below.' "
            "Lets each phrase breathe.\n\n"
            "EMOTION: Warm stillness. The weight has passed. She has said everything. "
            "Now she just steps back and lets the viewer decide.\n\n"
            "AUDIO CRITICAL: Speaks CLEARLY AUDIBLY at full conversational projection. "
            "NOT whispered but very quiet. Clean clear audio. "
            "NOT upbeat, NOT commercial, NOT TV-ad delivery on any word.\n\n"
            "EYES LOCK: Dark brown eyes stay dark brown, OPEN throughout.\n\n"
            "CRITICAL — NO SMILE: Soft neutral mouth. ZERO upturned corners.\n\n"
            "CRITICAL — DIALOGUE LOCK: English only. No fillers. STOP after 'phone.'\n\n"
            'SPOKEN DIALOGUE: "Tap below. Just a few questions, alone on your phone."\n\n'
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


def poll(job_id, n, timeout=900, interval=20):
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
    print(f"CA Women CWL5_F2 — Concept 1A 'You Still Flinch At Keys'")
    print(f"Persona: Colombian mestiza 45 — bedroom morning selfie")
    print(f"Model: veo-3.1-lite-low-priority (free, ultra-low-priority queue)")
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
