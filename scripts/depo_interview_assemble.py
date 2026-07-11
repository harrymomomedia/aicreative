#!/usr/bin/env python3
"""Assemble the full Depo interview ad — both STACKED (both panes, doc top / survivor bottom)
and CUT (shot-reverse full-frame) — from the useapi clips. Per-clip word-aware trim removes
leading/trailing Veo improv (keeps natural mid mm-hmm reactions). CTA is full-frame in both.

Run: .venv/bin/python scripts/depo_interview_assemble.py
"""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe

C = Path("outputs/depo_interview/clips_useapi")
T = Path("outputs/depo_interview/trimmed"); T.mkdir(parents=True, exist_ok=True)
E = Path("outputs/depo_interview/edits"); E.mkdir(parents=True, exist_ok=True)

# (talker, persona, listener, intended_line)
BEATS = [
 ("doc_talk_1","doc","surv_listen_for_doc_talk_1","When they told you it was a brain meningioma, did anyone ever explain why you got it?"),
 ("surv_talk_1","surv","doc_listen_for_surv_talk_1","No. Bad luck, they kept saying. Over and over. And for a long time, I believed that."),
 ("doc_talk_2","doc","surv_listen_for_doc_talk_2","So what changed your mind about it just being bad luck?"),
 ("surv_talk_2","surv","doc_listen_for_surv_talk_2","A lawyer showed me the studies. Women on the Depo shot for over a year were up to five times more likely to get one."),
 ("surv_talk_3","surv","doc_listen_for_surv_talk_3","Five times. That is not bad luck. And nobody ever warned me."),
 ("doc_talk_3","doc","surv_listen_for_doc_talk_3","And you are not alone in this. So many other women are finding out the very same thing."),
 ("surv_talk_4","surv","doc_listen_for_surv_talk_4","Not even close. Thousands of women. Same diagnosis, same shot. There is a federal lawsuit now."),
 ("doc_talk_4","doc","surv_listen_for_doc_talk_4","So what can someone actually do about it? Where would a person even start?"),
 ("surv_talk_5","surv","doc_listen_for_surv_talk_5","You answer a few private questions online. Your diagnosis, how long you were on Depo. It takes about a minute."),
 ("surv_talk_6","surv","doc_listen_for_surv_talk_6","A lawyer reviews it for free. No court. It is confidential. And even if it was years ago, you may still qualify."),
 ("doc_cta","doc",None,"If you or someone you love has a brain meningioma and was ever on Depo, you may qualify for significant compensation. Tap below and take the two-minute check."),
]

def canon(w): return re.sub(r"[^a-z0-9]", "", w.lower())

def words_of(mp4):
    mp3 = f"/tmp/asm_{Path(mp4).stem}.mp3"
    subprocess.run(["ffmpeg","-y","-i",str(mp4),"-vn","-ar","44100","-ac","1",mp3],capture_output=True)
    r = scribe(mp3, biased_keywords=["meningioma","Depo"])
    ws = r.get("words") if isinstance(r, dict) else None
    out = []
    for w in (ws or []):
        c = canon(w.get("text",""))
        if c:
            out.append((w["start"], w["end"], c))
    return out

def span(ws, line):
    intended = [canon(x) for x in line.split() if canon(x)]
    n = len(ws)
    # start: first i where ws[i..i+2] matches intended[0..2]
    def match_at(i, seq):
        return all(i+k < n and ws[i+k][2] == seq[k] for k in range(len(seq)))
    start = None
    for i in range(n):
        if match_at(i, intended[:3]): start = ws[i][0]; break
    if start is None:  # fallback: first occurrence of intended[0]
        for i in range(n):
            if ws[i][2] == intended[0]: start = ws[i][0]; break
    end = None
    tail = intended[-3:]
    for j in range(n-1, -1, -1):
        if j-len(tail)+1 >= 0 and all(ws[j-len(tail)+1+k][2] == tail[k] for k in range(len(tail))):
            end = ws[j][1]; break
    if end is None:
        for j in range(n-1, -1, -1):
            if ws[j][2] == intended[-1]: end = ws[j][1]; break
    return max(0.0, (start or 0.0) - 0.08), (end or ws[-1][1]) + 0.18

def trim_talker(name, line):
    src = C / f"{name}.mp4"; out = T / f"{name}.mp4"
    ws = words_of(src)
    a, b = span(ws, line)
    dur = round(b - a, 2)
    subprocess.run(["ffmpeg","-y","-i",str(src),"-ss",f"{a:.2f}","-to",f"{b:.2f}",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        str(out),"-loglevel","error"])
    print(f"  trimmed {name}: {a:.2f}-{b:.2f} = {dur}s")
    return out, dur

def main():
    trims = {}
    for talker, persona, listener, line in BEATS:
        trims[talker] = trim_talker(talker, line)

    # ---- CUT edit: concat trimmed talkers full-frame ----
    ins, fc, k = [], "", 0
    for talker, *_ in BEATS:
        ins += ["-i", str(trims[talker][0])]
        fc += f"[{k}:v]scale=720:1280,setsar=1,fps=30[v{k}];"
        k += 1
    labs = "".join(f"[v{i}][{i}:a]" for i in range(k))
    fc += f"{labs}concat=n={k}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg","-y",*ins,"-filter_complex",fc,"-map","[v]","-map","[a]",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        str(E/"cut_full.mp4"),"-loglevel","error"])
    print("[done] cut_full.mp4")

    # ---- STACKED edit: per beat, doc TOP + survivor BOTTOM; CTA full-frame ----
    seg_files = []
    for idx,(talker, persona, listener, line) in enumerate(BEATS):
        seg = T / f"seg_{idx:02d}.mp4"
        tfile, dur = trims[talker]
        if listener is None:  # CTA full-frame
            subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30",
                "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
                str(seg),"-loglevel","error"])
        else:
            lfile = C / f"{listener}.mp4"
            if persona == "doc":   # doc talks (top), survivor listens (bottom)
                top, bot, aud = tfile, lfile, "0:a"
            else:                  # survivor talks (bottom), doc listens (top)
                top, bot, aud = lfile, tfile, ("1:a" if persona=="surv" else "0:a")
            # inputs order: 0=top, 1=bottom ; audio from the talker
            audmap = "1:a" if persona == "surv" else "0:a"
            fc = ("[0:v]crop=720:640:0:110,setsar=1,fps=30[t];"
                  "[1:v]crop=720:640:0:110,setsar=1,fps=30[b];[t][b]vstack[v]")
            subprocess.run(["ffmpeg","-y","-i",str(top),"-i",str(bot),"-filter_complex",fc,
                "-map","[v]","-map",audmap,"-t",f"{dur}",
                "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
                str(seg),"-loglevel","error"])
        seg_files.append(seg)
        print(f"  seg {idx:02d} ({talker}) built")

    lst = Path("/tmp/asm_stack.txt")
    lst.write_text("".join(f"file '{s.resolve()}'\n" for s in seg_files))
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
        str(E/"stacked_full.mp4"),"-loglevel","error"])
    print("[done] stacked_full.mp4")

    for f in ["cut_full.mp4","stacked_full.mp4"]:
        d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
            "-of","default=nk=1:nw=1",str(E/f)],capture_output=True,text=True).stdout.strip()
        print(f"{f}: {d}s")

if __name__ == "__main__":
    main()
