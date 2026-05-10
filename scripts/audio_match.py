"""Compare each clip's audio profile to a reference clip; flag mismatches.

Detects:
  - voice loudness (RMS during speech)
  - background noise floor (RMS during silence)
  - spectral character (centroid + rolloff — proxies for "mic")
  - high-freq energy (mic quality)

Usage:
  .venv/bin/python scripts/audio_match.py <ref.mp4> <clip2.mp4> <clip3.mp4> ...
  .venv/bin/python scripts/audio_match.py outputs/.../clips_a2/clip1_trimmed.mp4 outputs/.../clips_a2/clip*_trimmed.mp4

Thresholds (tunable via --tol-*):
  voice loudness       ±2 dB
  noise floor          ±4 dB
  spectral centroid    ±20%
  spectral rolloff     ±20%

Each clip gets PASS / WARN / FAIL.
"""
import argparse
import sys
import tempfile
import subprocess
from pathlib import Path
import numpy as np
import librosa


def extract_audio(mp4_path):
    """Extract mono 22050Hz wav via ffmpeg into a temp file. Returns path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp4_path), "-vn", "-ac", "1", "-ar", "22050", tmp.name],
        capture_output=True, check=True,
    )
    return tmp.name


def features(mp4_path):
    """Return dict of audio features."""
    wav = extract_audio(mp4_path)
    y, sr = librosa.load(wav, sr=22050, mono=True)
    Path(wav).unlink()

    # split into non-silent intervals (top_db=25 → 25dB below peak counts as silent)
    intervals = librosa.effects.split(y, top_db=25, frame_length=2048, hop_length=512)
    voice_samples = np.concatenate([y[s:e] for s, e in intervals]) if len(intervals) else y
    if len(voice_samples) == 0:
        voice_samples = y

    # noise floor: samples NOT in any voice interval
    voice_mask = np.zeros(len(y), dtype=bool)
    for s, e in intervals:
        voice_mask[s:e] = True
    noise_samples = y[~voice_mask]
    if len(noise_samples) < sr * 0.1:  # need at least 0.1s
        noise_samples = y[: sr // 10]

    def db(x):
        return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-10)

    voice_db = db(voice_samples)
    noise_db = db(noise_samples)

    # spectral character on voice portions
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=voice_samples, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=voice_samples, sr=sr, roll_percent=0.85)))

    return {
        "voice_db": float(voice_db),
        "noise_db": float(noise_db),
        "centroid_hz": centroid,
        "rolloff_hz": rolloff,
        "duration_s": len(y) / sr,
    }


def compare(ref, target, tol_voice_db, tol_noise_db, tol_centroid_pct, tol_rolloff_pct):
    deltas = {
        "voice_db": target["voice_db"] - ref["voice_db"],
        "noise_db": target["noise_db"] - ref["noise_db"],
        "centroid_pct": (target["centroid_hz"] - ref["centroid_hz"]) / ref["centroid_hz"] * 100,
        "rolloff_pct": (target["rolloff_hz"] - ref["rolloff_hz"]) / ref["rolloff_hz"] * 100,
    }
    fails = []
    if abs(deltas["voice_db"]) > tol_voice_db:
        fails.append(f"voice {deltas['voice_db']:+.1f}dB")
    if abs(deltas["noise_db"]) > tol_noise_db:
        fails.append(f"noise {deltas['noise_db']:+.1f}dB")
    if abs(deltas["centroid_pct"]) > tol_centroid_pct:
        fails.append(f"centroid {deltas['centroid_pct']:+.0f}%")
    if abs(deltas["rolloff_pct"]) > tol_rolloff_pct:
        fails.append(f"rolloff {deltas['rolloff_pct']:+.0f}%")
    verdict = "PASS" if not fails else "FAIL"
    return verdict, deltas, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference", help="reference clip — others compared to this")
    ap.add_argument("clips", nargs="+", help="clips to compare")
    ap.add_argument("--tol-voice-db", type=float, default=2.0)
    ap.add_argument("--tol-noise-db", type=float, default=4.0)
    ap.add_argument("--tol-centroid-pct", type=float, default=20.0)
    ap.add_argument("--tol-rolloff-pct", type=float, default=20.0)
    args = ap.parse_args()

    ref_path = Path(args.reference)
    print(f"REFERENCE: {ref_path.name}")
    ref = features(ref_path)
    print(f"  voice {ref['voice_db']:+.1f}dB  noise {ref['noise_db']:+.1f}dB  "
          f"centroid {ref['centroid_hz']:.0f}Hz  rolloff {ref['rolloff_hz']:.0f}Hz  "
          f"({ref['duration_s']:.1f}s)\n")

    print(f"TOLERANCES: voice ±{args.tol_voice_db}dB  noise ±{args.tol_noise_db}dB  "
          f"centroid ±{args.tol_centroid_pct}%  rolloff ±{args.tol_rolloff_pct}%\n")

    fails_list = []
    for clip in args.clips:
        clip_path = Path(clip)
        if clip_path.resolve() == ref_path.resolve():
            continue  # skip self
        f = features(clip_path)
        verdict, deltas, fails = compare(
            ref, f,
            args.tol_voice_db, args.tol_noise_db,
            args.tol_centroid_pct, args.tol_rolloff_pct,
        )
        marker = "✓" if verdict == "PASS" else "✗"
        detail = " | ".join(fails) if fails else "all within tolerance"
        print(f"  {marker} {clip_path.name:<35} {verdict}  "
              f"voice{deltas['voice_db']:+5.1f}dB  noise{deltas['noise_db']:+5.1f}dB  "
              f"centroid{deltas['centroid_pct']:+5.0f}%  rolloff{deltas['rolloff_pct']:+5.0f}%   "
              f"[{detail}]")
        if verdict == "FAIL":
            fails_list.append(clip_path.name)

    print(f"\n{len(fails_list)} clip(s) flagged for re-roll: {fails_list}")


if __name__ == "__main__":
    main()
