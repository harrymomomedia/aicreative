#!/usr/bin/env python3
"""Assemble 'The Insider' — stacked (nurse-survivor TOP, documentarian BOTTOM) + cut, with b-roll
over the voice on the answer/qualifier beats. Grok clips, word-aware trim, stereo-48k concat,
static-gain loudness. Mirrors scripts/depo_grok_full_assemble.py (stacked-podcast-broll skill).
Run: .venv/bin/python scripts/insider_assemble.py
"""
import re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # for face_crop
from elevenlabs_client import scribe
from face_crop import pane_crop   # face-aware chin-safe crop

G  = Path("outputs/depo_figured/clips_grok")
LIB = Path("outputs/depo_interview/admachin_lib")
CL  = Path("outputs/depo_interview/broll_clips")
FUT = Path("outputs/depo_interview/broll_future_clips")
BR  = Path("outputs/depo_interview/admachin_broll/clips")   # recovery_surv etc.
S  = Path("outputs/depo_figured/seg"); S.mkdir(parents=True, exist_ok=True)
E  = Path("outputs/depo_figured/edits"); E.mkdir(parents=True, exist_ok=True)
T  = Path("outputs/depo_figured/trim"); T.mkdir(parents=True, exist_ok=True)

# tuned after checking a stacked frame; nurse and doc both centered close-ups
SURV_CROP = "crop=560:498:85:200,scale=720:640,setsar=1,fps=30"
DOC_CROP  = "crop=560:498:85:200,scale=720:640,setsar=1,fps=30"
AAUD = "aformat=channel_layouts=stereo:sample_rates=48000"

# (talker_clip, persona, listener_clip, intended_line)
BEATS = [
 ("doc_0","doc","surv_listen_1","When you were diagnosed with a brain meningioma, did anyone ever tell you why?"),
 ("surv_1","surv","doc_listen_1","No. Not one doctor. They said sometimes these things just happen. I believed that for two years."),
 ("doc_2","doc","surv_listen_2","So how did you find out it might not be random?"),
 ("surv_3","surv","doc_listen_2","I was scrolling one night and saw a lawsuit. Women on the Depo shot for over a year were up to five times more likely to get a meningioma. My stomach dropped."),
 ("surv_4","surv","doc_listen_1","Because that was me. Same shot, for years. And nobody had ever said a word."),
 ("doc_5","doc","surv_listen_1","Most women are finding out the exact same way, on their own."),
 ("surv_6","surv","doc_listen_2","Nobody calls you. I pieced it together myself. Thousands of women are doing the same thing right now. There's a federal lawsuit."),
 ("doc_7","doc","surv_listen_2","For someone who just realized this watching you, what's the first step?"),
 ("surv_8","surv","doc_listen_1","You answer a few private questions online. Your diagnosis, how long you were on Depo. About a minute."),
 ("surv_9","surv","doc_listen_2","A lawyer reviews it for free. No court, it's confidential. And even if your diagnosis was years ago, you may still qualify."),
 ("doc_cta","doc",None,"If you or someone you love has a brain meningioma and was ever on Depo, you may qualify for significant compensation. Tap below and take the two-minute check."),
]
# lessons applied: deterministic-zoom text clips (crisp), no lingering stat (3-clip beat), real Depo injection
BEAT_BROLL = {
 0: ["scan_lightbox_lib","postop_dressing","recovery_surv"],  # diagnosed with a brain meningioma
 3: ["D1_bmj_study","D2_bmj_stat","depo_inject_arm"],         # saw a lawsuit / the study / 5.6x / the shot
 4: ["B1_shot_record","depo_vial"],                            # same shot for years / nobody warned
 6: ["D3_mdl_filing","legal_folders"],                         # thousands / federal lawsuit
 8: ["C1_paper_form"],                                         # answer a few questions online
 9: ["red_pen","lawyer_review"],                               # lawyer reviews it free
}
BROLL_INTRO = 2.0

def bclip(name):
    for d in (LIB, CL, FUT, BR):
        p = d / f"{name}.mp4"
        if p.exists(): return p
    raise FileNotFoundError(name)

