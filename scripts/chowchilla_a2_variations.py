"""Generate 12 Chowchilla script-variation ads using the same persona via Poyo veo3.1-fast.

Persona anchor: scene_00 from final_a2_vc_ad copy.mp4 (Latina, "Loyalty" tattoo,
plaid flannel, pink wall + crucifix + family photos).

CLI:
  --variation V2 [--clip 1]                 # one variation, optionally one clip
  --variation V2 V4 V5                       # multiple variations, all clips each
  --variation all                            # all 12 variations
  --clips 1                                  # only clip 1 of each (canary mode)
  --max-workers 6                            # parallelism
  --dry-run                                  # print what would generate, don't call API

Per CLAUDE.md: clip 1 of every variation uses the source anchor (ANCHOR_URL).
For clips 2-N, the script EXPECTS the per-variation clip-1 anchor to already exist
at outputs/0502_a2_variations/<variation>/clip1_anchor.jpg (extracted manually
or by extract_clip1_anchors.py after clip 1's pass QA). If missing, falls back to
ANCHOR_URL for that clip too (with a warning).

Output: outputs/0502_a2_variations/<variation>/clip{N}_poyo.mp4
"""
import argparse, json, sys, pathlib, time
import concurrent.futures
sys.path.insert(0, "/Users/harry/aicreative")
from poyo_client import generate_veo, download

ANCHOR_URL = "https://tempfile.redpandaai.co/kieai/179128/aicreative/1778469671288-cgtogsucou9.jpg"
OUT_BASE = pathlib.Path("/Users/harry/aicreative/outputs/0502_a2_variations")
OUT_BASE.mkdir(parents=True, exist_ok=True)

# ─── Shared persona/scene blocks ─────────────────────────────────────

CHARACTER = (
    "A Latina woman, late 40s to early 50s, sitting on a plastic-covered tan couch in her own home. "
    "Vertical 9:16 selfie portrait, chest-up framing, handheld phone selfie aesthetic. "
    "Dark brown hair slicked back tight in a low ponytail, defined dark eyebrows. "
    "Gold hoop earrings. A faded 'Loyalty' Old English script tattoo across her upper chest above her white tank, "
    "and a faint prayer-hand tattoo on the right side of her neck. "
    "She wears a thin gold chain necklace alongside a thin rosary chain, over a white ribbed tank top, "
    "with a red and black buffalo-plaid flannel shirt unbuttoned over it. "
    "Light makeup, mascara'd lashes, no lipstick. "
    "Visible pores, fine lines, faint under-eye darkness, dry lips, slight asymmetry, "
    "no beauty mode, no retouching, no filter, no skin smoothing."
)

SETTING = (
    "Background: a pink-coral painted interior wall directly behind her, lined with multiple "
    "framed family photographs — a graduation portrait at left, a wedding photo center-left in an ornate gold frame, "
    "a smaller framed family portrait to her right, a baby photo in a small frame at lower left. "
    "A wooden crucifix is mounted dead-center on the wall above her head. "
    "Visible behind her shoulders: the back of a plastic-covered tan couch, the plastic shrink-wrap visible in soft folds. "
    "On the left edge of frame: a tall white prayer candle on a side table. "
    "Soft warm interior afternoon light from a window out of frame to her left. "
    "Mexican-American household interior. "
    "The background is a fully photorealistic real-world photograph throughout the entire clip."
)

CAMERA = "Camera: locked, no movement, no zoom, no pan, no rack focus. Static handheld phone selfie framing."

EYES_LOCK = (
    "CRITICAL — EYES OPEN AND ON CAMERA: Throughout the entire clip her eyes stay OPEN and "
    "looking DIRECTLY at the camera lens. She does NOT close her eyes during dialogue. "
    "No blinks longer than natural single-frame blinks."
)

MOUTH_LOCK_NEUTRAL = (
    "CRITICAL — NO SMILE EVER: Throughout the entire clip her mouth stays in a SOFT NEUTRAL "
    "LINE between syllables. ZERO upturned corners. ZERO smile. Weary, serious, direct."
)

NO_TEXT_LOCK = (
    "ABSOLUTELY NO ON-SCREEN TEXT, NO CAPTIONS, NO SUBTITLES, NO BURNED-IN GRAPHICS. "
    "The frame contains only the woman speaking in her living room — no logos, no watermarks, no on-screen words of any kind."
)

DIALOGUE_LOCK = (
    "CRITICAL — DIALOGUE LOCK: She speaks in ENGLISH ONLY. Do NOT add any Spanish words, "
    "fillers like 'uh', 'um', 'like', 'you know', 'so', or any extra words beyond what is listed. "
    "Do NOT add any trailing words at the end. Speak ONLY the words listed in SPOKEN DIALOGUE below, "
    "in order, with no insertions and no improvisation, and STOP speaking after the final word."
)

