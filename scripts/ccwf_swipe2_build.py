"""Assemble the 34 batch-2/3 image ads (n01-n20 swipe + m01-m14 creative) into AdMachin draft ads
(women's-prison subproject). Upload disclaimer-bar image -> create primary (disclaimer appended) ->
create headline -> create_ad. Drafts only; nothing launches. Run once.

  python scripts/ccwf_swipe2_build.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import admachin_client as am

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"
SUBPROJ = "acf1b974-9721-488b-a4e0-ffe0664070c5"
DISC = ("Paid legal advertisement. Jordan M. Jones, Attorney at Law (360 E 2nd St #820, Los Angeles, "
        "CA 90012) and Adam Pulaski, Attorney at Law (2925 Richmond Ave #1725, Houston, TX 77098) are "
        "responsible for this advertisement. A California-licensed attorney is associated for CA cases. "
        "This ad uses paid actors, dramatizations, and AI-generated imagery for illustration only and "
        "does not depict real clients or events. No guarantee or prediction of outcome is made. Cases "
        "may be referred to other attorneys.")

# (slug, image_path, headline, primary_body)
N = "outputs/ccwf_women/swipe2_concepts/final"
M = "outputs/ccwf_women/creative_concepts/final"
CONCEPTS = [
    ("n01", f"{N}/n01_tap_years_disc.png", "When Were You Inside?",
     "1998 or last year — the year doesn't matter. If a staff member sexually abused you in a "
     "California women's prison, you may qualify for significant potential compensation. No proof, no "
     "report, fully confidential. 👉 Tap your years to check."),
    ("n02", f"{N}/n02_ca_map_disc.png", "Were You at Chowchilla, CIW, or Valley State?",
     "If you were held at Chowchilla. Or Valley State. Or CIW in Chino, or Folsom. If a staff member "
     "crossed a line in any of them. If you've never said it out loud — you may still qualify for "
     "significant potential compensation. Free, confidential. 👉 Tap your facility to check."),
    ("n03", f"{N}/n03_select_happened_disc.png", "Abused by Staff Behind Bars? You Have Options",
     "✅ Held in a California women's prison\n✅ A guard, officer, counselor, or medical staffer crossed "
     "a line\n✅ Years ago is fine\n✅ Never reported is fine\n✅ No proof needed — a name or description "
     "can be enough\nIf any of these are you, you may qualify for significant potential compensation. "
     "Free. Confidential. 👉 Tap to check."),
    ("n04", f"{N}/n04_form_preview_disc.png", "Nobody Has to Know You Looked",
     "\"Will anyone find out?\" No — a private form, no names shared, nobody called. \"Do I need "
     "proof?\" No. \"Was it too long ago?\" Usually not. \"I never reported it…\" That's okay. If a "
     "staff member sexually abused you at Chowchilla, Valley State, CIW, or Folsom, you may qualify for "
     "significant potential compensation. 👉 Tap to check, privately."),
    ("n05", f"{N}/n05_survivors_counter_disc.png", "You Were Never the Only One",
     "What survivors are finally saying out loud:\n\"I thought it was just me.\"\n\"I never told a soul "
     "for 20 years.\"\n\"I didn't think anyone would believe an inmate.\"\nIf that's you, you're not "
     "alone — and you may qualify for significant potential compensation for sexual abuse by staff in a "
     "California women's prison. 👉 Tap to see."),
    ("n06", f"{N}/n06_imessage_disc.png", "A Friend Might Need to See This",
     "\"did you hear they're taking the CCWF cases now?\"\n\"wait, what cases\"\n\"if a guard ever did "
     "something to you in there, you might qualify\"\n\"…that was years ago. i never reported it\"\n"
     "\"doesn't matter. free, confidential, like two minutes.\"\nIf a staff member sexually abused you "
     "in a California women's prison, you may qualify for significant potential compensation. 👉 Tap to "
     "find out."),
    ("n07", f"{N}/n07_ask_me_disc.png", "I Never Reported It — Can I Still…?",
     "You're probably thinking it was too long ago. It usually isn't. That you have no proof. You don't "
     "need any. That someone will find out. No one has to. That it won't count because you never "
     "reported it. It still can. If a staff member sexually abused you in a California women's prison, "
     "you may qualify for significant potential compensation. 👉 Tap for a private answer."),
    ("n08", f"{N}/n08_review_quote_disc.png", "I Thought It Was Too Late",
     "MYTH: It's been too many years. FACT: Many survivors still qualify.\nMYTH: Without proof I have no "
     "case. FACT: You don't need proof.\nMYTH: I went along with it, so it doesn't count. FACT: In "
     "custody, a guard can't have your consent — it was abuse.\nSexually abused by staff in a CA "
     "women's prison? You may qualify for significant potential compensation. 👉 Tap to see."),
    ("n09", f"{N}/n09_consensual_reframe_disc.png", "It Was Never \"Consensual\"",
     "Did you know a staff member legally cannot have \"consent\" from a woman in their custody? "
     "Whatever they called it, whatever they made you feel — in California, that was abuse. If a guard "
     "or officer sexually abused you at Chowchilla, Valley State, CIW, or Folsom, you may qualify for "
     "significant potential compensation. 👉 Tap to see if you qualify."),
    ("n10", f"{N}/n10_feeling_enough_disc.png", "If It Still Doesn't Sit Right",
     "You don't need the perfect words for it. You don't need to have called it anything back then. If, "
     "after all these years, it still doesn't sit right when you think about that officer, that "
     "counselor, that night — that feeling is enough to ask the question. Women sexually abused by "
     "staff in California's women's prisons may qualify for significant potential compensation now, "
     "privately, with no proof and no report. 👉 Tap, whenever you're ready."),
    ("n11", f"{N}/n11_no_paperwork_disc.png", "No Records? You May Still Qualify",
     "No paperwork. No report. No proof. None of it disqualifies you. Sexually abused by staff at a CA "
     "women's prison — Chowchilla, Valley State, CIW, Folsom? You may qualify for significant potential "
     "compensation. Confidential. Free. 👉 Tap to check."),
    ("n12", f"{N}/n12_urgency_disc.png", "There May Be a Time Limit",
     "California opened a path for survivors — but there are time limits. If a staff member sexually "
     "abused you in a California women's prison, find out now if you qualify for significant potential "
     "compensation.\n✅ No proof or police report needed ✅ 100% confidential ✅ Free, no upfront cost\n"
     "👉 Tap to check — about 2 minutes."),
    ("n13", f"{N}/n13_calculator_disc.png", "What Could Your Case Be Worth?",
     "Every case is different, so no one can promise a number — but a free, confidential review can "
     "tell you if you may qualify for significant potential compensation. Sexually abused by staff at a "
     "CA women's prison? About 2 minutes. 👉 Start your free review."),
    ("n14", f"{N}/n14_postcard_disc.png", "To the Woman You Were",
     "To the woman you were back then —\nI know you did everything you could to survive that place. I "
     "know \"making a problem\" could cost you your visits, your level, your parole date — so when a "
     "staff member crossed a line, you did the math and you stayed quiet. That wasn't weakness. That "
     "was survival.\nBut I need you to hear something no one told you then: it wasn't your fault, and "
     "it's not too late.\nWomen sexually abused by staff inside California's women's prisons — "
     "Chowchilla (CCWF), Valley State, CIW (Chino), Folsom — may qualify for significant potential "
     "compensation. You don't need a police report. You don't need proof. You may qualify even if all "
     "you remember is his face. It's completely confidential — nobody in your life has to know — and "
     "it's free, with no upfront cost.\nYou carried this alone for a long time. You don't have to "
     "anymore.\n👉 Tap below to see, privately, if you qualify. P.S. — it takes about two minutes, and "
     "no one ever has to know you looked."),
    ("n15", f"{N}/n15_whisper_quote_disc.png", "Then Other Women Started Talking",
     "For years it stayed a secret, because that's what they counted on — that you'd be too ashamed, "
     "too scared, too sure no one would believe you. And then, quietly, other women started talking. "
     "One, then a few, then more. It turns out it was never just you. If a staff member sexually abused "
     "you in a California women's prison, you don't have to carry it alone anymore, and you may qualify "
     "for significant potential compensation. 👉 Tap to see if you qualify."),
    ("n16", f"{N}/n16_then_now_split_disc.png", "The Year You Finally Get Answers",
     "→ The year you went in.\n→ The year you got out and tried to forget.\n→ This year — when women "
     "from California's prisons are finally being heard about sexual abuse by staff, and finding out "
     "they may qualify for significant potential compensation.\nChowchilla, Valley State, CIW, Folsom. "
     "No proof needed. 👉 Tap to see if you qualify."),
    ("n17", f"{N}/n17_problem_solution_disc.png", "They Told You No One Would Believe You",
     "The whole system ran on one quiet threat: no one will believe an inmate over a guard. So you said "
     "nothing — and they knew you wouldn't. Every day you carried it, that silence protected them and "
     "cost you. That ends now. California law is on your side, and women sexually abused by staff in "
     "the state's women's prisons may qualify for significant potential compensation. No proof, no "
     "report, fully confidential. 👉 Tap to see if you qualify."),
    ("n18", f"{N}/n18_two_women_disc.png", "If It Happened to You — or Her",
     "If you were inside together. If you knew what was happening to the woman in the next bunk. If it "
     "happened to you and you've never told anyone. If you've wondered, all these years, whether "
     "anything could be done — there can be. Survivors of staff sexual abuse in California's women's "
     "prisons may qualify for significant potential compensation. 👉 Tap to learn more, or share this "
     "with her."),
    ("n19", f"{N}/n19_button_macro_disc.png", "You Remember the Uniform",
     "You remember the uniform. The keys. The way a door could open whenever they wanted. The law "
     "remembers too. If a staff member sexually abused you at Chowchilla, Valley State, CIW, or Folsom, "
     "you may qualify for significant potential compensation. Confidential. Free. 👉 Tap to see if you "
     "qualify."),
    ("n20", f"{N}/n20_verdict_clipping_disc.png", "The Courts Are Listening Now",
     "→ For years: women reported abuse by staff and were ignored.\n→ 2024: a federal women's prison in "
     "California paid survivors over a million dollars each.\n→ Now: state-prison survivors — "
     "Chowchilla, Valley State, CIW, Folsom — are coming forward and may qualify for significant "
     "potential compensation.\nThe thing that protected staff for decades is falling apart. 👉 Tap to "
     "see if you qualify."),
    ("m01", f"{M}/m01_return_gate_disc.png", "You Left. It Never Left You.",
     "I drove past Chowchilla last spring. I didn't plan to — the highway just takes you that way — but "
     "the second I saw the fence I had to pull over.\nI was inside there in my twenties. Three and a "
     "half years. There was an officer who figured out early that I'd do almost anything to keep my "
     "visits with my son, to not get written up, to make my board date clean. He used that. It started "
     "as \"favors\" and became something I still don't say out loud. Every time, his face said the same "
     "thing: who's going to believe you?\nHe was right, back then. I told one counselor. Nothing "
     "happened to him. Something happened to me — I got moved. So I learned the lesson they wanted me "
     "to learn, and I shut up. For almost twenty years.\nSitting on that shoulder, looking at the "
     "fence, I finally Googled it. Women from California's women's prisons are being heard now — if "
     "staff sexually abused you, you may qualify for significant potential compensation. Not just the "
     "federal place in the news. The state prisons. Chowchilla. Valley State. Chino. Folsom.\nHere's "
     "what I needed someone to tell me twenty years ago: You don't need a police report. You don't need "
     "proof — if you can describe him, that can be enough. It's free; you pay nothing unless "
     "compensation is recovered. And it's private. No one called my house. My son still knows only what "
     "I've chosen to tell him.\nIt took two minutes against twenty years. No one can promise how a case "
     "turns out. But I can tell you what it felt like to finally say the true thing and have someone "
     "treat it like it mattered.\nIf your chest got tight reading this, you already know. It is not too "
     "late. 👉 Tap below to see, privately, if you qualify."),
    ("m02", f"{M}/m02_at_fence_now_disc.png", "Some Things Don't Stay Behind the Fence",
     "You served your time. You walked out. You told yourself you left it all in there — the noise, the "
     "fear, the officer who always seemed to be working your unit. But some things don't stay behind "
     "the fence. They get in the car with you. They follow you home, into your sleep, into the way you "
     "still don't trust a man with keys. What he did to you wasn't your fault, and it wasn't nothing. "
     "If a staff member sexually abused you in a California women's prison, you may qualify for "
     "significant potential compensation — no proof, no report, completely confidential. 👉 Tap to see "
     "if you qualify."),
    ("m03", f"{M}/m03_windshield_lookback_disc.png", "You Don't Have to Go Back to Get Answers",
     "To the woman who never wants to see that place again —\nYou don't have to. You never have to set "
     "foot near those gates to find out if you have a case. It's a private form on your phone, a couple "
     "of minutes, and no one in your life has to know. If a staff member sexually abused you in a "
     "California women's prison — Chowchilla, Valley State, CIW, Folsom — you may qualify for "
     "significant potential compensation. No proof needed. 👉 Tap whenever you're ready."),
    ("m04", f"{M}/m04_small_against_wall_disc.png", "It Was Never a Fair Fight",
     "One woman, alone, against an entire institution — a badge, a uniform, and everyone's assumption "
     "that your word was worth less than his. That's not a fair fight, and it was never meant to be. "
     "It's exactly why so many women decided the safest thing was to say nothing and survive it. The "
     "ground has shifted. If a staff member sexually abused you in a California women's prison, you may "
     "qualify for significant potential compensation. No proof. No report. Confidential. 👉 Tap to see "
     "if you qualify."),
    ("m05", f"{M}/m05_then_now_fence_disc.png", "Then and Now",
     "There's a photo of me at 24, in the blues, standing in the yard at Valley State trying to smile "
     "for my mom's visit. I keep it in a drawer I don't open much.\nWhat that photo doesn't show is the "
     "officer who worked nights, and what he decided he was owed. Or the medical staffer who scheduled "
     "me when the unit was quiet. I didn't have words anyone would listen to. An inmate's word against "
     "theirs? I already knew how that ended.\nSo I did my time, came home, and built a whole life on "
     "top of it without ever looking down.\nA woman I was inside with found me on Facebook a few weeks "
     "ago. One line: \"Did you see they're taking our cases?\" I almost didn't answer. Then I read "
     "it.\nWomen sexually abused by staff in California's women's prisons — Valley State, Chowchilla, "
     "CIW in Chino, Folsom — may qualify for significant potential compensation. And the things I was "
     "sure would disqualify me didn't: No police report? I never made one. No proof? Not required. Only "
     "his face, not his full name? That can be enough. Years ago? Doesn't matter. And it's free, and "
     "confidential.\nThe woman in that old photo had no way to be heard. The woman I am today does. "
     "That's the whole difference, and it's enough.\nNo one can promise how a case turns out. But you "
     "deserve to find out. 👉 Tap below — private, free, about two minutes."),
    ("m06", f"{M}/m06_photo_held_at_prison_disc.png", "You Still Have the Photo",
     "My husband has never seen the photo I'm holding. Eleven years married, and he doesn't know I was "
     "ever inside — let alone what happened to me there.\nI was at CIW in Chino. Young and scared, and "
     "a counselor — someone whose whole job was supposed to be helping me — made it clear that help "
     "came with a price. I paid it, more than once, because the alternative was worse. Then I got out "
     "and buried the whole thing so deep I almost convinced myself it happened to someone else.\nIt "
     "didn't. It happened to me, and lately I've learned it happened to a lot of us.\nWomen from "
     "California's women's prisons — CIW, Chowchilla, Valley State, Folsom — sexually abused by staff "
     "may qualify for significant potential compensation. What stopped me for so long was fear that "
     "someone would find out. So here's what finally got me to look: it's completely confidential. No "
     "one is called. No one shows up. My husband still only knows what I choose to tell him. You don't "
     "need proof or a report, and it costs nothing unless compensation is recovered.\nI held that old "
     "photo the whole two minutes I filled out the form, like I was finally telling that girl I "
     "believed her.\nIf you've been carrying this alone — it's not too late, and you don't have to tell "
     "a single person in your life to find out if you qualify. 👉 Tap below, privately."),
    ("m07", f"{M}/m07_two_survivors_gate_disc.png", "You Don't Have to Do This Alone",
     "Some of the women who were inside together are coming forward together now: \"We never talked "
     "about it back then. We're talking now.\" / \"I found out three of us had the same officer.\" / "
     "\"I didn't have to do it alone — and neither do you.\" If a staff member sexually abused you in a "
     "California women's prison, you may qualify for significant potential compensation. Confidential. "
     "Free. 👉 Tap to see if you qualify."),
    ("m08", f"{M}/m08_empty_visiting_room_disc.png", "This Is Where They Pretended Everything Was Fine",
     "Visiting day was the performance, and everyone knew their part.\nIn the visiting rooms of "
     "California's women's prisons, mothers held their kids and couples posed against a painted mural, "
     "and for a couple of hours everything looked fine. Then the families drove home, the doors locked, "
     "and for some of the women the part no one saw began.\nFor years that's how it worked. An officer "
     "who found reasons to be alone with an inmate. A counselor who traded \"favors\" for phone time or "
     "a clean disciplinary record. A night-shift staffer who knew which corners the cameras missed and "
     "that a woman's word rarely outweighed a badge. The ones who tried to report it watched their "
     "complaints vanish — dismissed, buried, sometimes punished. The message: no one will believe "
     "you.\nFor a long time, that held. It isn't holding anymore.\nSurvivors are coming forward about "
     "sexual abuse by staff at Central California Women's Facility (Chowchilla/CCWF), Valley State "
     "Prison, the California Institution for Women (Chino/CIW), and Folsom Women's Facility. Attorneys "
     "are reviewing claims, and women who were abused may qualify for significant potential "
     "compensation.\nMost believed they had no case. Most never filed a report. Most have no documents. "
     "None of that is disqualifying. A survivor doesn't need a police report or any proof; she may "
     "qualify even if she only remembers his face. It doesn't matter how long ago it was. The review is "
     "free — a fee only if compensation is recovered — and it's confidential.\nNo outcome is "
     "guaranteed; every case is different. But the door that was shut for so long is finally open. If a "
     "staff member sexually abused you inside a California women's prison, you may qualify for "
     "significant potential compensation. 👉 Tap below for a free, confidential review."),
    ("m09", f"{M}/m09_payphone_disc.png", "The Call You Could Never Make",
     "There was no one safe to call. No number for what was happening to you in there. Even if you'd "
     "reached someone, what would you say — and who would believe an inmate over a man with a badge and "
     "a clean file? So you didn't call. You survived it quietly, the way you survived everything. "
     "There's a number now. Women sexually abused by staff in California's women's prisons may qualify "
     "for significant potential compensation — privately, with no proof and no report required. 👉 Tap "
     "to make the call that actually helps."),
    ("m10", f"{M}/m10_gate_dusk_disc.png", "What Happened After Dark",
     "Did you know the law doesn't care how long ago it was? After the lights went down in California's "
     "women's prisons, staff did things to the women in their custody that should never have happened — "
     "and survivors may still qualify for significant potential compensation, years later. Chowchilla, "
     "Valley State, CIW, Folsom. No proof needed. Confidential. 👉 Tap to see if you qualify."),
    ("m11", f"{M}/m11_made_bunk_disc.png", "You Couldn't Lock Your Own Door",
     "You learned the sound of the right key in the wrong lock. A cell isn't safety when the people "
     "with the keys are the ones you need protecting from — and you couldn't lock your own door against "
     "them. So you lay there and waited for it to be over, and you told no one, because who exactly "
     "were you going to tell? It wasn't your fault. If a staff member sexually abused you in a "
     "California women's prison, you may qualify for significant potential compensation. 👉 Tap to see "
     "if you qualify."),
    ("m12", f"{M}/m12_redacted_grievance_disc.png", "They Had Every Report",
     "Some of the women did report it.\nThey filled out the grievance. They told a counselor, a "
     "sergeant, a chaplain — someone. They did the brave, dangerous thing and put it in writing. And "
     "then they watched it disappear. The form went nowhere. The complaint was \"unsubstantiated.\" "
     "Some were moved, written up, or sent to solitary for the crime of speaking — while the staff "
     "member they named kept his keys and his shift.\nThat's the part that doesn't get said enough: for "
     "a lot of survivors in California's women's prisons, the system didn't just fail to stop the "
     "abuse. It failed again, on purpose, when they tried to report it. The reports existed. They were "
     "buried.\nThat history is exactly why this matters now. Survivors of sexual abuse by staff at "
     "Chowchilla (CCWF), Valley State, CIW (Chino), and Folsom may qualify for significant potential "
     "compensation — whether or not their report ever went anywhere, whether or not there's any paper "
     "left at all.\nYou do not need that grievance. You don't need proof. You may qualify even if all "
     "you have is a name, or a description, and the truth of what happened. It's 100% confidential — "
     "nobody in your life has to know. It's free, with no upfront cost; you pay only if compensation is "
     "recovered. And it doesn't matter how many years have passed.\nNo one can promise an outcome, and "
     "every case is different. But the women who were told their reports didn't matter deserve to know "
     "that this time, someone is actually reading. 👉 Tap to see if you qualify."),
    ("m13", f"{M}/m13_editorial_poster_disc.png", "You Were Supposed to Be Safe",
     "You were in the state's custody. Whatever you did to land there, the deal was simple, and it was "
     "the law: you'd be kept safe from the people guarding you. For too many women in California's "
     "prisons, that promise was a lie — broken by the officers, the guards, the staff who knew no one "
     "was watching. That broken promise has a name now, and it has consequences. If a staff member "
     "sexually abused you, you may qualify for significant potential compensation. Chowchilla, Valley "
     "State, CIW, Folsom. Confidential, free, no proof needed. 👉 Tap to see if you qualify."),
    ("m14", f"{M}/m14_torn_mended_disc.png", "What They Broke Can Still Be Made Right",
     "To the woman holding the pieces —\nWhat they did to you in there broke something. I won't pretend "
     "a form fixes that, or gives you back the years you spent carrying it alone. It doesn't work like "
     "that.\nBut here's what I've watched happen for other women: what was broken can still be named. It "
     "can be answered for. The officer, the guard, the counselor who decided your body was theirs "
     "because you were in a uniform and they had the keys — that can finally cost them something, "
     "instead of only ever costing you.\nThat's its own kind of repair. Not the kind that erases it. "
     "The kind that says, out loud and on the record: this happened, it was wrong, and it was not your "
     "fault.\nWomen sexually abused by staff in California's women's prisons — Chowchilla, Valley "
     "State, CIW, Folsom — may qualify for significant potential compensation. You don't need proof or "
     "a report. You may qualify even years later, even if you never told anyone. It's free, and "
     "completely confidential.\nYou taped yourself back together once already, alone, just to get "
     "through. You don't have to do the next part alone.\n👉 Tap below to see, privately, if you "
     "qualify. P.S. — about two minutes, and no one ever has to know you looked."),
]


def main():
    print(f"building {len(CONCEPTS)} ads → project {PROJECT[:8]} / subproj {SUBPROJ[:8]}", flush=True)
    rows = []
    for slug, img, headline, body in CONCEPTS:
        if not Path(img).is_file():
            print(f"  {slug}: MISSING {img} — skip", flush=True); continue
        try:
            cr = am.upload_creative(img, type="image", project_id=PROJECT, subproject_id=SUBPROJ)
            prim = am.create_ad_copy(body + "\n\n" + DISC, "primary_text", project_id=PROJECT,
                                     subproject_id=SUBPROJ, name=f"img2 {slug}")
            head = am.create_ad_copy(headline, "headline", project_id=PROJECT, subproject_id=SUBPROJ,
                                     name=f"img2 H {slug}")
            ad = am.create_ad(cr["id"], headline_id=head["id"], primary_id=prim["id"],
                              project_id=PROJECT, subproject_id=SUBPROJ)
            rows.append((slug, ad.get("row_number")))
            print(f"  {slug}: ad #{ad.get('row_number')}  creative {cr['id'][:8]}", flush=True)
        except Exception as e:
            print(f"  {slug}: ERROR {e}", flush=True)
    print(f"\nDONE — {len(rows)}/{len(CONCEPTS)} ads assembled (drafts, not launched).", flush=True)
    print("rows: " + ", ".join(f"{s}#{n}" for s, n in rows), flush=True)


if __name__ == "__main__":
    main()
