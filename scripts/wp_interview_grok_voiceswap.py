"""Grok interview: punch-in reframe + DISTINCT Latina voices per speaker (voice_changer).
Reporter (L) and survivor (R) each get a different Latina voice, so the back-and-forth reads as
two people. Per-turn: crop to speaker -> STS the segment audio -> remux -> concat + loudnorm.
"""
import subprocess, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from wp_voxpop_reframe import align, CONFIGS
from elevenlabs_client import voice_changer

CFG = CONFIGS["interview"]
D = pathlib.Path(CFG["dir"])
CROP_W, H = 405, 720
X_L, X_R = 120, 740
LEAD, TRAIL = 0.05, 0.22
VOICE = {"L": "0q9TlrIoQJIdxZP9oZh7",   # Hazel - Latino-English (reporter, brighter)
         "R": "tzRooR5RYgzzl2QoJNC0"}   # Hispanic 50 yr old (survivor, weathered)

pieces, lines = [], []
idx = 0
for slug in CFG["order"]:
    words = json.load(open(f"outputs/{slug}_qa/transcript.json"))["segments"][0]["words"]
    segs = align(words, CFG["turns"][slug])
    for k, (spk, s, e) in enumerate(segs):
        cin = max(0, (s - LEAD) if k == 0 else s)
        cout = segs[k+1][1] if k+1 < len(segs) else e + TRAIL
        x = X_L if spk == "L" else X_R
        vseg = str(D / f"_vs{idx}.mp4"); aseg = str(D / f"_vs{idx}.mp3"); vcseg = str(D / f"_vc{idx}.mp3")
        # cropped+trimmed video (keep original audio for now)
        subprocess.run(["ffmpeg","-y","-i",str(D/f"{slug}.mp4"),"-ss",str(round(cin,2)),"-to",str(round(cout,2)),
            "-vf",f"crop={CROP_W}:{H}:{x}:0,scale=720:1280,setsar=1,fps=30",
            "-c:v","libx264","-preset","fast","-crf","20","-an",vseg],capture_output=True)
        # extract segment audio, STS to the speaker's voice
        subprocess.run(["ffmpeg","-y","-i",str(D/f"{slug}.mp4"),"-ss",str(round(cin,2)),"-to",str(round(cout,2)),
            "-vn","-ar","44100","-ac","1",aseg],capture_output=True)
        try:
            voice_changer(aseg, VOICE[spk], vcseg, model_id="eleven_english_sts_v2",
                          stability=0.5, similarity_boost=0.7, output_format="mp3_44100_128")
            aud = vcseg
        except Exception as ex:
            print(f"  VC failed seg{idx} ({ex}); using raw"); aud = aseg
        out = str(D / f"_vp{idx:02d}.mp4")
        subprocess.run(["ffmpeg","-y","-i",vseg,"-i",aud,"-map","0:v","-map","1:a",
            "-c:v","copy","-c:a","aac","-b:a","192k","-shortest",out],capture_output=True)
        pieces.append(out); lines.append(f"file '{pathlib.Path(out).resolve()}'")
        print(f"[{slug}] turn{k} {spk} voice={VOICE[spk]} {round(cin,2)}->{round(cout,2)}", flush=True)

lst = D / "_vconcat.txt"; lst.write_text("\n".join(lines) + "\n")
outp = str(D / "interview_grok_voiceswap.mp4")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
    "-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:v","libx264","-preset","fast","-crf","20",
    "-c:a","aac","-b:a","192k",outp],capture_output=True)
subprocess.run(["ffmpeg","-y","-i",outp,"-c:v","libx264","-preset","fast","-crf","26",
    "-c:a","aac","-b:a","128k",outp.replace(".mp4","_web.mp4")],capture_output=True)
print("GROK VOICESWAP DONE ->", outp)
