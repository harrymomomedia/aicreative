"""Depo docu-series generator v3 — YouTube-docu montage.
User-locked (2026-07-09): NO plain black text cards. Every text card (study / labels / counter /
JUNE-15 / CTA) rides OVER a relevant b-roll clip with a dark scrim — the count-up over courthouse
footage, "two labels" over the product macro, etc. Clip beats use the real product (pv*) +
recovery (rec*/recb*) library. python gen_docu.py n1|n3|n6 -> index.html
"""
import sys
EP = sys.argv[1] if len(sys.argv) > 1 else "n1"

# spec: ("clip", broll) | ("card", card_id, bg_broll)   (mri kept as a bg option via a clip)
EPS = {
 "n1": dict(vo="n1_reason.mp3", dur=45.9, segs=[
    (0.0,  4.6, ("clip","v02_monitor_reveal")),
    (4.6,  7.1, ("clip","rec1_bed_bandaged")),
    (7.1, 11.6, ("card","study","v16_laptop_point")),
    (11.6,14.2, ("clip","pv3_injection")),
    (14.2,16.8, ("clip","pv13_vial_calendar")),
    (16.8,21.7, ("card","labels","pv6_vial_macro")),
    (21.7,23.2, ("clip","v22_signing")),
    (23.2,26.8, ("card","counter","v24_courthouse_steps")),
    (26.8,33.5, ("card","june","v23_folders_table")),
    (33.5,37.2, ("clip","recb1_bed_bandaged")),
    (37.2,39.7, ("clip","v16_laptop_point")),
    (39.7,45.9, ("card","cta","rec3_phone_selfie")),
 ]),
 "n3": dict(vo="n3_sixthousand.mp3", dur=41.5, segs=[
    (0.0,  4.0, ("card","counter","v24_courthouse_steps")),
    (4.0,  8.0, ("clip","v02_monitor_reveal")),
    (8.0, 12.0, ("clip","recb3_phone_selfie")),
    (12.0,14.0, ("clip","pv3_injection")),
    (14.0,17.6, ("card","study","v17_laptop_scans")),
    (17.6,20.6, ("clip","v24_courthouse_steps")),
    (20.6,26.1, ("card","june","v23_folders_table")),
    (26.1,29.7, ("clip","v20_claim_envelope")),
    (29.7,31.8, ("clip","v22_signing")),
    (31.8,35.5, ("clip","recb1_bed_bandaged")),
    (35.5,41.5, ("card","cta","rec3_phone_selfie")),
 ]),
 "n6": dict(vo="n6_goodnews.mp3", dur=45.1, segs=[
    (0.0,  4.1, ("clip","rec1_bed_bandaged")),
    (4.1,  7.9, ("card","june","v24_courthouse_steps")),
    (7.9, 12.7, ("clip","pv7_box_upright")),
    (12.7,15.0, ("clip","pv3_injection")),
    (15.0,17.5, ("clip","v02_monitor_reveal")),
    (17.5,22.8, ("card","counter","v23_folders_table")),
    (22.8,25.4, ("clip","v19_records_folder")),
    (25.4,29.5, ("card","study","v16_laptop_point")),
    (29.5,33.0, ("card","labels","pv6_vial_macro")),
    (33.0,36.7, ("clip","recb3_phone_selfie")),
    (36.7,39.1, ("clip","v18_phone_scan")),
    (39.1,45.1, ("card","cta","recb3_phone_selfie")),
 ]),
}[EP]

CARD_HTML = {
 "study": '<div class="cardtitle">2024</div><div class="cardbig">A MAJOR MEDICAL STUDY</div><div class="cardline" id="{i}-ul"></div><div class="cardsub">long-term use of the shot linked to<br/>BRAIN MENINGIOMAS</div>',
 "labels": '<div class="cardbig" style="font-size:64px">TWO LABELS. SAME SHOT.</div><div class="labelrow"><div class="labelbox"><div class="labelhead">OTHER COUNTRIES</div><div class="labelword ok" id="{i}-ok">meningioma&nbsp;&#10003;</div></div><div class="labelbox"><div class="labelhead">UNITED STATES</div><div class="labelword miss" id="{i}-miss">&mdash;</div></div></div>',
 "counter": '<div class="cardsub" style="margin-top:0">CASES FILED IN FEDERAL COURT</div><div class="counter" id="{i}-num">0</div><div class="cardsub">one court &middot; Florida</div>',
 "june": '<div class="datecard" id="{i}-date">JUNE 15</div><div class="cardbig" style="font-size:58px">PFIZER AGREES TO A<br/>GLOBAL SETTLEMENT</div><div class="cardsub">agreement in principle &middot; not final &middot; terms not public</div>',
 "cta": '<div class="cardbig" style="font-size:66px">FREE &middot; PRIVATE<br/>2 MINUTES</div><div class="cardsub" style="font-size:40px;color:#fff">you may qualify for<br/>SIGNIFICANT COMPENSATION</div>',
}

