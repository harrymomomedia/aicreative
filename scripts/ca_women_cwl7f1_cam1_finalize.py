"""
CA Women CWL7_F1 — 'Chest Tightening' finalize:
  word-aware trim → stitch → static loudnorm → watermark crop (9:16)
Persona: CWL7_F1_cam_v2_3 — Mexican-American 52, Central Valley, indoor kitchen selfie
No voice_changer (single-persona — raw Veo audio kept per CLAUDE.md rule)
"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

OUT  = Path("outputs/ca_women_cwl7f1_cam1")
DISC = Path("outputs")   # dissect outputs land at outputs/ca_women_cwl7f1_cam1_clip{n}/

# ── intended dialogue per clip (for word-aware trailing trim) ─────────────────
INTENDED = {
    1: "there are women who did time in california womens prisons",
    2: "women who cant walk past a corrections officer without their chest tightening",
    3: "if staff sexually abused you in there and thats still with you theres a compensation claim you may qualify for right now",
    4: "chowchilla valley state folsom and ciw the law has caught up to what happened behind those walls",
    5: "women who stayed quiet women who reported and were ignored women who thought their chance was gone",
    6: "hundreds have already come forward your memory alone is enough to check",
    7: "free completely private no one in your life finds out you looked tap below",
}

# ── special overrides: set if dissect reveals a trailing improv that needs exact cut ──
CLIP_TRIM_END = {
    3: 7.92,   # trailing "So-" at 7.94s after intended "now." (7.90s end)
}


def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{label or cmd[0]} failed:\n{r.stderr[-1000:]}")
    return r


def tokens(s):
    import re
    s = re.sub(r"'", "", s)
    return re.sub(r"[^\w\s]", " ", s.lower()).split()


def word_trim(n):
    clip    = OUT / f"clip{n}.mp4"
    tx_path = DISC / f"ca_women_cwl7f1_cam1_clip{n}" / "transcript.json"
    out     = OUT / f"clip{n}_trimmed.mp4"

    if out.exists() and out.stat().st_size > 50_000:
        print(f"  clip{n}_trimmed: exists, skipping")
        return out

    tx = json.loads(tx_path.read_text())
    all_words = [w for s in tx.get("segments", []) for w in s.get("words", [])]
    if not all_words:
        import shutil; shutil.copy(clip, out)
        return out

    itoks = tokens(INTENDED[n])
    wtoks = [tokens(w["word"])[0] if tokens(w["word"]) else "" for w in all_words]

    # leading trim: find first intended token
    start_t = all_words[0]["start"]
    for i, wt in enumerate(wtoks):
        if wt == itoks[0]:
            start_t = max(0.0, all_words[i]["start"] - 0.25)
            break

    # trailing trim: use hard override if set, else walk to last intended token
    if n in CLIP_TRIM_END:
        end_t = CLIP_TRIM_END[n]
    else:
        j = 0
        last_end = all_words[-1]["end"]
        for i, wt in enumerate(wtoks):
            if j < len(itoks) and wt == itoks[j]:
                j += 1
                if j == len(itoks):
                    last_end = all_words[i]["end"]
                    break
        end_t = last_end + 0.25

    print(f"  clip{n}: trim {start_t:.2f}s → {end_t:.2f}s")
    run(["ffmpeg", "-y", "-i", str(clip),
         "-ss", str(start_t), "-to", str(end_t),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k",
         str(out)], label=f"trim clip{n}")
    return out


def measure_lufs(path):
    r = run(["ffmpeg", "-y", "-i", str(path),
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
             "-f", "null", "-"], label="measure lufs")
    import re
    m = re.search(r'\{[^}]+\}', r.stderr, re.S)
    if m:
        d = json.loads(m.group())
        return float(d.get("input_i", -23))
    return -23.0


if __name__ == "__main__":
    print("\n[1/4] Word-aware trim")
    trimmed = {}
    for n in range(1, 8):
        try:
            trimmed[n] = word_trim(n)
            print(f"  ✓ clip{n} trimmed")
        except Exception as e:
            print(f"  ✗ clip{n} ERROR: {e}")

    if len(trimmed) < 7:
        print(f"\nERROR: only {len(trimmed)}/7 clips trimmed — aborting")
        sys.exit(1)

    print("\n[2/4] Stitch")
    concat_list = OUT / "concat.txt"
    abs_paths = [str(Path(trimmed[n]).resolve()) for n in sorted(trimmed)]
    concat_list.write_text("\n".join(f"file '{p}'" for p in abs_paths))

    stitched = OUT / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(stitched)], label="stitch")
    print(f"  stitched → {stitched}  ({stitched.stat().st_size // 1024}KB)")

    print("\n[3/4] Static loudnorm (measure → constant gain + limiter)")
    input_lufs = measure_lufs(stitched)
    target_lufs = -16.0
    gain_db = target_lufs - input_lufs
    print(f"  input LUFS: {input_lufs:.1f}  →  gain: {gain_db:+.2f}dB  →  target: {target_lufs}dB")

    loud = OUT / "stitched_loud.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-af", f"volume={gain_db:.2f}dB,alimiter=limit=0.794:level=disabled:asc=1",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         str(loud)], label="static loudnorm + limiter")
    print(f"  normalized → {loud}")

    print("\n[4/4] Crop watermark → 9:16 (720×1200, remove Veo logo at bottom)")
    cropped = OUT / "stitched_916.mp4"
    run(["ffmpeg", "-y", "-i", str(loud),
         "-vf", "crop=720:1200:0:40",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "copy",
         str(cropped)], label="crop 9:16")
    print(f"  cropped → {cropped}  ({cropped.stat().st_size // 1024}KB)")

    print(f"\nDONE → `{cropped}`")