def canon(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def words_of(mp4):
    mp3=f"/tmp/ins_{Path(mp4).stem}.mp3"
    subprocess.run(["ffmpeg","-y","-i",str(mp4),"-vn","-ar","44100","-ac","1",mp3],capture_output=True)
    r=scribe(mp3, biased_keywords=["meningioma","Depo"])
    ws=r.get("words") if isinstance(r,dict) else None
    return [(w["start"],w["end"],canon(w.get("text",""))) for w in (ws or []) if canon(w.get("text",""))]
def span(ws,line):
    it=[canon(x) for x in line.split() if canon(x)]; n=len(ws)
    def m(i,seq): return all(i+k<n and ws[i+k][2]==seq[k] for k in range(len(seq)))
    start=None
    for i in range(n):
        if m(i,it[:3]): start=ws[i][0]; break
    if start is None:
        for i in range(n):
            if ws[i][2]==it[0]: start=ws[i][0]; break
    end=None; tail=it[-3:]
    for j in range(n-1,-1,-1):
        if j-len(tail)+1>=0 and all(ws[j-len(tail)+1+k][2]==tail[k] for k in range(len(tail))): end=ws[j][1]; break
    if end is None:
        for j in range(n-1,-1,-1):
            if ws[j][2]==it[-1]: end=ws[j][1]; break
    return max(0.0,(start or 0.0)-0.08),(end or ws[-1][1])+0.18
def trim(name,line):
    src=G/f"{name}.mp4"; out=T/f"{name}.mp4"; ws=words_of(src); a,b=span(ws,line); d=round(b-a,2)
    subprocess.run(["ffmpeg","-y","-i",str(src),"-ss",f"{a:.2f}","-to",f"{b:.2f}","-c:v","libx264",
        "-crf","19","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","192k",str(out),"-loglevel","error"])
    print(f"  trim {name}: {a:.2f}-{b:.2f} = {d}s"); return out,d

def broll_video(names,dur,tag):
    per=dur/len(names); parts=[]
    for i,n in enumerate(names):
        p=S/f"bvid_{tag}_{i}.mp4"
        subprocess.run(["ffmpeg","-y","-ss","1.0","-i",str(bclip(n)),"-t",f"{per:.3f}",
            "-vf","scale=720:1280,setsar=1,fps=30","-an","-c:v","libx264","-crf","19","-pix_fmt","yuv420p",
            str(p),"-loglevel","error"]); parts.append(p)
    lst=Path(f"/tmp/insbv_{tag}.txt"); lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    vid=S/f"bvid_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:v","libx264","-crf","19",
        "-pix_fmt","yuv420p",str(vid),"-loglevel","error"]); return vid

