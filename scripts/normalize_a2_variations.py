"""Normalize all 12 a2-persona variations through ElevenLabs voice_changer.

Pipeline:
  1. Clone voice ONCE from the original 0502 source video's audio → voice_id
  2. For each variation, for each clip:
     a. Extract audio from clip{N}_poyo_trimmed.mp4 → tmp .mp3
     b. voice_changer(tmp_audio, voice_id) → normalized .mp3
     c. Re-mux: clip{N}_poyo_trimmed.mp4 video + normalized .mp3 → clip{N}_normalized.mp4
  3. Stitch clip{N}_normalized.mp4 → V{n}_raw_normalized.mp4
  4. Drawbox watermark cover → V{n}_final_normalized.mp4

CLI:
  --variation V2 [V4 ...] | all
  --voice-id <id>             # skip cloning, use existing voice
  --max-workers 8             # parallel voice_changer calls
  --skip-stitch               # only do per-clip normalization, don't stitch
"""
import argparse, json, subprocess, sys, pathlib, tempfile, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, "/Users/harry/aicreative")
from scripts.chowchilla_a2_variations import VARIATIONS
from elevenlabs_client import voice_changer, clone_voice
from scripts.finalize_a2_variations import (
    BASE, stitch_concat, cover_watermark, run, ffmpeg, WATERMARK_DRAWBOX
)

SOURCE_VIDEO = pathlib.Path("/Users/harry/Desktop/final_a2_vc_ad copy.mp4")


def extract_audio_for_clone():
    """Extract source video audio to mp3 (clone source). Cached if exists."""
    out = pathlib.Path("/tmp/a2_source_voice.mp3")
    if out.exists():
        return out
    ffmpeg(["-i", str(SOURCE_VIDEO), "-vn", "-acodec", "libmp3lame", "-b:a", "192k", str(out)],
           label="extract clone source")
    return out


def normalize_clip(clip_path, voice_id, out_path):
    """Per-clip: extract audio → voice_changer → re-mux."""
    if out_path.exists():
        return out_path, "exists"
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        orig_audio = td / "orig.mp3"
        norm_audio = td / "norm.mp3"
        ffmpeg(["-i", str(clip_path), "-vn", "-acodec", "libmp3lame", "-b:a", "192k", str(orig_audio)],
               label=f"extract {clip_path.name}")
        voice_changer(
            str(orig_audio), voice_id, str(norm_audio),
            model_id="eleven_multilingual_sts_v2",
            stability=0.5,
            similarity_boost=0.85,
        )
        ffmpeg([
            "-i", str(clip_path), "-i", str(norm_audio),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", str(out_path),
        ], label=f"mux {out_path.name}")
    return out_path, "normalized"


def normalize_variation(v, voice_id, max_workers=8, do_stitch=True):
    print(f"\n=== {v} ===", flush=True)
    out_dir = BASE / v
    n_clips = len(VARIATIONS[v]["clips"])
    jobs = []
    for i in range(1, n_clips + 1):
        trimmed = out_dir / f"clip{i}_poyo_trimmed.mp4"
        norm = out_dir / f"clip{i}_normalized.mp4"
        if not trimmed.exists():
            print(f"  ✗ clip{i}: trimmed source missing", flush=True)
            continue
        jobs.append((trimmed, norm, i))

    print(f"  [normalize] {len(jobs)} clips × voice_changer (max_workers={max_workers})", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(normalize_clip, t, voice_id, n): i for t, n, i in jobs}
        for f in as_completed(futs):
            i = futs[f]
            try:
                out, status = f.result()
                print(f"    clip{i}: {status} ({out.name})", flush=True)
            except Exception as e:
                print(f"    clip{i} FAILED: {e}", flush=True)
    print(f"  [normalize] {round(time.time()-t0, 1)}s", flush=True)

    if not do_stitch:
        return None

    # Stitch normalized clips
    norms = [out_dir / f"clip{i}_normalized.mp4" for i in range(1, n_clips + 1)
             if (out_dir / f"clip{i}_normalized.mp4").exists()]
    if len(norms) != n_clips:
        print(f"  ✗ {v}: only {len(norms)}/{n_clips} normalized clips — skipping stitch", flush=True)
        return None
    raw = out_dir / f"{v}_raw_normalized.mp4"
    stitch_concat(norms, raw)
    print(f"  [stitch] {raw.name}", flush=True)

    final = out_dir / f"{v}_final_normalized.mp4"
    cover_watermark(raw, final)
    print(f"  [watermark] {final.name}", flush=True)

    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(final)])
    dur = float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else 0
    print(f"  → {final} ({dur:.2f}s)", flush=True)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variation", nargs="+", required=True)
    ap.add_argument("--voice-id", default=None, help="reuse an existing voice_id (skip clone)")
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--skip-stitch", action="store_true")
    args = ap.parse_args()

    variations = list(VARIATIONS.keys()) if args.variation == ["all"] else args.variation

    if args.voice_id:
        voice_id = args.voice_id
        print(f"Using voice_id: {voice_id}", flush=True)
    else:
        print("Cloning voice from 0502 source video audio...", flush=True)
        clone_src = extract_audio_for_clone()
        voice_id = clone_voice("a2_chowchilla_persona", [str(clone_src)])
        print(f"Cloned voice_id: {voice_id}", flush=True)
        # Save for re-use
        pathlib.Path("/tmp/a2_voice_id.txt").write_text(voice_id)

    finals = []
    for v in variations:
        try:
            f = normalize_variation(v, voice_id, max_workers=args.max_workers, do_stitch=not args.skip_stitch)
            if f:
                finals.append(f)
        except Exception as e:
            print(f"  ✗ {v}: {e}", flush=True)

    print(f"\n=== FINISHED: {len(finals)}/{len(variations)} normalized ===", flush=True)
    for f in finals:
        print(f"  {f}", flush=True)


if __name__ == "__main__":
    main()
