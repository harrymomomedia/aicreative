"""Justice Covered eligibility-quiz FB image ad — PROFESSIONALLY DESIGNED via gpt-image-2 (KIE, 2K,
1:1), logo passed as i2i reference so the brand mark is incorporated. 5 distinct design directions
(not clones of the original white-card reference). Text is regulated — QA each render for verbatim
spelling; re-roll any typo.

  python scripts/jc_quiz_designs.py
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, upload_file, download as kie_download

LOGO = "/Users/harry/Desktop/yoigso1nztvls5wccxhz.webp"
OUT = Path("outputs/ccwf_women/image_ads")

TEXT = (
    ' EXACT TEXT to render, verbatim, spelled perfectly:'
    ' Headline: "Experienced sexual abuse in a California women\'s prison?"'
    ' List options: "Chowchilla (CCWF)" / "Valley State Prison" / "CIW (Chino)" / "Folsom Women\'s Facility"'
    ' Reassurance line: "You may qualify for significant potential compensation."'
    ' Button: "Start your free eligibility quiz"'
    ' Brand name: "JUSTICE COVERED" with the attached scales-of-justice logo mark.'
    ' No other text anywhere. Every word spelled exactly as given.'
)

DESIGNS = [
    ("des1_navy_card",
     "Professional Facebook ad for a legal-services brand. Deep navy blue background, a clean white "
     "rounded card centered containing the headline in bold charcoal, the four facility options as "
     "elegant list rows with subtle teal checkmark icons, the reassurance line below, and a wide "
     "rounded teal CTA button. Logo mark + brand name small at the top center. Premium, trustworthy "
     "law-firm design language, generous whitespace, crisp modern sans-serif typography."),
    ("des2_minimal_light",
     "Professional Facebook ad, premium minimal design: soft off-white background, dark navy bold "
     "typography, the headline large at top, four facility options as floating white chip cards "
     "with soft shadows and small navy radio dots, reassurance line in medium grey, a vivid green "
     "pill CTA button at the bottom, logo + brand name bottom center. Looks like a polished fintech "
     "or healthcare UI ad, lots of breathing room."),
    ("des3_split_panel",
     "Professional Facebook ad, split layout: left third is a deep navy vertical panel with the "
     "logo at top and the headline in white bold type stacked; right two-thirds is a light "
     "form panel with the four facility options as clean bordered rows with blue radio circles, "
     "reassurance line, and a navy CTA button at the bottom right. Sharp editorial grid, "
     "professional legal-brand aesthetic."),
    ("des4_phone_mock",
     "Professional Facebook ad: soft blue-grey gradient background, a realistic smartphone mockup "
     "slightly angled in the center showing the eligibility quiz on screen (headline at top of the "
     "screen, the four facility options as tappable rows, green CTA button), with the headline also "
     "written large in navy above the phone, and the logo + brand name below the phone. Clean app-"
     "marketing design style, soft shadows, premium."),
    ("des5_bold_flat",
     "Professional Facebook ad, bold flat editorial design: warm light background, oversized navy "
     "headline at top, the four facility options as two rows of rounded outline pill chips, a thin "
     "divider, reassurance line in dark grey, full-width deep-navy CTA button with white text at "
     "the bottom, small logo + brand name top-left. Confident modern law-brand poster, strong "
     "typographic hierarchy."),
]


def gen(slug, desc, logo_url):
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(desc + TEXT, aspect_ratio="1:1", resolution="2K",
                                 image_urls=[logo_url])
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    logo_url = upload_file(LOGO)
    print(f"logo uploaded: {logo_url}", flush=True)
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(gen, s, d, logo_url) for s, d in DESIGNS]
        for f in as_completed(futs):
            print(f.result(), flush=True)
