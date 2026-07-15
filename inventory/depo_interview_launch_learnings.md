# Depo-Provera brain-meningioma — INTERVIEW track + AdMachin launch state (2026-07-12→15)

Sibling of `depo_video_learnings.md` (animated explainers) and `depo_provera_ad_formats.md` (image
ads). This file covers the **two-person documentary/podcast interview** video track and records the
**live Meta launch state** so a future session does NOT re-launch duplicates.

## The three interview concepts (produced + staged + launched)

Two-person interview (survivor top / documentarian bottom), each cut into a **stacked** layout and a
**cut** (full-frame reverse-angle) layout → 6 creatives. Diagnosis-first angle; "significant
compensation"; ad text starts on brain meningioma, NOT Depo (user-locked).

| Concept | Slug | Interviewer / subject | Angle |
|---|---|---|---|
| **Bad Luck** | `badluck` | (original pair) | "This may not be bad luck" — prolonged Depo → meningioma |
| **Insider** | `insider` | new pair | Ex-nurse who gave the shot then got the diagnosis herself |
| **Figured** | `figured` | new pair | "She figured it out herself — nobody told her" |

Produced end-to-end per the **`stacked-podcast-broll`** and **`interview-scene`** skills — all the
locked rules (anchor-verification pass at the IMAGE stage, chin-safe face-aware crop via
`scripts/face_crop.py` `pane_crop`, b-roll-over-VO 2s-face-then-b-roll, stereo-48k concat, real-text
credibility b-roll, layout-aware captions) live in those skills + CLAUDE.md. Assembly scripts:
`scripts/depo_grok_full_assemble.py` (Bad Luck), `scripts/insider_assemble.py`,
`scripts/figured_assemble.py`. Captions: `scripts/caption_hormozi3.py --vpos-map` (seam 0.50 for
two-pane, bottom 0.82 for full-frame b-roll tails / CTA) built via `scripts/build_caption_vpos.py`.

### Interview-track specifics worth keeping
- **Grok Imagine (`grok-imagine/image-to-video` via KIE)** is THE model for both talking heads (clean
  native audio) AND genuine silent listeners (mouth stays CLOSED — every Veo tier animates it). Grok
  payload uses `input.image_urls`; gpt-image-2 i2i uses `input_urls` — don't cross them.
- **Real-text credibility b-roll = verified facts only.** Depo→meningioma proof beats used the real
  **BMJ 2024** study (Roland et al. — medroxyprogesterone acetate ≈ 5.6× meningioma risk) and the
  real **MDL No. 3140** (In re: Depo-Provera Products Liability Litigation, N.D. Florida). NEVER
  fabricate FDA/government-branded records — a plain manufacturer label is fine, a fake gov record is
  not.
- **Reuse existing AdMachin b-rolls** (post-op / recovery / scan) from the **B-Roll DB** (`/brolls/clips`,
  NOT `/creatives`) before generating new ones. Client: `admachin_client.upload_broll_clip` /
  `list_broll_clips`. Don't use the empty phone-form clip (no visible on-screen text reads as fake).
- Pronunciation respells that stuck: meningioma → "meninjioma", Depo → "Deppo" (mid-line so the
  word-aware trim is unaffected).

### B-roll direction the user locked (2026-07)
- **NO symptom-hook b-roll** (blur/vision-loss, eye exam, headache mimes) — they pull **broad,
  unqualified traffic**. The qualifier is the *diagnosis + Depo history*, not a symptom.
- **Category D = credibility, and it must use REAL on-screen text** (the BMJ study headline, the MDL
  docket) — "we should use the actual text for these, but if not, then let's not use it." A
  credibility beat with fake/blank text is worse than none.
- **Category E = emotional** (recovery, family, quiet resolve) is approved and works.
- Reuse the existing B-Roll DB clips (post-op/recovery/scan) before generating new; build the
  future-b-roll set "starting from gpt2" i2i. Don't use a phone-form clip with no visible text.

## LIVE LAUNCH STATE (Meta) — do NOT re-launch these

Account **YJE-23** `act_885970616544640` · campaign **Depo - Pulaski HJ** `120251695982040281` ·
page **Justice Covered** `451791144678410` · pixel `847793330973723` (LEAD) · CTA `LEARN_MORE` ·
landing `https://depop.justicecovered.com/` (default `{{ }}` UTM + `am_mb`). Each new adset $100/day,
duplicated from source adset **"41"** `120252846958710281` via `/launches/bulk` native `/copies`.

| Adset | id | Budget | Adset status | Ads (concept · layout) |
|---|---|---|---|---|
| **42** | `120252931068700281` | $100/day | **ACTIVE** | badluck_stacked + badluck_cut |
| **43** | `120252937187580281` | $100/day | **PAUSED** | insider_stacked (910) + insider_cut (911) |
| **44** | `120252937187800281` | $100/day | **PAUSED** | figured_stacked (912) + figured_cut (913) |

AdMachin ad-row ids (`outputs/depo_admachin_stage.json`): badluck_stacked `c2d189d3…`, badluck_cut
`0c312659…`, insider_stacked `6d5fcbb5…`, insider_cut `9eeb9edc…`, figured_stacked `04363eb5…`,
figured_cut `671aa30e…`. All 6 launched, no duplicates. **43 & 44 need to be flipped ACTIVE in the
Meta UI** when the user is ready (42 already ACTIVE).

Full endpoint map + the `use_create_from_source`-stalls / async-timeout-isn't-failure / Meta-6000
gotchas are in CLAUDE.md → "Launch via adset duplication". Reusable gated launcher:
`scripts/depo_launch_badluck.py`.
