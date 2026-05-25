"""Generalized finalize for the IL JDC Tier-1 ads (one persona per ad).

Pipeline (same as Ad 3 / He's Still Out There):
  Scribe-trim each clip (speech window, prints transcript for QA)
  -> clone ONE voice from clip1+clip2  -> voice_changer every clip (unify timbre)
  -> loudnorm -16  -> mux back onto trimmed video  -> concat 9:16
  -> crop_4x5  -> hormozi3 captions on both aspects.

Usage:
  .venv/bin/python scripts/jdc_finalize.py --ad illinois_jdc_confession_p03 --clips 5
  .venv/bin/python scripts/jdc_finalize.py --ad illinois_jdc_memorytrigger_p02 --clips 4
  .venv/bin/python scripts/jdc_finalize.py --ad illinois_jdc_youwereakid_p01 --clips 3

Outputs in outputs/<ad>/:
  final_vc.mp4 / final_vc_4x5.mp4                 (clean, no captions)
  final_vc_hormozi3.mp4 / final_vc_4x5_hormozi3.mp4
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat, clone_voice, voice_changer

LEAD_PAD = 0.10
TAIL_PAD = 0.22


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR {' '.join(cmd[:3])}… {r.stderr[-300:]}", flush=True)
    return r.returncode == 0


def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def speech_window(video):
    r = scribe_whisper_compat(str(video), language_code="en")
    words = [w for s in r["segments"] for w in s.get("words", [])]
    text = " ".join(w["word"] for w in words).strip()
    if not words:
        return None, None, ""
    return words[0]["start"], words[-1]["end"], text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", required=True, help="ad folder under outputs/")
    ap.add_argument("--clips", type=int, required=True)
    args = ap.parse_args()

    OUT = Path("outputs") / args.ad
    TRIM = OUT / "trimmed"; TRIM.mkdir(parents=True, exist_ok=True)
    VC = OUT / "vc"; VC.mkdir(parents=True, exist_ok=True)
    VOICE_CACHE = OUT / "voice_id.txt"
    clips = [f"clip{i}" for i in range(1, args.clips + 1)]

    # 1. Scribe-trim each clip (speech window) + print transcript for QA
    print("=== TRIM (speech window) + QA transcript ===", flush=True)
    for c in clips:
        src = OUT / f"{c}.mp4"
        dur = get_dur(src)
        first, last, text = speech_window(src)
        if first is None:
            print(f"  [{c}] NO SPEECH — skipping", flush=True); continue
        start = max(0.0, first - LEAD_PAD); end = min(dur, last + TAIL_PAD)
        dst = TRIM / f"{c}.mp4"
        run(["ffmpeg", "-y", "-i", str(src), "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "19",
             "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(dst)])
        print(f"  [{c}] [{start:.2f}-{end:.2f}s] -> {get_dur(dst):.2f}s | \"{text}\"", flush=True)

    # 2. Extract trimmed audio
    for c in clips:
        run(["ffmpeg", "-y", "-i", str(TRIM / f"{c}.mp4"), "-vn", "-ar", "44100",
             "-ac", "1", str(VC / f"{c}_orig.mp3")])

    # 3. Clone ONE voice from clip1+clip2 (richer source)
    if VOICE_CACHE.exists():
        voice_id = VOICE_CACHE.read_text().strip()
        print(f"Using cached voice_id: {voice_id}", flush=True)
    else:
        print("=== CLONE VOICE (clip1+clip2) ===", flush=True)
        cat = VC / "clone_src_list.txt"
        srcs = [VC / "clip1_orig.mp3"] + ([VC / "clip2_orig.mp3"] if len(clips) > 1 else [])
        cat.write_text("".join(f"file '{s.absolute()}'\n" for s in srcs))
        clone_src = VC / "clone_src.mp3"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat), "-c", "copy", str(clone_src)])
        voice_id = clone_voice(args.ad, [str(clone_src)])
        VOICE_CACHE.write_text(voice_id)
        print(f"voice_id: {voice_id}", flush=True)

    # 4. voice_changer each
    print("=== VOICE CHANGER ===", flush=True)
    for c in clips:
        voice_changer(str(VC / f"{c}_orig.mp3"), voice_id, str(VC / f"{c}_vc.mp3"),
                      model_id="eleven_multilingual_sts_v2", stability=0.5, similarity_boost=0.85)
        print(f"  [{c}] voice-changed", flush=True)

    # 5. loudnorm + mux
    print("=== LOUDNORM + MUX ===", flush=True)
    muxed = []
    for c in clips:
        norm = VC / f"{c}_vc_norm.mp3"
        run(["ffmpeg", "-y", "-i", str(VC / f"{c}_vc.mp3"),
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", str(norm)])
        out = VC / f"{c}.mp4"
        run(["ffmpeg", "-y", "-i", str(TRIM / f"{c}.mp4"), "-i", str(norm),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        muxed.append(out)
        print(f"  [{c}] muxed -> {get_dur(out):.2f}s", flush=True)

    # 6. concat
    print("=== CONCAT ===", flush=True)
    cl = VC / "concat.txt"
    cl.write_text("".join(f"file '{p.absolute()}'\n" for p in muxed))
    final_vc = OUT / "final_vc.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(final_vc)])
    print(f"DONE -> {final_vc} ({get_dur(final_vc):.2f}s)", flush=True)

    # 7. 4:5
    final_45 = OUT / "final_vc_4x5.mp4"
    run([".venv/bin/python", "scripts/crop_4x5.py", str(final_vc), "--out", str(final_45)])
    print(f"DONE -> {final_45}", flush=True)

    # 8. hormozi3 captions (4:5 nudged to 0.80 to clear the chin on the tighter crop)
    print("=== HORMOZI3 CAPTIONS ===", flush=True)
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final_vc),
         "--out", str(OUT / "final_vc_hormozi3.mp4")])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final_45),
         "--out", str(OUT / "final_vc_4x5_hormozi3.mp4"), "--vertical-pos", "0.80"])
    print(f"DONE -> {OUT}/final_vc_hormozi3.mp4 + final_vc_4x5_hormozi3.mp4", flush=True)


if __name__ == "__main__":
    main()