d = EPS
# Auto-rescale beat times to the ACTUAL VO duration (voice-agnostic — re-times on any narrator).
import subprocess
_r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"assets/vo/{d['vo']}"],
                    capture_output=True, text=True)
_actual = float(_r.stdout.strip()); _scale = _actual / d["dur"]
d = dict(d, dur=round(_actual,2),
         segs=[(round(t0*_scale,2), round(t1*_scale,2), spec) for t0,t1,spec in d["segs"]])
parts, media, tweens = [], [], []
for n, (t0, t1, spec) in enumerate(d["segs"]):
    sd = round(t1 - t0, 2); sid = f"s{n:02d}"
    def vid(elid, slug, z=1):
        media.append(f'<video id="{elid}" class="clip broll" src="assets/broll2/{slug}.mp4" data-start="{t0}" data-duration="{sd}" data-track-index="{z}" muted playsinline></video>')
        tweens.append(f'tl.fromTo("#{elid}",{{scale:1.0}},{{scale:1.06,duration:{sd},ease:"none"}},{t0});')
    if spec[0] == "clip":
        vid(sid, spec[1])
    else:
        _, cid, bg = spec
        vid(f"{sid}bg", bg, z=1)                        # b-roll background
        inner = CARD_HTML[cid].format(i=sid)
        parts.append(f'<div id="{sid}" class="cardov clip" data-start="{t0}" data-duration="{sd}" data-track-index="2">{inner}</div>')
        tweens.append(f'tl.from("#{sid}",{{opacity:0,duration:.4,ease:"power2.out"}},{t0});')
        if cid == "study":
            tweens.append(f'tl.fromTo("#{sid}-ul",{{scaleX:0}},{{scaleX:1,duration:.6,ease:"power2.out",transformOrigin:"left center"}},{t0+0.5});')
        if cid == "labels":
            tweens.append(f'tl.from("#{sid}-ok",{{opacity:0,scale:.6,duration:.45,ease:"back.out(2)"}},{t0+0.8});')
            tweens.append(f'tl.from("#{sid}-miss",{{opacity:0,duration:.45}},{t0+1.6});')
        if cid == "counter":
            tweens.append(f'var c{n}={{v:0}}; tl.to(c{n},{{v:5830,duration:{min(2.4,sd-0.6)},ease:"power1.out",onUpdate:function(){{var e=document.getElementById("{sid}-num"); if(e) e.textContent=Math.round(c{n}.v).toLocaleString("en-US");}}}},{t0+0.3});')
        if cid == "june":
            tweens.append(f'tl.from("#{sid}-date",{{scale:2.0,opacity:0,duration:.5,ease:"power3.out"}},{t0+0.05});')

html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face{{font-family:"Montserrat Black";src:url("assets/fonts/Montserrat-Black.ttf") format("truetype");font-weight:900;font-display:block;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{width:1080px;height:1920px;overflow:hidden;background:#0a0a0c;}}
#root{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#0a0a0c;}}
.broll{{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover;transform-origin:center center;}}
/* text card OVER b-roll: dark scrim + shadowed text (no more solid black) */
.cardov{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:0 70px;gap:34px;font-family:"Montserrat Black",sans-serif;
  background:linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,.62) 45%,rgba(0,0,0,.72));}}
.cardov *{{text-shadow:0 3px 20px rgba(0,0,0,.92);}}
.cardtitle{{font-size:110px;color:#ff5a5a;line-height:1;}}
.cardbig{{font-size:72px;color:#fff;line-height:1.15;}}
.cardline{{width:60%;height:10px;background:#ff3b3b;border-radius:5px;}}
.cardsub{{font-size:34px;color:#e6e6e6;line-height:1.5;letter-spacing:1px;}}
.labelrow{{display:flex;gap:40px;margin-top:20px;}}
.labelbox{{width:420px;border:3px solid rgba(255,255,255,.25);border-radius:18px;padding:44px 20px;background:rgba(10,10,14,.55);}}
.labelhead{{font-size:26px;color:#bbb;margin-bottom:26px;letter-spacing:2px;}}
.labelword{{font-size:44px;}} .ok{{color:#3dffb0;}} .miss{{color:#ff5a5a;font-size:64px;}}
.counter{{font-size:190px;color:#fff;line-height:1;}}
.datecard{{font-size:150px;color:#ff5a5a;line-height:1;}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{d['dur']}" data-width="1080" data-height="1920">
{chr(10).join(media)}
{chr(10).join(parts)}
<audio id="vo" src="assets/vo/{d['vo']}" data-start="0" data-duration="{d['dur']}" data-track-index="10" data-volume="1"></audio>
</div>
<script>
window.__timelines=window.__timelines||{{}};
const tl=gsap.timeline({{paused:true}});
{chr(10).join(tweens)}
window.__timelines["main"]=tl;
</script></body></html>'''
open("index.html","w").write(html)
print(f"wrote {EP}: {len(d['segs'])} segments, cards-over-broll, {d['dur']}s")
