"""Batch 2 — 20 NEW distinct FB image-ad concepts for the CA women's-prison campaign, mined from the
full swipe library (formats NOT used in batch 1): tap-year/region grids, fake iMessage/Q&A, quote
cards, reframe/urgency/objection, artifact/quiet formats, object macro, news clipping. ALL gpt-image-2
(KIE, 2K, 1:1). Factual only, Black + Latina personas, "significant potential compensation". No
disclaimer here (later pass). QA every render for verbatim spelling; re-roll garbled text.

  python scripts/ccwf_swipe2_concepts.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/ccwf_women/swipe2_concepts")
TEXTRULE = (" Render every quoted line of text EXACTLY as written, spelled perfectly and clearly "
            "legible. NO other text, words, letters, logos, or watermarks anywhere in the image.")
PHOTO = (" Photoreal documentary photo, ordinary working-class realism, natural light, real skin "
         "texture and imperfections, no beauty retouching, no filter, not stylized — like a real "
         "news or phone photo.")
GRAPHIC = (" Clean modern flat direct-response Facebook ad design, crisp legible bold sans-serif "
           "typography, strong contrast, generous spacing, professional.")

CONCEPTS = [
    ("n01_tap_years", "Clean direct-response ad on a dark navy background. Bold white headline at top: "
     "'When were you held in a California women's prison?'. Below it a 2x2 grid of four rounded "
     "tappable tiles labeled 'Before 2000', '2000-2010', '2010-2020', '2020-Now'. Small line at the "
     "bottom: 'Survivors of staff sexual abuse may qualify for significant potential compensation.'"
     + GRAPHIC + TEXTRULE),
    ("n02_ca_map", "Clean direct-response ad on a light background showing a simple stylized teal map "
     "of the state of California with four location pins. Bold dark headline above: 'Where were you "
     "incarcerated?'. Four small pin labels: 'Chowchilla', 'Chino', 'Folsom', 'Valley State'. Bottom "
     "line: 'Survivors may qualify for significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("n03_select_happened", "Clean direct-response ad on a dark background. Bold white headline: 'Tap "
     "what happened to you'. A vertical list of four rounded tappable tiles: 'Pulled from your cell', "
     "'Strip search', 'Coerced for favors', 'Touched by staff'. A green button at the bottom: 'See if "
     "you qualify'." + GRAPHIC + TEXTRULE),
    ("n04_form_preview", "Clean ad on a soft blue-grey background showing a simple private intake form "
     "on a white phone-style card. Form title: 'Confidential Case Review'. Two labeled fields "
     "'Facility' and 'Year', and a green button 'Start'. Bold dark headline above the card: 'One "
     "private form. No names shared.'. Small line below: 'CA women's prison survivors may qualify for "
     "significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("n05_survivors_counter", "Direct-response ad over a dim, empty California prison cell-block "
     "corridor with a dark overlay. Bold white text: 'Survivors are coming forward. You are not the "
     "only one.'. Smaller line below: 'California women's prison staff sexual abuse — you may qualify "
     "for significant potential compensation.'" + PHOTO + TEXTRULE),
    ("n06_imessage", "A realistic screenshot of a text-message conversation on a phone, grey incoming "
     "bubbles and blue outgoing bubbles. Messages in order: 'did you hear they're finally taking the "
     "CCWF cases?', 'wait what', 'if a guard did something to you, you might qualify'. A small caption "
     "bar at the very bottom: 'Survivors may qualify for significant potential compensation.'. Looks "
     "exactly like a real iMessage screenshot." + GRAPHIC + TEXTRULE),
    ("n07_ask_me", "A realistic social-media question-and-answer card on white. A bold question: 'I "
     "never reported it. Can I still do anything?'. An answer below in regular weight: 'Yes. Survivors "
     "of staff sexual abuse in a California women's prison may qualify for significant potential "
     "compensation, even with no paperwork.'. Looks like a real comment-reply screenshot."
     + GRAPHIC + TEXTRULE),
    ("n08_review_quote", "A clean testimonial quote card on an off-white background. A row of five gold "
     "stars at the top. A large bold centered quote: '\"I thought it was too late. It wasn't.\"'. A "
     "small circular portrait inset of an ordinary middle-aged Black woman in the lower corner. "
     "Smaller bottom line: 'CA women's prison survivors of staff sexual abuse may qualify for "
     "significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("n09_consensual_reframe", "A photoreal shot from behind of a Black woman in a pale-blue California "
     "prison chambray shirt, dark gradient at the bottom. Bold white overlaid text: 'They called it "
     "consensual. California law calls it abuse.'. Smaller line: 'Survivors may qualify for "
     "significant potential compensation.'" + PHOTO + TEXTRULE),
    ("n10_feeling_enough", "A weathered middle-aged Latina woman sitting quietly by a window in soft "
     "light, looking down, reflective. Bold white overlaid text across the lower third: 'If it still "
     "doesn't feel right after all these years, that feeling is enough.'. Smaller line: 'You may "
     "qualify for significant potential compensation.'" + PHOTO + TEXTRULE),
    ("n11_no_paperwork", "Clean direct-response ad on white. Bold dark headline: 'You may still qualify "
     "- even if:'. Three rows each with a green checkmark: 'You never reported it', 'It was years "
     "ago', 'You have no paperwork'. Bottom line: 'CA women's prison survivors of staff sexual abuse "
     "may qualify for significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("n12_urgency", "Direct-response ad on a dark charcoal background with a small simple clock icon. "
     "Bold white headline: 'Claim reviews are open now.'. Subline: 'Time limits apply. California "
     "women's prison survivors may qualify for significant potential compensation.'. A green button: "
     "'Check if you qualify'." + GRAPHIC + TEXTRULE),
    ("n13_calculator", "A clean ad styled like an estimate card on a light background with a simple "
     "calculator icon. Bold dark headline: 'What could your case be worth?'. Subline: 'CA women's "
     "prison survivors of staff sexual abuse may qualify for significant potential compensation.'. A "
     "green button: 'Start your free case review'. NO dollar amounts or numbers anywhere."
     + GRAPHIC + TEXTRULE),
    ("n14_postcard", "An intimate still life: an old faded prison visitation photo of a young Black "
     "woman in a pale-blue uniform lying on a wooden table next to a short handwritten note on lined "
     "paper. The handwritten note reads only: 'It wasn't your fault. It's not too late.'. A small "
     "printed caption at the bottom edge: 'Survivors may qualify for significant potential "
     "compensation.'" + PHOTO + TEXTRULE),
    ("n15_whisper_quote", "A quiet minimal ad on a dark muted background, no photo. A large bold serif "
     "pull-quote centered: '\"Nobody was supposed to find out. Then other women started talking.\"'. A "
     "small line at the bottom: 'CA women's prison survivors may qualify for significant potential "
     "compensation. 100% confidential.'" + GRAPHIC + TEXTRULE),
    ("n16_then_now_split", "A vertical split-screen photo ad of the SAME Latina woman. Left half: a "
     "faded older photo of her as a young woman, with a caption 'The year you got out.'. Right half: "
     "her older today, looking hopeful in warm light, with a caption 'The year you finally got "
     "answers.'. A caption bar at the very bottom: 'Survivors may qualify for significant potential "
     "compensation.'" + PHOTO + TEXTRULE),
    ("n17_problem_solution", "Clean two-column direct-response ad. Left column header in grey: 'THE "
     "SILENCE' with text below 'They told you no one would believe you.'. Right column header in "
     "green: 'THE TRUTH' with text below 'California law is on your side.'. A line across the bottom: "
     "'Survivors may qualify for significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("n18_two_women", "A photoreal candid documentary photo of two ordinary Latina women of similar "
     "age sitting close together on a couch, both looking at the camera with quiet seriousness, plain "
     "everyday clothes, available light. Bold white overlaid text on a dark gradient at the bottom: "
     "'If it happened to you, or someone you were inside with, you may qualify for significant "
     "potential compensation.'" + PHOTO + TEXTRULE),
    ("n19_button_macro", "An extreme macro close-up photo of the buttons and collar of a pale-blue "
     "California prison chambray uniform shirt, shallow depth of field, soft natural light, visible "
     "fabric weave. Small bold white text in the lower corner: 'You remember the uniform. The law "
     "remembers too.'. Smaller line: 'Survivors may qualify for significant potential compensation.'"
     + PHOTO + TEXTRULE),
    ("n20_verdict_clipping", "An ad styled like a clipped newspaper article on aged newsprint. Bold "
     "serif headline: 'Courts are holding California prisons accountable.'. A couple of lines of "
     "greyed newspaper body text below, and one highlighted line: 'Survivors of staff sexual abuse "
     "may qualify for significant potential compensation.'. Looks like a real news clipping."
     + GRAPHIC + TEXTRULE),
]


def gen(slug, prompt):
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(prompt, aspect_ratio="1:1", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, p) for s, p in CONCEPTS]
        for f in as_completed(futs):
            print(f.result(), flush=True)
