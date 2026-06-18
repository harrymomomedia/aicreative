# CA JDC Campaign Learnings

Durable notes for Tort / CA JDC legal lead-gen work. Keep campaign-specific
details here so the global rulebook does not get bloated.

## AdMachin State

- Project: `Tort` (`e15c60bd-95c2-47b9-9730-c29fb5325461`).
- Subproject: `CA JDC` (`f1ce41d8-4098-4f92-80ff-e65d08ed01a1`).
- Recent blue-bar/BBC-center creative rows: `#657`-`#662`.
- Existing CA creative `#656` was also used in the same final-ad batch.
- Final ads from that batch: `#364`-`#370`; later CA ads `#371`-`#372`
  were also created with the same CA copy.
- AdMachin creative transcriptions are often `null` for newer uploads. When
  auditing ideas, use local Scribe JSON/transcript files first, then AdMachin
  copy/ad structure as secondary evidence.
- Do not assume launch state from memory. Re-check `list_ads`; launched status
  changed after creation during this session.

## Current Approved Visual Package

- Use the cobalt/blue broadcast lower-third, not the red CNN-like version. The
  red version was too close to CNN; color change solved the issue.
- Lower-third headline: `JUVENILE HALL SEXUAL ABUSE CLAIMS`.
- For the current CA JDC news batch, use `BBC Center Medium` subtitles with the
  cobalt lower-third. `BBC Left` is an approved alternate, but ad02-ad08 used
  center medium.
- Place the Pulaski/Jones disclaimer at the top for 6 seconds when a lower-third
  is present. Bottom placement collides with the bar.
- Keep clean masters separate from lower-third/subtitle/disclaimer versions.

## Wording Rules

- The qualifying harm must be explicit: `sexual abuse` / `sexually abused`.
  Do not use generic `abuse` alone for CA JDC qualification.
- Prefer `may qualify for significant potential compensation` or a cautious
  `may qualify` form. Avoid new copy that says the viewer is `owed`, `paid`, or
  guaranteed anything unless legal explicitly approves.
- Existing primary text row `#465` has a typo (`an California`) and stronger
  wording (`paid millions`, `owed`). Do not copy those problems into new copy.
- CTA should be action-specific: tap below, fill out the short/private form,
  about 30 seconds, starts with name and phone number.
- Facility names are a targeting lever, not a required ingredient in every ad.
  Barry J. Nidorf, Eastlake Central, Los Padrinos, and probation camps are useful
  when the angle is facility recognition, but not every script needs a list.

## Creative Strategy

- The current CA batch is heavily clustered around news/reporter proof:
  L.A. County scale, major claims, facility names, and compensation CTA.
- Future concepts should test different decision moments, not just restated
  reporter copy. Strong next buckets:
  - form walkthrough: show how little the first step asks for
  - no old report needed
  - privacy-first: check without telling family/job/past contacts
  - family/brother perspective
  - facility-memory trigger
  - too-long-ago myth
  - wrong-claim filter: general mistreatment vs sexual abuse
- When the user says scripts feel repetitive, change the premise/speaker/proof
  type/CTA frame. Do not just rewrite the same structure.

## Reporter Avatar / Image Lessons

- For reporter-style avatars, generate the reporter without the news bar/footer
  if the bar will be composited separately. GPT image footer text was often
  empty, garbled, or too text-heavy.
- Use black or Latina women as credible reporter avatars when requested.
- More zoomed-out framing works better: head not near the top, enough lower
  body/desk room for overlays, no empty fake lower-half panels.

## Generation And QA

- Default Veo Lite path for this campaign: useapi Google Flow lower-priority
  (`googleflow_client.generate_veo`, free queue) unless the user changes route.
- If a Veo prompt is flagged as prominent/policy-blocked, switch avatar or
  generate new reporter avatars instead of repeatedly forcing the same avatar.
- Do not repair CA JDC video issues with frozen frames, speed changes, deshake,
  or artificial frame holds unless the user explicitly approves. Reroll or
  re-trim at original speed.
- Watch for audio problems before post: long silences between clips, repeated
  lines, weird sounds, disappearing mic/prop, or bad final gestures. Reroll the
  failing clip rather than hiding it in post.
- Replicate `prunaai/p-video` works as an I2V fallback but should use short
  prompts, native audio, 10s chunks, no generated text/subtitles, and clickable
  raw video links posted before any QA/post-production.

