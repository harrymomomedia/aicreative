import os, json, requests, pathlib, time, subprocess, re, sys, concurrent.futures
from dotenv import load_dotenv
load_dotenv("/Users/harry/aicreative/.env")
sys.path.insert(0, "/Users/harry/aicreative")
from elevenlabs_client import scribe_whisper_compat as scribe
TOKEN = os.environ["USEAPI_TOKEN"]; H = {"Authorization": f"Bearer {TOKEN}"}; EMAIL = "flowmomomedia@gmail.com"
ROOT = pathlib.Path("/Users/harry/aicreative/outputs/chowchilla_podcast")
BR = pathlib.Path("/Users/harry/aicreative/outputs/chowchilla_podcast_bright")

PERSONAS = {"B1":BR/"1.png","B2":BR/"2.png","B3":BR/"3.png","B4":BR/"4.png","B5":BR/"5.png","B6":BR/"6.png","B9":BR/"9.png"}

# letter: (persona, tone, vernacular_text)
SCRIPTS = {
 "A": ("B6","fired up, urgent, real grown-woman conviction",
   "Real talk. If a guard or an officer sexually abused you in a California women's prison, I need you to hear me. Whether it was Chowchilla, CCWF, or CIW, you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred million dollars. You don't need paperwork, you don't need proof, none of that. Most of these get handled without you ever stepping foot in a courtroom. You only pay if you win. It all stay private, just between you and the lawyers. Don't sleep on what could be yours. Tap that button and see if you qualify."),
 "B": ("B2","earnest, building conviction, like she's putting you on to something",
   "This is how women who was sexually abused in the California prisons may qualify for significant potential compensation. I know it sound wild. Stay with me. Survivors from another California women's prison just won over a hundred and sixteen million dollars. If you was sexually abused by a guard or an officer while you was locked up in Chowchilla, you may qualify too. Even if it happened years ago. Even if you never told a soul. Even if you never reported it. Tap that button and take the quiz to see if you qualify. It's free, and it's private."),
 "D": ("B1","authoritative but warm, urgent",
   "Attention. If you was sexually abused by a guard or an officer while you was locked up in a California women's prison, you need to hear this. Whether it was Chowchilla, CCWF, or CIW, the law is on your side now. You may qualify for significant potential compensation. This ain't no scam. Survivors from another California women's prison already won over a hundred and sixteen million dollars. Cases is being reviewed right now. You don't need a old report. You don't need your own lawyer. You don't even gotta set foot in a courtroom. And you pay nothing unless they win for you. Everything stay private, just between you and the attorneys. Take one minute. Tap that button and find out if you qualify."),
 "F": ("B3","righteous anger, fierce, fired up",
   "Those guards in Chowchilla was betting on one thing. That after they sexually abused us, we would be too ashamed to ever open our mouths. That we would carry it straight to our graves. They bet wrong. Women who was sexually abused inside the California prisons may qualify for significant potential compensation now. Survivors from another women's prison out here already won over a hundred million dollars for it. You don't need proof, or a old report, or none of that. The courts is finally making these places answer. You only pay if you win. It all stay private, just between you and the lawyers. After everything they took, this part is yours. Tap that button and see if you qualify."),
 "H": ("B4","warm, targeted, building intensity",
   "This is for you if a guard or an officer sexually abused you in a California women's prison. This is for you if it was Chowchilla, CCWF, or CIW. This is for you if you told yourself it wasn't that bad, or it was too long ago to matter. It was that bad, and it still matter. You may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred million dollars. You don't need proof, you don't need a report, and you don't gotta go to court. You don't pay unless they win. It stay private, just you and the lawyers. If any of this is landing for you, it ain't a coincidence. Tap that button and see if you qualify."),
 "I": ("B9","heavy, confronting, intimate, fired up",
   "If a guard ever came in your cell at night when you was locked up in Chowchilla, don't scroll past this. What he did to you was sexual abuse, even if you never once called it that. Women who lived through it in the California prisons may qualify for significant potential compensation. Survivors from another women's prison out here already won over a hundred million dollars. You don't need no proof, no old report, nothing like that. You only pay if you win. You don't even gotta go to court. It stay private, just between you and the lawyers, no matter how many years it's been. Take a minute. Tap the button. See if you qualify."),
 "M": ("B5","tender naming it plainly, then urgent",
   "What that guard did to you in prison has a name. It was sexual abuse. And if it happened to you inside Chowchilla, or any California women's prison, you may qualify for significant potential compensation. Survivors from another California women's prison already won over a hundred and sixteen million dollars. Cases like yours is being reviewed right now. You don't need proof. You don't need a report. You don't gotta set foot in court. You only pay if you win. Nobody gotta know but you and the lawyers. It don't matter how many years gone by. Take one minute, tap that button, and see if you qualify."),
}