PRONUNCIATION_LOCK = (
    "Pronunciation: 'Chowchilla' is the name of a California women's prison and is pronounced "
    "as three English syllables: chow (rhymes with 'cow') + chill + uh. Stress on the middle syllable. "
    "Say it as one fluid word, NOT as separate letters or spelled out. Never pronounce it as a Spanish word."
)

# ─── 12 picked variations, hand-chunked into ≤8s spoken segments ────

VARIATIONS = {
    "V2": {
        "register": "urgent social-proof. Slight emphasis on the number 'Five'. Voice carries weight; she's relaying news.",
        "clips": [
            "Five women from my old unit have already filed. Five. They're the ones who told me.",
            "Women from the California women's prisons may qualify for significant potential compensation. For the sexual abuse the guards committed against us.",
            "The form sits on a website. You enter when you were inside, what they did. That's it.",
            "They might call you to walk through your case. It's between you and the firm. Nothing leaves that conversation.",
            "Nobody pulls up at your address. You just learn if you have a case.",
            "Mine took two minutes flat. Word's spreading fast — don't be the last one in your unit.",
            "Find out. Click below. Check your eligibility.",
        ],
    },
    "V4": {
        "register": "anchored, almost matter-of-fact early on, then weight building toward 'most important two minutes of my year'.",
        "clips": [
            "Two minutes. That's how long this took me.",
            "Less time than ordering food. Less time than this video.",
            "And it might be the most important two minutes of my year.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards put us through in Chowchilla.",
            "There's a form. You put when you were inside and what happened. That's the whole step on you.",
            "They might call you privately to go through your case. Strictly between the two of you.",
            "Nobody knocks on your door. You just get an answer. Tap the link. Find out fast.",
        ],
    },
    "V5": {
        "register": "disbelief lifting into reassurance. 'Three times' said with measured surprise. Authority frame when citing the cousin.",
        "clips": [
            "I read this three times before I believed it.",
            "Then I called my cousin who works at a law office. She said it's legit.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards committed at Chowchilla.",
            "There's a form on the lawyers' site. You put down your dates inside, what was done. That's it.",
            "They may give you a call to walk you through it. Confidential. Every word.",
            "No agent shows up at your house. You just learn if you've got a case.",
            "I filled it out on my couch in under three minutes. I almost skipped it. Don't do what I almost did.",
            "Hit the link below. See if you qualify. It only takes a couple of minutes.",
        ],
    },
    "V7": {
        "register": "calm, reassuring, almost a 'sit down let me tell you' tone. Permission-giving, not urgent.",
        "clips": [
            "Listen. You don't have to talk to anybody about this.",
            "You don't tell your husband. You don't tell your kids.",
            "There's a form on a website. Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards inflicted in Chowchilla.",
            "You enter your dates and what happened.",
            "If a lawyer reaches out to discuss it, that talk is private. Your business stays your business.",
            "Nobody shows up unannounced at your home. You just see if you have a case.",
            "Mine took two minutes. Nobody finds out unless you decide to tell them.",
            "Tap the link. See where you stand.",
        ],
    },
    "V8": {
        "register": "cold, declarative, no euphemism. Voice steady, weight on every word. Eye contact unbroken.",
        "clips": [
            "What the guards did to us in Chowchilla was sexual abuse.",
            "We know what it was. We don't say it because nobody's listening.",
            "Now somebody's listening.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "There's a form. You put down when you were there and what was done. That's the whole step.",
            "If they call you to talk, what you say stays in that call.",
            "Nobody pulls up at your house. You just find out if you've got a claim.",
            "Took me two minutes. Tap below. See if you qualify.",
        ],
    },
    "V9": {
        "register": "slight challenge / confrontational frame. 'Be smarter' said directly to camera. Confident, not aggressive.",
        "clips": [
            "Most women aren't gonna fill this out. But you're not most women.",
            "They'll assume it's a scam. Or that it's too late. Or that it's not for them.",
            "Be smarter than that. Don't be the one who didn't try.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards committed against us in Chowchilla.",
            "There's a form. You enter when you were inside, what happened. That's it.",
            "They may give you a call after. Completely confidential, locked between you and them.",
            "No one shows up at your door. You just learn if you have a case.",
            "Took me three minutes. The smart ones already filed. Don't get left behind.",
            "Hit the link. See if you qualify.",
        ],
    },
    "V10": {
        "register": "objection-handling. Acknowledges doubt directly, then dismisses it with quiet certainty. 'It's real' grounded, not pushy.",
        "clips": [
            "I know how this is gonna sound. It's a scam.",
            "That's what I thought too. It's not. I checked.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For what the Chowchilla guards did to us. Sexual abuse.",
            "The form is on a real law firm's website. You log when you were inside and what was done.",
            "If they reach out to talk through your case, it's private. They don't share your info with anybody.",
            "Nobody knocks on your door. You just see if you have a case.",
            "Mine took two minutes. It's real. I'm not making this up.",
            "Tap below. See if you qualify.",
        ],
    },
    "V12": {
        "register": "private, conspiratorial. 'Listen' opening said quietly, leaning in. Privacy framing soft and reassuring.",
        "clips": [
            "Nobody at your job is gonna find out. Nobody on your block.",
            "Your kids don't have to know.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards inflicted on us in Chowchilla.",
            "There's a form. You enter when you were there and what was done.",
            "After that, if they call to walk through it with you. It's confidential. Your name stays out of it.",
            "Nobody comes to your house. You just see if you have a claim.",
            "Took me two minutes on my phone. Your past stays your business.",
            "Tap the link. Check your eligibility.",
        ],
    },
    "V14": {
        "register": "quiet, reflective. Story tease delivered with a slight pause before 'Yes. It is.' Emotional weight in the recognition.",
        "clips": [
            "My daughter sent me this and didn't even know she was sending it to the right person.",
            "She just said: Mom, isn't this the place you were at? Yes. It is.",
            "Women from the California women's prisons may qualify for significant potential compensation.",
            "For the sexual abuse the guards committed at Chowchilla.",
            "There's a form. You log when you were locked up and what happened.",
            "If a lawyer reaches out to discuss your case, it's strictly confidential. Between you and the firm. Nowhere else.",
            "No one comes by your house. You just see if you have a claim.",
            "Took me two minutes. Tap below. See if you qualify.",
        ],
    },
    "V15": {
        "register": "outraged but controlled. 'Makes me sick' delivered with weight, not yelling. Slow build to the call to action.",
        "clips": [
            "You know what makes me sick? Nobody told us.",
            "We did the time. We took the sexual abuse from the guards.",
            "And the people who knew — the supervisors, the ones above them — kept their mouths shut. Until now.",
            "Women from the California women's prisons may qualify for significant potential compensation. For exactly what happened to us in Chowchilla.",
            "There's a form. You enter when you were inside, what was done.",
            "If they call to walk through your case, that conversation stays sealed.",
            "No one shows up at your door. You just see if you have a claim.",
            "Took me two minutes. They wanted us to forget. Don't.",
            "Tap below. See if you qualify.",
        ],
    },
    "V18": {
        "register": "rhetorical questions delivered slowly, with eye contact, almost accusatory at the institutions. Then a turn to direct address.",
        "clips": [
            "Did anyone ever check on you after Chowchilla?",
            "Did anyone ever ask what those guards did to you in there?",
            "No. Nobody did. Until now.",
            "Women from the California women's prisons may qualify for significant potential compensation. For sexual abuse.",
            "There's a one-page form. You enter when you were locked up and what was done. That's the whole step.",
            "If they reach out, the call stays between the two of you. Your name doesn't leave that conversation.",
            "Nobody pulls up at your house. You just find out if you have a case.",
            "Took me a couple of minutes. Tap below. See where you stand.",
        ],
    },
    "V20": {
        "register": "tribute / reverence at the open. Voice softer for 'she passed last year', then steadies as she takes up the message for both of them.",
        "clips": [
            "My cellmate from Chowchilla passed last year.",
            "She never got to say what those guards did to her. The sexual abuse.",
            "So I'm saying it for both of us.",
            "Women from the California women's prisons may now qualify for significant potential compensation.",
            "There's a form on a law firm's site. You enter when you were locked up and what happened. That's the only thing on you.",
            "They might call to walk through your case. And that talk stays sealed. Nobody else hears it.",
            "No one comes to your address. You just find out if you have a case.",
            "Mine took two minutes. For her. For me. For you.",
            "Tap below. See if you qualify.",
        ],
    },
}


