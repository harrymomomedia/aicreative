# Depo-Provera Brain-Tumor Campaign — Ad-Format Dissection

New tort lead-gen campaign. This file dissects the **81 Depo-Provera ads in AdSwipe**
(swipe library, search="depo", noise pages dropped — corpus saved to
`inventory/depo_swipe_corpus.txt`) into format archetypes, folds in static-ad formats from
our other tort builds (CAWP F1, cilocala), and lists the compliant copy + the recommended
first image-ad batch. **We are building IMAGE ads first.**

Swipe split: **20 image + 17 carousel + 42 video** (after dropping vision/ED supplement ads
the broad search swept in). Project = Tort (`e15c60bd`), subprojects `9cfb5b76` (43) +
`5b93c4cb` (11) + null bucket.

## POSITIONING — LEAD WITH THE DIAGNOSIS (LOCKED 2026-06-15)

**Target the brain-tumor diagnosis FIRST, Depo-Provera second.** The qualifying injury — and the
high-value lead — is the woman who has ALREADY been **diagnosed with a meningioma (brain tumor)**.
Leading with "Did you take Depo?" pulls a huge low-value pool; leading with "Diagnosed with a
meningioma?" self-selects the claim-ready, high-value intake. So:

- **Hook = the diagnosis** ("Diagnosed with a brain tumor — a meningioma?"). **Depo-Provera = the
  link/cause** revealed second ("…the shot you were on may be why").
- Keep BOTH on the creative (the diagnosis qualifies; Depo establishes the claim), but the
  diagnosis is the headline and the visual emphasis (brain scan, the word MENINGIOMA, the
  diagnosis moment).
- Compliance phrase unchanged: "may qualify for significant compensation."

### Diagnosis-first lead hook per format (replaces the Depo-first openers below)

1. **Quiz Gate:** "Diagnosed with a brain tumor (meningioma)?" → "Were you on the Depo-Provera shot?" → "You may qualify…"
2. **Criteria Board:** title "Living with a meningioma? See if you qualify." order: ✓ Diagnosed with a meningioma (MRI/CT confirmed) → ✓ Used Depo-Provera/generic 1+ yr (2+ shots) → ✓ Diagnosed 1992+
3. **Stat Shock:** "Diagnosed with a meningioma? Studies link the Depo-Provera shot to up to **5.6× higher** risk of these brain tumors."
4. **Everything Right:** "You were diagnosed with a brain tumor. A meningioma. You did everything right — so where did it come from? The Depo shot may be the answer."
5. **Symptom Self-Check:** "A meningioma can grow quietly — headaches, vision changes, memory loss, seizures. Diagnosed, and once on Depo-Provera? You may qualify."
6. **Authority:** "Diagnosed with a meningioma after the Depo-Provera shot? We're reviewing claims nationwide."
7. **Native Post:** "If you've been diagnosed with a meningioma (a brain tumor) and you were on the Depo shot, the two may be linked…"
8. **Official Notice:** "MENINGIOMA / BRAIN-TUMOR LEGAL REVIEW — claims involving meningioma diagnoses after Depo-Provera use are under review."
9. **News-Headline:** "Brain-Tumor Diagnoses Tied to Common Birth-Control Shot" (deck: meningioma · Depo-Provera · 5× study).
10. **Value:** "A meningioma diagnosis changes everything. If you used Depo-Provera, you may qualify for significant compensation."
11. **Testimonial:** pull-quote "They said it was a brain tumor. A meningioma." — story opens on the diagnosis moment, Depo revealed as the cause.
12. **Advertorial:** "Thousands of women are being diagnosed with the same brain tumor — a meningioma. Here's the link doctors are now seeing…"
13. **Open Letter:** "To every woman living with a meningioma —"
14. **Reddit:** "Diagnosed with a meningioma — turns out my old birth control may have caused it?"
15. **Texts:** "you know that brain tumor i had removed? the meningioma?" → "they're saying the depo shot causes them"
16. **FAQ:** "Q: I have a meningioma and used Depo years ago — do I qualify?"
17. **Then/Now:** "Now: diagnosed with a meningioma." ↔ "Then: years on the Depo shot."
18. **Myth vs Fact:** "MYTH: a meningioma diagnosed years ago is too late. FACT: you may still qualify."
19. **Did You Know:** "Have a meningioma? It may be connected to a common birth-control shot — and a federal lawsuit."
20. **Loved-One:** "If a woman you love has been diagnosed with a meningioma and used Depo-Provera…"

