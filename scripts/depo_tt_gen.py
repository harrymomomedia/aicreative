"""Depo TikTok-voice UGC series (depo_tt) — distinct-ARC scripts, punchy spoken register.
Series extends the ugc10 machinery for the TikTok-voiced batch (2026-07). Currently: ad05
THE GATEKEEPER (filter-first, exclusion lever). One persona per ad, direct-to-lens yapper.
Locked: meningioma-only vocabulary (never "brain tumor"), meningioma word inside ~5s,
compensation inside ~15s, "may qualify for significant compensation", attorney-calls-but-
confidential, NO disclaimer lingo. Gen path: useapi google-flow veo-3.1-lite-low-priority,
9:16 anchor via startImage, duration=8 (free-tier I2V requirements). clip01 off the persona
still; clips 02+ off eyes-open anchors rotated from clip01.

  python scripts/depo_tt_gen.py 5 test    # clip01 only (QA gate)
  python scripts/depo_tt_gen.py 5 full    # all clips
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleflow_client import generate_veo, upload_asset, download   # FREE veo-3.1-lite-low-priority

OUT = Path("outputs/depo_tt")
PRON = ('"meningioma" = "men-in-jee-OH-muh". "Depo" = "DEP-oh" with a short e like in "deck", '
        'NOT "dee-po", NOT "depot" (no T sound).')

ADS = {
    5: dict(
        slug="gatekeeper",
        persona="gate_persona_01_couch_pixie.png",   # overridden by --persona at pick time
        reg=("She is an ordinary Black woman about 45, confident and direct, filming a candid selfie "
             "video straight into her phone's front camera, TikTok style."),
        voice=("a confident, direct middle-aged Black woman's voice, warm but no-nonsense, quick and "
               "punchy delivery with clear diction, NOT young-sounding"),
        tone=("playful-stern command at the start, drops to conspiratorial just-between-us in the "
              "middle, firm and factual through the center, ends on a warm direct push"),
        body=("punchy natural movements. A dismissive little wave on the opening, then a lean-in "
              "toward the lens, an eyebrow raise, small decisive nods on the short lines."),
        script=("If you don't have a meningioma, keep scrolling. Bye. This is not for you. Okay. "
                "Now that it's just us. You have a meningioma. Did you ever take the Depo shot? "
                "Even years ago? Then listen to me. You may qualify for significant compensation. "
                "That's it. That's the filter. The diagnosis plus the shot. I had both and nobody "
                "told me they were connected. Nobody. Checking took me two minutes. It's free. "
                "A few questions. One attorney, total privacy, zero courtrooms. We didn't get a "
                "choice about the meningioma. This part is a choice. Two minutes, right where "
                "you're sitting, right now. See if you qualify. Everybody else already scrolled. "
                "You stayed. That means it's you. Go."),
        # hand-segmented: auto-split glued the tail into a 23-word clip (>8s of speech — Veo
        # rushes/cuts). Explicit clips keep every line 11-18w. Trailing improv on the shorter
        # closers gets removed by the word-aware trim at finalize.
        clips=[
            "If you don't have a meningioma, keep scrolling. Bye. This is not for you. Okay.",
            "Now that it's just us. You have a meningioma. Did you ever take the Depo shot?",
            "Even years ago? Then listen to me. You may qualify for significant compensation. That's it. That's the filter.",
            "The diagnosis plus the shot. I had both and nobody told me they were connected. Nobody.",
            "Checking took me two minutes. It's free. A few questions. One attorney, total privacy, zero courtrooms.",
            "We didn't get a choice about the meningioma. This part is a choice.",
            "Two minutes, right where you're sitting, right now. See if you qualify.",
            "Everybody else already scrolled. You stayed. That means it's you. Go.",
        ],
    ),
}


def segment(script, lo=12, hi=18):
    """Sentence-boundary split into ~12-18-word clips (Veo ~2.4wps over 8s); merges short
    fragments so no clip is underfilled (underfilled => Veo improvises)."""
    sents = re.findall(r"[^.?!]+[.?!]+", script)
    clips, cur = [], ""
    for s in sents:
        s = s.strip()
        cand = (cur + " " + s).strip()
        if not cur:
            cur = s
        elif len(cur.split()) < lo or len(cand.split()) <= hi:
            cur = cand
        else:
            clips.append(cur)
            cur = s
    if cur:
        if clips and len(cur.split()) < lo:
            clips[-1] += " " + cur
        else:
            clips.append(cur)
    return clips


def last_word(s):
    t = re.findall(r"[A-Za-z']+", s)
    return t[-1] if t else ""


def P(ad, line):
    return f"""{ad['reg']}