# ─── Prompt builder ─────────────────────────────────────────────────

def build_prompt(variation_id, clip_idx):
    v = VARIATIONS[variation_id]
    spoken = v["clips"][clip_idx - 1]
    register = v["register"]
    parts = [
        CHARACTER,
        SETTING,
        CAMERA,
        f"Emotional register for this clip: {register}",
        STYLE := "",  # placeholder — not used here, all photoreal
        EYES_LOCK,
        MOUTH_LOCK_NEUTRAL,
        NO_TEXT_LOCK,
        PRONUNCIATION_LOCK,
        DIALOGUE_LOCK,
        f'SPOKEN DIALOGUE (verbatim, no additions, stop after final word): "{spoken}"',
    ]
    return "\n\n".join(p for p in parts if p)


def get_anchor_url(variation_id, clip_idx):
    """Return the image URL to use for IMAGE_2_VIDEO seed.

    Per CLAUDE.md clip-1 anchor strategy: clip 1 uses source anchor; clips 2-N
    use a clean frame from THE SAME variation's clip 1 (uploaded separately).
    Clip-1 anchors per variation must be uploaded after clip 1's pass QA;
    URLs live in <out>/clip1_anchor_url.txt next to clip 1's mp4.
    """
    out_dir = OUT_BASE / variation_id
    # Per-clip override (anchor rotation)
    per_clip = out_dir / f"clip{clip_idx}_anchor_url.txt"
    if per_clip.exists():
        return per_clip.read_text().strip()
    if clip_idx == 1:
        return ANCHOR_URL
    # Default: clip-1 anchor for clips 2-N
    anchor_url_file = out_dir / "clip1_anchor_url.txt"
    if anchor_url_file.exists():
        return anchor_url_file.read_text().strip()
    print(f"  [{variation_id} clip {clip_idx}] WARNING: no per-variation anchor — falling back to source anchor", flush=True)
    return ANCHOR_URL