> The format tables/copy below pre-date this pivot — they read Depo-first. Use the diagnosis-first
> hooks above as the lead line; everything else (criteria, CTA, disclaimer, compliance) stands.

## Case facts (anchors for our copy — all pulled from the swipe corpus + known litigation)

- **Drug:** Depo-Provera (medroxyprogesterone acetate), Pfizer's injectable birth control.
  Generics count (medroxyprogesterone acetate injectable). NDC 0009-0746-30, 150 mg/mL.
- **Harm:** intracranial **meningioma** (brain tumor; also spinal-cord tumors). Symptoms in
  the ads: headaches, vision changes/loss, memory loss, dizziness, seizures, trouble speaking.
- **Science:** BMJ study (Roland et al.) — **~5.6× / 5× / "more than 500%"** increased
  meningioma risk with **>1 year use**. One ad cites "83.2% of meningioma-diagnosed women had
  Depo exposure" and "16,000–18,000 potential cases."
- **Eligibility pattern competitors gate on:** used Depo **≥1 year (≈4 injections) / 2+ shots**;
  **meningioma diagnosis** confirmed by MRI/CT/surgery/radiation; diagnosed **after 1992** (some
  say "within last 15 years"). Brand or generic, mixed use OK.
- **Litigation:** **MDL 3140, Northern District of Florida** (consolidated Feb 2025); Pfizer
  defendant; "failed to warn." Pfizer updated the label in 2024. >1,000–2,000 women suing.
