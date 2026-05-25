"""Ad 3 — unify all 3 clips to one voice via ElevenLabs voice_changer.

Clip 3's timbre drifted from clips 1/2. Fix: clone the voice from clip 1+2
audio (the reference), run all 3 trimmed clips' audio through voice_changer
to that voice, loudnorm, mux back onto video, re-concat.

Inputs: outputs/illinois_jdc_stillout_p02/trimmed/clip{1,2,3}.mp4
Output: outputs/illinois_jdc_stillout_p02/final_vc.mp4
        (+ final_vc_4x5.mp4)
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from elevenlabs_client import clone_voice, voice_changer

OUT_DIR = Path("outputs/illinois_jdc_stillout_p02")
TRIM_DIR = OUT_DIR / "trimmed"
VC_DIR = OUT_DIR / "vc"
VC_DIR.mkdir(parents=True, exist_ok=True)
VOICE_ID_CACHE = OUT_DIR / "voice_id.txt"
FINAL_VC = OUT_DIR / "final_vc.mp4"
FINAL_VC_4X5 = OUT_DIR / "final_vc_4x5.mp4"

CLIPS = ["clip1", "clip2", "clip3"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERR: {' '.join(cmd[:3])}… {r.stderr[-300:]}", flush=True)
    return r.returncode == 0


def get_dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    # 1. Extract each clip's audio
    print("=== EXTRACT AUDIO ===", flush=True)
    for c in CLIPS:
        run(["ffmpeg", "-y", "-i", str(TRIM_DIR / f"{c}.mp4"), "-vn", "-ar", "44100",
             "-ac", "1", str(VC_DIR / f"{c}_orig.mp3")])

    # 2. Clone voice from clip1+clip2 (richer ~9s source than a single short clip)
    if VOICE_ID_CACHE.exists():
        voice_id = VOICE_ID_CACHE.read_text().strip()
        print(f"Using cached voice_id: {voice_id}", flush=True)
    else:
        print("=== CLONE VOICE (from clip1+clip2) ===", flush=True)
        # concat clip1+clip2 audio for the clone sample
        cat_list = VC_DIR / "clone_src_list.txt"
        cat_list.write_text(
            f"file '{(VC_DIR / 'clip1_orig.mp3').absolute()}'\n"
            f"file '{(VC_DIR / 'clip2_orig.mp3').absolute()}'\n"
        )
        clone_src = VC_DIR / "clone_src.mp3"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cat_list),
             "-c", "copy", str(clone_src)])
        voice_id = clone_voice("jdc_stillout_p02", [str(clone_src)])
        VOICE_ID_CACHE.write_text(voice_id)
        print(f"voice_id: {voice_id}", flush=True)

    # 3. voice_changer each clip
    print("=== VOICE CHANGER ===", flush=True)
    for c in CLIPS:
        voice_changer(
            str(VC_DIR / f"{c}_orig.mp3"), voice_id, str(VC_DIR / f"{c}_vc.mp3"),
            model_id="eleven_multilingual_sts_v2", stability=0.5, similarity_boost=0.85,
        )
        print(f"  [{c}] voice-changed", flush=True)

    # 4. loudnorm each + 5. mux back onto video
    print("=== LOUDNORM + MUX ===", flush=True)
    muxed = []
    for c in CLIPS:
        norm = VC_DIR / f"{c}_vc_norm.mp3"
        run(["ffmpeg", "-y", "-i", str(VC_DIR / f"{c}_vc.mp3"),
             "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", str(norm)])
        out = VC_DIR / f"{c}.mp4"
        run(["ffmpeg", "-y", "-i", str(TRIM_DIR / f"{c}.mp4"), "-i", str(norm),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out)])
        muxed.append(out)
        print(f"  [{c}] muxed → {get_dur(out):.2f}s", flush=True)

    # 6. concat
    print("=== CONCAT ===", flush=True)
    cl = VC_DIR / "concat.txt"
    cl.write_text("".join(f"file '{p.absolute()}'\n" for p in muxed))
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cl),
         "-c:v", "libx264", "-preset", "fast", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", str(FINAL_VC)])
    print(f"DONE → {FINAL_VC} ({get_dur(FINAL_VC):.2f}s)", flush=True)

    # 7. 4:5
    r = subprocess.run([".venv/bin/python", "scripts/crop_4x5.py", str(FINAL_VC),
                        "--out", str(FINAL_VC_4X5)], capture_output=True, text=True)
    print(f"DONE → {FINAL_VC_4X5}" if r.returncode == 0 else f"4:5 failed", flush=True)


if __name__ == "__main__":
    main()
