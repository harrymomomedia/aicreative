#!/usr/bin/env python3
"""Full Depo interview on GROK — stacked (survivor TOP, doc BOTTOM) + cut (shot-reverse) —
with the AdMachin recovery/surgery/scan b-roll bridge inserted after beat 1 (the "brain
meningioma" line), then back to stacked. Word-aware trim removes Grok leading/trailing improv.

Run: .venv/bin/python scripts/depo_grok_full_assemble.py
"""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from elevenlabs_client import scribe
from face_crop import pane_crop

G = Path("outputs/depo_interview/clips_grok")
BR = Path("outputs/depo_interview/admachin_broll/clips")
T = Path("outputs/depo_interview/grok_trim"); T.mkdir(parents=True, exist_ok=True)
S = Path("outputs/depo_interview/grok_seg"); S.mkdir(parents=True, exist_ok=True)
E = Path("outputs/depo_interview/edits"); E.mkdir(parents=True, exist_ok=True)

SURV_CROP = "crop=520:462:80:260,scale=720:640,setsar=1,fps=30"   # survivor tight centered (TOP)
DOC_CROP  = "crop=560:498:90:190,scale=720:640,setsar=1,fps=30"   # doc matched close-up (BOTTOM)

# beat: (talker_clip, persona, listener_clip, intended_line)
BEATS = [
 ("gtalk_doc_1","doc","surv_listen_grok_1","When they told you it was a brain meningioma, did anyone ever explain why you got it?"),
 ("gtalk_surv_1","surv","doc_listen_grok_1","No. Bad luck, they kept saying. Over and over. And for a long time, I believed that."),
 ("gtalk_doc_2","doc","surv_listen_grok_2","So what changed your mind about it just being bad luck?"),
 ("gtalk_surv_2","surv","doc_listen_grok_2","A lawyer showed me the studies. Women on the Depo shot for over a year were up to five times more likely to get one."),
 ("gtalk_surv_3","surv","doc_listen_grok_1","Five times. That is not bad luck. And nobody ever warned me."),
 ("gtalk_doc_3","doc","surv_listen_grok_1","And you are not alone in this. So many other women are finding out the very same thing."),
 ("gtalk_surv_4","surv","doc_listen_grok_2","Not even close. Thousands of women. Same diagnosis, same shot. There is a federal lawsuit now."),
 ("gtalk_doc_4","doc","surv_listen_grok_2","So what can someone actually do about it? Where would a person even start?"),
 ("gtalk_surv_5","surv","doc_listen_grok_1","You answer a few private questions online. Your diagnosis, how long you were on Depo. It takes about a minute."),
 ("gtalk_surv_6","surv","doc_listen_grok_2","A lawyer reviews it for free. No court, it is confidential, and even if it was years ago, you may still qualify."),
 ("gtalk_doc_cta","doc",None,"If you or someone you love has a brain meningioma and was ever on Depo, you may qualify for significant compensation. Tap below and take the two-minute check."),
]

# Per-beat b-roll: each listed beat shows ~BROLL_INTRO s of the speaker, then cuts to its b-roll
# clips while that beat's audio (their line) plays underneath, then the next beat returns to faces.
CL = Path("outputs/depo_interview/broll_clips")     # my generated answer-beat clips
LIB = Path("outputs/depo_interview/admachin_lib")   # EXISTING AdMachin B-Roll library clips
def bclip(name):
    for d in (LIB, BR, CL):   # prefer the existing library
        p = d / f"{name}.mp4"
        if p.exists(): return p
    raise FileNotFoundError(f"b-roll clip {name}")

# Uses the EXISTING AdMachin B-Roll library (real Depo branding, matching persona, real post-op
# recovery), plus a few of my generated clips where the library has no match. No empty phone form.
BEAT_BROLL = {
 0: ["scan_lightbox_lib", "postop_dressing", "recovery_surv"],  # diagnosis -> post-op -> her recovering
 3: ["medical_records", "depo_syringe"],       # "showed me the studies... the Depo shot" (real vial)
 4: ["depo_inject_arm"],                        # "nobody ever warned me" (real Depo box)
 5: ["women_group"],                            # "you are not alone... other women" (no library match)
 6: ["legal_folders", "legal_sign"],           # "there is a federal lawsuit now"
 9: ["red_pen", "lawyer_review"],              # "a lawyer reviews it for free, confidential"
}                                               # beat 8 ("questions online") stays on her face — no form clip
BROLL_INTRO = 2.0      # seconds of the speaker shown before the b-roll cuts in

def canon(w): return re.sub(r"[^a-z0-9]", "", w.lower())

def words_of(mp4):
    mp3 = f"/tmp/gf_{Path(mp4).stem}.mp3"
    subprocess.run(["ffmpeg","-y","-i",str(mp4),"-vn","-ar","44100","-ac","1",mp3],capture_output=True)
    r = scribe(mp3, biased_keywords=["meningioma","Depo"])
    ws = r.get("words") if isinstance(r, dict) else None
    out = []
    for w in (ws or []):
        c = canon(w.get("text",""))
        if c: out.append((w["start"], w["end"], c))
    return out

