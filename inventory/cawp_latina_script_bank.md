# CAWP Latina script bank — 6 unused full-script hooks (drafted 2026-05-22)

Six Latina-focused UGC scripts for the Chowchilla/CCWF Pulaski & Jones campaign, each with a
vastly different hook angle. **Status: drafted + presented in chat only — NEVER produced.**
The campaign instead went the "winner body + hook-line variants" route (R9 Mija dozen = 12
user-picked hook lines grafted onto the untouched winner script, `scripts/cawp_r9_mija_gen.py`;
then R10 winner rounds). These six remain an unused bank of *full-script* alternative angles —
reach for them when the winner-script family fatigues and the campaign needs genuinely different
structures, instead of re-drafting from scratch.

All six already satisfy the locked campaign-copy rules: explicit "sexually abused" beat,
"significant potential compensation" verbatim, lawyers-DO-call-but-confidential (never "nobody
calls you"), every recurring beat paraphrased differently across the six. Each runs ~50–60s at
~2.4 wps (≈6–8 Veo clips). Phonetic respells (Chow-CHILL-uh, Mee-hah) are applied at generation
time, not in these scripts. **Re-verify compliance phrasing against current memory before
producing** — e.g. the "potential" drop is an IL-JDC-only exception; CA women's prison keeps the
full "significant potential compensation."

---

## 1 — SURVIVOR CONFESSION
**HOOK:** First-person disclosure ("it happened to me") · **LEVER:** Raw authenticity / "you're not alone" · **PERSONA:** Latina, 40s–50s, former CCWF inmate, intimate selfie

> "I never told anybody this. I was at Chowchilla.
> While I was inside, one of the guards… sexually abused me. And I carried it alone for years.
> I thought nothing could ever be done. I was wrong.
> Women who went through this are getting significant potential compensation now.
> And if you reach out, it's confidential — they're attorneys, they protect you. Your family never has to find out.
> I answered a few questions in two minutes. You can too. The link is right here, mija."

## 2 — DAUGHTER / FAMILY
**HOOK:** Family advocate ("for my mom") · **LEVER:** Love / acting on a loved one's behalf · **PERSONA:** Younger Latina, 30s, speaking about her mother

> "My mom did three years in Chowchilla. She never said a word about it.
> It wasn't until last year she told me a guard sexually abused her in there.
> I didn't know we could do anything. Turns out we can.
> There's significant potential compensation for women who were hurt like she was.
> I called for her — the lawyers kept everything private. Nobody at her job, nobody in the family knew.
> Two minutes to see if she qualifies. If your mom, your tía, your sister was in there — tap the link."

## 3 — NEWS-REACTION
**HOOK:** Scroll-stopper ("I almost missed this") · **LEVER:** Urgency + curiosity gap · **PERSONA:** Latina, 40s, animated, car or kitchen

> "I almost scrolled right past this — then I saw the word Chowchilla.
> If you were locked up at that prison, and a guard sexually abused you, you need to hear this.
> They're saying there's significant potential compensation for the women this happened to.
> And before you worry — yes, an attorney reaches out, but it's completely confidential. Private. Discreet.
> All it takes is a two-minute quiz to find out. Don't scroll past it like I almost did. Link's below."

## 4 — MYTH-BUSTER / "TOO LATE"
**HOOK:** Objection-killer ("you think it's too late") · **LEVER:** Removes the #1 barrier (time has passed) · **PERSONA:** Latina, 50s, calm, matter-of-fact

> "You think because it happened years ago, it's too late. Mija, it's not.
> If you were at the women's prison in Chowchilla, and a guard sexually abused you — it doesn't matter how long ago it was.
> There is significant potential compensation available right now.
> And you don't have to tell a soul. The attorneys keep it confidential — that's their job, to protect you.
> Two minutes. A few simple questions. That's all it takes to find out. The link is right there."

## 5 — DIRECT ELIGIBILITY QUESTION
**HOOK:** Direct callout / qualifier question · **LEVER:** Self-identification ("this is about ME") · **PERSONA:** Latina, 40s, warm, leaning into camera

> "Were you ever inside the women's prison in Chowchilla? Then stop and listen.
> If a guard sexually abused you while you were in there, you are not alone — and you have options.
> Women who were hurt like that may qualify for significant potential compensation.
> When you reach out, it stays between you and the lawyers. Confidential. Nobody shows up at your door.
> It's a quick two-minute check. Just tap below and answer honestly. That's it."

## 6 — ANGER / ACCOUNTABILITY
**HOOK:** Righteous anger / justice · **LEVER:** Accountability — make them pay · **PERSONA:** Latina, 40s–50s, controlled intensity

> "Those guards at Chowchilla thought no one would ever find out what they did.
> They sexually abused the women inside and counted on us staying silent. That silence is over.
> The women they hurt may qualify for significant potential compensation.
> And coming forward is safe — it's all confidential, handled quietly by attorneys who are on your side.
> Two minutes to take the first step. Tap the link, answer a few questions, and let them answer for what they did."

---

## Notes for whoever picks these up

- These are SCRIPTS, not approved ads — get the user's pick + explicit copy approval before any
  AdMachin staging (memory `feedback_approve_copy_before_admachin`).
- Production path when picked: break into per-clip beats on natural speech breaks → generate 4–6
  Latina reference characters per persona via gpt-image-2 (KIE, 2K, 9:16) → user picks anchor →
  standard clip-1-anchor pipeline.
- Persona direction proven since drafting: rougher/weathered Latina-Chicana personas outperform
  cleaner glam looks (approved lane `latr1/2/3/6/8/9/10` — memory
  `feedback_womens_prison_latina_persona_voice`); keep original Veo audio if replacement voices
  flatten per-person differentiation.
- Extra angles offered but never drafted: "whisper/secret," "letter to my younger self," "two
  friends who were both inside."