GAZE = "GAZE LOCK: she looks DIRECTLY into the camera lens the ENTIRE clip, steady, never drifting off to the side."
BODY = ("She stays seated in place and speaks into the podcast microphone with natural expressive life: alive "
        "eyes and brows, small hand gestures, nods, blinks. She does NOT lunge at the camera and does NOT sway. No smile.")
BG = ("BACKGROUND LOCK: keep the EXACT SAME background, room, wall, and lighting as in the reference image. "
      "Do NOT change, swap, or re-imagine the background — reproduce the identical setting from the reference "
      "in every shot, unchanging across the whole clip. Same place, same background, same framing the entire time.")

def build(dia, tone):
    return ("Vertical podcast close-up, framed IDENTICALLY from the first frame to the last. The camera is a "
        "completely locked-off tripod: no reframing, no settling, no drift, no zoom, no pan. The background is "
        "a FROZEN still photograph that never moves or changes; only her face and hands move. Keep the exact "
        "same scene and background as the reference image. She stays seated and speaks with natural expressive life: alive eyes "
        "and brows, small hand gestures, nods, blinks, no smile, does not lunge. She looks straight into the lens. "
        "VOICE: a weathered late-40s Black woman from South Central Los Angeles, low, raspy, fired up, real LA "
        "vernacular, NOT flat, NOT an announcer. TONE: "+tone+". Brisk delivery, about 2.4 words per second, no "
        "long pauses. She says ONLY this, verbatim, no extra or repeated words, then stops: \""+dia+"\" No on-screen text, no music.")

def chunk(text):
    parts = re.split(r'(?<=[.?!])\s+', text.strip()); out=[]
    for p in parts:
        p=p.strip().rstrip('.?!').strip()
        if not p: continue
        if len(p.split())<=13: out.append(p); continue
        # pack comma-clauses into <=13-word groups (don't isolate tiny fragments)
        cur=[]
        for c in re.split(r',\s*', p):
            c=c.strip()
            if not c: continue
            if len((" ".join(cur+[c])).split())<=13: cur.append(c)
            else:
                if cur: out.append(", ".join(cur))
                cur=[c]
        if cur: out.append(", ".join(cur))
    return out

def dur_for(dia):
    w=len(dia.split())
    return 4 if w<=6 else (6 if w<=10 else 8)

def split_dia(dia):
    ws=dia.split()
    if ',' in dia:
        i=dia.find(','); return dia[:i].strip(), dia[i+1:].strip()
    mid=len(ws)//2; return " ".join(ws[:mid]), " ".join(ws[mid:])

def clean(text, dia):
    # Trailing/leading improv is NOT rejected here — the jump-cut assembler trims to the
    # intended span via Scribe word-timestamps, so paying to re-roll it is pure waste.
    # Reject ONLY defects that survive the trim: a false-start hyphen, the line not fully
    # spoken, or a stutter BETWEEN intended words (inside the kept span).
    raw=text.strip()
    if re.search(r"[A-Za-z]+-", raw): return False,"hyphen"
    w=re.findall(r"[a-z']+", raw.lower())
    intended=re.findall(r"[a-z']+", dia.lower())
    # ordered subsequence match; record the kept span [first_idx, last_idx]
    wi=0; first_idx=None; last_idx=None
    for j,tok in enumerate(w):
        if wi<len(intended) and tok==intended[wi]:
            if first_idx is None: first_idx=j
            last_idx=j; wi+=1
    if wi<len(intended): return False,"missing"          # whole line not spoken -> re-roll
    span=w[first_idx:last_idx+1]                          # exactly what survives the trim
    for n in (1,2,3):                                     # mid-line stutter in kept span
        for i in range(len(span)-2*n+1):
            if span[i:i+n]==span[i+n:i+2*n]: return False,f"{n}gram"
    return True,"ok"

