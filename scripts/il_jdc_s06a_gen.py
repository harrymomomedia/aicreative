"""
Script 06 — Persona A (urban_sidewalk_v3) — 10 clips × 8s
Veo 3.1 Fast via useapi.net Google Flow
9:16 portrait, startImage anchor
"""
import os, sys, time, requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

USEAPI_TOKEN = os.environ.get("USEAPI_TOKEN", "user:2478-GVIbsJwTLOJXBFuSQRV3a")
HEADERS = {"Authorization": f"Bearer {USEAPI_TOKEN}", "Content-Type": "application/json"}
OUT = Path("outputs/il_jdc_script06_a")
OUT.mkdir(exist_ok=True)

ANCHOR = "user:2478-email:666c6f776d6f6d6f6d6564696140676d61696c2e636f6d-image:df960c8c-7504-499e-80bf-4ba62b5b4a3d"

CLIPS = [
    {
        "n": 1,
        "dialogue": "I'm 36 years old. I was just a kid when I was in Illinois juvenile center.",
        "prompt": """GAZE: Locked directly into the lens from the first frame. Steady and unflinching.
BODY LANGUAGE: Completely still. Slight weight shift back — the posture of someone who has carried this a long time. Jaw relaxed but set.
VOICE STYLE: Mid-30s man, deep warm voice, street-level. Reflective and grounded, not performative.
TONE: Heavy opening statement. He is placing himself in front of the viewer. This is a confession, not a pitch.
SPEED: ~2.0 wps. Each sentence gets a beat of silence.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection into the phone mic. NOT whispered. Clean foreground audio.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy (never ill-ih-NOY). "juvenile" = JOO-veh-nile.

CRITICAL — NO SMILE EVER: Mouth stays in a flat, heavy neutral line throughout. ZERO upturned corners.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "I'm 36 years old. I was just a kid when I was in Illinois juvenile center."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 2,
        "dialogue": "I did my best to put it behind me, you know? I thought it was just a dark chapter that was closed.",
        "prompt": """GAZE: Eyes drop briefly — remembering — then return to lens, soft and steady.
BODY LANGUAGE: Slight exhale at the start. Shoulders carry weight. Head tilts very slightly. A tiny, tired nod on "dark chapter."
VOICE STYLE: Same voice, softer. Lower register. Almost private — like he is talking to one person who understands.
TONE: The quiet resignation of someone who buried something hard and moved on. A little bit of relief in saying it out loud.
SPEED: ~2.1 wps, unhurried. "You know?" gets a natural pause after.

AUDIO CRITICAL: Voice clear and audible despite soft tone. Not inaudible — fills the foreground.

CRITICAL — NO SMILE EVER: Mouth stays in a heavy, flat neutral. ZERO upturned corners.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "I did my best to put it behind me, you know? I thought it was just a dark chapter that was closed."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 3,
        "dialogue": "Then a friend of mine sent me an article. He said, You need to check this out.",
        "prompt": """GAZE: Eyes lift slightly — the memory of the moment. Stays on lens, a small flash of something — surprise mixed with recognition.
BODY LANGUAGE: Very subtle lean forward. The energy shifts slightly upward — not excited, but a shift. Like the memory activates something.
VOICE STYLE: Same voice, slight lift in register. Not performative — just the natural change when recalling a turning-point moment.
TONE: Discovery. The hinge point. Something arrived that changed the trajectory.
SPEED: ~2.1 wps. Natural storytelling pacing.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. The quoted phrase "You need to check this out" is spoken as if quoting his friend's voice — same register, not as an announcer. Stop after the final word.

SPOKEN DIALOGUE: "Then a friend of mine sent me an article. He said, You need to check this out."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 4,
        "dialogue": "It said that men who were abused in Illinois youth facilities are finally able to seek a settlement for what happened back then.",
        "prompt": """GAZE: Eyes steady on lens throughout. The look of someone reading something aloud from memory — precise, serious.
BODY LANGUAGE: Head still. A very slow single nod mid-sentence on "finally able" — the weight of that word landing.
VOICE STYLE: Slightly more deliberate, slightly more measured — reciting something official that hit hard when he first read it.
TONE: Factual gravity. The moment information becomes personal. He is not editorializing — he is recounting.
SPEED: ~2.6 wps. Slightly faster — an informational read-back that flows naturally.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

PRONUNCIATION LOCK: "Illinois" = ILL-ih-noy. "facilities" = fuh-SIL-ih-teez.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no trailing words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "It said that men who were abused in Illinois youth facilities are finally able to seek a settlement for what happened back then."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 5,
        "dialogue": "I'm reading it and it hits me. That's exactly what I went through.",
        "prompt": """GAZE: Eyes stay on lens but go slightly inward — the gaze of someone seeing something in their own memory. Then refocuses.
BODY LANGUAGE: A single slow blink mid-clip as the realization lands. Jaw tightens slightly. Very still otherwise — the stillness of impact.
VOICE STYLE: Quieter. The most personal moment in the video. Voice drops — not weak, just private.
TONE: Revelation and the weight of recognition. Not dramatic — just true. The quiet of being seen after years of hiding.
SPEED: ~1.6 wps. Very deliberate. Each word carries. Pause between sentences.

AUDIO CRITICAL: Voice clear and audible despite the soft intimate tone. Not inaudible — still fills the foreground.

CRITICAL — NO SMILE EVER: ZERO smile. Expression is heavy, inward, still.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "I'm reading it and it hits me. That's exactly what I went through."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 6,
        "dialogue": "It wasn't just me. It was happening to a lot of us in there. There's a form you fill out online.",
        "prompt": """GAZE: Refocused back to lens. Direct. He is moving toward the viewer now — drawing them into action.
BODY LANGUAGE: Very subtle straightening. Energy shifts from inward to outward — from "my story" to "our story." A small deliberate nod on "a lot of us."
VOICE STYLE: Slightly more forward — same register but more present, more connected. He is speaking FOR others now, not just about himself.
TONE: The pivot from personal pain to shared truth. Then immediately into practical — "There is something you can do right now."
SPEED: ~2.3 wps. First two sentences slow; third sentence slightly quicker — momentum building.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "It wasn't just me. It was happening to a lot of us in there. There's a form you fill out online."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 7,
        "dialogue": "You just list where you were and what happened. That's the whole process. Nobody is going to harass you or call your house.",
        "prompt": """GAZE: Eyes on lens, steady and informational — the clear look of someone explaining something simple.
BODY LANGUAGE: Relaxed and open. Slight nod on "that's the whole process" — affirming, like a reassurance. Head stays steady.
VOICE STYLE: Calm and clear. Practical friend voice — the tone of explaining something easy that sounded hard.
TONE: Demystification. Reassurance. The relief of simplicity. Each sentence strips away another barrier.
SPEED: ~2.5 wps, even pacing. List-like clarity.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — NO SMILE EVER: ZERO smile. Warm but neutral expression.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "You just list where you were and what happened. That's the whole process. Nobody is going to harass you or call your house."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 8,
        "dialogue": "It's private. You're just seeing if you have a claim. I finished it in about two minutes.",
        "prompt": """GAZE: Direct, soft, reassuring gaze into the lens throughout.
BODY LANGUAGE: Very slight head shake on "It's private" — emphasizing privacy. Then settles into calm stillness. A small nod on "two minutes" — confident, easy.
VOICE STYLE: Warm, low, unhurried. The tone of someone removing the last barrier of fear.
TONE: Safety and ease. The biggest hesitation (privacy, judgment) being quietly dismantled.
SPEED: ~2.1 wps. Slow and deliberate on "It's private." Slightly brisker on "two minutes" — casual confidence.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. Clean foreground audio.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "It's private. You're just seeing if you have a claim. I finished it in about two minutes."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 9,
        "dialogue": "Look, I'm just saying. Don't think you missed your chance. I thought the clock had run out, but it hasn't.",
        "prompt": """GAZE: Eyes locked directly into lens — the most direct, personal look of the video. He is talking to ONE person.
BODY LANGUAGE: Very slight forward lean at the start. Settles back into stillness. Deliberate, unhurried. A slow shake of the head on "but it hasn't."
VOICE STYLE: Same voice, slightly warmer — the quiet urgency of a friend who made it through and wants the same for you.
TONE: Quiet urgency bleeding into compassion. NOT salesy. NOT energetic. The last word of someone who knows what it cost to wait.
SPEED: ~2.0 wps. Each sentence lands separately. "But it hasn't" — even slower, let it breathe.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY at FULL conversational projection. NO rising inflection. NOT TV-ad voice. Calm and private.

CRITICAL — NO SMILE EVER: ZERO upturned corners. ZERO smile throughout.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "Look, I'm just saying. Don't think you missed your chance. I thought the clock had run out, but it hasn't."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
    {
        "n": 10,
        "dialogue": "Tap the button. See if you qualify.",
        "prompt": """GAZE: Eyes on lens. Soft, still, completely present. The quietest moment in the video.
BODY LANGUAGE: Completely still. No lean. The stillness of someone who has said everything that needed to be said. Face open and calm.
VOICE STYLE: Warm, low, private. The softest clip. Like he is whispering a favor to one person.
TONE: Compassion. Gentle CTA. A personal favor, not an ad.
SPEED: ~1.2 wps. Very slow. Each phrase has a FULL pause after it. NOT commercial. NOT energetic.

AUDIO CRITICAL: He speaks CLEARLY AUDIBLY despite soft tone. NOT inaudible — still fills the foreground. NO rising/upbeat inflection on either phrase. Delivered like a quiet afterthought from someone who cares.

CRITICAL — NO SMILE EVER: ZERO smile. Eyes carry the warmth, not the mouth.

CRITICAL — DIALOGUE LOCK: English only, no fillers, no extra words, no trailing words. Speak ONLY these words in order. Stop after the final word.

SPOKEN DIALOGUE: "Tap the button. See if you qualify."

No on-screen text, no captions, no subtitles, no watermarks.""",
    },
]


# ── API helpers ──────────────────────────────────────────────────────────────
def submit_clip(clip):
    n = clip["n"]
    out_path = OUT / f"clip{n}.mp4"
    if out_path.exists() and out_path.stat().st_size > 100_000:
        print(f"  clip{n}: already exists ({out_path.stat().st_size//1024}KB), skipping")
        return n, str(out_path), "skipped"

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
    print(f"  clip{n}: submitted → {job_id[:50]}…", flush=True)
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
    print(f"  clip{n}: downloaded → {size//1024}KB")
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


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generating {len(CLIPS)} clips → {OUT}")
    print(f"Model: veo-3.1-fast | Anchor: persona_A_urban_sidewalk_v3\n")

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
