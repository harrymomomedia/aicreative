---
name: admachin-video-ads
description: Create, analyze, script, generate, or QA AdMachin UGC video ads, especially AdSwipe transcript analysis, tort/legal lead-gen ads, women's prison/CIW/CCWF sexual-abuse compensation campaigns, Veo/Seedance/Kling clip workflows, persona images, and caption/disclaimer strategy. Use when the user asks for ad ideas, hooks, scripts, transcript analysis, viral ad analysis, video generation, stitched UGC ads, or sensitive legal ad production. For actual caption rendering, defer to the dedicated caption/disclaimer skills.
---

# AdMachin Video Ads

Use this skill to avoid re-learning hard-won production lessons from AdMachin ad sessions.

## First Principles

- For AdSwipe, analyze transcript-first. Viral metrics are sparse; do not overfit to the few ads that show them.
- For tort/legal lead-gen, the first 5 seconds must say: who it is for, what happened, and that the person may qualify for significant potential compensation.
- For JDC sexual-abuse lead-gen, do not say only "abuse" when describing the qualifying harm. The qualifying topic must be explicit: "sexual abuse" or "sexually abused."
- Use legally careful language: "may qualify," "could be eligible," "potential compensation," or "significant potential compensation." Never guarantee money, payouts, settlements, or outcomes.
- Keep UGC copy spoken-simple: short lines, one idea per sentence, no legalese, no over-polished AI voice.
- When the user asks for a specific community voice, capture rhythm and directness without caricature or exaggerated slang.

## Sensitive Legal Caption Rules

This skill chooses the caption strategy. For execution details, use the dedicated skills:
`yellow-text-sub`, `hormozi3`, `nick-subtitle`, and `pulaski-jones-disclaimer`.

For sexual abuse, prison abuse, juvenile detention, medical injury, or other trauma/legal ads:

- Do not use per-word flashing captions, emoji-heavy captions, or loud kinetic subtitle styles.
- Avoid `caption_styled.py` / `yellow-text-sub` unless the user explicitly asks for that exact look after seeing alternatives.
- Prefer calm phrase captions: Nick, simple `caption.py`, or `caption_hormozi3.py --no-emoji`.
- When the user asks for **Nick**, prefer the internal `caption_nick.py` path over the Submagic API so the transcript stays verbatim.
- Keep disclaimer readable and calm; it should not compete with the survivor-facing message.
- For regulated legal copy, prefer in-house caption scripts where the wording can be controlled. Real Submagic/API can alter words.

## Tort Script Rules

- Mention facility specificity early when relevant: "CIW Chino and other California women's prisons."
- Avoid "private check"; it can sound like a payment/check. Prefer "private form," "private page," "free case review," or "private questions."
- If Veo/Scribe keeps confusing a spoken word, rewrite around it. Example: if "form" becomes "forum," use "private page" or "answer a few private questions."
- Connect abuse to action clearly: "If staff sexually abused you, you may qualify for significant potential compensation."
- If the user is testing scripts, do not make every ad the same structure with different wording. Change the premise, speaker role, opening logic, proof type, and CTA framing.
- Do not make every concept a testimonial. Rotate formats: direct notice, comment debate, news-style explainer, advocate PSA, checklist, myth-busting, family member, case-worker tone, overheard conversation, "things no one told you."

## Prompting And Creative Development

- Start from the user's persuasion goal, not from the first format suggested. If the user says the ads sound the same, change the speaker, frame, and visual format.
- Write hooks as complete 2-3 sentence openings when the user is choosing concepts; a title alone is not enough to judge a 40-second ad.
- Use structure diversity for tests: direct eligibility notice, story cold open, comments/debate UI, document/checklist, faux local commentary, family-member perspective, advocate/case-worker perspective, myth-busting, "what they did not tell you," and facility-specific notice.
- If the user says the original ad is a winner and wants "the same angle," preserve the winning framing/camera position and beat order only as the scaffold. Rewrite the discovery mechanism, sentence rhythm, and speaker logic so each variation sounds like a different person, not a synonym-swapped clone.
- Keep the compensation point close to the abuse point. Do not let story texture bury the action: "sex abuse -> may qualify for significant potential compensation."
- For dialect or community voice, aim for plainness, cadence, and local directness. Do not overdo slang or write a caricature.
- If a model repeatedly mispronounces or mishears a phrase, prompt around the meaning instead of forcing the same phrase.
- For sensitive legal prompts, avoid piling multiple moderation-sensitive details into the same generation. Split age/minor references, sexual-abuse wording, lawsuit wording, and intense visual descriptors across clips when needed.

## Prompt Transparency