def upload(path, ctype="image/png"):
    with open(path,"rb") as f:
        r=requests.post(f"https://api.useapi.net/v1/google-flow/assets/{requests.utils.quote(EMAIL)}",headers={**H,"Content-Type":ctype},data=f.read(),timeout=180)
    m=r.json().get("mediaGenerationId"); return m.get("mediaGenerationId") if isinstance(m,dict) else m

def gen(out, dia, dur, mgid, tone, attempts=3):
    if out.exists() and out.stat().st_size>50000: return True
    for a in range(1,attempts+1):
        payload={"prompt":build(dia,tone),"model":"omni-flash","aspectRatio":"portrait","duration":dur,
                 "count":1,"referenceImage_1":mgid,"captchaRetry":3,"seed":(abs(hash(out.name))%9000)+a*31}
        try:
            g=requests.post("https://api.useapi.net/v1/google-flow/videos",headers={**H,"Content-Type":"application/json"},json=payload,timeout=600)
            gj=g.json()
            if g.status_code==200 and gj.get("media"):
                tmp=f"/tmp/_p_{out.stem}.mp4"; open(tmp,"wb").write(requests.get(gj["media"][0]["videoUrl"],timeout=180).content)
                subprocess.run(["ffmpeg","-y","-i",tmp,"-vn","-ar","16000","-ac","1",f"/tmp/_p_{out.stem}.wav"],capture_output=True)
                txt=scribe(f"/tmp/_p_{out.stem}.wav",biased_keywords=["Chowchilla","CCWF","CIW"],language_code="en").get("text","")
                ok,why=clean(txt,dia)
                if ok: open(out,"wb").write(open(tmp,"rb").read()); print(f"  {out.name} CLEAN a{a}",flush=True); return True
                print(f"  {out.name} a{a} REJECT[{why}]",flush=True)
            else:
                try: rs=gj["response"]["media"][0]["mediaMetadata"]["mediaStatus"].get("failureReasons")
                except Exception: rs=str(gj.get("error") or gj)[:70]
                print(f"  {out.name} a{a} GENFAIL {rs}",flush=True)
        except Exception as e: print(f"  {out.name} a{a} EXC {str(e)[:70]}",flush=True)
        time.sleep(6)
    return False

def do_chunk(args):
    i,dia,mgid,tone=args
    base=DIR/f"{i:02d}.mp4"; a_=DIR/f"{i:02d}a.mp4"; b_=DIR/f"{i:02d}b.mp4"
    if base.exists() and base.stat().st_size>50000: return
    if a_.exists() and b_.exists(): return
    if gen(base,dia,dur_for(dia),mgid,tone,attempts=3): return
    if len(dia.split())<=6:
        print(f"  !! {i:02d} short clip won't clear, NOT splitting into fragments (dropping): '{dia}'",flush=True); return
    d1,d2=split_dia(dia)
    print(f"  >> splitting {i:02d}: '{d1}' | '{d2}'",flush=True)
    gen(a_,d1,dur_for(d1),mgid,tone,attempts=2); gen(b_,d2,dur_for(d2),mgid,tone,attempts=2)

