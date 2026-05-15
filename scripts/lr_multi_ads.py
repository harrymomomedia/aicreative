"""Generate 4 photoreal Latina ads in parallel via Poyo veo3.1-fast.

Personas: lr01, lr04, lr08, lr10 (each in their own living room).
Script: 10-line Chowchilla dialogue with line 1 SHORTENED — drop "I'm fifty." so
the line works for any age (personas range 42-53). Same dialogue/eyes/no-text/no-smile
locks. Fast emotional pace.

Output: outputs/1777697550119-gyvk6m8/clips_<slug>/clip{N}_poyo.mp4

Cost: 40 clips × $0.10 = $4 total. Wall: ~5 min in parallel.
"""
import sys, pathlib, concurrent.futures, time
sys.path.insert(0, "/Users/harry/aicreative")
from poyo_client import generate_veo, download

# Per-persona anchor URLs + brief setting context (image carries identity, prompt carries setting)
PERSONAS = {
    "lr01": {
        "url": "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778466253407-b6lirivr3ro.png",
        "setting": (
            "Background: modest Inland Empire apartment living room, beige walls, framed school "
            "portraits of her kids on the wall behind her, a low couch with mismatched throw pillows, "
            "warm tungsten light from a corner floor lamp."
        ),
    },
    "lr04": {
        "url": "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778466254430-pk3mwjkula.png",
        "setting": (
            "Background: cramped East Los Angeles apartment living room, dim warm tungsten light, "
            "off-white walls with one large framed black-and-white photograph of her grown children "
            "behind her, a low couch with dark throw pillows, a small lit votive candle on a side table."
        ),
    },
    "lr08": {
        "url": "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778466255154-6kfnj8870su.png",
        "setting": (
            "Background: small Pomona apartment living room, framed school photographs of her two kids "
            "crowded above a low entertainment center, a TV on it playing something muted, a small "
            "folded stack of children's laundry on the arm of the couch, warm tungsten light."
        ),
    },
    "lr10": {
        "url": "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778466255846-07ti8wov8o6a.png",
        "setting": (
            "Background: dim East Los Angeles apartment living room, plain off-white walls with one "
            "large framed photograph of her teenage child centered behind her, a wooden rosary draped "
            "over a side-table lamp, a small unlit candle, dark couch partially visible, dim warm light."
        ),
    },
}

OUT_BASE = pathlib.Path("outputs/1777697550119-gyvk6m8")

CHARACTER_INSTRUCTION = (
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic. "
    "She is the SAME woman shown in the reference frame — preserve her exact identity, age, "
    "skin, hair, clothing, jewelry, tattoos and any distinguishing marks for the ENTIRE clip. "
    "Fully photorealistic real photograph throughout — NOT animated, NOT stylized, NOT 3D. "
    "Photographic imperfections preserved: visible pores, fine lines, slight asymmetry, no "
    "beauty filter, no makeup, no retouching."
)

NO_TEXT_LOCK = (
    "CRITICAL — ABSOLUTELY NO ON-SCREEN TEXT: The video MUST contain ZERO burned-in text of any "
    "kind. Do NOT render any subtitles, captions, lower-thirds, watermarks, words, letters, "
    "banners, text overlays, speech bubbles, or any text whatsoever anywhere in the frame. The "
    "frame must be 100% free of any rendered text or typography. NO subtitle bars at the bottom. "
    "NO floating words. NO captions. This is the most important constraint in this prompt."
)

CAMERA = "Camera: locked, no movement, no zoom, no pan. Static handheld phone selfie framing."

EYES_LOCK = (
    "CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip her eyes stay OPEN and "
    "looking DIRECTLY at the camera lens. She does NOT close her eyes during dialogue."
)

MOUTH_LOCK = (
    "CRITICAL — NO SMILE: Throughout the entire clip her mouth stays in a SOFT NEUTRAL LINE "
    "between syllables. ZERO upturned corners. ZERO smile."
)

DIALOGUE_LOCK = (
    "CRITICAL — DIALOGUE LOCK: She speaks in ENGLISH ONLY (except where a phonetic respell is "
    "explicitly listed below). Do NOT add any Spanish words, fillers like \"uh\", \"um\", "
    "\"like\", \"you know\", \"so\", or any extra words beyond what is listed. Do NOT add any "
    "trailing words at the end. Speak ONLY the words listed in SPOKEN DIALOGUE below, in order, "
    "with no insertions and no improvisation, and STOP speaking after the final word."
)

PACE = (
    "PACE: Speak at a natural conversational cadence with emotional weight — neither rushed nor "
    "overly slow. Minimal pauses between sentences. The dialogue carries the gravity."
)

PRONUNCIATION = (
    "Pronunciation respells: \"Chowchilla\" pronounced \"Chow-chilluh\" (three syllables, fused, "
    "soft \"uh\" ending — do NOT drop the final syllable). \"Mija\" pronounced \"Mee-hah\" "
    "(Spanish: /ˈmi.xa/, the \"j\" is an English \"h\" sound)."
)

