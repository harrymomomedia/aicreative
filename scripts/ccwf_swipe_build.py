"""Assemble the 20 swipe-concept image ads into AdMachin draft ads (women's-prison subproject).
Upload final disclaimer-bar image -> create primary (disclaimer appended) -> create/reuse headline
-> create_ad. Drafts only; nothing launches. Run once.

  python scripts/ccwf_swipe_build.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import admachin_client as am

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"
SUBPROJ = "acf1b974-9721-488b-a4e0-ffe0664070c5"
IMGDIR = Path("outputs/ccwf_women/swipe_concepts/final")

DISCLAIMER = (
    "Paid legal advertisement. Jordan M. Jones, Attorney at Law (360 E 2nd St #820, Los Angeles, "
    "CA 90012) and Adam Pulaski, Attorney at Law (2925 Richmond Ave #1725, Houston, TX 77098) are "
    "responsible for this advertisement. A California-licensed attorney is associated for CA cases. "
    "This ad uses paid actors, dramatizations, and AI-generated imagery for illustration only and "
    "does not depict real clients or events. No guarantee or prediction of outcome is made. Cases "
    "may be referred to other attorneys."
)

HEADLINES = {
    "A": "Sexually Abused in a California Women's Prison?",
    "B": "Were You at Chowchilla, CIW, or Valley State?",
    "C": "California Women's Prison Survivors May Qualify",
    "D": "Check If You Qualify — Free & Confidential",
    "E": "It's Not Too Late — Check If You Qualify",
    "F": "Former Inmates Could Be Owed Compensation",
    "G": "Do You Remember What They Did?",
    "H": "Abused by Staff Behind Bars? You Have Options",
    "I": "Your Story Deserves to Be Heard",
    "J": "Women Are Coming Forward — You Can Too",
}

# (slug, image stem, headline key, primary body)
CONCEPTS = [
    ("c01", "c01_id_card", "G",
     "Remember your inmate ID number? Then you remember what they did. If a staff member sexually "
     "abused you at a California women's prison — Chowchilla (CCWF), Valley State, CIW (Chino), or "
     "Folsom — you may qualify for significant potential compensation. No proof needed. 100% "
     "confidential. Free. Even if it was years ago. 👉 Tap to see if you qualify."),
    ("c02", "c02_yesno_poll", "B",
     "Were you held in a California women's prison between 2005 and 2024? If a staff member sexually "
     "abused you, you may qualify for significant potential compensation. Facilities include "
     "Chowchilla (CCWF), Valley State, CIW (Chino), and Folsom.\n"
     "✅ No proof or police report needed\n✅ 100% confidential and free\n"
     "✅ Even if it was years ago or you never reported it\n👉 Tap to check your eligibility."),
    ("c03", "c03_tap_location", "H",
     "Cell block. Medical. Laundry. The unit office. If a staff member sexually abused you anywhere "
     "inside a California women's prison (Chowchilla, Valley State, CIW, Folsom), you may qualify for "
     "significant potential compensation. No proof needed. Confidential. Free. 👉 Tap to start."),
    ("c04", "c04_input_field", "F",
     "Former California women's prison inmates: if a staff member sexually abused you at Chowchilla "
     "(CCWF), Valley State, CIW (Chino), or Folsom, you may qualify for significant potential "
     "compensation. No proof needed. 100% confidential. Free. Even if it was years ago. 👉 Check "
     "your eligibility in about 2 minutes."),
    ("c05", "c05_checkbox_quiz", "D",
     "Two questions. Were you in a California women's prison — Chowchilla, Valley State, CIW, or "
     "Folsom? Did a staff member sexually abuse you? If yes, you may qualify for significant "
     "potential compensation. No proof needed. Confidential. Free. 👉 Take the 30-second quiz."),
    ("c06", "c06_facility_checklist", "A",
     "Were you sexually abused by a staff member while you were incarcerated in a California women's "
     "prison? You are not alone — and what happened to you was not your fault.\n\n"
     "For years, women inside California's prisons were sexually abused by the officers, guards, "
     "counselors, and medical staff who were supposed to keep them safe. Many never said a word — "
     "out of fear of retaliation, out of shame, or because they believed no one would take their "
     "side over a guard's. That silence is finally breaking, and survivors are being heard.\n\n"
     "If a staff member sexually abused you at any of these facilities, you may qualify for "
     "significant potential compensation:\n"
     "• Central California Women's Facility — Chowchilla (CCWF)\n"
     "• Valley State Prison — Chowchilla\n"
     "• California Institution for Women — Chino (CIW)\n"
     "• Folsom Women's Facility\n\n"
     "✅ You do NOT need a police report, medical records, or any proof to start\n"
     "✅ You may qualify even if you can only name or describe the officer\n"
     "✅ It's 100% confidential — nobody in your life has to know\n"
     "✅ Completely free, no upfront cost — you never pay unless compensation is recovered\n"
     "✅ It doesn't matter how long ago it happened, or that you never reported it\n\n"
     "A private review takes about two minutes and is handled with care. No obligation, and no one "
     "shows up at your door. 👉 Tap below to find out, confidentially, if you may qualify."),
    ("c07", "c07_facility_grid", "B",
     "CCWF. VSP. CIW. FWF. If a staff member sexually abused you at any California women's prison, "
     "you may qualify for significant potential compensation.\n"
     "✅ No proof needed — even if you can only name or describe the officer\n"
     "✅ 100% confidential and free, no upfront cost\n"
     "✅ Even if it was years ago, even if you never reported it\n"
     "👉 Tap to check eligibility for Chowchilla, Valley State, CIW, or Folsom."),
    ("c08", "c08_dublin_precedent", "C",
     "In 2024, women at FCI Dublin — a federal women's prison in California — received over $1 "
     "million each on average in settlements after sexual abuse by staff.\n\n"
     "If you were sexually abused by a staff member in a California state women's prison, you may "
     "also qualify for significant potential compensation. We're reviewing claims from:\n"
     "• Chowchilla (CCWF) • Valley State Prison • California Institution for Women (Chino) • Folsom "
     "Women's Facility\n"
     "✅ No proof or police report needed\n✅ 100% confidential and free — no upfront cost\n"
     "✅ Even if it was years ago, even if you never reported it\n"
     "👉 Tap to see if you qualify — about 2 minutes."),
    ("c09", "c09_settlement_100m", "J",
     "Over 100 women from a California women's prison received more than $100 million after sexual "
     "abuse by staff.\n\n"
     "If it happened to you, you may qualify for significant potential compensation. Survivors from "
     "these facilities are coming forward:\n"
     "• Chowchilla (CCWF) • Valley State Prison • California Institution for Women (Chino) • Folsom "
     "Women's Facility\n"
     "✅ No proof needed — you may qualify if you can name or describe the officer\n"
     "✅ 100% confidential and free, no upfront cost\n"
     "✅ Even if it was years ago, even if you never reported it\n👉 Tap to see if you qualify."),
    ("c10", "c10_breaking_news", "F",
     "A former California women's prison guard was convicted of sexually abusing women in his "
     "custody — and he's not the only one. Survivors are coming forward now.\n\n"
     "If a staff member sexually abused you while incarcerated, you may qualify for significant "
     "potential compensation. We're reviewing claims from:\n"
     "• Chowchilla (CCWF) • Valley State Prison • California Institution for Women (Chino) • Folsom "
     "Women's Facility\n"
     "✅ No police report or proof needed\n✅ 100% confidential — free, no upfront cost\n"
     "✅ Even if it was years ago, even if you never reported it\n👉 Tap to see if you qualify."),
    ("c11", "c11_official_notice", "A",
     "OFFICIAL NOTICE — to women formerly incarcerated in California state women's facilities.\n\n"
     "If you were sexually abused by a staff member during your incarceration, you may be entitled "
     "to pursue significant potential compensation.\n\n"
     "Across California, women are coming forward about sexual abuse, assault, and coercion by "
     "correctional officers, guards, counselors, and medical staff. Claims are now being reviewed "
     "for women held at:\n"
     "• Central California Women's Facility — Chowchilla (CCWF)\n"
     "• Valley State Prison — Chowchilla\n"
     "• California Institution for Women — Chino (CIW)\n"
     "• Folsom Women's Facility\n\n"
     "You may qualify even if: ✅ you never filed a report at the time ✅ it happened many years ago "
     "✅ you have no documents or proof ✅ you can only remember the officer's name or describe what "
     "they looked like\n\n"
     "What you can expect: ✅ a 100% confidential review — nobody has to know ✅ no upfront cost — "
     "you never pay unless compensation is recovered ✅ a short, private case review handled with "
     "respect\n\n"
     "Many survivors stayed silent for years, fearing they wouldn't be believed or that speaking up "
     "would make things worse. That's exactly what the system counted on. It's not holding anymore — "
     "and your story matters. 👉 Tap below to confidentially check whether you may qualify. About "
     "two minutes."),
    ("c12", "c12_news_quote", "I",
     "For years, the sexual abuse of women by staff inside California prisons went ignored. That "
     "silence is finally breaking. If it happened to you at Chowchilla (CCWF), Valley State, CIW "
     "(Chino), or Folsom, you may qualify for significant potential compensation.\n"
     "✅ No proof or police report needed\n✅ 100% confidential and free\n"
     "✅ Even if it was years ago, even if you never reported it\n👉 Tap to see if you qualify."),
    ("c13", "c13_fake_tweet", "J",
     "California women's prison staff are being accused of sexual assault, and survivors are coming "
     "forward. If a staff member abused you at Chowchilla (CCWF), Valley State, CIW (Chino), or "
     "Folsom, you may qualify for significant potential compensation.\n"
     "✅ No proof needed ✅ 100% confidential ✅ Free, no upfront cost\n"
     "✅ Even if it was years ago or you never reported it\n👉 Tap to see if you qualify."),
    ("c14", "c14_news_article", "C",
     "California women's prison sexual abuse survivors may qualify for significant potential "
     "compensation.\n\n"
     "For decades, women incarcerated in California's prisons reported being sexually abused by the "
     "very staff responsible for their custody — officers, guards, counselors, medical personnel. "
     "For just as long, those reports were ignored, dismissed, or buried. That's changing. A wave of "
     "survivors is coming forward, and attorneys are actively reviewing claims.\n\n"
     "If a staff member sexually abused you at Central California Women's Facility — Chowchilla "
     "(CCWF), Valley State Prison, California Institution for Women — Chino (CIW), or Folsom Women's "
     "Facility, a free and confidential review can tell you whether you may have a case.\n"
     "✅ No police report, records, or proof required to begin\n"
     "✅ You may qualify even if you can only name or describe the officer\n"
     "✅ 100% confidential — nobody in your life has to know\n"
     "✅ Completely free, no upfront cost — you never pay unless compensation is recovered\n"
     "✅ It doesn't matter how long ago it was, or that you never reported it\n\n"
     "No obligation, no judgment, no one contacts the people in your life. A private review takes "
     "about two minutes. 👉 Tap to read more and confidentially check whether you may qualify."),
    ("c15", "c15_provocative", "H",
     "Your uniform was never consent. If a guard or staff member sexually abused you inside a "
     "California women's prison, what happened was not your fault — and you may qualify for "
     "significant potential compensation. Chowchilla (CCWF), Valley State, CIW (Chino), Folsom.\n"
     "✅ No proof or police report needed ✅ 100% confidential ✅ Free\n"
     "✅ Even if it was years ago or you never reported it\n👉 Tap to see if you qualify."),
    ("c16", "c16_memory_hook", "G",
     "Do you still remember the officer's name? A lot of survivors do. If a staff member sexually "
     "abused you inside a California women's prison — Chowchilla (CCWF), Valley State, CIW (Chino), "
     "or Folsom — you may qualify for significant potential compensation.\n"
     "✅ No proof needed — naming or describing the officer can be enough\n"
     "✅ 100% confidential and free\n✅ Even if it was years ago or you never reported it\n"
     "👉 Tap to see if you qualify."),
    ("c17", "c17_cdcr_headline", "A",
     "Sexually abused by staff while incarcerated in a California women's prison? You may qualify "
     "for significant potential compensation. Chowchilla (CCWF), Valley State, CIW (Chino), Folsom.\n"
     "✅ No proof or police report needed\n✅ 100% confidential — nobody has to know\n"
     "✅ Free, no upfront cost — even if it was years ago, even if you never reported it\n"
     "👉 Tap to see if you qualify."),
    ("c18", "c18_visit_photo_headline", "I",
     "If you did time in a California women's prison, you probably still have a photo like this one "
     "— taken in the visiting room, in front of that painted mural.\n\n"
     "What a lot of us never talked about is what happened when the visitors went home. The "
     "officers, the guards, the staff who were supposed to protect us — and what some of them did "
     "when no one was watching.\n\n"
     "A lot of women carried that in silence for years. Out of shame. Out of fear no one would "
     "believe an inmate over a guard. I understand it, because so many of us lived it.\n\n"
     "That silence is finally breaking. If a staff member sexually abused you at Chowchilla (CCWF), "
     "Valley State Prison, California Institution for Women (Chino), or Folsom Women's Facility, you "
     "may qualify for significant potential compensation.\n"
     "✅ You don't need a police report or any proof\n"
     "✅ You may qualify even if you can only name or describe the officer\n"
     "✅ It's 100% confidential — nobody in your life has to know\n"
     "✅ It's free, no upfront cost — you never pay unless compensation is recovered\n"
     "✅ It doesn't matter how long ago it was, or that you never reported it\n"
     "👉 Tap below for a free, confidential review. About two minutes."),
    ("c19", "c19_relational", "J",
     "Your sister. Your mother. Your best friend. If a woman you love was sexually abused by staff "
     "in a California women's prison, she may qualify for significant potential compensation — even "
     "if she's never said a word. Chowchilla (CCWF), Valley State, CIW (Chino), Folsom.\n"
     "✅ No proof or police report needed ✅ 100% confidential ✅ Free\n"
     "✅ Even if it was years ago or never reported\n👉 Share this, or tap to learn more."),
    ("c20", "c20_thennow", "E",
     "I'm in my 50s now. Chowchilla was a lifetime ago for me — or at least that's what I kept "
     "telling myself.\n\n"
     "For years I had this whole part of my life locked in a box I never opened. I got out, I put "
     "my head down, I tried to build something normal. I never told my kids. I never told my "
     "husband. I never told anyone what one of the officers did to me in there, more than once, "
     "when no one was around to see it. Who would have believed me? An inmate, against a guard with "
     "a badge and a clean file? That's the bet they were making the whole time — that we'd stay "
     "quiet.\n\nSo I stayed quiet. For decades.\n\n"
     "Then a few weeks ago someone close to me sent me an article. Women from California's women's "
     "prisons are coming forward about being sexually abused by staff — and they may qualify for "
     "significant potential compensation for what was done to them. I sat at my kitchen table and "
     "read it twice. Because that happened to me. And it happened to so many of us — women I was "
     "inside with, women who never said a word either.\n\n"
     "I almost talked myself out of looking into it. I'm so glad I didn't. Here's what I found out "
     "— the things I wish someone had told me twenty years ago:\n"
     "✅ You don't need a police report, records, or any proof to start\n"
     "✅ You may qualify even if all you remember is his name, or what he looked like\n"
     "✅ It is 100% confidential — nobody in my life had to know I was even looking\n"
     "✅ It's completely free — no upfront cost, and you never pay unless compensation is recovered\n"
     "✅ It doesn't matter that it was years ago. It doesn't matter that I never reported it back "
     "then\n\n"
     "It's for women who were at Chowchilla (CCWF), Valley State Prison, California Institution for "
     "Women (Chino), and Folsom Women's Facility.\n\n"
     "If you're reading this and your stomach just dropped because you know exactly what I'm talking "
     "about — please hear me. It is not too late. I thought it was. It's not. 👉 Tap below to see, "
     "privately, if you qualify."),
]


def main():
    hcache = {}
    print(f"building {len(CONCEPTS)} ads into project={PROJECT[:8]} subproj={SUBPROJ[:8]}", flush=True)
    rows = []
    for slug, stem, hk, body in CONCEPTS:
        img = IMGDIR / f"{stem}_disc.png"
        if not img.is_file():
            print(f"  {slug}: MISSING image {img} — skip", flush=True); continue
        try:
            cr = am.upload_creative(str(img), type="image", project_id=PROJECT, subproject_id=SUBPROJ)
            prim = am.create_ad_copy(body + "\n\n" + DISCLAIMER, "primary_text",
                                     project_id=PROJECT, subproject_id=SUBPROJ,
                                     name=f"swipe {slug} (image ad)")
            if hk not in hcache:
                h = am.create_ad_copy(HEADLINES[hk], "headline", project_id=PROJECT,
                                      subproject_id=SUBPROJ, name=f"swipe H-{hk}")
                hcache[hk] = h["id"]
            ad = am.create_ad(cr["id"], headline_id=hcache[hk], primary_id=prim["id"],
                              project_id=PROJECT, subproject_id=SUBPROJ)
            rows.append((slug, ad.get("row_number"), hk))
            print(f"  {slug}: ad #{ad.get('row_number')}  (H-{hk})  creative {cr['id'][:8]}", flush=True)
        except Exception as e:
            print(f"  {slug}: ERROR {e}", flush=True)
    print(f"\nDONE — {len(rows)}/{len(CONCEPTS)} ads assembled (drafts, not launched).", flush=True)
    print("rows:", ", ".join(f"{s}=#{n}" for s, n, _ in rows), flush=True)


if __name__ == "__main__":
    main()
