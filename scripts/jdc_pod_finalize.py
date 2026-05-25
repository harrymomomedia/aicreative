"""Finalize one podcast monologue video.

Pipeline:
  WORD-AWARE trim each clip (cut leading/trailing Veo improv at the intended first/last word —
    silence-trim can't catch trailing *speech* like "they got the worst system")
  -> host-clone voice_changer (english_sts_v2, 192k, sim 0.70)
  -> mux raw -> concat -> STATIC-gain audio to -16 LUFS + limiter (no pumping)
  -> hormozi3 captions, 9:16 + 4:5.

Usage: .venv/bin/python scripts/jdc_pod_finalize.py --slug jdc_pod_agepower_h07 --voice-id <id>
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat, voice_changer

LEAD, TAIL = 0.12, 0.08   # tight TAIL so trailing "mm-hmm/yeah" fillers get cut at the intended last word

# intended spoken line per clip (for word-aware trim)
DIALOGUES = {
    "jdc_pod_agepower_h07": [
        "You was twelve thirteen years old He was a grown man with a badge and the keys to your cell",
        "Whatever happened in there That's on him not you Period",
        "You was just a kid None of that was on you None of it",
        "If you was sexually abused in Illinois juvie you may qualify for significant compensation",
        "Free two minutes Quit blamin that little kid you was Go check",
    ],
    "jdc_pod_cookstat_h08": [
        "One building The Cook County juvenile center in Chicago A third of all these abuse cases came outta that one spot",
        "These was kids Locked up supposed to be protected",
        "The staff sexually abused us instead If that's where they had you listen close",
        "Almost a thousand men already filed You may qualify for significant compensation Free two minutes Go see if you qualify",
    ],
    "jdc_pod_theydont_h09": [
        "Real quick they don't want you knowing this You was a kid in juvie somebody on staff sexually abused you",
        "You think you gotta stand up say it in front of everybody Nah You don't",
        "It's confidential No name No face I filed mine quiet",
        "Illinois is payin for this right now and you may qualify for significant compensation",
        "Free Two minutes They been bankin on your silence Not no more Tap in",
    ],
    "jdc_pod_moneyreveal_h06": [
        "Illinois is paying out for this I'm dead serious A guard or staff sexually abused you as a kid in juvie",
        "You may qualify for significant compensation Could be life changing",
        "I already filed mine You check it private free two minutes",
        "That was you in there Don't sleep Go look right now",
    ],
    "jdc_pod_barbershop_h08": [
        "Yo last week barbershop dude brings up the juvie lawsuits I got real quiet Cause that was me",
        "He sexually abused me in there I buried it for years",
        "Went home checked it Two minutes Nobody knew Filed it",
        "Now they sayin I may qualify for significant compensation Nobody was in my business",
        "You don't gotta say it out loud Nowhere Just you Go look",
    ],
    "jdc_pod_familymoney_h06": [
        "This the kind of money that change your whole family situation For real",
        "If you was sexually abused in Illinois juvie you may qualify for significant compensation",
        "That's a different life for you and yours I filed mine quiet",
        "Check it free private two minutes You owe it to your people Go look",
    ],
    "jdc_pod_thousand_h01": [
        "Almost a thousand of us For real We was locked up in Illinois juvie",
        "The staff sexually abused us Every one of us",
        "Illinois is payin for what was done to us and you may qualify for significant compensation",
        "Free to check two minutes private That was you in there Add your name Go look",
    ],
    "jdc_pod_scalemoney_h05": [
        "This ain't a couple hundred dollars Nah Not for this",
        "A staff member sexually abused you in Illinois juvie",
        "You may qualify for significant compensation The kind of money that change things",
        "I filed mine already Find out private free two minutes Why you still scrollin Go check",
    ],
    # --- winning-structure announcer videos (direct-to-camera) ---
    "jdc_pod_winnerA_h11": [
        "Listen up Illinois This might be your shot at justice For real",
        "You went through sexual abuse while locked up in Cook County St Charles Warrenville or Kane County",
        "You may qualify for significant compensation No cap You don't need paperwork proof or an old report",
        "They reviewing cases right now Most get handled without you ever stepping in court",
        "Everything stays low-key and confidential Takes less than a minute to check Don't sleep on this",
    ],
    "jdc_pod_winnerB_h15": [
        "Yo Illinois Listen up This could be your shot at justice",
        "A staff member sexually abused you while you was locked up in St Charles Harrisburg or Cook County",
        "You may qualify for significant compensation Straight up You don't need paperwork no proof no old report",
        "They reviewing cases right now Most get handled without you ever seeing a courtroom",
        "It all stays private and confidential Less than a minute to see if you qualify Don't sleep on this one",
    ],
    "jdc_pod_winnerC_h14": [
        "Yo Illinois listen This might be your shot at some real justice",
        "You went through sexual abuse locked up in Kane County Warrenville or Cook County",
        "You may qualify for significant compensation No cap Don't even worry about paperwork proof or an old report",
        "They already reviewing cases right now Most get handled without you ever stepping in court",
        "Everything stays low-key confidential Takes under a minute to check Don't sleep on it",
    ],
}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR {' '.join(cmd[:3])}… {r.stderr[-200:]}", flush=True)
    return r


def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def word_window(video, intended):
    """Return (start, end) trimming to the intended FIRST and LAST word (drops lead/trail improv)."""
    r = scribe_whisper_compat(str(video), language_code="en")
    words = [w for s in r["segments"] for w in s.get("words", [])]
    if not words:
        return None, None
    nwords = [norm(w["word"]) for w in words]
    intended_n = [norm(x) for x in intended.split() if norm(x)]
    first_t, last_t = words[0]["start"], words[-1]["end"]
    # trim-IN: first occurrence of the intended first word
    fw = intended_n[0]
    for i, nw in enumerate(nwords):
        if nw == fw:
            first_t = words[i]["start"]; break
    # trim-OUT: last occurrence of the intended LAST word that is preceded (within 2 words) by the
    # second-to-last intended word — a bigram, so trailing improv reusing a common word is ignored
    # (e.g. intended "...of it" beats a trailing "It was-"). Fallbacks degrade gracefully.
    lw = intended_n[-1]
    lw2 = intended_n[-2] if len(intended_n) >= 2 else None
    cand = bigram = None
    for i, nw in enumerate(nwords):
        if nw == lw:
            cand = i
            if lw2 and i >= 1 and nwords[i - 1] == lw2:   # immediate predecessor only
                bigram = i
    chosen = bigram if bigram is not None else cand
    if chosen is not None:
        last_t = words[chosen]["end"]
    return first_t, last_t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--voice-id", required=True)
    args = ap.parse_args()
    OUT = Path("outputs") / args.slug
    VC = OUT / "vc"; VC.mkdir(parents=True, exist_ok=True)
    TRIM = OUT / "trimmed"; TRIM.mkdir(parents=True, exist_ok=True)
    dialogues = DIALOGUES[args.slug]
    n = len(dialogues)
    clips = [f"clip{i}" for i in range(1, n + 1)]

    # 1. WORD-AWARE trim
    print("=== WORD-AWARE TRIM + QA ===", flush=True)
    for i, c in enumerate(clips):
        src = OUT / f"{c}.mp4"
        s, e = word_window(src, dialogues[i])
        s = max(0.0, s - LEAD); e = min(get_dur(src), e + TAIL)
        dst = TRIM / f"{c}.mp4"
        run(["ffmpeg", "-y", "-i", str(src), "-ss", f"{s:.3f}", "-to", f"{e:.3f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "19",
             "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(dst)])
        print(f"  [{c}] [{s:.2f}-{e:.2f}] -> {get_dur(dst):.2f}s", flush=True)
        og = VC / f"{c}_orig.mp3"
        run(["ffmpeg", "-y", "-i", str(dst), "-vn", "-ar", "44100", "-ac", "1", str(og)])

    # 2. voice_changer (host clone)
    print("=== VOICE CHANGER (host clone) ===", flush=True)
    for c in clips:
        out = VC / f"{c}_vc.mp3"
        if out.exists() and out.stat().st_size > 5000:
            continue
        voice_changer(str(VC / f"{c}_orig.mp3"), args.voice_id, str(out),
                      model_id="eleven_english_sts_v2", stability=0.5, similarity_boost=0.70,
                      output_format="mp3_44100_192")

    # 3. mux raw + concat
    muxed = []
    for c in clips:
        out = VC / f"{c}_mux.mp4"
        run(["ffmpeg", "-y", "-i", str(TRIM / f"{c}.mp4"), "-i", str(VC / f"{c}_vc.mp3"),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        muxed.append(out)
    cl = VC / "concat.txt"; cl.write_text("".join(f"file '{p.absolute()}'\n" for p in muxed))
    concat_raw = VC / "concat_raw.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(concat_raw)])

    # 4. STATIC gain to -16 LUFS + true-peak limiter with auto-level DISABLED (level=disabled is the
    #    key — by default alimiter re-normalizes back to 0 dBFS, which was the clipping/red bug).
    #    Hard ceiling at -3 dBFS (0.71). Static gain = no pumping; level=disabled = real ceiling.
    mr = subprocess.run(["ffmpeg", "-i", str(concat_raw),
                         "-af", "loudnorm=I=-16:TP=-3.0:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    inp_i = float(json.loads(mr[mr.rfind("{"):mr.rfind("}") + 1])["input_i"])
    g = -16.0 - inp_i
    final = OUT / "final.mp4"
    run(["ffmpeg", "-y", "-i", str(concat_raw),
         "-af", f"volume={g:.2f}dB,alimiter=limit=0.71:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    print(f"DONE -> {final} ({get_dur(final):.2f}s) gain {g:+.2f}dB (limit -3dBFS, no auto-level)", flush=True)

    # 5. captions 9:16 + 4:5
    f45 = OUT / "final_4x5.mp4"
    run([".venv/bin/python", "scripts/crop_4x5.py", str(final), "--out", str(f45)])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final), "--out", str(OUT / "final_hormozi3.mp4")])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(f45), "--out", str(OUT / "final_4x5_hormozi3.mp4"), "--vertical-pos", "0.80"])
    print(f"DONE -> {OUT}/final_hormozi3.mp4 + 4x5", flush=True)


if __name__ == "__main__":
    main()
