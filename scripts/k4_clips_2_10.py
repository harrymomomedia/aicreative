"""Generate clips 2-10 of k4 Pixar Latina ad in parallel via Poyo veo3.1-fast.

Settings:
  - 720p 9:16 8s per clip
  - frame mode with k4 as both start + end frame (Poyo requires exactly 2)
  - Per-clip dialogue + emotional register; shared style/eyes/mouth/dialogue locks
  - Pronunciation respells: Chowchilla→Chow-chilluh, Mija→Mee-hah

Output: outputs/1777697550119-gyvk6m8/clips_k4/clip{N}_poyo.mp4
"""
import sys, pathlib, concurrent.futures, time
sys.path.insert(0, "/Users/harry/aicreative")
from poyo_client import generate_veo, download

K4_URL = "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778415142503-n2mzw4biry.png"
OUT_DIR = pathlib.Path("outputs/1777697550119-gyvk6m8/clips_k4")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHARACTER = (
    "A 56-year-old Latina woman sits at her kitchen table, alone. "
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic. "
    "Dark brown hair heavily streaked with grey, worn loose just past her shoulders. "
    "Weathered face with deep crow's feet, no makeup, simple silver hoop earrings, "
    "small abstract tattoo on the inside of her right forearm. Wears a faded chambray "
    "button-up shirt over a plain white t-shirt, sleeves rolled to her elbows."
)

SETTING = (
    "Background: cluttered small kitchen, an old white refrigerator covered in family photos "
    "and colorful magnets directly behind her, a stack of unopened mail on the counter, a "
    "coffee maker mid-brew, brown wooden cabinets with one door slightly ajar, warm yellow "
    "afternoon light. The background remains a fully photorealistic real-world photograph "
    "throughout."
)

STYLE_LOCK = (
    "CRITICAL — VISUAL STYLE LOCK: The character is rendered in Pixar/Disney 3D animated "
    "character style throughout the ENTIRE clip from frame one to the final frame. NEVER "
    "drift to photorealistic. Maintain large expressive Pixar eyes with cartoon highlights, "
    "soft stylized facial features, smooth shaded 3D skin, slightly enlarged head proportions "
    "in Pixar's signature character design, painterly hair texture, vivid clean color, "
    "Pixar-style subtle face shading. The CHARACTER is a Pixar 3D animation. The BACKGROUND "
    "is a real photograph. This hybrid composite is maintained for every single frame of the "
    "video."
)

CAMERA = "Camera: locked, no movement, no zoom, no pan. Static handheld phone selfie framing."

EYES_LOCK = (
    "CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip her eyes stay OPEN and "
    "looking DIRECTLY at the camera lens. She does NOT close her eyes during dialogue. "
    "No blinks longer than natural."
)

MOUTH_LOCK_NEUTRAL = (
    "CRITICAL — NO SMILE EVER: Throughout the entire clip her mouth stays in a SOFT NEUTRAL "
    "LINE between syllables. ZERO upturned corners. ZERO smile."
)

DIALOGUE_LOCK = (
    "CRITICAL — DIALOGUE LOCK: She speaks in ENGLISH ONLY (except where a phonetic respell is "
    "explicitly listed below). Do NOT add any Spanish words, fillers like \"uh\", \"um\", "
    "\"like\", \"you know\", \"so\", or any extra words beyond what is listed. Do NOT add any "
    "trailing words at the end. Speak ONLY the words listed in SPOKEN DIALOGUE below, in "
    "order, with no insertions and no improvisation, and STOP speaking after the final word."
)

PRONUNCIATION = (
    "Pronunciation respells: \"Chowchilla\" pronounced \"Chow-chilluh\" (three syllables, "
    "fused, soft \"uh\" ending — do NOT drop the final syllable). \"Mija\" pronounced "
    "\"Mee-hah\" (Spanish: /ˈmi.xa/, the \"j\" is an English \"h\" sound)."
)

# Per-clip dialogue + emotional register
CLIPS = {
    2: {
        "tone": "reflective, looking back into the past, voice slightly distant",
        "closing": "the feeling of: a memory she had filed away years ago",
        "dialogue": "I thought, you know, that part of my life was over. And I moved on.",
    },
    3: {
        "tone": "a small moment of recognition — her sister's voice arriving",
        "closing": "the feeling of: an unexpected ping from family that lands heavier than expected",
        "dialogue": "Then my sister sends me this article. She's like, Mee-hah, you need to look at this.",
    },
    4: {
        "tone": "informational and grave, NOT sudden — gradual shift toward weight",
        "closing": "the feeling of: realizing the news is not abstract — it's about her",
        "dialogue": "Women from California women's prisons are finding out they may qualify for compensation for what the guards did to them.",
    },
    5: {
        "tone": "the emotional peak — the moment of recognition '...that happened to me'",
        "closing": "the feeling of: the past is no longer past",
        "dialogue": "Sexual abuse. And I'm reading it like, that happened to me.",
    },
    6: {
        "tone": "solemn, expanding — speaking for many, not just herself",
        "closing": "the feeling of: a quiet shared truth among many women",
        "dialogue": "That happened to a lot of us in there. So there's a form.",
    },
    7: {
        "tone": "matter-of-fact, instructive, calm — easing the listener's fear",
        "closing": "the feeling of: she is helping you understand it is safe to look",
        "dialogue": "You put when you were there, what happened. That's it. Nobody's calling you. Nobody's showing up at your house.",
    },
    8: {
        "tone": "practical, light reassurance — slight warming of expression",
        "closing": "the feeling of: it's smaller than you fear",
        "dialogue": "You just find out if you got a case. I filled it out. It took me like two minutes.",
    },
    9: {
        "tone": "gentle urging — soft personal address, not pushy",
        "closing": "the feeling of: a sister telling another sister",
        "dialogue": "I'm just saying, Mee-hah, it's not too late. I thought it was, but it's not.",
    },
    10: {
        "tone": "direct call-to-action, quietly firm",
        "closing": "the feeling of: a clean ending — the door is open",
        "dialogue": "Tap the button. See if you qualify.",
    },
}


def build_prompt(clip_num):
    c = CLIPS[clip_num]
    expression = (
        f"Expression: {c['tone']}. Eyes direct to camera. Soft neutral mouth between syllables. "
        f"NOT smiling. NOT crying. Quiet, composed, weighty."
    )
    spoken = f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{c["dialogue"]}"'
    closing = f"No on-screen text, no captions, no subtitles. The feeling of: {c['closing']}."
    return "\n\n".join([
        CHARACTER, SETTING, STYLE_LOCK, CAMERA, EYES_LOCK, MOUTH_LOCK_NEUTRAL,
        DIALOGUE_LOCK, PRONUNCIATION, expression, spoken, closing,
    ])


def gen_one(n):
    t0 = time.time()
    out = OUT_DIR / f"clip{n}_poyo.mp4"
    print(f"[clip{n}] start", flush=True)
    res = generate_veo(
        build_prompt(n),
        image_urls=[K4_URL, K4_URL],  # Poyo frame mode requires exactly 2
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
    nums = list(CLIPS.keys())  # 2..10
    print(f"Generating clips {nums} in parallel via Poyo veo3.1-fast...", flush=True)
    results = {}
    # 9 workers — all clips submit immediately, then each polls independently
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
