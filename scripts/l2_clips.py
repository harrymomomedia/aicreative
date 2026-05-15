"""Generate 10 clips for the l2 Pixar Latina ad (East LA living room) on Poyo veo3.1-fast.

Same 10-line Chowchilla script as the k4 ad, but:
  - More emotional delivery (voice carries weight, slight tremble at peak moments)
  - Faster pace (less pause between sentences, quicker cadence)
  - Same dialogue/eyes/no-smile/NO-TEXT locks
  - "ABSOLUTELY NO ON-SCREEN TEXT" clause baked into every prompt (no clip 3 subtitle bug)

Output: outputs/1777697550119-gyvk6m8/clips_l2/clip{N}_poyo.mp4
"""
import sys, pathlib, concurrent.futures, time
sys.path.insert(0, "/Users/harry/aicreative")
from poyo_client import generate_veo, download

L2_URL = "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778425918894-yusoe94gkcr.png"
OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/clips_l2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHARACTER = (
    "A 52-year-old Latina woman sits on a couch in her living room, alone, taking a selfie video. "
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic. "
    "Dark brown hair shot through with prominent grey streaks, pulled back into a thick low ponytail "
    "with strands escaping at the temples. Faint under-eye shadows, soft crow's feet, penciled "
    "chola-style thin eyebrows, simple silver hoop earrings, no necklace, small chin scar, warm "
    "tan skin. Wears a faded navy zip-up sweatshirt halfway zipped over a plain white tank top."
)

SETTING = (
    "Background: cramped East Los Angeles apartment living room, wood-paneled accent wall behind her, "
    "an older boxy CRT television on a low entertainment center playing a muted telenovela (soft glow), "
    "tall floor lamp with fringed amber shade in the corner, framed photos of her kids in school "
    "uniforms hung above the TV, window with mini-blinds half-drawn, twilight blue light filtering "
    "through from outside. The background remains a fully photorealistic real-world photograph "
    "throughout."
)

NO_TEXT_LOCK = (
    "CRITICAL — ABSOLUTELY NO ON-SCREEN TEXT: The video MUST contain ZERO burned-in text of any "
    "kind. Do NOT render any subtitles, captions, lower-thirds, watermarks, words, letters, banners, "
    "text overlays, speech bubbles, or any text whatsoever anywhere in the frame. The frame must be "
    "100% free of any rendered text or typography. NO subtitle bars at the bottom. NO floating words. "
    "NO captions. This is the most important constraint in this prompt."
)

STYLE_LOCK = (
    "CRITICAL — VISUAL STYLE LOCK: The character is rendered in Pixar/Disney 3D animated character "
    "style throughout the ENTIRE clip from frame one to the final frame. NEVER drift to "
    "photorealistic. Maintain large expressive Pixar eyes with cartoon highlights, soft stylized "
    "facial features, smooth shaded 3D skin, slightly enlarged head proportions in Pixar's "
    "signature character design, painterly hair texture, vivid clean color, Pixar-style subtle "
    "face shading. The CHARACTER is a Pixar 3D animation. The BACKGROUND is a real photograph. "
    "This hybrid composite is maintained for every single frame of the video."
)

CAMERA = "Camera: locked, no movement, no zoom, no pan. Static handheld phone selfie framing."

EYES_LOCK = (
    "CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip her eyes stay OPEN and looking "
    "DIRECTLY at the camera lens. She does NOT close her eyes during dialogue. No blinks longer "
    "than natural."
)

MOUTH_LOCK_NEUTRAL = (
    "CRITICAL — NO SMILE EVER (unless noted in expression): Throughout the entire clip her mouth "
    "stays in a SOFT NEUTRAL LINE between syllables. ZERO upturned corners. ZERO smile."
)

DIALOGUE_LOCK = (
    "CRITICAL — DIALOGUE LOCK: She speaks in ENGLISH ONLY (except where a phonetic respell is "
    "explicitly listed below). Do NOT add any Spanish words, fillers like \"uh\", \"um\", \"like\", "
    "\"you know\", \"so\", or any extra words beyond what is listed. Do NOT add any trailing words "
    "at the end. Speak ONLY the words listed in SPOKEN DIALOGUE below, in order, with no "
    "insertions and no improvisation, and STOP speaking after the final word."
)

PACE = (
    "CRITICAL — PACE: Speak with a slightly faster, more urgent cadence than a typical reflective "
    "monologue. Minimal pauses between sentences. Push through the dialogue with energy and "
    "emotional weight. Don't rush the emotional beats — but everything between them is delivered "
    "quicker than slow contemplative speech."
)

PRONUNCIATION = (
    "Pronunciation respells: \"Chowchilla\" pronounced \"Chow-chilluh\" (three syllables, fused, "
    "soft \"uh\" ending — do NOT drop the final syllable). \"Mija\" pronounced \"Mee-hah\" "
    "(Spanish: /ˈmi.xa/, the \"j\" is an English \"h\" sound)."
)

