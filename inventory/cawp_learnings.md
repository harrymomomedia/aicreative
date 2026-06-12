# CAWP (CA Women's Prison, Pulaski/Jones) — campaign learnings & state

Session 2026-06-10/12. Campaign-specific facts; global rules live in CLAUDE.md.

## Shipped (36 ads, 3 AdMachin groups)

| Group | ad_type tag | Count | Status | State file |
|---|---|---|---|---|
| Launch list (F1×2, F2, F5×3, R1-R8) | `cawp-launchlist-2026-06` | 14 | staged drafts | `outputs/cawp_admachin_stage_state.json` |
| Mija dozen (12 hooks on l2) | `cawp-mija-2026-06` | 12 | LAUNCHED by user | `outputs/cawp_admachin_r9_state.json` |
| R10 winner (10 personas) | `cawp-r10-winner-2026-06` | 10 | staged drafts | `outputs/cawp_admachin_r10_state.json` |

All in Tort project `e15c60bd-…` / Women's Prison sub `acf1b974-…`. Live FB targeting (from the
running ads): campaign "WPA - Latina - HJ P2" `120250568266950281`, ad sets `120250582304530281`
("6 - latina") + `120250582569000281` ("8 - latina"), page `451791144678410`, LEARN_MORE,
`https://womensprison.justicecovered.com/?utm_campaign_fb=hj`.

## The proven copy

- **Launched standard headline:** "Chowchilla Survivors May Qualify" (+ CIW variant created).
- **Launched standard primary:** the "⚠️ File a Claim for Settlement…" text (note: contains
  "Settlement"/"owed" — grandfathered live winner; NEW copy uses "may qualify for significant
  potential compensation").
- **R10 approved copy pool (rotate):** primaries P1, P3, P4, P9, P10, P11, P12, P14, P15, P20;
  headlines H2 ("Check If You Qualify — Takes 2 Minutes"), H3 ("Were You at Chowchilla or CIW?
  Check Now"), H9 ("Even 20 Years Later, You May Qualify"), H10 ("See If You Qualify — Free &
  Confidential"). Ten one-per-video sense-paired combos staged (P11 "twenty years" → l8's
  20-yr video, etc.). Spaced template: intro → facility bullet list (CCWF / Valley State / CIW) →
  📄 never-reported line → ✅ free/confidential → 👇 CTA w/ locked phrase → verbatim disclaimer.
- Mija-dozen primaries = short/direct format: hook echo → "Guards and staff sexually abused women
  at [facility] for years…" → constant block.

## R9 "Mija" structure (12 ads, one persona l2)

Winner script with 12 user-picked hooks (9 Chowchilla / 3 CIW: i,j,k,m,o,p,q,s,v + y,x,z) and
8 per-hook BRIDGE variants so each discovery mechanism (cellmate/Facebook, funeral, daughter,
bunkie call, headline, phone, yard, sister) hands off to the SAME "She's like, Mee-hah…" body.
User rule: keep the winner's arc + second half untouched; only hook + bridge flex.
Script: `scripts/cawp_r9_mija_gen.py`, assembler `scripts/cawp_r9_assemble.py`.

## R10 winner-on-10-personas structure

Same winner script per persona; ONLY the first sentence swaps, with **age-true varied timeframes**
(user: "change the years… to make it more sense"): l7=15yrs, l8=20 (verbatim original), l9=16,
l10=25, l11=12, l12=18, l14=30, l17="the nineties", l19=22, l21=10. Tone: worried baseline,
controlled-anger beats on clips 4-5 ("…Sexual abuse." / "That happened to me"), softens at "it's
not too late". Mija → "Mee-hah" respell. Compliance fixes vs the raw winner: locked phrase, no
"Nobody's calling you" (lawyers DO call — privacy framing instead).
Scripts: `scripts/cawp_r10_winner_gen.py`, `cawp_r10_assemble.py`, `cawp_r10_blur_finish.py`.

## One-off facts worth keeping

- **l7 laundromat is the ONLY blur-background persona** (VEED matte + gblur σ7 + FROZEN-plate
  CTA after door-motion re-rolls failed twice). User explicitly scoped blur to l7 only.
- **9:16 + 4:5 both exist for all 10 R10 ads** (`r10_winner_<slug>_4x5_nick_disclaimer.mp4`,
  720×900, golden-third, captions re-burned at the new aspect from CLEAN masters — never crop a
  captioned combo). The earlier "no 4:5 versions" call was per-set, not absolute; user asked for
  newsfeed sizes on R10.
- OCR burn-flag false-positive wardrobe (band-sheet each flag, all benign): l8 floral dress,
  l10 plaid flannel, l14 knit sweater, l17 housecoat, l2 floral blouse.
- Watch-items the user may still review: l9 clip4 opener Scribe'd "therefore" vs "They're";
  l9 hook kept Veo's dropped-"I" delivery ("Did time at Chowchilla…" — line synced in registry
  so the trimmer anchors correctly).
