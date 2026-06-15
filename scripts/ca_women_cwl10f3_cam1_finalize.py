"""
CA Women CWL10_F3 — '$115M Settlement' finalize:
  word-aware trim → stitch → static loudnorm → watermark crop (9:16)
Persona: CWL10_F3 — Latina 51, warm medium-dark skin, natural curly hair
No voice_changer (single-persona — raw Veo audio kept per CLAUDE.md rule)
"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

OUT  = Path("outputs/ca_women_cwl10f3_cam1")
DISC = Path("outputs")  # dissect outputs at outputs/ca_women_cwl10f3_cam1_clip{n}/

# ── intended dialogue per clip (written to match Scribe transcription) ──────────
INTENDED = {
    1:  "california just paid over one hundred fifteen million dollars to women who were sexually abused by staff inside womens prisons",
    2:  "and most of the women who qualified had no idea they had a case this isnt a rumor this isnt a maybe",
    3:  "this is public record one of the largest prison sexual abuse settlements in american history",
    4:  "if you were incarcerated at either facility and any employee a correctional officer medical staff kitchen worker contractor or counselor",
    5:  "engaged in sexual contact with you whether through coercion threats to your parole manipulation or force",
    6:  "you may be entitled to significant individual compensation",
    7:  "but that window does not stay open indefinitely if you wait too long you lose your right to compensation permanently",
    8:  "tap the button below right now its a thirty second confidential quiz",
    9:  "no court appearances no cost ever the legal team only gets paid if you get paid",
    10: "your employer your po your family none of them are contacted or notified",
    11: "the state already admitted fault the money is there the only question is whether you claim it before the deadline passes",
}

# ── hard overrides (set from dissect transcript review) ──────────────────────────
CLIP_TRIM_START = {}
CLIP_TRIM_END = {
    # C4: Veo said "are incarcerated" not "were incarcerated" — breaks subsequence.
    #     "counselor," ends at 7.44s → 7.44 + 0.25.
    4: 7.69,
    # C7: "permanently." ends at 7.94s, "Now-" improv starts at 7.96s (0.02s gap).
    #     Must cut before 7.96s.
    7: 7.95,
    # C8: Veo said "30-second" not "thirty second" — breaks subsequence on "thirty".
    #     "quiz." ends at 5.24s → 5.24 + 0.25.
    8: 5.49,
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
    tx_path = DISC / f"ca_women_cwl10f3_cam1_clip{n}" / "transcript.json"
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

    # leading trim
    if n in CLIP_TRIM_START:
        start_t = CLIP_TRIM_START[n]
    else:
        start_t = all_words[0]["start"]
        for i, wt in enumerate(wtoks):
            if wt == itoks[0]:
                start_t = max(0.0, all_words[i]["start"] - 0.25)
                break

    # trailing trim
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
    for n in range(1, 12):
        try:
            trimmed[n] = word_trim(n)
            print(f"  ✓ clip{n} trimmed")
        except Exception as e:
            print(f"  ✗ clip{n} ERROR: {e}")

    if len(trimmed) < 11:
        print(f"\nERROR: only {len(trimmed)}/11 clips trimmed — aborting")
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
