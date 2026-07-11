#!/usr/bin/env python3
"""Hybrid stacked: split two-shot only when the DOC asks (survivor silently listens, which works);
FULL-FRAME survivor for her answers; full-frame doc for CTA. Avoids the unsolvable silent-doc pane.
"""
import subprocess
from pathlib import Path
T=Path("outputs/depo_interview/trimmed"); L=Path("outputs/depo_interview/listen_loops"); E=Path("outputs/depo_interview/edits")
SURV_LOOP=L/"surv_listen_loop.mp4"
BEATS=[("doc_talk_1","doc"),("surv_talk_1","surv"),("doc_talk_2","doc"),("surv_talk_2","surv"),
 ("surv_talk_3","surv"),("doc_talk_3","doc"),("surv_talk_4","surv"),("doc_talk_4","doc"),
 ("surv_talk_5","surv"),("surv_talk_6","surv"),("doc_cta","cta")]
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(p)],capture_output=True,text=True).stdout.strip())
segs=[]
for i,(talker,kind) in enumerate(BEATS):
    tf=T/f"{talker}.mp4"; d=dur(tf); seg=T/f"hy_{i:02d}.mp4"
    if kind=="doc":  # split: doc top talks, survivor bottom listens (silent loop)
        cmd=["ffmpeg","-y","-i",str(tf),"-stream_loop","-1","-i",str(SURV_LOOP),"-filter_complex",
             "[0:v]crop=720:640:0:110,setsar=1,fps=30[t];[1:v]crop=720:640:0:110,setsar=1,fps=30[b];[t][b]vstack[v]",
             "-map","[v]","-map","0:a","-t",f"{d:.2f}","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(seg),"-loglevel","error"]
    else:  # full-frame (survivor answer OR cta)
        cmd=["ffmpeg","-y","-i",str(tf),"-vf","scale=720:1280,setsar=1,fps=30,delogo=x=646:y=1222:w=72:h=48","-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(seg),"-loglevel","error"]
    subprocess.run(cmd); segs.append(seg); print(f"seg {i:02d} {talker} {kind} {d:.2f}s")
lst=Path("/tmp/hy.txt"); lst.write_text("".join(f"file '{s.resolve()}'\n" for s in segs))
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:v","libx264","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",str(E/"stacked_hybrid.mp4"),"-loglevel","error"])
info=subprocess.run(["ffmpeg","-i",str(E/"stacked_hybrid.mp4"),"-af","loudnorm=I=-16:TP=-1.5:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
ii=[l for l in info.splitlines() if '"input_i"' in l]; gain=-16.0-float(ii[0].split(':')[1].strip().strip(',').strip('"')) if ii else 0.0
subprocess.run(["ffmpeg","-y","-i",str(E/"stacked_hybrid.mp4"),"-af",f"volume={gain:.2f}dB,alimiter=limit=0.89:asc=1","-c:v","copy","-c:a","aac","-b:a","192k",str(E/"stacked_hybrid_norm.mp4"),"-loglevel","error"])
subprocess.run(["ffmpeg","-y","-i",str(E/"stacked_hybrid_norm.mp4"),"-c:v","libx264","-crf","27","-preset","veryfast","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k",str(E/"stacked_hybrid_web.mp4"),"-loglevel","error"])
print("hybrid:", dur(E/"stacked_hybrid_norm.mp4"),"s")