- Persona pool: approved trio l1 (car) / l2 (kitchen) / l4 (porch) + identity-distinct l7-l21
  (15). Unused bench: l13, l15, l16, l18, l20. One persona = one facility/story across live ads.
- Free-queue throughput reality: ~150+ clips/day works, but expect 403 retries and occasional
  run death + 429 holes late in the day — relaunch, sweep, done.

## A–E story testimonials (2026-06, 4th format)

Intimate single-persona confession arc, 6 clips × 8s (~42–44s): topic + "sexual abuse" by beat 1–2,
compensation arrives NATURALLY mid-story (~beat 4), CTA close. Full "significant potential
compensation". A=grooming ("the nice officer", latr8), B=retaliation ("punished me, not him", latr9),
C=aftermath ("the flinch", latr1), D=counselor dismissal (latr10, parked car), E=social proof ($100M,
latr3). Persona pool: approved Latina-rough `latr1/2/3/6/8/9/10` + new wide-variety batch `latr22–31`.

- **Scripts:** `scripts/ccwf_gen.py` (FREE google-flow veo-3.1-lite-low-priority), `ccwf_personas.py`
  (gpt-image-2 stills), `ccwf_finalize.py` (RAW-VEO-audio finalize: word-aware trim → watermark-crop
  `664:1180:28:0→720×1280` → per-clip gain → concat → master limiter), `ccwf_voice_audition.py`.
  **Naming slip — used `ccwf_`/`outputs/ccwf_story*` instead of the campaign's `cawp_` prefix; prefer
  `cawp_` next time (see `feedback_naming_convention_campaign_persona`).**
- **Voice = RAW VEO audio (user choice, no voice_changer).** Veo collapses every persona to ~one voice
  (per-prompt voice variety is weak); user accepted raw Veo over VC-differentiating "for now". If
  differentiation is ever needed, the ElevenLabs account has ~8 distinct Latina/Hispanic women voices
  (Hispanic 50/53/54/55/60, Latina_F_55, Hazel) — VC each ad to a distinct one; `ccwf_voice_audition.py`
  auditions them on one clip.
- **Veo PARKED-CAR must not move (story D):** i2v adds DRIVING motion to night-car scenes (streetlights
  slide past, reads as driving). Fix = aggressive lock in the prompt's `extra` field ("PARKED, ENGINE
  OFF, locked-off shot, the world through every window is a FROZEN still image, NOTHING outside moves")
  **+ generate 2 takes and auto-pick the one with the least window-region frame-diff** (measure right-side
  motion across sampled frames). Prompt alone is not enough; the 2-take pick is what nailed it.
- **Veo "X and Y" between two proper nouns → "X in Y"** (Chowchilla **and** Chino rendered as Chowchilla
  **in** Chino — conflates two separate prisons). Two re-rolls both did it. Fix = rewrite to the "at
  Chowchilla **or** Chino" qualifier (renders clean, matches B/C/D). General: don't join two proper nouns
  with "and"; use "or" / restructure.
- **Finalize trim gotcha:** Scribe reformats spoken numbers ("a hundred and three" → "103"), so the
  word-aware trim's leading subsequence match starts AFTER the number and chops it (E clip04 lost "103
  women"). Fixed in `ccwf_finalize.py`: when the first intended word is unmatched, back up over leading
  non-improv transcript words to keep the spoken number.
- **AdMachin:** 5 combo deliverables (Nick captions + Pulaski/Jones disclaimer) → Tort/Women's Prison;
  5 draft ads = headline `c53d1ea3` ("Chowchilla Survivors May Qualify") + primary `79fe1553`. **A LAUNCHED
  ad (#361, creative #654 = story E) had the WRONG juvie primary #465 — launched ads are IMMUTABLE, so
  the fix is "create one more" (a new draft ad with the correct primary), never edit the live one.**
  Subproject now resolvable by NAME (`list_subprojects(project_id, search="women")` → `acf1b974`).
- **Both internal caption engines produced for this set:** `caption_nick.py` (Nick) and
  `caption_hormozi3.py` (Hormozi 3), each combo'd with `burn_disclaimer.py`. NOTE: `caption_nick.py` +
  the `nick-subtitle` skill already existed from a prior session — check before rebuilding a caption engine.
