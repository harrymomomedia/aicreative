"""Stage the cawp launch list in AdMachin: 11 tailored primaries (user picks
A,D,H,J,M,Q,S,V,Y,CC,FF), upload the 12 not-yet-uploaded finals, assemble one draft ad per
video with the proven headline pair (Chowchilla winner / CIW variant). NO LAUNCHING.
Skip-if-done via a local state file; prints [ok] lines for monitoring."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import admachin_client as am

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"
SUB = "acf1b974-9721-488b-a4e0-ffe0664070c5"
HEADLINE_CHOW = "bb8294cc-7599-4cfa-9c97-2666b7f636a8"   # "Chowchilla Survivors May Qualify"
HEADLINE_CIW = "9e1d74c8-5524-4707-a8d5-0a7ce8f5c003"    # "CIW Survivors May Qualify"
STATE_PATH = "outputs/cawp_admachin_stage_state.json"

DISCLAIMER = (
    "Paid legal advertisement. Jordan M. Jones, Attorney at Law (360 E 2nd St #820, Los Angeles, "
    "CA 90012) and Adam Pulaski, Attorney at Law (2925 Richmond Ave #1725, Houston, TX 77098) are "
    "responsible for this advertisement. A California-licensed attorney is associated for CA "
    "cases. This ad uses paid actors, dramatizations, and AI-generated imagery for illustration "
    "only and does not depict real clients or events. No guarantee or prediction of outcome is "
    "made. Cases may be referred to other attorneys."
)

CONSTANT = (
    "Women from these facilities may qualify:\n\n"
    "• Chowchilla (CCWF)\n"
    "• Valley State Prison\n"
    "• California Institution for Women (CIW)\n\n"
    "\U0001F4C4 It counts even if you never reported it.\n\n"
    "✅ Free to check. Completely confidential.\n\n"
    "\U0001F447 Tap below to see if you qualify for significant potential compensation.\n\n"
    + DISCLAIMER
)

INTROS = {
    "A": ("⚠️ Did you see the news? That Chowchilla guard got 224 years.\n\n"
          "The jury believed the women — some testified while still locked up. Almost 500 "
          "more have already filed, and the federal government is now investigating both women's "
          "prisons.\n\n"
          "If a guard or staff member sexually abused you inside, this is the moment to take "
          "action. You may qualify for significant potential compensation."),
    "D": ("\U0001F4CB The claim form for women's prison survivors asks 4 questions. That's it.\n\n"
          "Which facility. Roughly when. Who it was. What happened — in your own words, as "
          "much or as little as you want.\n\n"
          "If staff sexually abused you inside, checking takes about two minutes, and you may "
          "qualify for significant potential compensation."),
    "H": ("Were you at Chowchilla or CIW? Did staff cross the line? Did you keep it to "
          "yourself?\n\n"
          "Almost 500 women answered yes to the same questions — and filed.\n\n"
          "What they did was sexual abuse, and you may qualify for significant potential "
          "compensation."),
    "J": ("Nobody warns you about the \"nice\" guard.\n\n"
          "The check-ins, the favors, the extra phone time — it was a setup. What came after "
          "was sexual abuse, even if it took years to call it that.\n\n"
          "It counts even if he never used force. You were locked up; you couldn't really say no. "
          "You may qualify for significant potential compensation."),
    "M": ("\U0001F494 \"Nobody's ever going to believe us.\" A jury just did.\n\n"
          "Thirteen women from Chowchilla testified — some still incarcerated — and "
          "that officer got 224 years.\n\n"
          "If a guard sexually abused you inside, it's a different world now. You may qualify "
          "for significant potential compensation."),
    "Q": ("\"Why didn't you report it?\" Some women did. Here's what happened to them.\n\n"
          "Solitary. Transfers. Case closed, insufficient evidence. The system taught women to "
          "keep their mouths shut.\n\n"
          "Telling works now — privately, through lawyers who don't work for the state. You "
          "may qualify for significant potential compensation."),
    "S": ("If you were at Chowchilla, you remember the buddy system.\n\n"
          "Nobody called it that — you just never walked certain places alone, and everybody "
          "knew which officers were the reason.\n\n"
          "That was sexual abuse happening in plain sight. The women who lived it may qualify for "
          "significant potential compensation."),
    "V": ("He knew her release date from CIW — and used it.\n\n"
          "A call-out you think is about going home, and it isn't. Going along because your date "
          "is sitting in his hands. That's sexual abuse.\n\n"
          "He can't touch your date now. You're home — and you may qualify for significant "
          "potential compensation."),
    "Y": ("You called it a relationship. In a prison. With a guard. Listen to how that "
          "sounds.\n\n"
          "Inside, you legally could not consent to staff — none of us could. It was sexual "
          "abuse, even if you went along, even if he was sweet about it.\n\n"
          "It still counts, and you may qualify for significant potential compensation."),
    "CC": ("The women who learned to sleep light at CIW know what this is about.\n\n"
           "Three in the morning is when nobody's watching the ones who are supposed to be "
           "watching us.\n\n"
           "What some officers did on night shift was sexual abuse — and you may qualify for "
           "significant potential compensation."),
    "FF": ("Why would anyone skip the doctor in prison? You know why.\n\n"
           "If you avoided those rooms to stay safe, you already understand what this ad is "
           "about.\n\n"
           "It counts even decades later — you may qualify for significant potential "
           "compensation."),
}

# ad group -> (pick, headline_id, [video files])
GROUPS = {
    "f1": ("A", HEADLINE_CHOW, []),  # creatives already uploaded; ads 375/376 updated separately
    "f2": ("D", HEADLINE_CHOW, ["outputs/cawp_f2_form/f2_form_explainer_v3_disclaimer.mp4"]),
    "f5": ("H", HEADLINE_CHOW, [
        "outputs/cawp_f5_l1/f5_l1_firedup_v1_nick_disclaimer.mp4",
        "outputs/cawp_f5_l1/f5_l1_stern_v1_nick_disclaimer.mp4",
        "outputs/cawp_f5_l1/f5_l1_heavy_v1_nick_disclaimer.mp4",
    ]),
    "r1": ("J", HEADLINE_CHOW, ["outputs/cawp_r1_niceone_l2/r1_niceone_l2_v1_nick_disclaimer.mp4"]),
    "r2": ("M", HEADLINE_CHOW, ["outputs/cawp_r2_believed_l4/r2_believed_l4_v1_nick_disclaimer.mp4"]),
    "r3": ("Q", HEADLINE_CHOW, ["outputs/cawp_r3_ididtell_l1/r3_ididtell_l1_v1_nick_disclaimer.mp4"]),
    "r4": ("S", HEADLINE_CHOW, ["outputs/cawp_r4_buddysystem_l2/r4_buddysystem_l2_v1_nick_disclaimer.mp4"]),
    "r5": ("V", HEADLINE_CIW, ["outputs/cawp_r5_mydate_l4/r5_mydate_l4_v1_nick_disclaimer.mp4"]),
    "r6": ("Y", HEADLINE_CHOW, ["outputs/cawp_r6_stillcounts_l2/r6_stillcounts_l2_v1_nick_disclaimer.mp4"]),
    "r7": ("CC", HEADLINE_CIW, ["outputs/cawp_r7_nightcount_l1/r7_nightcount_l1_v1_nick_disclaimer.mp4"]),
    "r8": ("FF", HEADLINE_CHOW, ["outputs/cawp_r8_appointments_l4/r8_appointments_l4_v1_nick_disclaimer.mp4"]),
}

AD_TYPE = "cawp-launchlist-2026-06"


def load_state():
    if os.path.exists(STATE_PATH):
        return json.load(open(STATE_PATH))
    return {"primaries": {}, "creatives": {}, "ads": {}}


def save_state(s):
    json.dump(s, open(STATE_PATH, "w"), indent=1)


def retry(fn, *a, tries=3, **kw):
    for t in range(1, tries + 1):
        try:
            return fn(*a, **kw)
        except Exception as e:
            if t == tries:
                raise
            print(f"  retry {t} after: {str(e)[:120]}", flush=True)
            time.sleep(5 * t)


def main():
    s = load_state()
    for grp, (pick, headline_id, videos) in GROUPS.items():
        if grp not in s["primaries"]:
            text = INTROS[pick] + "\n\n" + CONSTANT
            res = retry(am.create_ad_copy, text, "primary_text",
                        project_id=PROJECT, subproject_id=SUB,
                        name=f"CAWP {grp} primary (pick {pick})", platform="FB")
            s["primaries"][grp] = res["id"]
            save_state(s)
            print(f"[ok] primary {grp} (pick {pick}) -> {res['id']}", flush=True)

    for grp, (pick, headline_id, videos) in GROUPS.items():
        for v in videos:
            key = os.path.basename(v)
            if key not in s["creatives"]:
                res = retry(am.upload_creative, v, type="video",
                            project_id=PROJECT, subproject_id=SUB)
                s["creatives"][key] = res["id"]
                save_state(s)
                print(f"[ok] creative {key} -> {res['id']}", flush=True)
            if key not in s["ads"]:
                res = retry(am.create_ad, s["creatives"][key],
                            headline_id=headline_id, primary_id=s["primaries"][grp],
                            project_id=PROJECT, subproject_id=SUB, ad_type=AD_TYPE)
                s["ads"][key] = res["id"]
                save_state(s)
                print(f"[ok] ad {key} -> {res['id']}", flush=True)
    print("done — launch list staged (drafts only, nothing launched)", flush=True)


if __name__ == "__main__":
    main()
