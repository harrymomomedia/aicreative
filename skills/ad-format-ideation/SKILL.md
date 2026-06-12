---
name: ad-format-ideation
description: Brainstorm UNIQUE video-ad format concepts beyond the standard "person talks to camera" testimonial, for legal / tort / UGC lead-gen campaigns. Use when the user asks for new ad ideas, different / unique / fresh ad formats, "more ideas", ways to vary a campaign that has over-indexed on one format, or non-testimonial concepts. Holds the messenger/technique/hook taxonomy, a ready palette of ~19 archetypes, and the compliance rules for legal-ad messengers.
---

# Ad-Format Ideation

Use when a campaign needs **format variety** — especially when it has been running the same
"a person tells their story to camera" testimonial over and over. The user wants formats
that look *nothing like* what's already shipped.

> The palette below is a **brainstorm starting point, not a list of validated winners.**
> Performance is unproven; use it to escape the blank page and the testimonial-default, then
> let the user pick what to produce.

## Process (cadence the user prefers — do NOT run the heavy spec flow)

For creative ad-concept work this user wants **speed, not process**:

1. **Check what's already shipped** for the campaign (scan `outputs/` + `scripts/` + the
   campaign's `inventory/*` file) so you propose genuinely new formats, not re-skins.
2. **Aim with a few sharp questions** — bundle 2–3 multiple-choice questions in ONE
   `AskUserQuestion` call (format axis / messenger latitude / dramatization latitude).
   Do NOT drip one question at a time, and do NOT write a formal brainstorming spec doc or
   invoke `writing-plans` — that flow is for code. (`feedback_skip_planning_for_production`.)
3. **Present a concept MENU** — distinct concepts, each with: logline, messenger, a compact
   40s beat arc, the visual technique, why it's different, and the production path in our
   stack. Recommend a first batch of ~3 that are maximally different from each other.
4. **Produce on approval** — then the normal production rules apply (persona/anchor → one
   test clip per format through the QA gate before committing the full 40s).

## The 3 axes of "different"

Vary along any of these — the strongest menus mix all three:

- **Messenger / POV** — who carries the message.
- **Visual technique** — how it looks.
- **Hook mechanic** — what stops the scroll.

## Palette (≈19 archetypes)

### Messenger-driven
| Format | Logline | Faceless? | Production path |
|---|---|---|---|
| Mock news segment | Anchor + field reporter "cover" the settlement, chyron + facility b-roll | no | nano-banana facility b-roll + reporter persona Veo i2v, or PIP reporter over b-roll (`outputs/ca_jdc_tv_reporter*`) |
| Attorney / advocate explainer | Authority figure, direct-to-lens, plain explainer | no | gpt-image-2 persona → Veo i2v, announcer register, gaze in lens. **Generic advocate, NOT a named-attorney likeness** |
| Family member (daughter / sister) | Speaks for the survivor who couldn't | no | Veo i2v talking head |
| Ex-staff whistleblower | Anonymized insider, silhouette / back-to-camera, lowered voice | partial | Veo i2v + shadow framing; keep anonymized |
| Chorus of voices | Montage, many people each say one fragment ("I was there." "Me too.") | no | several personas, single-line clips, montage cut |

### Visual-technique
| Format | Logline | Faceless? | Production path |
|---|---|---|---|
| Claymation metaphor | Aardman stop-motion, VO + metaphor beats | n/a (VO) | Seedance claymation (`jdc_claymation_*`) + `eleven_v3` VO + Hormozi caps. **Clothe figures; reaction/metaphor only, never the act/a minor** |
| Text-thread / DM reenactment | Whole ad is a phone screen — someone forwards the news + the intake form | yes | PIL/ffmpeg phone composite + `tts()` VO |
| Form walkthrough / screen demo | Clean screen-cap of the 2-min intake — shows it's fast + private | yes | screen-style composite + VO |
| Then / Now split-screen | Institutional past vs free present, side by side | maybe | ffmpeg split + two b-roll sources |
| 2D motion-graphic explainer | Flat animated explainer, neutral narrator (non-clay) | yes | motion-graphic build + VO |
| Handwritten letter | Pen over paper ("Dear me, twenty years ago…"), VO reads | yes | document push-in + VO |
| Found-document / archival reveal | Slow push-ins on dramatized docs (intake form, clipping, complaint) | yes | Ken-Burns docu-zoom (`jdc_a_docu_zoom.py`) + VO |
| Justice / symbolic b-roll | Scales, empty witness chair, closing case file — gravitas | yes | b-roll + VO |

### Hook / on-screen-text
| Format | Logline | Faceless? | Production path |
|---|---|---|---|
| "3 things" listicle | Numbered cards, punchy, works on mute | yes | `caption_hormozi3.py` + VO + b-roll |
| Myth vs Truth | Objection-killer flips ("MYTH: too late → TRUTH: window's open") | yes | on-screen text + b-roll |
| The Numbers / data reveal | Kinetic count-up ("One facility. Decades. Thousands.") | yes | motion graphics + VO |
| Voicemail / audio-first | Near-black + waveform + captions; audio is a hotline / voicemail | yes | minimal composite, audio-led |
| Public notice / class-action card | Formal narrator, typographic, mimics a legal notice | yes | typographic build + VO |
| POV "you're scrolling" | Hands hold a phone that lands on this very ad (meta) | yes | POV hands + screen composite |

## Compliance rules for legal-ad messengers (carry into EVERY concept)

- **Never generate an AI persona that impersonates the real named attorneys** (e.g.
  Pulaski / Jones). Use a generic advocate / "legal team" figure. Naming a fabricated face
  as the actual firm's lawyer is a real compliance risk.
- Keep the campaign's locked recovery phrase. Women's-prison lines use the **full
  "significant potential compensation"**; IL JDC drops "potential" → "significant
  compensation" (`feedback_significant_potential_compensation`).
- Include an **explicit "sexual abuse" beat** (filters intake).
- **Confidential / private**, lawyers **do** reach out — never "nobody calls you"
  (`feedback_lawyers_do_call_privacy_safe`).
- Low-risk framing: "no court", "no cost to ask", "about two minutes", "see if you qualify".
- **Paraphrase recurring beats across variations** (`feedback_paraphrase_across_variations`).
- **One speaker per clip** on Veo — two voices in one clip collapse to the same pitch.
- Sensitive depiction: never the act or a minor; show reaction / power-imbalance metaphor
  (looming shadow), documentary distance, or claymation.
- Captions on sensitive legal ads stay calm (Nick / phrase-style), not flashing per-word
  (`admachin-video-ads` skill).