def span(ws, line):
    intended = [canon(x) for x in line.split() if canon(x)]
    n = len(ws)
    def match_at(i, seq): return all(i+k < n and ws[i+k][2] == seq[k] for k in range(len(seq)))
    start = None
    for i in range(n):
        if match_at(i, intended[:3]): start = ws[i][0]; break
    if start is None:
        for i in range(n):
            if ws[i][2] == intended[0]: start = ws[i][0]; break
    end = None; tail = intended[-3:]
    for j in range(n-1, -1, -1):
        if j-len(tail)+1 >= 0 and all(ws[j-len(tail)+1+k][2] == tail[k] for k in range(len(tail))):
            end = ws[j][1]; break
    if end is None:
        for j in range(n-1, -1, -1):
            if ws[j][2] == intended[-1]: end = ws[j][1]; break
    return max(0.0, (start or 0.0) - 0.10), (end or ws[-1][1]) + 0.22

def trim(name, line):
    src = G / f"{name}.mp4"; out = T / f"{name}.mp4"
    a, b = span(words_of(src), line)
    dur = round(b - a, 2)
    subprocess.run(["ffmpeg","-y","-i",str(src),"-ss",f"{a:.2f}","-to",f"{b:.2f}",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k",
        str(out),"-loglevel","error"])
    print(f"  trim {name}: {a:.2f}-{b:.2f} = {dur}s")
    return out, dur

AAUD = "aformat=channel_layouts=stereo:sample_rates=48000"  # force stereo 48k everywhere

def broll_video(names, dur, tag):
    """Silent b-roll montage of the given clip `names`, full-frame 720x1280, total length `dur`."""
    per = dur / len(names)
    parts = []
    for i, name in enumerate(names):
        p = S / f"bvid_{tag}_{i}.mp4"
        subprocess.run(["ffmpeg","-y","-ss","1.0","-i",str(bclip(name)),"-t",f"{per:.3f}",
            "-vf","scale=720:1280,setsar=1,fps=30","-an",
            "-c:v","libx264","-crf","19","-pix_fmt","yuv420p",str(p),"-loglevel","error"])
        parts.append(p)
    lst = Path(f"/tmp/gf_bvid_{tag}.txt"); lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    vid = S / f"bvid_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p",str(vid),"-loglevel","error"])
    return vid

def beat_with_broll_tail(idx, talker, persona, listener, tfile, dur, mode, names, intro=2.0):
    """Beat that shows the speaker for `intro` seconds, then cuts to the b-roll montage (`names`)
    for the remainder, with the beat's own AUDIO (their line) playing UNDER the whole thing.
    mode: 'stack' (vstack panes) or 'cut' (full-frame talker) for the intro portion."""
    tag = f"{idx}_{mode}"
    tail = max(0.5, dur - intro)
    intro_v = S / f"b0intro_{tag}.mp4"
    if mode == "stack":
        lfile = G / f"{listener}.mp4"
        # survivor is ALWAYS the top pane (SURV_CROP); doc is ALWAYS bottom (DOC_CROP)
        top = lfile if persona == "doc" else tfile   # surv clip on top
        bot = tfile if persona == "doc" else lfile   # doc clip on bottom
        fc = f"[0:v]{SURV_CROP}[t];[1:v]{DOC_CROP}[b];[t][b]vstack[v]"
        subprocess.run(["ffmpeg","-y","-i",str(top),"-i",str(bot),"-filter_complex",fc,
            "-map","[v]","-t",f"{intro:.2f}","-an","-c:v","libx264","-crf","19","-pix_fmt","yuv420p",
            str(intro_v),"-loglevel","error"])
    else:
        subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30",
            "-t",f"{intro:.2f}","-an","-c:v","libx264","-crf","19","-pix_fmt","yuv420p",
            str(intro_v),"-loglevel","error"])
    tail_v = broll_video(names, tail, tag)
    # concat intro + b-roll tail into one silent video, then mux the beat's full audio over it
    lst = Path(f"/tmp/gf_{tag}.txt")
    lst.write_text(f"file '{intro_v.resolve()}'\nfile '{tail_v.resolve()}'\n")
    combo_v = S / f"b0combo_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p",str(combo_v),"-loglevel","error"])
    out = S / f"bbeat_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-i",str(combo_v),"-i",str(tfile),
        "-filter_complex",f"[0:v]fade=t=out:st={dur-0.25:.2f}:d=0.25[v];[1:a]{AAUD}[a]",
        "-map","[v]","-map","[a]","-t",f"{dur}",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        str(out),"-loglevel","error"])
    print(f"  beat {idx} b-roll tail ({mode}): {intro:.1f}s face + {tail:.1f}s b-roll [{','.join(names)}]")
    return out