- **Real news exists** (high-credibility b-roll): NBC News (#309), ITV News (#488).

## STATIC ad-format archetypes (image + carousel) — what we'll build

Ranked by how heavily competitors run them (≈ market signal).

| # | Format | Hook mechanic | Swipe refs | Notes |
|---|---|---|---|---|
| 1 | **Two-Question Quiz Gate** | "Took Depo-Provera? / Have a brain tumor? → take the quiz, see if you qualify" | #215 #592 #354 #358 #375 #214 | MOST-replicated format → clearly working. Bold split text. |
| 2 | **Eligibility Criteria Board** | checklist: ≥1 yr · 2+ shots · brand/generic · MRI-confirmed meningioma · post-1992 → "check eligibility" | #496 #372 #366 #249 | Self-qualifies high-intent leads. = cilocala "feature-board". |
| 3 | **Stat / Study Shock** | "new study: 5.6× more likely to develop a meningioma" | #366 #372 #373 #374 #303 #304 | The scary number. Often + brain-scan motif. |
| 4 | **"You Did Everything Right" (betrayal)** | "You ate right. You worked out… so where did the brain tumor come from?" | #561 | Strongest emotion; not-your-fault. Healthy-woman photo. |
| 5 | **Symptom Self-Check (medical alert)** | "Confusion · memory loss · blurred vision · seizures → could mean meningioma" | #353 #204 #254 | Fear / self-diagnosis. Symptom list layout. |
| 6 | **Law-Firm Authority Card** | brand + claim line (Morgan & Morgan, Ward Black, Weitz & Luxenberg, Yost, Keller Postman) | #367 #352 #364 #256 #359 #365 #249 #220 | Trust/authority. #352 = "Your sister. Your best friend." referral angle. |
| 7 | **Native Social-Post / Screenshot** | mimics an organic FB/news post (handle, views, "If you took the Depo shot…") + Depo box photo | #298 | Highest scroll-stop (doesn't read as an ad). = cilocala "UGC-native". |
| 8 | **Official Investigation Notice** | "DEPO-PROVERA LAWSUIT INVESTIGATION — meningioma claims under legal review" + drug label | #221 #359 | Authority/legitimacy. Formal legal-notice styling. |
| 9 | **News-Headline Re-Creation** | rights-clean stylized headline ("Pfizer sued over Depo brain-tumor risk; 5× study") | #365(FDA) #309(NBC) #488(ITV) | Highest-credibility angle. = CAWP **F1** card format. **Re-create, never copy an outlet's logo/screenshot.** |
| 10 | **Settlement-Value Reveal** | "6–7 figure settlements possible / may be owed real money" | #222 #216 #302 | ⚠️ COMPLIANCE-HOT — competitors over-promise here; we soften (see below). |

## VIDEO formats observed (for a later video phase — not building now)

UGC selfie testimonial ("from one woman to another, listen up" #196/#210/#356/#357/#559) ·
"Ladies, stop scrolling" direct hook (#211/#250/#252) · two-person conversational/podcast
(#198 two attorneys, #217 friends) · attorney direct-to-cam MDL explainer (#376 — best factual
script) · real-news segment (#309 NBC, #488 ITV) · symptom-led (#204/#254) · "I trusted it"
confession (#357/#369/#559). These map cleanly onto our existing Veo/UGC + F1 + claymation stack.

## Formats folded in from OTHER tort projects

- **CAWP F1 news-reaction** (`scripts/cawp_f1_headline_cards.py`, memory
  `project_cawp_f1_newsreaction_format`) — PIL-rendered, rights-clean stylized news-headline
  cards (1080×1920), red/ink/paper palette, animated yellow-marker highlight on title words.
  → our **News-Headline Re-Creation** static format (#9). Static version = no PIP persona.
- **cilocala static-ad vocabulary** (`scripts/cilocala_ads_gen.py`) — the gpt-image-2 i2i batch
  pattern (concept dict → 1:1 / 4:5, skip-if-exists, parallel). Concepts that port to legal:
  feature-board → Eligibility Board; review-proof → testimonial quote card; before/after split
  → Then/Now; UGC-native → Native Social-Post.
- **Disclaimer burn-in** (`scripts/burn_disclaimer_image.py`) — image counterpart of the video
  disclaimer; auto light-smallprint vs dark-band by background. Depo needs its OWN disclaimer
  (NOT Pulaski/Jones) — see below.
- **jdc_podcast_image / persona i2i** — gpt-image-2 i2i off a persona ref for photoreal humans.

## Compliance landscape — DO / DON'T (Depo)

Most competitors run **non-compliant payout language** we must NOT copy:
- ❌ "owed real money", "owed", "claim what's yours", "settlements pending", "6–7 figure
  settlements", "huge financial settlements", "life-changing settlement", "payouts",
  "entitled to compensation" (as a promise).
- ✅ Use: "**may qualify for significant compensation**", "**may be eligible**", "compensation
  **may** be available", "see if you qualify", "free, confidential case review", "no cost to
  check", "results not guaranteed". (Mirrors our locked tort phrasing; women's-prison lines use
  the fuller "significant **potential** compensation" — Depo phrase to be confirmed with user.)
- ❌ **NO disclaimer lingo in the ad copy or on the creative** (user-LOCKED — memory
  `feedback_no_disclaimer_lingo_in_copy`): do NOT add "Attorney Advertising",
  "Dramatization / not an actual client", or "prior results…" to FB primary text, headlines, or
  on-image footers. The "Attorney Advertising" seen in competitor swipe ads is a page-name
  artifact, NOT a disclaimer to copy; required disclaimers live on the landing/advertiser page.
  (This REVERSES an earlier draft of this doc that wrongly said "always include" — that guidance
  shipped disclaimer footers onto all 20 creatives + primaries before the rule was applied.)
- Keep the **explicit "meningioma / brain tumor" + "Depo-Provera" + eligibility window** on the
  creative (filters intake). Don't tell anyone to stop a prescribed medication (#371 wording).

## EXPANSION TO 20 formats — long + short copy mix (user direction)

Formats 11–20 add **long-form, testimonial/advertorial copy** (women's-prison voice:
first-person, short declaratives, "I trusted it," not-your-fault, anger at the manufacturer —
per `inventory/womens_prison_testimonial_research.md` + `feedback_copy_conversational_not_poetic`).
"Ad text" length = the **FB primary text** (caption); some formats also carry long text ON the
image (Open Letter, Reddit, Texts).

| # | Format | Copy len | Image carries | Swipe/source |
|---|---|---|---|---|
| 11 | **First-Person Testimonial Story** | **LONG** | photoreal relatable woman + pull-quote | #196 #210 #357 #559 (video testimonials) |
| 12 | **Advertorial "Here's Why"** | **LONG** | editorial layout / woman | #222 #217 #297 #502 |
| 13 | **Open Letter / Note** | LONG (on-image) | handwritten-note card | ad-format-ideation "Handwritten Letter" |
| 14 | **Reddit / Forum Post** | LONG (on-image) | faux thread chrome | native-UI angle |
| 15 | **Text-Message / DM Story** | MED (on-image) | phone-screen texts | ad-format-ideation "Text-thread" |
| 16 | **FAQ / Q&A card** | MED | Q&A layout | #303 #566 |
| 17 | **Then / Now Split** | SHORT | before/after split photo | ad-format-ideation "Then/Now" |
| 18 | **Myth vs Fact** | MED | two-panel flip | ad-format-ideation "Myth vs Truth" |
| 19 | **"Did You Know" PSA Fact** | SHORT | clean fact card | PSA framing |
| 20 | **Loved-One Referral** | SHORT | two women / supportive | #352 "Your sister." |

**Copy-length split across all 20:** LONG = #4(primary) #11 #12 #13 #14 · MED = #6 #7 #10 #15 #16 #18 ·
SHORT = #1 #2 #3 #5 #8 #9 #17 #19 #20.

### Flagship LONG-copy bodies (FB primary text — compliant, women's-prison voice)

**#11 First-Person Testimonial Story** (persona: ordinary, relatable woman 40s–50s)
> I was on the Depo shot for almost six years. Every three months, like clockwork. My doctor
> said it was the easy one — no pill to forget. I trusted it.
> Then the headaches started. The kind that don't go away. My vision would blur in the grocery
> store. I thought I was just tired. Stressed. Getting older.
> It was a brain tumor. A meningioma. I sat in that cold exam room and all I could think was —
> where did this come from? I did everything right.
> Nobody ever warned me the shot could do this. Not my doctor. Not the company that made it. I
> found out later there were studies. They knew.
> I'm not the type to sue anybody. But women like me may qualify for significant compensation,
> and it's free and private just to check. So I did.
> If you were on Depo-Provera and you've been diagnosed with a meningioma, please — just see if
> you qualify. You're not alone in this. 👇
> *(Attorney Advertising. Dramatization. Not an actual client.)*

**#12 Advertorial "Here's Why"** (the #222/#217 winner structure, compliance-rewritten)
> Doctors recommended it to women for decades. Now thousands regret it. Here's why…
> The Depo-Provera shot was sold as the simple choice — one injection every three months, no
> daily pill. Millions of women trusted it.
> Then the research came out. Women who used it for more than a year were found to be up to 5×
> more likely to develop a meningioma — a tumor in the lining of the brain. Some needed surgery.
> Some lost their vision. Most were never warned.
> Thousands of women are now thought to be affected, and a federal lawsuit is underway against
> the manufacturer.
> If you or someone you love used Depo-Provera and was later diagnosed with a meningioma, you
> may qualify for significant compensation. It's free and confidential to check, about a minute.
> You may not be the type to sue. You still deserve answers. 👇
> *(Attorney Advertising.)*

**#13 Open Letter** (on-image, handwritten-note styling) — short primary
> To every woman who was on the Depo shot — / If you've been diagnosed with a brain tumor (a
> meningioma), please read this. It may not be a coincidence, and it may not be your fault. The
> shot has been linked to these tumors, and most of us were never warned. You may qualify for
> significant compensation. It's free and private to find out. You're not alone. — Depo-Provera Claims

**#14 Reddit / Forum Post** (on-image faux thread) — medium primary
> r/legaladvice · u/throwaway_depo · "TIL the birth-control shot I was on for years is linked to
> brain tumors?" / Body: "I was on Depo-Provera ~2016–2021. Diagnosed with a meningioma last year
> and my sister sent me an article saying they're connected. Apparently there's a lawsuit now?" /
> ▲ top reply: "If you were diagnosed with a meningioma after Depo you may qualify for significant
> compensation — free to check." *(Dramatization. Attorney Advertising.)*

**#15 Text-Message / DM Story** (on-image phone screen) — short primary
> — "did you ever take that depo shot??" / — "yeah for years, why" / — "they're saying it's linked
> to brain tumors. meningioma. there's a lawsuit" / — "wait WHAT. i had surgery for that in 2022" /
> — "girl you need to check this. it's free, you might qualify for compensation 👇"

### Other new formats (on-image copy)

- **#16 FAQ:** "Q: I used Depo years ago — too late to file? A: Not necessarily. If you were
  diagnosed with a meningioma, you may still qualify for significant compensation — even years
  later. Q: Cost to check? A: Nothing. Free + confidential." — *Check eligibility →*
- **#17 Then/Now:** LEFT "2016 — One shot every 3 months. I trusted it." RIGHT "2024 — Brain
  surgery for a meningioma." bar: "Used Depo-Provera + diagnosed with a meningioma? You may
  qualify for significant compensation." — *See if you qualify →*
- **#18 Myth vs Fact:** "MYTH: It's been too long, nothing I can do. / FACT: If you used
  Depo-Provera and were later diagnosed with a meningioma, you may still qualify for significant
  compensation." — *See if you qualify →*
- **#19 Did You Know:** "Did you know? The Depo-Provera shot is now part of a federal lawsuit over
  brain tumors (meningiomas). Women who used it a year or more may qualify for significant
  compensation." — *See if you qualify →*
- **#20 Loved-One Referral:** "Your mom. Your sister. Your best friend. If a woman you love used
  Depo-Provera and was diagnosed with a meningioma, she may qualify for significant compensation —
  help her take the first step." — *Help her check →*

## Recommended FIRST image-ad batch (maximally different, all market-proven)

Build as a gpt-image-2 (KIE, 2K) batch like cilocala, EXCEPT text-precise cards (Quiz, Criteria
Board, News-Headline) render cleaner in **PIL** (CAWP F1 approach) — gpt-image-2 garbles dense
small text. Proposed lead batch of 5:

1. **Two-Question Quiz Gate** (#1) — the proven workhorse.
2. **"You Did Everything Right"** (#4) — emotional outlier vs the rest.
3. **Stat / Study Shock 5.6×** (#3) — credibility/number hook.
4. **News-Headline Re-Creation** (#9) — highest-trust, reuses F1 card engine.
5. **Native Social-Post** (#7) — best scroll-stop, doesn't read as an ad.

Then expand into Eligibility Board (#2), Symptom Self-Check (#5), Official Notice (#8).

## Open decisions (asked of user before producing)

- Advertiser identity + locked recovery phrase (drives disclaimer + logo lockup).
- Which formats in batch 1, how many variants each.
- Visual lane (photoreal-woman+clinical vs bold text-card vs faux-news/native-UI — varies by format).
- Aspect ratios (default 1:1 + 4:5 for FB feed; add 9:16 for Stories/Reels).
- Landing/CTA destination + whether to burn the disclaimer or leave for post.
