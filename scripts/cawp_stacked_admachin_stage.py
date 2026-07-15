#!/usr/bin/env python3
"""Stage the CAWP women's-prison yapper set in AdMachin — DRAFT ONLY, no launch.

8 scripts (P, S1-S7) × 2 cuts (stacked male-guard + non-stacked full-frame) = 16 ads.
Each script = 1 headline copy row + 1 primary copy row (disclaimer appended), shared by
both its cuts. Resumable: one state file, skip-if-done per step. ad_type OMITTED
(ads.ad_type DB check-constraint — memory feedback_admachin_ad_type_constraint).
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import admachin_client as am

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"      # Tort
SUB     = "acf1b974-9721-488b-a4e0-ffe0664070c5"      # Women's Prison
POD     = os.path.join(ROOT, "outputs", "chowchilla_podcast")
STATE   = os.path.join(ROOT, "outputs", "cawp_stacked_admachin_state.json")

DISCLAIMER = ("Paid legal advertisement. Jordan M. Jones, Attorney at Law (360 E 2nd St #820, "
    "Los Angeles, CA 90012) and Adam Pulaski, Attorney at Law (2925 Richmond Ave #1725, Houston, "
    "TX 77098) are responsible for this advertisement. A California-licensed attorney is associated "
    "for CA cases. This ad uses paid actors, dramatizations, and AI-generated imagery for "
    "illustration only and does not depict real clients or events. No guarantee or prediction of "
    "outcome is made. Cases may be referred to other attorneys.")

HEADLINES = {
 "P":  "You're Not the Only One Who Remembers",
 "S1": "They Made Reporting It Cost You",
 "S2": "Fifteen Years Later — And It Wasn't Too Late",
 "S3": "Three Things You Believe That Aren't True",
 "S4": "You Were Never the Only One",
 "S5": "It Was Never Shame. It Was Training.",
 "S6": "You Carried It Long Enough",
 "S7": "Thirty Years, and Nobody in Her Life Knew",
}

BODIES = {
 "P": """When I filed, I thought it was my word against his. It wasn't.

The lawyers don't build these cases on one story — they look for the pattern. Same facility. Same years. Same staff.

One woman remembers a hallway. Another names the same officer. That's not one story anymore — that's a pattern of abuse.

If you were sexually abused inside a California women's prison — Chowchilla, Valley State, CIW, or Folsom — you may not be the only one.

Checking is private and confidential, just you and the lawyers. You may qualify for significant potential compensation.

👉 Tap to see where you stand.""",

 "S1": """I did time in a California women's prison. This past year I've helped other women file claims for the sexual abuse that happened inside.

Here's what the system doesn't want you to know.

It wasn't rare — same facilities, same officers, same stories.

Almost nobody reported it back then, because reporting got YOU punished. Not reporting doesn't disqualify you.

The women who stayed quiet the longest are the ones who qualify most often. Twenty years of silence doesn't close the door.

If a guard or staff member sexually abused you at Chowchilla, Valley State, CIW, or Folsom, there's a private form — a few questions, between you and the lawyers.

You may qualify for significant potential compensation.

👉 Take the two minutes.""",

 "S2": """She carried what a guard did to her at CIW for fifteen years, and told herself that door closed a long time ago.

Then she found out California changed the law. Women can file claims now, even for sexual abuse that happened years back — and those claims may mean significant potential compensation.

It took her a few minutes to fill out the form. Everything stayed private, between her and the lawyers.

If you were sexually abused inside a California women's prison — Chowchilla, Valley State, CIW, or Folsom — it's not too late for you either.

👉 Check for yourself.""",

 "S3": """A woman almost let this pass her by because she believed three things that aren't true.

"Nobody believes an incarcerated woman." Wrong — these cases get built from patterns: dozens of women describing the same officers, the same threats.

"It's been too long." Wrong — California opened the door for claims from years back.

"I'd have to face him in court." Wrong — the claim is against the institution that let it happen, and most women never see a courtroom.

What happened to her was sexual abuse, and she may qualify for significant potential compensation. She filled out the form — private, just her and the lawyers.

If a guard or staff member abused you at Chowchilla, Valley State, CIW, or Folsom, don't let the myths decide for you.

👉 Check for yourself.""",

 "S4": """She was sure nobody would believe her. A guard sexually abused her inside, and she'd never said it out loud — not once.

