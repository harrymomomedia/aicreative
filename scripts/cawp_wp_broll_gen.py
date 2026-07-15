#!/usr/bin/env python3
"""CAWP women's-prison b-roll stills — gpt-image-2 (KIE, 2K).

News-realistic documentary b-roll of women's-prison life for the stacked format
top-half + AdMachin Women's Prison b-roll library. NO identifiable faces (backs,
silhouettes, hands, distance). No abuse depiction — environment + daily-life only.
Skip-if-exists; re-run to fill holes.
"""
import os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kie_client import generate_gpt_image
import requests

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "outputs", "cawp_broll_wp", "gen")
os.makedirs(OUT, exist_ok=True)

STYLE = (" Photoreal news b-roll cinematography, shot like a 20/20 / Frontline / PBS "
         "documentary segment about a California women's prison. Natural color grading, "
         "real-world lighting (no dramatic Hollywood key-light), slight handheld feel, "
         "slight grain. NOT cinematic, NOT stylized — looks like genuine news investigative "
         "footage shot on a news ENG camera. No on-screen text, no captions, no watermarks, "
         "no readable signage text.")

SHOTS = {
 "wp01_yard_walk": "Several women in light-blue prison scrubs and grey sweatshirts walking across a dusty exercise yard, seen from BEHIND at a distance so no faces are visible, tall chain-link fencing topped with coiled razor wire, flat Central Valley farmland horizon, harsh midday sun.",
 "wp02_razor_wire": "Close-up of coiled razor wire along the top of a tall chain-link prison fence, slightly out-of-focus guard tower in the background, pale dusk sky, cold institutional mood.",
 "wp03_corridor": "Long empty prison corridor with polished concrete floor, rows of heavy cell doors with narrow windows on both sides, harsh fluorescent tube lighting, one flickering light far down the hall.",
 "wp04_cell_bunks": "Interior of a cramped women's prison dorm cell: steel bunk beds with thin green mattresses and folded grey blankets, small high barred window casting a shaft of daylight, personal photos taped to the wall edge, nobody in frame.",
 "wp05_hands_bars": "Close-up of a woman's weathered hands gripping the bars of a cell door, fine-line tattoo on the forearm, chipped nail polish, shallow depth of field, dim corridor light beyond the bars, face not visible.",
 "wp06_dorm_crowded": "Overcrowded women's prison dormitory room with eight steel bunk beds packed close together, plastic storage bins under the bunks, laundry hanging from bed frames, one woman seen from behind sitting on a far bunk, institutional beige walls.",
 "wp07_phone_bank": "A woman in light-blue prison scrubs standing at a wall-mounted prison phone bank, seen from BEHIND, holding the receiver to her ear, head bowed, row of steel phone cubicles, scuffed institutional wall.",
 "wp08_visiting_room": "Empty prison visiting room with rows of low round tables and plastic chairs bolted to the floor, vending machines along the wall, fluorescent lighting, painted cinder-block walls, waiting silence.",
 "wp09_guard_silhouette": "Dark silhouette of a uniformed correctional officer standing at the end of a prison corridor, backlit by harsh light through a doorway, keys and radio on the duty belt visible in outline, face completely in shadow, ominous institutional atmosphere.",
 "wp10_folded_blues": "A stack of folded light-blue prison uniforms and white towels on a steel intake counter, clear plastic property bag beside them, harsh overhead light, shallow depth of field.",
 "wp11_perimeter_dusk": "Long prison perimeter fence line at golden hour, double row of tall chain-link fencing with razor wire, gravel no-man's strip between the fences, floodlight poles, flat farmland beyond, moody dusk sky.",
 "wp12_guard_tower": "Concrete prison guard tower seen from below through chain-link fence, dark tinted windows, pale overcast sky, telephoto compression, grim institutional geometry.",
 "wp13_bunk_sitting": "A woman in light-blue prison scrubs sitting on the edge of a lower bunk seen from behind and slightly to the side so her face is NOT visible, shoulders slumped, hands clasped, thin daylight from a small high window, quiet heavy mood.",
 "wp14_yard_fence_line": "Empty prison exercise yard: cracked asphalt, a weathered basketball hoop with no net, picnic tables, tall fencing with razor wire beyond, low sun casting long shadows, nobody in frame.",
 "wp15_meal_trays": "Steel serving line in a prison chow hall with stacked beige meal trays, sneeze guard reflecting fluorescent light, industrial kitchen equipment blurred behind, no people visible.",
 "wp16_letters_photos": "Close-up of a small stack of handwritten letters and creased family photographs on a thin prison mattress, envelope edges worn soft from handling, dim natural window light, shallow depth of field.",
 "wp17_yard_filefootage": "Long telephoto shot through a chain-link fence of dozens of women in light-blue prison scrubs sitting and standing in groups on a large grass prison yard, heat shimmer, compressed perspective, slightly soft focus like archival news file footage, no faces distinguishable at this distance.",
 "wp18_tower_pond": "A concrete prison guard tower reflected in a still retention pond, seen through bare winter tree branches in the foreground, cold overcast light, muted colors, long lens.",
 "wp19_wire_dusk_silhouette": "Coils of razor wire and chain-link fence in pure black silhouette against a slate-blue dusk sky, floodlight pole silhouetted at the edge of frame, minimal and grim.",
 "wp20_fence_housing_units": "Extreme telephoto compression: rows of identical tan single-story prison housing units behind a double chain-link fence with razor wire, heat haze rippling the air, dry Central Valley light.",
 "wp21_bunk_through_bars": "Looking through dark steel cell bars into a dim cell where an empty bunk bed with a thin bare mattress catches a single shaft of cold light, everything else in shadow, bleak and quiet.",
 "wp22_aerial_farmland": "Straight-down satellite-style aerial view of a sprawling prison complex — octagonal clusters of buildings, exercise yards, double perimeter fencing — isolated in a vast grid of Central Valley farmland fields, no other development for miles.",
 "wp23_visitors_sign": "A sun-bleached blue metal roadside sign reading exactly 'VISITORS PARKING' with a white arrow, mounted on a pole beside a dusty road near a prison fence, mountains hazy in the background. Render ONLY the exact text specified — no extra words.",
 "wp24_notice_board": "A large white regulation notice board zip-tied to a chain-link fence outside a prison, with the heading exactly 'NOTICE TO THE PUBLIC' in red and 'AVISO AL PUBLICO' below it, the smaller body text too small and blurred to read, weathered and sun-faded. Render ONLY the exact heading text specified — body text stays illegible.",
 "wp25_caution_sign": "A yellow diamond-edged metal road sign reading exactly 'California State Prison CAUTION Reduce Speed Cross Traffic Ahead' in dark blue letters, against a bright blue sky, telephone poles behind. Render ONLY the exact text specified — no extra words.",
 "wp26_escort_corridor": "Two uniformed correctional officers escorting a woman in light-blue prison scrubs down a long institutional corridor, ALL THREE seen from directly behind at a distance so no faces are visible, fluorescent lighting, polished floor reflections.",
 "wp27_water_tower": "A pale water tower rising above low tan prison buildings and perimeter fencing, dry brown hills in the background, hazy afternoon light, long lens.",
 "wp28_sally_port": "A prison vehicle sally-port gate: heavy rolling steel gate on tracks, red STOP sign, empty guard booth with dark windows, chain-link and razor wire on both sides, harsh midday sun.",
 "wp29_patdown": "A uniformed female correctional officer performing a routine procedural pat-down search of a woman in light-blue prison scrubs who stands facing a cinder-block wall with her arms out, BOTH seen from behind at a distance so no faces are visible, harsh fluorescent light.",
 "wp30_escort_grip": "Close-up detail shot: a correctional officer's hand gripping the upper arm of a woman in a light-blue prison uniform during an escort, her wrists in front of her, shallow depth of field, institutional corridor blurred behind, no faces in frame.",
 "wp31_cell_check": "Seen from the corridor: a uniformed correctional officer stands in a cell doorway looking in, back to camera, while inside the dim cell a woman in blue scrubs sits on the lower bunk with her head down, face not visible, tense quiet moment.",
 "wp32_doorway_shadow": "Night in a women's prison dormitory: the dark silhouette of a uniformed correctional officer fills the lit doorway at the end of the room, duty belt visible in outline, rows of bunk beds in near-darkness in the foreground, ominous institutional atmosphere, no faces visible.",
 "wp33_yard_watch": "A correctional officer in a khaki uniform and sunglasses standing in the foreground watching over a prison exercise yard, arms crossed, women in light-blue scrubs small and out of focus in the background, harsh midday sun, documentary long lens.",
 "wp34_close_talk": "Across a prison dayroom seen from a distance: a standing uniformed correctional officer leans down over a woman in blue scrubs seated alone at a steel table, speaking to her, her shoulders hunched, both faces turned away from camera, uncomfortable power dynamic conveyed only through posture.",
 "wp35_intake_fingerprint": "Close-up of a correctional officer's hands rolling a woman's inked fingertip onto a fingerprint card on a steel intake counter, her other hand flat on the counter, no faces in frame, harsh overhead light.",
 "wp36_line_inspection": "A row of women in light-blue prison scrubs standing in a line facing a beige wall, hands behind their backs, while a uniformed correctional officer walks slowly along the line behind them, ALL seen from behind so no faces are visible, fluorescent corridor light.",
 "wp37_keys_belt": "Close-up of a correctional officer's duty belt at hip level — key ring, handcuffs, radio — with a blurred woman in blue scrubs sitting on a dayroom bench in the background, shallow depth of field, documentary detail shot.",
 "wp38_tower_watch": "Looking up from a prison yard at a guard tower window where the small figure of an officer stands watching, chain-link and razor wire crossing the foreground, women in blue scrubs tiny at the bottom edge of frame, overcast light.",
 "wp39_count_time": "A uniformed correctional officer with a clipboard walking past open dorm cubicles conducting count, women in blue scrubs standing at the foot of their bunks, everyone seen from behind at a distance, no faces visible, fluorescent institutional light.",
 "wp40_control_desk": "A correctional officer seen from behind at a control-room desk watching a wall of small security monitors showing corridors and dorm rooms of a women's prison, dim room lit by the screens, institutional atmosphere.",
 "wp41_male_guard_doorway": "A tall broad-shouldered MALE correctional officer in a khaki uniform standing in a cell doorway seen from inside the dim cell, his figure mostly in silhouette against the bright corridor light, duty belt in outline, while a woman in light-blue prison scrubs sits on the bunk in the foreground with her back to camera, tense institutional quiet, no faces visible.",
 "wp42_male_guard_follow": "A long empty prison corridor: a woman in light-blue prison scrubs walking away from camera, and a MALE correctional officer in khaki uniform walking close behind her, both seen from directly behind at a distance so no faces are visible, fluorescent light reflecting off the polished floor, uneasy spacing between them.",
 "wp43_male_guard_over_bunk": "Inside a dim prison dorm room: a MALE correctional officer in khaki uniform standing beside a bunk bed, one hand resting on the upper bunk frame, while a woman in blue scrubs sits on the lower bunk edge with her head down, BOTH seen from behind/side so no faces are visible, heavy quiet mood, documentary long lens through the doorway.",
 "wp44_male_guard_flashlight": "Night in a women's prison dormitory: the dark outline of a MALE correctional officer walking slowly down the aisle between bunk beds sweeping a flashlight beam across the sleeping rows, seen from low and behind, faces not visible, ominous institutional atmosphere.",
 "wp45_male_guard_office": "Seen from a prison corridor: a woman in light-blue scrubs standing hesitantly in the open doorway of a small administrative office where a MALE correctional officer sits at a desk inside, both figures small in frame and faces not visible, fluorescent hallway light, uneasy stillness.",
 "wp46_male_guard_towering": "Across a prison dayroom: a tall MALE correctional officer in khaki uniform standing very close over a small woman in blue scrubs seated alone at a bolted steel table, his posture looming, her shoulders drawn in, seen from a distance with both faces turned away, power imbalance carried entirely by the body language.",
 "wp47_male_guard_cell_talk": "A MALE correctional officer in khaki uniform leaning one arm against the frame of an open cell door speaking to a woman in blue scrubs who stands just inside the cell with her arms crossed, seen in profile from far down the corridor so faces are indistinct, harsh overhead light, uncomfortable closeness.",
 "wp48_male_guard_stairwell": "A concrete prison stairwell: a MALE correctional officer escorting a woman in light-blue scrubs up the stairs, gripping the rail, both seen from below and behind so no faces are visible, caged light fixture on the wall, cold green-grey paint.",
 "wp49_male_guards_yard_pair": "Two MALE correctional officers in khaki uniforms standing together at a chain-link fence line watching over a women's prison exercise yard, seen from behind, women in light-blue scrubs small and out of focus beyond the fence, harsh Central Valley sun.",
 "wp50_male_guard_door_hold": "Close detail shot: a MALE correctional officer's arm holding a heavy steel door open, his key ring hanging at his hip, while a woman in blue scrubs passes through the doorway ahead of him seen only from behind, shallow depth of field, institutional corridor.",
 "wp51_male_guard_cctv": "A prison corridor corner: a dome CCTV camera mounted high on the wall in the foreground, below it a MALE correctional officer in khaki standing at the corner watching a woman in blue scrubs walk away down the hall, all faces away from camera, fluorescent light, surveillance mood.",
 "wp52_male_guard_count_pause": "Night count in a women's prison dorm: a MALE correctional officer with a clipboard PAUSED at the foot of one bunk looking down at it while a woman lies turned toward the wall, seen from across the dark room, his face not visible, single cold pool of light from the doorway.",
}

def run(slug, desc):
    out = os.path.join(OUT, f"{slug}.png")
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        print(f"[SKIP] {slug}")
        return
    prompt = desc + STYLE
    try:
        r = generate_gpt_image(prompt, aspect_ratio="4:3", resolution="2K")
        if r.get("status") == "success" and r.get("urls"):
            img = requests.get(r["urls"][0], timeout=120).content
            with open(out, "wb") as f:
                f.write(img)
            print(f"[OK] {slug} ({len(img)//1024}KB)")
        else:
            print(f"[FAIL] {slug}: {str(r.get('raw'))[:200]}")
    except Exception as e:
        print(f"[ERR] {slug}: {e}")

if __name__ == "__main__":
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda kv: run(*kv), SHOTS.items()))
    print("DONE")
