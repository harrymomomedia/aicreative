"""Stage the 12 R9 Mija ads in AdMachin: tailored SHORT primaries (hook echo + direct
sexual-abuse-to-compensation line + proven constant block), upload combos, assemble drafts.
Headlines: Chowchilla winner (bb8294cc) / CIW variant (9e1d74c8). NO LAUNCHING."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import admachin_client as am

PROJECT = "e15c60bd-95c2-47b9-9730-c29fb5325461"
SUB = "acf1b974-9721-488b-a4e0-ffe0664070c5"
H_CHOW = "bb8294cc-7599-4cfa-9c97-2666b7f636a8"
H_CIW = "9e1d74c8-5524-4707-a8d5-0a7ce8f5c003"
STATE_PATH = "outputs/cawp_admachin_r9_state.json"
AD_TYPE = "cawp-mija-2026-06"

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

DIRECT_CHOW = ("Guards and staff sexually abused women at Chowchilla for years. If it happened "
               "to you, you may qualify for significant potential compensation.")
DIRECT_CIW = ("Guards and staff sexually abused women at CIW for years. If it happened to you, "
              "you may qualify for significant potential compensation.")

# hook slug -> (hook echo line, headline id, direct line)
ADS = {
    "i": ("Twenty years of silence — until her old cellmate found her on Facebook.", H_CHOW, DIRECT_CHOW),
    "j": ("Twenty years later, just driving past Chowchilla still shakes her.", H_CHOW, DIRECT_CHOW),
    "k": ("Her daughter finally asked about Chowchilla.", H_CHOW, DIRECT_CHOW),
    "m": ("The article about Chowchilla sat in her phone for a week.", H_CHOW, DIRECT_CHOW),
    "o": ("She used to change the channel. Then Chowchilla was the headline.", H_CHOW, DIRECT_CHOW),
    "p": ("A woman from her old unit pulled her aside at a funeral.", H_CHOW, DIRECT_CHOW),
    "q": ("She promised her sister she'd never talk about Chowchilla again.", H_CHOW, DIRECT_CHOW),
    "s": ("Five women from her old yard already filed.", H_CHOW, DIRECT_CHOW),
    "v": ("At 56, she finally told her husband about Chowchilla.", H_CHOW, DIRECT_CHOW),
    "y": ("Nobody ever asks what happened to the women from CIW.", H_CIW, DIRECT_CIW),
    "x": ("Her old bunkie from CIW called her crying. Good crying.", H_CIW, DIRECT_CIW),
    "z": ("Her daughter found out about CIW from a news story.", H_CIW, DIRECT_CIW),
}


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
            print(f"  retry {t} after: {str(e)[:110]}", flush=True)
            time.sleep(5 * t)


def main():
    s = load_state()
    for slug, (echo, headline_id, direct) in ADS.items():
        if slug not in s["primaries"]:
            text = echo + "\n\n" + direct + "\n\n" + CONSTANT
            res = retry(am.create_ad_copy, text, "primary_text",
                        project_id=PROJECT, subproject_id=SUB,
                        name=f"CAWP mija {slug} primary (short/direct)", platform="FB")
            s["primaries"][slug] = res["id"]
            save_state(s)
            print(f"[ok] primary {slug} -> {res['id']}", flush=True)

        video = f"outputs/cawp_r9_mija_l2/r9_mija_{slug}_v1_nick_disclaimer.mp4"
        if slug not in s["creatives"]:
            res = retry(am.upload_creative, video, type="video",
                        project_id=PROJECT, subproject_id=SUB)
            s["creatives"][slug] = res["id"]
            save_state(s)
            print(f"[ok] creative {slug} -> {res['id']}", flush=True)
        if slug not in s["ads"]:
            res = retry(am.create_ad, s["creatives"][slug],
                        headline_id=headline_id, primary_id=s["primaries"][slug],
                        project_id=PROJECT, subproject_id=SUB, ad_type=AD_TYPE)
            s["ads"][slug] = res["id"]
            save_state(s)
            print(f"[ok] ad {slug} -> {res['id']}", flush=True)
    print("done — mija dozen staged (drafts only, nothing launched)", flush=True)


if __name__ == "__main__":
    main()