def stacked_seg(idx, talker, persona, listener, tfile, dur):
    seg = S / f"seg_{idx:02d}.mp4"
    if listener is None:  # CTA full-frame
        subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30",
            "-af",AAUD,"-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
            str(seg),"-loglevel","error"])
        return seg
    lfile = G / f"{listener}.mp4"
    if persona == "doc":   # doc talks(bottom), surv listens(top); audio=doc=input1
        top, tcrop, bot, bcrop, aud = lfile, SURV_CROP, tfile, DOC_CROP, "[a1]"
    else:                  # surv talks(top), doc listens(bottom); audio=surv=input0
        top, tcrop, bot, bcrop, aud = tfile, SURV_CROP, lfile, DOC_CROP, "[a0]"
    asrc = "0:a" if aud == "[a0]" else "1:a"
    fc = f"[0:v]{tcrop}[t];[1:v]{bcrop}[b];[t][b]vstack[v];[{asrc}]{AAUD}[aud]"
    subprocess.run(["ffmpeg","-y","-i",str(top),"-i",str(bot),"-filter_complex",fc,
        "-map","[v]","-map","[aud]","-t",f"{dur}",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        str(seg),"-loglevel","error"])
    return seg

def normalize(src, dst):
    info = subprocess.run(["ffmpeg","-i",str(src),"-af","loudnorm=I=-16:TP=-1.5:print_format=json",
        "-f","null","-"],capture_output=True,text=True).stderr
    ii = [l for l in info.splitlines() if '"input_i"' in l]
    gain = -16.0 - float(ii[0].split(':')[1].strip().strip(',').strip('"')) if ii else 0.0
    subprocess.run(["ffmpeg","-y","-i",str(src),"-af",f"volume={gain:.2f}dB,alimiter=limit=0.89:asc=1",
        "-c:v","copy","-c:a","aac","-b:a","192k",str(dst),"-loglevel","error"])
    print(f"  normalized {dst.name} gain {gain:.2f}dB")

def web(src, dst):
    subprocess.run(["ffmpeg","-y","-i",str(src),"-c:v","libx264","-crf","28","-preset","veryfast",
        "-pix_fmt","yuv420p","-vf","scale=540:960","-c:a","aac","-b:a","128k",str(dst),"-loglevel","error"])

def dur_of(p):
    return subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of",
        "default=nk=1:nw=1",str(p)],capture_output=True,text=True).stdout.strip()

def main():
    global SURV_CROP, DOC_CROP
    SURV_CROP = pane_crop(G/'gtalk_surv_1.mp4'); DOC_CROP = pane_crop(G/'gtalk_doc_1.mp4')
    print(f'  SURV_CROP={SURV_CROP}\n  DOC_CROP={DOC_CROP}')
    trims = {b[0]: trim(b[0], b[3]) for b in BEATS}

    # ---- STACKED; beat BROLL_OVER_BEAT shows b-roll over the survivor's VO ----
    segs = []
    for idx,(talker,persona,listener,line) in enumerate(BEATS):
        tfile,d = trims[talker]
        if idx in BEAT_BROLL:
            segs.append(beat_with_broll_tail(idx,talker,persona,listener,tfile,d,"stack",BEAT_BROLL[idx],BROLL_INTRO))
        else:
            segs.append(stacked_seg(idx,talker,persona,listener,tfile,d))
        print(f"  seg {idx:02d} {talker} built")
    lst = Path("/tmp/gf_stack.txt"); lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
    stacked = E/"grok_full_stacked.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        str(stacked),"-loglevel","error"])
    normalize(stacked, E/"grok_full_stacked_norm.mp4"); web(E/"grok_full_stacked_norm.mp4", E/"grok_full_stacked_web.mp4")

    # ---- CUT (shot-reverse full-frame); same b-roll-over-VO on the survivor's answer ----
    csegs = []
    for idx,(talker,persona,listener,line) in enumerate(BEATS):
        tfile,d = trims[talker]
        if idx in BEAT_BROLL:
            csegs.append(beat_with_broll_tail(idx,talker,persona,listener,tfile,d,"cut",BEAT_BROLL[idx],BROLL_INTRO))
            continue
        cf = S/f"cut_{idx:02d}.mp4"
        subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30",
            "-af",AAUD,"-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
            str(cf),"-loglevel","error"])
        csegs.append(cf)
    lst2 = Path("/tmp/gf_cut.txt"); lst2.write_text("".join(f"file '{s.resolve()}'\n" for s in csegs))
    cut = E/"grok_full_cut.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst2),
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
        str(cut),"-loglevel","error"])
    normalize(cut, E/"grok_full_cut_norm.mp4"); web(E/"grok_full_cut_norm.mp4", E/"grok_full_cut_web.mp4")

    for f in ["grok_full_stacked_norm.mp4","grok_full_cut_norm.mp4"]:
        d = dur_of(E/f)
        mv = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(E/f),"-af","volumedetect","-f","null","-"],
            capture_output=True,text=True).stderr
        import re as _re
        m = _re.search(r"mean_volume: ([-0-9.]+) dB", mv)
        print(f"{f}: {d}s  mean_volume {m.group(1) if m else '?'} dB")

if __name__ == "__main__":
    main()
