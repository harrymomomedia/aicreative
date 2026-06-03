"""Finalize the tort IL JDC testimonial videos (FREE google-flow path).
Per video: word-aware trim (uses the per-clip dissect transcript) -> WATERMARK-CROP the bottom-right
"Veo" mark (crop 664x1180 + rescale to clean 720x1280) -> per-clip static gain -> concat -> master
limiter. Transcripts expected at outputs/jdc_tort_<v>_<cid>/transcript.json (unique stems to dodge
the dissect collision on clip01.mp4).

  python scripts/jdc_tort_finalize.py <whis|bro|fam>
"""
import json, subprocess, re, sys
from pathlib import Path

VIDEOS = {
    "whis": ("outputs/illinois_jdc_tort_whistleblower", 6, "story_whis_final.mp4"),
    "bro":  ("outputs/illinois_jdc_tort_brother", 5, "story_bro_final.mp4"),
    "fam":  ("outputs/illinois_jdc_tort_family", 5, "story_fam_final.mp4"),
}
TARGET_CLIP, TARGET_MASTER = -18.0, -16.0
VF = "crop=664:1180:28:0,scale=720:1280,setsar=1,fps=24"   # off the bottom-right Veo watermark


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def measure_i(path):
    p = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    t = p.stderr
    return float(json.loads(t[t.rfind("{"):t.rfind("}") + 1])["input_i"])


def main():
    v = sys.argv[1]
    src_dir, n, out_name = VIDEOS[v]
    SRC = Path(src_dir); WORK = SRC / "finalize"; WORK.mkdir(exist_ok=True)
    clips = [f"clip{i:02d}" for i in range(1, n + 1)]

    print(f"== [{v}] trim + watermark-crop + gain ==", flush=True)
    for cid in clips:
        s = SRC / f"{cid}.mp4"
        if not s.exists():
            print(f"  {cid} MISSING — skip", flush=True); continue
        trans = Path(f"outputs/jdc_tort_{v}_{cid}/transcript.json")
        if trans.exists():
            subprocess.run([".venv/bin/python", "scripts/trim_silence.py", str(s), str(trans),
                            "--lead", "0.10", "--tail", "0.25"], check=True, capture_output=True, text=True)
            tr = SRC / f"{cid}_trimmed.mp4"
        else:
            tr = s
        i = measure_i(tr); gain = TARGET_CLIP - i
        run(["ffmpeg", "-y", "-i", str(tr), "-vf", VF, "-af", f"volume={gain:.2f}dB",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", str(WORK / f"{cid}.mp4")])
        print(f"  {cid}: {i:.1f} LUFS -> {gain:+.1f}dB", flush=True)

    present = [c for c in clips if (WORK / f"{c}.mp4").exists()]
    listf = WORK / "concat.txt"
    listf.write_text("".join(f"file '{(WORK / f'{c}.mp4').resolve()}'\n" for c in present))
    stitched = WORK / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listf), "-c", "copy", str(stitched)])

    mi = measure_i(stitched)
    final = SRC / out_name
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-af", f"volume={TARGET_MASTER - mi:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", str(final)], capture_output=True, text=True).stdout.strip()
    print(f"\nFINAL [{v}]: {final}  dur {dur}s  {measure_i(final):.1f} LUFS", flush=True)


if __name__ == "__main__":
    main()