# Per-clip dialogue + emotional register (more emotional + faster than k4)
CLIPS = {
    1: {
        "tone": "weight in her voice, the past pulling on her — slight tremble on 'fifteen years ago' — eyes carrying memory",
        "closing": "the feeling of: she said it like the weight just landed on her again",
        "dialogue": "I'm fifty. Chow-chilluh was like fifteen years ago for me.",
    },
    2: {
        "tone": "still holding it together but the resolve is cracking — quicker delivery, jaw set",
        "closing": "the feeling of: she had buried this and now it's surfacing",
        "dialogue": "I thought, you know, that part of my life was over. And I moved on.",
    },
    3: {
        "tone": "her sister's name lands hard — eyes glisten momentarily — voice quickens",
        "closing": "the feeling of: a phone notification that changed everything",
        "dialogue": "Then my sister sends me this article. She's like, Mee-hah, you need to look at this.",
    },
    4: {
        "tone": "informational with rising gravity — voice carries weight — slightly faster than reflective",
        "closing": "the feeling of: she is realizing this is about her, not 'them'",
        "dialogue": "Women from California women's prisons are finding out they may qualify for compensation for what the guards did to them.",
    },
    5: {
        "tone": "EMOTIONAL BREAK — voice catches, eyes wet (NOT crying, just glistening), jaw tight — 'that happened to me' lands like a gut punch — slow ONLY on the recognition line, the rest is quicker",
        "closing": "the feeling of: the truth crashing in",
        "dialogue": "Sexual abuse. And I'm reading it like, that happened to me.",
    },
    6: {
        "tone": "expansive, speaking for many — voice steady but emotional — quicker pace",
        "closing": "the feeling of: a quiet shared truth, finally said out loud",
        "dialogue": "That happened to a lot of us in there. So there's a form.",
    },
    7: {
        "tone": "leaning slightly forward, urgent but reassuring — faster pace, easing the listener's fear",
        "closing": "the feeling of: she is helping you understand it is safe to look",
        "dialogue": "You put when you were there, what happened. That's it. Nobody's calling you. Nobody's showing up at your house.",
    },
    8: {
        "tone": "practical, quicker, light relief — small softening at the corners of the mouth (NOT a smile, just relief)",
        "closing": "the feeling of: it's smaller than you fear",
        "dialogue": "You just find out if you got a case. I filled it out. It took me like two minutes.",
    },
    9: {
        "tone": "urgent personal address — leaning in — voice raw, slightly trembling — sister to sister",
        "closing": "the feeling of: she is talking to YOU",
        "dialogue": "I'm just saying, Mee-hah, it's not too late. I thought it was, but it's not.",
    },
    10: {
        "tone": "direct call-to-action with a slight catch in her voice — quietly firm but emotional",
        "closing": "the feeling of: a clean ending — the door is open",
        "dialogue": "Tap the button. See if you qualify.",
    },
}


def build_prompt(clip_num):
    c = CLIPS[clip_num]
    expression = (
        f"Expression: {c['tone']}. Eyes direct to camera. Soft neutral mouth between syllables. "
        f"Quiet, composed, emotionally weighted."
    )
    spoken = f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{c["dialogue"]}"'
    closing = f"No on-screen text, no captions, no subtitles. {c['closing']}. CLEAN FRAME — no text anywhere on screen."
    return "\n\n".join([
        CHARACTER, SETTING, NO_TEXT_LOCK, STYLE_LOCK, CAMERA,
        EYES_LOCK, MOUTH_LOCK_NEUTRAL, DIALOGUE_LOCK, PACE, PRONUNCIATION,
        expression, spoken, closing,
    ])


def gen_one(n):
    t0 = time.time()
    out = OUT_DIR / f"clip{n}_poyo.mp4"
    print(f"[clip{n}] start", flush=True)
    res = generate_veo(
        build_prompt(n),
        image_urls=[L2_URL, L2_URL],
        aspect_ratio="9:16",
        resolution="720p",
        generation_type="frame",
    )
    dt = time.time() - t0
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[clip{n}] FAILED ({dt:.1f}s): {res.get('raw')}", flush=True)
        return n, None
    download(res["urls"][0], out)
    print(f"[clip{n}] DONE ({dt:.1f}s) → {out}", flush=True)
    return n, str(out)


def main():
    nums = list(CLIPS.keys())  # 1..10
    print(f"Generating l2 clips {nums} in parallel via Poyo veo3.1-fast...", flush=True)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(nums)) as ex:
        futs = {ex.submit(gen_one, n): n for n in nums}
        for fut in concurrent.futures.as_completed(futs):
            n, path = fut.result()
            results[n] = path
    print("\n=== summary ===", flush=True)
    for n in nums:
        print(f"  clip{n:<2d} → {results.get(n) or 'FAILED'}", flush=True)


if __name__ == "__main__":
    main()