GAZE: straight into the phone lens, holding the viewer's eye; natural blinks. Warm dark-brown eyes, OPEN, the SAME color throughout (never lighter/changing).
BODY: {ad['body']}
VOICE: {ad['voice']}.
TONE: {ad['tone']}.
SPEED: about 2.4 words per second, punchy but every word clear.
AUDIO CRITICAL: she speaks clearly and fully audibly at a close conversational volume right into the phone mic. NOT whispered, NOT muttered.
PRONUNCIATION: {PRON}
DIALOGUE LOCK: English only. Say ONLY the words in SPOKEN DIALOGUE, in order. No fillers (no uh, um, like, you know), no extra or trailing words, no repetition. Stop after the final word "{last_word(line)}".
NO on-screen text, NO captions, NO subtitles, NO watermark.
SPOKEN DIALOGUE (verbatim, stop after final word): "{line}\""""


def gen(ad_n, ad, idx, line, mgid):
    out = OUT / f"ad{ad_n:02d}_{ad['slug']}" / f"clip{idx:02d}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 50000:
        return "cached"
    r = generate_veo(prompt=P(ad, line), image_mgid=mgid, duration=8, aspect_ratio="portrait")
    if r.get("status") != "success" or not r.get("urls"):
        return "FAIL: " + str(r.get("raw"))[:160]
    download(r["urls"][0], str(out))
    return "ok"


def main():
    ad_n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    mode = sys.argv[2] if len(sys.argv) > 2 else "test"
    persona_override = None
    for a in sys.argv[3:]:
        if a.startswith("--persona="):
            persona_override = a.split("=", 1)[1]
    ad = ADS[ad_n]
    if persona_override:
        ad["persona"] = persona_override
    clips = ad.get("clips") or segment(ad["script"])
    print(f"[ad{ad_n:02d} {ad['slug']}] {len(clips)} clips, persona={ad['persona']}", flush=True)
    mgid = upload_asset(str(OUT / ad["persona"]))
    if mode == "test":
        print(f"  clip01 -> {gen(ad_n, ad, 1, clips[0], mgid)}", flush=True)
        return
    print(f"  clip01 -> {gen(ad_n, ad, 1, clips[0], mgid)}", flush=True)
    adir = OUT / f"ad{ad_n:02d}_{ad['slug']}" / "anchors"
    if not list(adir.glob("_anchor_*.jpg")):
        subprocess.run([".venv/bin/python", "scripts/pick_clean_anchors.py",
                        str(OUT / f"ad{ad_n:02d}_{ad['slug']}" / "clip01.mp4"),
                        "--out-dir", str(adir), "--n", "6", "--prefix", "_anchor"], check=False)
    anchors = sorted(adir.glob("_anchor_*.jpg"))
    amgids = [upload_asset(str(a), "image/jpeg") for a in anchors] or [mgid]
    print(f"  {len(amgids)} eyes-open anchors", flush=True)
    for i, line in enumerate(clips[1:], 2):
        print(f"  clip{i:02d} -> {gen(ad_n, ad, i, line, amgids[(i - 2) % len(amgids)])}", flush=True)


if __name__ == "__main__":
    main()
