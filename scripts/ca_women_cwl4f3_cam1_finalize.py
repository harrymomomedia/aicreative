"""
CA Women CWL4_F3 cam1 finalize:
  word-aware trim → voice clone (clip1) → voice_changer → loudnorm → stitch → crop
Persona: CWL4_F3_v1 — Latina 42, Peruvian/Andean, Sacramento apt living room
"""
import json, os, re, subprocess, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))
from elevenlabs_client import clone_voice, voice_changer

OUT = Path("outputs/ca_women_cwl4f3_cam1")
DISSECT = Path("outputs")
VOICE_ID_FILE = OUT / "voice_id.txt"

INTENDED = {
    1: "the fear was never the lawyers it was your husband finding out",
    2: "you never told your kids what happened in there that is the real reason you have scrolled past this ten times",
    3: "not the police your family i get it checking this does not change that",
    4: "there is a lawsuit for women sexually abused by staff inside california womens prisons",
    5: "you may qualify for significant potential compensation without a single person in your life ever finding out you looked",
    6: "there is no public filing no letter in the mail nobody knocks on your door nobody calls your house",
    7: "it is completely private it takes one minute to fill out the form this stays yours tap below",
}


def tokens(s):
    s = re.sub(r"'", "", s)
    return re.sub(r"[^\w\s]", " ", s.lower()).split()


def run(cmd, label=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{label or cmd[0]} failed:\n{r.stderr[-1000:]}")
    return r


def word_trim(n):
    clip = OUT / f"clip{n}.mp4"
    tx_path = DISSECT / f"ca_women_cwl4f3_cam1_clip{n}" / "transcript.json"
    out = OUT / f"clip{n}_trimmed.mp4"

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

    start_t = all_words[0]["start"]
    for i, wt in enumerate(wtoks):
        if wt == itoks[0]:
            start_t = max(0.0, all_words[i]["start"] - 0.30)
            break

    j = 0
    last_end = all_words[-1]["end"]
    for i, wt in enumerate(wtoks):
        if j < len(itoks) and wt == itoks[j]:
            j += 1
            if j == len(itoks):
                last_end = all_words[i]["end"]
                break

    end_t = last_end + 0.3
    print(f"  clip{n}: trim {start_t:.2f}s → {end_t:.2f}s (last word end={last_end:.2f}s)")
    run(["ffmpeg", "-y", "-i", str(clip),
         "-ss", str(start_t), "-to", str(end_t),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", str(out)],
        label=f"trim clip{n}")
    return out


def ensure_stereo(src, dst):
    if Path(dst).exists() and Path(dst).stat().st_size > 50_000:
        return
    run(["ffmpeg", "-y", "-i", str(src),
         "-af", "pan=stereo|c0=c0|c1=c0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)],
        label=f"stereo {src}")


def loudnorm(src, dst):
    if Path(dst).exists() and Path(dst).stat().st_size > 50_000:
        return
    run(["ffmpeg", "-y", "-i", str(src),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(dst)],
        label=f"loudnorm {src}")


if __name__ == "__main__":
    print("\n[1/4] Word-aware trim")
    trimmed = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(word_trim, n): n for n in range(1, 8)}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                trimmed[n] = fut.result()
                print(f"  ✓ clip{n} trimmed")
            except Exception as e:
                print(f"  ✗ clip{n} trim ERROR: {e}")

    print("\n[2/4] Voice clone")
    if VOICE_ID_FILE.exists():
        voice_id = VOICE_ID_FILE.read_text().strip()
        print(f"  reusing voice_id: {voice_id}")
    else:
        audio_src = "/tmp/cwl4f3_voice_src.mp3"
        run(["ffmpeg", "-y", "-i", str(trimmed[1]),
             "-vn", "-ar", "44100", "-ac", "1", audio_src],
            label="extract clip1 audio")
        voice_id = clone_voice("cwl4f3_cam1", [audio_src])
        VOICE_ID_FILE.write_text(voice_id)
        print(f"  cloned voice_id: {voice_id}")

    print("\n[3/4] Voice changer (4 concurrent)")

    def vc_clip(n):
        src_mp4  = trimmed[n]
        vc_audio = OUT / f"clip{n}_vc.mp3"
        vc_mp4   = OUT / f"clip{n}_vc.mp4"
        norm_mp4 = OUT / f"clip{n}_norm.mp4"

        if norm_mp4.exists() and norm_mp4.stat().st_size > 50_000:
            print(f"  clip{n}_norm: exists, skipping")
            return norm_mp4

        audio_in = f"/tmp/cwl4f3_clip{n}_in.mp3"
        run(["ffmpeg", "-y", "-i", str(src_mp4),
             "-vn", "-ar", "44100", "-ac", "1", audio_in],
            label=f"extract clip{n} audio")

        voice_changer(audio_in, voice_id, str(vc_audio),
                      model_id="eleven_multilingual_sts_v2",
                      stability=0.5, similarity_boost=0.85)

        run(["ffmpeg", "-y", "-i", str(src_mp4), "-i", str(vc_audio),
             "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
             str(vc_mp4)],
            label=f"mux clip{n}")

        stereo_mp4 = OUT / f"clip{n}_stereo.mp4"
        ensure_stereo(vc_mp4, stereo_mp4)
        loudnorm(stereo_mp4, norm_mp4)
        print(f"  ✓ clip{n} vc+norm done")
        return norm_mp4

    normed = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(vc_clip, n): n for n in range(1, 8)}
        for fut in as_completed(futs):
            n = futs[fut]
            try:
                normed[n] = fut.result()
            except Exception as e:
                print(f"  ✗ clip{n} vc ERROR: {e}")

    print("\n[4/4] Stitch")
    concat_list = OUT / "concat.txt"
    abs_paths = [str(Path(normed[n]).resolve()) for n in sorted(normed)]
    concat_list.write_text("\n".join(f"file '{p}'" for p in abs_paths))

    stitched = OUT / "stitched.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_list), "-c", "copy", str(stitched)],
        label="stitch")
    print(f"  stitched → {stitched} ({stitched.stat().st_size // 1024}KB)")

    cropped = OUT / "stitched_916.mp4"
    run(["ffmpeg", "-y", "-i", str(stitched),
         "-vf", "crop=720:1200:0:40",
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "copy", str(cropped)],
        label="crop 9:16 letterbox")
    print(f"  cropped 9:16 → {cropped}")
    print(f"\nDONE → {cropped}")