- Whenever generating images or videos, show the exact model/provider and the full prompt in chat.
- For image generation, show the prompt/model when submitting the job, not only after the asset lands.
- When using image-to-video, keep the prompt short and action-only; the scene and styling are already in the anchor image.

## Podcast / Announcer Register

- Confession / podcast monologues should feel like one person talking to someone else in the room: off-camera gaze, conversational cadence, natural pauses.
- Announcer / winner-clone reads should be direct-to-lens. Do not put a hype direct-response script on an off-camera confession visual.
- In podcast/interview format, audible `mm-hmm` / `yeah` reactions are acceptable. Keep them in audio if natural, but filter them out of captions.
- Do not invent props such as headphones or microphones unless they are intentionally part of the persona. If a prop keeps appearing inconsistently, inspect the prompt first before rerolling anchors.
- Veo renders `Ayo` badly. Use one clean opener such as `Yo, Illinois. Listen up.` or `Listen up, Illinois.` instead of stacking slang bursts.

## Caption Scaling

- Caption font size for 9:16 vs 4:5 should be sized from OUTPUT WIDTH, not height. The horizontal reading width is what stays perceptually constant on phone/feed playback.
- If a 9:16 caption line uses about 70% of the screen width, the 4:5 version should use about the same percentage of width; do not let 4:5 captions shrink just because the frame is shorter.

## Persona Image QA

- Pick animation-safe anchors: medium close-up or chest-up, face visible, mouth unobstructed, hands low or out of frame.
- Avoid hands/fingers close to camera, extreme gestures, blocked mouth, heavy shadows, tight crops, or photos that read too young for adult legal campaigns.
- For California women's-prison UGC, rougher/weathered Latina or Chicana personas generally outperform cleaner or glam-looking portraits. Start there unless the user asks for a different audience.
- For sensitive Veo prompts, reduce moderation risk by avoiding compounding visual triggers such as aggressive tattoo descriptors, car settings, or race words paired with sexual-abuse/lawsuit language. Use accurate, neutral visual description.
- For survivor/victim personas, bias toward **ordinary documentary realism**, not polished portraiture: average-looking adult, tired eyes, uneven skin tone, slight wear, no smile, no glamour, no beauty retouching, no "influencer" feel.
- If the user provides an existing photo and says "keep the background, only swap the person," default to a background-preserving edit path such as `nano-banana-2`. `gpt-image-2` edit mode often re-stages the whole scene and beautifies the subject instead of preserving the original environment.

## Veo / Clip Workflow

- For Veo Lite/free Google Flow, route through `googleflow_client.generate_veo` with `model="veo-3.1-lite-low-priority"` unless the user requests otherwise.
- Verify clip 1 before generating the rest: check face, voice, framing, pronunciation, tone, lip-sync, and legal phrasing.
- Once clip 1 passes, generate clips 2-N in parallel if the user wants speed.
- If every clip in a video uses the same approved persona anchor, keep raw Veo audio by default; only use ElevenLabs voice changer when it solves real cross-clip drift or multi-video host consistency.
- If external dubbing/voice replacement makes multiple personas sound too similar, keep the original model audio for now. Raw Veo audio usually preserves more person-to-person variation than samey external passes.
- Use clip-1 anchor rotation for multi-clip talking-head ads. Choose eyes-open, forward-gaze anchor frames.
- For reporter/interviewee or other 2-speaker scenes, **lip-sync alone is not enough**. Check each speaking turn with `scripts/voice_consistency.py` or a quick F0 comparison; if both speakers land in nearly the same register/timbre, treat it as a same-voice failure and split to one speaker per clip.
- Kling 3.0 element refs usually hold two identities better than Veo Lite on interview-style clips, but keep continuous 2-person takes short (~7s). Kling can auto-cut mid-clip even with `multi_shots=false`.
- Dense 8-second dialogue can cause end-of-clip wobble. Shorten the line rather than trying to hide the transition.
- Check the last 0.5-1.0 seconds of every clip for trailing words, face morphs, ghost tails, and silent drift.
- Build clip scripts on natural speech breaks. Do not cram too many questions into one 8-second clip when legal wording must stay clear.
- Do not fix cut-off words, dead air, repeated audio, disappearing props, or bad gestures with frozen frames, speed changes, stabilization, or frame holds unless the user explicitly approves that exact post process. Re-trim at original speed or re-roll the failing clip.

## Audio / Finalize

- For a single ad generated from one persona seed, prefer raw model audio plus loudness leveling. Use `voice_changer` when the same persona must sound consistent across multiple ads, when timbre drifts, or when music / room bleed must be removed.
- Trim to the scripted words, not only silence. Trailing improvised words survive silence trim.
- If a clip starts speaking immediately (first word under ~0.1s), prepend about `0.15s` of frozen first-frame plus silence before `voice_changer` so the opening word does not come out weak.
- Clone a persona voice once from the cleanest clips and reuse that `voice_id` across every variant for that persona.