def generate_one(variation_id, clip_idx, dry_run=False):
    out_dir = OUT_BASE / variation_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"clip{clip_idx}_poyo.mp4"
    if out_path.exists():
        return (variation_id, clip_idx, "exists", str(out_path))

    prompt = build_prompt(variation_id, clip_idx)
    image_url = get_anchor_url(variation_id, clip_idx)

    if dry_run:
        print(f"  DRY {variation_id} clip {clip_idx} → {out_path.name}")
        print(f"    spoken: {VARIATIONS[variation_id]['clips'][clip_idx-1]!r}")
        return (variation_id, clip_idx, "dry", str(out_path))

    t0 = time.time()
    # Veo 3.1 frame mode requires exactly 2 image_urls (start + end). Pass the
    # same anchor for both → keeps persona locked at start AND end of clip.
    res = generate_veo(
        prompt=prompt,
        image_urls=[image_url, image_url],
        aspect_ratio="9:16",
        resolution="720p",
        model="veo3.1-fast",
        generation_type="frame",
    )
    if res["status"] != "success" or not res.get("urls"):
        return (variation_id, clip_idx, "failed", res.get("raw"))
    download(res["urls"][0], str(out_path))
    return (variation_id, clip_idx, "success", str(out_path), round(time.time()-t0, 1))


# ─── CLI ──────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variation", nargs="+", required=True,
                    help="variation IDs (e.g. V2 V4) or 'all'")
    ap.add_argument("--clip", type=int, default=None, help="single clip index (1-based)")
    ap.add_argument("--clips", nargs="+", type=int, default=None,
                    help="explicit clip indices (e.g. --clips 1 2 3)")
    ap.add_argument("--max-workers", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    variations = list(VARIATIONS.keys()) if args.variation == ["all"] else args.variation
    for v in variations:
        if v not in VARIATIONS:
            raise SystemExit(f"unknown variation: {v}. valid: {list(VARIATIONS)}")

    jobs = []  # (variation_id, clip_idx)
    for v in variations:
        n_clips = len(VARIATIONS[v]["clips"])
        if args.clip is not None:
            jobs.append((v, args.clip))
        elif args.clips:
            for c in args.clips:
                jobs.append((v, c))
        else:
            for c in range(1, n_clips + 1):
                jobs.append((v, c))

    print(f"dispatching {len(jobs)} jobs, max_workers={args.max_workers}", flush=True)
    for v, c in jobs:
        print(f"  {v} clip {c}/{len(VARIATIONS[v]['clips'])}", flush=True)

    if args.dry_run:
        for v, c in jobs:
            generate_one(v, c, dry_run=True)
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futs = {ex.submit(generate_one, v, c): (v, c) for v, c in jobs}
        successes, failures = [], []
        for f in concurrent.futures.as_completed(futs):
            v, c = futs[f]
            try:
                r = f.result()
                print(f"  → {r}", flush=True)
                successes.append((v, c))
            except Exception as e:
                msg = str(e)[:200]
                print(f"  ✗ {v} clip {c} FAILED: {msg}", flush=True)
                failures.append((v, c, msg))
        print(f"\nSummary: {len(successes)} success, {len(failures)} failed", flush=True)
        if failures:
            print("Failed jobs:", flush=True)
            for v, c, msg in failures:
                print(f"  {v} clip {c}: {msg}", flush=True)


if __name__ == "__main__":
    main()
