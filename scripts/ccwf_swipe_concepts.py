"""20 DISTINCT-concept FB image ads for the CA women's-prison campaign, modeled on the dissected
tort swipe library (fake-UI / ID card / settlement-precedent / news-alert / social-post /
photo-overlay). ALL via gpt-image-2 (KIE, 2K, 1:1). Factual claims only (FCI Dublin + $100M are
referenced precedents that already happened). No disclaimer burned here — that's a later pass on
the picks. QA every render for verbatim spelling; re-roll garbled text.

  python scripts/ccwf_swipe_concepts.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/ccwf_women/swipe_concepts")
TEXTRULE = (" Render every quoted line of text EXACTLY as written, spelled perfectly and clearly "
            "legible. NO other text, words, letters, logos, or watermarks anywhere in the image.")
PHOTO = (" Photoreal documentary photo, natural light, real skin texture and imperfections, no "
         "beauty retouching, no filter, not stylized — looks like a real news or phone photo.")
GRAPHIC = (" Clean modern flat direct-response Facebook ad design, crisp legible bold sans-serif "
           "typography, strong contrast, generous spacing, professional.")

CONCEPTS = [
    # --- fake interactive UI / native-feel lead capture ---
    ("c01_id_card",
     "A photorealistic California state prison inmate ID card lying on a wooden table, pale-blue and "
     "white card with a small portrait of a weary middle-aged woman and the heading 'CDCR INMATE ID'. "
     "Large bold dark text above the card reads: 'Do you remember your inmate ID number?' and a green "
     "rounded button below reads: 'See if you qualify'." + GRAPHIC + TEXTRULE),
    ("c02_yesno_poll",
     "A direct-response ad on a clean dark background. Bold white headline: 'Were you held in a "
     "California women's prison between 2005 and 2024?'. Below it two large rounded buttons side by "
     "side, a green one labeled 'YES' and a grey one labeled 'NO'. Small line under them: 'Check if "
     "you may qualify for compensation.'" + GRAPHIC + TEXTRULE),
    ("c03_tap_location",
     "A direct-response ad. Top headline in bold white on dark: 'Where did the abuse happen?'. Below, "
     "a 2x2 grid of four rounded tappable tiles labeled 'Cell Block', 'Medical', 'Laundry', and 'Unit "
     "Office', each over a dim prison-interior photo. Bottom green button: 'Check eligibility'."
     + GRAPHIC + TEXTRULE),
    ("c04_input_field",
     "A direct-response ad mimicking a simple form on a light background. Bold headline: 'Former "
     "California women's prison inmates'. Below: 'Enter your inmate ID number to check eligibility' "
     "with an empty white rounded text input box showing a blinking cursor, and a green submit "
     "button labeled 'Check now'." + GRAPHIC + TEXTRULE),
    ("c05_checkbox_quiz",
     "A direct-response quiz card on a white background. Title: 'Do you qualify?'. Two checkbox rows "
     "with green checkmarks: 'Incarcerated in a California women's prison' and 'Sexually abused by a "
     "staff member'. Below, a green rounded button: 'Take the 30-second quiz'." + GRAPHIC + TEXTRULE),
    # --- qualifier cards ---
    ("c06_facility_checklist",
     "A clean direct-response ad. Bold headline: 'Sexually abused at one of these California women's "
     "prisons?'. A vertical list with green checkmarks: 'Chowchilla (CCWF)', 'Valley State Prison', "
     "'California Institution for Women (Chino)', 'Folsom Women's Facility'. Bottom line: 'You may "
     "qualify for significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("c07_facility_grid",
     "A bold direct-response ad on dark navy. Headline at top: 'You could be compensated for what "
     "happened at:'. A 2x2 grid of four large rounded tiles with big white acronyms 'CCWF', 'VSP', "
     "'CIW', 'FWF'. Bottom green button: 'Tap to check your eligibility'." + GRAPHIC + TEXTRULE),
    # --- settlement precedent / factual social proof ---
    ("c08_dublin_precedent",
     "A serious, credible direct-response ad over a faded photo of a prison exterior with razor wire. "
     "Bold white headline: 'Women at FCI Dublin received over $1 million each in 2024 settlements.'. "
     "Subline: 'California women's prison survivors may also qualify.'" + GRAPHIC + TEXTRULE),
    ("c09_settlement_100m",
     "A sober direct-response ad on a dark background. Large bold headline: 'Over 100 women from a "
     "California women's prison received more than $100 million.'. Subline below: 'If staff sexually "
     "abused you, you may qualify too.'" + GRAPHIC + TEXTRULE),
    # --- news / authority / alert ---
    ("c10_breaking_news",
     "A breaking-news style ad: a red banner across the top reading 'BREAKING NEWS', over a "
     "photoreal image of a California prison exterior with a guard tower. Below the banner a white "
     "lower-third caption reads: 'Former California women's prison guard convicted of sexual abuse.'"
     + TEXTRULE),
    ("c11_official_notice",
     "An official-document style ad that looks like a government notice on off-white paper, a small "
     "California state seal at the top, heading in serif: 'NOTICE TO FORMER INMATES'. Body line in "
     "bold: 'If you were sexually abused by staff at a California women's facility, you may qualify "
     "for significant potential compensation.'" + GRAPHIC + TEXTRULE),
    ("c12_news_quote",
     "A newspaper-style ad: black serif pull-quote on white newsprint with a thin rule, reading: "
     "'“The abuse of women by staff in California prisons went ignored for years.”'. Small "
     "italic attribution line below: '— investigative report'." + GRAPHIC + TEXTRULE),
    # --- fake social post ---
    ("c13_fake_tweet",
     "A realistic screenshot of a social media post on a white card. Account name in bold: 'Prison "
     "Justice' with a grey handle '@prisonjustice'. Post text: 'California women's prison staff "
     "accused of sexual assault.'. A row of engagement icons below with the numbers '12K', '4.5K', "
     "'892'. Looks exactly like a real X/Twitter post screenshot." + GRAPHIC + TEXTRULE),
    ("c14_news_article",
     "A realistic mockup of a news website article on a phone-screen card. Bold serif headline: "
     "'California women's prison sexual abuse survivors may qualify for compensation'. A photoreal "
     "news photo of a prison exterior below the headline, and a thin grey byline line. Looks like a "
     "real news article page." + GRAPHIC + TEXTRULE),
    # --- photo + overlay ---
    ("c15_provocative",
     "A photoreal shot from behind of a woman in a pale-blue prison shirt with faint yellow stencil "
     "lettering at a chain-link fence. Bold white overlaid text across the lower third: 'Your uniform "
     "was never consent.'" + PHOTO + TEXTRULE),
    ("c16_memory_hook",
     "A weary middle-aged Latina woman looking into the camera in a plain room, with bold white "
     "overlaid text across the lower third: 'Do you still remember the officer's name?'" + PHOTO
     + TEXTRULE),
    ("c17_cdcr_headline",
     "A photoreal shot from behind of a woman in a pale-blue California prison chambray shirt at a "
     "prison fence, with a dark gradient at the bottom and bold white text: 'Sexually abused by staff? "
     "You may qualify.'" + PHOTO + TEXTRULE),
    ("c18_visit_photo_headline",
     "An aged, faded early-2000s film snapshot of a Black woman in a pale-blue prison uniform posing "
     "in a prison visitation room in front of a painted beach mural, direct on-camera flash, grain, "
     "washed-out colors — a real shoebox visit photo. A clean white caption bar at the bottom reads: "
     "'What happened inside is finally being heard.'" + TEXTRULE),
    ("c19_relational",
     "A candid, unposed documentary photo of two ordinary Black women — one older, one younger — "
     "sitting close on a worn couch in a modest living room. The older woman holds in her hands an "
     "old faded printed photo of her younger self wearing a pale-blue prison uniform; the younger "
     "woman rests a comforting hand on her shoulder. Available window light, slight grain. NOT a "
     "stock photo, NOT staged, real imperfect faces. Bold white text at the bottom on a dark "
     "gradient: 'If she was in a California women's prison, she may have a claim.'" + PHOTO + TEXTRULE),
    ("c20_thennow",
     "A weathered Latina woman at her kitchen table holding up an old faded prison photo of her "
     "younger self, warm evening light, with bold white text on a dark gradient at the bottom: 'It's "
     "not too late to come forward.'" + PHOTO + TEXTRULE),
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
