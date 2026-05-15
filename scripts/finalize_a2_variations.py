"""End-to-end finalize pipeline for the 12 a2-persona Chowchilla script variations.

Per variation:
  1. Whisper-transcribe each clip → save transcript JSON next to clip
  2. Compare transcript vs intended → print PASS/FAIL summary
  3. Trim leading/trailing silence per clip via scripts/trim_silence.py
     → produces clip{N}_trimmed.mp4
  4. Concat-demuxer stitch all trimmed clips → variation_raw.mp4
  5. Apply drawbox over bottom-right Veo watermark area → final.mp4
  6. (optional) Audio normalize via ElevenLabs voice_changer per clip → re-mux

CLI:
  --variation V2 [V4 ...] | all
  --skip-qa                 # don't print QA report
  --skip-trim               # don't trim silence
  --no-watermark-cover      # don't draw black box over watermark
  --normalize               # run ElevenLabs voice_changer pass (slow)
  --voice-id <id>           # override voice for normalization
  --voice-source <path>     # source mp3 to clone voice from (default: 0502 audio)
"""
import argparse, json, subprocess, sys, pathlib, warnings, time
warnings.filterwarnings("ignore")
sys.path.insert(0, "/Users/harry/aicreative")
from scripts.chowchilla_a2_variations import VARIATIONS
from elevenlabs_client import scribe_whisper_compat

# Per-campaign proper nouns to bias toward in Scribe
BIASED_KEYWORDS = ["Chowchilla:3.0", "Miha:2.5", "CCWF:2.0"]

BASE = pathlib.Path("/Users/harry/aicreative/outputs/0502_a2_variations")
SOURCE_VIDEO = pathlib.Path("/Users/harry/Desktop/final_a2_vc_ad copy.mp4")

# Watermark cover: paint a black rounded-corner box over bottom-right ~140x80 area
WATERMARK_DRAWBOX = "drawbox=x=iw-160:y=ih-90:w=160:h=90:color=black:t=fill"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ffmpeg(args, label="ffmpeg"):
    r = subprocess.run(["ffmpeg", "-y", *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{label} failed:\n{r.stderr[-2000:]}")


def normalize_text(s):
    """Normalize for transcript comparison: lowercase, strip punctuation/whitespace."""
    import re
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def transcribe_clip(model, clip_path, transcript_path):
    """Transcribe via ElevenLabs Scribe (with biased keywords). Cache to JSON.

    `model` argument is unused (kept for signature compatibility — Scribe is
    stateless per-call). Returns Whisper-compatible shape so trim_silence.py works.
    """
    if transcript_path.exists():
        return json.loads(transcript_path.read_text())
    r = scribe_whisper_compat(str(clip_path), biased_keywords=BIASED_KEYWORDS,
                              language_code="en")
    transcript_path.write_text(json.dumps(r, indent=2, default=str))
    return r


def qa_variation(model, v):
    """Whisper-QA each clip in variation. Returns list of dicts."""
    chunks = VARIATIONS[v]["clips"]
    results = []
    for i, intended in enumerate(chunks, start=1):
        clip = BASE / v / f"clip{i}_poyo.mp4"
        if not clip.exists():
            results.append({"clip": i, "status": "MISSING", "intended": intended, "actual": ""})
            continue
        tx = BASE / v / f"clip{i}_transcript.json"
        result = transcribe_clip(model, clip, tx)
        actual = result["text"].strip()
        match = normalize_text(actual) == normalize_text(intended)
        # Soft-match: actual contains all words of intended (in order, possibly with extras)
        # Treat as PASS if actual contains every word of intended
        intended_words = normalize_text(intended).split()
        actual_words = normalize_text(actual).split()
        # Simple subsequence check
        j = 0
        for w in actual_words:
            if j < len(intended_words) and w == intended_words[j]:
                j += 1
        soft_pass = j == len(intended_words)
        status = "PASS" if match else ("SOFT" if soft_pass else "FAIL")
        results.append({"clip": i, "status": status, "intended": intended, "actual": actual})
    return results


def trim_silence_clip(v, clip_idx):
    """Run scripts/trim_silence.py with the cached transcript. Output clip{N}_poyo_trimmed.mp4."""
    clip = BASE / v / f"clip{clip_idx}_poyo.mp4"
    transcript = BASE / v / f"clip{clip_idx}_transcript.json"
    # trim_silence.py default output: <stem>_trimmed<suffix>
    trimmed = BASE / v / f"clip{clip_idx}_poyo_trimmed.mp4"
    if trimmed.exists():
        return trimmed
    if not transcript.exists():
        raise RuntimeError(f"No transcript for {v} clip {clip_idx}; run QA first")
    r = run([".venv/bin/python", "scripts/trim_silence.py", str(clip), str(transcript)],
            cwd="/Users/harry/aicreative")
    if r.returncode != 0:
        raise RuntimeError(f"trim_silence failed for {v} clip {clip_idx}:\n{r.stderr[-1000:]}")
    if not trimmed.exists():
        raise RuntimeError(f"trim_silence didn't produce {trimmed}")
    return trimmed


def stitch_concat(clip_paths, out_path):
    """Lossless concat via ffmpeg concat demuxer."""
    concat_list = out_path.with_name("concat.txt")
    concat_list.write_text("\n".join(f"file '{p.resolve()}'" for p in clip_paths))
    ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(out_path)],
           label="concat")
    concat_list.unlink(missing_ok=True)
    return out_path