def beat_broll(idx,persona,listener,tfile,dur,mode,names,intro=2.0):
    tag=f"{idx}_{mode}"; tail=max(0.5,dur-intro); iv=S/f"intro_{tag}.mp4"
    if mode=="stack":
        lf=G/f"{listener}.mp4"
        top=lf if persona=="doc" else tfile; bot=tfile if persona=="doc" else lf
        fc=f"[0:v]{SURV_CROP}[t];[1:v]{DOC_CROP}[b];[t][b]vstack[v]"
        subprocess.run(["ffmpeg","-y","-i",str(top),"-i",str(bot),"-filter_complex",fc,"-map","[v]",
            "-t",f"{intro:.2f}","-an","-c:v","libx264","-crf","19","-pix_fmt","yuv420p",str(iv),"-loglevel","error"])
    else:
        subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30","-t",f"{intro:.2f}",
            "-an","-c:v","libx264","-crf","19","-pix_fmt","yuv420p",str(iv),"-loglevel","error"])
    tv=broll_video(names,tail,tag)
    lst=Path(f"/tmp/insb_{tag}.txt"); lst.write_text(f"file '{iv.resolve()}'\nfile '{tv.resolve()}'\n")
    cv=S/f"combo_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:v","libx264","-crf","19",
        "-pix_fmt","yuv420p",str(cv),"-loglevel","error"])
    out=S/f"beat_{tag}.mp4"
    subprocess.run(["ffmpeg","-y","-i",str(cv),"-i",str(tfile),"-filter_complex",
        f"[0:v]fade=t=out:st={dur-0.25:.2f}:d=0.25[v];[1:a]{AAUD}[a]","-map","[v]","-map","[a]","-t",f"{dur}",
        "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(out),"-loglevel","error"])
    print(f"  beat {idx} b-roll ({mode}): {intro}s face + {tail:.1f}s [{','.join(names)}]"); return out

def stacked_seg(idx,persona,listener,tfile,dur):
    seg=S/f"seg_{idx:02d}.mp4"
    if listener is None:
        subprocess.run(["ffmpeg","-y","-i",str(tfile),"-vf","scale=720:1280,setsar=1,fps=30","-af",AAUD,
            "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(seg),"-loglevel","error"])
        return seg
    lf=G/f"{listener}.mp4"
    top=lf if persona=="doc" else tfile; bot=tfile if persona=="doc" else lf
    asrc="1:a" if persona=="doc" else "0:a"
    fc=f"[0:v]{SURV_CROP}[t];[1:v]{DOC_CROP}[b];[t][b]vstack[v];[{asrc}]{AAUD}[a]"
    subprocess.run(["ffmpeg","-y","-i",str(top),"-i",str(bot),"-filter_complex",fc,"-map","[v]","-map","[a]",
        "-t",f"{dur}","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(seg),"-loglevel","error"])
    return seg

def normalize(src,dst):
    info=subprocess.run(["ffmpeg","-i",str(src),"-af","loudnorm=I=-16:TP=-1.5:print_format=json","-f","null","-"],
        capture_output=True,text=True).stderr
    ii=[l for l in info.splitlines() if '"input_i"' in l]
    gain=-16.0-float(ii[0].split(':')[1].strip().strip(',').strip('"')) if ii else 0.0
    subprocess.run(["ffmpeg","-y","-i",str(src),"-af",f"volume={gain:.2f}dB,alimiter=limit=0.89:asc=1",
        "-c:v","copy","-c:a","aac","-b:a","192k",str(dst),"-loglevel","error"])
    print(f"  normalized {dst.name} gain {gain:.2f}dB")
def web(src,dst):
    subprocess.run(["ffmpeg","-y","-i",str(src),"-c:v","libx264","-crf","28","-preset","veryfast",
        "-pix_fmt","yuv420p","-vf","scale=540:960","-c:a","aac","-b:a","128k",str(dst),"-loglevel","error"])
def dur_of(p): return subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(p)],capture_output=True,text=True).stdout.strip()

def main():
    global SURV_CROP, DOC_CROP
    # face-aware chin-safe crops computed from the actual clips (matched face size, chin + margin)
    SURV_CROP = pane_crop(G/"surv_1.mp4"); DOC_CROP = pane_crop(G/"doc_0.mp4")
    print(f"  SURV_CROP={SURV_CROP}\n  DOC_CROP={DOC_CROP}")
    trims={b[0]:trim(b[0],b[3]) for b in BEATS}
    segs=[]
    for idx,(talk,persona,listener,line) in enumerate(BEATS):
        tf,d=trims[talk]
        segs.append(beat_broll(idx,persona,listener,tf,d,"stack",BEAT_BROLL[idx],BROLL_INTRO) if idx in BEAT_BROLL
                    else stacked_seg(idx,persona,listener,tf,d))
        print(f"  seg {idx:02d} {talk}")
    lst=Path("/tmp/ins_stack.txt"); lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
    st=E/"figured_stacked.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:v","libx264","-crf","19",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",str(st),"-loglevel","error"])
    normalize(st,E/"figured_stacked_norm.mp4"); web(E/"figured_stacked_norm.mp4",E/"figured_stacked_web.mp4")
    csegs=[]
    for idx,(talk,persona,listener,line) in enumerate(BEATS):
        tf,d=trims[talk]
        if idx in BEAT_BROLL: csegs.append(beat_broll(idx,persona,listener,tf,d,"cut",BEAT_BROLL[idx],BROLL_INTRO)); continue
        cf=S/f"cut_{idx:02d}.mp4"
        subprocess.run(["ffmpeg","-y","-i",str(tf),"-vf","scale=720:1280,setsar=1,fps=30","-af",AAUD,
            "-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(cf),"-loglevel","error"])
        csegs.append(cf)
    lst2=Path("/tmp/ins_cut.txt"); lst2.write_text("".join(f"file '{s.resolve()}'\n" for s in csegs))
    cut=E/"figured_cut.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst2),"-c:v","libx264","-crf","19",
        "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",str(cut),"-loglevel","error"])
    normalize(cut,E/"figured_cut_norm.mp4"); web(E/"figured_cut_norm.mp4",E/"figured_cut_web.mp4")
    for f in ["figured_stacked_norm.mp4","figured_cut_norm.mp4"]:
        import re as _re
        mv=subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",str(E/f),"-af","volumedetect","-f","null","-"],capture_output=True,text=True).stderr
        m=_re.search(r"mean_volume: ([-0-9.]+) dB",mv)
        print(f"{f}: {dur_of(E/f)}s mean_volume {m.group(1) if m else '?'} dB")

if __name__ == "__main__":
    main()
