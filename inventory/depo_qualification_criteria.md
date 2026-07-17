# Depo-Provera ("Pulaski" leads) — QUALIFICATION CRITERIA + INTAKE SPEC

Source: MTM (Michael Orell) email chain + attachments, read 2026-07-17. Campaign context:
`project_depo_meningioma_campaign`. Funnel: depop.justicecovered.com. FB campaign: "Depo - Pulaski HJ".

---

## ⚠️ UNRESOLVED — the DX + usage dates conflict THREE WAYS. Do not guess. Ask MTM.

The covering email says *"There was some confusion on the DX dates, and this will clear it up"* — but
the two attached criteria docs **disagree with each other AND with the April 3 email**:

| Source | Diagnosed | Used product |
|---|---|---|
| `Depo_Criteria_DX_ONLY.docx` | **1992+** (no upper bound) | 1/1/**1992** – 12/31/2019 |
| `Depo_Criteria_DX_ONLY (1).docx` | **1992 – 2019** | 1/1/**1992** – 12/31/2019 |
| **Email, Michael Orell, Fri Apr 3 2026 1:54 PM** | **2005+** ("moving from 1992 to 2005, not 2010") | 1/1/**2000** – 12/31/2019 |

The April 3 email explicitly says *"Please update all questionnaires, lead forms, and intake"* — but
**neither attachment reflects it**. So either the attachments are stale, or the April 3 change was
reverted. **This is worth real money — DX 1992+ vs DX 2005+ is a completely different audience and a
completely different funnel.** Escalate to MTM before touching copy, brackets, or intake.

**Until resolved, assume the TIGHTER set (April 3 email is the most recent dated instruction):**
diagnosed **2005+**, used **1/1/2000 – 12/31/2019**.

---

## Who the leads go to

**Pulaski Kherkher, PLLC + BD Law, PLLC** (contract: `Depo_PK_BD_Hickory_28_12 Contract.doc`).
40% contingency (28% Pulaski / 12% BD Law), $200 flat admin fee, minimum 90 days to evaluate a claim.
Client must not already be represented. CRM CaseType = **"Depo - BD Hickory - MoMo Media"**;
LeadProvider = **"MoMo Media"**.

## The criteria — what makes a lead signable

1. **1-year MINIMUM use of BRAND Depo-Provera** (injectable contraceptive) = **4+ shots**, one every
   3 months. **"MINIMUM" = ≥1 year, so exactly 4 shots qualifies** — the line is 4 inclusive.
   **It is OK to sign if she is unsure brand vs generic.**
2. **Diagnosed with brain/head meningioma AFTER the 1 year of use.** ⚠️ This means after the first
   year *accumulates* — **NOT** after use ends. A woman who started 2005, was diagnosed 2009, and
   stayed on it until 2015 qualifies: she banked 4+ shots by 2006. **The diagnosis can land mid-use.**
3. **Diagnosis date** — ⚠️ see the conflict table above (1992+ / 1992–2019 / **2005+**).
4. **Usage window** — ⚠️ see the conflict table above (1/1/1992 / **1/1/2000** – 12/31/2019).
5. **DX ONLY** — the program has moved to diagnosed-only. No "at-risk"/undiagnosed leads.
   (Consistent with `feedback_target_diagnosed_not_atrisk`.)
6. **Intake questions must be OPEN-ENDED, not yes/no** — e.g. "What were you diagnosed with?",
   "Where is the injury located?" Weeds out fraud: a yes/no hands the claimant the answer.

**No latency rule appears anywhere in MTM's criteria.** The wider litigation commonly requires a
diagnosis within ~10 years of the last injection (Siddons, Drugwatch) — **MTM has never said this
applies.** Do not design around it; ask them.

## Qualifying Depo products (any of these)

Depo Provera · Depo-Provera · DPCI · Depo Provera IM · DMPA · Depot medroxyprogesterone acetate ·
Medroxyprogesterone Acetate · MPA · IM MPA · Depo-SubQ Provera 104 · Greenstone Medroxyprogesterone ·
Greenstone MPA · Prasco Medroxyprogesterone · Prasco MPA

## Qualifying brain/head meningioma variations

Intracranial · Intercranial · Cranial · Brain meningioma · Meninges tumor ·
**Arachnoid tumor (but NOT arachnoid cyst)** · Convexity · Falcine · Parasagittal · Intraventricular ·
Skull base · Sphenoid wing · Olfactory groove · Posterior fossa/petrous · Suprasellar · Recurrent ·
Foramen magnum · Meningothelial · Fibrous · Psammomatous · **Angiomatous · Secretory**
*(the last two are in the attachments but were missing from our earlier copy)*

⚠️ **SPINAL meningioma does NOT qualify** — the criteria are brain/head only. Note the CRM's
"Location of your meningioma(s)?" dropdown offers **Spine** as an option; capturing it is fine,
but it is not a qualifying location.

---

## Data MTM REQUIRES to sign a retainer (the July escalations)

**Email — Thu Jul 16 2026:** *"We are getting quite a few Depo intakes with important Dx/RX
information missing, or the client 'does not recall'. We must have the diagnosing doctor
name/hospital and the prescribing doctor/pharmacy name to sign a retainer. This has to happen at the
intake level."* Plus: **must be posted via API — the PDF is mostly a backup**; opening PDFs is too
slow for the docket team.

**Email — Fri Jul 17 2026 (the newest, and the sharpest):**
- **Must collect the RX facility / clinic / location ADDRESS.** *"Simply putting Walmart or Planned
  Parenthood will not help us prove up usage."*
- **"Generic pharmacy info doesn't help either because that is not where it was administered. We need
  to know WHERE THE SHOT WAS GIVEN."**
- **Ask whether it was done by a physician, another healthcare provider, or SELF-ADMINISTERED.**
- *"We are getting the DX information needed; we need to make sure the RX detail is being collected."*

**→ This confirms our own read: "which pharmacy" is the WRONG question.** Depo is administered
in-clinic, not dispensed, so a pharmacy name is worthless for proving usage. The question that
carries the RX data is **"where was the shot given — clinic name, full address, phone"**.
(Self-administration is real for **Depo-SubQ Provera 104**, which is why they ask.)

**⚠️ FIELD-NAMING TRAP:** the CRM's fields are called **"Usage N Pharmacy Name / Address / Phone"** —
but per the Jul 17 email they must be filled with the **ADMINISTERING facility**, not a dispensing
pharmacy. An agent who dutifully types "Walmart" into the Pharmacy field is generating a rejected
lead. Brief the agents on this explicitly.

---

## The API — LawRuler (Pulaski)

Spec: `Depo_Hickory_MOMO_FG.xlsx` (field guide).
- **Endpoint:** `https://pulaski.lawruler.com/lawruler-parsing.aspx`
- **Key:** in the FG spreadsheet. **NEVER commit it — reference the file, not the value.**
- `LeadProvider = MoMo Media` · `CaseType = Depo - BD Hickory - MoMo Media` · `Hear = <intake>`
- `Status = Signed Contract Intake Complete` | `Signed Contract Reject Letter Needed`

**Field map (the qualification-relevant subset):**

| Data | API field |
|---|---|
| Start / Stop date (overall) | `Custom4551` / `Custom4552` |
| What were you taking Depo for? *(Birth Control · Regulate Cycle · Endometriosis · Unknown · Other)* | `Custom4651` |
| Usage 1 — generic? / start / stop | `Custom4553` / `Custom4554` / `Custom4555` |
| Usage 1 — "Pharmacy" name / **address** / phone → **the ADMINISTERING facility** | `Custom4556` / `Custom4557` / `Custom4558` |
| Usage 2 — generic? / start / stop | `Custom4559` / `Custom4560` / `Custom4561` |
| Usage 2 — "Pharmacy" name / **address** / phone → **the ADMINISTERING facility** | `Custom4562` / `Custom4563` / `Custom4564` |
| Diagnosed with meningioma? / Diagnosis date | `Custom4565` / `Custom4566` |
| How many meningiomas / Location *(Head·Brain·Spine·Other)* / Treatment *(Radiation·Surgery·Medication·Monitoring·Unknown)* | `Custom4652` / `Custom4653` / `Custom4654` |
| **Prescribing** doctor / facility / address / phone | `Custom4567` – `Custom4570` |
| **Diagnosing** doctor / facility / address / phone | `Custom4571` – `Custom4574` |
| Treating doctor / facility / address / phone | `Custom4575` – `Custom4578` |
| PCP name / address / phone | `Custom4579` – `Custom4581` |
| Other doctor / facility / address / phone | `Custom4582` – `Custom4585` |
| Medical notes / Notes | `Custom4586` / `Custom4587` |

Contact/OBO/emergency-contact fields also exist (`FirstName`, `LastName`, `CellPhone`, `Email1`,
`Address1`, `City`, `State`, `Zip`, `DOB`, `SSN`, `Custom4542`–`Custom4550`, `Custom4588`–`Custom4592`).
**The CRM supports TWO separate usage periods** — a woman with two stints is fully capturable.

## Gaps / questions for MTM

1. **THE DATES.** Which governs — the attachments (DX 1992+/1992–2019, use from 1992) or the Apr 3
   email (DX 2005+, use from 2000)? Everything downstream depends on this.
2. **Does the ~10-year-from-last-injection latency rule apply?** It's standard across the wider
   litigation and absent from their criteria.
3. **There is no API field for "physician / other healthcare provider / self-administered"** — the
   Jul 17 email demands it but the FG has nowhere to put it. Which field? (`Custom4586` Medical
   Notes?) Or is an FG update coming?
4. **Imaging confirmation (MRI/CT)** is a common criterion and is absent from theirs — required?
5. **Statute of limitations** — screened by them, or expected from us?
6. **Non-contraceptive indications:** the criteria say "injectable *contraceptive*", but `Custom4651`
   allows Regulate Cycle / Endometriosis. Do those qualify?

---

## CREATIVE IMPLICATIONS (what this changes in our ads)

Our shipped Depo copy qualifies only on **"diagnosed with a brain meningioma after using the Depo
shot"** — it does NOT filter on duration or the usage window, so we pay for leads that can't be
retained. Add:

- **Duration filter — the big one:** say **"a year or more"** / **"4 or more shots"** /
  **"every 3 months for at least a year"**.
- **Date-window filter:** pending the conflict above — **either** "any time between 1992 and 2019"
  **or** the tighter "between 2000 and 2019". **Don't ship either until MTM confirms.**
- **Order of events:** "used it for a year or more, and were **later** diagnosed" — but remember the
  diagnosis may land *mid-use*, so don't imply she must have stopped first.
- **Keep the wording locks:** still **"brain meningioma"**, still **never "tumor"**
  (`feedback_meningioma_only_targeting`). The firm's own list contains "meninges tumor" /
  "arachnoid tumor" — that is *their* intake vocabulary, NOT our ad-targeting vocabulary.
- **Don't turn the ad into a yes/no quiz.** Criterion 6 is about the intake form, but it rhymes: the
  ad states the qualifying facts and lets the intake screen.

---

# AUDIT: the LIVE funnel at depop.justicecovered.com (walked 2026-07-17)

**The live form is 4 questions → contact details. It captures NONE of the data MTM requires.**

1. "Did you or a loved one received Depo-Provera medication on a regular basis?" → Yes/No
2. "Were you diagnosed with Meningioma after taking the Depo Provera?" → Meningioma / Other type of
   brain tumor / Other injury / **"No injury (You do not qualify)"**
3. "Approximately how long did you or a loved one take Depo-Provera…?" → **1 year / 2 years /
   3 or more years / Never took Depo-Provera**
4. "Currently represented by an attorney?" → Yes/No → contact details → RECEIVE RESULTS

**The API-vs-PDF debate is moot for the FORM — the Dx/Rx data is never collected there, so there's
nothing to post.** That data has to come from the agents (see the plan below); the API posting
obligation is real and lands on whoever writes the CRM record.

### The three bugs

1. **Q2 signposts the losing answer** — the option is literally labelled **"No injury (You do not
   qualify)"**, and "Meningioma" is served as choice #1. It teaches every claimant which box to avoid
   and which to pick. Catastrophic for fraud; zero-cost to fix.
2. **Q3 manufactures qualifying answers — the root of the unqualified intakes.** The LOWEST real
   option (**1 year**) **IS the qualifying minimum**. A woman who took it for 3 months has no honest
   choice ("Never took Depo-Provera" is false), so she clicks "1 year." The form *generates* the exact
   leads MTM is rejecting. **"1 year" is therefore a contaminated bucket** — it holds both the best
   leads (genuine 4-shot users = MTM's exact line) and the worst. **You cannot qualify OR disqualify
   on it.**
3. **Q1 is a leading yes/no that names the drug** → free "yes" for anyone.

### Also seen / unverified

A question exists somewhere reading *"Have you or a loved one used Depo-Provera at least once in the
12 month period prior to diagnosis?"* — **not encountered on the walked path** (may be conditional).
If it is live and gates anything, **it is a leak**: "at least once" is a 1-shot bar (MTM wants 4+),
and a 12-month recency window is far tighter than any MTM criterion — it would disqualify a woman who
used 2005–2015 and was diagnosed 2018, who is a good claimant. Find what it's wired to.

---

# THE PLAN — ADDITIVE ONLY (user-locked 2026-07-17)

**Two hard constraints from the user:**
1. **This is a MARKETING funnel, not a legal intake. Volume is the goal.** **NEVER ask doctor name /
   hospital / pharmacy / addresses in the funnel** — typing + memory questions are where a form bleeds
   leads. **The AGENTS collect all of it on the call.** *That is the answer to MTM's "this has to
   happen at the intake level": **the agents ARE the intake.*** No post-capture enrichment step either.
2. **DO NOT touch the existing questions — UTM + pixel are tied to their conditions.** Reordering,
   rewording or re-optioning a tracked step breaks the pixel conditions and resets FB's learning on
   the conversion event.

**The form disqualifies NOBODY.** We already paid for the click; blocking her at the form recovers
nothing, while a captured non-qualifier can still be re-qualified on the call, referred, or routed.
**Capture everyone, score in the CRM.** Disqualification is a routing decision, not a form decision —
which is exactly why the `"(You do not qualify)"` label is a bug: the form doing the CRM's job, and
only teaching people to lie.

## The whole form fix: ONE new option, zero new questions

**Add "Less than 1 year"** (and optionally "Not sure") **to the existing duration BUTTONS FIELD.**
No new screen, existing options untouched, so any pixel condition keyed on "1 year" / "2 years" /
"3 or more years" fires exactly as before. It gives the sub-1-year user somewhere honest to land, so
"1 year" stops being a dumping ground and starts meaning **4 shots = MTM's exact line**. The question
you already have starts doing its job.

**Check before saving:** what does the field's conditional logic do with an answer it doesn't
recognise? If a condition enumerates the qualifying options, "Less than 1 year" falls to the else —
make sure the else doesn't dead-end her. She continues to contact like everyone else.

**Optional, not recommended:** a separate shot-count question (1·2·3·4–6·7–12·13–20·20+·Not sure).
More precise than self-reported duration, but the gap is small and the agent catches it. Costs a screen.

**Cut:** the usage-window question and the diagnosis-year question. The window barely bites, and the
latency rule that would justify a DX-year question **isn't in MTM's criteria**. Revisit only if MTM
confirms the dates (Q1) and the latency rule (Q2) above.

## What the AGENT script must now capture (this is where MTM's demands land)

- **DX:** diagnosing doctor name · facility name · **full address** · phone · diagnosis date ·
  how many meningiomas · location (brain/head — flag spine) · treatment
- **RX:** prescribing doctor · **and critically — WHERE THE SHOT WAS GIVEN**: clinic/facility name,
  **full street address**, phone. **"Walmart" / "Planned Parenthood" alone = a rejected lead.**
- **Who administered it:** physician / other healthcare provider / **self-administered**.
- **Per usage period** (the CRM holds two): generic? · start · stop.
- **"Does not recall" is a call-script problem, not a form problem.** Scaffold down rather than
  accepting the blank: provider TYPE → city/state → facility → insurer at the time. Any one of those
  lets the docket team find the provider; all are far easier to recall than a name from 2003.
- **Post via API, not PDF** (MTM, Jul 16).