def cover_watermark(in_path, out_path):
    """Re-encode with drawbox over bottom-right watermark area."""
    ffmpeg(["-i", str(in_path), "-vf", WATERMARK_DRAWBOX,
            "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "copy", str(out_path)],
           label="drawbox")
    return out_path


def finalize_one(v, *, do_qa=True, do_trim=True, do_cover=True):
    print(f"\n=== {v} ===", flush=True)
    out_dir = BASE / v

    if do_qa:
        print(f"  [QA] Scribe-transcribing {len(VARIATIONS[v]['clips'])} clips", flush=True)
        # _MODEL kept as a no-op placeholder for signature compatibility
        global _MODEL
        _MODEL = None
        results = qa_variation(_MODEL, v)
        n_pass = sum(1 for r in results if r["status"] in ("PASS", "SOFT"))
        n_fail = sum(1 for r in results if r["status"] == "FAIL")
        n_missing = sum(1 for r in results if r["status"] == "MISSING")
        print(f"  [QA] {n_pass} pass/soft, {n_fail} fail, {n_missing} missing", flush=True)
        for r in results:
            if r["status"] not in ("PASS",):
                print(f"    [{r['status']}] clip {r['clip']}: intended={r['intended']!r}\n"
                      f"             actual={r['actual']!r}", flush=True)
        if n_missing > 0:
            print(f"  ABORT: {n_missing} clips missing for {v}; re-roll then re-run", flush=True)
            return None

    n_clips = len(VARIATIONS[v]["clips"])

    if do_trim:
        print(f"  [TRIM] silence-trimming clips", flush=True)
        trimmed = [trim_silence_clip(v, i) for i in range(1, n_clips + 1)]
    else:
        trimmed = [out_dir / f"clip{i}_poyo.mp4" for i in range(1, n_clips + 1)]

    print(f"  [STITCH] concat {len(trimmed)} clips", flush=True)
    raw = out_dir / f"{v}_raw.mp4"
    stitch_concat(trimmed, raw)

    if do_cover:
        print(f"  [WATERMARK] cover bottom-right", flush=True)
        final = out_dir / f"{v}_final.mp4"
        cover_watermark(raw, final)
    else:
        final = out_dir / f"{v}_final_uncovered.mp4"
        raw.rename(final)

    # Probe final
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(final)])
    dur = float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0
    print(f"  → {final} ({dur:.2f}s)", flush=True)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variation", nargs="+", required=True)
    ap.add_argument("--skip-qa", action="store_true")
    ap.add_argument("--skip-trim", action="store_true")
    ap.add_argument("--no-watermark-cover", action="store_true")
    args = ap.parse_args()

    variations = list(VARIATIONS.keys()) if args.variation == ["all"] else args.variation
    for v in variations:
        if v not in VARIATIONS:
            raise SystemExit(f"unknown variation: {v}")

    finals = []
    for v in variations:
        try:
            f = finalize_one(v, do_qa=not args.skip_qa, do_trim=not args.skip_trim,
                              do_cover=not args.no_watermark_cover)
            if f:
                finals.append(f)
        except Exception as e:
            print(f"  ✗ {v}: {e}", flush=True)
    print(f"\n=== FINISHED: {len(finals)}/{len(variations)} variations ===", flush=True)
    for f in finals:
        print(f"  {f}", flush=True)


if __name__ == "__main__":
    _MODEL = None
    main()
