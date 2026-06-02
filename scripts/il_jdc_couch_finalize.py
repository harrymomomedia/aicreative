"""
IL JDC Couch persona finalize:
  word-aware trim → voice clone (clip1) → voice_changer → loudnorm → stitch
"""
import json, os, re, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from elevenlabs_client import clone_voice, voice_changer

OUT = Path("outputs/il_jdc_couch")
DISSECT = Path("outputs")  # dissect outputs land at outputs/il_jdc_couch_clip{N}/
VOICE_ID_FILE = OUT / "voice_id.txt"

INTENDED = {
    1: "What if I told you Illinois has been settling these cases quietly and most survivors don't even know they're entitled to be part of it",
    2: "If you were in an Illinois juvenile facility as a child and you were abused or neglected",
    3: "Active legal claims are happening right now on behalf of survivors like you",
    4: "If you don't come forward before the deadline you won't be included period",
    5: "Everything is completely confidential and private nobody in your life finds out you did this",
    6: "And the process couldn't be simpler you just fill out a form sixty seconds",
    7: "A legal team reviews it immediately and tells you if you qualify",
    8: "No cost unless they win for you",
    9: "The deadline is real it is not flexible and it is getting closer every single day",
    10: "Tap below right now just fill out the form make sure you don't get left out",
}


def tokens(s):
    return re.sub(r"[^\w\s]", " ", s.lower()).split()


def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{label or cmd[0]} failed:\n{r.stderr[-1000:]}")
    return r


def word_trim(n):
    """Trim clip to span of intended words + pad. Returns trimmed path."""
    clip = OUT / f"clip{n}.mp4"
    tx_path = DISSECT / f"il_jdc_couch_clip{n}" / "transcript.json"
    out = OUT / f"clip{n}_trimmed.mp4"

    if out.exists() and out.stat().st_size > 50_000:
        print(f"  clip{n}_trimmed: exists, skipping")
        return out

    tx = json.loads(tx_path.read_text())
    all_words = [w for s in tx.get("segments", []) for w in s.get("words", [])]
    if not all_words:
        print(f"  clip{n}: no word timings, copying as-is")
        import shutil; shutil.copy(clip, out)
        return out

    itoks = tokens(INTENDED[n])
    wtoks = [tokens(w["word"])[0] if tokens(w["word"]) else "" for w in all_words]

    # find first intended word
    start_t = all_words[0]["start"]
    for i, wt in enumerate(wtoks):
        if wt == itoks[0]:
            start_t = max(0.0, all_words[i]["start"] - 0.05)
            break

    # find last intended word end (subsequence match)
    j = 0
    last_end = all_words[-1]["end"]
    for i, wt in enumerate(wtoks):
        if j < len(itoks) and wt == itoks[j]:
            j += 1
            if j == len(itoks):
                last_end = all_words[i]["end"]
                break

    end_t = last_end + 0.3

    print(f"  clip{n}: trim {start_t:.2f}s → {end_t:.2f}s (last intended word end={last_end:.2f}s)")
    run(["ffmpeg", "-y", "-i", str(clip),
         "-ss", str(start_t), "-to", str(end_t),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", str(out)],
        label=f"trim clip{n}")
    return out


def loudnorm(src, dst):
    if Path(dst).exists() and Path(dst).stat().st_size > 50_000:
        return
    run(["ffmpeg", "-y", "-i", str(src),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)],
        label=f"loudnorm {src}")


def ensure_stereo(src, dst):
    if Path(dst).exists() and Path(dst).stat().st_size > 50_000:
        return
    run(["ffmpeg", "-y", "-i", str(src),
         "-af", "aformat=channel_layouts=stereo",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)],
        label=f"stereo {src}")


if __name__ == "__main__":
    # ── 1. Word-aware trim ──────────────────────────────────────────────────
    print("\n[1/4] Word-aware trim")
    trimmed = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(word_trim, n): n for n in range(1, 11)}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                trimmed[n] = fut.result()
                print(f"  ✓ clip{n} trimmed")
            except Exception as e:
                print(f"  ✗ clip{n} trim ERROR: {e}")

    # ── 2. Clone voice from clip1 ───────────────────────────────────────────
    print("\n[2/4] Voice clone")
    if VOICE_ID_FILE.exists():
        voice_id = VOICE_ID_FILE.read_text().strip()
        print(f"  reusing voice_id: {voice_id}")
    else:
        # extract audio from clip1
        audio_src = "/tmp/couch_voice_src.mp3"
        run(["ffmpeg", "-y", "-i", str(trimmed[1]),
             "-vn", "-ar", "44100", "-ac", "1", audio_src],
            label="extract clip1 audio")
        voice_id = clone_voice("il_jdc_couch", [audio_src])
        VOICE_ID_FILE.write_text(voice_id)
        print(f"  cloned voice_id: {voice_id}")

    # ── 3. Voice changer on all clips ──────────────────────────────────────
    print("\n[3/4] Voice changer (4 concurrent)")

    def vc_clip(n):
        src_mp4 = trimmed[n]
        vc_audio = OUT / f"clip{n}_vc.mp3"
        vc_mp4   = OUT / f"clip{n}_vc.mp4"
        norm_mp4 = OUT / f"clip{n}_norm.mp4"

        if norm_mp4.exists() and norm_mp4.stat().st_size > 50_000:
            print(f"  clip{n}_norm: exists, skipping")
            return norm_mp4

        # extract audio
        audio_in = f"/tmp/couch_clip{n}_in.mp3"
        run(["ffmpeg", "-y", "-i", str(src_mp4),
             "-vn", "-ar", "44100", "-ac", "1", audio_in],
            label=f"extract clip{n} audio")

        # voice changer
        voice_changer(audio_in, voice_id, str(vc_audio),
                      model_id="eleven_multilingual_sts_v2",
                      stability=0.5, similarity_boost=0.85)

        # mux vc audio back into video
        run(["ffmpeg", "-y", "-i", str(src_mp4), "-i", str(vc_audio),
             "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
             str(vc_mp4)],
            label=f"mux clip{n}")

        # ensure stereo then loudnorm
        stereo_mp4 = OUT / f"clip{n}_stereo.mp4"
        ensure_stereo(vc_mp4, stereo_mp4)
        loudnorm(stereo_mp4, norm_mp4)
        print(f"  ✓ clip{n} vc+norm done")
        return norm_mp4

    normed = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(vc_clip, n): n for n in range(1, 11)}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                normed[n] = fut.result()
            except Exception as e:
                print(f"  ✗ clip{n} vc ERROR: {e}")

    # ── 4. Stitch ───────────────────────────────────────────────────────────
    print("\n[4/4] Stitch")
    concat_list = OUT / "concat.txt"
    abs_paths = [str(Path(normed[n]).resolve()) for n in sorted(normed)]
    concat_list.write_text("\n".join(f"file '{p}'" for p in abs_paths))

    stitched = OUT / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(stitched)],
        label="stitch")
    print(f"  stitched → {stitched} ({stitched.stat().st_size // 1024}KB)")

    # crop 4:5
    from scripts.crop_4x5 import crop_4x5
    cropped_916 = OUT / "stitched_cropped.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-vf", "crop=720:1200:0:40",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "copy", str(cropped_916)],
        label="crop 9:16 letterbox")
    print(f"  cropped 9:16 → {cropped_916}")

    print(f"\nDONE → {OUT}/stitched_cropped.mp4")
    print("Next: run caption_hormozi3.py on stitched_cropped.mp4")
