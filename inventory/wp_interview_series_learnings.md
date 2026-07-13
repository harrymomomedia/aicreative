# Women's Prison — street-interview series (vox-pop → Nice One → "It Was Never Consent"), 2026-07

Campaign record for the 6-ad interview roster built 2026-07-11/12. General rules were promoted to
CLAUDE.md + skills (`street-interview-production`, `veo-interview-qa`, `proper-noun-pronunciation`,
`admachin-platform-ops`); this doc keeps the campaign-specific details.

## Final roster (one per unique script) — all staged to AdMachin as DRAFTS 2026-07-12

Tort project `e15c60bd-95c2-47b9-9730-c29fb5325461` / Women's Prison sub `acf1b974-9721-488b-a4e0-ffe0664070c5`.
Staging script `scripts/wp_stage6_admachin.py` (state: `outputs/wp_stage6_state.json`, gitignored).
User-approved copy 2026-07-12: recommended Headline A per ad + spaced primary template with the FULL
4-facility list (CCWF Chowchilla / CIW Chino / Valley State / Folsom Women's Facility — user rule:
always list all four, all qualify) + verbatim Pulaski/Jones disclaimer at the end of every primary.
NOTHING LAUNCHED.

| Ad (slug) | Video | Dur | Draft ad id | Creative id |
|---|---|---|---|---|
| voxpop-didyouknow | `outputs/wp_voxpop/FINAL_grok.mp4` | 40s | `2ca1fbbc-5d97-491b-bfa3-6a33098a44c2` | `543cb3f7-…` |
| omni-500women | `outputs/wp_voxpop/FINAL_omni.mp4` | 39s | `749ed08b-d43d-4467-85b5-d35e142adecb` | `f7e7e6cc-…` |
| niceone | `outputs/wp_interview2/FINAL_niceone.mp4` | 78s | `218a7973-d0af-45b7-8d1d-1548112f2579` | `f8db1bc7-…` |
| relationship | `outputs/wp_series2/FINAL_relationship.mp4` | 74s | `c52215ae-bf03-4b7c-9be6-dfe1cfcad617` | `b26bdc85-…` |
| moved | `outputs/wp_series2/FINAL_moved.mp4` | 53s | `59a7a791-e5a0-438a-8c4c-bb2cf724d798` | `f15e34b8-…` |
| kids | `outputs/wp_series2/FINAL_kids.mp4` | 59s | `f7d6882a-39e8-4930-8128-ebd9c0ed4a60` | `05408de8-…` |

Headlines (approved, per ad): "Chowchilla Survivors May Qualify — Check Now" · "Even 20 Years
Later, You May Qualify" · "It Wasn't Kindness. You May Qualify." · "In Prison, It Was Never
Consent" · "They Moved You to Keep You Quiet" · "You Never Told Anyone. You May Still Qualify."

WIP iterations dropped from the roster (archived `outputs/wp_voxpop/wip/`): `FINAL_veo.mp4`
(two-shot voice collapse), `FINAL_grok_voiceswap.mp4` (28% male-range flag, redundant variant).

## LAUNCHED (PAUSED) 2026-07-12 — YJE-23 / WPA - Latina - HJ P1

Launcher `scripts/wp_launch_adsets.py` (state `outputs/wp_launch_state.json`, gitignored). Account
`act_885970616544640` (YJE-23), campaign `120242151877070281`. 3 NEW adsets, 2 ads each, **$100/day,
NO bid cap** (LOWEST_COST_WITHOUT_CAP), duplicated audience from adset `120248405890960281`. **ALL
PAUSED — do NOT re-launch; activate in Meta UI.** Full default UTM (`admachin_utm.default_landing_url`)
in landing_url.

| Adset | FB adset id | Ads (launch ids) |
|---|---|---|
| 42 - interview street - 20-64 | `120252946177060281` | voxpop-didyouknow `3c22995e…` · niceone `fe5027c9…` |
| 43 - interview reframe - 20-64 | `120252946395690281` | omni-500women `4469f755…` · relationship `4296320e…` |
| 44 - interview personal - 20-64 | `120252946729910281` | moved `57770185…` · kids `13ee6cd1…` |

Endpoint-forced deviations from the source adset (note for exact-match tweaks in Meta UI):
placements → **Advantage+ automatic** (API rejected source's manual `threads`/`biz_disco_feed`/
`facebook_reels_overlay`/etc.), attribution → **Meta default** (source's custom attribution_spec
format rejected). Audience/geo/age(20-64)/gender(women)/pixel(`1345276490863660`→LEAD) identical.
Meta code-6000 video-upload glitches on relationship/moved were transient (cleared on idempotent
retry).

## Production pipeline (what actually built these)

- Anchors: `wp_voxpop_personas` / `wp_courthouse_personas` / `wp_series2_personas` (t2i, explicit
  anthropometry), `wp_series2_camlock` (into-lens closers), `wp_series2_eyeline_fix` (screen-left
  i2i flips), canonical mic ref `outputs/wp_interview2/reference/mic_ref.png`.
- Produce: `wp_series2_produce.py` — solo clip per turn, `WP_PROVIDER=googleflow` (useapi-first),
  adaptive 4/6/8s duration from word count, screen-direction gaze wording.
- Finalize: `wp_series2_finalize.py` → `veo_clip_qa.qa_clip()` gate (keep-best ≤3 attempts) →
  span-trim → concat + loudnorm → `caption_nick.py` → `burn_disclaimer.py` → master + `_web`.
- Disclaimer verification: OCR the bottom 12% band at fps 0.5 (`tesseract --psm 6`, grep
  advertisement/attorney/dramatiz) — the 6s calmest-window burn is easy to miss by eye; confirmed
  present on all 6 (grok@18s, omni@14s, niceone@42s, relationship@54s, moved@6s, kids@32s).

## Campaign-specific QA numbers (context for thresholds)

- Whole-video voice sweep (assembled finals): male-range 1–3%, female 90–93% — CLEAN.
- Worst per-beat male_frac kept: 18% (kids t09_S) — low female chest register, NOT bimodal; the
  22% MALE_MAX + bimodal check separates this correctly from the true failures (31–60% male).
- True male-voice failures all hit interviewer question-opener beats t01/t03 on the free Lite tier.
- Free-tier Veo watermark present bottom-right on these (user accepted; crop recipe in
  veo-interview-qa skill if ever needed).

## Session learnings already promoted (pointers, don't re-derive)

- Eyeline/gaze, adaptive duration, provider chain, parallel run phases → `street-interview-production`.
- 7-check per-clip gate + trim/assembly + visual QA extras → `veo-interview-qa` + `scripts/veo_clip_qa.py`.
- Chowchilla descriptive lock + isolated-window unbiased Scribe verify → `proper-noun-pronunciation`.
- AdMachin upload-verify / ad_type / immutability / launch gating → `admachin-platform-ops`.
- Cloud video presentation (SendUserFile render, one per call, filename-first caption) → CLAUDE.md.
- gpt-image-2 i2i `input_urls` identity fix; GAZE-baked-into-anchor rule → CLAUDE.md.
