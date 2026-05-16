"""IL JDC power-dynamics b-roll pool (20 clips) via useapi.net Seedance 2.0.

Brief: power-over / access / surveillance imagery that LINKS to sexual abuse
without depicting it — the kind of B-roll that runs over an investigative
news segment about juvenile facility abuse. Black teen detainees, IL JDC
setting users can relate to. Variety across 4 thematic categories.

Specs: 480p / 9:16 / 4s / t2v / audio on / Seedance 2.0 / useapi.net explore mode.
Concurrency: 2 (useapi rate limit + user request).
Outputs: outputs/illinois_jdc_power_broll/{slug}.mp4
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from useapi_client import generate_seedance, download

OUT_DIR = Path("outputs/illinois_jdc_power_broll")
OUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE = (
    " Photoreal observational realism — reads like leaked corrections facility footage, "
    "CCTV, or a Frontline investigative documentary segment. No stylization. "
    "Painted cinderblock walls with chipped institutional paint, scuffed polished concrete floors, "
    "cold blue-white fluorescent overhead light, faded orange detention jumpsuits with visible wear. "
    "Natural light only, no movie key or fill. "
    "ABSOLUTELY NO on-screen text, NO captions, NO watermarks."
)

PROMPTS = {
    # ─── A. Isolation & private access ───────────────────────────────────
    "01_doorway_silhouette_night": (
        "Locked-off observational medium shot from inside a juvenile detention cell at night. "
        "The cell is dark, lit only by red emergency exit light bleeding under the door and a thin "
        "shaft of bluish fluorescent light from the open doorway. A Black teenage boy, around 15, "
        "lies on his bunk in a faded orange jumpsuit, eyes open, looking toward the doorway. The "
        "full silhouette of a large adult male guard fills the doorway, motionless, watching. The "
        "guard does not enter, does not leave. Slight handheld micro-shake. "
        "Atmosphere: watched, unsafe." + STYLE
    ),
    "02_escort_hand_lower_back": (
        "Observational handheld tracking shot from behind, following a uniformed adult male guard "
        "escorting a Black teenage boy, around 14, in a faded orange jumpsuit down a long empty "
        "fluorescent-lit corridor at night. The guard's right hand rests low on the boy's back, "
        "not on his upper arm or shoulder. The boy walks slowly, head slightly down. Footsteps "
        "echo in the empty hall. Camera follows about 4 meters back, natural micro-shake. "
        "Atmosphere: too familiar, off." + STYLE
    ),
    "03_peephole_observation": (
        "Extreme close-up of an adult man's eye looking through a small reinforced wire-glass "
        "observation window in a heavy painted metal cell door. Faint reflection of the dim "
        "interior visible in his pupil — a small figure on a bunk. The eye is still, watching for "
        "several seconds, does not blink. Subtle handheld micro-shake. Cool blue fluorescent "
        "corridor light on the side of his face. "
        "Atmosphere: surveilled, observed." + STYLE
    ),
    "04_office_door_closes": (
        "Locked-off observational medium-wide shot down a juvenile detention administrative corridor "
        "at night. A uniformed adult guard leads a Black teenage boy, around 15, in a faded orange "
        "jumpsuit into a windowless side office. The boy steps inside hesitantly; the guard follows "
        "behind him and pulls the heavy door shut from inside. The latch clicks. The corridor "
        "returns to empty stillness, fluorescent light buzzing. Camera does not move. "
        "Atmosphere: behind closed doors." + STYLE
    ),
    "05_bunk_edge_lean_in": (
        "Observational static medium shot inside a closed juvenile detention cell at night, low "
        "ambient light. A uniformed adult male guard, white, in his 40s, sits on the edge of the "
        "lower metal bunk where a Black teenage boy, around 14, lies on his back in a faded orange "
        "jumpsuit. The guard leans down and forward, face close to the boy's, speaking quietly. The "
        "boy lies still, eyes open, looking up. The cell door is closed. Cold blue light from a "
        "caged ceiling bulb above. "
        "Atmosphere: trapped, no exit." + STYLE
    ),

    # ─── B. Body / search / shower ───────────────────────────────────────
    "06_pat_down_wall": (
        "Observational handheld medium-wide shot in a fluorescent-lit juvenile detention corridor. "
        "A Black teenage boy, around 15, stands facing a painted cinderblock wall, palms flat on the "
        "wall at shoulder height, feet spread. A uniformed adult guard stands close behind him "
        "conducting a thorough pat-down — hands moving down the boy's sides, down the outside of his "
        "legs. The boy's jaw is clenched, eyes closed. Slight camera handheld shake. "
        "Atmosphere: routine, dehumanizing." + STYLE
    ),
    "07_empty_cell_strip_clothing": (
        "Locked-off observational wide shot inside an empty juvenile detention solitary cell, open "
        "door, fluorescent corridor light spilling in. A pile of clothing on the polished concrete "
        "floor — a faded orange jumpsuit twisted inside-out, plain white briefs on top, a pair of "
        "canvas slip-on shoes kicked aside. The thin mattress on the metal bunk is undisturbed. No "
        "one in frame. Camera does not move. "
        "Atmosphere: aftermath, absence." + STYLE
    ),
    "08_shower_door_steam": (
        "Observational handheld medium shot of a closed shower-room door in a juvenile detention "
        "corridor. Heavy painted metal door with a small peephole, paint chipped at the bottom. A "
        "single pair of canvas slip-on shoes sits neatly outside the door. Steam drifts slowly out "
        "from under the door. Distant water sound implied. No one else in the corridor. Slight "
        "camera micro-shake. "
        "Atmosphere: privacy, vulnerability." + STYLE
    ),
    "09_post_shower_towel_walk": (
        "Observational handheld tracking shot down a juvenile detention corridor. A Black teenage "
        "boy, around 14, walks barefoot away from the camera back toward his cell, wrapped from the "
        "waist down in a thin white state-issued towel, upper back wet, water dripping from his "
        "short hair, shoulders hunched. At the far end of the corridor a uniformed adult guard "
        "stands in an open cell doorway, watching him approach. Camera tracks slowly behind. Cold "
        "fluorescent overhead light. "
        "Atmosphere: exposed, watched." + STYLE
    ),
    "10_bloodied_jumpsuit_laundry": (
        "Locked-off observational close-up of an industrial laundry cart in a juvenile detention "
        "service corridor. The cart is piled high with worn faded orange detention jumpsuits, "
        "sleeves and pant legs tangled. Near the top of the pile, one jumpsuit has a dark dried "
        "stain on the inside thigh area. Cold overhead fluorescent light. Slight micro-shake. "
        "Atmosphere: evidence in plain sight." + STYLE
    ),

    # ─── C. Surveillance, conspiracy, paper trail ────────────────────────
    "11_cctv_wall_two_figures": (
        "Observational static medium-wide shot of a juvenile detention security monitoring wall. "
        "Eight small grainy black-and-white CCTV feeds arranged in a 4-by-2 grid on a CRT-style "
        "monitor wall, each showing a different cell or corridor — most show single Black teenage "
        "boys sleeping or sitting alone. One feed in the middle shows two figures inside a cell — "
        "one adult-sized standing, one teen-sized seated on a bunk. Subtle scan-line flicker on the "
        "monitors. Cool blue ambient light. Camera locked-off. "
        "Atmosphere: surveillance fails, anyway." + STYLE
    ),
    "12_yard_corner_whisper": (
        "Observational telephoto-look handheld wide shot of a juvenile detention outdoor rec yard, "
        "late afternoon overcast. In the foreground, a group of Black teenage boys in orange "
        "jumpsuits stand near a basketball court. In the far corner of the yard, separated from the "
        "group, a single Black teenage boy stands close to a uniformed adult male guard against the "
        "cinderblock perimeter wall. The guard's hand rests on the boy's shoulder; he leans in to "
        "speak quietly. The boy looks down at the cracked concrete. "
        "Atmosphere: isolated within a crowd." + STYLE
    ),
    "13_stairwell_two_guards": (
        "Observational handheld medium shot inside a concrete juvenile detention stairwell. Two "
        "uniformed adult male guards stand close together on a landing, whispering. One has his "
        "hand on the other's forearm. Mid-conversation, both heads turn sharply toward the camera "
        "as if they have just heard a sound, eyes alert and wary. Cold fluorescent ceiling light, "
        "painted concrete walls, exposed pipes. Camera handheld with natural shake. "
        "Atmosphere: caught." + STYLE
    ),
    "14_logbook_late_hours": (
        "Locked-off observational overhead close-up of an open juvenile detention cell-check "
        "logbook on a counter, lit by a single desk lamp. Pages filled with handwritten entries in "
        "blue ballpoint pen. Visible time stamps in a single column: 23:00, 23:30, 00:00, 00:30, "
        "01:00, 01:30, 02:00, 02:30, 03:00 — each line initialed with the same set of initials. "
        "Cell number column shows the same cell number repeated. Subtle camera micro-shake. "
        "Atmosphere: pattern, evidence." + STYLE
    ),
    "15_personnel_file_open": (
        "Locked-off observational close-up of an open manila juvenile file folder on a wooden "
        "office desk. A 4-by-6 color photograph of a Black teenage boy, around 14, is paper-clipped "
        "to the inside cover — an intake portrait, the boy holds a small information board with his "
        "name redacted. Beneath, typed pages with sentences highlighted in yellow marker, several "
        "with handwritten notes in the margins. A coffee mug ring stains one corner. Warm desk-lamp "
        "light, cinderblock office wall blurred in background. "
        "Atmosphere: targeted, marked." + STYLE
    ),

    # ─── D. Aftermath / news-doc B-roll ──────────────────────────────────
    "16_untouched_food_tray": (
        "Observational static medium shot inside a juvenile detention cell. A Black teenage boy, "
        "around 14, sits on the edge of the lower metal bunk in a faded orange jumpsuit, hands "
        "clasped between his knees, staring down at the concrete floor. Beside him on the bunk is a "
        "plastic meal tray — rectangular compartments holding mashed potatoes, gray meat, green "
        "beans — completely untouched. His hands tremble slightly. He does not move. Cold "
        "fluorescent overhead light, painted cinderblock walls. "
        "Atmosphere: shutdown, withdrawn." + STYLE
    ),
    "17_solitary_silent_cry": (
        "Observational static medium shot inside a small concrete solitary confinement cell, viewed "
        "through the small reinforced wire-glass observation window in the closed door. Through the "
        "slightly distorted glass: a Black teenage boy, around 13, sits on the concrete floor "
        "against the back wall, knees pulled to his chest, head buried in his folded arms. His "
        "shoulders shake silently. No one approaches the door. Dim greenish-amber bulb above him in "
        "a wire cage. Subtle camera micro-shake. "
        "Atmosphere: alone, unheard." + STYLE
    ),
    "18_jdc_exterior_night": (
        "Observational locked-off wide exterior shot of a 1970s-era concrete-and-brick Illinois "
        "juvenile detention facility at night. Tall chain-link perimeter fence topped with razor "
        "wire in the foreground, sodium-vapor parking-lot lights casting orange pools on cracked "
        "asphalt. The building is mostly dark — only one small barred cell window, third floor, has "
        "its light on, glowing pale yellow. A faded state seal sign reads 'ILLINOIS DEPARTMENT OF "
        "JUVENILE JUSTICE' beside the entrance. No people, no movement. "
        "Atmosphere: institutional silence." + STYLE
    ),
    "19_empty_corridor_flicker": (
        "Observational locked-off wide shot down a long empty juvenile detention corridor at "
        "change-of-shift, deep one-point perspective. Heavy painted cell doors line both walls into "
        "the distance. A single fluorescent tube halfway down the corridor flickers visibly, "
        "casting unstable shadows. Polished concrete floor catches the flickering light. No one in "
        "frame. A faint distant door slam echoes. Slight handheld micro-shake. "
        "Atmosphere: in-between hours, no oversight." + STYLE
    ),
    "20_redacted_court_docs": (
        "Observational locked-off overhead close-up of a wooden judge's desk. A stack of legal "
        "documents fanned across it — top page reads 'COMPLAINT' in bold, with rows of "
        "black-redacted lines beneath, 'PLAINTIFF: [REDACTED], a minor' visible. A heavy wooden "
        "judge's gavel rests beside the stack. A pair of reading glasses folded on top. Warm soft "
        "desk-lamp light from upper right. Subtle camera micro-shake. "
        "Atmosphere: documented, on the record." + STYLE
    ),
}


def gen(slug, prompt):
    out = OUT_DIR / f"{slug}.mp4"
    if out.exists():
        return slug, "exists", str(out)
    print(f"[{slug}] submitting...", flush=True)
    try:
        r = generate_seedance(
            prompt=prompt,
            duration=4,
            aspect_ratio="9:16",
            resolution="480p",
            audio=True,
        )
    except Exception as e:
        return slug, "exception", str(e)[:400]
    if r["status"] != "success" or not r["urls"]:
        return slug, "failed", str(r.get("raw"))[:400]
    download(r["urls"][0], str(out))
    return slug, "success", str(out)


def main():
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = {ex.submit(gen, s, p): s for s, p in PROMPTS.items()}
        for f in as_completed(futures):
            s = futures[f]
            try:
                _, status, info = f.result()
                results[s] = (status, info)
                print(f"[{s}] {status}: {info}", flush=True)
            except Exception as e:
                results[s] = ("EXC", str(e))
                print(f"[{s}] EXC: {e}", flush=True)

    print("\n=== SUMMARY ===")
    ok = [s for s, (st, _) in results.items() if st in ("success", "exists")]
    bad = [s for s, (st, _) in results.items() if st not in ("success", "exists")]
    print(f"  ok:   {len(ok)}/{len(PROMPTS)}")
    print(f"  bad:  {len(bad)}")
    for s in bad:
        print(f"    [{s}] {results[s][0]}: {results[s][1][:200]}")


if __name__ == "__main__":
    main()
