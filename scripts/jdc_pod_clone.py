"""One clean voice clone per PODCAST HOST, from the crispest clips across that host's videos
(ranked by spectral centroid, audio-isolated). Reused across all that host's videos.
Cache: outputs/podcast_voices/<host>.txt
"""
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import elevenlabs_client as ec

warnings.filterwarnings("ignore")
VDIR = Path("outputs/podcast_voices"); VDIR.mkdir(parents=True, exist_ok=True)

# host -> list of clip mp4s across their videos
HOSTS = {
    "real_06": [f"outputs/jdc_pod_moneyreveal_h06/clip{i}.mp4" for i in (1, 2, 3, 4)]
             + [f"outputs/jdc_pod_familymoney_h06/clip{i}.mp4" for i in (1, 2, 3, 4)],
    "real_07": [f"outputs/jdc_pod_agepower_h07/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
    "real_08": [f"outputs/jdc_pod_cookstat_h08/clip{i}.mp4" for i in (1, 2, 3, 4)]
             + [f"outputs/jdc_pod_barbershop_h08/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
    "real_09": [f"outputs/jdc_pod_theydont_h09/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
    "real_01": [f"outputs/jdc_pod_thousand_h01/clip{i}.mp4" for i in (1, 2, 3, 4)],
    "real_05": [f"outputs/jdc_pod_scalemoney_h05/clip{i}.mp4" for i in (1, 2, 3, 4)],
    "real_11": [f"outputs/jdc_pod_winnerA_h11/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
    "real_14": [f"outputs/jdc_pod_winnerC_h14/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
    "real_15": [f"outputs/jdc_pod_winnerB_h15/clip{i}.mp4" for i in (1, 2, 3, 4, 5)],
}


def centroid(p):
    import librosa
    y, sr = librosa.load(str(p), sr=22050)
    return float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))


def isolate(infile, outfile):
    with open(infile, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/audio-isolation",
                          headers={"xi-api-key": ec.API_KEY},
                          files={"audio": (Path(infile).name, f, "audio/mpeg")})
    if not r.ok:
        return False
    open(outfile, "wb").write(r.content); return True


def main():
    for host, clips in HOSTS.items():
        cache = VDIR / f"{host}.txt"
        if cache.exists():
            print(f"{host}: cached {cache.read_text().strip()}", flush=True); continue
        clips = [c for c in clips if Path(c).exists()]
        work = VDIR / host; work.mkdir(exist_ok=True)
        # rank by centroid, take crispest 3
        scored = []
        for c in clips:
            a = work / (Path(c).parent.name + "_" + Path(c).stem + ".mp3")
            subprocess.run(["ffmpeg", "-y", "-i", c, "-vn", "-ar", "44100", "-ac", "1", str(a)], capture_output=True)
            scored.append((centroid(a), a))
        scored.sort(reverse=True)
        top = [a for _, a in scored[:3]]
        print(f"{host}: cloning from {[p.name for p in top]}", flush=True)
        parts = []
        for a in top:
            iso = a.with_suffix(".iso.mp3")
            parts.append(iso if isolate(a, iso) else a)
        lst = work / "clone_list.txt"
        lst.write_text("".join(f"file '{p.absolute()}'\n" for p in parts))
        src = work / "clone_src.mp3"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(src)], capture_output=True)
        vid = ec.clone_voice(f"jdc_pod_{host}", [str(src)])
        cache.write_text(vid)
        print(f"{host}: voice_id {vid}", flush=True)


if __name__ == "__main__":
    main()