def jumpcut(files, dias, out):
    trimmed=[]
    for j,fn in enumerate(files):
        p=DIR/fn; wav=f"/tmp/_jc_{p.stem}.wav"
        subprocess.run(["ffmpeg","-y","-i",str(p),"-vn","-ar","16000","-ac","1",wav],capture_output=True)
        ws=[w for w in scribe(wav,biased_keywords=["Chowchilla"],language_code="en").get("segments",[{}])[0].get("words",[]) if w.get("start") is not None]
        D=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",str(p)],capture_output=True,text=True).stdout.strip())
        # Trim to the INTENDED span: subsequence-match the scripted line against the transcript,
        # cut at the first & last intended word -> drops leading junk AND trailing improv
        # (so we keep clips that clean() now accepts instead of paying to re-roll them).
        intended=re.findall(r"[a-z']+", dias[j].lower()) if j < len(dias) else []
        wi=0; st=None; en=None
        for w in ws:
            tok=re.sub(r"[^a-z']","",(w.get("word") or "").lower())
            if wi<len(intended) and tok==intended[wi]:
                if st is None: st=w["start"]
                en=w["end"]; wi+=1
        if st is None or en is None:                 # match failed -> full speech span fallback
            st=ws[0]["start"] if ws else 0.0; en=ws[-1]["end"] if ws else D
        st=max(0.0,st-0.03); en=min(D,en+0.05)
        t=DIR/f"_jt{j:02d}.mp4"
        subprocess.run(["ffmpeg","-y","-ss",f"{st:.3f}","-i",str(p),"-t",f"{en-st:.3f}","-vf","scale=720:1280,fps=24,setsar=1","-c:v","libx264","-preset","fast","-crf","18","-c:a","aac","-ar","44100","-b:a","192k",str(t)],capture_output=True,check=True)
        trimmed.append(t)
    lst=DIR/"_jc.txt"; lst.write_text("".join(f"file '{t.resolve()}'\n" for t in trimmed))
    raw=DIR/"_jcraw.mp4"; subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(raw)],capture_output=True,check=True)
    meas=subprocess.run(["ffmpeg","-i",str(raw),"-af","loudnorm=I=-16:TP=-1.5:print_format=json","-f","null","-"],capture_output=True,text=True)
    mm=re.search(r"\{[^{}]*\"input_i\"[^{}]*\}",meas.stderr.replace("\n"," ")); gn=0.0
    if mm:
        try: gn=-16.0-float(json.loads(mm.group(0))["input_i"])
        except Exception: gn=0.0
    subprocess.run(["ffmpeg","-y","-i",str(raw),"-af",f"volume={gn:.2f}dB,alimiter=limit=0.891","-c:v","copy","-c:a","aac","-b:a","192k",out],capture_output=True,check=True)

if __name__=="__main__":
    letter=sys.argv[1]; persona,tone,text=SCRIPTS[letter]
    DIR=ROOT/f"{letter}_{persona}_la"; DIR.mkdir(parents=True,exist_ok=True)
    chunks=chunk(text)
    print(f"=== {letter} on {persona}: {len(chunks)} chunks ===",flush=True)
    mgid=upload(PERSONAS[persona])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(do_chunk,[(i,d,mgid,tone) for i,d in enumerate(chunks)]))
    files=[]; dias=[]
    for i in range(len(chunks)):
        if (DIR/f"{i:02d}.mp4").exists():
            files.append(f"{i:02d}.mp4"); dias.append(chunks[i])
        elif (DIR/f"{i:02d}a.mp4").exists() and (DIR/f"{i:02d}b.mp4").exists():
            d1,d2=split_dia(chunks[i]); files+=[f"{i:02d}a.mp4",f"{i:02d}b.mp4"]; dias+=[d1,d2]
        elif (DIR/f"{i:02d}a.mp4").exists():
            d1,_=split_dia(chunks[i]); files.append(f"{i:02d}a.mp4"); dias.append(d1)
        else: print(f"  !! chunk {i:02d} MISSING (gave up)",flush=True)
    print(f"  assembling {len(files)} clips",flush=True)
    out=str(ROOT/f"{letter}_full.mp4")
    if files: jumpcut(files,dias,out); print(f"DONE {letter} -> {out}",flush=True)
    else: print(f"DONE {letter} -> NO CLIPS",flush=True)
