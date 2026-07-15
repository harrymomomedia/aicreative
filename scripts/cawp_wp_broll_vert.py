#!/usr/bin/env python3
"""Vertical 9:16 women's-prison b-roll stills — gpt-image-2 (KIE, 2K) — for PIP composites
(persona bg-removed talking over a static prison backdrop + docu zoom + Nick captions).

"Day in the life" of a CA women's prison: guards + inmates in natural institutional settings.
NEWS-DOC realism, NON-EXPLICIT — faces away/obscured (backs, distance, silhouette, hands), NO
abuse act depicted; power imbalance conveyed only through posture/framing (dramatization-safe).
Skip-if-exists.
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kie_client import generate_gpt_image, download as kie_download

OUT = Path("outputs/cawp_broll_wp/vert")
STYLE = (" Vertical 9:16 portrait framing. Photoreal news b-roll cinematography, shot like a 20/20 / "
         "Frontline / PBS documentary segment about a California women's prison. Natural color grading, "
         "real-world lighting (no dramatic Hollywood key-light), slight handheld feel, slight grain. "
         "NOT cinematic, NOT stylized — looks like genuine news investigative footage on an ENG camera. "
         "EVERY correctional officer in frame is MALE — never a female officer. "
         "No on-screen text, no captions, no watermarks, no readable signage.")

SHOTS = {
 "v01_yard_line": "A row of women in light-blue prison scrubs and grey sweatshirts lined up along a chain-link fence in a dusty exercise yard, seen from BEHIND at a distance so no faces are visible, a uniformed MALE correctional officer standing to the side watching them, tall fencing topped with coiled razor wire, flat Central Valley farmland horizon, harsh midday sun.",
 "v02_corridor_escort": "A uniformed correctional officer escorting a woman in light-blue prison scrubs down a long institutional cellblock corridor, BOTH seen from directly behind at a distance so no faces are visible, rows of heavy cell doors, harsh fluorescent tube lighting, polished concrete floor with reflections receding to a far door.",
 "v03_cell_doorway_guard": "Seen from the corridor: a uniformed MALE correctional officer stands filling an open cell doorway looking in, his back to camera, while inside the dim cell a woman in blue scrubs sits on the lower bunk with her head down, her face not visible, tense quiet institutional moment.",
 "v04_count_tier": "Women in light-blue prison scrubs standing at their open cell doors along a two-tier cellblock for a count, all seen from behind or at a distance so no faces are visible, a MALE correctional officer walking the lower tier counting, harsh overhead light, painted steel railings.",
 "v05_chow_line": "Women in light-blue prison scrubs waiting in a single-file line at a steel chow-hall serving counter holding beige meal trays, seen from BEHIND so no faces are visible, a MALE correctional officer supervising from the side, industrial kitchen and fluorescent light behind.",
 "v06_dayroom_watch": "A women's prison dayroom: several women in blue scrubs sitting at bolted steel tables seen from behind and at a distance, a uniformed MALE correctional officer standing watch in the foreground with back partly to camera, cinder-block walls, a wall-mounted TV, flat fluorescent light.",
 "v07_bunk_alone": "A woman in light-blue prison scrubs sitting alone on the edge of a lower bunk seen from behind and slightly to the side so her face is NOT visible, shoulders slumped, hands clasped in her lap, a thin shaft of daylight from a small high barred window, bare cinder-block cell, quiet heavy mood.",
 "v08_guard_over_seated": "Across a women's prison dayroom seen from a distance: a standing uniformed male correctional officer leans down over a woman in blue scrubs who sits hunched alone at a steel table, his posture looming, BOTH faces turned away from camera, an uncomfortable power imbalance conveyed only through body language, muted institutional light.",
 "v09_phone_call": "A woman in light-blue prison scrubs standing at a wall-mounted prison phone bank holding the receiver to her ear, seen from BEHIND, head bowed, one hand against the scuffed cinder-block wall, a row of steel phone cubicles, an officer blurred far down the corridor.",
 "v10_escort_grip": "Vertical close detail: a MALE correctional officer's hand gripping the upper arm of a woman in a light-blue prison uniform during an escort, her hands held in front of her, shallow depth of field, dim institutional corridor blurred behind, NO faces in frame.",
 "v11_night_doorway": "Night in a women's prison dormitory: the dark silhouette of a uniformed MALE correctional officer fills a single lit doorway at the far end, duty belt and radio visible in outline, rows of steel bunk beds in near-darkness in the foreground, a woman's form asleep on a near bunk, ominous quiet, no faces visible.",
 "v12_perimeter_tower": "A concrete prison guard tower rising above a double row of tall chain-link perimeter fencing topped with coiled razor wire, a gravel no-man's strip between the fences, floodlight poles, flat farmland beyond, moody overcast dusk sky, long lens.",
 "v13_intake_counter": "A woman in light-blue prison scrubs standing at a steel intake counter seen from behind, a MALE correctional officer on the far side handling a clear plastic property bag and a stack of folded blue uniforms, harsh overhead light, bare institutional processing room.",
 "v14_yard_wide": "Wide vertical view of a large women's prison exercise yard: dozens of women in light-blue scrubs small and scattered in groups walking and sitting, tall double fencing with razor wire and a guard tower behind, dry Central Valley light, compressed telephoto haze, no faces distinguishable at this distance.",
 "v15_laundry": "Women in light-blue prison scrubs working in a hot institutional prison laundry room, folding sheets and pushing large canvas laundry carts, seen from behind and the side so no faces are visible, a MALE correctional officer standing by the door watching, steam and industrial washers, fluorescent light.",
 "v16_pill_line": "Women in light-blue prison scrubs waiting in a single-file line at a medication pass window in a cinder-block corridor, seen from BEHIND so no faces are visible, a MALE correctional officer standing beside the window, harsh overhead light, painted floor line.",
 "v17_yard_basketball": "A women's prison exercise yard with a weathered basketball hoop, a few women in grey sweatshirts and blue scrubs playing and standing seen from a distance so no faces are visible, a MALE correctional officer watching from the fence line, chain-link and razor wire, harsh afternoon sun.",
 "v18_classroom": "A bare prison classroom or program room: women in light-blue scrubs seated at long tables facing away from camera toward a whiteboard, a MALE correctional officer standing at the back doorway, cinder-block walls, flat fluorescent light, no faces visible.",
 "v19_sally_gate": "A woman in light-blue prison scrubs being escorted by a MALE correctional officer through a heavy rolling steel security gate in a chain-link sally port, BOTH seen from behind at a distance so no faces are visible, razor wire above, harsh midday sun.",
 "v20_dorm_wake": "Early morning in a women's prison dormitory: rows of steel bunk beds, a few women rising and sitting on their bunks seen from behind or in silhouette, a MALE correctional officer standing in the lit doorway at the end, cold grey dawn light through high windows, no faces visible.",
 "v21_wall_search_line": "Several women in light-blue prison scrubs standing facing a cinder-block corridor wall with their hands flat against it waiting to be searched, all seen from BEHIND so no faces are visible, a MALE correctional officer moving down the line, harsh fluorescent light.",
 "v22_visiting_table": "A women's prison visiting room: a woman in light-blue prison scrubs sitting alone at a low round bolted table seen from behind, waiting, vending machines and painted cinder-block walls behind, a MALE correctional officer standing watch by the far door, flat fluorescent light, quiet mood.",
 # --- guard-over-inmate POWER-DYNAMIC series (like v03/v08/v10): proximity/isolation, NON-explicit, faces obscured ---
 "v23_doorway_lean": "A uniformed male correctional officer leaning one hand high against the frame of an open cell doorway, standing close over a woman in light-blue prison scrubs who sits on the lower bunk inside with her head lowered, BOTH seen from the side and behind so no faces are visible, dim cell, empty corridor beyond, tense private power imbalance.",
 "v24_counter_behind": "A uniformed male correctional officer standing close behind a woman in light-blue prison scrubs at a steel counter, his posture crowding her space, both seen from behind so no faces are visible, harsh institutional light, uncomfortable proximity.",
 "v25_shoulder_hand": "A uniformed correctional officer's hand resting on the shoulder of a woman in light-blue prison scrubs who sits hunched on a steel bench, seen from behind and the side so no faces are visible, dim institutional room, unsettling quiet, shallow depth of field.",
 "v26_ear_lean": "A uniformed male correctional officer leaning down to speak close to the ear of a woman in light-blue prison scrubs standing against a cinder-block wall, BOTH faces turned away from camera so neither is visible, empty corridor, intimidating proximity conveyed through posture only.",
 "v27_corner_wall": "A uniformed male correctional officer cornering a woman in light-blue prison scrubs against a cinder-block corridor wall, his forearm braced on the wall beside her head, BOTH seen from behind and the side so no faces are visible, harsh fluorescent light, empty hallway, tense power imbalance.",
 "v28_block_doorway": "A uniformed male correctional officer standing filling a narrow doorway with his back to camera, blocking the way, while inside a small dim room a woman in blue scrubs stands with her arms crossed, her face not visible, no witnesses, tense isolation.",
 "v29_bunk_edge": "A uniformed male correctional officer sitting on the edge of a lower bunk in a dim cell, close beside a woman in light-blue prison scrubs who sits pulled away with her head down, BOTH seen from behind and the side so no faces are visible, cramped private cell, unsettling closeness.",
 "v30_office_alone": "A uniformed male correctional officer and a woman in light-blue prison scrubs alone together in a small institutional office with the door nearly shut, seen through the narrow doorway gap from a distance, both faces turned away so neither is visible, isolated and tense.",
 "v31_belt_foreground": "Foreground: the duty belt, radio and torso of a uniformed male correctional officer standing very close, filling most of the frame; background slightly blurred: a woman in light-blue prison scrubs sitting on a bunk with her head lowered, her face not visible, oppressive proximity, dim cell light.",
 "v32_escort_back": "A uniformed male correctional officer escorting a woman in light-blue prison scrubs down an empty corridor with his hand at her lower back, BOTH seen from directly behind so no faces are visible, harsh fluorescent light, unsettling control.",
 "v33_stand_over_task": "A uniformed male correctional officer standing over a woman in light-blue prison scrubs who kneels doing a cleaning task on the floor of a dim utility room, his posture looming above her, both faces away from camera so not visible, isolated back room, tense power imbalance.",
 "v34_stairwell": "A uniformed male correctional officer and a woman in light-blue prison scrubs alone in a dim concrete institutional stairwell, the officer a step above and standing close, BOTH seen from behind and the side so no faces are visible, isolated, tense, harsh single overhead light.",
}


def gen(slug, prompt):
    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"{slug}.png"
    if dst.exists():
        return f"skip {slug}"
    try:
        res = generate_gpt_image(prompt + STYLE, aspect_ratio="9:16", resolution="2K")
        urls = res.get("urls") or []
        if not urls:
            return f"FAIL {slug}: {res.get('status')} {str(res.get('raw'))[:140]}"
        kie_download(urls[0], str(dst))
        return f"ok {slug}"
    except Exception as e:
        return f"ERR {slug}: {e}"


if __name__ == "__main__":
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    todo = [(s, p) for s, p in SHOTS.items() if (only is None or s in only)]
    with ThreadPoolExecutor(max_workers=5) as ex:
        for f in as_completed([ex.submit(gen, s, p) for s, p in todo]):
            print(f.result(), flush=True)
    print(f"DONE — {len(todo)} shots -> {OUT}", flush=True)
