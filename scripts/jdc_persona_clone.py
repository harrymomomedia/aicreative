"""Build ONE clean voice clone per persona, from the CLEANEST clips across all that
persona's ads (ranked by spectral centroid), audio-isolated for maximum clarity.

Cloning from the crispest available speech (not whatever clip1+2 happened to be) is the
root fix for the muffled voice-changer. One clone per persona → every ad of that guy matches.

Caches voice_id to outputs/persona_voices/<persona>.txt (reused by jdc_finalize_v2 --voice-id).
"""
import subprocess
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import elevenlabs_client as ec

# cleanest 3 clips per persona (by spectral-centroid ranking, all 8s)
CLEAN = {
    "p1_young":      ["youwereakid_p01/clip3", "statshock_p01/clip4", "keptquiet_p01/clip3"],
    "p2_guarded":    ["stopscroll_p02/clip1",  "memorytrigger_p02/clip4", "stopscroll_p02/clip2"],
    "p3_reflective": ["secret_p03/clip2",      "confession_p03/clip5",  "confession_p03/clip1"],
}
VOICE_DIR = Path("outputs/persona_voices")
VOICE_DIR.mkdir(parents=True, exist_ok=True)


def isolate(infile, outfile):
    with open(infile, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/audio-isolation",
                          headers={"xi-api-key": ec.API_KEY},
                          files={"audio": (Path(infile).name, f, "audio/mpeg")})
    if not r.ok:
        print(f"    isolation failed ({r.status_code}) for {infile} — using raw", flush=True)
        return False
    open(outfile, "wb").write(r.content)
    return True


def main():
    for pname, clips in CLEAN.items():
        cache = VOICE_DIR / f"{pname}.txt"
        if cache.exists():
            print(f"{pname}: cached {cache.read_text().strip()}", flush=True)
            continue
        work = VOICE_DIR / pname
        work.mkdir(exist_ok=True)
        parts = []
        for cl in clips:
            slug, ci = cl.split("/")
            a = work / f"{slug}_{ci}.mp3"
            subprocess.run(["ffmpeg", "-y", "-i", f"outputs/illinois_jdc_{slug}/{ci}.mp4",
                            "-vn", "-ar", "44100", "-ac", "1", str(a)], capture_output=True)
            iso = work / f"{slug}_{ci}_iso.mp3"
            parts.append(iso if isolate(a, iso) else a)
        lst = work / "clone_list.txt"
        lst.write_text("".join(f"file '{p.absolute()}'\n" for p in parts))
        src = work / "clone_src.mp3"
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(src)], capture_output=True)
        vid = ec.clone_voice(f"jdc_{pname}_clean", [str(src)])
        cache.write_text(vid)
        print(f"{pname}: voice_id {vid}  (from {clips})", flush=True)


if __name__ == "__main__":
    main()