## Seedance / useapi B-Roll Workflow

- For high-volume Seedance b-roll, use `useapi_client.generate_seedance` with `model="seedance-2"`, `resolution="480p"`, `aspect_ratio="9:16"`, and short 4-second clips when the user wants fast atmospheric coverage.
- useapi's `/runwayml/` endpoint is just the platform namespace; `model="seedance-2"` is still ByteDance Seedance, not Runway Gen-4.
- Explore mode can sit `THROTTLED` for hours and has a shallow queue. Keep polling for hours, persist task IDs, and use submit-side 429 backoff instead of treating 429s as final failures.
- For juvenile detention / JDC abuse-adjacent b-roll, avoid prompt combinations that pair youth/minor language with body-search, shower/towel, bunk/bed proximity, or an adult guard physically looming over a minor. Seedance commonly rejects these as `SAFETY.INPUT.TEXT` / `CHILDREN`.
- Safer implication shots for JDC sexual-abuse-adjacent b-roll: closed office doors, doorway silhouettes, peepholes, CCTV shadows, logbooks, personnel files, empty clothing on a bunk, laundry evidence, untouched trays, exterior night, stairwells, yard corner whispers, and redacted court documents.

## Claymation / Stylized Sensitive Explainers

- Seedance has no claymation preset. Put the style in the prompt and reuse the same style block across every shot so the batch cuts together.
- For claymation people shown below the neck, explicitly specify clothing like "wearing a t-shirt" or "wearing a hoodie." Otherwise Seedance can render nude or shirtless clay figures.
- For child / officer / lockup / abuse-adjacent clay shots, prefer KIE Seedance. OpenRouter moderation is stricter on sensitive outputs; save OpenRouter for benign or faceless shots.
- For survivor explainers, start on the affected person when possible. A face-first / taken-away / police-car / lockup opening lands harder than a building-first establishing shot.
- On proof beats, be literal. "Saw the news" should show the person seeing news and reacting; "other people" should show a group, not a single generic cutaway.
- On justice / relief beats, switch to a frame that is already bright and emotionally resolved from frame one. Slow smile transitions usually miss the line.
- End on human resolution such as reunion, release, or community. Avoid symbolic or abstract endings when the script wants concrete closure.
- Keep the abuse itself off-frame. Show fear, power imbalance, closed doors, looming shadows, surveillance, aftermath, and reaction instead of depicting the act.

## Replicate p-video Fallback

Use `prunaai/p-video` only when the user asks for it or Veo policy blocks a simple talking-head/reporter ad.

- Use image-to-video with native model audio for talking heads. Do not pass external audio by default.
- Chunk at about 10 seconds. The model can attempt 20s, but 10s chunks gave better lips, pacing, and fewer odd sounds.
- Keep prompts short: fixed camera, fixed frame, no zooming, no panning, no screen text, no graphics, clean native audio.
- If it hallucinates subtitles or lower-third text, re-prompt shorter with "No screen text, no graphics, no labels, no captions, no subtitles."
- The camera may still breathe slightly. The user accepted this as a model limit; do not try to hide it with ffmpeg unless explicitly approved.
- Post every generated chunk/final video link before QA, verification, stitching, captions, or other post-production.

## Stitching And QA

- Clean masters, captioned versions, and disclaimer versions should be separate files.
- Show each generated video to the user immediately with a backticked local path before deep QA or post-processing.
- After stitching, create a boundary/contact-sheet check around every clip join.
- Default join style is hard jump cut unless the user asks for a transition.
- If a boundary looks like a soft dissolve, suspect the generated clip tail first. Trim or reroll the clip; do not assume ffmpeg caused it.
- Do not burn captions by default. Burn captions only when the user asks for captions/subtitles/disclaimer on the deliverable.
- Once a concept is approved, rename outputs and finals with descriptive slugs (`confession`, `sister-call`, `read-twice`, `direct`) instead of leaving deliverables as only `A/B/C/D` or `v3d`.

## Session Memory Pattern

When a mistake costs time, money, or quality, write it down in one of these places:

- `CLAUDE.md` for always-on project rules.
- `skills/admachin-video-ads/SKILL.md` for reusable ad-production behavior across sessions.
- `inventory/<campaign>_learnings.md` for campaign-specific language, selected persona, rejected styles, final asset paths, and QA findings.

Keep an explicit "do not repeat" note for rejected outputs, not just approved settings.

When the user asks to save learnings from a finished session, use the `session-memory-pass` skill to decide what belongs in campaign memory, global project rules, or reusable skills.
