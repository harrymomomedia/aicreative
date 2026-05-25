"""Re-finish the audio without pumping/clipping.

Root issue: per-clip single-pass `loudnorm` runs in DYNAMIC mode (time-varying gain) →
audible "volume cutting off"/pumping, and hot STS peaks risk inter-sample clipping.

Fix: mux the RAW STS clone output (vc/{c}_vc2.mp3) onto each trimmed clip with NO per-clip
loudnorm, concat, then apply ONE TWO-PASS LINEAR loudnorm (single static gain, TP -2.0) to the
whole ad. Reuses the saved STS outputs — NO new ElevenLabs calls.

Usage: .venv/bin/python scripts/jdc_refinish.py --ad illinois_jdc_confession_p03 --clips 5 --suffix _pv
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR {' '.join(cmd[:3])}… {r.stderr[-300:]}", flush=True)
    return r


def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def measure_loudnorm(infile):
    r = subprocess.run(["ffmpeg", "-i", str(infile),
                        "-af", "loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    s, e = txt.rfind("{"), txt.rfind("}")
    return json.loads(txt[s:e + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", required=True)
    ap.add_argument("--clips", type=int, required=True)
    ap.add_argument("--suffix", default="_pv")
    args = ap.parse_args()

    OUT = Path("outputs") / args.ad
    TRIM = OUT / "trimmed"
    VC = OUT / "vc"
    clips = [f"clip{i}" for i in range(1, args.clips + 1)]

    # 1. mux RAW STS clone output onto each trimmed clip (NO per-clip loudnorm)
    muxed = []
    for c in clips:
        sts = VC / f"{c}_vc2.mp3"           # raw STS clone output (from finalize_v2)
        if not sts.exists():
            print(f"  MISSING {sts} — run finalize_v2 first", flush=True)
            return
        out = VC / f"{c}{args.suffix}_raw.mp4"
        run(["ffmpeg", "-y", "-i", str(TRIM / f"{c}.mp4"), "-i", str(sts),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        muxed.append(out)

    # 2. concat (raw audio, no normalization yet)
    cl = VC / f"concat{args.suffix}_raw.txt"
    cl.write_text("".join(f"file '{p.absolute()}'\n" for p in muxed))
    concat_raw = VC / f"concat{args.suffix}_raw.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(concat_raw)])

    # 3. STATIC gain to -16 LUFS + true-peak safety limiter (NO dynamic gain-riding = NO pumping)
    m = measure_loudnorm(concat_raw)
    gain = -16.0 - float(m["input_i"])           # single constant gain, preserves natural dynamics
    af = f"volume={gain:.2f}dB,alimiter=limit=0.794:asc=1"   # 0.794 ≈ -2.0 dBFS ceiling
    final = OUT / f"final{args.suffix}.mp4"
    run(["ffmpeg", "-y", "-i", str(concat_raw), "-af", af,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    print(f"DONE -> {final} ({get_dur(final):.2f}s)  static gain {gain:+.2f}dB "
          f"(in {m['input_i']} -> -16 LUFS), limiter -2dBFS", flush=True)

    # 4. 4:5 + captions
    final45 = OUT / f"final{args.suffix}_4x5.mp4"
    run([".venv/bin/python", "scripts/crop_4x5.py", str(final), "--out", str(final45)])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final),
         "--out", str(OUT / f"final{args.suffix}_hormozi3.mp4")])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final45),
         "--out", str(OUT / f"final{args.suffix}_4x5_hormozi3.mp4"), "--vertical-pos", "0.80"])
    print(f"DONE -> {OUT}/final{args.suffix}_hormozi3.mp4 + 4x5", flush=True)


if __name__ == "__main__":
    main()
