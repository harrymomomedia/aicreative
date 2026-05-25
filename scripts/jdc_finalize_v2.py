"""Higher-quality voice-change finalize (fixes the muffled VC).

Changes vs jdc_finalize.py:
  - STS output is LOSSLESS pcm_44100 (was 128k mp3) — no codec muffle, single AAC encode at the end.
  - eleven_english_sts_v2 (crisper for English than multilingual).
  - Clone from the CRISPEST clips (highest spectral centroid), not the dull ones —
    a fuller/brighter voice model. (the "2 clips together" idea, picked by quality.)
  - similarity_boost 0.70 so a dull clone doesn't dominate the synthesis.

Reuses existing outputs/<ad>/trimmed/ + vc/*_orig.mp3 when present (fast re-run).
Writes final_vc2.mp4 / final_vc2_4x5.mp4 / *_hormozi3 so it doesn't clobber final_vc / final_orig.

Usage: .venv/bin/python scripts/jdc_finalize_v2.py --ad illinois_jdc_confession_p03 --clips 5
"""
import argparse
import subprocess
import sys
import json
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import scribe_whisper_compat, clone_voice, voice_changer

warnings.filterwarnings("ignore")
LEAD_PAD, TAIL_PAD = 0.10, 0.22


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR {' '.join(cmd[:3])}… {r.stderr[-300:]}", flush=True)
    return r.returncode == 0


def measure_i(infile):
    """Integrated loudness (LUFS) via loudnorm's measurement pass."""
    r = subprocess.run(["ffmpeg", "-i", str(infile),
                        "-af", "loudnorm=I=-16:TP=-2.0:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    s, e = r.stderr.rfind("{"), r.stderr.rfind("}")
    return float(json.loads(r.stderr[s:e + 1])["input_i"])


def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)], capture_output=True, text=True)
    return float(r.stdout.strip())


def speech_window(video):
    r = scribe_whisper_compat(str(video), language_code="en")
    words = [w for s in r["segments"] for w in s.get("words", [])]
    if not words:
        return None, None, ""
    return words[0]["start"], words[-1]["end"], " ".join(w["word"] for w in words).strip()


