"""Batch 3 — 20 NEW distinct FB image-ad concepts for the CA women's-prison campaign, in the
IL-JDC designed/news style (the formats performing well), every ad a DIFFERENT format and NONE
repeating the 74 already in the campaign (no ID card / poll / map / form / checklist / iMessage /
tweet / news-clipping / then-now / calculator / postcard / cinematic prison scenes / selfies).
Only ONE testimonial. ALL gpt-image-2 (KIE, 2K, 1:1). Factual / allegation framing only, Black +
Latina personas, "significant potential compensation". Disclaimer added in a later bar pass.
QA every render for verbatim spelling; re-roll garbled text.

  python scripts/ccwf_jdcstyle20.py            # generate all (skip-if-exists)
  python scripts/ccwf_jdcstyle20.py --only j07_reddit,j13_voicemail
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/ccwf_women/jdcstyle20")
TEXTRULE = (" Render every quoted line of text EXACTLY as written, spelled perfectly and clearly "
            "legible. NO other text, words, letters, logos, or watermarks anywhere in the image.")
GRAPHIC = (" Clean modern flat direct-response Facebook ad design, crisp legible bold sans-serif "
           "typography, strong contrast, generous spacing, professional.")
NEWS = (" Realistic news/editorial design, authentic newspaper or news-website typography and "
        "layout, documentary news photography, not flashy, looks like genuine journalism.")
PHOTO = (" Photoreal documentary photo, ordinary working-class realism, natural light, real skin "
         "texture and imperfections, no beauty retouching, no filter, not stylized — like a real "
         "news or phone photo.")

CONCEPTS = [
    # ── News / editorial family (6) ──────────────────────────────────────────
    ("j01_newspaper",
     "A realistic black-and-white newspaper FRONT PAGE, aged newsprint texture, photographed "
     "slightly angled on a table. Masthead across the top in classic serif: 'THE GOLDEN STATE "
     "LEDGER'. A small kicker above the headline: 'STATEWIDE INVESTIGATION'. A large bold serif "
     "headline: 'California women's prisons face wave of staff sexual-abuse lawsuits'. A subhead "
     "below it: 'Survivors at Chowchilla, Chino, Valley State and Folsom may qualify for "
     "significant potential compensation.'. Two narrow columns of small grey body text and a "
     "black-and-white documentary photo of an empty prison corridor." + NEWS + TEXTRULE),

    ("j02_tv_broadcast",
     "A realistic television news broadcast still, as if paused on a TV screen. A slightly soft "
     "broadcast-quality background showing the exterior of a large institutional prison building "
     "under a flat grey sky. A red-and-white lower-third graphics bar across the bottom with bold "
     "white text: 'WOMEN ALLEGE STAFF SEXUAL ABUSE IN CALIFORNIA PRISONS'. A thin ticker strip "
     "under it reads: 'Survivors may qualify for significant potential compensation'. A small "
     "white 'LIVE' tag in the top-left corner." + TEXTRULE),

    ("j03_accountability",
     "A realistic online news article hero layout. A documentary photo of the California State "
     "Capitol dome under a clear sky. A small red kicker above: 'ACCOUNTABILITY'. A bold dark "
     "headline: 'Lawsuits say California failed to protect women in its prisons'. A grey subhead "
     "below: 'Staff sexually abused women in custody for years, the suits allege. Survivors may "
     "qualify for significant potential compensation.'." + NEWS + TEXTRULE),

    ("j04_explainer",
     "A clean editorial explainer card on a soft off-white background with muted navy and teal "
     "accents. A bold title at top: 'WHAT SURVIVORS SHOULD KNOW'. Four short stacked points, each "
     "with a small simple line icon: 'Staff sexual abuse in a California women's prison may "
     "qualify you', 'No police report needed', 'No deadline — even decades later', '100% free and "
     "confidential'. A line at the bottom: 'You may qualify for significant potential "
     "compensation.'." + GRAPHIC + TEXTRULE),

    ("j05_magazine",
     "A glossy magazine FEATURE spread layout. A large serif display headline at the top: 'The "
     "Reckoning Inside California's Women's Prisons'. A grey italic dek below: 'For years, women "
     "said staff sexually abused them behind bars. Now survivors are being heard.'. Two columns of "
     "small ILLEGIBLE greeked placeholder body text — blurry lorem-ipsum-style filler with NO readable words, sentences, or claims, a large pull-quote: '\"I never thought anyone would believe me.\"', and a "
     "moody editorial photo of an ordinary middle-aged Latina woman in shadow looking out a "
     "window. A small line at the bottom: 'Survivors may qualify for significant potential "
     "compensation.'." + NEWS + TEXTRULE),

    ("j06_oped",
     "A realistic newspaper OPINION column layout on off-white paper. A small red kicker: "
     "'OPINION'. A bold serif headline: 'They were ignored for years. Now they're being "
     "believed.'. A byline line: 'Commentary'. A single column of small grey ILLEGIBLE greeked placeholder body text (lorem-ipsum-style filler, NO readable words, sentences, or claims). A line"
     "set apart at the bottom in slightly bolder type: 'Survivors of staff sexual abuse in "
     "California women's prisons may qualify for significant potential compensation.'." + NEWS + TEXTRULE),

    # ── Social-proof / native family (4) ─────────────────────────────────────
    ("j07_reddit",
     "A realistic Reddit screenshot on a white background. At the top a subreddit label "
     "'r/Ex_Inmates' with a small icon. A post title in bold: 'Did anyone else get abused by "
     "staff at CCWF?'. Upvote and downvote arrows with a count '312' on the left. Below, a top "
     "comment in a slightly indented box from user 'survivor_voice': 'You're not alone. If a "
     "guard or staff member sexually abused you at a California women's prison, you may qualify "
     "for significant potential compensation. No police report needed, and it's completely "
     "confidential.'. Looks exactly like a real Reddit thread." + TEXTRULE),

    ("j08_comments",
     "A realistic GENERIC online comment-section screenshot on a plain white card — NOT Facebook, "
     "no Facebook logo, no blue header bar, no like/share/comment chrome, no platform branding of "
     "any kind. A small post caption at the top: "
     "'California women's prison survivors — you are being heard.'. Below it, three comments, each "
     "with a small round profile photo of an ordinary Black or Latina woman and a first name: "
     "'This happened to me at Chino. I never told anyone.', 'My sister was at Valley State. Same "
     "thing.', 'I thought I was the only one. Thank you for posting this.'. A pinned reply at the "
     "bottom in slightly bolder text: 'Survivors may qualify for significant potential "
     "compensation — free and confidential.'." + TEXTRULE),

    ("j09_google",
     "A realistic Google search box on a clean white page, centered, with a typed query 'were "
     "women sexually abused at' and an autocomplete dropdown of grey suggestions below it: "
     "'chowchilla women's prison', 'ciw chino by staff', 'california women's prison guards', "
     "'valley state prison'. A small line beneath the search box: 'If it happened to you, you may "
     "qualify for significant potential compensation.'." + GRAPHIC + TEXTRULE),

    ("j10_native_post",
     "A plain Facebook text status post with NO photo, on a solid deep-teal background with large "
     "white centered text (the native colored-background status style). The text reads: 'If you "
     "were sexually abused by staff while you were in a California women's prison, please read "
     "this. You are not alone. It was not your fault. You may qualify for significant potential "
     "compensation — it's free, private, and no one has to know.'. Looks like a real organic "
     "Facebook status, no ad design." + TEXTRULE),

    # ── Document / object family (4) ─────────────────────────────────────────
    ("j11_definition",
     "An extreme close-up of a dictionary page in soft natural light, shallow focus. One entry is "
     "in sharp focus: the bold word 'co·er·cion' with phonetics '/koh-UR-zhun/' and "
     "'noun' in italics, then the definition: 'the use of authority or power to force someone into "
     "sexual acts against their will.'. Below the entry, slightly separated, a clean printed line: "
     "'If a staff member did this to you in a California women's prison, the law calls it abuse. "
     "You may qualify for significant potential compensation.'." + TEXTRULE),

    ("j12_calendar",
     "A clean graphic ad on a soft paper background showing a simple row of year labels '2005   "
     "2010   2015   2020   2024' with light grey strike-throughs. A bold dark headline above: "
     "'There is no deadline to come forward.'. A smaller line below: 'It doesn't matter how long "
     "ago it was.'. A line at the bottom: 'California women's prison abuse survivors may qualify "
     "for significant potential compensation.'." + GRAPHIC + TEXTRULE),

    ("j13_voicemail",
     "A realistic smartphone screen showing a VOICEMAIL transcript. A header reads: 'Voicemail   "
     "·   Confidential Line   ·   0:42'. A play bar below it. Transcript text in grey: "
     "'Hi... I saw your post. Something happened to me at Chowchilla a long time ago, and I never "
     "told anyone. I think I'm finally ready to talk.'. A small caption bar at the very bottom: "
     "'You're not alone. Survivors may qualify for significant potential compensation.'." + TEXTRULE),

    ("j14_stickynote",
     "A photoreal close-up of a yellow sticky note stuck on a stainless-steel refrigerator door in "
     "soft kitchen light. Handwritten in blue ballpoint pen on the note: 'It wasn't your fault. "
     "You can still come forward — it's free and private.'. Below the note, a small clean printed "
     "label taped to the fridge reads: 'CA women's prison abuse survivors may qualify for "
     "significant potential compensation.'." + TEXTRULE),

    # ── Direct-response / educational family (4) ─────────────────────────────
    ("j15_faq",
     "A clean FAQ card on a soft off-white background with navy text. A bold title: 'FREQUENTLY "
     "ASKED'. Three question-and-answer pairs stacked, questions in bold and answers in regular "
     "weight: 'Q: It was years ago. Do I still qualify?   A: Yes — there is no deadline.', "
     "'Q: I never reported it.   A: You don't need a police report.', 'Q: Will anyone find out?   "
     "A: No. It's 100% confidential.'. A line at the bottom: 'Survivors may qualify for "
     "significant potential compensation.'." + GRAPHIC + TEXTRULE),

    ("j16_myth_fact",
     "A clean two-panel ad split down the middle. The LEFT panel on muted grey is labeled 'MYTH' "
     "in bold with the text: 'It's been too long. Nothing can be done.'. The RIGHT panel on bright "
     "teal-green is labeled 'FACT' in bold white with the text: 'There's no deadline. Survivors "
     "are coming forward now.'. A full-width line across the bottom: 'If staff sexually abused you "
     "in a California women's prison, you may qualify for significant potential compensation.'."
     + GRAPHIC + TEXTRULE),

    ("j17_numbers",
     "A clean modern infographic ad on a deep-navy background with large bold white-and-gold "
     "numbers. A title at top: 'BY THE NUMBERS'. Four stat blocks stacked: '4 — California women's "
     "prisons named: Chowchilla, Chino, Valley State, Folsom', '0 — police reports required', "
     "'No deadline to come forward', '100% free and confidential'. A line at the bottom: "
     "'Survivors of staff sexual abuse may qualify for significant potential compensation.'."
     + GRAPHIC + TEXTRULE),

    ("j18_authority",
     "A clean, professional, trustworthy direct-response card on a deep-navy background with "
     "restrained gold accents and a simple scales-of-justice line motif (no real logo). Bold white "
     "text: 'NOW REVIEWING CLAIMS'. Below: 'Sexual-abuse claims from survivors of California "
     "women's prisons — Chowchilla, Chino, Valley State, and Folsom.'. Then: 'Free, confidential "
     "case review.'. A line at the bottom: 'You may qualify for significant potential "
     "compensation.'." + GRAPHIC + TEXTRULE),

    # ── Human (minimal) (2) ──────────────────────────────────────────────────
    ("j19_lovedone",
     "A warm but realistic documentary photo of two ordinary women — an older Latina woman and a "
     "younger Black woman — sitting close together on a couch, one gently comforting the other, "
     "natural light, real skin texture, no glamour. Bold clean white text overlaid across the "
     "lower third: 'Your mother. Your sister. Your friend. If a woman you love was sexually abused "
     "by staff in a California women's prison, she may qualify for significant potential "
     "compensation.'." + PHOTO + TEXTRULE),

    ("j20_testimonial",
     "A photoreal candid iPhone-style selfie of a weathered middle-aged Latina woman, about 54, "
     "sitting at a modest kitchen table in soft natural light, tired eyes, no makeup, real skin "
     "texture and imperfections, an ordinary everyday look, not glamorous. A bold clean white text "
     "band across the lower third reads: 'A guard did things to me at Chowchilla. I never told a "
     "soul — until now.'. A smaller line below it: 'You may qualify for significant potential "
     "compensation.'." + PHOTO + TEXTRULE),
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
            return f"FAIL {slug}: {res.get('status')} {str(res.get('raw'))[:160]}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    todo = [(s, p) for s, p in CONCEPTS if (only is None or s in only)]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, p) for s, p in todo]
        for f in as_completed(futs):
            print(f.result(), flush=True)
    print(f"DONE — {len(todo)} concepts → {OUT}", flush=True)