What she didn't know: hundreds of women from that same facility were already filing claims. Women she walked the yard with. Women she never met. All telling stories that matched hers.

She wasn't alone — she just couldn't see the others. When she found out, she filled out the form that same night.

If you were sexually abused at a California women's prison — Chowchilla, Valley State, CIW, or Folsom — you're not the only one, and you may qualify for significant potential compensation.

The form's private.

👉 See where you stand.""",

 "S5": """The most common reason women from places like Chowchilla never came forward about the sexual abuse inside? It's not shame. It's training.

Inside, we learned telling made it worse. You report it, you get written up. You get moved. Your parole date gets played with. Silence felt like the only safe move.

That's exactly why the law changed. California opened the door for women like us to file claims now — and those claims may mean significant potential compensation, even for things that happened way back.

If a guard or staff member sexually abused you at Chowchilla, Valley State, CIW, or Folsom, staying quiet doesn't have to be the plan anymore. One private form, you and the lawyers.

👉 Check where you stand.""",

 "S6": """Since I came home I've talked with about fifty women who did time at CIW or Chowchilla — women who went through sexual abuse inside, like I did.

It never broke them. They raised kids, held down jobs, carried the whole thing in silence.

But strength shouldn't mean carrying it for free. A lot of them are checking their claims now, and many may qualify for significant potential compensation. Quietly, privately, between them and the lawyers — nobody else.

If you were abused at Chowchilla, Valley State, CIW, or Folsom, take the two minutes. You've carried enough already.

👉 See where you stand.""",

 "S7": """I've helped a lot of women get their claims for sexual abuse inside the California prisons looked at this past year. Three things surprised me.

How much the stories overlap — different women, different years, same officers, same buildings. It was never just you, and that overlap is exactly why these claims may qualify for significant potential compensation.

How many never told a single soul — husbands of thirty years who still don't know. That's fine; the form is private.

And how fast checking is compared to how long we waited. Women sat on this twenty years, and the check took two minutes.

If a guard or staff member sexually abused you at Chowchilla, Valley State, CIW, or Folsom, that's all it takes.

👉 See where you stand.""",
}

CUTS = {  # cut label -> filename template
 "stacked": "{L}_stacked_male_redwood_disclaimer.mp4",
 "regular": "{L}_full_redwood_disclaimer.mp4",
}

def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {}

def save(st):
    json.dump(st, open(STATE, "w"), indent=2)

def main():
    st = load()
    for L in ["P","S1","S2","S3","S4","S5","S6","S7"]:
        e = st.setdefault(L, {})
        primary_text = BODIES[L].strip() + "\n\n" + DISCLAIMER
        # 1. headline copy row
        if not e.get("headline_id"):
            r = am.create_ad_copy(HEADLINES[L], "headline", project_id=PROJECT,
                                  subproject_id=SUB, name=f"CAWP WP {L} headline")
            e["headline_id"] = r["id"]; save(st); print(f"[{L}] headline {r['id']}")
        # 2. primary copy row
        if not e.get("primary_id"):
            r = am.create_ad_copy(primary_text, "primary_text", project_id=PROJECT,
                                  subproject_id=SUB, name=f"CAWP WP {L} primary")
            e["primary_id"] = r["id"]; save(st); print(f"[{L}] primary {r['id']}")
        # 3. per-cut: upload creative + create ad
        for cut, tmpl in CUTS.items():
            path = os.path.join(POD, tmpl.format(L=L))
            assert os.path.exists(path), path
            c = e.setdefault(cut, {})
            if not c.get("creative_id"):
                r = am.upload_creative(path, project_id=PROJECT, subproject_id=SUB)
                c["creative_id"] = r["id"]; save(st); print(f"[{L}/{cut}] creative {r['id']}")
            if not c.get("ad_id"):
                r = am.create_ad(c["creative_id"], headline_id=e["headline_id"],
                                 primary_id=e["primary_id"], project_id=PROJECT,
                                 subproject_id=SUB)  # ad_type OMITTED
                c["ad_id"] = r["id"]; save(st); print(f"[{L}/{cut}] AD {r['id']}")
    save(st)
    n_ads = sum(1 for L in st for cut in CUTS if st[L].get(cut, {}).get("ad_id"))
    print(f"\nDONE — {n_ads} draft ads staged (NO launch). State: {STATE}")

if __name__ == "__main__":
    main()