def centroid(p):
    import librosa
    y, sr = librosa.load(str(p), sr=22050)
    return float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", required=True)
    ap.add_argument("--clips", type=int, required=True)
    ap.add_argument("--suffix", default="_vc2")
    ap.add_argument("--clone-n", type=int, default=3, help="how many crispest clips to clone from")
    ap.add_argument("--voice-id", default=None,
                    help="use a pre-made persona clone (skips per-ad cloning) — see outputs/persona_voices/")
    args = ap.parse_args()

    OUT = Path("outputs") / args.ad
    TRIM = OUT / "trimmed"; TRIM.mkdir(parents=True, exist_ok=True)
    VC = OUT / "vc"; VC.mkdir(parents=True, exist_ok=True)
    clips = [f"clip{i}" for i in range(1, args.clips + 1)]

    # 1. trim (reuse if present) + extract orig audio
    print("=== TRIM + EXTRACT (reuse if present) ===", flush=True)
    for c in clips:
        dst = TRIM / f"{c}.mp4"
        if not dst.exists():
            src = OUT / f"{c}.mp4"
            first, last, text = speech_window(src)
            start = max(0.0, first - LEAD_PAD); end = min(get_dur(src), last + TAIL_PAD)
            run(["ffmpeg", "-y", "-i", str(src), "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "19",
                 "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(dst)])
            print(f"  [{c}] trimmed [{start:.2f}-{end:.2f}] | \"{text}\"", flush=True)
        og = VC / f"{c}_orig.mp3"
        if not og.exists():
            run(["ffmpeg", "-y", "-i", str(dst), "-vn", "-ar", "44100", "-ac", "1", str(og)])

    # 2. voice source: a pre-made PERSONA clone (preferred) or per-ad crispest-clip clone
    if args.voice_id:
        voice_id = args.voice_id
        print(f"=== Using persona clone voice_id: {voice_id} ===", flush=True)
    else:
        cents = {c: centroid(VC / f"{c}_orig.mp3") for c in clips}
        crisp = sorted(clips, key=lambda c: cents[c], reverse=True)[:args.clone_n]
        crisp = [c for c in clips if c in crisp]  # keep timeline order
        print(f"=== CLONE from crispest {args.clone_n}: {crisp} "
              f"(centroids { {c: round(cents[c]) for c in clips} }) ===", flush=True)
        vid_cache = OUT / "voice_id_v2.txt"
        if vid_cache.exists():
            voice_id = vid_cache.read_text().strip()
            print(f"Using cached voice_id (v2): {voice_id}", flush=True)
        else:
            cat = VC / "clone_src_v2_list.txt"
            cat.write_text("".join(f"file '{(VC / (c + '_orig.mp3')).absolute()}'\n" for c in crisp))
            clone_src = VC / "clone_src_v2.mp3"
            run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat), "-c", "copy", str(clone_src)])
            voice_id = clone_voice(args.ad + "_v2", [str(clone_src)])
            vid_cache.write_text(voice_id)
            print(f"voice_id (v2): {voice_id}", flush=True)

    # 3. voice_changer — 192k mp3 (pcm needs Pro tier), English model, lower similarity.
    #    Skip-if-exists so re-runs (e.g. audio re-finish) don't burn ElevenLabs calls.
    print("=== VOICE CHANGER (mp3_44100_192, english_sts_v2, sim 0.70) ===", flush=True)
    for c in clips:
        vcout = VC / f"{c}_vc2.mp3"
        if vcout.exists() and vcout.stat().st_size > 5000:
            print(f"  [{c}] STS cached", flush=True)
            continue
        voice_changer(str(VC / f"{c}_orig.mp3"), voice_id, str(vcout),
                      model_id="eleven_english_sts_v2", stability=0.5, similarity_boost=0.70,
                      output_format="mp3_44100_192")

    # 4. mux RAW STS onto each trimmed clip (NO per-clip loudnorm), then concat
    muxed = []
    for c in clips:
        out = VC / f"{c}{args.suffix}_raw.mp4"
        run(["ffmpeg", "-y", "-i", str(TRIM / f"{c}.mp4"), "-i", str(VC / f"{c}_vc2.mp3"),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        muxed.append(out)
    cl = VC / f"concat{args.suffix}.txt"
    cl.write_text("".join(f"file '{p.absolute()}'\n" for p in muxed))
    concat_raw = VC / f"concat{args.suffix}_raw.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(concat_raw)])

    # 4b. STATIC gain to -16 LUFS + true-peak limiter (NO dynamic loudnorm = NO pumping/clipping).
    #     Single-pass loudnorm rides gain over time ("volume cutting off"); two-pass linear falls
    #     back to dynamic when LRA>target. A constant gain + alimiter is transparent and consistent.
    g = -16.0 - measure_i(concat_raw)
    final = OUT / f"final{args.suffix}.mp4"
    run(["ffmpeg", "-y", "-i", str(concat_raw),
         "-af", f"volume={g:.2f}dB,alimiter=limit=0.794:asc=1",   # 0.794 ≈ -2.0 dBFS ceiling
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final)])
    print(f"DONE -> {final} ({get_dur(final):.2f}s)  static gain {g:+.2f}dB -> -16 LUFS", flush=True)

    # 5. 4:5 + captions
    final45 = OUT / f"final{args.suffix}_4x5.mp4"
    run([".venv/bin/python", "scripts/crop_4x5.py", str(final), "--out", str(final45)])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final),
         "--out", str(OUT / f"final{args.suffix}_hormozi3.mp4")])
    run([".venv/bin/python", "scripts/caption_hormozi3.py", str(final45),
         "--out", str(OUT / f"final{args.suffix}_4x5_hormozi3.mp4"), "--vertical-pos", "0.80"])
    print(f"DONE -> {OUT}/final{args.suffix}_hormozi3.mp4 + 4x5", flush=True)


if __name__ == "__main__":
    main()