# 10-line script — line 1 has "I'm fifty." DROPPED so it works for any persona age.
CLIPS = {
    1: {
        "tone": "weight in her voice, the past pulling on her — slight tremble on 'fifteen years ago'",
        "closing": "the feeling of: the weight just landed on her again",
        "dialogue": "Chow-chilluh was like fifteen years ago for me.",
    },
    2: {
        "tone": "still holding it together, resolve cracking, jaw set",
        "closing": "the feeling of: she had buried this and now it's surfacing",
        "dialogue": "I thought, you know, that part of my life was over. And I moved on.",
    },
    3: {
        "tone": "her sister's name lands hard — eyes glisten momentarily",
        "closing": "the feeling of: a phone notification that changed everything",
        "dialogue": "Then my sister sends me this article. She's like, Mee-hah, you need to look at this.",
    },
    4: {
        "tone": (
            "SAME intimate quiet weary tone as the rest of the ad — NOT news-anchor, NOT "
            "informational, NOT energetic. She's repeating what she just read in her own quiet "
            "personal voice, like she's still processing it. Speak it the way you'd say it to a "
            "friend at the kitchen table — soft, level, slightly stunned. Do NOT raise the "
            "energy of your voice for this line. Match the calm of the previous clip exactly."
        ),
        "closing": "the feeling of: she is realizing this is about her, not 'them'",
        "dialogue": "Women in California prisons may qualify for compensation. For what the guards did to them.",
    },
    5: {
        "tone": "EMOTIONAL BREAK — voice catches, eyes wet (NOT crying, just glistening), jaw tight",
        "closing": "the feeling of: the truth crashing in",
        "dialogue": "Sexual abuse. And I'm reading it like, that happened to me.",
    },
    6: {
        "tone": "expansive, speaking for many — voice steady but emotional",
        "closing": "the feeling of: a quiet shared truth, finally said out loud",
        "dialogue": "That happened to a lot of us in there. So there's a form.",
    },
    7: {
        "tone": "leaning slightly forward, urgent but reassuring — easing the listener's fear",
        "closing": "the feeling of: she is helping you understand it is safe to look",
        "dialogue": "You put when you were there, what happened. That's it. Nobody's calling you. Nobody's showing up at your house.",
    },
    8: {
        "tone": "practical, light relief — small softening at the corners (NOT a smile)",
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


def build_prompt(persona_setting, clip_num):
    c = CLIPS[clip_num]
    expression = (
        f"Expression: {c['tone']}. Eyes direct to camera. Soft neutral mouth between syllables. "
        f"Quiet, composed, emotionally weighted."
    )
    spoken = f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{c["dialogue"]}"'
    closing = f"No on-screen text, no captions, no subtitles. {c['closing']}. CLEAN FRAME — no text anywhere on screen."
    return "\n\n".join([
        CHARACTER_INSTRUCTION, persona_setting, NO_TEXT_LOCK, CAMERA,
        EYES_LOCK, MOUTH_LOCK, DIALOGUE_LOCK, PACE, PRONUNCIATION,
        expression, spoken, closing,
    ])


def gen_one(slug, n):
    p = PERSONAS[slug]
    out_dir = OUT_BASE / f"clips_{slug}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"clip{n}_poyo.mp4"
    if out.exists():
        print(f"[{slug} clip{n}] SKIP (already exists)", flush=True)
        return slug, n, str(out)
    t0 = time.time()
    print(f"[{slug} clip{n}] start", flush=True)
    res = generate_veo(
        build_prompt(p["setting"], n),
        image_urls=[p["url"], p["url"]],  # frame mode: start+end both = anchor
        aspect_ratio="9:16",
        resolution="720p",
        generation_type="frame",
    )
    dt = time.time() - t0
    if res.get("status") != "success" or not res.get("urls"):
        print(f"[{slug} clip{n}] FAILED ({dt:.1f}s): {res.get('raw')}", flush=True)
        return slug, n, None
    download(res["urls"][0], out)
    print(f"[{slug} clip{n}] DONE ({dt:.1f}s) → {out}", flush=True)
    return slug, n, str(out)


def main():
    tasks = [(slug, n) for slug in PERSONAS for n in range(1, 11)]
    print(f"Submitting {len(tasks)} clips ({len(PERSONAS)} personas × 10 lines) in parallel via Poyo...", flush=True)
    results = {}
    # max 10 concurrent — Poyo's submit rate limit is 20 req per 10s, so 10 in flight
    # at a time keeps us well under (each gen takes 90-180s, so submission rate ~5-6/min).
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(gen_one, s, n): (s, n) for s, n in tasks}
        for fut in concurrent.futures.as_completed(futs):
            s, n, path = fut.result()
            results[(s, n)] = path
    print("\n=== summary ===", flush=True)
    for slug in PERSONAS:
        ok = sum(1 for n in range(1, 11) if results.get((slug, n)))
        print(f"  {slug}: {ok}/10 done")


if __name__ == "__main__":
    main()
