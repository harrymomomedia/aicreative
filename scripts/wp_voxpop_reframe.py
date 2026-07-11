"""9:16 punch-in reframe + assemble. Crop each wide 16:9 two-shot to a vertical window on the
ACTIVE speaker per turn (L=interviewer, R=respondent), switching per turn. Turn timings from
aligning the Scribe transcript to the known script turns. Per-segment fixed crop -> concat
(robust; no dynamic-crop expression). Output = final 9:16 ad with even loudness.
Usage: python scripts/wp_voxpop_reframe.py [out.mp4]
"""
import sys, subprocess, json, re, pathlib

CROP_W, H = 405, 720
X_L, X_R = 120, 740
LEAD, TRAIL = 0.05, 0.25

# ---- format configs (dir, clip order, per-clip turns: L=interviewer/reporter, R=respondent) ----
CONFIGS = {
 "voxpop": {
  "dir": "outputs/wp_voxpop/grok_ad",
  "order": ["clip1_A", "clip2_B", "clip3_C"],
  "turns": {
   "clip1_A": [("L","Did you know women who were sexually abused at Chowchilla may qualify for significant potential compensation"),
               ("R","Wait for real My cousin was in there She never told anybody what happened to her"),
               ("L","It is free and confidential to check"),
               ("R","That is about time Those women deserve that")],
   "clip2_B": [("L","Have you heard what happened to the women at Chowchilla"),
               ("R","Yeah I did time in there What those guards did to us nobody listened back then"),
               ("L","You may qualify for significant potential compensation now"),
               ("R","For real After all these years")],
   "clip3_C": [("L","If you were at Chowchilla would you come forward"),
               ("R","I would Those women waited too long for somebody to finally listen"),
               ("L","It is free confidential and there is no court")]}},
 "interview": {
  "dir": "outputs/wp_voxpop/interview_ad",
  "order": ["clip1", "clip2", "clip3"],
  "turns": {
   "clip1": [("L","Nearly 500 women who were incarcerated in California's prisons are coming forward You were at Chowchilla What happened in there"),
             ("R","The guards crossed the line Sexually And back then nobody would have believed us"),
             ("L","A lot of women think that because they never reported it it is too late"),
             ("R","That is exactly what I thought I thought it was my fault")],
   "clip2": [("L","But under California law a woman in prison cannot consent to a guard So women like you may qualify for significant potential compensation"),
             ("R","Wait Even after all these years"),
             ("L","Even now It is free to check completely confidential and you never go to court"),
             ("R","If I had only known that sooner")],
   "clip3": [("L","If you were at Chowchilla Valley State or Folsom there is a private two minute form"),
             ("R","So anyone who was in there should check"),
             ("L","Yes Tap below and see if you qualify")]}},
}

def toks(s): return re.findall(r"[a-z]+", s.lower())

def align(words, turns):
    """Find each turn's start via its first 1-2 words (anchor), advancing a cursor. Robust to a
    mispronounced/missing word MID-turn (which the old every-word matcher choked on -> it let one
    turn eat the whole clip, so the crop never switched speakers)."""
    def norm(w): return re.sub(r"[^a-z]", "", (w.get("word") or w.get("text") or "").lower())
    tw = [w for w in words if w.get("type","word") == "word"]
    if not tw: return []
    starts, pos = [], 0
    for spk, text in turns:
        exp = toks(text); a0 = exp[0]; a1 = exp[1] if len(exp) > 1 else None
        found = None
        for j in range(pos, len(tw)):
            if norm(tw[j]) == a0 and (a1 is None or (j+1 < len(tw) and norm(tw[j+1]) == a1)):
                found = j; break
        if found is None:                                    # relax to single-word anchor
            for j in range(pos, len(tw)):
                if norm(tw[j]) == a0: found = j; break
        if found is None: found = pos
        starts.append(found)
        pos = max(found + 1, found + len(exp) - 2)           # advance past most of this turn
    segs = []
    for k, (spk, text) in enumerate(turns):
        s = tw[starts[k]]["start"]
        e = tw[starts[k+1]]["start"] if k+1 < len(starts) else tw[-1]["end"]
        segs.append([spk, round(s,2), round(e,2)])
    return segs

def main():
    setname = sys.argv[1] if len(sys.argv) > 1 else "voxpop"
    cfg = CONFIGS[setname]
    D = pathlib.Path(cfg["dir"]); ORDER = cfg["order"]; TURNS = cfg["turns"]
    out = sys.argv[2] if len(sys.argv) > 2 else str(D / f"{setname}_9x16.mp4")
    pieces, concat_lines = [], []
    idx = 0
    for slug in ORDER:
        words = json.load(open(f"outputs/{slug}_qa/transcript.json"))["segments"][0]["words"]
        segs = align(words, TURNS[slug])
        # extend cut boundaries: each turn holds until next turn's start; last turn +TRAIL
        for k, (spk, s, e) in enumerate(segs):
            cut_in = max(0, (s - LEAD) if k == 0 else s)
            cut_out = segs[k+1][1] if k + 1 < len(segs) else e + TRAIL
            x = X_L if spk == "L" else X_R
            p = str(D / f"_seg{idx}.mp4"); idx += 1
            subprocess.run(["ffmpeg","-y","-i",str(D/f"{slug}.mp4"),"-ss",str(cut_in),"-to",str(cut_out),
                "-vf",f"crop={CROP_W}:{H}:{x}:0,scale=720:1280,setsar=1,fps=30",
                "-c:v","libx264","-preset","fast","-crf","20","-c:a","aac","-b:a","192k","-avoid_negative_ts","make_zero",p],
                capture_output=True)
            pieces.append(p); concat_lines.append(f"file '{pathlib.Path(p).resolve()}'")
            print(f"[{slug}] turn{k} {spk} {round(cut_in,2)}->{round(cut_out,2)}")
    lst = D / "_concat.txt"; lst.write_text("\n".join(concat_lines) + "\n")
    # concat + loudnorm
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
        "-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-preset","fast","-crf","20",
        "-c:a","aac","-b:a","192k",out],capture_output=True)
    web = out.replace(".mp4","_web.mp4")
    subprocess.run(["ffmpeg","-y","-i",out,"-c:v","libx264","-preset","fast","-crf","26",
        "-c:a","aac","-b:a","128k",web],capture_output=True)
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nk=1:nw=1",out],
                       capture_output=True,text=True).stdout.strip()
    print(f"[done] {out}  ({d}s)  web={web}")

if __name__ == "__main__":
    main()
