"""
Depo — 20 MENINGIOMA-ONLY image ads (dead-targeted to a meningioma diagnosis).
Full gpt-image-2 render (baked exact on-image text), 1:1 2K, KIE. NO PIL.

Targeting rule (feedback_meningioma_only_targeting): the specific word "meningioma" IS the
filter — lead on it, DROP the broad "brain tumor" hook, do NOT belabor "not symptoms / not
other conditions" (the word self-filters). The ONE natural home for an explicit
"other brain tumors don't qualify" line is the conversational / iMessage format (ad #10).
No symptom-bait. Diagnosed-speaking. "may qualify for significant compensation". No disclaimer.

Run:  .venv/bin/python scripts/depo_meningioma20_gen.py [--only <slug|n,...>] [--regen] [--workers 5]
                                                        [--provider kie|openai] [--dump]
Output: outputs/depo_ads/meningioma20/<NN>_<slug>.png   (skip-if-exists)
Copy sheet: outputs/depo_ads/meningioma20/copy.json (via --dump)
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

OUT = Path("outputs/depo_ads/meningioma20")
SUFFIX = (" Render ONLY the exact text specified — no extra words, headlines, claims, logos, "
          "watermarks, or disclaimers. Clean, high-contrast, mobile-readable.")

# persona realism tail (Depo demographic = Black / African American women)
REAL = (" Photoreal candid documentary photo, shot-on-phone realism, plain everyday setting, natural "
        "imperfect skin with visible pores and fine lines, no makeup, no glamour, no retouching, an "
        "ordinary relatable woman. ")


def persona_img(person, quote):
    """A distinct real woman + ONE clean readable on-image pull-quote band."""
    return (f"{person}{REAL}A large clean highly-readable text band across the lower third reading "
            f"EXACTLY: \"{quote}\" in a bold legible sans-serif on a high-contrast strip." + SUFFIX)


ADS = [
    {
        "n": 1, "slug": "one_word", "format": "one-word typographic", "style": "brutalist poster",
        "angle": "The word itself is the hook + filter",
        "headline": "Was Your Diagnosis a Meningioma?",
        "pull_quote": "MENINGIOMA",
        "primary": ("This is for women diagnosed with a meningioma — the tumor in the lining of the "
                    "brain — who used the Depo-Provera shot. If that's your diagnosis, you may qualify "
                    "for significant compensation. See if you qualify."),
        "image_prompt": (
            "A stark brutalist typographic poster, plain deep-charcoal background, slight print grain, "
            "huge bold condensed sans-serif, lots of negative space. Text reads EXACTLY: an enormous "
            "word 'MENINGIOMA' filling the center, then a smaller line beneath it 'The diagnosis this "
            "is about.', then a small line at the bottom 'You may qualify for significant "
            "compensation.'" + SUFFIX),
    },
    {
        "n": 2, "slug": "check_records", "format": "medical-record document", "style": "top-down photo",
        "angle": "Pull your chart, look for the word",
        "headline": "Pull Your Records. Look for One Word.",
        "pull_quote": "Diagnosis: Meningioma",
        "primary": ("The Depo-Provera claim comes down to one word on your chart: meningioma. If your "
                    "records say it and you used Depo, you may qualify for significant compensation. "
                    "See if you qualify."),
        "image_prompt": (
            "A realistic top-down photo of a printed medical after-visit summary on white paper under "
            "clean even documentary light, a pen resting beside it. One line is highlighted in yellow "
            "marker and reads EXACTLY 'Diagnosis: Meningioma'. A bold heading at the top reads 'PULL "
            "YOUR RECORDS' and a dark bar at the bottom with white text reads 'One word may qualify "
            "you. Used Depo-Provera? Tap below.' (Leave any name fields blank or generic.)" + SUFFIX),
    },
    {
        "n": 3, "slug": "was_it", "format": "bold question card", "style": "deep-teal type card",
        "angle": "Direct qualifier question",
        "headline": "It Has to Be a Meningioma",
        "pull_quote": "Was it a MENINGIOMA?",
        "primary": ("If your diagnosis was a meningioma and you used the Depo-Provera shot, you may "
                    "qualify for significant compensation. It only takes a minute to find out. See if "
                    "you qualify."),
        "image_prompt": (
            "A clean bold question card, deep teal background, large white modern sans-serif, generous "
            "spacing. Text reads EXACTLY: very large 'Was it a MENINGIOMA?' across the upper half, then "
            "a line 'That's the diagnosis that may qualify.', then a small footer 'Used the Depo-"
            "Provera shot? Tap below.'" + SUFFIX),
    },
    {
        "n": 4, "slug": "mri_report", "format": "radiology report", "style": "clinical close-up photo",
        "angle": "The word on the scan report",
        "headline": "If Your Report Said Meningioma",
        "pull_quote": "...findings consistent with a meningioma.",
        "primary": ("A meningioma has a specific name on your scan report. If yours said it, and you "
                    "used Depo-Provera, you may qualify for significant compensation. See if you "
                    "qualify."),
        "image_prompt": (
            "A realistic close-up photo of a radiology / MRI report page on white paper under even "
            "clinical light, a small grayscale brain-MRI thumbnail in the corner. One impression line "
            "is underlined and reads EXACTLY '...findings consistent with a meningioma.' A bold header "
            "reads 'IF YOUR REPORT SAID THIS WORD' and a footer line reads 'You may qualify for "
            "significant compensation.' Authentic and legible. (Leave any patient name fields blank "
            "or generic.)" + SUFFIX),
    },
    {
        "n": 5, "slug": "two_boxes", "format": "two-criteria checklist", "style": "clean check card",
        "angle": "The gate IS the creative — two boxes",
        "headline": "The Two Boxes That Matter",
        "pull_quote": "✓ Meningioma   ✓ Depo-Provera",
        "primary": ("It comes down to two things: a meningioma diagnosis, and Depo-Provera use. If "
                    "that's you, you may qualify for significant compensation. See if you qualify."),
        "image_prompt": (
            "A clean modern checklist card, soft off-white background, two large GREEN CHECKMARK "
            "ticks (checkmarks, NOT X marks), simple sans-serif, generous spacing. Text reads "
            "EXACTLY: a heading 'THE TWO BOXES THAT MATTER', then two lines each preceded by a green "
            "checkmark tick — 'Diagnosed with a meningioma' and 'Used Depo-Provera' — then a downward "
            "arrow and a dark bar reading 'You may qualify for significant compensation.'" + SUFFIX),
    },
    {
        "n": 6, "slug": "defined", "format": "dictionary definition", "style": "editorial serif card",
        "angle": "Define the exact word",
        "headline": "One Word, Defined",
        "pull_quote": "meningioma (n.)",
        "primary": ("A meningioma forms in the lining of the brain. If that was your diagnosis after "
                    "using Depo-Provera, you may qualify for significant compensation. See if you "
                    "qualify."),
        "image_prompt": (
            "A clean editorial dictionary-definition card, off-white paper, elegant serif typography "
            "like a printed dictionary page. Text reads EXACTLY: the entry word 'meningioma' in bold "
            "serif followed by '(n.)', then a definition line 'a tumor that forms in the lining of the "
            "brain', then on its own line in bold 'The diagnosis this claim is about.', then smaller "
            "'Used Depo-Provera? You may qualify for significant compensation.'" + SUFFIX),
    },
    {
        "n": 7, "slug": "after_depo", "format": "FAQ card", "style": "clean minimalist card",
        "angle": "Qualifying-confirmation FAQ (not a deflector)",
        "headline": "Diagnosed With a Meningioma After Depo?",
        "pull_quote": "A question we get a lot",
        "primary": ("If you were diagnosed with a meningioma and used the Depo-Provera shot, you may "
                    "qualify for significant compensation. It's free and confidential to find out. See "
                    "if you qualify."),
        "image_prompt": (
            "A clean minimalist FAQ card, soft white background, modern sans-serif, generous spacing. "
            "Text reads EXACTLY: a heading 'A QUESTION WE GET A LOT', then a bold question 'Diagnosed "
            "with a meningioma after Depo-Provera?' and a lighter answer 'Then this is for you. You "
            "may qualify.', then a small footer 'Free & confidential — tap below.'" + SUFFIX),
    },
    {
        "n": 8, "slug": "testimonial", "format": "UGC testimonial", "style": "documentary phone selfie",
        "angle": "She'd never heard the word",
        "headline": "The Word Was Meningioma",
        "pull_quote": "They said 'meningioma.' I'd never heard the word.",
        "primary": ("When the doctor said meningioma, I had to ask her to spell it. I didn't know that "
                    "one word would matter so much later. I was on the Depo shot for years.\n\n"
                    "If your diagnosis was a meningioma, you may qualify for significant compensation. "
                    "See if you qualify."),
        "image_prompt": persona_img(
            "A Black woman about 45, natural hair, plain everyday top, sitting in a modest living room, "
            "quiet and serious, looking into a phone camera held at arm's length. ",
            "They said 'meningioma.' I'd never heard the word."),
    },
    {
        "n": 9, "slug": "news", "format": "news article", "style": "newsprint, generic masthead",
        "angle": "High-trust news framing of the specific diagnosis",
        "headline": "The Claim Is About Meningioma",
        "pull_quote": "Depo-Provera Claim Centers on One Diagnosis: Meningioma",
        "primary": ("The litigation over Depo-Provera centers on one diagnosis — meningioma. Women "
                    "with it who used the shot are coming forward. If yours was a meningioma, you may "
                    "qualify for significant compensation. See if you qualify."),
        "image_prompt": (
            "A realistic health-news article layout with a generic masthead reading 'THE HEALTH "
            "REPORT' (not a real outlet), printed serif body. A large headline reads EXACTLY 'Depo-"
            "Provera Claim Centers on One Diagnosis: Meningioma', and a smaller deck beneath reads "
            "'Women diagnosed with a meningioma who used the shot may qualify for significant "
            "compensation.' Below, greeked/blurred body columns and a neutral documentary photo of a "
            "Black woman in her forties looking thoughtfully toward a window. "
            "Authentic newsprint, legible, no real logos." + SUFFIX),
    },
    {
        "n": 10, "slug": "imessage", "format": "iMessage", "style": "phone-UI screenshot",
        "angle": "Conversational — the ONE place the exclusion is natural",
        "headline": "What Did Your Chart Say?",
        "pull_quote": "other brain tumors don't count, just meningioma",
        "primary": ("Women are comparing notes on the exact word on their diagnosis. The Depo-Provera "
                    "claim is only for a meningioma — other brain tumors don't count. If your chart "
                    "said meningioma and you used Depo, you may qualify for significant compensation. "
                    "See if you qualify."),
        "image_prompt": (
            "A clean realistic iMessage-style text conversation screenshot on a white phone "
            "background, grey incoming bubbles on the left and blue outgoing bubbles on the right, "
            "fully readable. The conversation reads EXACTLY, in order: (grey) 'what did your chart "
            "actually say?', (blue) 'meningioma, why?', (grey) \"that's the one — other brain tumors "
            "don't count, just meningioma\", (blue) 'wait seriously', (grey) 'if you were on the depo "
            "shot you may qualify'. A small footer line below reads 'Tap below to see if you "
            "qualify.'" + SUFFIX),
    },
    {
        "n": 11, "slug": "years_ago", "format": "myth vs fact", "style": "bauhaus two-panel",
        "angle": "Too-long-ago myth (diagnosed-speaking, no exclusion)",
        "headline": "Years Ago? You May Still Qualify",
        "pull_quote": "MYTH vs FACT",
        "primary": ("A lot of women assume a meningioma from years back is too late. It may not be. If "
                    "you were diagnosed with a meningioma and used the Depo-Provera shot, you may "
                    "qualify for significant compensation. See if you qualify."),
        "image_prompt": (
            "A bold two-panel graphic split down the middle in a geometric bauhaus style, heavy sans-"
            "serif. Text reads EXACTLY: left panel labeled 'MYTH' with 'My meningioma was years ago — "
            "too late.', right panel labeled 'FACT' with 'You may still qualify.', then a footer bar "
            "across the bottom 'Diagnosed with a meningioma and used Depo-Provera? Tap below.' Left "
            "panel muted grey, right panel bright, high-contrast." + SUFFIX),
    },
    {
        "n": 12, "slug": "search_bar", "format": "search bar", "style": "clean phone-UI",
        "angle": "The exact search",
        "headline": "Is It Only for Meningioma?",
        "pull_quote": "is the depo lawsuit only for meningioma",
        "primary": ("The Depo-Provera claim is specific to a meningioma diagnosis — the tumor in the "
                    "lining of the brain — in women who used the shot. If that's yours, you may "
                    "qualify for significant compensation. See if you qualify."),
        "image_prompt": (
            "A clean smartphone search screenshot on a white background, a rounded search field with a "
            "magnifier icon. The search field contains the typed text EXACTLY 'is the depo lawsuit "
            "only for meningioma'. Below it two autocomplete suggestion rows, each with a small "
            "magnifier icon, reading EXACTLY 'depo meningioma claim how to qualify' and 'depo "
            "meningioma diagnosis compensation'. A small footer line 'If your diagnosis was a "
            "meningioma, you may qualify.'" + SUFFIX),
    },
    {
        "n": 13, "slug": "spotlight", "format": "spotlight profile", "style": "editorial persona photo",
        "angle": "Her diagnosis had a specific name",
        "headline": "A Specific Diagnosis",
        "pull_quote": "Her diagnosis had a specific name: meningioma.",
        "primary": ("After years on the Depo shot, her diagnosis had a specific name — meningioma. If "
                    "yours was too, you may qualify for significant compensation. See if you qualify."),
        "image_prompt": persona_img(
            "A Black woman about 52, natural hair going grey, calm and dignified, soft documentary "
            "light, plain background, looking slightly off-camera. ",
            "Her diagnosis had a specific name: meningioma."),
    },
    {
        "n": 14, "slug": "solidarity", "format": "solidarity statement", "style": "minimalist poster",
        "angle": "You're exactly who this is for",
        "headline": "For a Meningioma Diagnosis",
        "pull_quote": "If your diagnosis was a meningioma, this is for you.",
        "primary": ("If you were diagnosed with a meningioma and used Depo-Provera, you're exactly who "
                    "this is for — and you may qualify for significant compensation. See if you "
                    "qualify."),
        "image_prompt": (
            "A clean minimalist statement poster, warm muted background, large centered modern sans-"
            "serif, lots of negative space. Text reads EXACTLY: 'If your diagnosis was a meningioma,' "
            "then on a new line in bold 'this is for you.', then a small footer 'Used Depo-Provera? "
            "You may qualify for significant compensation.'" + SUFFIX),
    },
    {
        "n": 15, "slug": "case_card", "format": "case-file card", "style": "flat line-art",
        "angle": "The diagnosis that opens a claim",
        "headline": "The Diagnosis That Opens a Claim",
        "pull_quote": "DIAGNOSIS ON FILE: MENINGIOMA",
        "primary": ("One diagnosis opens this Depo-Provera claim: a meningioma. If that's on your file "
                    "and you used the shot, you may qualify for significant compensation. See if you "
                    "qualify."),
        "image_prompt": (
            "A clean flat line-art case-file card with a simple folder/document icon, a minimal palette "
            "of navy, white and one accent color. Text reads EXACTLY: a small label 'DIAGNOSIS ON "
            "FILE', then large bold 'MENINGIOMA', then an arrow line '→ may qualify', then a footer "
            "'Used Depo-Provera? Tap below to find out.'" + SUFFIX),
    },
    {
        "n": 16, "slug": "then_now", "format": "then / now split", "style": "editorial split",
        "angle": "Years on Depo, then one word",
        "headline": "Years on Depo, Then Meningioma",
        "pull_quote": "THEN: the Depo shot.  NOW: meningioma.",
        "primary": ("For some women the story ends with a specific diagnosis — a meningioma. If that's "
                    "yours, you may qualify for significant compensation. See if you qualify."),
        "image_prompt": (
            "A clean two-part 'then / now' split graphic, simple editorial style with a thin vertical "
            "divider line. Text reads EXACTLY: left side label 'THEN' with 'years on the Depo-Provera "
            "shot', right side label 'NOW' with 'one word — meningioma', then a footer bar 'You may "
            "qualify for significant compensation. Tap below.' Balanced, high-contrast." + SUFFIX),
    },
    {
        "n": 17, "slug": "circled_word", "format": "circled word", "style": "macro chart photo",
        "angle": "The exact word circled — clearly for meningioma",
        "headline": "Look for This Exact Word",
        "pull_quote": "meningioma (circled in red)",
        "primary": ("Check what your diagnosis was actually called. If that word is meningioma and you "
                    "used Depo-Provera, you may qualify for significant compensation. See if you "
                    "qualify."),
        "image_prompt": (
            "A realistic extreme close-up photo of a printed medical chart line on white paper, shallow "
            "depth of field, the single word 'meningioma' hand-circled in red ink and in sharp focus. "
            "A small bold caption at the bottom reads EXACTLY 'Look for this exact word.' and a footer "
            "line 'Used Depo-Provera? You may qualify.' Authentic, documentary, the circled word fully "
            "legible." + SUFFIX),
    },
    {
        "n": 18, "slug": "loved_one", "format": "loved-one referral", "style": "golden-hour persona photo",
        "angle": "Help her find out",
        "headline": "Was Her Diagnosis a Meningioma?",
        "pull_quote": "If her diagnosis was a meningioma.",
        "primary": ("If a woman you love was diagnosed with a meningioma and used Depo-Provera, she may "
                    "qualify for significant compensation. Help her find out. See if she qualifies."),
        "image_prompt": persona_img(
            "Two Black women — a daughter about 30 with an arm around her mother about 60 — in warm "
            "golden-hour light, a plain outdoor background, tender and quiet. ",
            "If her diagnosis was a meningioma."),
    },
    {
        "n": 19, "slug": "quiz", "format": "quiz / poll card", "style": "clean rounded UI",
        "angle": "Y/N qualifier — clearly sets the meningioma tone",
        "headline": "One Simple Question",
        "pull_quote": "Was your diagnosis a meningioma?",
        "primary": ("Was your diagnosis a meningioma? If yes, and you used the Depo-Provera shot, you "
                    "may qualify for significant compensation. Not sure? Check your records for that "
                    "word. See if you qualify."),
        "image_prompt": (
            "A clean modern quiz / poll card with a friendly rounded UI, soft background, large "
            "readable sans-serif. Text reads EXACTLY: a question 'Was your diagnosis a meningioma?', "
            "then two stacked tappable answer buttons — a filled button 'YES' and an outline button "
            "'NOT SURE — check your records' — then a small footer 'Used Depo-Provera? You may qualify "
            "for significant compensation.'" + SUFFIX),
    },
    {
        "n": 20, "slug": "investigative", "format": "investigative poster", "style": "serious editorial",
        "angle": "One word on a pathology report",
        "headline": "One Word Makes the Difference",
        "pull_quote": "One word on a pathology report: MENINGIOMA",
        "primary": ("In the Depo-Provera litigation, the diagnosis that matters is meningioma. If "
                    "that's the word on your report, you may qualify for significant compensation. See "
                    "if you qualify."),
        "image_prompt": (
            "A serious editorial / investigative poster, dark slate background, a restrained bold serif "
            "and sans mix with a thin underline accent. Text reads EXACTLY: a large line 'One word on "
            "a pathology report:' then bold 'MENINGIOMA', then a smaller line 'In the Depo-Provera "
            "litigation, that's the diagnosis that matters.', then a footer 'You may qualify for "
            "significant compensation.' Sober, high-contrast, legible." + SUFFIX),
    },
]


def dest_for(ad):
    return OUT / f"{ad['n']:02d}_{ad['slug']}.png"


def run_one(ad, regen, provider, size):
    dest = dest_for(ad)
    if dest.exists() and not regen:
        return ad["n"], ad["slug"], "skip"
    prompt = ad["image_prompt"]
    try:
        if provider == "kie":
            import kie_client as kie
            r = kie.generate_gpt_image(prompt, aspect_ratio="1:1", resolution="2K")
            if r.get("status") == "success" and r.get("urls"):
                kie.download(r["urls"][0], dest)
                return ad["n"], ad["slug"], "ok"
            return ad["n"], ad["slug"], f"fail:{str(r.get('raw'))[:80]}"
        from openai_image import generate_image
        r = generate_image(prompt, out_path=str(dest), size=size, quality="high")
        return ad["n"], ad["slug"], "ok" if r.get("status") == "success" else f"fail:{str(r)[:80]}"
    except Exception as e:
        return ad["n"], ad["slug"], f"err:{type(e).__name__}:{str(e)[:70]}"


def dump_copy():
    OUT.mkdir(parents=True, exist_ok=True)
    copy = [{k: ad[k] for k in ("n", "slug", "format", "style", "angle",
                                 "headline", "pull_quote", "primary")} for ad in ADS]
    (OUT / "copy.json").write_text(json.dumps(copy, indent=2, ensure_ascii=False))
    print(f"wrote {OUT/'copy.json'} ({len(copy)} ads)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--regen", action="store_true")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--provider", default="kie", choices=["kie", "openai"])
    ap.add_argument("--size", default="1024x1024")
    ap.add_argument("--dump", action="store_true", help="write copy.json and exit")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.dump:
        dump_copy()
        return
    ads = ADS
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        ads = [a for a in ADS if a["slug"] in want or str(a["n"]) in want]
    ok = fail = skip = 0
    fails = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, a, args.regen, args.provider, args.size): a for a in ads}
        for f in as_completed(futs):
            n, slug, st = f.result()
            print(f"[{st}] {n:02d} {slug}", flush=True)
            if st == "ok":
                ok += 1
            elif st == "skip":
                skip += 1
            else:
                fail += 1
                fails.append(f"{n:02d}_{slug}")
    print(f"\n=== ok={ok} skip={skip} fail={fail} / {len(ads)} ===", flush=True)
    if fails:
        print("FAILS:", ",".join(fails), flush=True)


if __name__ == "__main__":
    main()
